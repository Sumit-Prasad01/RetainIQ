from typing import Literal

from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    """Customer attributes required by the churn model."""

    gender: Literal["Female", "Male"]
    age: int = Field(ge=18, le=120)
    salary: float = Field(ge=0)
    geography: Literal["Canada", "France", "Germany", "Spain", "UK", "USA"]
    tenure: int = Field(ge=0, le=100)
    balance: float = Field(ge=0)
    numproducts: int = Field(ge=1, le=4)
    hascreditcard: bool
    isactive: bool


class PredictionResponse(BaseModel):
    churn_probability: float
    churn_prediction: bool
    threshold: float
    cache_status: Literal["cache_hit", "cache_miss", "cache_unavailable"]
