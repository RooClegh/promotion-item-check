import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목 아이콘 변경 (📋 아이콘 적용)
st.set_page_config(page_title="판촉물 재고 현황", layout="wide", page_icon="📋")

# 제목 및 설명 문구 변경
st.title("📋 실시간 판촉물 재고 대시보드")
st.caption("실시간으로 판촉물 재고 현황을 볼 수 있습니다.") # 2번 요청 반영
st.divider()

# 데이터 불러오기
try:
    df = pd.read_csv('inventory_data.csv')
    df['입고'] = df['입고'].fillna(0)
    df['출고'] = df['출고'].fillna(0)
except FileNotFoundError:
    st.error("데이터 파일을 찾을 수 없습니다.")
    st.stop()

# 재고 계산
inventory = df.groupby(['카테고리', '색상']).apply(
    lambda x: x['입고'].sum() - x['출고'].sum()
).reset_index(name='현재재고')

# 색상 매핑 (4번 요청: 한국어 색상 및 시각적 색상 코드)
color_map = {
    "블랙": {"name": "검정색", "code": "#000000"},
    "실버": {"name": "은색", "code": "#C0C0C0"},
    "핑크": {"name": "핑크색", "code": "#FFC0CB"},
    "그린": {"name": "초록색", "code": "#2E7D32"},
    "우드": {"name": "우드색", "code": "#8B4513"},
    "블루": {"name": "파란색", "code": "#1976D2"}
}

# 3. 카테고리별 이모티콘 설정
category_icons = {
    "무선충전기": "📱",
    "우산": "☂️"
}

# 화면 구성
categories = inventory['카테고리'].unique()

for cat in categories:
    # 카테고리 옆에 이모티콘 추가
    icon = category_icons.get(cat, "📦")
    st.subheader(f"{icon} {cat}")
    
    cols = st.columns(4)
    cat_items = inventory[inventory['카테고리'] == cat]
    
    for i, (idx, row) in enumerate(cat_items.iterrows()):
        color_info = color_map.get(row['색상'], {"name": row['색상'], "code": "#333333"})
        
        with cols[i % 4]:
            # 카드 스타일로 색상 강조
            st.markdown(
                f"""
                <div style="
                    padding: 20px;
                    border-radius: 10px;
                    background-color: #f0f2f6;
                    border-left: 10px solid {color_info['code']};
                    margin-bottom: 10px;
                ">
                    <p style="margin:0; font-size: 14px; color: #555;">{color_info['name']}</p>
                    <h2 style="margin:0; color: #1f1f1f;">{int(row['현재재고'])} <span style="font-size: 16px;">개</span></h2>
                </div>
                """,
                unsafe_allow_stdio=True,
                unsafe_allow_html=True
            )
    st.divider()

with st.expander("📝 전체 입출고 내역 확인하기"):
    st.dataframe(df.sort_values(by='날짜', ascending=False), use_container_width=True)