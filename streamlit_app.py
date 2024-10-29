# 필요한 라이브러리 불러오기
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import ipywidgets as widgets
from IPython.display import display

# 데이터 로드 및 날짜 형식 변환
file_path = "/mnt/data/sqllab_temp_test2.csv"
data = pd.read_csv(file_path)
data['날짜'] = pd.to_datetime(data['날짜'])

# 최근 날짜 계산
latest_date = data['날짜'].max()
recent_data = data[data['날짜'] == latest_date]

# 통합국명 선택 위젯 생성
unique_names = data['통합국명'].unique()
dropdown = widgets.Dropdown(options=unique_names, description='통합국명:')

# 최근 1주일 데이터 필터링
one_week_ago = latest_date - timedelta(days=7)
one_week_data = data[(data['날짜'] >= one_week_ago) & (data['날짜'] <= latest_date)]

def generate_summary(selected_name):
    # 선택된 통합국명 데이터 필터링
    filtered_data = data[data['통합국명'] == selected_name]
    recent_filtered_data = recent_data[recent_data['통합국명'] == selected_name]
    week_filtered_data = one_week_data[one_week_data['통합국명'] == selected_name]

    # 1. 최근 온도의 모듈별 히트맵
    heatmap_data = recent_filtered_data.pivot_table(values='온도', index='모듈번호', columns='hh', aggfunc=np.mean)

    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', fmt=".1f", cbar=True)
    plt.title(f'{selected_name} 모듈별 시간대 평균 온도 히트맵')
    plt.xlabel('시간 (시)')
    plt.ylabel('모듈번호')
    plt.show()

    # 2. 최근 1주일 평균 온도 표
    daily_avg = week_filtered_data.groupby(week_filtered_data['날짜'].dt.date)['온도'].mean()
    overall_avg = week_filtered_data['온도'].mean()
    module_avg = week_filtered_data.groupby('모듈번호')['온도'].mean()

    summary_table = pd.DataFrame({
        '일자': daily_avg.index,
        '일별 평균 온도': daily_avg.values,
        '전체 평균 온도': [overall_avg] * len(daily_avg),
        '모듈별 평균 온도': [module_avg.mean()] * len(daily_avg)
    })

    # 3. 최근 1주일 최고/최저 온도 발생일 및 모듈번호
    max_temp_data = week_filtered_data.loc[week_filtered_data['온도'].idxmax()]
    min_temp_data = week_filtered_data.loc[week_filtered_data['온도'].idxmin()]

    extreme_temp_table = pd.DataFrame({
        '구분': ['최고 온도', '최저 온도'],
        '온도': [max_temp_data['온도'], min_temp_data['온도']],
        '발생일': [max_temp_data['날짜'].date(), min_temp_data['날짜'].date()],
        '모듈번호': [max_temp_data['모듈번호'], min_temp_data['모듈번호']]
    })

    display(summary_table)
    display(extreme_temp_table)

    return filtered_data

# 통합국명 선택 시 실행되는 콜백 함수
def on_select(change):
    selected_name = change['new']
    generate_summary(selected_name)

# 이벤트 리스너 설정
dropdown.observe(on_select, names='value')
display(dropdown)
