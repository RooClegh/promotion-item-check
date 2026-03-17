import streamlit as st
import pandas as pd

# --- [설정 부분] ---
BASE_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=398277773&single=true&output=csv"
OUT_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=0&single=true&output=csv"
google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdiLZvBYd1x-0gXxQz0cfSZq5szvXvsgCqTmi8D82lQAYIypw/viewform?usp=dialog"

# --- [1. 데이터 로드 함수 수정] ---
st.set_page_config(page_title="판촉물 재고 관리", layout="wide", page_icon="📋")

@st.cache_data(ttl=60)
def load_data(url, col_names):
    try:
        # 데이터 로드 (skiprows=1로 엑셀 제목줄 제외)
        df = pd.read_csv(url, skiprows=1, names=col_names, on_bad_lines='skip', engine='python')
        # 데이터가 있는 행만 추출
        df = df.dropna(subset=['카테고리'])
        # 모든 비교 대상(카테고리, 색상)을 문자열로 통일
        df['카테고리'] = df['카테고리'].astype(str).str.strip()
        df['색상'] = df['색상'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame(columns=col_names)

# 각 시트의 실제 범례 순서에 맞춰서 읽어오기
# 기본 시트: 번호(0), 날짜(1), 카테고리(2), 색상(3), 입고(4), 출고(5), 상세내역(6), 담당자(7)
base_raw = load_data(BASE_STOCK_URL, ['번호', '날짜', '카테고리', '색상', '입고', '출고', '상세내역', '담당자'])
# 설문지 응답: 타임스탬프(0), 카테고리(1), 색상(2), 출고(3), 수량(4), 업체명(5), 작성자(6)
out_raw = load_data(OUT_STOCK_URL, ['타임스탬프', '카테고리', '색상', '출고구분', '수량', '업체명', '작성자'])

# --- [2. 재고 계산 로직] ---

# 기초 재고: 기본 시트에서 '입고' 수량을 가져옵니다.
base_df = base_raw.groupby(['카테고리', '색상'])['입고'].sum().reset_index()

# 출고 재고: 설문지 응답 시트에서 '수량' 합계를 가져옵니다.
out_raw['수량'] = pd.to_numeric(out_raw['수량'], errors='coerce').fillna(0)
out_sum = out_raw.groupby(['카테고리', '색상'])['수량'].sum().reset_index()

# 두 데이터 합치기
final_df = pd.merge(base_df, out_sum, on=['카테고리', '색상'], how='left').fillna(0)
final_df['현재재고'] = final_df['입고'] - final_df['수량']

# --- [3. 화면 구성] ---
st.title("📋 실시간 판촉물 재고 현황")
st.link_button("🚀 즉시 출고 신청서 작성 (구글 폼)", google_form_url, use_container_width=True)
st.divider()

emoji_dict = {"무선충전기": "⚡", "우산": "☔"}
categories = ["무선충전기", "우산"]

for cat in categories:
    emoji = emoji_dict.get(cat, "📦")
    st.subheader(f"{emoji} {cat}")
    cat_items = final_df[final_df['카테고리'] == cat]
    cols = st.columns(4)
    
    for i, (idx, row) in enumerate(cat_items.iterrows()):
        with cols[i % 4]:
            st.metric(label=row['색상'], 
                      value=f"{int(row['현재재고'])} 개", 
                      delta=f"입고합계: {int(row['입고'])}")

st.divider()
with st.expander("📝 최근 출고 기록 (설문지 응답)"):
    st.dataframe(out_raw.sort_values(by='타임스탬프', ascending=False), use_container_width=True)