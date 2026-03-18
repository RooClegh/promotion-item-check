import streamlit as st
import pandas as pd

# --- [1. 설정 부분: 구글 시트 및 폼 링크] ---
# 일반 시트 (과거 출고 내역 포함)
BASE_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=0&single=true&output=csv"
# 설문지 응답 시트 (신규 출고 내역)
OUT_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=398277773&single=true&output=csv"
# 구글 폼 주소
google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdiLZvBYd1x-0gXxQz0cfSZq5szvXvsgCqTmi8D82lQAYIypw/viewform?usp=dialog"

# 페이지 기본 설정
st.set_page_config(page_title="2026 판촉물 재고 현황", layout="wide", page_icon="📋")

# --- [2. 데이터 로드 및 전처리 함수] ---
@st.cache_data(ttl=60)
def load_data_smart(url):
    try:
        # 제목줄을 기준으로 데이터를 읽어옵니다.
        df = pd.read_csv(url, on_bad_lines='skip', engine='python')
        # 매칭을 위해 카테고리와 색상 열의 공백 제거
        df['카테고리'] = df['카테고리'].astype(str).str.strip()
        df['색상'] = df['색상'].astype(str).str.strip()
        # '출고' 열의 데이터를 숫자로 변환 (쉼표 제거 포함)
        if '출고' in df.columns:
            df['출고'] = pd.to_numeric(df['출고'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        else:
            df['출고'] = 0
        return df
    except:
        return pd.DataFrame()

# --- [3. 재고 계산 로직] ---

# A. 최초 입고량 설정 (고정 수치)
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

# B. 각 시트에서 출고 데이터 불러오기
base_raw = load_data_smart(BASE_STOCK_URL)
out_raw = load_data_smart(OUT_STOCK_URL)

# C. 출고 합계 계산
past_out_sum = base_raw.groupby(['카테고리', '색상'])['출고'].sum().reset_index()
new_out_sum = out_raw.groupby(['카테고리', '색상'])['출고'].sum().reset_index()

# D. 데이터 병합 및 최종 재고 산출
final_df = pd.merge(inventory_df, past_out_sum, on=['카테고리', '색상'], how='left', suffixes=('', '_과거')).fillna(0)
final_df = pd.merge(final_df, new_out_sum, on=['카테고리', '색상'], how='left', suffixes=('', '_신규')).fillna(0)
final_df['현재재고'] = final_df['입고'] - final_df['출고'] - final_df['출고_신규']

# --- [4. UI 화면 구성] ---

# 앱 제목 및 신청 버튼
st.title("📊 2026 판촉물 재고 현황 및 출고 신청")
st.link_button("🔗 출고 신청서 작성(구글 폼)", google_form_url, use_container_width=True, type="primary")
st.divider()

# 시각화용 설정
color_icons = {
    "블랙": "⚫", "실버": "⚪", "핑크": "🌸", "그린": "🟢", 
    "우드": "🪵", "블루": "🔵", "화이트": "⚪"
}
emoji_dict = {"무선충전기": "⚡", "우산": "☔"}

# 카테고리별 재고 카드 출력
for cat in ["무선충전기", "우산"]:
    st.subheader(f"{emoji_dict.get(cat, '📦')} {cat} 현황")
    cat_items = final_df[final_df['카테고리'] == cat]
    
# 4개씩 한 줄에 표시
    cols = st.columns(4)
    for i, (idx, row) in enumerate(cat_items.iterrows()):
        with cols[i % 4]:
            # 카드 배경색을 어둡게 설정하여 하얀색 글자가 잘 보이게 합니다.
            current_stock = int(row['현재재고'])
            
            # 재고가 5개 미만이면 배경을 약간 붉은 계열로, 아니면 진한 회색(#262730)으로!
            card_bg = "#852222" if current_stock < 5 else "#262730"
            
            with st.container(border=True):
                # HTML을 이용해 카드 내부 스타일을 직접 제어합니다.
                icon = color_icons.get(row['색상'], "▫️")
                
                st.markdown(f"""
                    <div style='background-color: {card_bg}; padding: 15px; border-radius: 10px; color: white;'>
                        <div style='font-size: 0.85rem; opacity: 0.8; margin-bottom: 5px;'>
                            {icon} {row['색상']}
                        </div>
                        
                        <div style='font-size: 1.8rem; font-weight: 900; line-height: 1.2;'>
                            잔량: {current_stock}개
                        </div>
                        
                        <div style='font-size: 0.75rem; opacity: 0.7; margin-top: 10px;'>
                            누적 출고: {int(row['출고'] + row['출고_신규'])}개
                        </div>
                    </div>
                """, unsafe_allow_html=True)

st.divider()
with st.expander("🔍 데이터 동기화 정보 확인"):
    st.write("마지막 업데이트: 실시간 (1분 간격 자동 갱신)")
    st.dataframe(final_df[['카테고리', '색상', '입고', '현재재고']], use_container_width=True)