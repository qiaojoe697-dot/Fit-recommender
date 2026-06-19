from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from src.model import UserBehavior, UserPreference
from src.outfit_recommender import load_outfits, recommend_for_user, recommend_similar
from src.profile import build_user_profile
from src.recommender import recommend

# ── 页面配置 ──────────────────────────────────────────────────────────────────
st.set_page_config(page_title="穿搭推荐系统", page_icon="👗", layout="wide")

st.markdown("""
<style>
.score-badge { font-size: 2rem; font-weight: 700; color: #ff6b6b; }
.tip-box {
    background: #fff8f0; border-radius: 8px; padding: 10px 14px;
    font-size: 0.9rem; color: #888; margin-top: 8px;
}
.item-tag {
    display: inline-block; background: #f0f0f0; border-radius: 20px;
    padding: 2px 10px; margin: 3px 3px 3px 0; font-size: 0.85rem;
}
.tag-chip {
    display: inline-block; background: #e8f4fd; border-radius: 12px;
    padding: 2px 8px; margin: 2px; font-size: 0.8rem; color: #2E75B6;
}
</style>
""", unsafe_allow_html=True)

# ── 标题 ──────────────────────────────────────────────────────────────────────
st.title("👗 穿搭推荐系统")
st.markdown("支持 **单品搭配推荐** 与 **用户画像个性化推荐** 双模式")
st.divider()

tab1, tab2, tab3 = st.tabs(["🎯 单品搭配推荐", "👤 个性化穿搭推荐", "🔍 相似穿搭推荐"])

# ═══════════════════════════════════════════════════════
# TAB 1：原有单品打分推荐（ClothingItem 组合）
# ═══════════════════════════════════════════════════════
with tab1:
    st.subheader("根据季节、场合、风格推荐单品搭配")

    col_left, col_main = st.columns([1, 3])

    with col_left:
        st.markdown("**选择偏好**")
        season = st.selectbox("🌤 季节", ["spring", "summer", "autumn", "winter"],
            format_func=lambda x: {"spring":"🌸 春季","summer":"☀️ 夏季",
                                    "autumn":"🍂 秋季","winter":"❄️ 冬季"}[x], key="t1_season")
        occasion = st.selectbox("📍 场合", ["casual","business","formal","sporty","date"],
            format_func=lambda x: {"casual":"🛍 日常休闲","business":"💼 商务办公",
                                    "formal":"🎩 正式场合","sporty":"🏃 运动健身",
                                    "date":"💕 约会出行"}[x], key="t1_occasion")
        style = st.selectbox("✨ 风格", ["casual","formal","sporty","street"],
            format_func=lambda x: {"casual":"😊 休闲简约","formal":"👔 商务正式",
                                    "sporty":"🏅 运动机能","street":"🔥 街头潮流"}[x], key="t1_style")
        color = st.selectbox("🎨 颜色偏好", [None,"white","black","gray","blue","navy",
                "brown","beige","red","pink","green","gold","purple","orange"],
            format_func=lambda x: "不限" if x is None else {
                "white":"⬜ 白色","black":"⬛ 黑色","gray":"🩶 灰色","blue":"🔵 蓝色",
                "navy":"🌊 藏青","brown":"🤎 棕色","beige":"🟤 米色","red":"❤️ 红色",
                "pink":"🩷 粉色","green":"💚 绿色","gold":"🥇 金色",
                "purple":"💜 紫色","orange":"🧡 橙色"}.get(x, x), key="t1_color")
        top_n = st.slider("推荐数量", 1, 6, 3, key="t1_topn")
        btn1 = st.button("🚀 获取推荐", type="primary", use_container_width=True, key="btn1")

    with col_main:
        if btn1:
            pref = UserPreference(season=season, occasion=occasion,
                                  style=style, color_preference=color, top_n=top_n)
            with st.spinner("搭配中..."):
                outfits = recommend(pref)

            if not outfits:
                st.warning("😕 没有找到匹配搭配，请尝试调整条件。")
            else:
                st.success(f"✅ 找到 **{len(outfits)}** 套搭配")
                for i, outfit in enumerate(outfits, 1):
                    col_info, col_score = st.columns([5, 1])
                    with col_info:
                        st.markdown(f"#### 搭配 #{i}")
                        tags_html = "".join(
                            f'<span class="item-tag">{"👕" if it.category=="top" else "👖" if it.category=="bottom" else "👟" if it.category=="shoes" else "💼"} {it.name}</span>'
                            for it in outfit.items
                        )
                        st.markdown(tags_html, unsafe_allow_html=True)
                        if outfit.style_tip:
                            st.markdown(f'<div class="tip-box">💡 {outfit.style_tip}</div>',
                                        unsafe_allow_html=True)
                    with col_score:
                        st.markdown(f'<div class="score-badge">{outfit.score}</div>'
                                    '<div style="color:#aaa;font-size:0.8rem">综合评分</div>',
                                    unsafe_allow_html=True)
                    st.divider()
        else:
            st.info("在左侧选择条件，点击「获取推荐」查看搭配结果。")

