"""
Body shape classification & Smart Fit Notes generator.
Rule-based expert system without external LLM dependencies.
"""

from typing import List, Tuple
from app.models.vision import BodyMeasurements, BodyShapeType


def classify_body_shape(
    shoulder_cm: float,
    chest_cm: float,
    waist_cm: float,
    hips_cm: float,
    gender: str,
) -> BodyShapeType:
    """
    Classifies body shape based on anthropometric ratios (Shoulder, Chest, Waist, Hips).
    - Female (5 shapes): Hourglass, Pear, Apple, Rectangle, Inverted Triangle
    - Male (5 shapes): Trapezoid, Rectangle, Triangle, Inverted Triangle, Oval
    """
    whr = waist_cm / hips_cm if hips_cm > 0 else 0.80
    wcr = waist_cm / chest_cm if chest_cm > 0 else 0.85

    if gender == "female":
        # 1. Quả táo (Apple / Round): Vòng eo/bụng lớn vượt trội
        if whr >= 0.85 or waist_cm >= chest_cm - 3.0:
            return "qua_tao"

        # 2. Đồng hồ cát (Hourglass): Eo thắt rõ rệt, ngực và hông nở đều
        if whr <= 0.75 and abs(chest_cm - hips_cm) <= 6.0 and (chest_cm - waist_cm) >= 15.0:
            return "dong_ho_cat"

        # 3. Quả lê (Pear / Triangle): Hông lớn hơn ngực rõ rệt
        if hips_cm >= chest_cm + 5.0 and whr <= 0.82:
            return "qua_le"

        # 4. Tam giác ngược (Inverted Triangle): Vai & ngực rộng hơn hông
        if chest_cm >= hips_cm + 5.0 or shoulder_cm >= (hips_cm * 0.44):
            return "tam_giac_nguoc"

        # 5. Hình chữ nhật (Rectangle): 3 vòng đều nhau, eo ít thắt
        return "chu_nhat"

    else:  # male
        # 1. Hình Oval: Bụng là phần lớn nhất, lớn hơn cả ngực và hông
        if waist_cm > chest_cm and waist_cm > hips_cm:
            return "oval"

        # 2. Hình Tam Giác: Thân dưới (hông/eo) nở nang hơn ngực và vai
        if hips_cm >= chest_cm or (waist_cm >= chest_cm and waist_cm <= hips_cm):
            return "tam_giac"

        # 3. Tam Giác Ngược (V-Taper): Vai ngực cực kỳ vạm vỡ, eo thon gọn
        if chest_cm >= waist_cm + 15.0 and wcr <= 0.80 and shoulder_cm >= 44.0:
            return "tam_giac_nguoc"

        # 4. Hình Thang (Trapezoid): Vóc dáng chuẩn tỷ lệ vàng của nam (vai ngực nở, eo gọn)
        if chest_cm >= waist_cm + 6.0 and chest_cm >= hips_cm - 2.0:
            return "hinh_thang"

        # 5. Hình Chữ Nhật (Rectangle): Thân người thẳng, vai ngực eo gần bằng nhau
        return "chu_nhat"


def generate_smart_fit_notes(
    shape: BodyShapeType,
    measurements: BodyMeasurements,
    gender: str,
    bmi: float,
) -> List[str]:
    notes: List[str] = []

    # Female specific notes
    if shape == "dong_ho_cat":
        notes.append("Vóc dáng đồng hồ cát lý tưởng: Eo thon cân đối với ngực và hông.")
        notes.append("Trang phục tôn dáng: Ưu tiên áo dáng ôm (Slim-fit) hoặc đầm nhấn eo, tránh áo quá rộng làm mất đường cong.")
    elif shape == "qua_le":
        notes.append("Vóc dáng quả lê: Hông và đùi đầy đặn hơn so với phần thân trên.")
        notes.append("Lưu ý chọn size: Chọn size áo theo số đo vòng ngực, quần/chân váy nên ưu tiên tăng 1 size để thoải mái vòng hông.")
    elif shape == "qua_tao":
        notes.append("Vóc dáng quả táo: Tập trung vòng eo và bụng tròn đầy đặn.")
        notes.append("Lưu ý chọn size: Ưu tiên form áo suông (Regular/Relaxed) hoặc chất liệu co giãn tốt để không bị kích vòng bụng.")

    # Male specific notes
    elif shape == "hinh_thang":
        notes.append("Vóc dáng hình thang chuẩn nam: Vai và ngực nở nang, eo và hông thon gọn cân đối.")
        notes.append("Gợi ý chọn size: Dễ mặc đồ nhất, phù hợp với hầu hết các mẫu áo Slim-fit và Regular-fit.")
    elif shape == "tam_giac":
        notes.append("Vóc dáng hình tam giác: Thân dưới nở nang hơn so với độ rộng vai và ngực.")
        notes.append("Gợi ý chọn size: Ưu tiên áo khoác có đệm vai nhẹ, phom suông để cân bằng tỷ lệ với hông.")
    elif shape == "oval":
        notes.append("Vóc dáng hình oval: Phần thân giữa (bụng/eo) tròn đầy hơn vai và hông.")
        notes.append("Gợi ý chọn size: Ưu tiên áo phom Relaxed/Comfort, cổ chữ V và gam màu tối để tạo cảm giác thon gọn.")

    # Shared shapes
    elif shape == "tam_giac_nguoc":
        notes.append("Vóc dáng tam giác ngược: Khung vai và ngực rộng thể thao, hông thon gọn.")
        notes.append("Lưu ý chọn size: Chọn size áo dựa trên bề rộng vai để tránh bị bó nách; quần ống đứng hoặc suông giúp cân bằng tỷ lệ.")
    else:  # chu_nhat
        notes.append("Vóc dáng chữ nhật: Tỷ lệ vai, eo và hông tương đối đồng đều, dáng người thẳng mỏng.")
        notes.append("Gợi ý chọn size: Phù hợp với bảng size tiêu chuẩn (Regular fit), có thể layer nhiều lớp áo để tạo chiều sâu.")

    # Specific height & inseam advice
    if measurements.inseam_cm and measurements.height_cm:
        leg_ratio = measurements.inseam_cm / measurements.height_cm
        if leg_ratio > 0.46:
            notes.append("Đôi chân dài so với tỷ lệ chiều cao: Quần dài nên chọn dòng tall hoặc kiểm tra kỹ chiều dài ống quần.")
        elif leg_ratio < 0.42:
            notes.append("Thân dài chân ngắn: Nên phối đồ cạp cao để tạo hiệu ứng kéo dài chân.")

    return notes
