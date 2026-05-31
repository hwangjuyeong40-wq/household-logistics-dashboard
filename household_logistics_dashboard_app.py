import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Household Goods Logistics Insight",
    page_icon="📦",
    layout="wide",
)

SENTIMENT_ORDER = ["긍정", "중립", "부정"]
ITEM_ORDER = ["세제", "액체류", "주방용품", "생활잡화"]

@st.cache_data
def load_data():
    # 파일명이 실제 파일과 일치하도록 수정되었습니다.
    df = pd.read_csv("household_logistics_reviews_600.csv")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    return df

def calculate_satisfaction(data):
    if len(data) == 0:
        return 0.0

    positive = (data["sentiment"] == "긍정").sum()
    neutral = (data["sentiment"] == "중립").sum()
    return round(((positive + neutral * 0.5) / len(data)) * 100, 2)

# 데이터 로드
df = load_data()

st.title("Household Goods Logistics Insight")
st.caption("한·중 생활용품 배송·포장 이슈 분석 대시보드")

metric_cols = st.columns(5)
metric_cols[0].metric("전체 리뷰 수", f"{len(df):,}")
metric_cols[1].metric("한국어 리뷰 수", f"{(df['language'] == 'ko').sum():,}")
metric_cols[2].metric("중국어 리뷰 수", f"{(df['language'] == 'zh').sum():,}")
metric_cols[3].metric("품목 수", f"{df['item_type'].nunique():,}")
metric_cols[4].metric("중국어 제품 수", f"{df.loc[df['language'] == 'zh', 'product'].nunique():,}")

st.info(
    "한국어 데이터는 네이버 API 기반 실제 검색 결과 데이터이며, "
    "중국어 데이터는 샤오홍슈 리뷰 형식을 참고한 구조화 생성 데이터입니다. "
    "두 데이터의 성격을 구분하여 해석해야 합니다."
)

st.divider()

st.subheader("데이터 구성")
col1, col2 = st.columns(2)

language_counts = (
    df["language_label"]
    .value_counts()
    .reindex(["한국어", "중국어"])
    .fillna(0)
    .reset_index()
)
language_counts.columns = ["언어", "리뷰 수"]

fig_language = px.bar(
    language_counts,
    x="언어",
    y="리뷰 수",
    color="언어",
    text="리뷰 수",
    color_discrete_map={"한국어": "#2F80ED", "중국어": "#EB5757"},
)
fig_language.update_layout(showlegend=False)
fig_language.update_traces(textposition="outside")
col1.plotly_chart(fig_language, use_container_width=True)

item_counts = (
    df.groupby(["item_type", "language_label"])
    .size()
    .reset_index(name="리뷰 수")
)
fig_item = px.bar(
    item_counts,
    x="item_type",
    y="리뷰 수",
    color="language_label",
    barmode="group",
    text="리뷰 수",
    category_orders={"item_type": ITEM_ORDER, "language_label": ["한국어", "중국어"]},
    labels={"item_type": "품목", "language_label": "언어"},
    color_discrete_map={"한국어": "#2F80ED", "중국어": "#EB5757"},
)
fig_item.update_traces(textposition="outside")
col2.plotly_chart(fig_item, use_container_width=True)

st.subheader("한·중 감성 비교")
sentiment_lang = (
    pd.crosstab(df["language_label"], df["sentiment"])
    .reindex(index=["한국어", "중국어"], fill_value=0)
    .reindex(columns=SENTIMENT_ORDER, fill_value=0)
    .reset_index()
    .melt(id_vars="language_label", var_name="감성", value_name="리뷰 수")
)

fig_sentiment_lang = px.bar(
    sentiment_lang,
    x="language_label",
    y="리뷰 수",
    color="감성",
    barmode="group",
    text="리뷰 수",
    category_orders={"감성": SENTIMENT_ORDER, "language_label": ["한국어", "중국어"]},
    color_discrete_map={"긍정": "#27AE60", "중립": "#F2C94C", "부정": "#EB5757"},
    labels={"language_label": "언어"},
)
fig_sentiment_lang.update_traces(textposition="outside")
st.plotly_chart(fig_sentiment_lang, use_container_width=True)

st.subheader("물류 이슈 분석")
issue_cols = st.columns(2)

issue_counts = df["logistics_issue"].value_counts().reset_index()
issue_counts.columns = ["물류 이슈", "리뷰 수"]
fig_issue = px.bar(
    issue_counts,
    x="물류 이슈",
    y="리뷰 수",
    color="물류 이슈",
    text="리뷰 수",
    title="전체 물류 이슈 분포",
)
fig_issue.update_layout(showlegend=False)
fig_issue.update_traces(textposition="outside")
issue_cols[0].plotly_chart(fig_issue, use_container_width=True)

