# 🍗 TastePrice Ghana — A Taste-Price Food Recommender for Urban Centers

> *Empowering consumers through crowdsourced transparency in Accra, Kumasi & beyond.*

TastePrice is a **crowd-sourced food recommender system** designed for Ghanaian urban centers. It helps users discover meals that balance **affordability** and **taste**, using fuzzy matching, dynamic preference weighting, and community contributions. Built with Python and Streamlit, it runs on any laptop and requires no GPU.

Perfect for students, workers, and budget-conscious food lovers trying to navigate Ghana’s informal food economy — where price transparency is scarce and information asymmetry is high.

---

## 🚀 Features

- 🔍 **Fuzzy Search**: Handles misspellings like “waaky3” → “Waakye”
- ⚖️ **Price-Taste Slider**: Prioritize cheapness or taste — or find the perfect balance
- ⭐ **Rate Existing Meals**: Update average ratings + vote counts
- ➕ **Add New Meals**: Contribute restaurants, prices, and descriptions
- 📊 **Transparent Rankings**: Results ranked by hybrid score: `score = (cheap_bias × price_norm) + ((1 - cheap_bias) × taste_norm)`
- 💾 **Persistent Storage**: All contributions saved to `ghana_restaurants_master.csv`

---

## 🧰 Tech Stack

- **Language**: Python 3.10+
- **Framework**: Streamlit (for UI)
- **Libraries**: pandas, scikit-learn, rapidfuzz, matplotlib, seaborn
- **Frontend**: Streamlit (no React needed!)
- **Data**: CSV-based (scalable to SQLite later)

---

## ▶️ How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/trtrex-hax/Food-Recommender
cd Food-Recommender

### 2. Install Dependencies
pip install -r requirements.txt

###3. Run the App
streamlit run app.py
Open http://localhost:8501 in your browser

📈 Reproducing Evaluation Results
To reproduce the metrics from the paper  ( Precision@5, Recall@5, NDCG@5):

Bash

python evaluate.py
→ Outputs markdown table + saves precision_plot.png.

Evaluation uses simulated user profiles and keyword-based relevance matching to reflect real-world usage.

🙌 Crowd-Source Data
Hit “Add Meal” 
Fill restaurant, dish, price, location, optional photo URL
Submit → instantly appended to ghana_restaurants_master.csv
Next search re-reads the file → your entry is live
