import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score

# 1. Load dataset[cite: 14]
df = pd.read_csv("sih_ml_ready.csv")

# Identify and convert string/object columns to category
cat_cols = df.select_dtypes(include=['object', 'str']).columns.tolist()
for col in cat_cols:
    df[col] = df[col].astype('category')

target_column = 'heavy_rain_target'
X = df.drop(columns=[target_column])
y = df[target_column]

# Save feature columns and categorical column names
joblib.dump(X.columns.tolist(), "model_features.pkl")
joblib.dump(cat_cols, "categorical_cols.pkl")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Initialize and Train XGBoost with enable_categorical=True
model = XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42,
    enable_categorical=True
)
model.fit(X_train, y_train)

# 3. Evaluate and Save
y_pred = model.predict(X_test)
print(f"Model Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print("\nClassification Report:\n", classification_report(y_test, y_pred))

joblib.dump(model, "heavy_rain_model.pkl")
print("Model, features, and categorical columns saved successfully!")