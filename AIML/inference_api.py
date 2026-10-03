import numpy as np
import joblib
import pandas as pd

# Load the model, feature names, and categorical column names
model = joblib.load("heavy_rain_model.pkl")
model_features = joblib.load("model_features.pkl")
categorical_cols = joblib.load("categorical_cols.pkl")

def predict_risk_status(features_list):
    """
    Inference function called by FastAPI backend[cite: 10].
    """
    # Create DataFrame with exact training columns
    input_df = pd.DataFrame([features_list], columns=model_features)
    
    # Explicitly cast categorical columns back to 'category' dtype
    for col in categorical_cols:
        if col in input_df.columns:
            input_df[col] = input_df[col].astype('category')

    probabilities = model.predict_proba(input_df)[0]
    predicted_class = int(np.argmax(probabilities))
    confidence = float(np.max(probabilities))
    
    risk_mapping = {0: "Low", 1: "Moderate", 2: "High"}
    
    return {
        "risk_level": risk_mapping.get(predicted_class, "Unknown"),
        "confidence_score": round(confidence * 100, 2)
    }

# --- Test Prediction Block ---
if __name__ == "__main__":
    df = pd.read_csv("sih_ml_ready.csv")
    sample_row = df.drop(columns=['heavy_rain_target']).iloc[0].tolist()
    
    result = predict_risk_status(sample_row)
    print("\n--- Test Prediction Output ---")
    print(result)