from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict
from pathlib import Path

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import PredictionHistory

import numpy as np
import pandas as pd
import joblib


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="SIH26071 Early Warning System",
    description="Rainfall and Flood Risk Prediction Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAINFALL_DIR = BASE_DIR / "models" / "rainfall"
FLOOD_DIR = BASE_DIR / "models" / "flood"


# ============================================================
# MODEL VARIABLES
# ============================================================

rainfall_model = None
rainfall_features = []
rainfall_categorical_cols = []

flood_model = None
flood_features = []
flood_categorical_cols = []


# ============================================================
# DATABASE SAVE FUNCTION
# ============================================================

def save_prediction(
    prediction_type,
    risk_level,
    predicted_class,
    confidence_score,
    probabilities=None,
    overall_status=None
):
    db: Session = SessionLocal()

    try:
        record = PredictionHistory(
            prediction_type=prediction_type,
            risk_level=risk_level,
            predicted_class=predicted_class,
            confidence_score=confidence_score,
            probabilities=probabilities,
            overall_status=overall_status
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# MODEL LOADING FUNCTION
# ============================================================

def load_model_files():

    global rainfall_model
    global rainfall_features
    global rainfall_categorical_cols

    global flood_model
    global flood_features
    global flood_categorical_cols


    # ========================================================
    # RAINFALL MODEL
    # ========================================================

    try:

        rainfall_model = joblib.load(
            RAINFALL_DIR / "heavy_rain_model.pkl"
        )

        rainfall_features = joblib.load(
            RAINFALL_DIR / "model_features.pkl"
        )

        rainfall_categorical_cols = joblib.load(
            RAINFALL_DIR / "categorical_cols.pkl"
        )

        print("=" * 60)
        print("Rainfall model loaded successfully.")
        print("Rainfall feature count:", len(rainfall_features))
        print("Rainfall features:")
        print(rainfall_features)
        print("Rainfall categorical columns:")
        print(rainfall_categorical_cols)
        print("=" * 60)

    except Exception as e:

        rainfall_model = None
        rainfall_features = []
        rainfall_categorical_cols = []

        print("=" * 60)
        print("Rainfall model could not be loaded.")
        print("Error:", e)
        print("=" * 60)


    # ========================================================
    # FLOOD MODEL
    # ========================================================

    try:

        flood_model = joblib.load(
            FLOOD_DIR / "flood_risk_model.pkl"
        )

        flood_features = joblib.load(
            FLOOD_DIR / "model_features.pkl"
        )

        flood_categorical_cols = joblib.load(
            FLOOD_DIR / "categorical_cols.pkl"
        )

        print("=" * 60)
        print("Flood model loaded successfully.")
        print("Flood feature count:", len(flood_features))
        print("Flood features:")
        print(flood_features)
        print("Flood categorical columns:")
        print(flood_categorical_cols)
        print("=" * 60)

    except Exception as e:

        flood_model = None
        flood_features = []
        flood_categorical_cols = []

        print("=" * 60)
        print("Flood model could not be loaded.")
        print("Error:", e)
        print("=" * 60)


# ============================================================
# LOAD MODELS WHEN BACKEND STARTS
# ============================================================

load_model_files()


# ============================================================
# REQUEST MODEL
# ============================================================

class PredictionRequest(BaseModel):
    features: Dict[str, Any]


# ============================================================
# COMBINED REQUEST MODEL
# ============================================================

class CombinedPredictionRequest(BaseModel):
    rainfall_features: Dict[str, Any]
    flood_features: Dict[str, Any]


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "SIH26071 Backend is running"
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/api/health")
def health():

    return {
        "status": "healthy",

        "rainfall_model_loaded": (
            rainfall_model is not None
        ),

        "flood_model_loaded": (
            flood_model is not None
        )
    }


# ============================================================
# MODEL INFORMATION
# ============================================================

@app.get("/api/models")
def model_information():

    return {

        "rainfall": {

            "loaded":
                rainfall_model is not None,

            "feature_count":
                len(rainfall_features),

            "features":
                rainfall_features,

            "categorical_columns":
                rainfall_categorical_cols
        },

        "flood": {

            "loaded":
                flood_model is not None,

            "feature_count":
                len(flood_features),

            "features":
                flood_features,

            "categorical_columns":
                flood_categorical_cols
        }
    }


# ============================================================
# FEATURE VALIDATION FUNCTION
# ============================================================

def validate_features(
    received_features,
    expected_features
):

    received = set(
        received_features.keys()
    )

    expected = set(
        expected_features
    )

    missing_features = list(
        expected - received
    )

    extra_features = list(
        received - expected
    )

    return missing_features, extra_features


# ============================================================
# CREATE MODEL DATAFRAME
# ============================================================

def create_input_dataframe(
    features,
    expected_features,
    categorical_columns
):

    values = []

    for feature in expected_features:

        values.append(
            features[feature]
        )

    input_df = pd.DataFrame(
        [values],
        columns=expected_features
    )

    # Restore categorical columns

    for column in categorical_columns:

        if column in input_df.columns:

            input_df[column] = (
                input_df[column]
                .astype("category")
            )

    return input_df


# ============================================================
# RAINFALL PREDICTION
# ============================================================

@app.post("/api/predict/rainfall")
def predict_rainfall(
    request: PredictionRequest
):

    if rainfall_model is None:

        raise HTTPException(
            status_code=503,
            detail="Rainfall model is not loaded."
        )


    # ========================================================
    # VALIDATE FEATURES
    # ========================================================

    missing_features, extra_features = (
        validate_features(
            request.features,
            rainfall_features
        )
    )


    if missing_features or extra_features:

        raise HTTPException(

            status_code=400,

            detail={

                "message":
                    "Incorrect features supplied.",

                "expected_feature_count":
                    len(rainfall_features),

                "received_feature_count":
                    len(request.features),

                "missing_features":
                    missing_features,

                "extra_features":
                    extra_features,

                "expected_features":
                    rainfall_features
            }
        )


    try:

        # ====================================================
        # CREATE DATAFRAME
        # ====================================================

        input_df = create_input_dataframe(
            request.features,
            rainfall_features,
            rainfall_categorical_cols
        )


        # ====================================================
        # PREDICTION
        # ====================================================

        probabilities = (
            rainfall_model
            .predict_proba(input_df)[0]
        )


        predicted_class = int(
            np.argmax(probabilities)
        )


        confidence = float(
            np.max(probabilities)
        )


        # ====================================================
        # RISK MAPPING
        # ====================================================

        risk_mapping = {

            0: "Low",

            1: "Moderate",

            2: "High"
        }


        risk_level = risk_mapping.get(
            predicted_class,
            "Unknown"
        )


        probability_percentages = [

            round(
                float(probability) * 100,
                2
            )

            for probability in probabilities
        ]


        confidence_score = round(
            confidence * 100,
            2
        )


        # ====================================================
        # SAVE TO DATABASE
        # ====================================================

        prediction_id = save_prediction(

            prediction_type="rainfall",

            risk_level=risk_level,

            predicted_class=predicted_class,

            confidence_score=confidence_score,

            probabilities=probability_percentages
        )


        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "model":
                "heavy_rain_model",

            "prediction_id":
                prediction_id,

            "risk_level":
                risk_level,

            "predicted_class":
                predicted_class,

            "confidence_score":
                confidence_score,

            "probabilities":
                probability_percentages
        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                f"Rainfall prediction failed: {str(e)}"
            )
        )


