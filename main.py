import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(
    page_title="서울 100년 연평균 기온 변화",
    page_icon="🌡️",
    layout="centered"
)

st.title("🌡️ 서울 연평균 기온 변화 (100년 데이터)")
st.write("기상청의 서울 기온 데이터를 바탕으로 연평균 기온의 변화 추이를 살펴봅니다.")

# 데이터 로드 함수 (캐싱 처리하여 빠르게 로드)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"
    
    # 인코딩 문제(한글 인코딩 cp949/euc-kr 등) 처리
    try:
        df = pd.read_csv(url, encoding='cp949')
    except:
        df = pd.read_csv(url, encoding='utf-8')
    
    # 공백 제거 및 열 이름 통일
    df.columns = df.columns.str.strip()
    
    # '날짜' 열을 날짜형 데이터로 변환
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    # 연도 열 생성
    df['연도'] = df['날짜'].dt.year
    
    # '평균기온(℃)' 또는 '평균기온' 열 이름 자동 탐색
    temp_col = [col for col in df.columns if '평균기온' in col][0]
    
    # 결측치 제거 후 연도별 평균 기온 계산
    annual_df = df.groupby('연도')[temp_col].mean().reset_index()
    annual_df.columns = ['연도', '연평균기온']
    
    return annual_df

try:
    with st.spinner('데이터를 불러오는 중입니다...'):
        df_annual = load_data()

    # 요약 정보 표시 (KPI 카드리 형태)
    col1, col2, col3 = st.columns(3)
    start_year = int(df_annual['연도'].min())
    end_year = int(df_annual['연도'].max())
    min_temp = df_annual['연평균기온'].min()
    max_temp = df_annual['연평균기온'].max()
    
    col1.metric("조회 기간", f"{start_year}년 ~ {end_year}년")
    col2.metric("최저 연평균 기온", f"{min_temp:.1f} ℃")
    col3.metric("최고 연평균 기온", f"{max_temp:.1f} ℃")

    st.markdown("---")

    # Plotly 선 그래프 생성
    fig = px.line(
        df_annual, 
        x='연도', 
        y='연평균기온', 
        labels={'연도': '연도 (년)', '연평균기온': '연평균 기온 (℃)'},
        title="<b>서울 연도별 평균 기온 추이</b>"
    )

    # 추세선(Trendline) 추가 옵션
    show_trend = st.checkbox("📈 추세선(기온 상승 경향) 함께 보기", value=True)
    if show_trend:
        fig = px.scatter(
            df_annual, 
            x='연도', 
            y='연평균기온', 
            trendline="ols",
            labels={'연도': '연도 (년)', '연평균기온': '연평균 기온 (℃)'},
            title="<b>서울 연도별 평균 기온 추이 및 추세선</b>"
        )
        fig.update_traces(marker=dict(size=5, color='#FF5722'))

    # 그래프 스타일 커스텀 (한국어 적용 및 디자인)
    fig.update_layout(
        xaxis_title="연도",
        yaxis_title="연평균 기온 (℃)",
        hovermode="x unified",
        template="plotly_white",
        title_font_size=18
    )

    st.plotly_chart(fig, use_container_width=True)

    # 데이터 표 보기 옵션
    with st.expander("📊 상세 연도별 데이터 보기"):
        st.dataframe(df_annual.style.format({'연평균기온': '{:.2f} ℃'}), use_container_width=True)

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
