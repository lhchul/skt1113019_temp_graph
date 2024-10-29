import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 대시보드 제목
st.title("통합국 온도 모니터링 대시보드")

# 파일 업로드 기능
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # 데이터 로드 및 날짜 변환
    data = pd.read_csv(uploaded_file)
    data['날짜'] = pd.to_datetime(data['날짜'])
    
    # 최근 날짜 계산
    latest_date = data['날짜'].max().strftime('%Y-%m-%d')
    one_week_ago = (data['날짜'].max() - timedelta(days=7)).strftime('%Y-%m-%d')

    # 통합국명 선택 드롭다운
    selected_name = st.selectbox("통합국명을 선택하세요:", data['통합국명'].unique())

    # 선택한 통합국명에 해당하는 데이터 필터링
    filtered_data = data[data['통합국명'] == selected_name]
    week_data = filtered_data[(filtered_data['날짜'] >= one_week_ago) & 
                              (filtered_data['날짜'] <= latest_date)]

    # CSV 다운로드 버튼 (폴더식 구성)
    st.subheader(f"{selected_name} 데이터 다운로드")
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="CSV 파일 다운로드",
        data=csv,
        file_name=f"{selected_name}_data.csv",
        mime='text/csv',
    )

    # 1. 모듈별 1주일 평균 온도 표
    st.subheader(f"{selected_name} - 모듈별 1주일 평균 온도")
    module_avg_table = week_data.groupby('모듈번호')['온도'].mean().reset_index()
    st.dataframe(module_avg_table)

    # 2. 1주일 일별, 전체, 모듈별 평균 온도 표
    st.subheader("1주일 평균 온도")
    daily_avg = week_data.groupby(week_data['날짜'].dt.date)['온도'].mean()
    overall_avg = week_data['온도'].mean()
    module_avgs = week_data.groupby('모듈번호')['온도'].mean()

    summary_table = pd.DataFrame({
        '일자': daily_avg.index,
        '일별 평균 온도': daily_avg.values,
        '전체 평균 온도': [overall_avg] * len(daily_avg)
    })
    for module, avg in module_avgs.items():
        summary_table[f'{module} 평균 온도'] = avg

    st.dataframe(summary_table)

    # 3. 1주일 최고/최저 온도 발생일 및 모듈번호 표
    st.subheader("1주일 최고/최저 온도")
    max_temp = week_data.loc[week_data['온도'].idxmax()]
    min_temp = week_data.loc[week_data['온도'].idxmin()]

    extreme_temp_table = pd.DataFrame({
        '구분': ['최고 온도', '최저 온도'],
        '온도': [max_temp['온도'], min_temp['온도']],
        '발생일': [max_temp['날짜'].strftime('%m-%d'), min_temp['날짜'].strftime('%m-%d')],
        '모듈번호': [max_temp['모듈번호'], min_temp['모듈번호']]
    })
    st.dataframe(extreme_temp_table)

    # 4. 그래프 옵션 선택
    st.subheader("그래프 옵션")
    option = st.selectbox(
        "보고 싶은 그래프를 선택하세요:",
        ["전체보기", "24시간 평균 온도", "2주 일단위 평균 온도", "2주 일단위 최고 온도"]
    )

    plt.figure(figsize=(10, 6))

    if option == "전체보기":
        last_24_hours = filtered_data[filtered_data['날짜'] >= pd.Timestamp.now() - timedelta(days=1)]
        plt.plot(last_24_hours['hh'], last_24_hours['온도'], marker='o')
        plt.title("최근 24시간 평균 온도 (hh)")
        plt.xlabel("시간 (hh)")
        plt.ylabel("온도 (°C)")
        st.pyplot(plt)

        plt.figure(figsize=(10, 6))
        daily_avg_2weeks = filtered_data.groupby(filtered_data['날짜'].dt.date)['온도'].mean()
        plt.plot(daily_avg_2weeks.index, daily_avg_2weeks.values, marker='o')
        plt.title("2주 일단위 평균 온도")
        plt.xlabel("날짜 (mm-dd)")
        plt.ylabel("온도 (°C)")
        plt.xticks(rotation=45)
        st.pyplot(plt)

        plt.figure(figsize=(10, 6))
        daily_max_2weeks = filtered_data.groupby(filtered_data['날짜'].dt.date)['온도'].max()
        plt.plot(daily_max_2weeks.index, daily_max_2weeks.values, marker='o')
        plt.title("2주 일단위 최고 온도")
        plt.xlabel("날짜 (mm-dd)")
        plt.ylabel("온도 (°C)")
        plt.xticks(rotation=45)
        st.pyplot(plt)

    elif option == "24시간 평균 온도":
        last_24_hours = filtered_data[filtered_data['날짜'] >= pd.Timestamp.now() - timedelta(days=1)]
        plt.plot(last_24_hours['hh'], last_24_hours['온도'], marker='o')
        plt.title("24시간 평균 온도")
        plt.xlabel("시간 (hh)")
        plt.ylabel("온도 (°C)")
        st.pyplot(plt)

    elif option == "2주 일단위 평균 온도":
        daily_avg_2weeks = filtered_data.groupby(filtered_data['날짜'].dt.date)['온도'].mean()
        plt.plot(daily_avg_2weeks.index, daily_avg_2weeks.values, marker='o')
        plt.title("2주 일단위 평균 온도")
        plt.xlabel("날짜 (mm-dd)")
        plt.ylabel("온도 (°C)")
        plt.xticks(rotation=45)
        st.pyplot(plt)

    elif option == "2주 일단위 최고 온도":
        daily_max_2weeks = filtered_data.groupby(filtered_data['날짜'].dt.date)['온도'].max()
        plt.plot(daily_max_2weeks.index, daily_max_2weeks.values, marker='o')
        plt.title("2주 일단위 최고 온도")
        plt.xlabel("날짜 (mm-dd)")
        plt.ylabel("온도 (°C)")
        plt.xticks(rotation=45)
        st.pyplot(plt)