issue_item = (
    df.groupby(["item_type", "logistics_issue"])
    .size()
    .reset_index(name="리뷰 수")
)
fig_issue_item = px.bar(
    issue_item,
    x="item_type",
    y="리뷰 수",
    color="logistics_issue",
    barmode="stack",
    category_orders={"item_type": ITEM_ORDER},
    title="품목별 물류 이슈 분포",
    labels={"item_type": "품목", "logistics_issue": "물류 이슈"},
)
issue_cols[1].plotly_chart(fig_issue_item, use_container_width=True)

st.subheader("감성 기반 만족도")
st.info(
    "만족도는 긍정 리뷰를 1점, 중립 리뷰를 0.5점, 부정 리뷰를 0점으로 환산한 감성 기반 지표입니다. "
    "계산식: (긍정 리뷰 수 + 중립 리뷰 수 × 0.5) ÷ 전체 리뷰 수 × 100"
)

satisfaction_rows = []
for (language_label, item_type), group in df.groupby(["language_label", "item_type"]):
    satisfaction_rows.append(
        {
            "언어": language_label,
            "품목": item_type,
            "리뷰 수": len(group),
            "만족도": calculate_satisfaction(group),
            "주요 이슈": group["logistics_issue"].value_counts().index[0],
        }
    )

satisfaction_df = pd.DataFrame(satisfaction_rows)

sat_cols = st.columns([2, 1])
fig_satisfaction = px.bar(
    satisfaction_df,
    x="품목",
    y="만족도",
    color="언어",
    barmode="group",
    text="만족도",
    category_orders={"품목": ITEM_ORDER, "언어": ["한국어", "중국어"]},
    color_discrete_map={"한국어": "#2F80ED", "중국어": "#EB5757"},
    labels={"만족도": "만족도(%)"},
)
fig_satisfaction.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
sat_cols[0].plotly_chart(fig_satisfaction, use_container_width=True)
sat_cols[1].dataframe(satisfaction_df.sort_values(["언어", "품목"]), use_container_width=True, hide_index=True)

st.subheader("품목별 리스크 요약")
risk_summary = (
    df.groupby(["language_label", "item_type"])["logistics_issue"]
    .agg(lambda x: x.value_counts().index[0])
    .reset_index()
)
risk_summary.columns = ["언어", "품목", "주요 물류 이슈"]
st.dataframe(risk_summary, use_container_width=True, hide_index=True)

st.divider()
st.subheader("리뷰 검색")

filter_cols = st.columns(5)
selected_language = filter_cols[0].selectbox("언어", ["전체"] + ["한국어", "중국어"])
selected_item = filter_cols[1].selectbox("품목", ["전체"] + ITEM_ORDER)
selected_issue = filter_cols[2].selectbox("물류 이슈", ["전체"] + sorted(df["logistics_issue"].dropna().unique().tolist()))
selected_sentiment = filter_cols[3].selectbox("감성", ["전체"] + SENTIMENT_ORDER)
keyword = filter_cols[4].text_input("키워드", placeholder="예: 누수, 包装, 배송")

filtered_df = df.copy()

if selected_language != "전체":
    filtered_df = filtered_df[filtered_df["language_label"] == selected_language]
if selected_item != "전체":
    filtered_df = filtered_df[filtered_df["item_type"] == selected_item]
if selected_issue != "전체":
    filtered_df = filtered_df[filtered_df["logistics_issue"] == selected_issue]
if selected_sentiment != "전체":
    filtered_df = filtered_df[filtered_df["sentiment"] == selected_sentiment]
if keyword.strip():
    filtered_df = filtered_df[filtered_df["review"].str.contains(keyword.strip(), case=False, na=False)]

st.dataframe(
    filtered_df[
        [
            "id",
            "language_label",
            "platform",
            "data_type",
            "item_type",
            "product_display",
            "review",
            "sentiment",
            "logistics_issue",
            "rating",
            "packaging_quality",
            "delivery_speed",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.subheader("원본 데이터 조회")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("활용 가능성")
roadmap_cols = st.columns(4)
roadmap_cols[0].success("물류 이슈 사전 구축")
roadmap_cols[1].success("품목별 포장 리스크 분석")
roadmap_cols[2].success("다국어 리뷰 라벨링 실습")
roadmap_cols[3].success("SCM 품질 모니터링 확장")