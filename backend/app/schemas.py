"""Mô hình dữ liệu vào/ra của API (pydantic v2)."""
from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

Num = Union[int, float, str]


class ConstraintIn(BaseModel):
    a: list[Num]
    sign: Literal["<=", ">=", "="]
    b: Num


class LPRequest(BaseModel):
    sense: Literal["max", "min"]
    c: list[Num] = Field(min_length=1)
    constraints: list[ConstraintIn] = Field(min_length=1)
    var_signs: Optional[list[Literal["ge0", "le0", "free"]]] = None
    method: Literal["simplex", "dual_simplex"] = "simplex"


class CheckRequest(LPRequest):
    x: list[Num]


class TransportRequest(BaseModel):
    supply: list[Num] = Field(min_length=1)
    demand: list[Num] = Field(min_length=1)
    cost: list[list[Num]] = Field(min_length=1)
    method: Literal["northwest", "least_cost", "least_cost_row", "least_cost_column"] = "northwest"
