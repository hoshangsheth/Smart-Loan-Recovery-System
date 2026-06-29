"""
Prediction route.

Per architecture rules: this route only receives the request, delegates to
services, and shapes the response. No calculation, model call, or business
rule lives here.
"""
from fastapi import APIRouter, Depends

from api.schemas.borrower import BorrowerInput, PredictionResult
from models.loader import MLArtifacts, get_ml_artifacts
from services import feature_engineering, prediction_service, segmentation_service, shap_service
from utils.borrower_id import generate_borrower_id

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("", response_model=PredictionResult)
def predict_risk(payload: BorrowerInput, artifacts: MLArtifacts = Depends(get_ml_artifacts)) -> PredictionResult:
    """
    Run the full pipeline for one borrower: feature engineering -> risk
    model -> strategy assignment -> segmentation -> SHAP explainability.
    """
    engineered = feature_engineering.engineer_features(
        loan_type=payload.loan_type.value,
        loan_amount=payload.loan_amount,
        collateral_value=payload.collateral_value,
        monthly_income=payload.monthly_income,
        missed_payments=payload.missed_payments,
        interest_rate=payload.interest_rate,
        loan_tenure=payload.loan_tenure,
    )

    model_vector = prediction_service.build_model_feature_vector(
        age=payload.age,
        monthly_income=payload.monthly_income,
        num_dependents=payload.num_dependents,
        engineered=engineered,
        outstanding_loan=payload.outstanding_loan,
    )
    risk_score = prediction_service.predict_risk_score(artifacts, model_vector)
    strategy_info = prediction_service.assign_recovery_strategy(risk_score, engineered.days_past_due)

    segmentation_vector = segmentation_service.build_segmentation_feature_vector(
    age=payload.age,
    monthly_income=payload.monthly_income,
    num_dependents=payload.num_dependents,
    outstanding_loan=payload.outstanding_loan,
    engineered=engineered,
    )
    segment = segmentation_service.assign_segment(artifacts, segmentation_vector)

    shap_top_features = shap_service.compute_shap_top_features(artifacts, model_vector)

    borrower_id = generate_borrower_id(payload.loan_type.value, payload.first_name, payload.last_name)

    return PredictionResult(
        borrower_id=borrower_id,
        risk_score=risk_score,
        risk_category=strategy_info["label"],
        strategy=strategy_info["strategy"],
        calculated={
            "monthly_emi": engineered.monthly_emi or 0.0,
            "days_past_due": engineered.days_past_due,
            "collection_attempts": engineered.collection_attempts,
            "emi_to_income_ratio": engineered.emi_to_income_ratio or 0.0,
            "collateral_coverage": engineered.collateral_coverage or 0.0,
            "default_severity": engineered.default_severity,
            "interest_rate_used": engineered.interest_rate_used,
            "loan_tenure_used": engineered.loan_tenure_used,
        },
        segment={
            "segment_id": segment["segment_id"],
            "segment_name": segment["segment_name"],
            "description": segment["description"],
        },
        shap_top_features=shap_top_features,
        input=payload,
    )
