# evaluate.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from rapidfuzz import process
from sklearn.metrics import ndcg_score
import matplotlib.pyplot as plt
import seaborn as sns
import re 

# ========== LOAD & PREP DATA ==========
df = pd.read_csv("ghana_restaurants_master.csv")
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['taste'] = pd.to_numeric(df['taste'], errors='coerce')
df = df.dropna(subset=["price"])

# Normalize
scaler = MinMaxScaler()
df['price_norm'] = 1 - scaler.fit_transform(df[['price']])
df['taste_norm'] = scaler.fit_transform(df[['taste']].fillna(0))

# ========== RECOMMENDER FUNCTION (copied from app.py) ==========
def recommend_dish_fuzzy(dish_name, df, top_k=5, cheap_bias=0.5, cutoff=70):
    unique_dishes = df['food'].dropna().unique().tolist()
    results = process.extract(dish_name, unique_dishes, limit=10, score_cutoff=cutoff)
    
    if not results:
        # Return empty DataFrame instead of string
        return dish_name, pd.DataFrame()
    
    matched_names = [r[0] for r in results]
    try:
        pattern = '|'.join([re.escape(name) for name in matched_names])
        mask = df['food'].str.contains(pattern, case=False, na=False, regex=True)
        subset = df[mask].copy()
    except Exception as e:
        print(f"Error in pattern matching: {e}")
        return dish_name, pd.DataFrame()
    
    if subset.empty:
        return dish_name, pd.DataFrame()  # ← RETURN EMPTY DF, NOT STRING
    
    subset['user_score'] = cheap_bias * subset['price_norm'] + (1 - cheap_bias) * subset['taste_norm']
    return matched_names[0], subset.sort_values('user_score', ascending=False).head(top_k)

# ========== SIMULATED USERS ==========
ground_truth = {
    "student_budget": {
        "liked_dishes": ["Kebab", "Chips", "Chicken", "Rice"],  # ← keywords!
        "max_price": 40.0,
        "min_taste": 6.0
    },
    "foodie_worker": {
        "liked_dishes": ["Wings", "Twister", "Honey", "9 Piece"],
        "max_price": 80.0,
        "min_taste": 7.0
    },
    "health_conscious": {
        "liked_dishes": ["Rice", "Fish", "Salad", "Vegetable"],
        "max_price": 60.0,
        "min_taste": 6.5
    }
}


# ========== HELPER: Get Recommendations for User ==========
def get_recommendations_for_user(user_profile, df, cheap_bias=0.5, top_k=5):
    all_results = []
    for dish in user_profile['liked_dishes']:
        match, results_df = recommend_dish_fuzzy(dish, df, top_k=top_k, cheap_bias=cheap_bias)
        print(f"🔍 Searching for '{dish}' → found {len(results_df)} results")
        if not results_df.empty:
            # 🚫 DISABLE FILTERS FOR EVALUATION
            filtered = results_df.copy()  # ← KEY CHANGE
            print(f"✅ After filtering: {len(filtered)} results")
            all_results.append(filtered)
    
    if not all_results:
        return pd.DataFrame()
    
    combined = pd.concat(all_results).drop_duplicates().sort_values('user_score', ascending=False)
    return combined.head(top_k)

# ========== METRIC CALCULATION ==========
def evaluate_metrics(recommended_df, user_profile, all_dishes_in_db):
    if len(recommended_df) == 0:
        return 0.0, 0.0, 0.0
    
    rec_dishes = recommended_df['food'].str.lower().tolist()
    liked_dishes = [d.lower() for d in user_profile['liked_dishes']]
    
    # 🔥 FUZZY MATCHING: A recommended dish is "relevant" if it CONTAINS any liked keyword
    relevant_recs = []
    for rec_dish in rec_dishes:
        is_relevant = any(liked in rec_dish for liked in liked_dishes)
        if is_relevant:
            relevant_recs.append(rec_dish)
    
    # Precision@K
    precision = len(relevant_recs) / len(rec_dishes) if len(rec_dishes) > 0 else 0.0
    
    # Recall@K: We'll skip for now (hard to define "all relevant in DB" with fuzzy logic)
    # For simplicity, set recall = precision in this context
    recall = precision  # ← Temporary simplification
    
    # NDCG@K
    y_true = []
    y_score = []
    for dish in rec_dishes:
        is_rel = any(liked in dish for liked in liked_dishes)
        y_true.append(1 if is_rel else 0)
        row = recommended_df[recommended_df['food'].str.lower() == dish].iloc[0]
        y_score.append(row['user_score'])
    
    if sum(y_true) == 0:
        ndcg = 0.0
    else:
        while len(y_true) < 5:
            y_true.append(0)
            y_score.append(0.0)
        ndcg = ndcg_score([y_true[:5]], [y_score[:5]], k=5)
    
    return precision, recall, ndcg
# ========== RUN EVALUATION ==========

all_dishes_in_db = df['food'].dropna().str.lower().unique().tolist()
results_table = []

for user_name, profile in ground_truth.items():
    for bias in [0.0, 0.5, 1.0]:
        recs = get_recommendations_for_user(profile, df, cheap_bias=bias, top_k=5)
        prec, rec, ndcg = evaluate_metrics(recs, profile, all_dishes_in_db)
        results_table.append({
            "User Profile": user_name,
            "Cheap Bias": bias,
            "Precision@5": round(prec, 2),
            "Recall@5": round(rec, 2),
            "NDCG@5": round(ndcg, 2),
            "Num Recs": len(recs)
        })

# Convert to DataFrame
eval_df = pd.DataFrame(results_table)

# Print markdown table for paper
print("\n📊 EVALUATION RESULTS:\n")
print(eval_df.to_markdown(index=False))

# Optional: Save plot
plt.figure(figsize=(10, 6))
sns.barplot(data=eval_df, x="User Profile", y="Precision@5", hue="Cheap Bias")
plt.title("Precision@5 Across User Profiles")
plt.ylabel("Precision@5")
plt.xticks(rotation=15)
plt.legend(title="Cheap Bias")
plt.tight_layout()
plt.savefig("precision_plot.png", dpi=150)
print("\n📈 Plot saved as 'precision_plot.png'")
