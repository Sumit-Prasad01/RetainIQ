import hashlib
import json
import os
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from backend.api.schemas.prediction import PredictionInput

ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = Path(os.getenv("MODEL_PATH", ROOT_DIR / "artifacts/models/lgbm_model.pkl"))


class ChurnPredictor:
    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        artifact = joblib.load(model_path)
        self.model = artifact["model"]
        self.threshold = float(artifact.get("threshold", 0.5))
        self.scaler = artifact.get("scaler")
        self.encoder = artifact.get("encoder")
        self.numeric_features = artifact.get(
            "numeric_features",
            ["age", "salary", "tenure", "balance", "numproducts", "balancesalaryratio", "tenurebyage"],
        )
        self.categorical_features = artifact.get(
            "categorical_features", ["gender", "geography", "hascreditcard", "isactive"],
        )
        self.feature_names = list(self.model.feature_name_)

    @staticmethod
    def cache_key(payload: PredictionInput) -> str:
        # Canonical JSON means the same input always produces the same key.
        raw = json.dumps(payload.model_dump(), sort_keys=True, separators=(",", ":"))
        return "churn:prediction:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _to_features(self, payload: PredictionInput) -> pd.DataFrame:
        row = pd.DataFrame([payload.model_dump()])
        row["balancesalaryratio"] = row["balance"] / row["salary"].replace(0, 1)
        row["tenurebyage"] = row["tenure"] / row["age"].replace(0, 1)

        if self.scaler is not None and self.encoder is not None:
            numeric = pd.DataFrame(
                self.scaler.transform(row[self.numeric_features]),
                columns=self.numeric_features,
                index=row.index,
            )
            encoded = pd.DataFrame(
                self.encoder.transform(row[self.categorical_features]),
                columns=self.encoder.get_feature_names_out(self.categorical_features),
                index=row.index,
            )
            features = pd.concat([numeric, encoded], axis=1)
        else:
            # Compatibility path for models produced before preprocessors were saved.
            features = pd.get_dummies(row, columns=self.categorical_features, dtype=float)

        return features.reindex(columns=self.feature_names, fill_value=0)

    def predict(self, payload: PredictionInput) -> dict[str, Any]:
        probability = float(self.model.predict_proba(self._to_features(payload))[0, 1])
        return {
            "churn_probability": round(probability, 6),
            "churn_prediction": probability >= self.threshold,
            "threshold": self.threshold,
        }
