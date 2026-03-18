import streamlit as st
import pandas as pd

# --- [1. 설정 부분: 구글 시트 및 폼 링크] ---
BASE_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=0&single=true&output=csv"
OUT_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=398277773&single=true&output=csv"
google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdiLZvBYd1x-0gXxQz0cfSZq5szvXvsgCqTmi8D82lQAYIypw/viewform?usp=dialog"

st.set_page_config(page_title="2026 판촉물 재고 현황", layout="wide", page_icon="📋")

# --- [2. 데이터 로드 및 전처리 함수] ---
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

# --- [3. 재고 계산 로직] ---
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

# --- [4. UI 화면 구성: 상단 카드 섹션] ---
st.title("📊 2026 판촉물 재고 현황 및 출고 신청")
st.link_button("🔗 출고 신청서 작성(구글 폼)", google_form_url, use_container_width=True, type="primary")
st.divider()

color_icons = {
    "블랙": "⚫", "실버": "⚪", "핑크": "🌸", "그린": "🟢", 
    "우드": "🪵", "블루": "🔵", "화이트": "⚪"
}
emoji_dict = {"무선충전기": "⚡", "우산": "☔"}

for cat in ["무선충전기", "우산"]:
    st.subheader(f"{emoji_dict.get(cat, '📦')} {cat} 현황")
    cat_items = final_df[final_df['카테고리'] == cat]
    
    cols = st.columns(4)
    for i, (idx, row) in enumerate(cat_items.iterrows()):
        with cols[i % 4]:
            current_stock = int(row['현재재고'])
            card_bg = "#852222" if current_stock < 5 else "#262730"
            
            with st.container(border=True):
                icon = color_icons.get(row['색상'], "▫️")
                st.markdown(f"""
                    <div style='background-color: {card_bg}; padding: 15px; border-radius: 10px; color: white; border: 1px solid #4A4A4A;'>
                        <div style='font-size: 0.85rem; opacity: 0.8; margin-bottom: 8px;'>
                            {icon} {row['색상']}
                        </div>
                        <div style='font-size: 1.8rem; font-weight: 900; line-height: 1.2;'>
                            잔량: {current_stock}개
                        </div>
                        <div style='font-size: 0.75rem; opacity: 0.7; margin-top: 12px;'>
                            누적 출고: {int(row['출고'] + row['출고_신규'])}개
                        </div>
                    </div>
                """, unsafe_allow_html=True)

st.divider()

# --- [5. UI 화면 구성: 하단 상세 표 섹션] ---
color_codes = {
    "블랙": "#000000", "실버": "#C0C0C0", "핑크": "#FFB6C1", "그린": "#2E8B57", 
    "우드": "#DEB887", "블루": "#4169E1", "화이트": "#FFFFFF"
}

with st.expander("📝 전체 상세 재고 표 (실시간 동기화 정보)"):
    st.write("마지막 업데이트: 1분 간격 자동 갱신")
    
    # 표 상단 제목 및 스타일 정의
    html_table = """
    <style>
        .inventory-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .inventory-table th {
            background-color: #f8f9fa;
            color: #333;
            padding: 12px;
            border: 1px solid #dee2e6;
            font-weight: bold;
        }
        .inventory-table td {
            padding: 10px;
            border: 1px solid #dee2e6;
            text-align: center;
        }
    </style>
    <table class='inventory-table'>
        <thead>
            <tr>
                <th>구분</th>
                <th>카테고리</th>
                <th>색상</th>
                <th>최초 입고</th>
                <th>누적 출고</th>
                <th>현재 잔량</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for idx, row in final_df.iterrows():
        cat = row['카테고리']
        color = row['색상']
        cat_emoji = emoji_dict.get(cat, "📦")
        color_emoji = color_icons.get(color, "▫️")
        color_hex = color_codes.get(color, "#FFFFFF")
        
        # 가독성을 위한 텍스트 색상 결정
        text_color = "white" if color in ["블랙", "블루", "그린"] else "black"
        
        current_stock = int(row['현재재고'])
        stock_style = "color: #FF4B4B; font-weight: bold;" if current_stock < 5 else ""
        
        html_table += f"""
            <tr>
                <td style='font-size: 1.2rem;'>{cat_emoji}</td>
                <td>{cat}</td>
                <td style='background-color: {color_hex}; color: {text_color}; font-weight: bold;'>
                    {color_emoji} {color}
                </td>
                <td>{int(row['입고'])}개</td>
                <td>{int(row['출고'] + row['출고_신규'])}개</td>
                <td style='{stock_style}'>{current_stock}개</td>
            </tr>
        """
        
    html_table += "</tbody></table>"
    st.markdown(html_table, unsafe_allow_html=True)