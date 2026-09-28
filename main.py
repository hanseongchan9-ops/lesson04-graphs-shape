import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"

# 데이터 불러오기 및 전처리 함수
@st.cache_data
def load_data(url):
    try:
        df = pd.read_csv(url, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(url, encoding='cp949')
    
    # 장르 전처리 (첫 번째 장르만 추출)
    if 'genre' in df.columns:
        df['genre'] = df['genre'].fillna('미상').astype(str).apply(lambda x: x.split('|')[0].strip())
    
    # 국가 전처리 (결측치 처리)
    if 'nation' in df.columns:
        df['nation'] = df['nation'].fillna('미상').astype(str).str.strip()

    # 수치형 데이터 변환 (콤마 제거 및 예외 처리)
    numeric_cols = ['total_audi', 'first_scrn', 'first_show', 'first_week_audi', 'days_in_top10']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(',', ''), 
                errors='coerce'
            ).fillna(0)

    # 집계용 수량 컬럼 생성
    df['movie_count'] = 1

    return df

try:
    df = load_data(DATA_URL)

    # --------------------------------------------------
    # 1. 장르별 영화 편수 분포 (도넛 그래프)
    # --------------------------------------------------
    st.header("1. 장르별 영화 편수 분포")

    genre_counts = df['genre'].value_counts().reset_index()
    genre_counts.columns = ['장르', '편수']

    fig1 = px.pie(
        genre_counts,
        names='장르',
        values='편수',
        hole=0.4,
        title="장르별 영화 편수 비율"
    )

    fig1.update_traces(
        textinfo='percent+label',
        hovertemplate='<b>장르</b>: %{label}<br><b>편수</b>: %{value}편<br><b>비율</b>: %{percent}'
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.divider()
    st.subheader("이 그래프로 알 수 있는 것")
    st.write("박스오피스 상위권에 도달한 영화 중 특정 소수 장르가 전체 편수의 과반 이상을 차지하여 장르 편중 현상이 나타남을 알 수 있습니다.")
    st.divider()

    # --------------------------------------------------
    # 2. 장르 및 영화별 총 관객 수 분포 (트리맵)
    # --------------------------------------------------
    st.header("2. 장르 및 영화별 총 관객 수 분포")

    fig2 = px.treemap(
        df,
        path=['genre', 'movieNm'],
        values='total_audi',
        title="장르-영화별 총 관객 수 트리맵"
    )

    fig2.update_traces(
        hovertemplate='<b>영화명/장르</b>: %{label}<br><b>총 관객 수</b>: %{value:,}명'
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("이 그래프로 알 수 있는 것")
    st.write("각 장르 내에서 총 관객 수 집계에 크게 기여한 대표 흥행작과 장르별 관객 점유 비중을 시각적으로 파악할 수 있습니다.")
    st.divider()

    # --------------------------------------------------
    # 3. 총 관객 수 분포 (히스토그램)
    # --------------------------------------------------
    st.header("3. 총 관객 수 분포")

    fig3 = px.histogram(
        df,
        x='total_audi',
        nbins=30,
        title="영화별 총 관객 수 구간 분포",
        labels={'total_audi': '총 관객 수'}
    )

    fig3.update_traces(
        hovertemplate='<b>관객 수 구간</b>: %{x:,}명<br><b>영화 수</b>: %{y}편'
    )

    fig3.update_layout(
        xaxis_title="총 관객 수 (명)",
        yaxis_title="영화 수 (편)"
    )

    st.plotly_chart(fig3, use_container_width=True)

    if not df.empty and 'total_audi' in df.columns:
        top_movie_row = df.loc[df['total_audi'].idxmax()]
        top_movie_name = top_movie_row['movieNm']
        top_movie_audi = int(top_movie_row['total_audi'])

        st.divider()
        st.subheader("이 그래프로 알 수 있는 것")
        st.write(
            f"대부분의 영화가 관객 수 하위 구간(약 100만~300만 명 이하)에 집중되어 있는 오른쪽으로 꼬리가 긴(Right-skewed) 분포를 보이며, "
            f"가장 관객이 많은 영화는 '{top_movie_name}'(총 {top_movie_audi:,}명)입니다."
        )
        st.divider()

    # --------------------------------------------------
    # 4. 개봉일 스크린 수와 총 관객 수의 관계 (산점도)
    # --------------------------------------------------
    st.header("4. 개봉일 스크린 수와 총 관객 수의 관계")

    fig4 = px.scatter(
        df,
        x='first_scrn',
        y='total_audi',
        color='genre',
        hover_name='movieNm',
        title="개봉일 스크린 수 vs 총 관객 수",
        labels={
            'first_scrn': '개봉일 스크린 수',
            'total_audi': '총 관객 수',
            'genre': '장르'
        }
    )

    fig4.update_traces(
        hovertemplate='<b>영화명</b>: %{hovertext}<br><b>개봉일 스크린 수</b>: %{x:,}개<br><b>총 관객 수</b>: %{y:,}명'
    )

    fig4.update_layout(
        xaxis_title="개봉일 스크린 수 (개)",
        yaxis_title="총 관객 수 (명)"
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    st.subheader("이 그래프로 알 수 있는 것")
    st.write(
        "개봉일 스크린 수가 많을수록 대체로 총 관객 수가 증가하는 양의 상관관계를 보이지만, "
        "일부 영화는 스크린 수에 비해 관객 수가 매우 높거나 낮게 나타나는 등 흥행 성과에 차이가 존재함을 알 수 있습니다."
    )
    st.divider()

    # --------------------------------------------------
    # 5. 주요 장르별 총 관객 수 분포 (박스플롯)
    # --------------------------------------------------
    st.header("5. 주요 장르별 총 관객 수 분포")

    genre_counts_series = df['genre'].value_counts()
    target_genres = genre_counts_series[genre_counts_series >= 10].index
    df_filtered = df[df['genre'].isin(target_genres)]

    if not df_filtered.empty:
        fig5 = px.box(
            df_filtered,
            x='genre',
            y='total_audi',
            color='genre',
            hover_name='movieNm',
            points='outliers',
            title="10편 이상 개봉 장르별 총 관객 수 분포",
            labels={
                'genre': '장르',
                'total_audi': '총 관객 수'
            }
        )

        fig5.update_traces(
            hovertemplate='<b>영화명</b>: %{hovertext}<br><b>총 관객 수</b>: %{y:,}명'
        )

        fig5.update_layout(
            xaxis_title="장르",
            yaxis_title="총 관객 수 (명)",
            showlegend=False
        )

        st.plotly_chart(fig5, use_container_width=True)

        st.divider()
        st.subheader("이 그래프로 알 수 있는 것")
        st.write(
            "주요 장르별 관객 수 중앙값과 상위/하위 분포 범위를 비교할 수 있으며, "
            "상자 밖 이상치(Outlier) 점에 마우스를 올리면 각 장르 내에서 이례적인 흥행을 기록한 대표 영화명을 확인할 수 있습니다."
        )
        st.divider()

    # --------------------------------------------------
    # 6. 개봉일 스크린 수, 총 관객 수, 첫 주 관객 수의 관계 (버블 그래프)
    # --------------------------------------------------
    st.header("6. 개봉일 스크린 수, 총 관객 수, 첫 주 관객 수의 관계")

    fig6 = px.scatter(
        df,
        x='first_scrn',
        y='total_audi',
        size='first_week_audi',
        color='genre',
        hover_name='movieNm',
        size_max=40,
        title="개봉일 스크린 수 vs 총 관객 수 (버블 크기: 개봉 첫 주 관객 수)",
        labels={
            'first_scrn': '개봉일 스크린 수',
            'total_audi': '총 관객 수',
            'first_week_audi': '개봉 첫 주 관객 수',
            'genre': '장르'
        }
    )

    fig6.update_traces(
        hovertemplate='<b>영화명</b>: %{hovertext}<br><b>개봉일 스크린 수</b>: %{x:,}개<br><b>총 관객 수</b>: %{y:,}명'
    )

    fig6.update_layout(
        xaxis_title="개봉일 스크린 수 (개)",
        yaxis_title="총 관객 수 (명)"
    )

    st.plotly_chart(fig6, use_container_width=True)

    st.divider()
    st.subheader("이 그래프로 알 수 있는 것")
    st.write(
        "버블 크기(개봉 첫 주 관객 수)를 통해 초기 흥행 속도, 초기 스크린 확보 수, 최종 총 관객 수 간의 상관관계를 종합적으로 비교할 수 있습니다."
    )
    st.divider()

    # --------------------------------------------------
    # 7. 제작 국가 및 장르별 영화 편수 구조 (선버스트 그래프)
    # --------------------------------------------------
    st.header("7. 제작 국가 및 장르별 영화 편수 구조")

    fig7 = px.sunburst(
        df,
        path=['nation', 'genre'],
        values='movie_count',
        title="제작 국가 - 장르 계층별 영화 편수 분포"
    )

    fig7.update_traces(
        hovertemplate='<b>국가/장르</b>: %{label}<br><b>영화 편수</b>: %{value}편'
    )

    st.plotly_chart(fig7, use_container_width=True)

    st.divider()
    st.subheader("이 그래프로 알 수 있는 것")
    st.write(
        "제작 국가별 영화 비중과 함께, 각 국가 내에서 어떤 장르의 영화가 주를 이루는지 계층적 구조로 확인할 수 있습니다."
    )
    st.divider()

    # --------------------------------------------------
    # 8. 10위권에 오래 머문 영화는 총 관객도 많은가 (산점도)
    # --------------------------------------------------
    st.header("8. 10위권에 오래 머문 영화는 총 관객도 많은가")

    fig8 = px.scatter(
        df,
        x='days_in_top10',
        y='total_audi',
        color='genre',
        hover_name='movieNm',
        title="10위권에 오래 머문 영화는 총 관객도 많은가",
        labels={
            'days_in_top10': '10위권에 머문 날수',
            'total_audi': '총 관객 수',
            'genre': '장르'
        }
    )

    fig8.update_traces(
        hovertemplate='<b>영화명</b>: %{hovertext}<br><b>10위권 머문 날수</b>: %{x}일<br><b>총 관객 수</b>: %{y:,}명'
    )

    fig8.update_layout(
        xaxis_title="10위권에 머문 날수 (일)",
        yaxis_title="총 관객 수 (명)"
    )

    st.plotly_chart(fig8, use_container_width=True)

    st.divider()
    st.subheader("이 그래프로 알 수 있는 것")
    st.write(
        "10위권 머문 날수가 길수록 대체로 총 관객 수가 늘어나는 강한 양의 상관관계를 보이지만, "
        "유지 기간이 비슷하더라도 총 관객 수의 절대적인 규모에는 영화별 차이가 크게 나타남을 알 수 있습니다."
    )
    st.divider()

except Exception as e:
    st.error(f"데이터를 불러오거나 처리하는 중 오류가 발생했습니다: {e}")
