import time
import joblib
import pandas as pd
import streamlit as st
import serial

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Smart Gas AI Monitor",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0b1220 0%, #111827 45%, #0f172a 100%);
    color: white;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0b1220;
    border-right: 1px solid #1f2937;
}

/* Main title */
.main-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 0px;
    color: #f8fafc;
}

.subtitle {
    color: #94a3b8;
    font-size: 17px;
    margin-bottom: 25px;
}

/* Sensor Cards */
.sensor-card {
    background: rgba(30, 41, 59, 0.85);
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 22px;
    min-height: 145px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.20);
}

.sensor-label {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 8px;
}

.sensor-value {
    color: white;
    font-size: 34px;
    font-weight: 800;
}

.sensor-unit {
    color: #64748b;
    font-size: 13px;
}

/* System status cards */
.status-safe {
    background: rgba(16, 185, 129, 0.13);
    border: 1px solid #10b981;
    border-radius: 18px;
    padding: 24px;
    text-align: center;
}

.status-danger {
    background: rgba(239, 68, 68, 0.14);
    border: 1px solid #ef4444;
    border-radius: 18px;
    padding: 24px;
    text-align: center;
    animation: pulse 1.2s infinite;
}

.status-warning {
    background: rgba(245, 158, 11, 0.14);
    border: 1px solid #f59e0b;
    border-radius: 18px;
    padding: 24px;
    text-align: center;
}

.status-title {
    font-size: 15px;
    color: #cbd5e1;
}

.status-value {
    font-size: 28px;
    font-weight: 800;
    margin-top: 8px;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
    70% { box-shadow: 0 0 0 18px rgba(239,68,68,0); }
    100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
}

/* Section headings */
.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #f8fafc;
    margin-top: 10px;
    margin-bottom: 15px;
}

/* Probability card */
.prob-card {
    background: rgba(15,23,42,0.95);
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 25px;
}

.prob-number {
    font-size: 46px;
    font-weight: 900;
    text-align: center;
}

.small-muted {
    color: #94a3b8;
    text-align: center;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    font-weight: 700;
    min-height: 45px;
}

