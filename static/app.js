const MAX_POINTS = 30;

const labels = [];
const rawData = [];
const baselineData = [];

const chart = new Chart(
    document.getElementById("gasChart"),
    {
        type: "line",

        data: {
            labels: labels,

            datasets: [
                {
                    label: "MQ-2 Raw",
                    data: rawData,
                    borderWidth: 2,
                    tension: 0.35
                },
                {
                    label: "Baseline",
                    data: baselineData,
                    borderWidth: 2,
                    tension: 0.35
                }
            ]
        },

        options: {
            responsive: true,

            animation: false,

            plugins: {
                legend: {
                    labels: {
                        color: "#b8c5d6"
                    }
                }
            },

            scales: {
                x: {
                    ticks: {
                        color: "#71869f"
                    },

                    grid: {
                        color: "rgba(255,255,255,.04)"
                    }
                },

                y: {
                    ticks: {
                        color: "#71869f"
                    },

                    grid: {
                        color: "rgba(255,255,255,.05)"
                    }
                }
            }
        }
    }
);


function updateConnection(connected) {

    const badge =
        document.getElementById("connectionBadge");

    if (connected) {

        badge.textContent =
            "ESP32 Connected";

        badge.className =
            "badge online";

    } else {

        badge.textContent =
            "ESP32 Offline";

        badge.className =
            "badge offline";
    }
}


function updateStatus(status) {

    const banner =
        document.getElementById("alertBanner");

    const mainStatus =
        document.getElementById("mainStatus");

    const icon =
        banner.querySelector(".alert-icon");

    if (status === "GAS") {

        banner.className =
            "alert danger";

        mainStatus.textContent =
            "GAS EXPOSURE DETECTED";

        icon.textContent = "!";

    } else {

        banner.className =
            "alert safe";

        mainStatus.textContent =
            "Environment Safe";

        icon.textContent = "✓";
    }
}


function updateChart(raw, baseline, time) {

    labels.push(time);
    rawData.push(raw);
    baselineData.push(baseline);

    if (labels.length > MAX_POINTS) {

        labels.shift();
        rawData.shift();
        baselineData.shift();
    }

    chart.update();
}


async function fetchStatus() {

    try {

        const response =
            await fetch("/api/status");

        const data =
            await response.json();

        if (!data.sensor) {

            updateConnection(
                data.connected === true
            );

            return;
        }

        updateConnection(true);

        const sensor = data.sensor;
        const ml = data.ml;

        document.getElementById(
            "rawValue"
        ).textContent =
            sensor.raw.toFixed(0);

        document.getElementById(
            "baselineValue"
        ).textContent =
            sensor.baseline.toFixed(0);

        document.getElementById(
            "deltaValue"
        ).textContent =
            ml.gas_delta.toFixed(0);

        document.getElementById(
            "temperatureValue"
        ).textContent =
            `${sensor.temp_c.toFixed(1)} °C`;

        document.getElementById(
            "humidityValue"
        ).textContent =
            `${sensor.hum_pct.toFixed(1)} %`;

        const gasPercentage =
            ml.gas_probability * 100;

        document.getElementById(
            "gasProbability"
        ).textContent =
            `${gasPercentage.toFixed(1)}%`;

        document.getElementById(
            "probabilityBar"
        ).style.width =
            `${gasPercentage}%`;

        document.getElementById(
            "esp32State"
        ).textContent =
            sensor.esp32_state;

        document.getElementById(
            "mlState"
        ).textContent =
            ml.status;

        document.getElementById(
            "timeValue"
        ).textContent =
            `${sensor.time_ms} ms`;

        document.getElementById(
            "normalProbability"
        ).textContent =
            `${(
                ml.normal_probability * 100
            ).toFixed(1)}%`;

        document.getElementById(
            "gasProbabilitySmall"
        ).textContent =
            `${gasPercentage.toFixed(1)}%`;

        updateStatus(
            ml.status
        );

        const agreement =
            document.getElementById(
                "agreementBox"
            );

        if (data.agreement) {

            agreement.textContent =
                "ESP32 and AI decisions agree";

            agreement.className =
                "agreement good";

        } else {

            agreement.textContent =
                "ESP32 and AI decisions disagree";

            agreement.className =
                "agreement warning";
        }

        updateChart(
            sensor.raw,
            sensor.baseline,
            sensor.time_ms
        );

    } catch (error) {

        updateConnection(false);

        console.error(
            "Status fetch failed:",
            error
        );
    }
}


fetchStatus();

setInterval(
    fetchStatus,
    1000
);