"""
web/app.py — Streamlit 网页界面（三 Tab 结构）

Tab1：单品搭配推荐      按季节/场合/风格/颜色打分，推荐单品组合
Tab2：个性化穿搭推荐    基于用户画像（显式+隐式）+杰卡德相似度推荐穿搭库
Tab3：相似穿搭推荐      详情页逻辑，以目标穿搭为基准输出10高+10低
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.model import UserBehavior, UserPreference, UserProfile
from src.outfit_recommender import load_outfits, recommend_for_user, recommend_similar
from src.profile import build_user_profile
from src.recommender import recommend

# ── 页面配置 ──────────────────────────────────────────────────────────────────
st.set_page_config(page_title="穿搭推荐系统", page_icon="👗", layout="wide")

st.markdown("""
<style>
.score-badge  { font-size: 2rem; font-weight: 700; color: #ff6b6b; }
.tip-box      { background:#fff8f0; border-radius:8px; padding:10px 14px;
                font-size:0.9rem; color:#888; margin-top:8px; }
.tag-chip     { display:inline-block; background:#e8f4fd; border-radius:12px;
                padding:2px 8px; margin:2px; font-size:0.82rem; color:#2E75B6; }
.item-tag     { display:inline-block; background:#f0f0f0; border-radius:20px;
                padding:2px 10px; margin:3px; font-size:0.85rem; }
.section-note { background:#f8f9fa; border-left:3px solid #2E75B6;
                padding:8px 12px; border-radius:4px; font-size:0.88rem; color:#555; }
</style>
""", unsafe_allow_html=True)

# ── 标题 ──────────────────────────────────────────────────────────────────────
st.title("👗 穿搭推荐系统")
st.markdown("支持 **单品搭配推荐** · **个性化穿搭推荐（用户画像 + 杰卡德相似度）** · **相似穿搭推荐（10高+10低）**")
st.divider()

tab1, tab2, tab3 = st.tabs(["🎯 单品搭配推荐", "👤 个性化穿搭推荐", "🔍 相似穿搭推荐"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1：单品搭配推荐（ClothingItem 打分组合）
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("根据季节、场合、风格推荐最优单品组合")
    st.markdown('<div class="section-note">算法：单品多维度打分（风格×2.5 + 场合×2.0 + 季节×1.0 + 颜色×1.5）→ 三维组合 → 颜色和谐度加成 + 风格一致性加成</div>', unsafe_allow_html=True)
    st.markdown("")

    col_left, col_main = st.columns([1, 3])

    with col_left:
        season = st.selectbox("🌤 季节", ["spring","summer","autumn","winter"],
            format_func=lambda x: {"spring":"🌸 春季","summer":"☀️ 夏季",
                                    "autumn":"🍂 秋季","winter":"❄️ 冬季"}[x], key="t1_season")
        occasion = st.selectbox("📍 场合", ["casual","business","formal","sporty","date"],
            format_func=lambda x: {"casual":"🛍 日常休闲","business":"💼 商务办公",
                                    "formal":"🎩 正式场合","sporty":"🏃 运动健身",
                                    "date":"💕 约会出行"}[x], key="t1_occasion")
        style = st.selectbox("✨ 风格", ["casual","formal","sporty","street"],
            format_func=lambda x: {"casual":"😊 休闲简约","formal":"👔 商务正式",
                                    "sporty":"🏅 运动机能","street":"🔥 街头潮流"}[x], key="t1_style")
        color = st.selectbox("🎨 颜色偏好",
            [None,"white","black","gray","blue","navy","brown","beige",
             "red","pink","green","gold","purple","orange"],
            format_func=lambda x: "不限" if x is None else {
                "white":"⬜ 白","black":"⬛ 黑","gray":"🩶 灰","blue":"🔵 蓝",
                "navy":"🌊 藏青","brown":"🤎 棕","beige":"🟤 米","red":"❤️ 红",
                "pink":"🩷 粉","green":"💚 绿","gold":"🥇 金",
                "purple":"💜 紫","orange":"🧡 橙"}.get(x, x), key="t1_color")
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
                        icons = {"top":"👕","bottom":"👖","shoes":"👟","accessory":"💼"}
                        tags_html = "".join(
                            f'<span class="item-tag">{icons.get(it.category,"🔸")} {it.name}</span>'
                            for it in outfit.items)
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
            st.info("在左侧选择条件后点击「获取推荐」。")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2：个性化穿搭推荐（用户画像 + 杰卡德相似度）
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("基于用户画像的个性化穿搭推荐")
    st.markdown('<div class="section-note">算法：构建用户画像（显式标签 ∪ 隐式标签）→ 杰卡德相似度 J(A,B)=|A∩B|/|A∪B| → 按相似度降序推荐 | 冷启动时按热门度兜底</div>', unsafe_allow_html=True)
    st.markdown("")

    col_l, col_r = st.columns([1, 3])

    with col_l:
        st.markdown("**① 显式偏好标签**（手动勾选，模拟个人中心）")
        # 标签与 outfits.json 的 tags 字段保持完全一致（纯中文）
        ALL_TAGS = [
            "休闲","商务","正式","街头","运动","约会",
            "校园","通勤","浪漫","简约","甜美","知性",
            "度假","保暖","复古","工装","机能","温柔",
            "潮流","晚宴","礼服","健身","户外",
            "春季","夏季","秋季","冬季",
        ]
        explicit_tags = st.multiselect(
            "选择你喜欢的标签",
            ALL_TAGS,
            default=["休闲","夏季"],
            key="explicit_tags",
        )

        st.markdown("**② 行为记录**（浏览/收藏，模拟数据埋点）")
        all_outfits_for_behavior = load_outfits()
        outfit_name_to_id = {o.name: o.id for o in all_outfits_for_behavior}

        viewed = st.multiselect(
            "👀 浏览过的穿搭", list(outfit_name_to_id.keys()), key="viewed")
        liked = st.multiselect(
            "❤️ 收藏过的穿搭", list(outfit_name_to_id.keys()), key="liked")

        use_weighted = st.checkbox("启用加权杰卡德（显式权重 w₁=2，隐式权重 w₂=1）", value=True)
        top_n2 = st.slider("推荐数量", 1, 10, 5, key="t2_topn")
        btn2 = st.button("🔍 个性化推荐", type="primary", use_container_width=True, key="btn2")

    with col_r:
        if btn2:
            # 构建行为列表
            behaviors = (
                [UserBehavior(outfit_id=outfit_name_to_id[n], action="view") for n in viewed]
                + [UserBehavior(outfit_id=outfit_name_to_id[n], action="like") for n in liked]
            )

            outfit_map = {o.id: o for o in all_outfits_for_behavior}

            # 构建用户画像（显式 + 隐式 → merged）
            profile = build_user_profile(
                user_id="demo_user",
                explicit_tags=set(explicit_tags),
                behaviors=behaviors,
                outfit_map=outfit_map,
            )

            with st.spinner("计算杰卡德相似度中..."):
                results = recommend_for_user(
                    profile=profile,
                    outfits=all_outfits_for_behavior,
                    top_n=top_n2,
                    use_weighted=use_weighted,
                )

            # 展示用户画像详情
            with st.expander("📊 用户画像详情", expanded=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**显式标签**（手动勾选）")
                    if profile.explicit_tags:
                        st.markdown("".join(f'<span class="tag-chip">{t}</span>'
                                            for t in sorted(profile.explicit_tags)),
                                    unsafe_allow_html=True)
                    else:
                        st.caption("无")
                with c2:
                    st.markdown("**隐式标签**（行为挖掘）")
                    if profile.implicit_tags:
                        st.markdown("".join(f'<span class="tag-chip">{t}</span>'
                                            for t in sorted(profile.implicit_tags)),
                                    unsafe_allow_html=True)
                    else:
                        st.caption("无行为数据或频次不足")
                with c3:
                    st.markdown("**合并画像**（显式 ∪ 隐式）")
                    if profile.merged_tags:
                        st.markdown("".join(f'<span class="tag-chip">{t}</span>'
                                            for t in sorted(profile.merged_tags)),
                                    unsafe_allow_html=True)

            # 推荐结果
            algo_name = "加权杰卡德相似度" if use_weighted else "基础杰卡德相似度"
            is_cold = profile.is_cold_start()

            if is_cold:
                st.info(f"💡 未检测到偏好数据（冷启动），已按穿搭热门度为你推荐。")
            else:
                st.success(f"✅ 基于 **{algo_name}** 匹配，共推荐 **{len(results)}** 套穿搭")

            for i, (outfit, score) in enumerate(results, 1):
                col_info, col_score = st.columns([5, 1])
                with col_info:
                    st.markdown(f"**#{i} {outfit.name}**")
                    st.markdown("".join(f'<span class="tag-chip">{t}</span>'
                                        for t in outfit.tags[:6]),
                                unsafe_allow_html=True)
                with col_score:
                    label = "热门度" if is_cold else "相似度"
                    st.markdown(f'<div class="score-badge">{score:.2f}</div>'
                                f'<div style="color:#aaa;font-size:0.8rem">{label}</div>',
                                unsafe_allow_html=True)
                st.divider()

        else:
            st.info("在左侧配置标签和行为记录后点击「个性化推荐」。")
            st.markdown("""
**算法说明**

| 步骤 | 内容 |
|------|------|
| 显式画像 | 用户手动勾选标签，直接加入偏好集合 |
| 隐式画像 | 收藏行为权重×2，浏览行为权重×1；标签加权频次 ≥ 2.0 才纳入 |
| 画像合并 | merged = 显式 ∪ 隐式（自动去重） |
| 相似度 | 基础：J = \|A∩B\| / \|A∪B\|；加权：显式标签权重更高 |
| 冷启动 | 无偏好数据时，改用热门度降序兜底 |
""")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3：相似穿搭推荐（穿搭 → 穿搭，10高+10低）
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("穿搭详情页相似推荐（10高相似 + 10低相似）")
    st.markdown('<div class="section-note">算法：以目标穿搭标签为基准集，遍历计算杰卡德相似度 → 高相似度（≥阈值）前10套 + 低相似度（<阈值）前10套，各组内按相似度降序</div>', unsafe_allow_html=True)
    st.markdown("")

    all_outfits = load_outfits()
    outfit_name_map = {o.name: o.id for o in all_outfits}

    col_ctrl, col_res = st.columns([1, 3])

    with col_ctrl:
        selected_name = st.selectbox(
            "选择基准穿搭", list(outfit_name_map.keys()), key="similar_select")
        threshold = st.slider(
            "高/低相似度分界阈值", 0.0, 1.0, 0.3, 0.05, key="threshold")
        btn3 = st.button("🔍 查找相似穿搭", type="primary", key="btn3")

    with col_res:
        if btn3:
            target_id = outfit_name_map[selected_name]
            target_outfit = next(o for o in all_outfits if o.id == target_id)

            st.markdown(f"**基准穿搭：{target_outfit.name}**")
            st.markdown("".join(f'<span class="tag-chip">{t}</span>'
                                for t in target_outfit.tags),
                        unsafe_allow_html=True)
            st.divider()

            with st.spinner("计算相似度中..."):
                result = recommend_similar(
                    target_outfit_id=target_id,
                    outfits=all_outfits,
                    threshold=threshold,
                )

            high_list = result["high"]
            low_list  = result["low"]

            col_high, col_low = st.columns(2)

            with col_high:
                st.markdown(f"### 🔴 高相似（{len(high_list)} 套）")
                st.caption(f"相似度 ≥ {threshold}")
                if not high_list:
                    st.info("无高相似穿搭，可尝试降低阈值。")
                for outfit, score in high_list:
                    st.markdown(f"**{outfit.name}**  `{score:.2f}`")
                    st.markdown("".join(f'<span class="tag-chip">{t}</span>'
                                        for t in outfit.tags[:5]),
                                unsafe_allow_html=True)
                    st.markdown("---")

            with col_low:
                st.markdown(f"### 🔵 低相似（{len(low_list)} 套）")
                st.caption(f"相似度 < {threshold}")
                if not low_list:
                    st.info("无低相似穿搭。")
                for outfit, score in low_list:
                    st.markdown(f"**{outfit.name}**  `{score:.2f}`")
                    st.markdown("".join(f'<span class="tag-chip">{t}</span>'
                                        for t in outfit.tags[:5]),
                                unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info("在左侧选择基准穿搭后点击「查找相似穿搭」。")
            st.markdown("""
**说明**
- 高相似组：与基准穿搭标签重叠度高，适合作为同类替换推荐
- 低相似组：与基准穿搭风格差异大，适合作为对比或探索推荐
- 阈值可实时调整，影响高/低组的划分比例
""")
