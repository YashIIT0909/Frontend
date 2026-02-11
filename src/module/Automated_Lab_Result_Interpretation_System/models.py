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

class InterpretationRuleCreate(BaseModel):
    RuleName: str = Field(min_length=1)
    RuleDescription: str | None = None
    RuleType: RuleTypeEnum
    LogicCondition: str = Field(min_length=1)
    ConfidenceScore: float = Field(default=0.5, ge=0, le=1)
    GeneratedRecommendationIDs: list[str] = Field(default_factory=list)
    DetectedPatternIDs: list[str] = Field(default_factory=list)
    CreatedTimestamp: datetime | None = None


class PatternCreate(BaseModel):
    PatternName: str = Field(min_length=1)
    PatternDescription: str | None = None
    PatternLogic: str = Field(min_length=1)
    ProbabilityCalculation: float | None = Field(default=None, ge=0, le=1)
    GeneratedRecommendationIDs: list[str] = Field(default_factory=list)
    CreatedTimestamp: datetime | None = None


def map_interpretation_rule_read(document: dict[str, Any]) -> dict[str, Any]:
    confidence = document.get("ConfidenceScore")
    return {
        "RuleID": str(document["_id"]),
        "RuleName": document["RuleName"],
        "RuleDescription": document.get("RuleDescription"),
        "RuleType": document["RuleType"],
        "LogicCondition": document["LogicCondition"],
        "ConfidenceScore": confidence if isinstance(confidence, (int, float)) else 0.5,
        "GeneratedRecommendationIDs": document.get("GeneratedRecommendationIDs", []),
        "DetectedPatternIDs": document.get("DetectedPatternIDs", []),
        "CreatedTimestamp": _as_iso(document.get("CreatedTimestamp")),
    }


def map_pattern_read(document: dict[str, Any]) -> dict[str, Any]:
    probability = document.get("ProbabilityCalculation")
    return {
        "PatternID": str(document["_id"]),
        "PatternName": document["PatternName"],
        "PatternDescription": document.get("PatternDescription"),
        "PatternLogic": document["PatternLogic"],
        "ProbabilityCalculation": probability if isinstance(probability, (int, float)) else None,
        "GeneratedRecommendationIDs": document.get("GeneratedRecommendationIDs", []),
        "CreatedTimestamp": _as_iso(document.get("CreatedTimestamp")),
    }

# =====================================================================================
# MEMBER 3 CODE START
# Owns model: RecommendationCreate
# Owns mapper: map_recommendation_read
# =====================================================================================
class RecommendationCreate(BaseModel):
    PatientID: str = Field(min_length=1)
    SourceRuleID: str = Field(min_length=1)
    SourcePatternID: str | None = None
    SuggestionText: str = Field(min_length=1)
    FollowUpTestName: str | None = None
    CreatedTimestamp: datetime | None = None


def map_recommendation_read(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "RecommendationID": str(document["_id"]),
        "PatientID": document["PatientID"],
        "SourceRuleID": document["SourceRuleID"],
        "SourcePatternID": document.get("SourcePatternID"),
        "SuggestionText": document["SuggestionText"],
        "FollowUpTestName": document.get("FollowUpTestName"),
        "CreatedTimestamp": _as_iso(document.get("CreatedTimestamp")),
    }

def _as_iso(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, str):
        return value
    return None
