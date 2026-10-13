import joblib
import pandas as pd


class GasModelService:
    def __init__(self, model_path="gas_model.pkl"):
        package = joblib.load(model_path)

        self.model = package["model"]
        self.features = package["features"]

    def predict(
        self,
        raw: float,
        baseline: float,
        temp_c: float,
        hum_pct: float,
    ):
        gas_delta = raw - baseline

        sample = pd.DataFrame(
            [[
                raw,
                baseline,
                gas_delta,
                temp_c,
                hum_pct
            ]],
            columns=self.features
        )

        prediction = int(self.model.predict(sample)[0])
        probabilities = self.model.predict_proba(sample)[0]

        return {
            "prediction": prediction,
            "status": "GAS" if prediction == 1 else "SAFE",
            "normal_probability": float(probabilities[0]),
            "gas_probability": float(probabilities[1]),
            "gas_delta": float(gas_delta),
        }