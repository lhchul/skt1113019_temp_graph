import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Streamlit 제목과 설명
st.title("온도 데이터 분석 대시보드")
st.markdown("CSV 파일을 업로드하고 원하는 통합국명을 선택해 데이터를 분석하세요.")

# 파일 업로드 기능
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # 파일을 읽어와 데이터프레임으로 변환
    data = pd.read_csv(uploaded_file)
    data['날짜'] = pd.to_datetime(data['날짜'])

    # 최신 날짜 및 1주일 데이터 계산
    latest_date = data['날짜'].max()
    one_week_ago = latest_date - timedelta(days=7)

    # 통합국명 선택 드롭다운
    selected_name = st.selectbox("통합국명을 선택하세요:", data['통합국명'].unique())

    # 선택한 통합국명 데이터 필터링
    filtered_data = data[data['통합국명'] == selected_name]
    recent_data = filtered_data[filtered_data['날짜'] == latest_date]
    week_data = filtered_data[(filtered_data['날짜'] >= one_week_ago) & (filtered_data['날짜'] <= latest_date)]

    # 1. 최신 온도의 모듈별 히트맵 생성
    st.subheader(f"{selected_name} - 최신 온도 모듈별 히트맵")
    heatmap_data = recent_data.pivot_table(values='온도', index='모듈번호', columns='hh', aggfunc=np.mean)

    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', fmt=".1f", cbar=True)
    plt.title(f'{selected_name} 모듈별 시간대 평균 온도 히트맵')
    st.pyplot(plt)

    # 2. 최근 1주일 평균 온도 계산 및 표 생성
    st.subheader("최근 1주일 평균 온도")
    daily_avg = week_data.groupby(week_data['날짜'].dt.date)['온도'].mean()
    overall_avg = week_data['온도'].mean()
    module_avg = week_data.groupby('모듈번호')['온도'].mean()

    summary_table = pd.DataFrame({
        '일자': daily_avg.index,
        '일별 평균 온도': daily_avg.values,
        '전체 평균 온도': [overall_avg] * len(daily_avg),
        '모듈별 평균 온도': [module_avg.mean()] * len(daily_avg)
    })
    st.dataframe(summary_table)

    # 3. 최근 1주일 최고/최저 온도 발생일 및 모듈번호
    st.subheader("최근 1주일 최고/최저 온도")
    max_temp_data = week_data.loc[week_data['온도'].idxmax()]
    min_temp_data = week_data.loc[week_data['온도'].idxmin()]

    extreme_temp_table = pd.DataFrame({
        '구분': ['최고 온도', '최저 온도'],
        '온도': [max_temp_data['온도'], min_temp_data['온도']],
        '발생일': [max_temp_data['날짜'].date(), min_temp_data['날짜'].date()],
        '모듈번호': [max_temp_data['모듈번호'], min_temp_data['모듈번호']]
    })
    st.dataframe(extreme_temp_table)

    # 4. CSV 다운로드 버튼 추가
    st.subheader(f"{selected_name} 데이터 다운로드")
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="CSV 파일 다운로드",
        data=csv,
        file_name=f"{selected_name}_data.csv",
        mime='text/csv',
    )

    # 5. 추가 그래프: 전체 데이터와 선택된 기간의 온도 그래프
    st.subheader("추가 그래프 옵션")
    option = st.selectbox(
        "보고 싶은 그래프를 선택하세요:",
        ["전체 데이터 보기", "최근 24시간 평균 온도", "2주 평균 온도", "일단위 최고 온도"]
    )

    if option == "전체 데이터 보기":
        st.line_chart(filtered_data.set_index('날짜')['온도'])

    elif option == "최근 24시간 평균 온도":
        last_24_hours = filtered_data[filtered_data['날짜'] >= latest_date - timedelta(days=1)]
        st.line_chart(last_24_hours.set_index('날짜')['온도'])

    elif option == "2주 평균 온도":
        last_2_weeks = filtered_data[filtered_data['날짜'] >= latest_date - timedelta(days=14)]
        weekly_avg = last_2_weeks.resample('D', on='날짜')['온도'].mean()
        st.line_chart(weekly_avg)

    elif option == "일단위 최고 온도":
        daily_max = filtered_data.resample('D', on='날짜')['온도'].max()
        st.line_chart(daily_max)
