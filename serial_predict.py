import serial
import joblib
import pandas as pd
import time

# -----------------------------
# SETTINGS
# -----------------------------
PORT = "COM7"
BAUD_RATE = 115200

# -----------------------------
# LOAD TRAINED MODEL
# -----------------------------
package = joblib.load("gas_model.pkl")

model = package["model"]
features = package["features"]

print("Model loaded successfully.")
print("Features:", features)

# -----------------------------
# CONNECT TO ESP32
# -----------------------------
ser = serial.Serial(
    PORT,
    BAUD_RATE,
    timeout=2
)

time.sleep(2)

print(f"\nConnected to {PORT}")
print("Waiting for ESP32 sensor readings...\n")

while True:

    try:
        line = ser.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if not line:
            continue

        # ESP32 sends:
        # time_ms,raw,baseline,temp_c,hum_pct,state

        values = line.split(",")

        # Ignore warm-up messages, headers and other debug text
        if len(values) != 6:
            continue

        try:
            time_ms = int(values[0])
            raw = float(values[1])
            baseline = float(values[2])
            temp_c = float(values[3])
            hum_pct = float(values[4])

        except ValueError:
            # Example header:
            # time_ms,raw,baseline,temp_c,hum_pct,state
            continue

        esp32_state = values[5].strip()

        # -----------------------------
        # VALIDATE SENSOR VALUES
        # -----------------------------
        if raw < 0 or baseline < 0:
            continue

        if not (-20 <= temp_c <= 80):
            continue

        if not (0 <= hum_pct <= 100):
            continue

        # -----------------------------
        # FEATURE ENGINEERING
        # -----------------------------
        gas_delta = raw - baseline

        sample = pd.DataFrame(
            [[
                raw,
                baseline,
                gas_delta,
                temp_c,
                hum_pct
            ]],
            columns=features
        )

        # -----------------------------
        # MACHINE LEARNING PREDICTION
        # -----------------------------
        prediction = model.predict(sample)[0]

        probabilities = model.predict_proba(sample)[0]

        normal_probability = probabilities[0]
        gas_probability = probabilities[1]

        # -----------------------------
        # DISPLAY RESULTS
        # -----------------------------
        print(
            f"Time: {time_ms} ms | "
            f"Raw: {raw:.0f} | "
            f"Baseline: {baseline:.0f} | "
            f"Delta: {gas_delta:.0f}"
        )

        print(
            f"Temperature: {temp_c:.1f} C | "
            f"Humidity: {hum_pct:.1f}%"
        )

        print(
            f"ESP32 threshold state: {esp32_state}"
        )

        print(
            f"ML Normal probability: "
            f"{normal_probability:.2%}"
        )

        print(
            f"ML Gas probability: "
            f"{gas_probability:.2%}"
        )

        if prediction == 1:
            print("ML RESULT: GAS EXPOSURE DETECTED")
        else:
            print("ML RESULT: NORMAL / NO GAS EXPOSURE")

        # Compare old threshold system with ML
        if prediction == 1 and esp32_state == "GAS":
            print("Decision comparison: BOTH detect GAS")

        elif prediction == 0 and esp32_state == "SAFE":
            print("Decision comparison: BOTH detect SAFE")

        else:
            print("Decision comparison: ML and ESP32 threshold DISAGREE")

        print("-" * 70)

    except KeyboardInterrupt:
        print("\nStopped by user.")
        break

    except serial.SerialException as e:
        print("\nSerial connection error:", e)
        break

    except Exception as e:
        print("\nUnexpected error:", e)

if ser.is_open:
    ser.close()

print("Serial connection closed.")