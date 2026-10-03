import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score

# 1. Loading the ML-ready dataset
df = pd.read_csv("flood_inventory_ml_ready.csv")

# Identifying and converting string/object columns to category format for XGBoost
cat_cols = df.select_dtypes(include=['object', 'str']).columns.tolist()
for col in cat_cols:
    df[col] = df[col].astype('category')

# Choose your Target Column (e.g., predicting 'severe_flood' or mapping to a risk category)
# Let's use 'severe_flood' as a binary classification target (0 or 1)
target_column = 'severe_flood'

# Drop target and any redundant ID columns
drop_cols = [target_column, 'unnamed:_0', 'start_date', 'end_date']
X = df.drop(columns=[col for col in drop_cols if col in df.columns])
y = df[target_column]

# Save feature names and categorical column names for inference
joblib.dump(X.columns.tolist(), "model_features.pkl")
joblib.dump(cat_cols, "categorical_cols.pkl")

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and Train XGBoost Model
print("Training XGBoost model on flood inventory data...")
model = XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42,
    enable_categorical=True
)
model.fit(X_train, y_train)

# Evaluate Performance
y_pred = model.predict(X_test)
print(f"\n--- Model Evaluation Results ---")
print(f"Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# 4. Save the Model
joblib.dump(model, "flood_risk_model.pkl")
print("\nModel saved successfully as 'flood_risk_model.pkl'!")