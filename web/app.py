from __future__ import annotations

import sys
from pathlib import Path

# 确保 src 模块可导入（Streamlit 以 web/ 为 cwd 运行）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.model import UserPreference
from src.recommender import recommend

st.set_page_config(page_title="穿搭推荐系统", layout="centered")
st.title("穿搭推荐系统")
st.markdown("选择你需要的条件，获取个性化的服装搭配推荐。")

with st.sidebar:
    st.header("选择偏好")
    season = st.selectbox("季节", ["spring", "summer", "autumn", "winter"])
    occasion = st.selectbox("场合", ["casual", "business", "formal", "sporty"])
    style = st.selectbox("风格", ["casual", "formal", "sporty", "street"])
    color = st.selectbox("颜色偏好（可选）", [None, "white", "black", "gray", "blue", "brown", "beige"])
    top_n = st.slider("推荐数量", 1, 5, 3)

    recommend_btn = st.button("获取推荐", type="primary")

if recommend_btn:
    pref = UserPreference(
        season=season,
        occasion=occasion,
        style=style,
        color_preference=color,
        top_n=top_n,
    )

    with st.spinner("正在为你搭配..."):
        outfits = recommend(pref)

    if not outfits:
        st.warning("没有找到匹配的搭配，请尝试调整筛选条件。")
    else:
        st.success(f"找到 {len(outfits)} 套搭配推荐")
        for i, outfit in enumerate(outfits, 1):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"搭配 #{i}")
                    items_text = " + ".join(item.name for item in outfit.items)
                    st.write(f"**{items_text}**")
                    st.caption(outfit.reason)
                with col2:
                    st.metric("评分", outfit.score)
else:
    st.info("请在左侧选择偏好后点击「获取推荐」")
    st.page_link("https://streamlit.io", label="Powered by Streamlit", icon="🌐")
