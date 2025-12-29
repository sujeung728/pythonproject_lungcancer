import streamlit as st
import pandas as pd
from urllib.parse import urlencode

st.set_page_config(layout="wide")

# -----------------------
# 데이터 로드
# -----------------------
path = r"C:\python-study\python-study-2025\mini-project\ProjectCode\Lung Cancer_Ct.csv"
df = pd.read_csv(path, encoding="cp949")

# -----------------------
# 1) 상세/목록 모드 분기 (가장 먼저!)
# -----------------------
query = st.query_params
patient_param = query.get("patient")
is_detail = patient_param is not None
patient_id = (patient_param[0] if isinstance(patient_param, list) else patient_param) if is_detail else None

if is_detail:
    st.title("🩺 폐암 환자 데이터 탐색기")
    st.subheader(f"🧬 {patient_id} 환자 상세 정보")

    # 문자열 비교 + 공백 제거로 안전하게 필터
    pid = str(patient_id).strip()
    id_series_str = df["id"].astype(str).str.strip()
    filtered_detail = df[id_series_str == pid].copy()

    if filtered_detail.empty:
        st.warning("해당 환자 정보가 없습니다.")
        st.markdown('<a href="./" target="_self">← 목록으로 돌아가기</a>', unsafe_allow_html=True)
        st.stop()
#----------------------------------------------------------------------------------------------------------
  # biomarker 컬럼을 생성

    def make_biomarker_text(row):
        results = []
        for col in row.index:
            if str(col).startswith("MMX"):
                val = row[col]
                if pd.notna(val) and val != 0:
                    results.append(f"{col} ({val} Ct)")
        return ", ".join(results) if results else ""
    filtered_detail['biomarker'] = filtered_detail.apply(make_biomarker_text, axis = 1)

#-----------------------------------------------------------------------------------------------------------
    detail_cols = [
            "id", "name", "age", "gender", "country",
            "family_history", "cancer_stage", "smoking_status",
            "bmi", "cholesterol_level", "treatment_type", "biomarker", "mutation_detected"
]

    valid_cols = [c for c in detail_cols if c in filtered_detail.columns]
    detail_to_show = filtered_detail[valid_cols]

    st.dataframe(detail_to_show)

    row = filtered_detail.iloc[0]   # [수정 포인트 1]
# -----------------------------------------------------------------------------------------------
    biomarker_list = []             # [수정 포인트 2]
    for col in row.index:
        if str(col).startswith("MMX") and pd.notna(row[col]) and row[col] != 0:
            biomarker_list.append(f"{col} ({row[col]} Ct)")
    biomarker_text = ", ".join(biomarker_list) if biomarker_list else "정보 없음"
# -----------------------------------------------------------------------------------------------
    st.markdown(f"""
    **🧍‍♂️ 환자 요약**
    - 나이: {row.get('age','N/A')}
    - 성별: {row.get('gender','N/A')}
    - 병기: {row.get('cancer_stage','N/A')}
    - 흡연 상태: {row.get('smoking_status','N/A')}
    - BMI: {row.get('bmi','N/A')}
    - 콜레스테롤 수치: {row.get('cholesterol_level','N/A')}
    - 치료 유형: {row.get('treatment_type','N/A')}
    - 바이오마커: {biomarker_text}
    - 변이 감지: {row.get('mutation_detected','N/A')}
    """)
    st.markdown('<a href="./" target="_self">← 목록으로 돌아가기</a>', unsafe_allow_html=True)

    st.stop()  # ✅ 상세 모드는 여기서 끝. 아래 목록 UI는 렌더링되지 않음.

# -----------------------
# 2) 목록 모드 (검색 + 결과표)
# -----------------------
st.title("🩺 폐암 환자 데이터 탐색기")
st.write("환자의 **ID, 이름, 성별, 나이, 병기, 가족력, 기저질환, MMX** 정보를 조회할 수 있습니다.")
st.subheader("🔍 개별 환자 검색")

col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
with col1:
    id_input = st.text_input("ID로 검색", "")
with col2:
    name_input = st.text_input("이름으로 검색", "")
with col3:
    gender_input = st.selectbox("성별 선택", ["", "Male", "Female"])
with col4:
    age_input = st.number_input("나이 입력", min_value=0, max_value=120, step=1, value=0)
with col5:
    stage_input = st.selectbox("병기 선택", ["", "Stage I", "Stage II", "Stage III", "Stage IV"])
with col6:
    disease_input = st.selectbox("기저질환 선택", ["", "hypertension", "asthma", "cirrhosis", "other_cancer"])
with col7:
    family_input = st.selectbox("가족력 여부", ["", "Yes", "No"])

# 필터링
filtered = df.copy()
if id_input:
    filtered = filtered[filtered["id"].astype(str).str.contains(id_input, case=False, na=False)]
if name_input:
    filtered = filtered[filtered["name"].astype(str).str.contains(name_input, case=False, na=False)]
if gender_input:
    filtered = filtered[filtered["gender"] == gender_input]
if age_input > 0:
    filtered = filtered[filtered["age"] == age_input]
if stage_input:
    filtered = filtered[filtered["cancer_stage"] == stage_input]
if disease_input:
    filtered = filtered[filtered[disease_input] == 1]
if family_input:
    filtered = filtered[filtered["family_history"] == family_input]

# 결과 출력
if filtered.empty:
    st.warning("🔍 조건에 맞는 환자가 없습니다.")
else:
    st.success(f"검색 결과: {len(filtered)}명")

    # 새 탭으로 ID 링크 만들기 (상대경로 사용)
    def make_link(pid):
        return f'<a href="./?patient={pid}" target="_blank">{pid}</a>'

    MAX_ROWS = 500
    result_final = (
        filtered[["id", "name", "age", "gender", "country", "family_history"]]
        .sort_values(by="id")
        .head(MAX_ROWS)
    )
    result_final_display = result_final.copy()
    result_final_display["id"] = result_final_display["id"].apply(make_link)

    st.write(result_final_display.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.caption(f"표시는 최대 {MAX_ROWS}행까지만 미리보기로 보여줍니다.")

st.markdown("---")
st.caption("💡 데이터는 예시이며, 의료 데이터 분석 학습 목적용입니다.")
