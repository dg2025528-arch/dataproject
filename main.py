import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="최고 온도는 점점 올라가고 있는가?",
    layout="wide"
)

st.title("🌡️ 최고 온도는 점점 올라가고 있는가?")
st.write("기상청 기온 데이터를 이용하여 최고기온 상승 추세를 분석합니다.")

# CSV 파일명 (반드시 그대로 사용)
FILE_NAME = "ta_20260601093156 - ta_20260601093156.csv"

try:
    df = pd.read_csv(FILE_NAME, encoding="utf-8")
except:
    try:
        df = pd.read_csv(FILE_NAME, encoding="cp949")
    except Exception as e:
        st.error(f"파일을 읽을 수 없습니다.\n\n{e}")
        st.stop()

# 날짜 변환
df["날짜"] = pd.to_datetime(df["날짜"])

# 연도 추출
df["연도"] = df["날짜"].dt.year

# 최고기온 결측 제거
df = df.dropna(subset=["최고기온(℃)"])

# 연도별 최고기온
yearly = (
    df.groupby("연도")["최고기온(℃)"]
    .max()
    .reset_index()
)

yearly = yearly.sort_values("연도")

x = yearly["연도"].values
y = yearly["최고기온(℃)"].values

# 선형회귀
slope, intercept = np.polyfit(x, y, 1)

# 예측값
trend = slope * x + intercept

# 상관계수
corr = np.corrcoef(x, y)[0, 1]

# 결정계수 R²
ss_res = np.sum((y - trend) ** 2)
ss_tot = np.sum((y - np.mean(y)) ** 2)
r2 = 1 - ss_res / ss_tot

# 이동평균
yearly["10년 이동평균"] = (
    yearly["최고기온(℃)"]
    .rolling(10)
    .mean()
)

yearly["회귀선"] = trend

# 초기/최근 30년 비교
first_avg = yearly.head(30)["최고기온(℃)"].mean()
last_avg = yearly.tail(30)["최고기온(℃)"].mean()

difference = last_avg - first_avg

st.header("📊 통계 결과")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "상승 기울기",
    f"{slope:.4f} ℃/년"
)

c2.metric(
    "상관계수",
    f"{corr:.3f}"
)

c3.metric(
    "결정계수(R²)",
    f"{r2:.3f}"
)

c4.metric(
    "30년 평균 변화",
    f"{difference:.2f} ℃"
)

st.header("📈 연도별 최고기온")

chart1 = yearly.set_index("연도")[["최고기온(℃)"]]
st.line_chart(chart1)

st.header("📈 최고기온 + 10년 이동평균")

chart2 = yearly.set_index("연도")[
    ["최고기온(℃)", "10년 이동평균"]
]

st.line_chart(chart2)

st.header("📈 최고기온 + 회귀선")

chart3 = yearly.set_index("연도")[
    ["최고기온(℃)", "회귀선"]
]

st.line_chart(chart3)

st.header("🔍 결론")

if slope > 0:
    st.success(
        f"""
        최고기온은 장기적으로 상승하는 추세를 보입니다.

        • 상승 속도 : {slope:.4f} ℃/년

        • 상관계수 : {corr:.3f}

        • 최근 30년 평균이 과거 30년 평균보다
          {difference:.2f} ℃ 높습니다.
        """
    )
else:
    st.warning(
        "명확한 상승 추세가 확인되지 않았습니다."
    )

st.header("📝 탐구 보고서용 결론")

st.write(f"""
서울 기온 관측 자료를 이용하여 연도별 최고기온을 분석하였다.

분석 결과 최고기온의 선형회귀 기울기는
{slope:.4f} ℃/년으로 나타났다.

상관계수는 {corr:.3f},
결정계수는 {r2:.3f}로 계산되었다.

또한 최근 30년 평균 최고기온은
과거 30년 평균보다 {difference:.2f} ℃ 높게 나타났다.

따라서 본 자료는 최고기온이 장기적으로 상승하고 있다는 가설을 지지한다.
""")

with st.expander("연도별 데이터 보기"):
    st.dataframe(yearly, use_container_width=True)
