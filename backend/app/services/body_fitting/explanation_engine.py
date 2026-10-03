"""
Cloudline Studio - Explanation AI Engine (Model 2)
Generates natural, persuasive, and context-aware fashion copywriting in Vietnamese.

Architecture:
1. Cloud LLM Engine: Generative AI via Google Gemini API (gemini-1.5-flash) when API key is provided.
2. Contextual Dynamic NLP Engine: Anthropometric synthesis utilizing brand tone, body ratios,
   and zone delta easing (supports offline mode & fallback).
3. S07 Multi-Size Comparison Matrix: Compares Size A vs Size B across 4 anatomical zones.
"""
import os
import json
from typing import Dict, Any, List, Optional


class ExplanationEngine:
    """
    Model 2: Generative AI & Contextual Fashion Stylist Engine.
    Powers Figma screens S06 (Fit Recommendation) and S07 (Size Comparison).
    """

    PREFERENCE_VN = {
        "regular": "Vừa vặn",
        "tight": "Ôm gọn",
        "loose": "Thoải mái"
    }

    # Brand voice tailored to 5 major fashion brands
    BRAND_VOICE = {
        "zara": {
            "tone": "thời thượng châu Âu",
            "shoulder_trait": "cầu vai sắc nét chuẩn phom tailored",
            "silhouette": "phom dáng hiện đại sang trọng"
        },
        "uniqlo": {
            "tone": "tối giản công năng Nhật Bản",
            "shoulder_trait": "đường may vai cử động êm ái linh hoạt",
            "silhouette": "tối ưu sự thoải mái và độ bền nhẹ"
        },
        "h&m": {
            "tone": "trẻ trung hiện đại",
            "shoulder_trait": "đường vai chuẩn phom thời trang thường nhật",
            "silhouette": "dễ phối layer thanh lịch"
        },
        "stradivarius": {
            "tone": "nữ tính thời thượng",
            "shoulder_trait": "vai áo ôm vừa vặn tôn dáng thanh mảnh",
            "silhouette": "tôn đường nét cơ thể tự nhiên"
        },
        "pull&bear": {
            "tone": "phóng khoáng streetwear",
            "shoulder_trait": "phom vai trễ nhẹ dropped-shoulder năng động",
            "silhouette": "dáng áo suông thoải mái đậm chất đường phố"
        }
    }

    @classmethod
    def try_llm_generation(
        cls,
        fit_result: Dict[str, Any],
        user_meas: Dict[str, float],
        garment: Dict[str, Any],
        preference: str
    ) -> Optional[Dict[str, Any]]:
        """
        Attempts to generate natural copy using Google Gemini API if GEMINI_API_KEY is configured.
        Supports gemini-3.8-flash and gemini-flash-latest with graceful local fallback.
        """
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return None

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)

            candidate_models = ["gemini-3.8-flash", "gemini-flash-latest"]
            model = None
            for m_name in candidate_models:
                try:
                    model = genai.GenerativeModel(m_name)
                    break
                except Exception:
                    continue
            
            if model is None:
                return None

            prompt = f"""
            Bạn là Chuyên gia Cố vấn Kích cỡ Thời trang Cao cấp (Senior Fit Intelligence Stylist) của Cloudline Studio.
            Nhiệm vụ: Viết văn bản tư vấn size cho khách hàng theo chuẩn thiết kế thời trang chuyên nghiệp, sành điệu, tự nhiên.

            Thông tin:
            - Khách hàng: Chiều cao {user_meas.get('height')}cm, Cân nặng {user_meas.get('weight')}kg, Rộng vai {user_meas.get('shoulder')}cm, Vòng ngực {user_meas.get('bust')}cm, Vòng eo {user_meas.get('waist')}cm.
            - Sản phẩm: {garment.get('brand')} - {garment.get('product_name')} (Loại áo: {garment.get('category')}, form {garment.get('fit_cut')}).
            - Model 1 ML đã dự đoán: Size đề xuất là {fit_result['recommended_size']} với độ tin cậy {fit_result['confidence']}%. Size phụ so sánh là {fit_result.get('alternative_size')}.
            - Phân tích 4 vùng giải phẫu:
              + Vai: {fit_result['zones'][0]['badge']}
              + Ngực: {fit_result['zones'][1]['badge']}
              + Eo: {fit_result['zones'][2]['badge']}
              + Chiều dài: {fit_result['zones'][3]['badge']}
            - Sở thích độ ôm: {cls.PREFERENCE_VN.get(preference, 'Vừa vặn')}

            Yêu cầu: Trả về DUY NHẤT một chuỗi JSON hợp lệ (không markdown block) có cấu trúc:
            {{
              "headline": "Tiêu đề tóm tắt 1 dòng độc đáo, tự nhiên phản ánh cảm giác mặc của loại áo này",
              "why_text": "Câu lý do sành điệu bắt đầu bằng 'Vì sao Size X: ...', phân tích rõ tính năng chất liệu và phom dáng của loại áo này",
              "details": [
                {{"step": "01", "title": "Vai · ...", "desc": "Chi tiết giải thích cảm giác vùng vai trên mẫu áo này"}},
                {{"step": "02", "title": "Ngực · ...", "desc": "Chi tiết khoảng thở cử động ngực"}},
                {{"step": "03", "title": "Eo · ...", "desc": "Chi tiết phom eo khi đứng và ngồi"}},
                {{"step": "04", "title": "Chiều dài · ...", "desc": "Tỉ lệ chiều dài áo cân đối với vóc dáng"}}
              ],
              "advisory": "Lời khuyên thời trang đánh đổi phong cách giữa size đề xuất và size phụ",
              "calculation_info": [
                {{"step": "01", "title": "Số đo nhân trắc học của bạn", "desc": "..."}},
                {{"step": "02", "title": "Bảng thông số kỹ thuật {garment.get('brand')}", "desc": "..."}},
                {{"step": "03", "title": "Mô hình Machine Learning", "desc": "..."}},
                {{"step": "04", "title": "Sở thích mặc của bạn", "desc": "..."}}
              ]
            }}
            """
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.4, "max_output_tokens": 1024}
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                if lines and lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_text = "\n".join(lines).strip()
            data = json.loads(raw_text)
            print("[ExplanationEngine] Generated natural copy via Google Gemini LLM.")
            return data
        except Exception as e:
            print(f"[ExplanationEngine] LLM note ({e}). Using Dynamic Contextual NLP Stylist Engine.")
            return None

    @classmethod
    def generate_contextual_nlp(
        cls,
        fit_result: Dict[str, Any],
        user_meas: Dict[str, float],
        garment: Dict[str, Any],
        preference: str
    ) -> Dict[str, Any]:
        """
        Category-Aware Dynamic Fashion Linguistics Engine:
        Synthesizes organic, varied, and highly contextual Vietnamese fashion copywriting
        tailored specifically to jacket categories (biker, puffer, coat, blazer, bomber, denim).
        """
        best_size = fit_result["recommended_size"]
        alt_size = fit_result.get("alternative_size", "L")
        zones = fit_result.get("zones", [])
        brand = garment.get("brand", "Cloudline Studio")
        p_name = garment.get("product_name", "Áo khoác")
        b_key = brand.lower().replace("&", "")
        brand_meta = cls.BRAND_VOICE.get(b_key, cls.BRAND_VOICE["uniqlo"])
        pref_vn = cls.PREFERENCE_VN.get(preference, "Vừa vặn")

        zone_dict = {z["zone"]: z for z in zones}
        v_vai = zone_dict.get("Vai", {})
        v_nguc = zone_dict.get("Ngực", {})
        v_eo = zone_dict.get("Eo", {})
        v_dai = zone_dict.get("Chiều dài", {})

        delta_vai = round(float(v_vai.get("delta_cm", 2.0)), 1)
        delta_nguc = round(float(v_nguc.get("delta_cm", 10.0)), 1)
        delta_eo = round(float(v_eo.get("delta_cm", 10.0)), 1)
        len_val = int(v_dai.get("measurement", 68))
        u_height = int(user_meas.get("height", 165))
        u_bust = int(user_meas.get("bust", 86))
        u_waist = int(user_meas.get("waist", 70))
        u_shoulder = round(float(user_meas.get("shoulder", 39)), 1)

        # 1. Identify Specific Garment Persona & Silhouettes
        text_corpus = f"{garment.get('category', '')} {p_name}".lower()
        if any(w in text_corpus for w in ["da", "biker", "leather"]):
            cat_type = "leather"
        elif any(w in text_corpus for w in ["phao", "puffer", "bông", "down", "lông vũ"]):
            cat_type = "puffer"
        elif any(w in text_corpus for w in ["dạ", "măng tô", "trench", "overcoat", "dáng dài"]):
            cat_type = "coat"
        elif any(w in text_corpus for w in ["blazer", "vest", "suit", "tailored"]):
            cat_type = "blazer"
        elif any(w in text_corpus for w in ["bomber", "bóng chày"]):
            cat_type = "bomber"
        elif any(w in text_corpus for w in ["denim", "bò", "jean"]):
            cat_type = "denim"
        else:
            cat_type = "casual"

        # 2. Dynamic Headline tailored to Category and Fit State
        if cat_type == "leather":
            headline = "Cầu vai đứng phom sắc nét · ôm gọn eo tôn nét cá tính" if delta_eo <= 8.0 else "Cầu vai sắc nét · phom biker thoải mái cử động"
        elif cat_type == "puffer":
            headline = "Khoảng ngực dôi lý tưởng mặc layer · phồng nhẹ ấm áp" if delta_nguc >= 10.0 else "Phom phao gọn gàng giữ ấm · cử động vừa vặn linh hoạt"
        elif cat_type == "coat":
            headline = "Cầu vai thanh lịch · chiều dài áo tôn dáng cao ráo"
        elif cat_type == "blazer":
            headline = "Cầu vai tailored sắc nét · chiết eo tôn đường nét tự nhiên"
        elif cat_type == "bomber":
            headline = "Bo gấu eo gọn gàng · nách và ngực áo cử động năng động"
        elif cat_type == "denim":
            headline = "Chất denim cứng cáp đứng dáng · chuẩn tỉ lệ vai và ngực"
        else:
            eo_str = "eo thả suông tự nhiên" if delta_eo >= 9.0 else ("chiết nhẹ tôn dáng eo" if delta_eo <= 6.0 else "vừa vặn ở eo")
            headline = f"Vừa vặn ở vai và ngực · {eo_str}"

        # 3. Dynamic Why Text tailored to specific Category & Biomechanical ratios
        if cat_type == "leather":
            why_text = (
                f"Vì sao Size {best_size}: Chất liệu da PU/biker cao cấp của {brand} cần độ ôm sát vai và ngực chuẩn mực. "
                f"Với số đo vai {u_shoulder}cm và ngực {u_bust}cm, size {best_size} mang lại độ dôi cử động +{int(round(delta_nguc))}cm ở ngực, "
                f"đủ để cài kín khóa kéo xéo mà không bị kéo căng nếp da hay gãy nếp ve cổ."
            )
        elif cat_type == "puffer":
            why_text = (
                f"Vì sao Size {best_size}: Áo phao cần khoảng thở để các khoang bông/lông vũ bung nở tối đa hiệu năng giữ nhiệt. "
                f"Độ dôi ngực +{int(round(delta_nguc))}cm trên size {best_size} vừa vặn hoàn hảo để bạn mặc thêm áo len cổ lọ hoặc hoodie bên trong "
                f"mà vẫn duy trì phom dáng gọn gàng, không bị cảm giác cồng kềnh."
            )
        elif cat_type == "coat":
            why_text = (
                f"Vì sao Size {best_size}: Măng tô dáng dài đòi hỏi cầu vai là điểm neo vững chắc để tà áo buông rủ thanh thoát. "
                f"Size {best_size} ôm trọn bờ vai {u_shoulder}cm với độ dôi +{delta_vai}cm, kết hợp chiều dài {len_val}cm tạo tỉ lệ vàng cân xứng, "
                f"giúp đôi chân trông dài hơn khi sải bước."
            )
        elif cat_type == "blazer":
            why_text = (
                f"Vì sao Size {best_size}: Thiết kế tailored của {brand} tôn vinh nét lịch lãm với cầu vai định hình phẳng phiu. "
                f"Size {best_size} khớp tỉ lệ ngực {u_bust}cm và eo {u_waist}cm, khi cài khuy áo phẳng mượt tự nhiên mà không tạo nếp nhăn kéo căng chữ X."
            )
        elif cat_type == "bomber":
            why_text = (
                f"Vì sao Size {best_size}: Phom bomber streetwear đặc trưng cần thân áo có độ phồng nhẹ đi cùng bo gấu ôm gọn ngang hông. "
                f"Size {best_size} cung cấp độ cử động +{int(round(delta_nguc))}cm ngực, đảm bảo vung tay lái xe hay hoạt động ngoài trời cực kỳ êm ái."
            )
        else:
            why_text = (
                f"Vì sao Size {best_size}: Phom áo {brand_meta['silhouette']} ôm trọn tỉ lệ ngực {u_bust}cm và eo {u_waist}cm của bạn. "
                f"Độ cử động +{int(round(delta_nguc))}cm ở ngực kết hợp độ dôi vai +{delta_vai}cm đảm bảo vận động linh hoạt mà vẫn giữ phom đứng chuẩn chỉnh."
            )

        # 4. Details cards with Category-Specific Anatomy Context
        if cat_type == "leather":
            vai_desc = f"Đường may vai nằm khớp chính xác đỉnh xương vai (+{delta_vai}cm), giúp giữ thẳng sống lưng và không bị đùn da khi giơ tay."
            nguc_desc = f"Khoảng dôi +{int(round(delta_nguc))}cm đủ ôm sát tôn khuôn ngực nhưng vẫn thoải mái kéo khóa kín cổ phong cách biker."
            eo_desc = f"Phom eo ôm nhẹ ({v_eo.get('badge', 'Vừa vặn').replace('● ', '')}), giữ vạt áo thẳng thớm khi ngồi."
        elif cat_type == "puffer":
            vai_desc = f"Cầu vai thả nhẹ êm ái (+{delta_vai}cm), trọng lượng áo phân bổ đều không gây cảm giác nặng vai."
            nguc_desc = f"Dôi ngực +{int(round(delta_nguc))}cm đạt chuẩn áo khoác giữ ấm, cho phép phối layer linh hoạt áo thun dày hoặc áo len."
            eo_desc = f"Thân áo buông suông thoáng khí (+{delta_eo}cm), giữ nhiệt cơ thể ổn định mà không bị bí bách."
        elif cat_type == "coat":
            vai_desc = f"Cầu vai sắc nét kiểu Âu (+{delta_vai}cm), làm điểm tựa định hình cho toàn bộ thân áo dài thanh mảnh."
            nguc_desc = f"Vòng ngực dôi +{int(round(delta_nguc))}cm tạo độ rủ mềm mại cho ve cổ áo khi thả phanh hoặc thắt đai."
            eo_desc = f"Eo suông tự nhiên, tạo khoảng trống thoải mái khi cài khuy hoặc thắt đai tôn vòng hai."
        elif cat_type == "blazer":
            vai_desc = f"Đường đệm vai sắc nét chuẩn tailored (+{delta_vai}cm), tôn dáng đứng đắn thanh lịch."
            nguc_desc = f"Ngực áo phẳng phiu (+{int(round(delta_nguc))}cm), ve cổ chữ K nằm êm ái trên ngực áo."
            eo_desc = f"Đường chiết eo tinh tế làm nổi bật tỉ lệ eo {u_waist}cm, giữ form phẳng phiu khi ngồi họp hay làm việc."
        else:
            vai_desc = f"Với chiều rộng vai {u_shoulder}cm, size {best_size} mang lại {brand_meta['shoulder_trait']} (+{delta_vai}cm độ cử động)."
            nguc_desc = f"Ngực áo có khoảng dôi {int(round(delta_nguc))}cm, đáp ứng đúng sở thích mặc {pref_vn} và không bị co kéo khi cài khóa."
            eo_desc = f"Vòng eo {u_waist}cm tạo độ ôm {v_eo.get('status')} vừa vặn, giữ form áo phẳng phiu khi vận động."

        details = [
            {
                "step": "01",
                "title": f"Vai · {v_vai.get('badge', 'Vừa vặn').replace('● ', '')}",
                "desc": vai_desc
            },
            {
                "step": "02",
                "title": f"Ngực · {v_nguc.get('badge', 'Vừa vặn').replace('● ', '')}",
                "desc": nguc_desc
            },
            {
                "step": "03",
                "title": f"Eo · {v_eo.get('badge', 'Vừa vặn').replace('● ', '')}",
                "desc": eo_desc
            },
            {
                "step": "04",
                "title": f"Chiều dài · {v_dai.get('badge', 'Vừa vặn').replace('● ', '')}",
                "desc": f"Chiều dài thân áo {len_val} cm tạo tỉ lệ cân xứng với chiều cao {u_height} cm của bạn."
            }
        ]

        # 5. Direction & Garment-aware Advisory Note
        size_order = ["XS", "S", "M", "L", "XL", "XXL"]
        idx_b = size_order.index(best_size) if best_size in size_order else 2
        idx_a = size_order.index(alt_size) if alt_size in size_order else 3

        if idx_a > idx_b:
            if cat_type == "puffer":
                advisory = f"Muốn thoải mái mặc áo nỉ bông siêu dày bên trong? Size {alt_size} sẽ rộng hơn, nhưng độ phồng tổng thể sẽ to hơn một chút."
            elif cat_type == "leather":
                advisory = f"Muốn mặc phóng khoáng hơn? Size {alt_size} cho thêm cử động ở nách và ngực, tuy nhiên vai áo sẽ hơi trễ nhẹ ra ngoài."
            else:
                advisory = f"Muốn thoải mái hơn ở eo hoặc mặc layer nhiều lớp? Size {alt_size} rộng rãi hơn nhưng cầu vai có thể hơi thừa."
            alt_tag = "Thoải mái & mặc layer hơn"
            summary_comp = f"{best_size} chuẩn phom tôn dáng nhất. {alt_size} ưu tiên rộng rãi thoải mái."
        else:
            if cat_type == "leather":
                advisory = f"Muốn phom biker ôm sát body hơn? Size {alt_size} tôn dáng triệt để nhưng cài khóa sẽ hơi căng tức vùng ngực."
            else:
                advisory = f"Muốn áo ôm gọn dáng người hơn? Size {alt_size} ôm sát hơn nhưng cử động vai và ngực sẽ hạn chế hơn một chút."
            alt_tag = "Gọn dáng & ôm sát hơn"
            summary_comp = f"{best_size} cân bằng thoải mái nhất. {alt_size} phù hợp nếu bạn muốn mặc ôm sát."

        # Calculation Info
        calculation_info = [
            {
                "step": "01",
                "title": "Số đo nhân trắc học của bạn",
                "desc": f"Cao {u_height} cm · Ngực {u_bust} cm · Eo {u_waist} cm · Vai {u_shoulder} cm"
            },
            {
                "step": "02",
                "title": f"Bảng số đo kỹ thuật {brand}",
                "desc": f"Dữ liệu thông số may chuẩn từng centimet của Size {best_size} và Size {alt_size}"
            },
            {
                "step": "03",
                "title": "Mô hình Machine Learning",
                "desc": f"Random Forest phân tích 10 đặc trưng hình thể với độ tin cậy {fit_result['confidence']}%"
            },
            {
                "step": "04",
                "title": "Sở thích mặc của bạn",
                "desc": f"Ưu tiên phong cách {pref_vn} để điều chỉnh biên độ cử động phù hợp"
            }
        ]

        comparison = {
            "primary_size": best_size,
            "alt_size": alt_size,
            "primary_tag": "Cân bằng nhất theo Fit Profile của bạn",
            "alt_tag": alt_tag,
            "summary": summary_comp,
            "preference_mapping": {
                "tight": size_order[max(0, idx_b - 1)],
                "regular": best_size,
                "loose": size_order[min(len(size_order) - 1, idx_b + 1)]
            }
        }


        return {
            "headline": headline,
            "why_text": why_text,
            "details": details,
            "advisory": advisory,
            "calculation_info": calculation_info,
            "comparison": comparison
        }

    @classmethod
    def generate(
        cls,
        fit_result: Dict[str, Any],
        user_meas: Dict[str, float],
        garment: Dict[str, Any],
        preference: str = "regular"
    ) -> Dict[str, Any]:
        """Entrypoint for Model 2 explanation generation (LLM with local NLP fallback)."""
        # 1. Try Generative AI Cloud Model (Gemini)
        llm_output = cls.try_llm_generation(fit_result, user_meas, garment, preference)
        if llm_output:
            if "comparison" not in llm_output:
                llm_output["comparison"] = cls.generate_contextual_nlp(fit_result, user_meas, garment, preference)["comparison"]
            return llm_output

        # 2. Contextual Dynamic NLP Engine
        return cls.generate_contextual_nlp(fit_result, user_meas, garment, preference)

    @classmethod
    def compare_two_sizes(
        cls,
        garment: Dict[str, Any],
        user_meas: Dict[str, float],
        size_a: str,
        size_b: str
    ) -> Dict[str, Any]:
        """Figma S07 Multi-zone size comparison matrix between Size A and Size B."""
        size_chart = garment.get("size_chart", {})
        spec_a = size_chart.get(size_a, {})
        spec_b = size_chart.get(size_b, {})

        u_shoulder = float(user_meas.get("shoulder", 39))
        u_bust = float(user_meas.get("bust", 86))
        u_waist = float(user_meas.get("waist", 70))

        sh_a, sh_b = spec_a.get("shoulder", 41), spec_b.get("shoulder", 43)
        bu_a, bu_b = spec_a.get("bust", 96), spec_b.get("bust", 102)
        wa_a, wa_b = spec_a.get("waist", 80), spec_b.get("waist", 86)
        le_a, le_b = spec_a.get("length", 68), spec_b.get("length", 70)

        diff_sh = round(sh_b - sh_a, 1)
        diff_bu = round(bu_b - bu_a, 1)
        diff_wa = round(wa_b - wa_a, 1)
        diff_le = round(le_b - le_a, 1)

        b_shoulder_desc = (
            f"Vai rộng hơn +{int(diff_sh)}cm" if diff_sh > 0
            else (f"Vai ôm gọn hơn {int(diff_sh)}cm" if diff_sh < 0 else "Ngang vai tương đương")
        )
        b_bust_desc = (
            f"Rộng rãi (+{int(round(bu_b - u_bust))}cm cử động)" if diff_bu > 0
            else f"Ôm sát ({int(round(bu_b - u_bust))}cm cử động)"
        )
        b_waist_desc = (
            f"Suông rộng (+{int(diff_wa)}cm)" if diff_wa > 0
            else (f"Chiết eo gọn ({int(diff_wa)}cm)" if diff_wa < 0 else "Phom eo tương đương")
        )
        b_len_desc = (
            f"{int(le_b)} cm (Dài hơn +{int(diff_le)}cm)" if diff_le > 0
            else (f"{int(le_b)} cm (Ngắn hơn {int(diff_le)}cm)" if diff_le < 0 else f"{int(le_b)} cm")
        )

        is_b_larger = diff_bu >= 0
        tag_b = f"Size {size_b} · Rộng rãi thoải mái hơn" if is_b_larger else f"Size {size_b} · Gọn gàng tôn dáng hơn"
        guide_summary = (
            f"Chọn Size {size_a} nếu bạn muốn phom dáng cân đối chuẩn chỉnh. Chọn Size {size_b} nếu bạn ưu tiên cử động rộng rãi hoặc mặc layer áo len dày bên trong."
            if is_b_larger else
            f"Chọn Size {size_a} để có cử động thoải mái chuẩn phom. Chọn Size {size_b} nếu bạn thích áo ôm vừa khít đường cong cơ thể."
        )

        zones_comparison = [
            {
                "zone": "Vai",
                "size_a_val": sh_a,
                "size_b_val": sh_b,
                "diff_cm": diff_sh,
                "size_a_status": "Vừa vặn chuẩn phom",
                "size_b_status": b_shoulder_desc
            },
            {
                "zone": "Ngực",
                "size_a_val": bu_a,
                "size_b_val": bu_b,
                "diff_cm": diff_bu,
                "size_a_status": f"Vừa vặn (+{int(round(bu_a - u_bust))}cm cử động)",
                "size_b_status": b_bust_desc
            },
            {
                "zone": "Eo",
                "size_a_val": wa_a,
                "size_b_val": wa_b,
                "diff_cm": diff_wa,
                "size_a_status": "Hơi ôm nhẹ tôn dáng",
                "size_b_status": b_waist_desc
            },
            {
                "zone": "Chiều dài",
                "size_a_val": le_a,
                "size_b_val": le_b,
                "diff_cm": diff_le,
                "size_a_status": f"{int(le_a)} cm (Chạm mông)",
                "size_b_status": b_len_desc
            }
        ]

        return {
            "size_a": size_a,
            "size_b": size_b,
            "product_id": garment.get("id"),
            "product_name": garment.get("product_name"),
            "brand": garment.get("brand"),
            "headline": f"So sánh chi tiết Size {size_a} và Size {size_b}",
            "tag_a": f"Size {size_a} · Cân bằng nhất theo Fit Profile của bạn",
            "tag_b": tag_b,
            "recommendation_summary": guide_summary,
            "zones_comparison": zones_comparison
        }


# Canonical Aliases
ExplanationAIEngine = ExplanationEngine
