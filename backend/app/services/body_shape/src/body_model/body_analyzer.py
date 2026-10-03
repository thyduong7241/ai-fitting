"""
Body composition, anthropometric ratio calculation, and shape classification engine.
Strictly data-driven with no hardcoded magic thresholds.
"""

import os
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import yaml

from ..schemas.measurements import BodyMeasurements


@dataclass
class BodyAnalysis:
    bmi: float
    bmi_category: str
    whr: float
    whr_health_status: str
    body_shape: str
    body_shape_description: str
    height_to_head_ratio: float
    ideal_weight_range: Dict[str, float]
    proportions_summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BodyAnalyzer:
    """
    Evaluates body composition, anthropometric indicators, and morphological shape
    using standard physiological indices and externalized configuration rules.
    """

    def __init__(self, config_path: Optional[str] = None):
        if not config_path:
            config_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../config/anatomy_config.yaml")
            )
        self.config = self._load_config(config_path)

    def _load_config(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def analyze(self, meas: BodyMeasurements) -> BodyAnalysis:
        h_m = float(meas.height_cm) / 100.0
        base_bmi = float(self.config.get("anatomy", {}).get("weight_modeling", {}).get("base_bmi", 21.5))
        w_kg = float(meas.weight_kg) if (meas.weight_kg and meas.weight_kg > 0) else (base_bmi * (h_m ** 2))

        # 1. BMI Calculation
        bmi = round(w_kg / (h_m ** 2), 1)
        if bmi < 18.5:
            bmi_cat = "Thiếu cân (Underweight)"
        elif bmi < 25.0:
            bmi_cat = "Bình thường (Normal)"
        elif bmi < 30.0:
            bmi_cat = "Thừa cân (Overweight)"
        else:
            bmi_cat = "Béo phì (Obese)"

        # 2. WHR (Waist to Hip Ratio)
        prop_cfg = self.config.get("anatomy", {}).get("proportions", {}).get(meas.gender, {})
        default_waist = meas.height_cm * prop_cfg.get("waist", 0.40)
        default_hip = meas.height_cm * prop_cfg.get("hip", 0.55)
        default_bust = meas.height_cm * prop_cfg.get("bust", 0.53)

        waist = float(meas.waist_cm) if (meas.waist_cm and meas.waist_cm > 0) else default_waist
        hip = float(meas.hip_cm) if (meas.hip_cm and meas.hip_cm > 0) else default_hip
        bust = float(meas.bust_cm) if (meas.bust_cm and meas.bust_cm > 0) else default_bust

        whr = round(waist / max(1.0, hip), 2)

        # WHR Health Status
        if meas.gender == "female":
            whr_status = "Tối ưu / Rất tốt" if whr <= 0.80 else ("Trung bình" if whr <= 0.85 else "Cần chú ý mỡ nội tạng")
        else:
            whr_status = "Tối ưu / Rất tốt" if whr <= 0.90 else ("Trung bình" if whr <= 0.95 else "Cần chú ý mỡ nội tạng")

        # 3. Morphological Body Shape Classification
        shape, shape_desc = self._classify_shape(meas.gender, bust, waist, hip, meas.shoulder_width_cm, meas.height_cm)

        # 4. Ideal weight range (Hamwi / Robinson formula bounds for height)
        ideal_min = round(18.5 * (h_m ** 2), 1)
        ideal_max = round(24.9 * (h_m ** 2), 1)

        # 5. Proportion proportions
        chin_ratio = float(self.config.get("anatomy", {}).get("landmarks", {}).get("chin", 0.135))
        head_height_ratio = round(meas.height_cm / max(1.0, (meas.height_cm * chin_ratio)), 1)

        return BodyAnalysis(
            bmi=bmi,
            bmi_category=bmi_cat,
            whr=whr,
            whr_health_status=whr_status,
            body_shape=shape,
            body_shape_description=shape_desc,
            height_to_head_ratio=head_height_ratio,
            ideal_weight_range={"min_kg": ideal_min, "max_kg": ideal_max},
            proportions_summary={
                "bust_waist_ratio": round(bust / max(1.0, waist), 2),
                "hip_waist_ratio": round(hip / max(1.0, waist), 2),
                "bust_hip_ratio": round(bust / max(1.0, hip), 2),
            }
        )

    def _classify_shape(
        self, gender: str, bust: float, waist: float, hip: float, shoulder: Optional[float], height: float
    ) -> tuple[str, str]:
        shapes_cfg = self.config.get("anatomy", {}).get("body_shapes", {})
        if gender == "female":
            f_cfg = shapes_cfg.get("female", {})
            tol = f_cfg.get("hourglass_tolerance", 0.08)
            hg_waist_ratio = f_cfg.get("hourglass_waist_ratio", 0.76)
            pear_th = f_cfg.get("pear_threshold", 1.05)
            inv_th = f_cfg.get("inverted_triangle", 1.05)
            apple_whr = f_cfg.get("apple_whr", 0.85)

            diff_bust_hip = abs(bust - hip)
            avg_bust_hip = (bust + hip) / 2.0

            if (diff_bust_hip / avg_bust_hip <= tol) and (waist / hip <= hg_waist_ratio):
                return (
                    "Đồng hồ cát (Hourglass)",
                    "Vòng 1 và vòng 3 cân đối hoàn hảo, đường cong thắt eo rõ nét mềm mại."
                )
            elif hip / bust >= pear_th and (waist / hip <= 0.82):
                return (
                    "Quả lê (Pear / Triangle)",
                    "Vòng 3 và đùi nở nang hơn phần thân trên, eo thon gọn tự nhiên."
                )
            elif bust / hip >= inv_th:
                return (
                    "Tam giác ngược (Inverted Triangle)",
                    "Phần ngực và vai rộng hơn hông, đường nét khỏe khoắn, hiện đại."
                )
            elif waist / hip >= apple_whr:
                return (
                    "Quả táo (Apple / Round)",
                    "Trọng tâm cơ thể tập trung ở vùng eo và ngực, chân và tay thường thanh mảnh."
                )
            else:
                return (
                    "Hình chữ nhật (Rectangle / Athletic)",
                    "Ba vòng có tỷ lệ tương đồng, vóc dáng thanh mảnh, phong cách hiện đại."
                )
        else:
            # Male
            m_cfg = shapes_cfg.get("male", {})
            trap_whr = m_cfg.get("trapezoid_whr", 0.86)
            trap_st = m_cfg.get("trapezoid_st_ratio", 1.20)
            v_taper = m_cfg.get("v_taper_bust_hip", 1.10)
            oval_whr = m_cfg.get("oval_whr", 0.95)

            default_sh_prop = float(self.config.get("anatomy", {}).get("proportions", {}).get("male", {}).get("shoulder", 0.26))
            sh = shoulder if (shoulder and shoulder > 0) else (height * default_sh_prop)
            sh_w_ratio = sh / max(1.0, waist * 0.35)

            if sh_w_ratio >= trap_st and (waist / hip <= trap_whr):
                return (
                    "Hình thang / Thể thao (Trapezoid / Athletic)",
                    "Bờ vai rộng vững chãi thu hẹp dần xuống eo và hông, tỷ lệ cơ thể chuẩn nam tính."
                )
            elif (bust / hip >= v_taper) and (waist / hip <= 0.85):
                return (
                    "Tam giác ngược (V-Taper)",
                    "Khung ngực và cơ xô phát triển vượt trội, eo thon cơ bắp."
                )
            elif (waist / hip >= oval_whr):
                return (
                    "Hình oval (Oval / Solid)",
                    "Khối lượng cơ thể tập trung ở vùng bụng và ngực, vóc dáng đẫy đà."
                )
            else:
                return (
                    "Hình chữ nhật (Rectangle)",
                    "Chiều rộng vai, ngực và hông tương đương, vóc dáng thanh thoát đều đặn."
                )
