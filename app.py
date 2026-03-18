import streamlit as st
import pandas as pd

# --- [설정 부분] ---
BASE_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=0&single=true&output=csv"
OUT_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=398277773&single=true&output=csv"
google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdiLZvBYd1x-0gXxQz0cfSZq5szvXvsgCqTmi8D82lQAYIypw/viewform?usp=dialog"

st.set_page_config(page_title="판촉물 재고 관리", layout="wide", page_icon="📋")

# --- [1. 데이터 로드 함수: 이름으로 찾기 모드] ---
@st.cache_data(ttl=60)
def load_data_smart(url):
    try:
        # 이번에는 제목줄을 건너뛰지 않고 그대로 읽습니다.
        df = pd.read_csv(url, on_bad_lines='skip', engine='python')
        # 양쪽 시트 공통으로 '카테고리'와 '색상' 공백 제거
        df['카테고리'] = df['카테고리'].astype(str).str.strip()
        df['색상'] = df['색상'].astype(str).str.strip()
        # '출고' 열이 있다면 숫자로 변환 (없으면 0으로 채운 열 생성)
        if '출고' in df.columns:
            df['출고'] = pd.to_numeric(df['출고'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        else:
            df['출고'] = 0
        return df
    except Exception as e:
        return pd.DataFrame()

# --- [2. 데이터 불러오기] ---

# 기초 데이터 (개발자님 제공 고정 수치)
initial_inventory = [
    {"카테고리": "무선충전기", "색상": "블랙", "입고": 80},
    {"카테고리": "무선충전기", "색상": "실버", "입고": 70},
    {"카테고리": "무선충전기", "색상": "핑크", "입고": 50},
    {"카테고리": "무선충전기", "색상": "그린", "입고": 50},
    {"카테고리": "우산", "색상": "블랙", "입고": 150},
    {"카테고리": "우산", "색상": "우드", "입고": 100},
    {"카테고리": "우산", "색상": "블루", "입고": 100},
    {"카테고리": "우산", "색상": "그린", "입고": 100},
]
inventory_df = pd.DataFrame(initial_inventory)

# 각 시트 로드
base_raw = load_data_smart(BASE_STOCK_URL)
out_raw = load_data_smart(OUT_STOCK_URL)

# --- [3. 재고 계산] ---
# A. 일반 시트 출고 합계
past_out_sum = base_raw.groupby(['카테고리', '색상'])['출고'].sum().reset_index()

# B. 설문지 시트 출고 합계
new_out_sum = out_raw.groupby(['카테고리', '색상'])['출고'].sum().reset_index()

# C. 병합 및 최종 계산
final_df = pd.merge(inventory_df, past_out_sum, on=['카테고리', '색상'], how='left', suffixes=('', '_과거')).fillna(0)
final_df = pd.merge(final_df, new_out_sum, on=['카테고리', '색상'], how='left', suffixes=('', '_신규')).fillna(0)

# 현재재고 = 입고 - 일반시트출고 - 설문지출고
final_df['현재재고'] = final_df['입고'] - final_df['출고'] - final_df['출고_신규']

# --- [4. 화면 구성] ---
st.title("📋 실시간 판촉물 통합 재고 관리")
st.info("💡 엑셀 시트의 '출고' 칸 숫자를 자동으로 추적하여 계산합니다.")
st.link_button("🚀 즉시 출고 신청서 작성 (구글 폼)", google_form_url, use_container_width=True)
st.divider()

emoji_dict = {"무선충전기": "⚡", "우산": "☔"}
categories = ["무선충전기", "우산"]

for cat in categories:
    st.subheader(f"{emoji_dict.get(cat, '📦')} {cat}")
    cat_items = final_df[final_df['카테고리'] == cat]
    cols = st.columns(4)
    for i, (idx, row) in enumerate(cat_items.iterrows()):
        with cols[i % 4]:
            st.metric(
                label=row['색상'], 
                value=f"{int(row['현재재고'])} 개",
                delta=f"총 출고: -{int(row['출고'] + row['출고_신규'])}"
            )

st.divider()
with st.expander("📝 시트 데이터 로드 확인 (숫자가 0이라면 시트의 제목을 확인하세요)"):
    t1, t2 = st.tabs(["일반 시트 데이터", "설문지 데이터"])
    t1.write("일반 시트에서 읽어온 '출고' 열 데이터:")
    t1.dataframe(base_raw[['카테고리', '색상', '출고']].head(), use_container_width=True)
    t2.write("설문지 시트에서 읽어온 '출고' 열 데이터:")
    t2.dataframe(out_raw[['카테고리', '색상', '출고']].head(), use_container_width=True)