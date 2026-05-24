import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 페이지 설정

st.set_page_config(
page_title="K-뷰티 리뷰 분석",
layout="wide"
)

# 제목

st.title("💄 K-뷰티 한·중 리뷰 분석 대시보드")

# 엑셀 파일 불러오기

df = pd.read_excel(
r"C:\Users\why\Desktop\dash board\data_726.xlsx"
)


# 컬럼명 정리

df.columns = [
str(col).lower()
for col in df.columns
]

# 데이터 미리보기

st.subheader("📌 데이터 미리보기")

st.dataframe(
df.head(),
width="stretch"
)

# 총 리뷰 수

st.subheader("📊 총 리뷰 수")

st.metric(
label="리뷰 개수",
value=len(df)
)

# 플랫폼별 리뷰 개수

st.subheader("📈 플랫폼별 리뷰 개수")

platform_df = (
df["platform"]
.value_counts()
.reset_index()
)

platform_df.columns = [
"플랫폼",
"리뷰 수"
]

fig = px.bar(
platform_df,
x="플랫폼",
y="리뷰 수",
text="리뷰 수"
)

st.plotly_chart(
fig,
width="stretch"
)

# 감성 분포

st.subheader("😊 감성 분포")

sentiment_df = (
df["sentiment"]
.value_counts()
.reset_index()
)

sentiment_df.columns = [
"감성",
"개수"
]

fig2 = px.pie(
sentiment_df,
names="감성",
values="개수"
)

st.plotly_chart(
fig2,
width="stretch"
)

# 워드클라우드

st.subheader("☁️ 워드클라우드")

text = " ".join(
df["review"]
.astype(str)
)

wordcloud = WordCloud(
font_path="C:/Windows/Fonts/malgun.ttf",
width=1000,
height=500,
background_color="white"
).generate(text)

fig3, ax = plt.subplots(
figsize=(12, 6)
)

ax.imshow(
wordcloud,
interpolation="bilinear"
)

ax.axis("off")

# st.pyplot(fig3)

# 리뷰 검색

st.subheader("🔍 리뷰 검색")

keyword = st.text_input(
"검색어 입력"
)

result = df[
df["review"]
.astype(str)
.str.contains(keyword, na=False)
]

st.write(
f"검색 결과: {len(result)}건"
)

st.dataframe(
result,
width="stretch"
)

# 결론

st.subheader("📌 프로젝트 결론")

st.write("""
한·중 소비자 리뷰 데이터를 분석한 결과,
배송·통관·정품 여부 같은 구매 경험 요소가
소비자 만족도에 영향을 미치는 것으로 나타났다.
""")

