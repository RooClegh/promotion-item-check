import streamlit as st
import pandas as pd

# --- [설정 부분] ---
# 1. 아까 '웹에 게시'에서 복사한 .csv 링크를 여기에 넣으세요
SHEET_CSV_URL = "여기에_복사한_링크를_넣으세요"

# 2. 기초 재고 데이터 (기존에 엑셀로 관리하던 초기 수량)
# 실제로는 이것도 구글 시트의 다른 탭에서 불러오면 더 좋습니다!
initial_stock = [
    {"카테고리": "무선충전기", "색상": "블랙", "기초수량": 50},
    {"카테고리": "무선충전기", "색상": "그린", "기초수량": 30},
    {"카테고리": "우산", "색상": "블랙", "기초수량": 100},
    {"카테고리": "우산", "색상": "블루", "기초수량": 80},
]
base_df = pd.DataFrame(initial_stock)

# --- [데이터 로드 및 계산] ---
st.set_page_config(page_title="판촉물 재고 관리", layout="wide", page_icon="📋")

@st.cache_data(ttl=60) # 60초마다 데이터를 새로 읽어옵니다
def get_out_data():
    try:
        # 구글 폼 응답 데이터 읽기
        df = pd.read_csv(SHEET_CSV_URL)
        # 구글 폼 열 이름에 맞춰 수정 (예: '출고 수량', '카테고리', '색상')
        # 보통 폼 데이터는 [타임스탬프, 카테고리, 색상, 수량, ...] 순서입니다.
        df.columns = ['시간', '카테고리', '색상', '수량', '업체명', '작성자']
        return df
    except:
        return pd.DataFrame(columns=['시간', '카테고리', '색상', '수량', '업체명', '작성자'])

out_df = get_out_data()

# 실시간 재고 계산 (기초수량 - 출고합계)
out_sum = out_df.groupby(['카테고리', '색상'])['수량'].sum().reset_index()
final_df = pd.merge(base_df, out_sum, on=['카테고리', '색상'], how='left').fillna(0)
final_df['현재재고'] = final_df['기초수량'] - final_df['수량']

# --- [화면 구성] ---
st.title("📋 실시간 판촉물 재고 현황")
st.info("💡 구글 폼으로 출고를 입력하면 1분 내로 아래 재고에 반영됩니다.")

# 카드 스타일 디자인 (기존 코드 활용)
categories = final_df['카테고리'].unique()
for cat in categories:
    st.subheader(f"📦 {cat}")
    cols = st.columns(4)
    cat_items = final_df[final_df['카테고리'] == cat]
    
    for i, (idx, row) in enumerate(cat_items.iterrows()):
        with cols[i % 4]:
            st.metric(label=row['색상'], value=f"{int(row['현재재고'])} 개")

# --- 이 부분을 통째로 복사해서 교체하세요 ---
st.divider()

# 출고 신청 버튼 섹션
st.subheader("📤 수량 신청하기")

# 주소는 반드시 한 줄로 쭉 이어져야 합니다!
google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdiLZvBYd1x-0gXxQz0cfSZq5szvXvsgCqTmi8D82lQAYIypw/viewform?usp=dialog"

# 버튼 만들기
st.link_button("🚀 출고 신청서 작성 (구글 폼 열기)", google_form_url, use_container_width=True)
# ------------------------------------------