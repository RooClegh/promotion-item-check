import streamlit as st
import pandas as pd

# --- [설정 부분] ---
BASE_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=0&single=true&output=csv"
OUT_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=398277773&single=true&output=csv"
google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdiLZvBYd1x-0gXxQz0cfSZq5szvXvsgCqTmi8D82lQAYIypw/viewform?usp=dialog"

# 페이지 설정
st.set_page_config(page_title="2026 판촉물 재고 현황", layout="wide", page_icon="📋")

# --- [데이터 로드 함수] ---
@st.cache_data(ttl=60)
def load_data_smart(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip', engine='python')
        df['카테고리'] = df['카테고리'].astype(str).str.strip()
        df['색상'] = df['색상'].astype(str).str.strip()
        if '출고' in df.columns:
            df['출고'] = pd.to_numeric(df['출고'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        else:
            df['출고'] = 0
        return df
    except:
        return pd.DataFrame()

# --- [재고 계산] ---
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

base_raw = load_data_smart(BASE_STOCK_URL)
out_raw = load_data_smart(OUT_STOCK_URL)

past_out_sum = base_raw.groupby(['카테고리', '색상'])['출고'].sum().reset_index()
new_out_sum = out_raw.groupby(['카테고리', '색상'])['출고'].sum().reset_index()

final_df = pd.merge(inventory_df, past_out_sum, on=['카테고리', '색상'], how='left', suffixes=('', '_과거')).fillna(0)
final_df = pd.merge(final_df, new_out_sum, on=['카테고리', '색상'], how='left', suffixes=('', '_신규')).fillna(0)
final_df['현재재고'] = final_df['입고'] - final_df['출고'] - final_df['출고_신규']

# --- [UI 구성] ---

# 1. 앱 제목 변경
st.title("📊 2026 판촉물 재고 현황 및 출고 신청")

# 2. 신청서 버튼 제목 변경 및 스타일링
st.link_button("🔗 출고 신청서 작성(구글 폼)", google_form_url, use_container_width=True, type="primary")

st.markdown("---")

# 3. 색상별 카드 형식 표시
# 색상별 이모지 매칭
color_icons = {
    "블랙": "⚫", "실버": "⚪", "핑크": "🌸", "그린": "🟢", 
    "우드": "🪵", "블루": "🔵", "화이트": "⚪"
}

emoji_dict = {"무선충전기": "⚡", "우산": "☔"}

# --- [기존의 UI 구성 부분에서 카드 출력 로직만 이걸로 교체하세요] ---

for cat in ["무선충전기", "우산"]:
    st.subheader(f"{emoji_dict.get(cat, '📦')} {cat} 현황")
    cat_items = final_df[final_df['카테고리'] == cat]
    
    cols = st.columns(4)
    for i, (idx, row) in enumerate(cat_items.iterrows()):
        with cols[i % 4]:
            with st.container(border=True):
                icon = color_icons.get(row['색상'], "▫️")
                st.markdown(f"### {icon} {row['색상']}")
                
                current_stock = int(row['현재재고'])
                
                # 'black' 글자가 뜨지 않도록 일반 굵게 처리로 변경
                # 만약 5개 미만이면 주의 표시(⚠️)를 붙여줍니다.
                warning = "⚠️ " if current_stock < 5 else ""
                
                st.markdown(f"**현재 잔량: {warning}{current_stock} 개**")
                st.caption(f"누적 출고: {int(row['출고'] + row['출고_신규'])}개")

st.markdown("---")
with st.expander("🔍 데이터 동기화 정보 확인"):
    st.write("마지막 업데이트: 실시간 (1분 간격 자동 갱신)")
    st.dataframe(final_df[['카테고리', '색상', '입고', '현재재고']], use_container_width=True)