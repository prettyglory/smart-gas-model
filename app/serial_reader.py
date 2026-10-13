import threading
import time

import serial


class SerialReader:
    def __init__(
        self,
        port="COM7",
        baud_rate=115200,
    ):
        self.port = port
        self.baud_rate = baud_rate

        self.serial = None
        self.running = False

        self.latest = None
        self.error = None

        self.thread = None

    def connect(self):
        if self.running:
            return

        try:
            self.serial = serial.Serial(
                self.port,
                self.baud_rate,
                timeout=2
            )

            time.sleep(2)

            self.running = True
            self.error = None

            self.thread = threading.Thread(
                target=self._read_loop,
                daemon=True
            )

            self.thread.start()

        except Exception as exc:
            self.error = str(exc)
            self.running = False

    def _read_loop(self):
        while self.running:

            try:
                line = (
                    self.serial
                    .readline()
                    .decode("utf-8", errors="ignore")
                    .strip()
                )

                if not line:
                    continue

                values = line.split(",")

                # ESP32 format:
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

                if raw < 0 or baseline < 0:
                    continue

                if not -20 <= temp_c <= 80:
                    continue

                if not 0 <= hum_pct <= 100:
                    continue

                self.latest = {
                    "time_ms": time_ms,
                    "raw": raw,
                    "baseline": baseline,
                    "temp_c": temp_c,
                    "hum_pct": hum_pct,
                    "esp32_state": esp32_state,
                }

            except Exception as exc:
                self.error = str(exc)
                self.running = False

    def disconnect(self):
        self.running = False

        if self.serial and self.serial.is_open:
            self.serial.close()

    def get_latest(self):
        return self.latest