hr {
    border-color: #1f2937 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SETTINGS
# =========================================================
PORT = "COM7"
BAUD_RATE = 115200

# =========================================================
# LOAD MODEL
# =========================================================
@st.cache_resource
def load_model():
    package = joblib.load("gas_model.pkl")
    return package["model"], package["features"]

model, features = load_model()

# =========================================================
# SESSION STATE
# =========================================================
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

if "serial_connection" not in st.session_state:
    st.session_state.serial_connection = None

if "history" not in st.session_state:
    st.session_state.history = []

# =========================================================
# HEADER
# =========================================================
st.markdown(
    '<div class="main-title">🔥 Smart Gas AI Monitor</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Real-time LPG and gas safety monitoring powered by ESP32 and Machine Learning.'
    '</div>',
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.markdown("## ⚙️ System Control")

    st.markdown("---")

    st.write("**Device Port**")
    st.code(PORT)

    st.write("**Baud Rate**")
    st.code(str(BAUD_RATE))

    st.markdown("---")

    start = st.button("▶ Start Monitoring")

    stop = st.button("■ Stop Monitoring")

    st.markdown("---")

    st.markdown("### 🤖 Model")

    st.success("Random Forest Loaded")

    st.caption(
        "Features: raw, baseline, gas_delta, temperature, humidity"
    )

# =========================================================
# START / STOP
# =========================================================
if start:

    try:

        if (
            st.session_state.serial_connection is None
            or not st.session_state.serial_connection.is_open
        ):

            st.session_state.serial_connection = serial.Serial(
                PORT,
                BAUD_RATE,
                timeout=2
            )

            time.sleep(2)

        st.session_state.monitoring = True

    except Exception as e:
        st.error(f"Unable to connect to ESP32: {e}")


if stop:

    st.session_state.monitoring = False

    if st.session_state.serial_connection is not None:
        try:
            st.session_state.serial_connection.close()
        except:
            pass

    st.session_state.serial_connection = None

# =========================================================
# PLACEHOLDERS
# =========================================================

main_status = st.empty()

st.markdown(
    '<div class="section-title">Live Sensor Readings</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4, c5 = st.columns(5)

raw_placeholder = c1.empty()
baseline_placeholder = c2.empty()
delta_placeholder = c3.empty()
temp_placeholder = c4.empty()
hum_placeholder = c5.empty()

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns([1.2, 1])

with left:

    st.markdown(
        '<div class="section-title">AI Detection</div>',
        unsafe_allow_html=True
    )

    probability_placeholder = st.empty()
    progress_placeholder = st.empty()

with right:

    st.markdown(
        '<div class="section-title">Decision Engine</div>',
        unsafe_allow_html=True
    )

    comparison_placeholder = st.empty()

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">Recent Readings</div>',
    unsafe_allow_html=True
)

history_placeholder = st.empty()

# =========================================================
# DEFAULT CARDS
# =========================================================
def sensor_card(label, value, unit=""):
    return f"""
    <div class="sensor-card">
        <div class="sensor-label">{label}</div>
        <div class="sensor-value">{value}</div>
        <div class="sensor-unit">{unit}</div>
    </div>
    """

raw_placeholder.markdown(
    sensor_card("MQ-2 Raw", "--"),
    unsafe_allow_html=True
)

baseline_placeholder.markdown(
    sensor_card("Baseline", "--"),
    unsafe_allow_html=True
)

delta_placeholder.markdown(
    sensor_card("Gas Delta", "--"),
    unsafe_allow_html=True
)

temp_placeholder.markdown(
    sensor_card("Temperature", "--", "°C"),
    unsafe_allow_html=True
)

hum_placeholder.markdown(
    sensor_card("Humidity", "--", "%"),
    unsafe_allow_html=True
)

# =========================================================
# LIVE MONITORING
# =========================================================
if st.session_state.monitoring:

    ser = st.session_state.serial_connection

    while st.session_state.monitoring:

        try:

            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            values = line.split(",")

            # Expected:
            # time_ms,raw,baseline,temp_c,hum_pct,state
            if len(values) != 6:
                continue

            try:
                time_ms = int(values[0])
                raw = float(values[1])
                baseline = float(values[2])
                temp_c = float(values[3])
                hum_pct = float(values[4])
                esp32_state = values[5].strip()

            except ValueError:
                continue

            # Validation
            if raw < 0 or baseline < 0:
                continue

            if not (-20 <= temp_c <= 80):
                continue

            if not (0 <= hum_pct <= 100):
                continue

            # Feature engineering
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

            # Model prediction
            prediction = model.predict(sample)[0]
            probability = model.predict_proba(sample)[0]

            normal_probability = probability[0]
            gas_probability = probability[1]

            # =================================================
            # MAIN STATUS
            # =================================================
            if prediction == 1:

                main_status.markdown(
                    """
                    <div class="status-danger">
                        <div class="status-title">
                            SYSTEM STATUS
                        </div>
                        <div class="status-value">
                            🚨 GAS EXPOSURE DETECTED
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                main_status.markdown(
                    """
                    <div class="status-safe">
                        <div class="status-title">
                            SYSTEM STATUS
                        </div>
                        <div class="status-value">
                            ✅ ENVIRONMENT SAFE
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # =================================================
            # SENSOR CARDS
            # =================================================
            raw_placeholder.markdown(
                sensor_card(
                    "MQ-2 Raw",
                    f"{raw:.0f}"
                ),
                unsafe_allow_html=True
            )

            baseline_placeholder.markdown(
                sensor_card(
                    "Baseline",
                    f"{baseline:.0f}"
                ),
                unsafe_allow_html=True
            )

            delta_placeholder.markdown(
                sensor_card(
                    "Gas Delta",
                    f"{gas_delta:.0f}"
                ),
                unsafe_allow_html=True
            )

            temp_placeholder.markdown(
                sensor_card(
                    "Temperature",
                    f"{temp_c:.1f}",
                    "°C"
                ),
                unsafe_allow_html=True
            )

            hum_placeholder.markdown(
                sensor_card(
                    "Humidity",
                    f"{hum_pct:.1f}",
                    "%"
                ),
                unsafe_allow_html=True
            )

            # =================================================
            # AI PROBABILITY
            # =================================================
            probability_placeholder.markdown(
                f"""
                <div class="prob-card">
                    <div class="small-muted">
                        Gas Exposure Probability
                    </div>

                    <div class="prob-number">
                        {gas_probability:.1%}
                    </div>

                    <div class="small-muted">
                        AI confidence based on current sensor readings
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            progress_placeholder.progress(
                min(max(float(gas_probability), 0.0), 1.0)
            )

            # =================================================
            # DECISION COMPARISON
            # =================================================
            if prediction == 1 and esp32_state == "GAS":

                comparison_placeholder.markdown(
                    """
                    <div class="status-danger">
                        <div class="status-title">
                            ESP32 + AI
                        </div>
                        <div class="status-value">
                            BOTH DETECT GAS
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif prediction == 0 and esp32_state == "SAFE":

                comparison_placeholder.markdown(
                    """
                    <div class="status-safe">
                        <div class="status-title">
                            ESP32 + AI
                        </div>
                        <div class="status-value">
                            BOTH DETECT SAFE
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                comparison_placeholder.markdown(
                    f"""
                    <div class="status-warning">
                        <div class="status-title">
                            DECISION DISAGREEMENT
                        </div>
                        <div class="status-value">
                            ESP32: {esp32_state}
                            <br>
                            AI: {"GAS" if prediction == 1 else "SAFE"}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # =================================================
            # HISTORY
            # =================================================
            st.session_state.history.append({
                "Time (ms)": time_ms,
                "Raw": raw,
                "Baseline": baseline,
                "Delta": gas_delta,
                "Temp °C": temp_c,
                "Humidity %": hum_pct,
                "ESP32": esp32_state,
                "AI": "GAS" if prediction == 1 else "SAFE",
                "Gas Probability": f"{gas_probability:.1%}"
            })

            # Keep only latest 15 readings
            st.session_state.history = (
                st.session_state.history[-15:]
            )

            history_df = pd.DataFrame(
                st.session_state.history
            )

            history_placeholder.dataframe(
                history_df.iloc[::-1],
                use_container_width=True,
                hide_index=True
            )

            time.sleep(0.3)

        except serial.SerialException as e:

            st.session_state.monitoring = False

            main_status.error(
                f"ESP32 connection lost: {e}"
            )

            break

        except Exception as e:

            st.error(
                f"System error: {e}"
            )

            time.sleep(1)

else:

    main_status.markdown(
        """
        <div class="status-warning">
            <div class="status-title">
                SYSTEM STATUS
            </div>
            <div class="status-value">
                MONITORING OFF
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )