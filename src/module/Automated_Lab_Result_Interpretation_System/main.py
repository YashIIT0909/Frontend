
import operator
import re
from datetime import datetime
from typing import Any, Callable

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from pymongo import ReturnDocument

from database import close_mongo, connect_to_mongo, get_collection, get_lab_results_collection
from models import LabResultCreate, map_lab_result_read

from models import RecommendationCreate, map_recommendation_read

app = FastAPI(title="Result Interpretation Engine API")


@app.on_event("startup")
def on_startup() -> None:
    connect_to_mongo()


@app.on_event("shutdown")
def on_shutdown() -> None:
    close_mongo()


@app.post("/lab-results/", status_code=201)
def create_lab_result(payload: LabResultCreate) -> dict[str, str]:
    lab_results_collection = get_lab_results_collection()
    document = payload.model_dump()
    insert_result = lab_results_collection.insert_one(document)
    return {
        "message": "Lab result created successfully",
        "ResultID": str(insert_result.inserted_id),
    }


@app.get("/patients/{patient_id}/results")
def get_patient_results(patient_id: str) -> list[dict[str, Any]]:
    lab_results_collection = get_lab_results_collection()
    documents = (
        lab_results_collection.find({"PatientID": patient_id})
        .sort("ResultTimestamp", -1)
        .limit(1000)
    )
    return [map_lab_result_read(document) for document in documents]

# =====================================================================================
# MEMBER 2 CODE START
# Owns APIs here: all /rules/* and /patterns/* endpoints
# =====================================================================================


# =====================================================================================
# MEMBER 3 CODE START
# Owns APIs here: /recommendations/* and /evaluate/{patient_id}
# =====================================================================================
from models import RecommendationCreate, map_recommendation_read

@app.get("/patients/{patient_id}/recommendations")
def get_patient_recommendations(patient_id: str) -> list[dict[str, Any]]:
    recommendations_collection = get_collection("recommendations")
    documents = (
        recommendations_collection.find({"PatientID": patient_id})
        .sort("CreatedTimestamp", -1)
        .limit(1000)
    )
    return [map_recommendation_read(document) for document in documents]


@app.post("/recommendations/", status_code=201)
def create_recommendation(payload: RecommendationCreate) -> dict[str, str]:
    recommendations_collection = get_collection("recommendations")
    document = payload.model_dump()
    document["CreatedTimestamp"] = document.get("CreatedTimestamp") or datetime.utcnow().isoformat()

    insert_result = recommendations_collection.insert_one(document)
    return {
        "message": "Recommendation created",
        "RecommendationID": str(insert_result.inserted_id),
    }


@app.post("/evaluate/{patient_id}")
def evaluate_patient(patient_id: str) -> dict[str, Any]:
    lab_results_collection = get_lab_results_collection()
    recommendations_collection = get_collection("recommendations")
    rules_collection = get_collection("interpretation_rules")

    lab_results = (
        lab_results_collection.find({"PatientID": patient_id})
        .sort("ResultTimestamp", -1)
        .limit(100)
    )
    lab_results = list(lab_results)

    if not lab_results:
        raise HTTPException(status_code=404, detail="No lab results found for this patient")

    rules = list(rules_collection.find({}))
    if not rules:
        raise HTTPException(status_code=404, detail="No interpretation rules available")

    now = datetime.utcnow().isoformat()
    generated_docs: list[dict[str, Any]] = []

    for result in lab_results:
        for rule in rules:
            if _evaluate_logic_condition(rule.get("LogicCondition", ""), float(result.get("TestValue", 0))):
                generated_docs.append(
                    {
                        "PatientID": patient_id,
                        "SourceRuleID": str(rule["_id"]),
                        "SourcePatternID": None,
                        "SuggestionText": rule.get("RuleDescription")
                        or f'Rule "{rule.get("RuleName", "Unknown")}" triggered for {result.get("TestName", "test")}',
                        "FollowUpTestName": result.get("TestName"),
                        "CreatedTimestamp": now,
                    }
                )

    if not generated_docs:
        return {"message": "Evaluation complete — no rules triggered", "generated": []}

    insert_result = recommendations_collection.insert_many(generated_docs)
    generated = []

    for index, _id in enumerate(insert_result.inserted_ids):
        generated_docs[index]["_id"] = _id
        generated.append(map_recommendation_read(generated_docs[index]))

    return {
        "message": f"Evaluation complete — {len(generated)} recommendation(s) generated",
        "generated": generated,
    }


_CONDITION_REGEX = re.compile(r"^\s*TestValue\s*(==|!=|>=|<=|>|<)\s*(-?\d+(?:\.\d+)?)\s*$")
_OPERATORS: dict[str, Callable[[float, float], bool]] = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
}


def _evaluate_logic_condition(logic_condition: str, test_value: float) -> bool:
    match = _CONDITION_REGEX.match(logic_condition)
    if not match:
        return False

    op_symbol, raw_threshold = match.group(1), match.group(2)
    threshold = float(raw_threshold)
    return _OPERATORS[op_symbol](test_value, threshold)