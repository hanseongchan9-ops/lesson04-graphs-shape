import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

# 데이터 불러오기 함수 (예외 처리 추가)
@st.cache_data
def load_data(url):
    try:
        df = pd.read_csv(url, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(url, encoding='cp949')
    
    if 'genre' in df.columns:
        df['genre'] = df['genre'].fillna('미상').astype(str).apply(lambda x: x.split('|')[0].strip())
    return df

# 메인 실행 구역
try:
    df = load_data(DATA_URL)

    # 1. 장르별 영화 편수 분포 (도넛 그래프)
    st.header("1. 장르별 영화 편수 분포")

    genre_counts = df['genre'].value_counts().reset_index()
    genre_counts.columns = ['장르', '편수']

    fig = px.pie(
        genre_counts,
        names='장르',
        values='편수',
        hole=0.4,
        title="장르별 영화 편수 비율"
    )

    fig.update_traces(
        textinfo='percent+label',
        hovertemplate='<b>장르</b>: %{label}<br><b>편수</b>: %{value}편<br><b>비율</b>: %{percent}'
    )

    st.plotly_chart(fig, use_container_width=True)

    # 그래프 해석 구역
    st.divider()
    st.subheader("이 그래프로 알 수 있는 것")
    st.write("박스오피스 상위권에 도달한 영화 중 특정 소수 장르가 전체 편수의 과반 이상을 차지하여 장르 편중 현상이 나타남을 알 수 있습니다.")
    st.divider()

except Exception as e:
    st.error(f"데이터를 불러오거나 처리하는 중 오류가 발생했습니다: {e}")