# ============================================================
# FLOOD PREDICTION
# ============================================================

@app.post("/api/predict/flood")
def predict_flood(
    request: PredictionRequest
):

    if flood_model is None:

        raise HTTPException(
            status_code=503,
            detail="Flood model is not loaded."
        )


    # ========================================================
    # VALIDATE FEATURES
    # ========================================================

    missing_features, extra_features = (
        validate_features(
            request.features,
            flood_features
        )
    )


    if missing_features or extra_features:

        raise HTTPException(

            status_code=400,

            detail={

                "message":
                    "Incorrect features supplied.",

                "expected_feature_count":
                    len(flood_features),

                "received_feature_count":
                    len(request.features),

                "missing_features":
                    missing_features,

                "extra_features":
                    extra_features,

                "expected_features":
                    flood_features
            }
        )


    try:

        # ====================================================
        # CREATE DATAFRAME
        # ====================================================

        input_df = create_input_dataframe(

            request.features,

            flood_features,

            flood_categorical_cols
        )


        # ====================================================
        # PREDICTION
        # ====================================================

        probabilities = (
            flood_model
            .predict_proba(input_df)[0]
        )


        predicted_class = int(
            np.argmax(probabilities)
        )


        confidence = float(
            np.max(probabilities)
        )


        # ====================================================
        # RISK MAPPING
        # ====================================================

        risk_mapping = {

            0: "Low/Moderate Risk",

            1: "Severe Flood Risk"
        }


        risk_level = risk_mapping.get(

            predicted_class,

            "Unknown"
        )


        probability_percentages = [

            round(
                float(probability) * 100,
                2
            )

            for probability in probabilities
        ]


        confidence_score = round(
            confidence * 100,
            2
        )


        # ====================================================
        # SAVE TO DATABASE
        # ====================================================

        prediction_id = save_prediction(

            prediction_type="flood",

            risk_level=risk_level,

            predicted_class=predicted_class,

            confidence_score=confidence_score,

            probabilities=probability_percentages
        )


        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "model":
                "flood_risk_model",

            "prediction_id":
                prediction_id,

            "risk_level":
                risk_level,

            "predicted_class":
                predicted_class,

            "confidence_score":
                confidence_score,

            "probabilities":
                probability_percentages
        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                f"Flood prediction failed: {str(e)}"
            )
        )


