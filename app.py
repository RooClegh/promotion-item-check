import streamlit as st
import pandas as pd

# 1. 페이지 설정 (모바일에서 보기 좋게!)
st.set_page_config(page_title="판촉물 재고 현황", layout="wide")

st.title("📦 실시간 판촉물 재고 대시보드")
st.caption("우리 직원들을 위한 실시간 재고 확인 서비스입니다.")
st.divider()

# 2. 데이터 불러오기
# 데이터가 바뀔 때마다 앱이 새로 읽어올 수 있도록 캐싱은 일단 제외할게요.
try:
    df = pd.read_csv('inventory_data.csv')
    # 혹시 모를 빈 칸(NaN)을 0으로 채워주는 센스!
    df['입고'] = df['입고'].fillna(0)
    df['출고'] = df['출고'].fillna(0)
except FileNotFoundError:
    st.error("데이터 파일을 찾을 수 없습니다. inventory_data.csv 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

# 3. 데이터 계산 (카테고리별/색상별 재고 합산)
# 입고 총합 - 출고 총합 = 현재 재고
inventory = df.groupby(['카테고리', '색상']).apply(
    lambda x: x['입고'].sum() - x['출고'].sum()
).reset_index(name='현재재고')

# 4. 화면 구성 (카드 스타일로 보기 좋게!)
# 카테고리별로 그룹을 지어 보여줍니다.
categories = inventory['카테고리'].unique()

for cat in categories:
    st.subheader(f"📍 {cat}")
    cols = st.columns(4) # 한 줄에 4개씩 카드 배치
    
    cat_items = inventory[inventory['카테고리'] == cat]
    
    for i, (idx, row) in enumerate(cat_items.iterrows()):
        with cols[i % 4]:
            # 카드 형태의 메트릭(Metric) 위젯 사용
            st.metric(label=row['색상'], value=f"{int(row['현재재고'])} 개")
    st.divider()

# 5. 상세 내역 보기 (선택 사항)
with st.expander("📝 전체 입출고 내역 확인하기"):
    st.dataframe(df.sort_values(by='날짜', ascending=False), use_container_width=True)