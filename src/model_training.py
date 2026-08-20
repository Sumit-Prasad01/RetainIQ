import os
import joblib
import numpy as np
import lightgbm as lgb
import mlflow
import mlflow.sklearn
import mlflow.lightgbm
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from utils.logger import get_logger
from utils.custom_exception import CustomException
from constants import TRAIN_DATA_PATH, MODEL_OUTPUT_PATH
from config.model_params import LIGHTGBM_PARAMS, RANDOM_SEARCH_PARAMS

logger = get_logger(__name__)


class ModelTraining:
    def __init__(self, data_path: str, model_output_path: str):
        self.data_path = data_path
        self.model_output_path = model_output_path
        self.params_dist = LIGHTGBM_PARAMS
        self.random_search_params = RANDOM_SEARCH_PARAMS

    def load_data(self):
        try:
            logger.info(f"Loading data from: {self.data_path}")
            data = joblib.load(self.data_path)
            return data["X_train"], data["y_train"], data["X_test"], data["y_test"]
        except Exception as e:
            logger.error(f"Error while loading data: {e}")
            raise CustomException("Failed to load data", e)

    def train_lgbm(self, X_train, y_train):
        try:
            logger.info("Starting LightGBM hyperparameter tuning.")
            lgbm = lgb.LGBMClassifier(
                objective="binary",
                random_state=self.random_search_params.get("random_state", 42),
                n_jobs=1,
                verbosity=-1,
            )
            search = RandomizedSearchCV(
                estimator=lgbm,
                param_distributions=self.params_dist,
                refit=True,
                return_train_score=False,
                **self.random_search_params,
            )
            search.fit(X_train, y_train)
            logger.info(f"Best CV F1: {search.best_score_:.4f}")
            return search.best_estimator_, search.best_params_, search.best_score_
        except Exception as e:
            logger.error(f"Error during LightGBM training: {e}")
            raise CustomException("Failed to train LightGBM", e)

    def find_best_threshold(self, model, X_val, y_val):
        try:
            y_prob = model.predict_proba(X_val)[:, 1]
            thresholds = np.arange(0.10, 0.91, 0.01)
            best_threshold, best_f1 = 0.50, 0.0

            for threshold in thresholds:
                y_pred = (y_prob >= threshold).astype(np.int8)
                score = f1_score(y_val, y_pred, zero_division=0)
                if score > best_f1:
                    best_f1, best_threshold = score, threshold

            logger.info(f"Optimal threshold: {best_threshold:.2f} (Val F1: {best_f1:.4f})")
            return float(best_threshold), float(best_f1)
        except Exception as e:
            logger.error(f"Error finding optimal threshold: {e}")
            raise CustomException("Failed to find optimal threshold", e)

    def evaluate_model(self, model, X_test, y_test, threshold: float):
        try:
            y_prob = model.predict_proba(X_test)[:, 1]
            y_pred = (y_prob >= threshold).astype(np.int8)

            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, zero_division=0),
                "recall": recall_score(y_test, y_pred, zero_division=0),
                "f1_score": f1_score(y_test, y_pred, zero_division=0),
                "roc_auc": roc_auc_score(y_test, y_prob),
            }
            for name, val in metrics.items():
                logger.info(f"{name}: {val:.4f}")
            return metrics
        except Exception as e:
            logger.error(f"Error during model evaluation: {e}")
            raise CustomException("Failed to evaluate model", e)

    def save_model(self, model, threshold: float):
        try:
            os.makedirs(os.path.dirname(self.model_output_path), exist_ok=True)
            joblib.dump({"model": model, "threshold": threshold}, self.model_output_path)
            logger.info(f"Model saved to: {self.model_output_path}")
        except Exception as e:
            logger.error(f"Error while saving model: {e}")
            raise CustomException("Failed to save model", e)

    def log_mlflow(self, model, params: dict, cv_score: float, val_f1: float, threshold: float, metrics: dict):
        try:
            mlflow.log_params(params)
            mlflow.log_params({
                "cv_f1": cv_score,
                "validation_f1": val_f1,
                "classification_threshold": threshold,
            })
            mlflow.log_metrics({f"test_{k}": v for k, v in metrics.items()})
            mlflow.lightgbm.log_model(model, artifact_path="lightgbm_model")
            mlflow.log_artifact(self.data_path, artifact_path="datasets")
            mlflow.log_artifact(self.model_output_path, artifact_path="model_artifact")
        except Exception as e:
            logger.error(f"Error while logging to MLflow: {e}")
            raise CustomException("Failed to log to MLflow", e)

    def run(self):
        try:
            with mlflow.start_run():
                X_train, y_train, X_test, y_test = self.load_data()

                X_train_tuning, X_val, y_train_tuning, y_val = train_test_split(
                    X_train, y_train, test_size=0.20, random_state=42, stratify=y_train
                )

                best_model, best_params, cv_score = self.train_lgbm(X_train_tuning, y_train_tuning)
                best_threshold, val_f1 = self.find_best_threshold(best_model, X_val, y_val)

                logger.info("Refitting best model on full training set.")
                best_model.fit(X_train, y_train)

                metrics = self.evaluate_model(best_model, X_test, y_test, best_threshold)
                self.save_model(best_model, best_threshold)
                self.log_mlflow(best_model, best_params, cv_score, val_f1, best_threshold, metrics)
                logger.info("Training pipeline completed successfully.")
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            raise CustomException("Pipeline execution failed", e)


if __name__ == "__main__":
    trainer = ModelTraining(
        data_path=TRAIN_DATA_PATH,
        model_output_path=MODEL_OUTPUT_PATH,
    )
    trainer.run()