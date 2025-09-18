import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from rapidfuzz import process
import os
import re 

# ========== HELPER FUNCTIONS ==========
def add_rating(df, restaurant, food, new_rating):
    mask = (df['restaurant'].str.lower() == restaurant.lower()) & \
           (df['food'].str.lower() == food.lower())
    
    if not mask.any():
        return None, f"❌ No entry found for '{food}' at '{restaurant}'. Add it first!"
    
    idx = df[mask].index[0]
    
    # 🔥 SAFELY CONVERT TO NUMERIC
    old_avg = pd.to_numeric(df.at[idx, 'taste'], errors='coerce')
    old_votes = pd.to_numeric(df.at[idx, 'votes_count'], errors='coerce')
    
    # Handle NaN or invalid values
    if pd.isna(old_avg) or pd.isna(old_votes):
        old_avg = 0.0
        old_votes = 0
    
    # Calculate new average
    new_avg = (old_avg * old_votes + new_rating) / (old_votes + 1)
    
    # Update DataFrame
    df.at[idx, 'taste'] = new_avg
    df.at[idx, 'votes_count'] = old_votes + 1
    
    msg = f"✅ Updated {food} at {restaurant}: new avg taste = {new_avg:.2f} ({int(old_votes + 1)} votes)"
    return df, msg
def get_matching_dishes(df, query_rest="", query_food=""):
    """
    Returns list of (restaurant, food) tuples matching partial input.
    """
    mask = True
    if query_rest.strip():
        mask &= df['restaurant'].str.contains(query_rest, case=False, na=False)
    if query_food.strip():
        mask &= df['food'].str.contains(query_food, case=False, na=False)
    matches = df[mask][['restaurant', 'food']].drop_duplicates().head(5)
    return [(row['restaurant'], row['food']) for _, row in matches.iterrows()]

