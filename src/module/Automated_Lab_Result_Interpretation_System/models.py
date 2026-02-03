from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RuleTypeEnum(str, Enum):
    SINGLE = "Single"
    MULTIPLE = "Multiple"
    TEMPORAL = "Temporal"


# =====================================================================================
# MEMBER 1 CODE START
# Owns model: LabResultCreate and map_lab_result_read
# =====================================================================================
class LabResultCreate(BaseModel):
    PatientID: str = Field(min_length=1)
    TestName: str = Field(min_length=1)
    TestValue: float
    Units: str = Field(min_length=1)
    ResultTimestamp: datetime
    TriggeredRuleIDs: list[str] = Field(default_factory=list)
    DetectedPatternIDs: list[str] = Field(default_factory=list)


def map_lab_result_read(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "ResultID": str(document["_id"]),
        "PatientID": document["PatientID"],
        "TestName": document["TestName"],
        "TestValue": document["TestValue"],
        "Units": document["Units"],
        "ResultTimestamp": _as_iso(document.get("ResultTimestamp")),
        "TriggeredRuleIDs": document.get("TriggeredRuleIDs", []),
        "DetectedPatternIDs": document.get("DetectedPatternIDs", []),
    }


# =====================================================================================
# MEMBER 2 CODE START
# Owns models: InterpretationRuleCreate, PatternCreate
# Owns mappers: map_interpretation_rule_read, map_pattern_read
# =====================================================================================


# =====================================================================================
# MEMBER 3 CODE START
# Owns model: RecommendationCreate
# Owns mapper: map_recommendation_read
# =====================================================================================


def _as_iso(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, str):
        return value
    return None
