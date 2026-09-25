"""Full scoring pipeline for one borrower: features -> risk model -> strategy -> segment -> SHAP."""
from api.schemas.borrower import BorrowerInput, PredictionResult
from models.loader import MLArtifacts
from services import feature_engineering, prediction_service, segmentation_service, shap_service
from utils.borrower_id import generate_borrower_id


def score_borrower(payload: BorrowerInput, artifacts: MLArtifacts, borrower_id: str | None = None) -> PredictionResult:
    engineered = feature_engineering.engineer_features(
        loan_type=payload.loan_type.value,
        loan_amount=payload.loan_amount,
        collateral_value=payload.collateral_value,
        monthly_income=payload.monthly_income,
        missed_payments=payload.missed_payments,
        days_past_due=payload.days_past_due,
        collection_attempts=payload.collection_attempts,
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
    assessment = prediction_service.assess_risk(risk_score, engineered.days_past_due)

    segmentation_vector = segmentation_service.build_segmentation_feature_vector(
        age=payload.age,
        monthly_income=payload.monthly_income,
        num_dependents=payload.num_dependents,
        outstanding_loan=payload.outstanding_loan,
        engineered=engineered,
    )
    segment = segmentation_service.assign_segment(artifacts, segmentation_vector)
    shap_top_features = shap_service.compute_shap_top_features(artifacts, model_vector)

    return PredictionResult(
        borrower_id=borrower_id
        or generate_borrower_id(payload.loan_type.value, payload.first_name, payload.last_name),
        model_version=artifacts.model_version,
        risk_score=risk_score,
        risk_category=assessment.label,
        risk_tier=assessment.tier,
        risk_band=assessment.band,
        asset_classification=assessment.asset_classification,
        policy_override=assessment.policy_override,
        risk_warning=assessment.warning,
        strategy=assessment.strategy,
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
        segment=segment,
        shap_top_features=shap_top_features,
        input=payload,
    )
