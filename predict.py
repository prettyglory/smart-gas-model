import joblib
import pandas as pd

# Load saved model package
package = joblib.load("gas_model.pkl")

model = package["model"]
features = package["features"]

print("Model loaded successfully.")
print("Expected features:", features)

# Example sensor readings
raw = 520
baseline = 170
temp_c = 30.0
hum_pct = 32.0

gas_delta = raw - baseline

sample = pd.DataFrame(
    [[raw, baseline, gas_delta, temp_c, hum_pct]],
    columns=features
)

prediction = model.predict(sample)[0]
probability = model.predict_proba(sample)[0]

print("\nSensor readings:")
print(sample)

print("\nPrediction:", prediction)

print(f"Probability NORMAL (0): {probability[0]:.2%}")
print(f"Probability EXPOSURE (1): {probability[1]:.2%}")

if prediction == 1:
    print("\nResult: GAS EXPOSURE DETECTED")
else:
    print("\nResult: NORMAL / NO GAS EXPOSURE")