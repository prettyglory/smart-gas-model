from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.model_service import GasModelService
from app.serial_reader import SerialReader


model_service = GasModelService("gas_model.pkl")

serial_reader = SerialReader(
    port="COM7",
    baud_rate=115200
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    serial_reader.connect()

    yield

    serial_reader.disconnect()


app = FastAPI(
    title="Smart Gas AI Monitoring API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "project": "Smart Gas AI Monitoring System",
        "api": "running"
    }


@app.get("/api/health")
def health():

    return {
        "api": "online",
        "esp32_connected": serial_reader.running,
        "serial_port": serial_reader.port,
        "serial_error": serial_reader.error,
    }


@app.get("/api/status")
def status():

    sensor_data = serial_reader.get_latest()

    if sensor_data is None:

        return {
            "connected": serial_reader.running,
            "message": "Waiting for sensor readings",
            "serial_error": serial_reader.error,
        }

    ml = model_service.predict(
        raw=sensor_data["raw"],
        baseline=sensor_data["baseline"],
        temp_c=sensor_data["temp_c"],
        hum_pct=sensor_data["hum_pct"],
    )

    return {
        "connected": True,
        "sensor": sensor_data,
        "ml": ml,
        "agreement": (
            sensor_data["esp32_state"] == ml["status"]
        ),
    }