import joblib

# Try loading them to verify they aren't corrupted
model = joblib.load("heavy_rain_model.pkl")
features = joblib.load("model_features.pkl")

print("Model loaded successfully! Expected feature count:", len(features))