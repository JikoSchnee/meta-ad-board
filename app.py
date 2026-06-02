from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Meta Ads 数据分析看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


DATE_COL = "报告开始日期"
SPEND_COL = "已花费金额 (USD)"
IMPRESSIONS_COL = "展示次数"
REACH_COL = "覆盖人数"
CPM_COL = "CPM（千次展示费用） (USD)"
CTR_ALL_COL = "点击率（全部）"
ALL_CLICKS_COL = "点击量"
CLICKS_COL = "链接点击量"
LANDING_PAGE_VIEWS_COL = "落地页浏览量"
VIDEO_PLAYS_COL = "视频播放量"
VIDEO_3S_RATE_COL = "单次展示的播放视频达3秒率"
VIDEO_AVG_PLAY_TIME_COL = "视频平均播放时长"
ATC_COL = "加入购物车次数"
CHECKOUT_COL = "结账发起次数"
PURCHASES_COL = "成效"
ROAS_COL = "广告花费回报 (ROAS) - 购物"

NON_NUMERIC_COMPARE_COLUMNS = {
    DATE_COL,
    "报告结束日期",
    "广告名称",
    "广告投放",
    "广告组预算类型",
    "归因设置",
    "成效指标",
    "成效值指标",
    "Campaign name",
    "Ad set name",
    "Ad name",
}


CANONICAL_COLUMNS = {
    DATE_COL: ["报告开始日期", "开始报告日期", "开始日期", "日期", "Date", "Day"],
    SPEND_COL: ["已花费金额 (USD)", "花费", "支出", "Amount spent (USD)", "Amount spent"],
    IMPRESSIONS_COL: ["展示次数", "Impressions"],
    REACH_COL: ["覆盖人数", "覆盖", "Reach"],
    CPM_COL: ["CPM（千次展示费用） (USD)", "CPM (USD)", "CPM"],
    CTR_ALL_COL: ["点击率（全部）", "CTR (All)", "CTR"],
    ALL_CLICKS_COL: ["点击量", "点击次数", "全部点击量", "Clicks (all)", "Clicks"],
    CLICKS_COL: ["链接点击量", "链接点击", "Link clicks"],
    LANDING_PAGE_VIEWS_COL: [
        "落地页浏览量",
        "落地页浏览",
        "落地页查看量",
        "Landing page views",
        "Landing Page Views",
    ],
    VIDEO_PLAYS_COL: ["视频播放量", "视频播放次数", "Video plays", "Video plays at 100%"],
    VIDEO_3S_RATE_COL: [
        "单次展示的播放视频达3秒率",
        "单次展示的播放视频达 3 秒率",
        "播放视频达3秒率",
        "播放视频达 3 秒率",
        "3秒视频播放率",
        "3-second video plays per impression",
        "3-second video play rate",
    ],
    VIDEO_AVG_PLAY_TIME_COL: [
        "视频平均播放时长",
        "平均视频播放时长",
        "Video average play time",
        "Average video play time",
    ],
    ATC_COL: ["加入购物车次数", "加入购物车", "Adds to cart", "Add to cart"],
    CHECKOUT_COL: ["结账发起次数", "发起结账", "Checkouts initiated", "Initiate checkout"],
    PURCHASES_COL: ["成效", "购买", "购物次数", "Purchases", "Results"],
    ROAS_COL: ["广告花费回报 (ROAS) - 购物", "购物 ROAS", "Purchase ROAS", "ROAS"],
}


NUMERIC_COLUMNS = [
    SPEND_COL,
    IMPRESSIONS_COL,
    REACH_COL,
    CPM_COL,
    CTR_ALL_COL,
    ALL_CLICKS_COL,
    CLICKS_COL,
    LANDING_PAGE_VIEWS_COL,
    VIDEO_PLAYS_COL,
    VIDEO_3S_RATE_COL,
    VIDEO_AVG_PLAY_TIME_COL,
    ATC_COL,
    CHECKOUT_COL,
    PURCHASES_COL,
    ROAS_COL,
]


DIMENSION_CANDIDATES = ["广告系列名称", "广告组名称", "广告名称", "Campaign name", "Ad set name", "Ad name"]

VIDEO_SOURCE_COLUMNS = [VIDEO_PLAYS_COL, VIDEO_3S_RATE_COL, VIDEO_AVG_PLAY_TIME_COL]

DERIVED_COMPARE_COLUMNS = {
    "整体CTR (%)",
    "CPC (USD)",
    "CPM (USD)",
    "CVR 点击到购买 (%)",
    "CPA 购买成本 (USD)",
}


GLOSSARY = {
    "CTR": ("点击率", "Click-Through Rate"),
    "CPC": ("单次点击成本", "Cost Per Click"),
    "CPM": ("千次展示费用", "Cost Per Mille"),
    "CPA": ("单次购买/转化成本", "Cost Per Acquisition"),
    "CVR": ("转化率", "Conversion Rate"),
    "ROAS": ("广告花费回报率", "Return On Ad Spend"),
    "KPI": ("核心绩效指标", "Key Performance Indicator"),
}


FUNNEL_STAGE_OPTIONS = [
    ("点击量", ALL_CLICKS_COL),
    ("落地页浏览量", LANDING_PAGE_VIEWS_COL),
    ("加购次数", ATC_COL),
    ("发起结账次数", CHECKOUT_COL),
    ("购买次数", PURCHASES_COL),
]


