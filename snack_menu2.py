import streamlit as st
import pandas as pd
import oracledb
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- [DB 설정] ---
try:
    conn = oracledb.connect(user="MYID", password="mypw", dsn="localhost:1521/orcl")
    
    # --- [데이터 추출 쿼리] ---
    query = """
        SELECT
            TO_CHAR(ORDER_DATE, 'YYYY-MM-DD') AS 주문일,
            COUNT(ORDER_ID) AS 주문건수,
            SUM(TOTAL_AMT) AS 매출액
        FROM SNACK_ORDERS
        GROUP BY TO_CHAR(ORDER_DATE, 'YYYY-MM-DD')
        ORDER BY 주문일 ASC
    """
    
    # 1. 데이터를 가져와서 df라는 바구니에 담기
    df = pd.read_sql(query, conn)
    
    # 2. 파일로 저장 (배포용 도시락 싸기)
    df.to_csv("snack_data.csv", index=False, encoding='utf-8-sig')
    st.success("✅ DB 연결 성공 및 CSV 파일이 생성되었습니다!")

except Exception as e:
    # 만약 오라클 연결이 안 되면 미리 만들어둔 CSV라도 읽기
    if os.path.exists("snack_data.csv"):
        df = pd.read_csv("snack_data.csv")
        st.info("ℹ️ DB 연결 없이 저장된 CSV 파일을 불러왔습니다.")
    else:
        st.error(f"🚨 DB 연결에 실패했고, CSV 파일도 없습니다: {e}")
        st.stop()

# --- [여기서부터는 수련님의 소중한 대시보드 코드] ---

# 데이터 계산
total_val = df['매출액'].sum()
count_val = df['주문건수'].sum()
avg_check = total_val / count_val if count_val > 0 else 0

# 화면 구성
st.set_page_config(layout="wide")
st.title("----- 우리 떡볶이집 현황 -----")

st.subheader("이번 달 요약")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("총 매출액", f"{total_val:,}원")
with col2:
    st.metric("총 주문수", f"{count_val:,}건")
with col3:
    st.metric("객단가", f"{avg_check:,.0f}원")

st.divider()
st.subheader("이번 달 매출 및 주문건수 추이")

c1, c2 = st.columns(2)
with c1:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df['주문일'], y=df['매출액'], name="일별 매출액", marker_color='lightblue'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['주문일'], y=df['주문건수'], name="일별 주문건수", line=dict(color='royalblue', width=3), mode='lines+markers'), secondary_y=True)
    fig.update_layout(title_text="일자별 매출 및 주문추이")
    fig.update_xaxes(tickformat="%Y-%m-%d")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("#### 📋 일별 주문 상세내역")
    st.dataframe(df, use_container_width=True)