# ═══════════════════════════════════════════════════════
# TAB 2：用户画像个性化推荐（Jaccard 相似度）
# ═══════════════════════════════════════════════════════
with tab2:
    st.subheader("基于用户画像的个性化穿搭推荐")
    st.caption("系统根据你的显式偏好标签 + 行为记录，构建用户画像，用杰卡德相似度匹配最适合你的穿搭。")

    col_l, col_r = st.columns([1, 3])

    with col_l:
        st.markdown("**① 显式偏好标签**（手动勾选）")
        # ✅ 修复：只用中文标签，与 outfits.json 的 tags 字段保持一致
        all_explicit_options = [
            "休闲", "商务", "正式", "街头", "运动", "约会",
            "校园", "通勤", "浪漫", "简约", "甜美", "知性",
            "度假", "保暖", "复古", "工装", "机能", "温柔",
            "潮流", "晚宴", "礼服", "健身", "户外",
            "春季", "夏季", "秋季", "冬季",
        ]
        explicit_tags = st.multiselect(
            "选择你喜欢的标签",
            all_explicit_options,
            default=["休闲", "夏季"],
            key="explicit_tags"
        )

        st.markdown("**② 模拟行为记录**（隐式画像）")
        outfits_for_behavior = load_outfits()
        outfit_options = {o.name: o.id for o in outfits_for_behavior}

        viewed = st.multiselect("👀 浏览过的穿搭",
            list(outfit_options.keys()), key="viewed")
        liked = st.multiselect("❤️ 收藏过的穿搭",
            list(outfit_options.keys()), key="liked")

        use_weighted = st.checkbox("启用加权杰卡德（显式标签权重更高）", value=True)
        top_n2 = st.slider("推荐数量", 1, 10, 5, key="t2_topn")
        btn2 = st.button("🔍 个性化推荐", type="primary", use_container_width=True, key="btn2")

    with col_r:
        if btn2:
            behaviors = []
            for name in viewed:
                behaviors.append(UserBehavior(outfit_id=outfit_options[name], action="view"))
            for name in liked:
                behaviors.append(UserBehavior(outfit_id=outfit_options[name], action="like"))

            outfit_map = {o.id: o for o in outfits_for_behavior}

            profile = build_user_profile(
                user_id="demo_user",
                explicit_tags=set(explicit_tags),
                behaviors=behaviors,
                outfit_map=outfit_map,
            )

            with st.spinner("计算相似度中..."):
                results = recommend_for_user(
                    profile=profile,
                    outfits=outfits_for_behavior,
                    top_n=top_n2,
                    use_weighted=use_weighted,
                )

            with st.expander("📊 查看用户画像详情", expanded=False):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**显式标签**")
                    if profile.explicit_tags:
                        st.markdown("".join(f'<span class="tag-chip">{t}</span>' for t in sorted(profile.explicit_tags)), unsafe_allow_html=True)
                    else:
                        st.caption("无")
                with c2:
                    st.markdown("**隐式标签**（行为挖掘）")
                    if profile.implicit_tags:
                        st.markdown("".join(f'<span class="tag-chip">{t}</span>' for t in sorted(profile.implicit_tags)), unsafe_allow_html=True)
                    else:
                        st.caption("无行为数据")
                with c3:
                    st.markdown("**合并画像**")
                    if profile.merged_tags:
                        st.markdown("".join(f'<span class="tag-chip">{t}</span>' for t in sorted(profile.merged_tags)), unsafe_allow_html=True)

            if not profile.merged_tags:
                st.info("💡 未检测到偏好数据，已按热门度为你推荐。")
            else:
                algo = "加权杰卡德相似度" if use_weighted else "基础杰卡德相似度"
                st.success(f"✅ 基于 **{algo}** 匹配，共推荐 **{len(results)}** 套穿搭")

            for i, (outfit, score) in enumerate(results, 1):
                col_info, col_score = st.columns([5, 1])
                with col_info:
                    st.markdown(f"**#{i} {outfit.name}**")
                    st.markdown("".join(f'<span class="tag-chip">{t}</span>' for t in outfit.tags[:6]), unsafe_allow_html=True)
                with col_score:
                    score_label = "相似度" if profile.merged_tags else "热门度"
                    st.markdown(f'<div class="score-badge">{score:.2f}</div>'
                                f'<div style="color:#aaa;font-size:0.8rem">{score_label}</div>',
                                unsafe_allow_html=True)
                st.divider()
        else:
            st.info("在左侧设置你的标签偏好和行为记录，点击「个性化推荐」查看结果。")
            st.markdown("""
**算法说明：**
- **显式画像**：你手动勾选的标签，代表主动偏好
- **隐式画像**：系统从浏览/收藏行为中自动提取的高频标签（收藏权重 ×2）
- **相似度计算**：杰卡德相似度 = 交集标签数 / 并集标签数
- **冷启动**：若无任何偏好数据，改用穿搭热门度排序
""")

