from scipy.stats import randint, uniform


LIGHTGBM_PARAMS = {

    "n_estimators": randint(200, 1000),

    "learning_rate": uniform(0.01, 0.15),

    "num_leaves": randint(20, 150),

    "max_depth": randint(3, 20),

    "min_child_samples": randint(10, 100),

    "subsample": uniform(0.6, 0.4),

    "colsample_bytree": uniform(0.6, 0.4),

    "reg_alpha": uniform(0, 2),

    "reg_lambda": uniform(0, 2),

    "boosting_type": [
        "gbdt",
        "dart"
    ]
}


RANDOM_SEARCH_PARAMS = {

    "n_iter": 30,

    "cv": 5,

    "n_jobs": -1,

    "verbose": 0,

    "random_state": 42,

    "scoring": "f1"
}