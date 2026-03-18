import streamlit as st
import pandas as pd

# --- [설정 부분] ---
BASE_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=0&single=true&output=csv"
OUT_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=398277773&single=true&output=csv"
google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdiLZvBYd1x-0gXxQz0cfSZq5szvXvsgCqTmi8D82lQAYIypw/viewform?usp=dialog"

st.set_page_config(page_title="판촉물 재고 관리", layout="wide", page_icon="📋")

@st.cache_data(ttl=60)
def load_data(url, col_names):
    try:
        df = pd.read_csv(url, skiprows=1, names=col_names, on_bad_lines='skip', engine='python')
        df = df.dropna(subset=['카테고리'])
        df['카테고리'] = df['카테고리'].astype(str).str.strip()
        df['색상'] = df['색상'].astype(str).str.strip()
        return df
    except Exception as e:
        return pd.DataFrame(columns=col_names)

# --- [1. 데이터 읽기] ---

# 기초 데이터: 최초 입고량 (개발자님 제공 수치)
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

# 일반 시트: [번호, 날짜, 카테고리, 색상, 입고, 출고, 상세내역, 담당자] (8칸)
base_raw = load_data(BASE_STOCK_URL, ['번호', '날짜', '카테고리', '색상', '입고', '출고', '상세내역', '담당자'])
base_raw['출고'] = pd.to_numeric(base_raw['출고'], errors='coerce').fillna(0)
past_out_sum = base_raw.groupby(['카테고리', '색상'])['출고'].sum().reset_index()

# 설문지 응답 시트: [타임스탬프, 카테고리, 색상, 출고, 상세내역, 작성자] (6칸으로 수정 완료!)
out_raw = load_data(OUT_STOCK_URL, ['타임스탬프', '카테고리', '색상', '출고', '상세내역', '작성자'])
out_raw['출고'] = pd.to_numeric(out_raw['출고'], errors='coerce').fillna(0)
new_out_sum = out_raw.groupby(['카테고리', '색상'])['출고'].sum().reset_index()

# --- [2. 최종 재고 계산] ---
final_df = pd.merge(inventory_df, past_out_sum, on=['카테고리', '색상'], how='left', suffixes=('', '_과거')).fillna(0)
final_df = pd.merge(final_df, new_out_sum, on=['카테고리', '색상'], how='left', suffixes=('', '_신규')).fillna(0)

# 현재재고 = 입고 - 과거출고 - 신규출고
final_df['현재재고'] = final_df['입고'] - final_df['출고'] - final_df['출고_신규']

# --- [3. 화면 구성] ---
st.title("📋 실시간 판촉물 통합 재고 관리")
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
with st.expander("📝 최근 상세 기록 확인 (과거 및 신규 통합)"):
    tab1, tab2 = st.tabs(["일반 시트 (과거)", "설문지 응답 (신규)"])
    with tab1:
        st.dataframe(base_raw[['날짜', '카테고리', '색상', '출고', '상세내역']], use_container_width=True)
    with tab2:
        st.dataframe(out_raw[['타임스탬프', '카테고리', '색상', '출고', '상세내역']], use_container_width=True)