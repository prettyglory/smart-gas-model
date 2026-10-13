import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)

# Load cleaned data
df = pd.read_csv("gas_data_clean.csv")

features = [
    "raw",
    "baseline",
    "gas_delta",
    "temp_c",
    "hum_pct",
]

X = df[features]
y = df["exposure"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# Train model
model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluation
print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))
print("F1 Score:", f1_score(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nFeature Importance:")
for feature, importance in sorted(
    zip(features, model.feature_importances_),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{feature}: {importance:.4f}")

# Save model package
joblib.dump(
    {
        "model": model,
        "features": features
    },
    "gas_model.pkl"
)

print("\nModel saved as gas_model.pkl")