# ============================================================
# COMBINED EARLY WARNING PREDICTION
# ============================================================

@app.post("/api/predict/combined")
def predict_combined(
    request: CombinedPredictionRequest
):

    # ========================================================
    # CHECK MODELS
    # ========================================================

    if rainfall_model is None:

        raise HTTPException(

            status_code=503,

            detail="Rainfall model is not loaded."
        )


    if flood_model is None:

        raise HTTPException(

            status_code=503,

            detail="Flood model is not loaded."
        )


    try:

        # ====================================================
        # RAINFALL INPUT
        # ====================================================

        rainfall_input = {}


        for feature in rainfall_features:

            if feature not in request.rainfall_features:

                raise HTTPException(

                    status_code=400,

                    detail={

                        "message":
                            "Missing rainfall feature.",

                        "missing_feature":
                            feature
                    }
                )


            rainfall_input[feature] = (
                request.rainfall_features[feature]
            )


        rainfall_df = pd.DataFrame(

            [rainfall_input],

            columns=rainfall_features
        )


        # Restore categorical columns

        for col in rainfall_categorical_cols:

            if col in rainfall_df.columns:

                rainfall_df[col] = (
                    rainfall_df[col]
                    .astype("category")
                )


        # ====================================================
        # RAINFALL PREDICTION
        # ====================================================

        rainfall_probabilities = (

            rainfall_model
            .predict_proba(rainfall_df)[0]

        )


        rainfall_class = int(

            np.argmax(
                rainfall_probabilities
            )
        )


        rainfall_confidence = float(

            np.max(
                rainfall_probabilities
            )
        )


        rainfall_mapping = {

            0: "Low",

            1: "Moderate",

            2: "High"
        }


        rainfall_risk_level = (
            rainfall_mapping.get(
                rainfall_class,
                "Unknown"
            )
        )


        rainfall_probability_percentages = [

            round(
                float(x) * 100,
                2
            )

            for x in rainfall_probabilities
        ]


        rainfall_confidence_score = round(

            rainfall_confidence * 100,

            2
        )


        rainfall_result = {

            "risk_level":
                rainfall_risk_level,

            "predicted_class":
                rainfall_class,

            "confidence_score":
                rainfall_confidence_score,

            "probabilities":
                rainfall_probability_percentages
        }


        # ====================================================
        # FLOOD INPUT
        # ====================================================

        flood_input = {}


        for feature in flood_features:

            if feature not in request.flood_features:

                raise HTTPException(

                    status_code=400,

                    detail={

                        "message":
                            "Missing flood feature.",

                        "missing_feature":
                            feature
                    }
                )


            flood_input[feature] = (
                request.flood_features[feature]
            )


        flood_df = pd.DataFrame(

            [flood_input],

            columns=flood_features
        )


        # Restore categorical columns

        for col in flood_categorical_cols:

            if col in flood_df.columns:

                flood_df[col] = (
                    flood_df[col]
                    .astype("category")
                )


        # ====================================================
        # FLOOD PREDICTION
        # ====================================================

        flood_probabilities = (

            flood_model
            .predict_proba(flood_df)[0]

        )


        flood_class = int(

            np.argmax(
                flood_probabilities
            )
        )


        flood_confidence = float(

            np.max(
                flood_probabilities
            )
        )


        flood_mapping = {

            0: "Low/Moderate Risk",

            1: "Severe Flood Risk"
        }


        flood_risk_level = (

            flood_mapping.get(

                flood_class,

                "Unknown"
            )
        )


        flood_probability_percentages = [

            round(
                float(x) * 100,
                2
            )

            for x in flood_probabilities
        ]


        flood_confidence_score = round(

            flood_confidence * 100,

            2
        )


        flood_result = {

            "risk_level":
                flood_risk_level,

            "predicted_class":
                flood_class,

            "confidence_score":
                flood_confidence_score,

            "probabilities":
                flood_probability_percentages
        }


        # ====================================================
        # COMBINED ALERT LOGIC
        # ====================================================

        if (

            rainfall_class == 2

            or flood_class == 1

        ):

            overall_status = "High Alert"


        elif (

            rainfall_class == 1

            or flood_class == 0

        ):

            overall_status = "Moderate Alert"


        else:

            overall_status = "Low Alert"


        # ====================================================
        # SAVE RAINFALL PREDICTION
        # ====================================================

        rainfall_prediction_id = save_prediction(

            prediction_type="rainfall",

            risk_level=rainfall_risk_level,

            predicted_class=rainfall_class,

            confidence_score=rainfall_confidence_score,

            probabilities=rainfall_probability_percentages,

            overall_status=overall_status
        )


        # ====================================================
        # SAVE FLOOD PREDICTION
        # ====================================================

        flood_prediction_id = save_prediction(

            prediction_type="flood",

            risk_level=flood_risk_level,

            predicted_class=flood_class,

            confidence_score=flood_confidence_score,

            probabilities=flood_probability_percentages,

            overall_status=overall_status
        )


        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        return {

            "model":
                "SIH26071 Combined Early Warning System",

            "rainfall": {

                **rainfall_result,

                "prediction_id":
                    rainfall_prediction_id
            },

            "flood": {

                **flood_result,

                "prediction_id":
                    flood_prediction_id
            },

            "overall_status":
                overall_status
        }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                f"Combined prediction failed: {str(e)}"
            )
        )


# ============================================================
# DATABASE HISTORY ENDPOINT
# ============================================================

@app.get("/api/predictions")
def get_prediction_history():

    db: Session = SessionLocal()

    try:

        records = (

            db.query(
                PredictionHistory
            )

            .order_by(
                PredictionHistory.created_at.desc()
            )

            .limit(100)

            .all()
        )


        return [

            {

                "id":
                    record.id,

                "prediction_type":
                    record.prediction_type,

                "risk_level":
                    record.risk_level,

                "predicted_class":
                    record.predicted_class,

                "confidence_score":
                    record.confidence_score,

                "probabilities":
                    record.probabilities,

                "overall_status":
                    record.overall_status,

                "created_at":
                    record.created_at
                    .isoformat()
            }

            for record in records
        ]


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                f"Could not fetch prediction history: {str(e)}"
            )
        )


    finally:

        db.close()