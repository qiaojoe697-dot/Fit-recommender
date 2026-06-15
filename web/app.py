from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from src.model import UserPreference
from src.recommender import recommend

# ── 页面配置 ──────────────────────────────────────────────
st.set_page_config(
    page_title="穿搭推荐系统",
    page_icon="👗",
    layout="wide",
)

# ── 全局样式 ──────────────────────────────────────────────
st.markdown("""
<style>
.outfit-card {
    background: #fafafa;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    border-left: 4px solid #ff6b6b;
}
.score-badge {
    font-size: 2rem;
    font-weight: 700;
    color: #ff6b6b;
}
.tip-box {
    background: #fff8f0;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.9rem;
    color: #888;
    margin-top: 8px;
}
.item-tag {
    display: inline-block;
    background: #f0f0f0;
    border-radius: 20px;
    padding: 2px 10px;
    margin: 3px 3px 3px 0;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

# ── 标题区 ────────────────────────────────────────────────
st.title("👗 穿搭推荐系统")
st.markdown("根据你的**季节、场合、风格**偏好，智能推荐最适合的搭配方案。")
st.divider()

# ── 侧边栏：筛选条件 ──────────────────────────────────────
with st.sidebar:
    st.header("🎯 选择你的偏好")

    season = st.selectbox(
        "🌤 季节",
        ["spring", "summer", "autumn", "winter"],
        format_func=lambda x: {"spring": "🌸 春季", "summer": "☀️ 夏季",
                                "autumn": "🍂 秋季", "winter": "❄️ 冬季"}[x],
    )
    occasion = st.selectbox(
        "📍 场合",
        ["casual", "business", "formal", "sporty", "date"],
        format_func=lambda x: {
            "casual": "🛍 日常休闲", "business": "💼 商务办公",
            "formal": "🎩 正式场合", "sporty": "🏃 运动健身",
            "date": "💕 约会出行",
        }[x],
    )
    style = st.selectbox(
        "✨ 风格",
        ["casual", "formal", "sporty", "street"],
        format_func=lambda x: {
            "casual": "😊 休闲简约", "formal": "👔 商务正式",
            "sporty": "🏅 运动机能", "street": "🔥 街头潮流",
        }[x],
    )
    color = st.selectbox(
        "🎨 颜色偏好（可选）",
        [None, "white", "black", "gray", "blue", "navy", "brown",
         "beige", "red", "pink", "green", "gold", "purple", "orange"],
        format_func=lambda x: "不限" if x is None else {
            "white": "⬜ 白色", "black": "⬛ 黑色", "gray": "🩶 灰色",
            "blue": "🔵 蓝色", "navy": "🌊 藏青色", "brown": "🤎 棕色",
            "beige": "🟤 米色", "red": "❤️ 红色", "pink": "🩷 粉色",
            "green": "💚 绿色", "gold": "🥇 金色", "purple": "💜 紫色",
            "orange": "🧡 橙色",
        }.get(x, x),
    )
    top_n = st.slider("📋 推荐数量", 1, 6, 3)

    st.divider()
    recommend_btn = st.button("🚀 获取推荐", type="primary", use_container_width=True)

# ── 主内容区 ──────────────────────────────────────────────
if recommend_btn:
    pref = UserPreference(
        season=season,
        occasion=occasion,
        style=style,
        color_preference=color,
        top_n=top_n,
    )

    with st.spinner("正在为你智能搭配中..."):
        outfits = recommend(pref)

    if not outfits:
        st.warning("😕 没有找到完全匹配的搭配，建议尝试调整场合或风格。")
    else:
        season_label = {"spring": "春季", "summer": "夏季", "autumn": "秋季", "winter": "冬季"}[season]
        occasion_label = {"casual": "日常休闲", "business": "商务办公", "formal": "正式场合",
                          "sporty": "运动健身", "date": "约会出行"}[occasion]
        style_label = {"casual": "休闲简约", "formal": "商务正式",
                       "sporty": "运动机能", "street": "街头潮流"}[style]

        st.success(f"✅ 为你找到 **{len(outfits)}** 套搭配 | {season_label} · {occasion_label} · {style_label}风格")

        for i, outfit in enumerate(outfits, 1):
            with st.container():
                col_left, col_right = st.columns([5, 1])

                with col_left:
                    st.markdown(f"#### 搭配 #{i}")

                    # 单品展示（用标签样式）
                    tags_html = "".join(
                        f'<span class="item-tag">{"👕" if item.category == "top" else "👖" if item.category == "bottom" else "👟" if item.category == "shoes" else "💼"} {item.name}</span>'
                        for item in outfit.items
                    )
                    st.markdown(tags_html, unsafe_allow_html=True)

                    # 穿搭建议
                    if outfit.style_tip:
                        st.markdown(
                            f'<div class="tip-box">💡 {outfit.style_tip}</div>',
                            unsafe_allow_html=True,
                        )

                with col_right:
                    st.markdown(
                        f'<div class="score-badge">{outfit.score}</div><div style="color:#aaa;font-size:0.8rem">综合评分</div>',
                        unsafe_allow_html=True,
                    )

                st.divider()

else:
    # 默认引导页
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**第一步**\n\n在左侧选择季节、场合和风格")
    with col2:
        st.info("**第二步**\n\n可选择颜色偏好和推荐数量")
    with col3:
        st.info("**第三步**\n\n点击「获取推荐」查看搭配结果")

    st.markdown("---")
    st.markdown("**支持的场合：** 日常休闲 · 商务办公 · 正式场合 · 运动健身 · 💕 约会出行（新增）")
    st.markdown("**支持的颜色：** 白 · 黑 · 灰 · 蓝 · 藏青 · 棕 · 米 · 红 · 粉 · 绿 · 金 · 紫 · 橙（新增 8 色）")
