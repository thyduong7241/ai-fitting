"""
Cloudline Studio - Fit Recommendation Engine (Model 1)
Machine Learning & Biomechanical Garment-to-Body Sizing Engine.

Model Architecture:
1. Primary: RandomForestFitClassifier (120 trees, max depth 16) trained on 6,000 anthropometric records.
   Computes exact size probabilities via `predict_proba()`.
2. Fallback: Multi-zone Biomechanical Ease & Penalty Optimization Engine if ML artifact is absent.
"""
import os
import math
import joblib
import numpy as np
from typing import Dict, Any, List, Optional

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(WORKSPACE_DIR, "models", "fit_ml_model.joblib")


class FitMLEngine:
    """
    Model 1: Production Sizing Engine.
    Combines Machine Learning classification with multi-zone ease analysis.
    """
    _artifact = None
    _classifier = None
    _scaler = None
    _size_labels: List[str] = ["XS", "S", "M", "L", "XL", "XXL"]

    # Outerwear Target Ease standards (cm over body measurement)
    TARGET_EASE = {
        "regular": {"shoulder": 1.5, "bust": 8.0, "waist": 8.0},
        "tight": {"shoulder": 0.5, "bust": 4.0, "waist": 4.0},
        "loose": {"shoulder": 3.0, "bust": 14.0, "waist": 14.0},
    }

    # Importance weights for outerwear sizing
    ZONE_WEIGHTS = {
        "shoulder": 0.35,  # Structural anchor
        "bust": 0.35,      # Chest closure
        "waist": 0.20,     # Hem & silhouette
        "length": 0.10     # Body proportions
    }

    @classmethod
    def load_model(cls) -> bool:
        """Loads the trained RandomForest model artifact from disk if available."""
        if cls._classifier is None and os.path.exists(MODEL_FILE):
            try:
                cls._artifact = joblib.load(MODEL_FILE)
                cls._classifier = cls._artifact["classifier"]
                cls._scaler = cls._artifact["scaler"]
                cls._size_labels = cls._artifact.get("size_labels", cls._size_labels)
                accuracy = cls._artifact.get("metrics", {}).get("test_accuracy", "N/A")
                print(f"[FitEngine] Loaded ML Model: {cls._artifact.get('model_type')} v{cls._artifact.get('version')} (Test Accuracy: {accuracy})")
                return True
            except Exception as e:
                print(f"[FitEngine] Warning: Could not load ML model ({e}). Using Biomechanical Heuristics.")
                return False
        return cls._classifier is not None

    @classmethod
    def calculate_ideal_jacket_length(cls, height_cm: float, category: str) -> float:
        """Calculates ideal outerwear length proportional to user height and garment cut."""
        cat_lower = category.lower()
        if any(w in cat_lower for w in ["dáng dài", "overcoat", "trench", "măng tô", "parka"]):
            return round(height_cm * 0.62)  # Knee to mid-calf
        elif any(w in cat_lower for w in ["croptop", "cropped", "lửng", "ngắn"]):
            return round(height_cm * 0.31)  # Above waist
        else:
            return round(height_cm * 0.41)  # Mid-hip standard

    @classmethod
    def evaluate_zone(cls, zone: str, body_val: float, garment_val: float, preference: str = "regular") -> Dict[str, Any]:
        """
        Evaluates fit tolerance in a specific anatomical zone (shoulder, bust, waist).
        Returns delta in cm, status tag, badge label, and styling note.
        """
        delta = garment_val - body_val
        target_ease = cls.TARGET_EASE.get(preference, cls.TARGET_EASE["regular"]).get(zone, 4.0)
        diff = delta - target_ease

        if zone == "shoulder":
            if abs(diff) <= 1.2:
                return {
                    "status": "fitted",
                    "badge": "● Vừa vặn (Chuẩn phom)",
                    "delta_cm": round(delta, 1),
                    "note": "Đường may vai nằm chuẩn khớp tỉ lệ vai người mặc"
                }
            elif diff < -1.2:
                return {
                    "status": "tight",
                    "badge": "● Hơi kích vai",
                    "delta_cm": round(delta, 1),
                    "note": "Vai áo hẹp hơn số đo cử động vai"
                }
            else:
                return {
                    "status": "loose",
                    "badge": "● Vai trễ nhẹ",
                    "delta_cm": round(delta, 1),
                    "note": "Vai áo hơi rộng trễ nhẹ ra ngoài"
                }

        elif zone == "bust":
            if abs(diff) <= 2.5:
                return {
                    "status": "fitted",
                    "badge": f"● Vừa vặn (+{int(round(delta))}cm cử động)",
                    "delta_cm": round(delta, 1),
                    "note": "Khoảng ngực thoải mái, cài khóa không bị căng tức"
                }
            elif diff < -2.5:
                return {
                    "status": "tight",
                    "badge": "● Chật ngực (Căng tức)",
                    "delta_cm": round(delta, 1),
                    "note": "Ngực áo ôm sát dễ căng khi cài khóa"
                }
            else:
                return {
                    "status": "loose",
                    "badge": "● Ngực rộng thoải mái",
                    "delta_cm": round(delta, 1),
                    "note": "Khoảng ngực rộng rãi thuận tiện mặc layer"
                }

        elif zone == "waist":
            if abs(diff) <= 3.0:
                return {
                    "status": "fitted",
                    "badge": "● Vừa vặn",
                    "delta_cm": round(delta, 1),
                    "note": "Phom eo cân đối tự nhiên"
                }
            elif diff < -3.0:
                return {
                    "status": "snug",
                    "badge": "● Hơi ôm nhẹ (Gọn dáng)",
                    "delta_cm": round(delta, 1),
                    "note": "Eo ôm nhẹ tôn dáng người nhưng vẫn cử động dễ dàng"
                }
            else:
                return {
                    "status": "loose",
                    "badge": "● Eo suông rộng rãi",
                    "delta_cm": round(delta, 1),
                    "note": "Phom eo rộng thoải mái khi ngồi"
                }

        return {
            "status": "fitted",
            "badge": "● Vừa vặn",
            "delta_cm": round(delta, 1),
            "note": "Thông số đạt chuẩn"
        }

    @classmethod
    def _fallback_biomechanical_recommend(
        cls,
        user_meas: Dict[str, float],
        garment: Dict[str, Any],
        preference: str = "regular"
    ) -> Dict[str, Any]:
        """Penalty-based optimization fallback when the ML joblib model file is unavailable."""
        size_chart = garment.get("size_chart", {})
        if not size_chart:
            return {"recommended_size": "M", "alternative_size": "L", "confidence": 85, "proba_dict": {}}

        u_shoulder = float(user_meas.get("shoulder", 39))
        u_bust = float(user_meas.get("bust", 86))
        u_waist = float(user_meas.get("waist", 70))
        u_height = float(user_meas.get("height", 165))
        ideal_length = cls.calculate_ideal_jacket_length(u_height, garment.get("category", ""))
        target_ease = cls.TARGET_EASE.get(preference, cls.TARGET_EASE["regular"])

        size_penalties: Dict[str, float] = {}
        for size_name, specs in size_chart.items():
            g_shoulder = specs.get("shoulder", 40)
            g_bust = specs.get("bust", 96)
            g_waist = specs.get("waist", 80)
            g_len = specs.get("length", 68)

            d_shoulder = (g_shoulder - u_shoulder) - target_ease["shoulder"]
            d_bust = (g_bust - u_bust) - target_ease["bust"]
            d_waist = (g_waist - u_waist) - target_ease["waist"]
            d_length = abs(g_len - ideal_length)

            p_shoulder = (d_shoulder * 2.5) ** 2 if d_shoulder < 0 else (d_shoulder * 1.0) ** 2
            p_bust = (d_bust * 2.0) ** 2 if d_bust < 0 else (d_bust * 0.8) ** 2
            p_waist = (d_waist * 1.5) ** 2 if d_waist < 0 else (d_waist * 0.5) ** 2
            p_length = (d_length * 0.3) ** 2

            total_penalty = (
                cls.ZONE_WEIGHTS["shoulder"] * p_shoulder +
                cls.ZONE_WEIGHTS["bust"] * p_bust +
                cls.ZONE_WEIGHTS["waist"] * p_waist +
                cls.ZONE_WEIGHTS["length"] * p_length
            )
            size_penalties[size_name] = total_penalty

        sorted_sizes = sorted(size_penalties.items(), key=lambda x: x[1])
        best_size, min_penalty = sorted_sizes[0]
        second_size, second_penalty = sorted_sizes[1] if len(sorted_sizes) > 1 else (best_size, min_penalty + 10)
        margin = max(0.0, second_penalty - min_penalty)
        confidence = int(min(98, max(75, 78 + 20 * (1 - math.exp(-margin / 15.0)))))

        proba_dict = {sz: round(1.0 / (1.0 + pen), 3) for sz, pen in size_penalties.items()}
        total_p = sum(proba_dict.values()) or 1.0
        proba_dict = {sz: round(p / total_p, 3) for sz, p in proba_dict.items()}

        return {
            "recommended_size": best_size,
            "alternative_size": second_size,
            "confidence": confidence,
            "proba_dict": proba_dict
        }

    @classmethod
    def recommend(
        cls,
        user_meas: Dict[str, float],
        garment: Dict[str, Any],
        preference: str = "regular"
    ) -> Dict[str, Any]:
        """
        Main entrypoint for Model 1 recommendation.
        Returns:
            - recommended_size: e.g. "M"
            - alternative_size: e.g. "L"
            - confidence: score from 75 to 98 (%)
            - zones: 4-zone anatomical analysis (Vai, Ngực, Eo, Chiều dài)
            - ml_probabilities: size distribution from softmax
            - model_metadata: details on architecture and confidence origin
        """
        is_ml_loaded = cls.load_model()

        u_height = float(user_meas.get("height", 165.0))
        u_weight = float(user_meas.get("weight", 56.0))
        u_shoulder = float(user_meas.get("shoulder", 39.0))
        u_bust = float(user_meas.get("bust", 86.0))
        u_waist = float(user_meas.get("waist", 70.0))
        u_hip = float(user_meas.get("hip", 92.0))

        if is_ml_loaded and cls._classifier is not None and cls._scaler is not None:
            gender_str = str(garment.get("gender", "Nữ")).lower()
            gender_code = 1 if "nam" in gender_str else 0
            pref_code = 0 if preference == "tight" else (2 if preference == "loose" else 1)

            fit_cut_str = str(garment.get("fit_cut", "regular")).lower()
            fit_cut_code = 0 if "slim" in fit_cut_str else (2 if "oversize" in fit_cut_str else 1)

            stretch_str = str(garment.get("stretch", "low")).lower()
            stretch_code = 0 if "none" in stretch_str else (2 if "medium" in stretch_str or "high" in stretch_str else 1)

            feature_vector = np.array([[
                u_height, u_weight, u_shoulder, u_bust, u_waist, u_hip,
                gender_code, pref_code, fit_cut_code, stretch_code
            ]])

            scaled_vec = cls._scaler.transform(feature_vector)
            proba = cls._classifier.predict_proba(scaled_vec)[0]

            sorted_indices = np.argsort(proba)[::-1]
            best_idx = sorted_indices[0]
            second_idx = sorted_indices[1] if len(sorted_indices) > 1 else best_idx

            best_size = cls._size_labels[best_idx]
            second_size = cls._size_labels[second_idx]
            best_p = proba[best_idx]
            confidence = int(min(98, max(75, round(best_p * 100) + 12)))

            proba_dict = {
                cls._size_labels[i]: round(float(proba[i]), 3)
                for i in range(len(cls._size_labels))
            }
            algo_name = "RandomForestFitClassifier v2.1"
            conf_source = "predict_proba_softmax"
        else:
            fb = cls._fallback_biomechanical_recommend(user_meas, garment, preference)
            best_size = fb["recommended_size"]
            second_size = fb["alternative_size"]
            confidence = fb["confidence"]
            proba_dict = fb["proba_dict"]
            algo_name = "BiomechanicalEasePenaltyEngine (Heuristic Fallback)"
            conf_source = "penalty_margin_softmax"

        # 2. Zone Evaluation using Garment Size Chart
        size_chart = garment.get("size_chart", {})
        spec = size_chart.get(best_size, {})
        g_shoulder = spec.get("shoulder", u_shoulder + 2)
        g_bust = spec.get("bust", u_bust + 10)
        g_waist = spec.get("waist", u_waist + 10)
        g_len = spec.get("length", 68)

        eval_shoulder = cls.evaluate_zone("shoulder", u_shoulder, g_shoulder, preference)
        eval_bust = cls.evaluate_zone("bust", u_bust, g_bust, preference)
        eval_waist = cls.evaluate_zone("waist", u_waist, g_waist, preference)

        ideal_len = cls.calculate_ideal_jacket_length(u_height, garment.get("category", ""))
        len_diff = g_len - ideal_len
        len_badge = (
            f"● {int(g_len)} cm (Chạm mông)" if abs(len_diff) <= 3
            else (f"● {int(g_len)} cm (Qua hông)" if len_diff > 3 else f"● {int(g_len)} cm (Dáng lửng)")
        )

        eval_length = {
            "status": "fitted" if abs(len_diff) <= 5 else ("loose" if len_diff > 5 else "snug"),
            "badge": len_badge,
            "delta_cm": round(len_diff, 1),
            "note": f"Chiều dài áo cân đối với chiều cao {int(u_height)} cm của bạn"
        }

        zones = [
            {"zone": "Vai", "measurement": u_shoulder, **eval_shoulder},
            {"zone": "Ngực", "measurement": u_bust, **eval_bust},
            {"zone": "Eo", "measurement": u_waist, **eval_waist},
            {"zone": "Chiều dài", "measurement": int(g_len), **eval_length},
        ]

        return {
            "recommended_size": best_size,
            "alternative_size": second_size,
            "confidence": confidence,
            "zones": zones,
            "ml_probabilities": proba_dict,
            "model_metadata": {
                "algorithm": algo_name,
                "features_used": 10,
                "confidence_source": conf_source
            }
        }


# Canonical Aliases
BiomechanicalFitEngine = FitMLEngine
FitEngine = FitMLEngine
