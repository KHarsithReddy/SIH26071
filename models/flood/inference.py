import numpy as np
import joblib
import pandas as pd

# Load the saved model, features, and categorical columns
model = joblib.load("flood_risk_model.pkl")
model_features = joblib.load("model_features.pkl")
categorical_cols = joblib.load("categorical_cols.pkl")

def predict_flood_risk(features_list):
    """
    Inference function called by FastAPI backend.
    Takes a list of feature values matching the training structure.
    """
    # Create DataFrame with exact training columns
    input_df = pd.DataFrame([features_list], columns=model_features)
    
    # Cast categorical columns back to category type
    for col in categorical_cols:
        if col in input_df.columns:
            input_df[col] = input_df[col].astype('category')

    # Get predictions and probabilities
    probabilities = model.predict_proba(input_df)[0]
    predicted_class = int(np.argmax(probabilities))
    confidence = float(np.max(probabilities))
    
    # Map binary output to prototype risk tiers
    risk_mapping = {
        0: "Low/Moderate Risk",
        1: "Severe Flood Risk"
    }
    
    return {
        "risk_level": risk_mapping.get(predicted_class, "Unknown"),
        "confidence_score": round(confidence * 100, 2)
    }

# --- Test Block ---
if __name__ == "__main__":
    df = pd.read_csv("flood_inventory_ml_ready.csv")
    drop_cols = ['severe_flood', 'unnamed:_0', 'start_date', 'end_date']
    sample_row = df.drop(columns=[col for col in drop_cols if col in df.columns]).iloc[0].tolist()
    
    result = predict_flood_risk(sample_row)
    print("\n--- Test Prediction Output ---")
    print(result)