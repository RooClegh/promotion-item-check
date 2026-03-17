import streamlit as st
import pandas as pd

# --- [설정 부분: 두 개의 링크를 정확히 넣어주세요] ---
# 1. 기초 재고(입고량) 시트의 CSV 링크
BASE_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=0&single=true&output=csv"
# 2. 설문지 응답(출고량) 시트의 CSV 링크 
OUT_STOCK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQceyq1k7axfRWw6uhud07HCyXKcnRpvV3HAHiiF_s9I6WodxZExSgRJBIPf62Xw_DZ9-UUr3-76iuY/pub?gid=398277773&single=true&output=csv"
# 3. 구글 폼 주소
google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdiLZvBYd1x-0gXxQz0cfSZq5szvXvsgCqTmi8D82lQAYIypw/viewform?usp=dialog"

# --- [1. 설정 및 데이터 로드] ---
st.set_page_config(page_title="판촉물 재고 관리", layout="wide", page_icon="📋")

emoji_dict = {"무선충전기": "⚡", "우산": "☔"}

@st.cache_data(ttl=60)
def load_data(url, columns):
    try:
        # on_bad_lines='skip': 칸 수가 안 맞는 이상한 줄은 일단 무시하고 넘어갑니다.
        # engine='python': 좀 더 정밀하게 데이터를 읽어옵니다.
        df = pd.read_csv(url, skiprows=1, names=columns, on_bad_lines='skip', engine='python')
        
        # 실제 데이터가 있는 행만 남기기 (카테고리가 비어있는 행 삭제)
        df = df.dropna(subset=['카테고리'])
        
        for col in df.columns:
            if '수량' in col:
                # 숫자가 아닌 데이터는 0으로 처리
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        # 에러가 나면 화면에 어떤 링크에서 문제가 생겼는지 보여줍니다.
        st.error(f"데이터 로드 오류 ({url[:30]}...): {e}")
        return pd.DataFrame(columns=columns)

# 데이터 불러오기
# 기초 재고 시트 컬럼: [카테고리, 색상, 기초수량] 순서라고 가정합니다.
base_df = load_data(BASE_STOCK_URL, ['카테고리', '색상', '기초수량'])
# 설문지 응답 시트 컬럼: [시간, 카테고리, 색상, 수량, 업체명, 작성자]
out_df = load_data(OUT_STOCK_URL, ['시간', '카테고리', '색상', '수량', '업체명', '작성자'])

# --- [2. 재고 계산 로직] ---
# 출고량 합계 계산
out_sum = out_df.groupby(['카테고리', '색상'])['수량'].sum().reset_index()

# 기초 재고와 출고 합계 합치기
final_df = pd.merge(base_df, out_sum, on=['카테고리', '색상'], how='left').fillna(0)
final_df['현재재고'] = final_df['기초수량'] - final_df['수량']

# --- [3. 화면 구성] ---
st.title("📋 실시간 판촉물 재고 현황")
st.info("💡 모든 데이터는 구글 시트와 실시간 연동됩니다. (1분 간격)")

st.link_button("🚀 즉시 출고 신청서 작성 (구글 폼)", google_form_url, use_container_width=True)
st.divider()

categories = ["무선충전기", "우산"]
for cat in categories:
    emoji = emoji_dict.get(cat, "📦")
    st.subheader(f"{emoji} {cat}")
    
    cat_items = final_df[final_df['카테고리'] == cat]
    cols = st.columns(4)
    
    # 기초 재고 시트에 등록된 색상들을 순서대로 표시
    for i, (idx, row) in enumerate(cat_items.iterrows()):
        with cols[i % 4]:
            st.metric(label=row['색상'], 
                      value=f"{int(row['현재재고'])} 개", 
                      delta=f"기초: {int(row['기초수량'])}")

st.divider()
with st.expander("📝 최근 상세 출고 기록 확인"):
    st.dataframe(out_df.sort_values(by='시간', ascending=False), use_container_width=True)