def add_new_entry(df, restaurant, food, price, rating, location, portion_size, category, description="", source="user"):
    new_row = {
        "restaurant": restaurant.strip().title(),
        "food": food.strip().title(),
        "price": float(price),
        "taste": float(rating),
        "location": location.strip().title(),
        "portion_size": portion_size,
        "dish_category": category.strip().title() if category else "Uncategorized",
        "description": description.strip() if description else None,
        "source_url": source,
        "votes_count": 1
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return df

# ========== Load & Prepare Data ==========
@st.cache_data
def load_data():
    if not os.path.exists("ghana_restaurants_master.csv"):
        st.error("Dataset not found! Please run data prep script first.")
        return None
    df = pd.read_csv("ghana_restaurants_master.csv")
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['taste'] = pd.to_numeric(df['taste'], errors='coerce')
    df = df.dropna(subset=["price"])

    # 🔥 CRITICAL: Ensure 'votes_count' exists
    if 'votes_count' not in df.columns:
        df['votes_count'] = 1  # Default to 1 vote for all existing entries
    else:
        df['votes_count'] = pd.to_numeric(df['votes_count'], errors='coerce').fillna(1).astype(int)
        
    # Normalize
    scaler = MinMaxScaler()
    df['price_norm'] = 1 - scaler.fit_transform(df[['price']])
    df['taste_norm'] = scaler.fit_transform(df[['taste']].fillna(0))
    
    # Optional: Weight score by popularity (log scale to avoid dominance)
    df['popularity_weight'] = (df['votes_count'].fillna(1).apply(lambda x: max(1, x))).apply(lambda x: x**0.2)
    df['weighted_score'] = df['price_norm'] * 0.5 + df['taste_norm'] * 0.5
    df['score'] = df['weighted_score'] * df['popularity_weight']
    
    return df

df = load_data()
if df is None:
    st.stop()

# ======== Recommender Function (Slightly Enhanced) ========
def recommend_dish_fuzzy(dish_name, df, top_k=5, cheap_bias=0.5, cutoff=70):
    unique_dishes = df['food'].dropna().unique().tolist()
    
    # Use process.extract → returns LIST of (match, score, index)
    results = process.extract(dish_name, unique_dishes, limit=10, score_cutoff=cutoff)
    
    if not results:  # if empty list
        return None, f"No close matches found for '{dish_name}'"
    
    # Extract ALL matched dish names (not just one!)
    matched_names = [r[0] for r in results]  # r[0] = the matched string
    
    # Create a regex pattern: "waakye|wakye|waaky3|..."
    pattern = '|'.join([re.escape(name) for name in matched_names])
    
    # Filter rows where 'food' contains ANY of the matched names
    mask = df['food'].str.contains(pattern, case=False, na=False, regex=True)
    subset = df[mask].copy()
    
    if subset.empty:
        return None, f"No dishes found matching any of: {matched_names}"
    
    # Compute score based on user preference
    subset['user_score'] = cheap_bias * subset['price_norm'] + (1 - cheap_bias) * subset['taste_norm']
    
    # Return first match (for display) + top K sorted results
    return matched_names[0], subset.sort_values('user_score', ascending=False).head(top_k)
# ========= Streamlit UI =========
st.set_page_config(page_title="🍗 TastePrice Ghana", page_icon="🍗", layout="centered")

st.title("🍗 TastePrice Food Recommender")
st.markdown("*Find affordable, tasty meals in Accra, Kumasi & beyond — powered by community data.*")

# --- Search + Preference ---
col1, col2 = st.columns([3,1])
with col1:
    dish_name = st.text_input("🔍 Search for a dish (e.g., Waakye, Jollof, Kebab)", placeholder="Type a dish name...")
with col2:
    cheap_bias = st.slider("💰 vs 😋", 0.0, 1.0, 0.5, 
                           help="Slide left for tastier, right for cheaper",
                           label_visibility="collapsed")

# --- Display Results ---
if dish_name:
    with st.spinner("Finding the best bites..."):
        match, results_or_msg = recommend_dish_fuzzy(dish_name, df, top_k=5, cheap_bias=cheap_bias)

    if isinstance(results_or_msg, str):  # error message
        st.warning(results_or_msg)
    else:
        st.success(f"✅ Matched to: **{match}**")
        st.subheader("🏆 Top Recommendations")
        
        for idx, row in results_or_msg.iterrows():
            with st.container(border=True):
                cols = st.columns([3,1])
                with cols[0]:
                    st.markdown(f"### {row['restaurant']}")
                    st.write(f"📍 {row['location']}")
                    st.write(f"🍽️ **{row['food']}** — ₵{row['price']:.2f}")
                    if not pd.isna(row.get('description')):
                        st.caption(f"*{row['description']}*")
                with cols[1]:
                    st.metric("Taste", f"{row['taste']}/10" if not pd.isna(row['taste']) else "N/A")
                    st.metric("Value Score", f"{row['user_score']:.2f}")
                    st.caption(f"({int(row['votes_count'])} votes)")

                st.divider()

# --- Rate Existing Dish ---
# --- Rate Existing Dish ---
st.markdown("---")
st.subheader("⭐ Rate an Existing Dish")

with st.form("rating_form", clear_on_submit=True):
    r1, r2 = st.columns(2)
    with r1:
        rate_rest = st.text_input("Restaurant Name*", placeholder="e.g., ChopBar")
        rate_food = st.text_input("Dish Name*", placeholder="e.g., Waakye")
    with r2:
        new_taste = st.slider("Your Taste Rating (1-10)", 1, 10, 7)
    
    # 🔍 LIVE SUGGESTIONS (optional but helpful)
    if rate_rest or rate_food:
        suggestions = get_matching_dishes(df, rate_rest, rate_food)
        if suggestions:
            st.caption("🔎 Matching dishes:")
            for rest, food in suggestions:
                st.write(f"- **{rest}** → {food}")
        else:
            st.caption("📭 No matches found — make sure you’re spelling it right, or add a new dish below.")

    rate_submitted = st.form_submit_button("🗳️ Submit Rating", use_container_width=True)

    if rate_submitted:
        if not all([rate_rest, rate_food]):
            st.error("Please fill in both restaurant and dish name.")
        else:
            # Reload current live data
            current_df = pd.read_csv("ghana_restaurants_master.csv")
            updated_df, msg = add_rating(current_df, rate_rest, rate_food, new_taste)
            
            if updated_df is not None:
                updated_df.to_csv("ghana_restaurants_master.csv", index=False, encoding="utf-8")
                st.success(msg)
                st.cache_data.clear()
            else:
                st.warning(msg)
                st.info("💡 Try adding this dish using the 'Add New Meal' form below.")
                             
# --- User Contribution Form ---
st.markdown("---")
st.subheader("✨ Help us grow! Add a new meal or update info")

with st.form("contribution_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        rest = st.text_input("Restaurant Name*", placeholder="e.g., Auntie Ama's Spot")
        food = st.text_input("Dish Name*", placeholder="e.g., Fried Yam & Kontomire")
        price = st.number_input("Price (₵)*", min_value=0.0, step=1.0, format="%.2f")
        loc = st.text_input("Location*", placeholder="e.g., Osu, KNUST, Adenta")
    with c2:
        taste = st.slider("Taste Rating (1-10)", 1, 10, 7)
        portion = st.selectbox("Portion Size", ["Small", "Medium", "Large", "Extra Large"])
        category = st.text_input("Dish Category", placeholder="e.g., Breakfast, Street Food")
        desc = st.text_area("Description (optional)", placeholder="Crispy yam, spicy sauce, generous serving")

    submitted = st.form_submit_button("✅ Submit Entry", use_container_width=True)

    if submitted:
        if not all([rest, food, price, loc]):
            st.error("Please fill in all required fields (*)")
        else:
            # Create new row
            new_entry = {
                "restaurant": rest.strip().title(),
                "food": food.strip().title(),
                "price": price,
                "taste": taste,
                "location": loc.strip().title(),
                "portion_size": portion,
                "dish_category": category.strip().title() if category else "Uncategorized",
                "description": desc.strip() if desc else None,
                "source_url": "user_submission",
                "votes_count": 1
            }
            
            # Append to master CSV
            try:
                # Reload current data
                current_df = pd.read_csv("ghana_restaurants_master.csv")
                updated_df = pd.concat([current_df, pd.DataFrame([new_entry])], ignore_index=True)
                updated_df.to_csv("ghana_restaurants_master.csv", index=False, encoding="utf-8")
                
                st.success("🎉 Thank you! Your submission helps the community find better meals.")
                st.cache_data.clear()  # Clear cache so next search includes new data
            except Exception as e:
                st.error(f"Failed to save: {e}")

# --- Footer ---
st.markdown("---")
st.caption("💡 Built for students, workers, and food lovers across Ghana. Data is crowdsourced — your input makes it better!")
st.caption("© 2025 TastePrice Ghana | Empowering consumers through transparency")

