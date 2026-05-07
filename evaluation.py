"""
Evaluation Module
Computes RMSE, MAE, Precision, Recall, and F1-Score.
"""
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score


def compute_rmse(actual, predicted):
    return np.sqrt(np.mean((np.array(actual) - np.array(predicted))**2))


def compute_mae(actual, predicted):
    return np.mean(np.abs(np.array(actual) - np.array(predicted)))


def compute_precision_recall_f1(actual, predicted, threshold=3.5):
    y_true = [1 if a >= threshold else 0 for a in actual]
    y_pred = [1 if p >= threshold else 0 for p in predicted]

    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    return {"precision": precision, "recall": recall, "f1_score": f1}


def full_evaluation(cf_model):
    """
    Run evaluation by comparing actual ratings in the test set 
    against the model's predictions.
    """
    # For the custom SVD, we'll sample some actual ratings to evaluate
    actual_ratings = cf_model.ratings.sample(min(2000, len(cf_model.ratings)))
    
    y_true = []
    y_pred = []
    
    for _, row in actual_ratings.iterrows():
        pred = cf_model.predict(row['user_id'], row['movie_id'])
        y_true.append(row['rating'])
        y_pred.append(pred)

    rmse = compute_rmse(y_true, y_pred)
    mae = compute_mae(y_true, y_pred)
    prf = compute_precision_recall_f1(y_true, y_pred)

    return {
        "RMSE": round(rmse, 4),
        "MAE": round(mae, 4),
        "Precision": round(prf["precision"], 4),
        "Recall": round(prf["recall"], 4),
        "F1-Score": round(prf["f1_score"], 4),
    }
