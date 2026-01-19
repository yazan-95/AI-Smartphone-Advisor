import numpy as np

def average_precision_at_k(recommended, relevant, k):
    score = 0.0
    hits = 0.0

    for i, item in enumerate(recommended[:k]):
        if item in relevant and item not in recommended[:i]:
            hits += 1
            score += hits / (i + 1)

    return score / min(len(relevant), k)

def mean_average_precision(recommendations, ground_truth, k=5):
    scores = []
    for user_id in recommendations:
        scores.append(
            average_precision_at_k(
                recommendations[user_id],
                ground_truth.get(user_id, []),
                k
            )
        )
    return np.mean(scores)
