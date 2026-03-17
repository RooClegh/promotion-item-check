import streamlit as st
import pandas as pd

# --- [설정 부분: 이 부분을 정확히 채워주세요] ---
# 1. 구글 시트 '웹에 게시' CSV 링크
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1QIJO04NgGIM4SUxcsMp8Zl2WuWRwj0bnwh4svKoILhg/edit?usp=sharing"
# 2. 구글 폼 주소
google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdiLZvBYd1x-0gXxQz0cfSZq5szvXvsgCqTmi8D82lQAYIypw/viewform?usp=dialog"

# --- [1. 기초 재고 및 이모티콘 설정] ---
# 카테고리별 이모티콘 설정
emoji_dict = {
    "무선충전기": "⚡",
    "우산": "☔"
}

initial_stock = [
    # 무선충전기 (블랙, 실버, 그린, 핑크)
    {"카테고리": "무선충전기", "색상": "블랙", "기초수량": 50},
    {"카테고리": "무선충전기", "색상": "실버", "기초수량": 50},
    {"카테고리": "무선충전기", "색상": "그린", "기초수량": 50},
    {"카테고리": "무선충전기", "색상": "핑크", "기초수량": 50},
    # 우산 (블랙, 블루, 그린, 우드)
    {"카테고리": "우산", "색상": "블랙", "기초수량": 100},
    {"카테고리": "우산", "색상": "블루", "기초수량": 100},
    {"카테고리": "우산", "색상": "그린", "기초수량": 100},
    {"카테고리": "우산", "색상": "우드", "기초수량": 100},
]
base_df = pd.DataFrame(initial_stock)

# --- [2. 데이터 로드 및 계산 로직] ---
st.set_page_config(page_title="판촉물 재고 관리", layout="wide", page_icon="📋")

@st.cache_data(ttl=60)
def get_out_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        # 구글 폼 응답 시트의 열 개수에 맞춰 강제로 이름을 부여합니다.
        # [타임스탬프, 카테고리, 색상, 수량, 업체명, 작성자] 순서라고 가정합니다.
        df.columns = ['시간', '카테고리', '색상', '수량', '업체명', '작성자'] + list(df.columns[6:])
        # 수량 데이터를 숫자로 변환 (오류 방지)
        df['수량'] = pd.to_numeric(df['수량'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        return pd.DataFrame(columns=['시간', '카테고리', '색상', '수량', '업체명', '작성자'])

out_df = get_out_data()

# 실시간 재고 계산
out_sum = out_df.groupby(['카테고리', '색상'])['수량'].sum().reset_index()
final_df = pd.merge(base_df, out_sum, on=['카테고리', '색상'], how='left').fillna(0)
final_df['현재재고'] = final_df['기초수량'] - final_df['수량']

# --- [3. 화면 구성] ---
st.title("📋 실시간 판촉물 재고 현황")
st.info("💡 구글 폼으로 출고를 입력하면 1분 내로 아래 재고에 반영됩니다.")

# 출고 신청 버튼을 상단에 배치하여 접근성 향상
st.link_button("🚀 즉시 출고 신청서 작성 (구글 폼)", google_form_url, use_container_width=True)
st.divider()

# 카드 스타일 디자인
categories = ["무선충전기", "우산"] # 순서 고정
for cat in categories:
    emoji = emoji_dict.get(cat, "📦")
    st.subheader(f"{emoji} {cat}")
    
    cat_items = final_df[final_df['카테고리'] == cat]
    cols = st.columns(4) # 4개 색상을 한 줄에 표시
    
    for i, (idx, row) in enumerate(cat_items.iterrows()):
        with cols[i % 4]:
            st.metric(label=row['색상'], value=f"{int(row['현재재고'])} 개")

st.divider()

# 최근 출고 내역 확인
with st.expander("📝 최근 상세 출고 기록 확인"):
    st.dataframe(out_df.sort_values(by='시간', ascending=False), use_container_width=True)