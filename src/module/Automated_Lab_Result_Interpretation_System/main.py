
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

from models import InterpretationRuleCreate, PatternCreate, map_interpretation_rule_read, map_pattern_read

@app.post("/rules/", status_code=201)
def create_rule(payload: InterpretationRuleCreate) -> dict[str, str]:
    rules_collection = get_collection("interpretation_rules")
    document = payload.model_dump()
    document["CreatedTimestamp"] = document.get("CreatedTimestamp") or datetime.utcnow().isoformat()

    insert_result = rules_collection.insert_one(document)
    return {
        "message": "Interpretation rule created",
        "RuleID": str(insert_result.inserted_id),
    }


@app.get("/rules/")
def list_rules() -> list[dict[str, Any]]:
    rules_collection = get_collection("interpretation_rules")
    docs = rules_collection.find({}).limit(1000)
    return [map_interpretation_rule_read(doc) for doc in docs]


@app.get("/rules/{rule_id}")
def get_rule(rule_id: str) -> dict[str, Any]:
    if not ObjectId.is_valid(rule_id):
        raise HTTPException(status_code=400, detail="Invalid rule id")

    rules_collection = get_collection("interpretation_rules")
    doc = rules_collection.find_one({"_id": ObjectId(rule_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Rule not found")

    return map_interpretation_rule_read(doc)


@app.patch("/rules/{rule_id}/detects-pattern/{pattern_id}")
def link_rule_detects_pattern(rule_id: str, pattern_id: str) -> dict[str, Any]:
    if not ObjectId.is_valid(rule_id) or not ObjectId.is_valid(pattern_id):
        raise HTTPException(status_code=400, detail="Invalid ids")

    rules_collection = get_collection("interpretation_rules")
    patterns_collection = get_collection("patterns")

    pattern = patterns_collection.find_one({"_id": ObjectId(pattern_id)})
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    updated = rules_collection.find_one_and_update(
        {"_id": ObjectId(rule_id)},
        {"$addToSet": {"DetectedPatternIDs": pattern_id}},
        return_document=ReturnDocument.AFTER,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Rule not found")

    return map_interpretation_rule_read(updated)


@app.post("/patterns/", status_code=201)
def create_pattern(payload: PatternCreate) -> dict[str, str]:
    patterns_collection = get_collection("patterns")
    document = payload.model_dump()
    document["CreatedTimestamp"] = document.get("CreatedTimestamp") or datetime.utcnow().isoformat()

    insert_result = patterns_collection.insert_one(document)
    return {"PatternID": str(insert_result.inserted_id), "message": "Pattern created"}


@app.get("/patterns/")
def list_patterns() -> list[dict[str, Any]]:
    patterns_collection = get_collection("patterns")
    docs = patterns_collection.find({}).limit(1000)
    return [map_pattern_read(doc) for doc in docs]


@app.get("/patterns/{pattern_id}")
def get_pattern(pattern_id: str) -> dict[str, Any]:
    if not ObjectId.is_valid(pattern_id):
        raise HTTPException(status_code=400, detail="Invalid pattern id")

    patterns_collection = get_collection("patterns")
    doc = patterns_collection.find_one({"_id": ObjectId(pattern_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Pattern not found")

    return map_pattern_read(doc)

# =====================================================================================
# MEMBER 3 CODE START
# Owns APIs here: /recommendations/* and /evaluate/{patient_id}
# =====================================================================================
