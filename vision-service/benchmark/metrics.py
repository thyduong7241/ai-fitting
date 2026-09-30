"""
Quantitative Benchmark Metrics Calculator for Vision Service.
Implements formulas from Section 3.1 of VISION_SERVICE_MICROSERVICE_AND_BENCHMARK_PLAN.md:
- Confusion Matrix, Precision, Recall, F1-Score, Blur Accuracy
- MAE, RMSE, MAPE, Tolerance Pass Rate (+-3cm), Error Std Dev (Repeatability)
"""

import math
from typing import Dict, List, Optional
from pydantic import BaseModel


class QualityMetrics(BaseModel):
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0
    total: int = 0
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    false_rejection_rate: float = 0.0
    blur_accuracy: float = 0.0


class MeasurementPartMetric(BaseModel):
    part: str
    sample_count: int
    mae: float
    rmse: float
    mape: float
    tolerance_rate_3cm: float  # % within +-3.0cm
    std_dev: float             # repeatability sigma


class OverallMeasurementMetrics(BaseModel):
    sample_count: int
    overall_mae: float
    overall_rmse: float
    overall_mape: float
    overall_tolerance_rate_3cm: float
    part_metrics: Dict[str, MeasurementPartMetric]


def calculate_quality_metrics(
    evaluations: List[Dict[str, any]],
) -> QualityMetrics:
    """
    Evaluate binary classification of invalid images (positive = has issue / invalid).
    """
    tp = 0  # correctly identified as invalid/having issue
    fp = 0  # valid image wrongly flagged as invalid
    tn = 0  # correctly identified as valid
    fn = 0  # invalid image wrongly passed as valid

    blur_correct = 0
    blur_total = 0

    valid_total = 0
    valid_rejected = 0

    for item in evaluations:
        expected_valid = item["expected_valid"]
        predicted_valid = item["predicted_valid"]
        expected_issues = set(item.get("expected_issues", []))
        predicted_issues = set(item.get("predicted_issues", []))

        # Ground truth: positive = invalid
        is_ground_truth_invalid = not expected_valid
        is_predicted_invalid = not predicted_valid

        if is_ground_truth_invalid:
            if is_predicted_invalid:
                tp += 1
            else:
                fn += 1
        else:
            valid_total += 1
            if is_predicted_invalid:
                fp += 1
                valid_rejected += 1
            else:
                tn += 1

        # Check blur accuracy specifically if blur is tested
        if "blurry" in expected_issues or "blurry" in predicted_issues:
            blur_total += 1
            if ("blurry" in expected_issues) == ("blurry" in predicted_issues):
                blur_correct += 1

    total = len(evaluations)
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    frr = (valid_rejected / valid_total) * 100 if valid_total > 0 else 0.0
    blur_acc = (blur_correct / blur_total) * 100 if blur_total > 0 else 100.0

    return QualityMetrics(
        tp=tp,
        fp=fp,
        tn=tn,
        fn=fn,
        total=total,
        accuracy=round(accuracy * 100, 2),
        precision=round(precision * 100, 2),
        recall=round(recall * 100, 2),
        f1_score=round(f1 * 100, 2),
        false_rejection_rate=round(frr, 2),
        blur_accuracy=round(blur_acc, 2),
    )


def calculate_measurement_metrics(
    evaluations: List[Dict[str, any]],
    tolerance_cm: float = 3.0,
) -> OverallMeasurementMetrics:
    """
    evaluations item format:
    {
        "subject_id": str,
        "ground_truth": {"shoulder": float, "chest": float, ...},
        "predicted": {"shoulder": float, "chest": float, ...}
    }
    """
    parts = ["shoulder", "chest", "waist", "hips", "arm_length", "inseam"]
    part_errors: Dict[str, List[float]] = {p: [] for p in parts}
    part_gt_values: Dict[str, List[float]] = {p: [] for p in parts}

    for item in evaluations:
        gt = item["ground_truth"]
        pred = item["predicted"]
        for p in parts:
            if p in gt and p in pred and pred[p] is not None:
                err = pred[p] - gt[p]
                part_errors[p].append(err)
                part_gt_values[p].append(gt[p])

    part_results: Dict[str, MeasurementPartMetric] = {}
    all_abs_errors: List[float] = []
    all_gt_values: List[float] = []

    for p in parts:
        errors = part_errors[p]
        gts = part_gt_values[p]
        n = len(errors)
        if n == 0:
            continue

        abs_errors = [abs(e) for e in errors]
        all_abs_errors.extend(abs_errors)
        all_gt_values.extend(gts)

        mae = sum(abs_errors) / n
        mse = sum(e ** 2 for e in errors) / n
        rmse = math.sqrt(mse)
        mape = (sum(abs(errors[i]) / gts[i] for i in range(n)) / n) * 100
        within_tol = sum(1 for a in abs_errors if a <= tolerance_cm)
        tpr = (within_tol / n) * 100

        # Standard deviation of error (repeatability sigma)
        mean_err = sum(errors) / n
        var = sum((e - mean_err) ** 2 for e in errors) / n
        std_dev = math.sqrt(var)

        part_results[p] = MeasurementPartMetric(
            part=p,
            sample_count=n,
            mae=round(mae, 2),
            rmse=round(rmse, 2),
            mape=round(mape, 2),
            tolerance_rate_3cm=round(tpr, 2),
            std_dev=round(std_dev, 2),
        )

    total_n = len(all_abs_errors)
    overall_mae = sum(all_abs_errors) / total_n if total_n > 0 else 0.0
    overall_rmse = math.sqrt(sum(a ** 2 for a in all_abs_errors) / total_n) if total_n > 0 else 0.0
    overall_mape = (sum(all_abs_errors[i] / all_gt_values[i] for i in range(total_n)) / total_n * 100) if total_n > 0 else 0.0
    overall_tpr = (sum(1 for a in all_abs_errors if a <= tolerance_cm) / total_n * 100) if total_n > 0 else 0.0

    return OverallMeasurementMetrics(
        sample_count=len(evaluations),
        overall_mae=round(overall_mae, 2),
        overall_rmse=round(overall_rmse, 2),
        overall_mape=round(overall_mape, 2),
        overall_tolerance_rate_3cm=round(overall_tpr, 2),
        part_metrics=part_results,
    )
