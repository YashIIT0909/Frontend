
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
