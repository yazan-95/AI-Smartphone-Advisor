from ai_engine.recommender.recommender_engine import recommend

# Example user input
test_input = {
    "price": 700,
    "camera": 48,
    "battery": 5000,
    "ram": 8,
    "display_size": 6.5,
    "weight": 180,
    "release_year": 2023
}

# Get top 3 recommendations
results = recommend(test_input, top_n=3)

for r in results.itertuples():
    print(f"Model: {r.model}")
    print(f"Score: {r.match_score:.3f}")
    print(f"Feature Scores: {r.feature_scores}")
    print("-" * 40)