@dataclass(frozen=True)
class HealthBand:
    label: str
    color: str


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --meta-primary: #0064e0;
            --meta-primary-deep: #0457cb;
            --meta-canvas: #ffffff;
            --meta-soft: #f1f4f7;
            --meta-ink-deep: #0a1317;
            --meta-ink: #1c1e21;
            --meta-charcoal: #444950;
            --meta-steel: #5d6c7b;
            --meta-stone: #8595a4;
            --meta-hairline: #ced0d4;
            --meta-hairline-soft: #dee3e9;
            --meta-success: #31a24c;
            --meta-warning: #f2a918;
            --meta-critical: #e41e3f;
            --ink: var(--meta-ink-deep);
            --muted: var(--meta-steel);
            --paper: var(--meta-soft);
            --panel: var(--meta-canvas);
            --line: var(--meta-hairline-soft);
            --green: var(--meta-success);
            --amber: var(--meta-warning);
            --red: var(--meta-critical);
            --blue: var(--meta-primary);
        }

        .stApp {
            background: var(--meta-soft);
            color: var(--ink);
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--meta-ink-deep);
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
        }

        [data-testid="stSidebar"] {
            background: var(--meta-canvas);
            color: var(--meta-ink);
            border-right: 1px solid var(--meta-hairline-soft);
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: var(--meta-ink);
        }

        .stButton button,
        .stDownloadButton button,
        [data-testid="stBaseButton-secondary"] {
            border-radius: 100px !important;
            border: 1px solid rgba(10, 19, 23, 0.12) !important;
            font-weight: 700 !important;
        }

        .stFileUploader,
        [data-testid="stFileUploader"],
        [data-testid="stExpander"],
        [data-testid="stDataFrame"],
        .stAlert {
            border-radius: 24px;
        }

        [data-testid="stTabs"] button {
            border-radius: 100px !important;
            font-weight: 700;
        }

        [data-testid="stTabs"] [aria-selected="true"] {
            color: var(--meta-primary) !important;
        }

        .hero {
            border: 1px solid var(--meta-hairline-soft);
            background: var(--meta-canvas);
            border-radius: 24px;
            padding: 20px 24px;
            margin-bottom: 14px;
        }

        .hero-title {
            font-size: 36px;
            font-weight: 500;
            line-height: 1.17;
            margin: 0 0 6px 0;
            color: var(--meta-ink-deep);
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
        }

        .hero-copy {
            max-width: 920px;
            font-size: 14px;
            line-height: 1.42;
            color: var(--meta-steel);
            margin: 0;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin: 12px 0 18px 0;
        }

        .kpi {
            min-height: 122px;
            border: 1px solid var(--meta-hairline-soft);
            background: var(--panel);
            border-radius: 24px;
            padding: 24px;
        }

        .kpi-label {
            color: var(--meta-steel);
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 12px;
        }

        .kpi-value {
            color: var(--meta-ink-deep);
            font-size: 32px;
            font-weight: 500;
            line-height: 1.1;
        }

        .kpi-note {
            color: var(--muted);
            font-size: 12px;
            margin-top: 10px;
        }

        .section-title {
            color: var(--meta-ink-deep);
            font-size: 22px;
            font-weight: 500;
            line-height: 1.25;
            margin: 16px 0 8px 0;
        }

        [data-testid="stWidgetLabel"] {
            margin-bottom: 3px;
        }

        [data-testid="stWidgetLabel"] label,
        [data-testid="stWidgetLabel"] p {
            font-size: 12px;
            font-weight: 700;
            color: var(--meta-charcoal);
            line-height: 1.2;
        }

        [data-testid="stFileUploader"] {
            padding: 8px 10px;
            border: 1px solid var(--meta-hairline-soft);
            background: var(--meta-canvas);
        }

        [data-testid="stFileUploader"] section {
            padding: 8px 10px;
            min-height: 52px;
        }

        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] span,
        [data-testid="stFileUploader"] p {
            font-size: 12px;
            line-height: 1.25;
        }

        [data-testid="stAlert"] {
            padding: 8px 12px;
            margin: 6px 0;
            border-radius: 16px;
        }

        [data-testid="stAlert"] div {
            font-size: 13px;
            line-height: 1.35;
        }

        [data-testid="stExpander"] {
            border-radius: 16px;
            border-color: var(--meta-hairline-soft);
            margin: 6px 0 10px 0;
        }

        [data-testid="stExpander"] details > summary {
            min-height: 36px;
            padding: 6px 12px;
        }

        [data-testid="stNumberInput"] input,
        [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] div,
        [data-testid="stMultiSelect"] div {
            min-height: 34px;
            font-size: 13px;
        }

        [data-testid="stNumberInput"] input,
        [data-testid="stTextInput"] input,
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div {
            background: #f7f9fb !important;
            border-color: var(--meta-hairline) !important;
            color: var(--meta-ink-deep) !important;
            box-shadow: inset 0 0 0 1px rgba(10, 19, 23, 0.03);
        }

        [data-testid="stNumberInput"] input,
        [data-testid="stTextInput"] input,
        [data-baseweb="select"] span,
        [data-baseweb="select"] input,
        [data-baseweb="select"] div,
        [data-baseweb="input"] input {
            color: var(--meta-ink-deep) !important;
            -webkit-text-fill-color: var(--meta-ink-deep) !important;
        }

        [data-baseweb="select"] svg,
        [data-baseweb="input"] svg {
            color: var(--meta-charcoal) !important;
            fill: var(--meta-charcoal) !important;
        }

        [data-testid="stMultiSelect"] [data-baseweb="tag"] {
            margin: 2px;
            height: 24px;
            border-radius: 100px;
            background: #e8f1ff;
            border: 1px solid rgba(0, 100, 224, 0.18);
            color: var(--meta-primary-deep) !important;
        }

        [data-testid="stMultiSelect"] [data-baseweb="tag"] span {
            color: var(--meta-primary-deep) !important;
            -webkit-text-fill-color: var(--meta-primary-deep) !important;
            font-weight: 700;
        }

        [data-testid="stCheckbox"] {
            margin-top: 18px;
        }

        [data-testid="stCheckbox"] label {
            min-height: 34px;
            padding: 5px 10px;
            border: 1px solid var(--meta-hairline-soft);
            border-radius: 100px;
            background: var(--meta-canvas);
        }

        [data-testid="stHorizontalBlock"] {
            gap: 10px;
        }

        .abbr {
            position: relative;
            display: inline-flex;
            align-items: center;
            border-bottom: 1px dotted rgba(24, 32, 42, 0.55);
            cursor: help;
            color: inherit;
            overflow: visible;
        }

        .abbr::after {
            content: attr(data-tooltip);
            position: absolute;
            left: 50%;
            bottom: calc(100% + 8px);
            transform: translateX(-50%);
            min-width: 188px;
            max-width: 260px;
            padding: 9px 10px;
            background: #1f252c;
            color: #ffffff;
            border: 1px solid rgba(255, 254, 250, 0.16);
            font-size: 12px;
            font-weight: 560;
            line-height: 1.35;
            text-align: center;
            white-space: normal;
            opacity: 0;
            pointer-events: none;
            z-index: 50;
            transition: opacity 120ms ease, transform 120ms ease;
        }

        .abbr::before {
            content: "";
            position: absolute;
            left: 50%;
            bottom: calc(100% + 3px);
            transform: translateX(-50%);
            border: 5px solid transparent;
            border-top-color: #1f252c;
            opacity: 0;
            pointer-events: none;
            z-index: 51;
            transition: opacity 120ms ease;
        }

        .abbr:hover::after,
        .abbr:hover::before {
            opacity: 1;
        }

        .abbr:hover::after {
            transform: translateX(-50%) translateY(-2px);
        }

        .suggestion {
            border-left: 5px solid var(--blue);
            background: var(--panel);
            padding: 14px 16px;
            margin: 10px 0;
            border-top: 1px solid var(--line);
            border-right: 1px solid var(--line);
            border-bottom: 1px solid var(--line);
        }

        .suggestion.warn {
            border-left-color: var(--amber);
        }

        .suggestion.bad {
            border-left-color: var(--red);
        }

        .suggestion.good {
            border-left-color: var(--green);
        }

        .suggestion-title {
            font-weight: 720;
            margin-bottom: 4px;
        }

        .suggestion-body {
            color: var(--muted);
            line-height: 1.55;
        }

        .funnel-metrics {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
            margin: 0;
        }

        .funnel-metric {
            border: 1px solid #e0e0e0;
            background: #ffffff;
            border-radius: 18px;
            padding: 18px;
            min-height: 118px;
        }

        .funnel-label {
            color: #6e6e73;
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            font-size: 14px;
            font-weight: 400;
            line-height: 1.35;
            letter-spacing: -0.224px;
            margin-bottom: 10px;
        }

        .funnel-value {
            color: var(--meta-ink-deep);
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            font-size: 34px;
            font-weight: 600;
            line-height: 1.12;
            letter-spacing: -0.374px;
        }

        .funnel-rate {
            color: #6e6e73;
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            font-size: 12px;
            font-weight: 400;
            margin-top: 10px;
            line-height: 1.42;
            letter-spacing: -0.12px;
        }

        .apple-funnel-stage {
            display: inline-flex;
            align-items: center;
            min-height: 28px;
            padding: 5px 12px;
            border-radius: 9999px;
            background: var(--meta-canvas);
            color: var(--meta-ink-deep);
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            border: 1px solid var(--meta-hairline);
            font-size: 13px;
            font-weight: 400;
            letter-spacing: -0.12px;
            margin-bottom: 12px;
        }

        .apple-funnel-panel {
            background: var(--meta-canvas);
            border-radius: 32px;
            padding: 32px;
            border: 1px solid var(--meta-hairline-soft);
        }

        .apple-funnel-title {
            color: var(--meta-ink-deep);
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            font-size: 28px;
            font-weight: 500;
            line-height: 1.15;
            letter-spacing: -0.28px;
            margin: 0 0 4px 0;
        }

        .apple-funnel-copy {
            color: #6e6e73;
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            font-size: 14px;
            font-weight: 400;
            line-height: 1.45;
            letter-spacing: -0.224px;
            margin: 0 0 16px 0;
        }

        .apple-rate-title {
            color: var(--meta-ink-deep);
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            font-size: 24px;
            font-weight: 600;
            line-height: 1.15;
            letter-spacing: -0.28px;
            margin: 0 0 12px 0;
        }

        .apple-rate-bar {
            width: 100%;
            height: 6px;
            border-radius: 9999px;
            background: #e8e8ed;
            overflow: hidden;
            margin-top: 14px;
        }

        .apple-rate-fill {
            display: block;
            height: 100%;
            border-radius: 9999px;
            background: var(--meta-primary);
        }

        .flow-funnel {
            display: flex;
            flex-direction: column;
            gap: 0;
            margin-top: 18px;
        }

        .flow-stage {
            display: grid;
            grid-template-columns: minmax(110px, 150px) 1fr minmax(92px, auto);
            gap: 14px;
            align-items: center;
            padding: 12px 0;
        }

        .flow-stage-name {
            color: var(--meta-ink-deep);
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            font-size: 14px;
            font-weight: 600;
            line-height: 1.25;
            letter-spacing: -0.224px;
        }

        .flow-track {
            height: 42px;
            border-radius: 9999px;
            background: #e8e8ed;
            overflow: hidden;
        }

        .flow-fill {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            height: 100%;
            min-width: 38px;
            border-radius: 9999px;
            background: var(--meta-primary);
            color: #ffffff;
            padding-right: 14px;
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: -0.12px;
        }

        .flow-value {
            color: var(--meta-ink-deep);
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            font-size: 24px;
            font-weight: 600;
            line-height: 1.1;
            letter-spacing: -0.28px;
            text-align: right;
        }

        .flow-connector {
            display: grid;
            grid-template-columns: minmax(110px, 150px) 1fr minmax(92px, auto);
            gap: 14px;
            align-items: center;
            min-height: 34px;
        }

        .flow-connector-line {
            position: relative;
            height: 1px;
            background: #d2d2d7;
        }

        .flow-connector-rate {
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            border-radius: 9999px;
            border: 1px solid #d2d2d7;
            background: #ffffff;
            color: var(--meta-primary);
            padding: 5px 11px;
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: -0.12px;
            white-space: nowrap;
        }

        .flow-connector-caption {
            color: #6e6e73;
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            font-size: 12px;
            letter-spacing: -0.12px;
            text-align: right;
        }

        .compare-style-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 10px 0 14px 0;
            overflow: hidden;
            border: 1px solid #e0e0e0;
            border-radius: 18px;
            background: #ffffff;
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
        }

        .compare-style-table th,
        .compare-style-table td {
            border-bottom: 1px solid #f0f0f0;
            border-right: 1px solid #f0f0f0;
            padding: 10px 12px;
            color: var(--meta-ink-deep);
            font-size: 12px;
            letter-spacing: -0.12px;
            vertical-align: middle;
        }

        .compare-style-table th {
            background: var(--meta-soft);
            color: #6e6e73;
            font-weight: 600;
        }

        .compare-style-table tr:last-child td {
            border-bottom: 0;
        }

        .compare-style-table th:last-child,
        .compare-style-table td:last-child {
            border-right: 0;
        }

        .style-swatch {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            white-space: nowrap;
        }

        .style-line {
            width: 34px;
            height: 0;
            border-top-width: 3px;
            border-top-style: solid;
            display: inline-block;
        }

        .style-marker {
            width: 10px;
            height: 10px;
            display: inline-block;
            background: currentColor;
        }

        .style-marker.circle {
            border-radius: 50%;
        }

        .style-marker.square {
            border-radius: 2px;
        }

        .style-marker.diamond {
            transform: rotate(45deg);
            border-radius: 2px;
        }

        .style-marker.triangle-up {
            width: 0;
            height: 0;
            background: transparent;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-bottom: 11px solid currentColor;
        }

        [data-testid="stRadio"] {
            margin: 4px 0 18px 0;
        }

        [data-testid="stRadio"] > div {
            gap: 8px;
        }

        [data-testid="stRadio"] label {
            min-height: 36px;
            padding: 8px 14px;
            border: 1px solid #e0e0e0;
            border-radius: 9999px;
            background: #ffffff;
            color: #1d1d1f;
            font-family: "Optimistic VF", Montserrat, Helvetica, Arial, "Noto Sans", sans-serif;
            font-size: 14px;
            letter-spacing: -0.224px;
        }

        [data-testid="stRadio"] label:has(input:checked) {
            border-color: var(--meta-primary);
            color: var(--meta-primary);
            background: #f5f9ff;
        }

        @media (max-width: 980px) {
            .kpi-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .funnel-metrics {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 560px) {
            .hero-title {
                font-size: 26px;
            }

            .kpi-grid {
                grid-template-columns: 1fr;
            }

            .funnel-metrics {
                grid-template-columns: 1fr;
            }

            .flow-stage,
            .flow-connector {
                grid-template-columns: 1fr;
                gap: 8px;
            }

            .flow-value,
            .flow-connector-caption {
                text-align: left;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">Meta Ads 自动化数据分析看板</div>
            <p class="hero-copy">
                上传 Meta Ads Manager 导出的 CSV 或 Excel 文件，系统会自动清洗中文列名、生成趋势图、转化漏斗、广告层级排行，并给出可执行的投放诊断建议。
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def glossary_term(abbr: str) -> str:
    chinese, english = GLOSSARY[abbr]
    tooltip = f"{chinese} / {english}"
    return f'<span class="abbr" title="{tooltip}" data-tooltip="{tooltip}">{abbr}</span>'


def render_section_title(title_html: str) -> None:
    st.markdown(f'<div class="section-title">{title_html}</div>', unsafe_allow_html=True)


def normalize_label(label: object) -> str:
    return str(label).strip().replace("\n", " ").replace("\u3000", " ")


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized_to_original = {normalize_label(col): col for col in df.columns}
    rename_map = {}

    for canonical, aliases in CANONICAL_COLUMNS.items():
        if canonical in df.columns:
            continue

        for alias in aliases:
            if alias in normalized_to_original:
                rename_map[normalized_to_original[alias]] = canonical
                break

    return df.rename(columns=rename_map)


def parse_duration_seconds(value: object) -> float | None:
    text = str(value).strip()
    if ":" not in text:
        return None

    parts = text.split(":")
    if not 2 <= len(parts) <= 3:
        return None

    try:
        numbers = [float(part) for part in parts]
    except ValueError:
        return None

    if len(numbers) == 2:
        minutes, seconds = numbers
        return minutes * 60 + seconds

    hours, minutes, seconds = numbers
    return hours * 3600 + minutes * 60 + seconds


def clean_numeric(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace("--", "", regex=False)
        .str.replace("—", "", regex=False)
        .str.replace("N/A", "", regex=False)
    )
    numeric = pd.to_numeric(cleaned, errors="coerce").astype("float64")
    duration_values = pd.to_numeric(series.map(parse_duration_seconds), errors="coerce").astype("float64")
    numeric.loc[numeric.isna()] = duration_values.loc[numeric.isna()]
    return numeric.fillna(0)


def discover_numeric_columns(df: pd.DataFrame) -> list[str]:
    numeric_columns = []
    for col in df.columns:
        if col in NON_NUMERIC_COMPARE_COLUMNS:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_columns.append(col)
            continue

        cleaned = clean_numeric(df[col])
        non_empty = df[col].notna() & df[col].astype(str).str.strip().ne("")
        if non_empty.any() and cleaned[non_empty].notna().any():
            if cleaned[non_empty].abs().sum() > 0:
                numeric_columns.append(col)
    return numeric_columns


def ensure_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    for col in columns:
        if col not in df.columns:
            df[col] = 0
    return df


def parse_uploaded_file(uploaded_file) -> pd.DataFrame:
    if uploaded_file.name.lower().endswith(".csv"):
        try:
            return pd.read_csv(uploaded_file, encoding="utf-8-sig")
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding="gb18030")

    return pd.read_excel(uploaded_file)


def parse_uploaded_files(uploaded_files: list) -> pd.DataFrame:
    frames = []
    for uploaded_file in uploaded_files:
        frame = parse_uploaded_file(uploaded_file)
        frame["_来源文件"] = uploaded_file.name
        frames.append(frame)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True, sort=False)


def preprocess(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    df.columns = [normalize_label(col) for col in df.columns]
    df = rename_columns(df)
    has_all_clicks_col = ALL_CLICKS_COL in df.columns
    present_columns = set(df.columns)
    discovered_numeric_columns = discover_numeric_columns(df)

    if DATE_COL not in df.columns:
        raise ValueError(f"未找到日期列。请确认文件里包含“{DATE_COL}”或“日期”。")

    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    df = df[df[DATE_COL].notna()].copy()
    if df.empty:
        raise ValueError("日期列无法解析，清洗后没有可用数据。")

    compare_numeric_columns = list(dict.fromkeys(NUMERIC_COLUMNS + discovered_numeric_columns))
    df = ensure_columns(df, compare_numeric_columns)
    for col in compare_numeric_columns:
        df[col] = clean_numeric(df[col])

    if (not has_all_clicks_col or df[ALL_CLICKS_COL].sum() == 0) and df[CLICKS_COL].sum() > 0:
        df[ALL_CLICKS_COL] = df[CLICKS_COL]

    df = df.sort_values(DATE_COL).reset_index(drop=True)
    df.attrs["present_columns"] = present_columns
    df.attrs["compare_numeric_columns"] = [
        col for col in compare_numeric_columns if col in present_columns
    ]
    return df


def weighted_average(values: pd.Series, weights: pd.Series) -> float:
    value_sum = (values * weights).sum()
    weight_sum = weights.sum()
    if weight_sum == 0:
        return 0.0
    return float(value_sum / weight_sum)


def build_daily_df(df: pd.DataFrame) -> pd.DataFrame:
    compare_numeric_columns = df.attrs.get("compare_numeric_columns", NUMERIC_COLUMNS)
    roas_source = df.assign(
        _roas_value=df[ROAS_COL] * df[SPEND_COL],
        _video_3s_rate_value=df[VIDEO_3S_RATE_COL] * df[IMPRESSIONS_COL],
        _video_avg_time_value=df[VIDEO_AVG_PLAY_TIME_COL] * df[VIDEO_PLAYS_COL],
    )
    agg_map = {
        col: "sum"
        for col in compare_numeric_columns
        if col in roas_source.columns and col not in {ROAS_COL, VIDEO_3S_RATE_COL, VIDEO_AVG_PLAY_TIME_COL}
    }
    agg_map.update(
        {
            SPEND_COL: "sum",
            IMPRESSIONS_COL: "sum",
            REACH_COL: "sum",
            ALL_CLICKS_COL: "sum",
            CLICKS_COL: "sum",
            LANDING_PAGE_VIEWS_COL: "sum",
            VIDEO_PLAYS_COL: "sum",
            ATC_COL: "sum",
            CHECKOUT_COL: "sum",
            PURCHASES_COL: "sum",
            "_roas_value": "sum",
            "_video_3s_rate_value": "sum",
            "_video_avg_time_value": "sum",
        }
    )
    daily = (
        roas_source.groupby(DATE_COL, as_index=False)
        .agg(agg_map)
        .sort_values(DATE_COL)
    )

    daily["整体CTR (%)"] = safe_divide(daily[CLICKS_COL], daily[IMPRESSIONS_COL]) * 100
    daily["CPC (USD)"] = safe_divide(daily[SPEND_COL], daily[CLICKS_COL])
    daily["CPM (USD)"] = safe_divide(daily[SPEND_COL], daily[IMPRESSIONS_COL]) * 1000
    daily["CVR 点击到购买 (%)"] = safe_divide(daily[PURCHASES_COL], daily[CLICKS_COL]) * 100
    daily["CPA 购买成本 (USD)"] = safe_divide(daily[SPEND_COL], daily[PURCHASES_COL])
    daily[ROAS_COL] = safe_divide(daily["_roas_value"], daily[SPEND_COL])
    daily[VIDEO_3S_RATE_COL] = safe_divide(daily["_video_3s_rate_value"], daily[IMPRESSIONS_COL])
    daily[VIDEO_AVG_PLAY_TIME_COL] = safe_divide(daily["_video_avg_time_value"], daily[VIDEO_PLAYS_COL])
    daily = daily.drop(columns=["_roas_value", "_video_3s_rate_value", "_video_avg_time_value"])
    daily.attrs["present_columns"] = df.attrs.get("present_columns", set(df.columns))
    daily.attrs["compare_numeric_columns"] = compare_numeric_columns
    return daily


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    numerator = pd.to_numeric(numerator, errors="coerce").fillna(0)
    denominator = pd.to_numeric(denominator, errors="coerce").fillna(0)
    result = pd.Series(0.0, index=numerator.index)
    valid = denominator.ne(0)
    result.loc[valid] = numerator.loc[valid] / denominator.loc[valid]
    return result


def money(value: float) -> str:
    return f"${value:,.2f}"


def number(value: float) -> str:
    return f"{int(round(value)):,}"


def percentage(value: float) -> str:
    return f"{value:.2f}%"


def roas_health(roas: float) -> HealthBand:
    if roas >= 2.0:
        return HealthBand("健康", "#236a4e")
    if roas >= 1.0:
        return HealthBand("观察", "#b6641f")
    return HealthBand("危险", "#a53d2f")


def render_kpis(daily_df: pd.DataFrame) -> None:
    total_spend = daily_df[SPEND_COL].sum()
    total_impressions = daily_df[IMPRESSIONS_COL].sum()
    total_clicks = daily_df[CLICKS_COL].sum()
    total_purchases = daily_df[PURCHASES_COL].sum()
    weighted_roas = weighted_average(daily_df[ROAS_COL], daily_df[SPEND_COL])
    ctr = safe_divide(pd.Series([total_clicks]), pd.Series([total_impressions])).iloc[0] * 100
    cpa = total_spend / total_purchases if total_purchases else 0
    health = roas_health(weighted_roas)
    ctr_term = glossary_term("CTR")
    roas_term = glossary_term("ROAS")
    cpa_term = glossary_term("CPA")

    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi">
                <div class="kpi-label">总消耗金额</div>
                <div class="kpi-value">{money(total_spend)}</div>
                <div class="kpi-note">全部日期合计</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">总展示 / 点击</div>
                <div class="kpi-value">{number(total_impressions)}</div>
                <div class="kpi-note">{number(total_clicks)} 次链接点击</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">整体链接 {ctr_term}</div>
                <div class="kpi-value">{percentage(ctr)}</div>
                <div class="kpi-note">点击量 ÷ 展示次数</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">购物 {roas_term} / {cpa_term}</div>
                <div class="kpi-value" style="color:{health.color};">{weighted_roas:.2f}</div>
                <div class="kpi-note">{health.label} · {cpa_term} {money(cpa)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_trend_chart(daily_df: pd.DataFrame) -> None:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=daily_df[DATE_COL],
            y=daily_df[SPEND_COL],
            name="每日花费",
            marker_color="#275f8f",
            yaxis="y1",
            hovertemplate="%{x|%Y-%m-%d}<br>花费: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily_df[DATE_COL],
            y=daily_df[ROAS_COL],
            name="购物 ROAS",
            mode="lines+markers",
            line=dict(color="#b6641f", width=3),
            marker=dict(size=8),
            yaxis="y2",
            hovertemplate="%{x|%Y-%m-%d}<br>ROAS: %{y:.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="花费 (USD)", side="left", gridcolor="rgba(24,32,42,0.08)"),
        yaxis2=dict(title="ROAS", side="right", overlaying="y", showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_efficiency_chart(daily_df: pd.DataFrame) -> None:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=daily_df[DATE_COL],
            y=daily_df["整体CTR (%)"],
            name="整体 CTR",
            mode="lines+markers",
            line=dict(color="#236a4e", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily_df[DATE_COL],
            y=daily_df["CPC (USD)"],
            name="CPC",
            mode="lines+markers",
            line=dict(color="#a53d2f", width=3),
            yaxis="y2",
        )
    )
    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="CTR (%)", gridcolor="rgba(24,32,42,0.08)"),
        yaxis2=dict(title="CPC (USD)", side="right", overlaying="y", showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_cpa_change_table(daily_df: pd.DataFrame) -> None:
    cpa_df = daily_df[
        [DATE_COL, SPEND_COL, PURCHASES_COL, "CPA 购买成本 (USD)", ROAS_COL]
    ].copy()
    cpa_df = cpa_df.rename(
        columns={
            DATE_COL: "日期",
            SPEND_COL: "花费 (USD)",
            PURCHASES_COL: "购物次数",
            "CPA 购买成本 (USD)": "单次成效费用 CPA (USD)",
            ROAS_COL: "购物 ROAS",
        }
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=cpa_df["日期"],
            y=cpa_df["单次成效费用 CPA (USD)"],
            name="CPA",
            mode="lines+markers",
            line=dict(color="#0066cc", width=3),
            marker=dict(size=8),
            hovertemplate="%{x|%Y-%m-%d}<br>CPA: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=12, b=10),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        hovermode="x unified",
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="CPA (USD)", gridcolor="rgba(24,32,42,0.08)"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        cpa_df.sort_values("日期", ascending=False),
        use_container_width=True,
        hide_index=True,
    )


def aggregate_compare_by_date(df: pd.DataFrame, group_cols: list[str] | None = None) -> pd.DataFrame:
    group_cols = group_cols or []
    compare_numeric_columns = df.attrs.get("compare_numeric_columns", NUMERIC_COLUMNS)
    source = df.assign(
        _roas_value=df[ROAS_COL] * df[SPEND_COL],
        _video_3s_rate_value=df[VIDEO_3S_RATE_COL] * df[IMPRESSIONS_COL],
        _video_avg_time_value=df[VIDEO_AVG_PLAY_TIME_COL] * df[VIDEO_PLAYS_COL],
    )
    agg_map = {
        col: "sum"
        for col in compare_numeric_columns
        if col in source.columns and col not in {ROAS_COL, VIDEO_3S_RATE_COL, VIDEO_AVG_PLAY_TIME_COL}
    }
    agg_map.update(
        {
            SPEND_COL: "sum",
            IMPRESSIONS_COL: "sum",
            REACH_COL: "sum",
            ALL_CLICKS_COL: "sum",
            CLICKS_COL: "sum",
            LANDING_PAGE_VIEWS_COL: "sum",
            VIDEO_PLAYS_COL: "sum",
            ATC_COL: "sum",
            CHECKOUT_COL: "sum",
            PURCHASES_COL: "sum",
            "_roas_value": "sum",
            "_video_3s_rate_value": "sum",
            "_video_avg_time_value": "sum",
        }
    )
    grouped = (
        source.groupby([DATE_COL] + group_cols, as_index=False)
        .agg(agg_map)
        .sort_values([DATE_COL] + group_cols)
    )
    grouped["整体CTR (%)"] = safe_divide(grouped[CLICKS_COL], grouped[IMPRESSIONS_COL]) * 100
    grouped["CPC (USD)"] = safe_divide(grouped[SPEND_COL], grouped[CLICKS_COL])
    grouped["CPM (USD)"] = safe_divide(grouped[SPEND_COL], grouped[IMPRESSIONS_COL]) * 1000
    grouped["CVR 点击到购买 (%)"] = safe_divide(grouped[PURCHASES_COL], grouped[CLICKS_COL]) * 100
    grouped["CPA 购买成本 (USD)"] = safe_divide(grouped[SPEND_COL], grouped[PURCHASES_COL])
    grouped[ROAS_COL] = safe_divide(grouped["_roas_value"], grouped[SPEND_COL])
    grouped[VIDEO_3S_RATE_COL] = safe_divide(grouped["_video_3s_rate_value"], grouped[IMPRESSIONS_COL])
    grouped[VIDEO_AVG_PLAY_TIME_COL] = safe_divide(grouped["_video_avg_time_value"], grouped[VIDEO_PLAYS_COL])
    return grouped.drop(columns=["_roas_value", "_video_3s_rate_value", "_video_avg_time_value"])


COMPARE_COLORS = ["#0066cc", "#34a853", "#fbbc04", "#ea4335", "#8e44ad", "#00a0b0", "#1d1d1f"]
COMPARE_DASHES = ["solid", "dash", "dot", "dashdot", "longdash", "longdashdot"]
COMPARE_SYMBOLS = ["circle", "square", "diamond", "triangle-up", "cross", "x"]


def get_compare_metric_options(daily_df: pd.DataFrame) -> dict[str, str]:
    compare_numeric_columns = daily_df.attrs.get("compare_numeric_columns", NUMERIC_COLUMNS)
    selectable_columns = set(compare_numeric_columns) | DERIVED_COMPARE_COLUMNS
    metric_options = {
        "花费 (USD)": SPEND_COL,
        "展示次数": IMPRESSIONS_COL,
        "覆盖人数": REACH_COL,
        "点击量": ALL_CLICKS_COL,
        "链接点击量": CLICKS_COL,
        "落地页浏览量": LANDING_PAGE_VIEWS_COL,
        "加购次数": ATC_COL,
        "发起结账次数": CHECKOUT_COL,
        "购买次数": PURCHASES_COL,
        "CTR (%)": "整体CTR (%)",
        "CPC (USD)": "CPC (USD)",
        "CPM (USD)": "CPM (USD)",
        "CVR 点击到购买 (%)": "CVR 点击到购买 (%)",
        "CPA (USD)": "CPA 购买成本 (USD)",
        "ROAS": ROAS_COL,
    }
    metric_options.update(
        {
            "视频播放量": VIDEO_PLAYS_COL,
            "单次展示的播放视频达 3 秒率": VIDEO_3S_RATE_COL,
            "视频平均播放时长": VIDEO_AVG_PLAY_TIME_COL,
        }
    )
    for col in compare_numeric_columns:
        metric_options.setdefault(col, col)

    available_options = {
        label: column
        for label, column in metric_options.items()
        if column in daily_df.columns and column in selectable_columns
    }
    return available_options


def render_compare_style_table(selected_labels: list[str], selected_ad_names: list[str]) -> None:
    rows: list[dict[str, str]] = []
    for metric_index, metric in enumerate(selected_labels):
        row = {"指标名": metric}
        for ad_index, _ad_name in enumerate(selected_ad_names):
            color = COMPARE_COLORS[ad_index % len(COMPARE_COLORS)]
            dash = COMPARE_DASHES[metric_index % len(COMPARE_DASHES)]
            symbol = COMPARE_SYMBOLS[metric_index % len(COMPARE_SYMBOLS)]
            row[_ad_name] = f"颜色 {color} / 线型 {dash} / 端点 {symbol}"
        rows.append(row)

    st.caption("样式说明：列为广告名称，行为指标名。")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_custom_compare_panel(
    filtered_df: pd.DataFrame,
    daily_df: pd.DataFrame,
    available_options: dict[str, str],
    panel_index: int,
) -> None:
    key_prefix = f"compare_{panel_index}"

    scope_col, mode_col = st.columns([1, 1])
    with scope_col:
        compare_scope = st.radio(
            "对比范围",
            ["总量对比", "按广告名称对比"],
            horizontal=True,
            help="总量对比会汇总所有广告；按广告名称对比会把不同广告名称拆成多条线。",
            key=f"{key_prefix}_scope",
        )
    with mode_col:
        mode = st.radio(
            "对比模式",
            ["标准化对比", "原始数值对比"],
            horizontal=True,
            help="标准化会把每个指标缩放到 0-100，适合不同量级一起比较。",
            key=f"{key_prefix}_mode",
        )

    default_labels = [label for label in ["花费 (USD)", "链接点击量", "购买次数", "CPA (USD)"] if label in available_options]
    metric_col, ad_col = st.columns([1.35, 1])
    with metric_col:
        selected_labels = st.multiselect(
            "选择要对比的数据",
            list(available_options.keys()),
            default=default_labels[: min(4, len(default_labels))],
            help="选择多个指标后，会在同一张图中按日期对比。",
            key=f"{key_prefix}_metrics",
        )
    selected_labels = [label for label in selected_labels if label in available_options]

    if not selected_labels:
        st.warning("请至少选择一个指标。")
        return

    ad_name_col = next((col for col in DIMENSION_CANDIDATES if col in filtered_df.columns), None)
    selected_ad_names: list[str] = []
    with ad_col:
        if compare_scope != "按广告名称对比":
            st.caption("总量对比会自动汇总所有广告。")
    if compare_scope == "按广告名称对比":
        if ad_name_col is None:
            st.warning("当前数据没有检测到广告名称列，无法按广告名称对比。")
            return
        ad_summary = (
            filtered_df.groupby(ad_name_col, as_index=False)[SPEND_COL]
            .sum()
            .sort_values(SPEND_COL, ascending=False)
        )
        ad_options = [str(name) for name in ad_summary[ad_name_col].dropna().tolist()]
        with ad_col:
            selected_ad_names = st.multiselect(
                "选择广告名称",
                ad_options,
                default=ad_options[: min(5, len(ad_options))],
                help="建议一次选择 3-5 个广告，图表更清楚。",
                key=f"{key_prefix}_ads",
            )
        if not selected_ad_names:
            st.warning("请至少选择一个广告名称。")
            return

    if compare_scope == "总量对比":
        compare_df = daily_df[[DATE_COL] + [available_options[label] for label in selected_labels]].copy()
        compare_df = compare_df.rename(columns={available_options[label]: label for label in selected_labels})
        series_id_cols: list[str] = []
    else:
        ad_df = filtered_df[filtered_df[ad_name_col].astype(str).isin(selected_ad_names)].copy()
        compare_df = aggregate_compare_by_date(ad_df, [ad_name_col])
        compare_df = compare_df[
            [DATE_COL, ad_name_col] + [available_options[label] for label in selected_labels]
        ].copy()
        compare_df = compare_df.rename(columns={available_options[label]: label for label in selected_labels})
        series_id_cols = [ad_name_col]

    plot_df = compare_df.copy()
    y_title = "数值"
    if mode == "标准化对比":
        if compare_scope == "总量对比":
            for label in selected_labels:
                max_value = plot_df[label].max()
                plot_df[label] = plot_df[label] / max_value * 100 if max_value else 0
        else:
            for label in selected_labels:
                plot_df[label] = plot_df.groupby(ad_name_col)[label].transform(
                    lambda series: series / series.max() * 100 if series.max() else 0
                )
        y_title = "标准化指数 (0-100)"

    long_df = plot_df.melt(
        id_vars=[DATE_COL] + series_id_cols,
        value_vars=selected_labels,
        var_name="指标",
        value_name="数值",
    )
    if compare_scope == "按广告名称对比":
        long_df["系列"] = long_df[ad_name_col].astype(str) + " · " + long_df["指标"]
    else:
        long_df["系列"] = long_df["指标"]

    fig = go.Figure()
    if compare_scope == "按广告名称对比":
        render_compare_style_table(selected_labels, selected_ad_names)
        for metric_index, metric in enumerate(selected_labels):
            for ad_index, ad_name in enumerate(selected_ad_names):
                color = COMPARE_COLORS[ad_index % len(COMPARE_COLORS)]
                series_df = long_df[
                    (long_df["指标"] == metric) & (long_df[ad_name_col].astype(str) == ad_name)
                ]
                fig.add_trace(
                    go.Scatter(
                        x=series_df[DATE_COL],
                        y=series_df["数值"],
                        name=f"{ad_name} · {metric}",
                        mode="lines+markers",
                        line=dict(
                            color=color,
                            width=2.8,
                            dash=COMPARE_DASHES[metric_index % len(COMPARE_DASHES)],
                        ),
                        marker=dict(
                            symbol=COMPARE_SYMBOLS[metric_index % len(COMPARE_SYMBOLS)],
                            size=8,
                            color=color,
                        ),
                    )
                )
    else:
        for metric_index, metric in enumerate(selected_labels):
            series_df = long_df[long_df["指标"] == metric]
            fig.add_trace(
                go.Scatter(
                    x=series_df[DATE_COL],
                    y=series_df["数值"],
                    name=metric,
                    mode="lines+markers",
                    line=dict(color=COMPARE_COLORS[metric_index % len(COMPARE_COLORS)], width=3),
                    marker=dict(size=8, symbol=COMPARE_SYMBOLS[metric_index % len(COMPARE_SYMBOLS)]),
                )
            )

    fig.update_layout(
        height=460,
        margin=dict(l=10, r=10, t=16, b=10),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title=y_title, gridcolor="rgba(24,32,42,0.08)"),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        compare_df.sort_values(DATE_COL, ascending=False),
        use_container_width=True,
        hide_index=True,
    )


def render_custom_compare(filtered_df: pd.DataFrame, daily_df: pd.DataFrame) -> None:
    available_options = get_compare_metric_options(daily_df)
    count_col, hint_col = st.columns([0.85, 3])
    with count_col:
        panel_count = st.number_input(
            "创建对比图数量",
            min_value=1,
            max_value=4,
            value=1,
            step=1,
            help="可创建多个对比图，每个图保留独立的数据、广告和模式选择。",
        )
    with hint_col:
        st.caption("每个对比图都有独立的数据、广告名称和显示模式选择。")
    for panel_index in range(int(panel_count)):
        with st.expander(f"对比图 {panel_index + 1}", expanded=True):
            render_custom_compare_panel(filtered_df, daily_df, available_options, panel_index)


def build_funnel_figure(steps: pd.DataFrame) -> go.Figure:
    steps = steps.copy()
    rates = []
    labels = []
    previous_value = None

    for _, row in steps.iterrows():
        current_value = float(row["数量"])
        if previous_value is None:
            rate_text = "入口"
        else:
            rate = current_value / previous_value * 100 if previous_value else 0
            rate_text = percentage(rate)
        rates.append(rate_text)
        labels.append(f"{number(current_value)}<br>{rate_text}")
        previous_value = current_value

    colors = ["#0066cc", "#4d9de0", "#8bbce8", "#c7d9ec", "#e4edf7"]
    fig = go.Figure(
        go.Funnel(
            y=steps["环节"],
            x=steps["数量"],
            text=labels,
            textinfo="text",
            customdata=rates,
            marker=dict(color=colors[: len(steps)]),
            connector=dict(line=dict(color="#d2d2d7", width=1)),
            hovertemplate="%{y}<br>数量: %{x:,.0f}<br>相邻转化率: %{customdata}<extra></extra>",
        )
    )
    fig.update_layout(
        height=440,
        margin=dict(l=8, r=8, t=12, b=8),
        plot_bgcolor="#f1f4f7",
        paper_bgcolor="#f1f4f7",
        showlegend=False,
        font=dict(
            family="Optimistic VF, Montserrat, Helvetica, Arial, Noto Sans, sans-serif",
            color="#0a1317",
            size=13,
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
        yaxis=dict(title=""),
    )
    return fig


def bounded_percent(value: float) -> float:
    return max(0.0, min(100.0, value))


def render_flow_funnel(stages: list[dict[str, float | str]]) -> None:
    max_value = max(float(stage["value"]) for stage in stages) if stages else 0
    rows = []

    for index, stage in enumerate(stages):
        value = float(stage["value"])
        width = value / max_value * 100 if max_value else 0
        rows.append(
            f"""
            <div class="flow-stage">
                <div class="flow-stage-name">{stage["label"]}</div>
                <div class="flow-track">
                    <div class="flow-fill" style="width:{bounded_percent(width):.2f}%;">{number(value)}</div>
                </div>
                <div class="flow-value">{number(value)}</div>
            </div>
            """
        )

        if index < len(stages) - 1:
            next_stage = stages[index + 1]
            next_value = float(next_stage["value"])
            rate = next_value / value * 100 if value else 0
            rows.append(
                f"""
                <div class="flow-connector">
                    <div></div>
                    <div class="flow-connector-line">
                        <span class="flow-connector-rate">{percentage(rate)}</span>
                    </div>
                    <div class="flow-connector-caption">{next_stage["label"]} / {stage["label"]}</div>
                </div>
                """
            )

    st.markdown(f'<div class="flow-funnel">{"".join(rows)}</div>', unsafe_allow_html=True)


def render_funnel(df: pd.DataFrame) -> None:
    total_spend = float(df[SPEND_COL].sum())
    total_purchases = float(df[PURCHASES_COL].sum())
    cpa = total_spend / total_purchases if total_purchases else 0
    cpa_term = glossary_term("CPA")

    stage_lookup = {label: column for label, column in FUNNEL_STAGE_OPTIONS}
    default_stages = ["点击量", "落地页浏览量", "发起结账次数", "购买次数"]
    stage_col, summary_col = st.columns([1.7, 0.8])
    with stage_col:
        selected_labels = st.multiselect(
            "选择漏斗环节",
            list(stage_lookup.keys()),
            default=default_stages,
            help="按固定业务顺序生成漏斗；至少选择两个环节。",
        )

    ordered_labels = [label for label, _ in FUNNEL_STAGE_OPTIONS if label in selected_labels]
    if len(ordered_labels) < 2:
        st.warning("请至少选择两个漏斗环节。")
        return

    stages = [
        {
            "label": label,
            "value": float(df[stage_lookup[label]].sum()),
        }
        for label in ordered_labels
    ]
    path_copy = " → ".join(ordered_labels)
    connector_count = len(stages) - 1
    with summary_col:
        st.caption(f"{len(stages)} 个环节 · {connector_count} 段转化率")
        st.caption(path_copy)
    steps = pd.DataFrame(stages).rename(columns={"label": "环节", "value": "数量"})
    fig = build_funnel_figure(steps)

    chart_col, metric_col = st.columns([1.7, 0.82])
    with chart_col:
        st.markdown(
            f"""
            <div class="apple-funnel-panel">
                <div class="apple-funnel-stage">自定义路径</div>
                <div class="apple-funnel-title">广告转化漏斗</div>
                <p class="apple-funnel-copy">{path_copy}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True)
    with metric_col:
        st.markdown(
            f"""
            <div class="apple-rate-title">摘要</div>
            <div class="funnel-metrics">
                <div class="funnel-metric">
                    <div class="funnel-label">已选环节</div>
                    <div class="funnel-value">{len(stages)}</div>
                    <div class="funnel-rate">{connector_count} 段连接转化率</div>
                </div>
                <div class="funnel-metric">
                    <div class="funnel-label">单次成效费用 {cpa_term}</div>
                    <div class="funnel-value">{money(cpa)}</div>
                    <div class="funnel-rate">总花费 {money(total_spend)} / 购买次数 {number(total_purchases)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_dimension_rank(df: pd.DataFrame) -> None:
    available_dimensions = [col for col in DIMENSION_CANDIDATES if col in df.columns]
    if not available_dimensions:
        st.info("没有检测到广告系列、广告组或广告名称列，因此跳过层级排行。")
        return

    dimension = st.selectbox("选择排行维度", available_dimensions, index=0)
    ranked = (
        df.groupby(dimension, as_index=False)
        .agg(
            {
                SPEND_COL: "sum",
                IMPRESSIONS_COL: "sum",
                CLICKS_COL: "sum",
                ATC_COL: "sum",
                CHECKOUT_COL: "sum",
                PURCHASES_COL: "sum",
            }
        )
        .sort_values(SPEND_COL, ascending=False)
        .head(20)
    )
    ranked["CTR (%)"] = safe_divide(ranked[CLICKS_COL], ranked[IMPRESSIONS_COL]) * 100
    ranked["CPA (USD)"] = safe_divide(ranked[SPEND_COL], ranked[PURCHASES_COL])

    fig = px.bar(
        ranked.sort_values(SPEND_COL),
        x=SPEND_COL,
        y=dimension,
        orientation="h",
        color="CTR (%)",
        color_continuous_scale=["#a53d2f", "#b6641f", "#236a4e"],
        hover_data={
            SPEND_COL: ":,.2f",
            CLICKS_COL: ":,",
            PURCHASES_COL: ":,",
            "CTR (%)": ":.2f",
            "CPA (USD)": ":.2f",
        },
    )
    fig.update_layout(
        height=max(420, min(820, len(ranked) * 34)),
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        xaxis_title="花费 (USD)",
        yaxis_title="",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        ranked.sort_values(SPEND_COL, ascending=False),
        use_container_width=True,
        hide_index=True,
    )


def build_suggestions(df: pd.DataFrame, daily_df: pd.DataFrame) -> list[tuple[str, str, str]]:
    total_spend = float(daily_df[SPEND_COL].sum())
    total_impressions = float(daily_df[IMPRESSIONS_COL].sum())
    total_clicks = float(daily_df[CLICKS_COL].sum())
    total_atc = float(daily_df[ATC_COL].sum())
    total_checkout = float(daily_df[CHECKOUT_COL].sum())
    total_purchases = float(daily_df[PURCHASES_COL].sum())
    ctr = total_clicks / total_impressions * 100 if total_impressions else 0
    cpc = total_spend / total_clicks if total_clicks else 0
    click_to_atc = total_atc / total_clicks * 100 if total_clicks else 0
    checkout_to_purchase = total_purchases / total_checkout * 100 if total_checkout else 0
    roas = weighted_average(df[ROAS_COL], df[SPEND_COL])

    suggestions: list[tuple[str, str, str]] = []

    if ctr < 1:
        suggestions.append(
            (
                "bad",
                "素材与受众需要优先排查",
                f"整体链接 CTR 为 {ctr:.2f}%，低于 1%。优先测试首屏更直接的产品卖点、不同角度素材，并拆分高意图受众与宽泛受众。",
            )
        )
    else:
        suggestions.append(
            (
                "good",
                "点击吸引力达标",
                f"整体链接 CTR 为 {ctr:.2f}%，素材能吸引用户进入落地页。下一步重点看加购率、结账率和 ROAS。",
            )
        )

    if total_clicks > 0 and click_to_atc < 3:
        suggestions.append(
            (
                "warn",
                "落地页承接可能偏弱",
                f"点击到加购率为 {click_to_atc:.2f}%。建议检查产品页加载速度、价格信息、变体选择、评价和信任背书。",
            )
        )

    if total_atc > 0 and total_purchases == 0:
        suggestions.append(
            (
                "bad",
                "加购后没有形成购买",
                "已有加购但购买成效为 0。建议立刻检查支付网关、运费、折扣码、库存状态，并建立加购未购买再营销。",
            )
        )

    if total_checkout > 0 and checkout_to_purchase < 25:
        suggestions.append(
            (
                "warn",
                "结账流失较高",
                f"发起结账到购买转化率为 {checkout_to_purchase:.2f}%。请重点检查结账页费用突增、支付方式覆盖和移动端表单体验。",
            )
        )

    if total_spend > 100 and total_purchases == 0:
        suggestions.append(
            (
                "bad",
                "消耗已进入止损区间",
                "总花费超过 $100 且没有购买。建议暂停明显低效广告组，把预算转向再营销或重新测试产品页与素材组合。",
            )
        )

    if roas >= 2:
        suggestions.append(
            (
                "good",
                "存在可放量信号",
                f"按花费加权后的购物 ROAS 为 {roas:.2f}。可以小步提升预算，并观察 CPA、频次和 CTR 是否同步恶化。",
            )
        )
    elif total_purchases > 0:
        suggestions.append(
            (
                "warn",
                "有转化但利润空间需复核",
                f"当前购物 ROAS 为 {roas:.2f}，建议结合毛利率判断盈亏线，并按广告组筛掉高花费低回报单元。",
            )
        )

    if cpc > 2:
        suggestions.append(
            (
                "warn",
                "点击成本偏高",
                f"当前 CPC 为 ${cpc:.2f}。如果客单价不高，建议增加低成本素材测试，并关注 CPM 是否由受众竞争推高。",
            )
        )

    return suggestions


def render_suggestions(df: pd.DataFrame, daily_df: pd.DataFrame) -> None:
    suggestions = build_suggestions(df, daily_df)
    for level, title, body in suggestions:
        st.markdown(
            f"""
            <div class="suggestion {level}">
                <div class="suggestion-title">{title}</div>
                <div class="suggestion-body">{body}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_data_quality(df: pd.DataFrame) -> None:
    present = [col for col in CANONICAL_COLUMNS if col in df.columns]
    missing = [col for col in CANONICAL_COLUMNS if col not in df.columns]

    with st.expander("数据字段检查", expanded=False):
        st.write("已识别字段：", "、".join(present))
        if missing:
            st.write("未识别字段：", "、".join(missing))
        st.dataframe(df.head(30), use_container_width=True, hide_index=True)


def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("筛选")
    min_date = df[DATE_COL].min().date()
    max_date = df[DATE_COL].max().date()
    selected_range = st.sidebar.date_input(
        "日期范围",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    filtered = df.copy()
    if isinstance(selected_range, tuple) and len(selected_range) == 2:
        start, end = selected_range
        filtered = filtered[
            (filtered[DATE_COL].dt.date >= start) & (filtered[DATE_COL].dt.date <= end)
        ]

    available_dimensions = [col for col in DIMENSION_CANDIDATES if col in filtered.columns]
    for dim in available_dimensions:
        values = sorted(str(v) for v in filtered[dim].dropna().unique())
        if not values:
            continue
        selected = st.sidebar.multiselect(
            dim,
            values,
            default=[],
            help="留空表示不过滤该维度。",
        )
        if selected:
            filtered = filtered[filtered[dim].astype(str).isin(selected)]

    st.sidebar.caption(f"当前样本：{len(filtered):,} 行")
    return filtered


def main() -> None:
    inject_css()
    render_header()

    upload_col, option_col = st.columns([4, 1.25])
    with upload_col:
        uploaded_files = st.file_uploader(
            "上传 Meta 广告数据文件",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=True,
            help="支持 Meta Ads Manager 导出的中文 CSV、Excel 文件。",
        )
    with option_col:
        dedupe_rows = st.checkbox(
            "合并后去重",
            value=True,
            help="按所有真实数据列完全一致的行去重。",
        )

    if not uploaded_files:
        st.info("请先上传 CSV 或 Excel 文件。上传后会自动生成 KPI、趋势、漏斗、排行和诊断建议。")
        with st.expander("需要包含哪些字段？", expanded=False):
            st.write(
                "建议至少包含：报告开始日期、已花费金额 (USD)、展示次数、链接点击量、加入购物车次数、结账发起次数、成效、广告花费回报 (ROAS) - 购物。"
            )
        return

    try:
        raw_df = parse_uploaded_files(uploaded_files)
        before_dedupe_rows = len(raw_df)
        if dedupe_rows:
            dedupe_columns = [col for col in raw_df.columns if col != "_来源文件"]
            raw_df = raw_df.drop_duplicates(subset=dedupe_columns)
            removed_rows = before_dedupe_rows - len(raw_df)
            if removed_rows:
                st.info(f"已合并 {len(uploaded_files)} 个文件，并去除 {removed_rows:,} 行重复数据。")
            else:
                st.info(f"已合并 {len(uploaded_files)} 个文件，未发现重复行。")
        else:
            st.info(f"已合并 {len(uploaded_files)} 个文件，保留全部 {len(raw_df):,} 行。")
        df = preprocess(raw_df)
    except Exception as exc:
        st.error(f"数据读取或清洗失败：{exc}")
        return

    filtered_df = render_sidebar(df)
    if filtered_df.empty:
        st.warning("当前筛选条件下没有数据。")
        return

    daily_df = build_daily_df(filtered_df)

    render_data_quality(filtered_df)
    render_kpis(daily_df)

    tab_compare, tab_overview, tab_funnel, tab_rank, tab_raw = st.tabs(
        ["自定义对比", "趋势效率", "转化漏斗", "广告排行", "明细导出"]
    )

    with tab_compare:
        render_section_title("自定义数据对比")
        render_custom_compare(filtered_df, daily_df)

    with tab_overview:
        render_section_title(f"每日花费与 {glossary_term('ROAS')}")
        render_trend_chart(daily_df)
        render_section_title(f"{glossary_term('CTR')} 与 {glossary_term('CPC')}")
        render_efficiency_chart(daily_df)
        render_section_title(f"单次成效费用 {glossary_term('CPA')} 变化表")
        render_cpa_change_table(daily_df)

    with tab_funnel:
        render_section_title(f"广告转化漏斗与单次成效费用 {glossary_term('CPA')}")
        render_funnel(filtered_df)
        render_section_title("自动化诊断与策略建议")
        render_suggestions(filtered_df, daily_df)

    with tab_rank:
        render_section_title("广告层级表现排行")
        render_dimension_rank(filtered_df)

    with tab_raw:
        render_section_title("每日聚合数据")
        st.dataframe(daily_df, use_container_width=True, hide_index=True)
        st.download_button(
            "下载每日聚合 CSV",
            data=daily_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="meta_ads_daily_analysis.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