# ═══════════════════════════════════════════════════════
# TAB 3：穿搭详情页相似推荐（10高 + 10低）
# ═══════════════════════════════════════════════════════
with tab3:
    st.subheader("穿搭相似推荐（高相似 + 低相似）")
    st.caption("模拟穿搭详情页逻辑：选一套穿搭，系统计算与其他所有穿搭的杰卡德相似度，分为高/低相似两组各展示。")

    all_outfits = load_outfits()
    outfit_name_map = {o.name: o.id for o in all_outfits}

    selected_name = st.selectbox("选择一套穿搭作为基准", list(outfit_name_map.keys()), key="similar_select")
    threshold = st.slider("高/低相似度分界阈值", 0.0, 1.0, 0.3, 0.05, key="threshold")
    btn3 = st.button("🔍 查找相似穿搭", type="primary", key="btn3")

    if btn3:
        target_id = outfit_name_map[selected_name]
        target_outfit = next(o for o in all_outfits if o.id == target_id)
        st.markdown(f"**基准穿搭：{target_outfit.name}**")
        st.markdown("".join(f'<span class="tag-chip">{t}</span>' for t in target_outfit.tags), unsafe_allow_html=True)
        st.divider()

        with st.spinner("计算相似度中..."):
            result = recommend_similar(
                target_outfit_id=target_id,
                outfits=all_outfits,
                threshold=threshold,
            )

        col_high, col_low = st.columns(2)

        with col_high:
            high_list = result["high"]
            st.markdown(f"### 🔴 高相似穿搭（{len(high_list)} 套）")
            st.caption(f"相似度 ≥ {threshold}")
            if not high_list:
                st.info("无高相似穿搭")
            for outfit, score in high_list:
                st.markdown(f"**{outfit.name}** — 相似度 `{score:.2f}`")
                st.markdown("".join(f'<span class="tag-chip">{t}</span>' for t in outfit.tags[:5]), unsafe_allow_html=True)
                st.markdown("---")

        with col_low:
            low_list = result["low"]
            st.markdown(f"### 🔵 低相似穿搭（{len(low_list)} 套）")
            st.caption(f"相似度 < {threshold}")
            if not low_list:
                st.info("无低相似穿搭")
            for outfit, score in low_list:
                st.markdown(f"**{outfit.name}** — 相似度 `{score:.2f}`")
                st.markdown("".join(f'<span class="tag-chip">{t}</span>' for t in outfit.tags[:5]), unsafe_allow_html=True)
                st.markdown("---")
    else:
        st.info("选择基准穿搭后点击查找。")
