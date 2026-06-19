"""
test_profile.py — 测试用户画像构建与杰卡德相似度

覆盖文档「二、用户画像构成」与「三、相似度计算方法」全部逻辑。
"""
from src.model import OutfitRecord, UserBehavior, UserProfile
from src.profile import (
    build_implicit_tags,
    build_user_profile,
    jaccard_similarity,
    weighted_jaccard,
)

# ── 测试数据 ──────────────────────────────────────────────────────────────────

OUTFITS = {
    "o1": OutfitRecord("o1", "清新校园风",  ["休闲", "校园", "夏季"]),
    "o2": OutfitRecord("o2", "都市通勤",    ["商务", "通勤", "秋季"]),
    "o3": OutfitRecord("o3", "街头潮搭",    ["街头", "潮流", "休闲"]),
    "o4": OutfitRecord("o4", "约会浪漫",    ["约会", "浪漫", "春季"]),
}


# ── 1. 基础杰卡德相似度（对应文档「三、1. 基础公式」）────────────────────────

def test_jaccard_identical():
    """完全相同的集合，相似度应为 1.0"""
    assert jaccard_similarity({"a", "b"}, {"a", "b"}) == 1.0

def test_jaccard_no_overlap():
    """无交集，相似度应为 0.0"""
    assert jaccard_similarity({"a", "b"}, {"c", "d"}) == 0.0

def test_jaccard_partial_match():
    """文档原文计算示例：A={休闲,校园,夏季}, B={休闲,日常,夏季} → J=2/4=0.5"""
    a = {"休闲", "校园", "夏季"}
    b = {"休闲", "日常", "夏季"}
    assert jaccard_similarity(a, b) == 0.5

def test_jaccard_both_empty():
    """两集合均为空，返回 0.0"""
    assert jaccard_similarity(set(), set()) == 0.0

def test_jaccard_one_empty():
    """一个集合为空，返回 0.0"""
    assert jaccard_similarity({"a"}, set()) == 0.0

def test_jaccard_subset():
    """A 是 B 的子集，相似度应等于 |A|/|B|"""
    a = {"休闲", "夏季"}
    b = {"休闲", "夏季", "校园"}
    assert jaccard_similarity(a, b) == pytest_approx(2 / 3)

def test_jaccard_symmetry():
    """相似度应对称：J(A,B) == J(B,A)"""
    a = {"休闲", "校园"}
    b = {"校园", "夏季", "潮流"}
    assert jaccard_similarity(a, b) == jaccard_similarity(b, a)


# ── 2. 隐式画像构建（对应文档「二、2. 隐式画像」）──────────────────────────────

def test_build_implicit_tags_like_and_view():
    """
    收藏 o1 × 1 (权重2) + 浏览 o1 × 1 (权重1) → 休闲/校园/夏季 各累计 3.0 → 纳入
    浏览 o3 × 1 → 街头/潮流/休闲 各累计 1.0 → 低于阈值 2.0 → 不纳入
    """
    behaviors = [
        UserBehavior("o1", "like"),   # 休闲+2, 校园+2, 夏季+2
        UserBehavior("o1", "view"),   # 休闲+1, 校园+1, 夏季+1
        UserBehavior("o3", "view"),   # 街头+1, 潮流+1, 休闲+1
    ]
    implicit = build_implicit_tags(behaviors, OUTFITS, freq_threshold=2.0)
    assert "休闲" in implicit   # 2+1+1=4 ≥ 2
    assert "校园" in implicit   # 2+1=3 ≥ 2
    assert "夏季" in implicit   # 2+1=3 ≥ 2
    assert "街头" not in implicit  # 1 < 2
    assert "潮流" not in implicit  # 1 < 2

def test_build_implicit_tags_empty():
    """无行为时，隐式画像为空集"""
    assert build_implicit_tags([], OUTFITS) == set()

def test_build_implicit_tags_unknown_outfit():
    """行为对应穿搭不存在时，静默跳过不报错"""
    behaviors = [UserBehavior("nonexistent", "view")]
    assert build_implicit_tags(behaviors, OUTFITS) == set()

def test_build_implicit_tags_threshold_boundary():
    """恰好在阈值边界的标签应被纳入"""
    behaviors = [UserBehavior("o1", "like")]  # 每个标签累计 2.0
    implicit = build_implicit_tags(behaviors, OUTFITS, freq_threshold=2.0)
    assert "休闲" in implicit  # 2.0 == 2.0，应纳入

def test_build_implicit_tags_only_view_below_threshold():
    """单次浏览权重 1.0 < 默认阈值 2.0，不应纳入"""
    behaviors = [UserBehavior("o1", "view")]
    implicit = build_implicit_tags(behaviors, OUTFITS, freq_threshold=2.0)
    assert implicit == set()


# ── 3. 用户画像合并（对应文档「二、3. 合并规则」）──────────────────────────────

def test_build_user_profile_merged_contains_both():
    """合并画像应同时包含显式和隐式标签"""
    behaviors = [UserBehavior("o1", "like"), UserBehavior("o1", "like")]  # 累计4.0
    profile = build_user_profile("u1", {"商务"}, behaviors, OUTFITS, freq_threshold=2.0)
    assert "商务" in profile.explicit_tags
    assert "休闲" in profile.implicit_tags
    assert "商务" in profile.merged_tags
    assert "休闲" in profile.merged_tags

def test_build_user_profile_no_behaviors():
    """无行为时，合并画像等于显式画像"""
    profile = build_user_profile("u2", {"休闲", "夏季"}, [], OUTFITS)
    assert profile.merged_tags == {"休闲", "夏季"}
    assert profile.implicit_tags == set()

def test_build_user_profile_no_duplicate():
    """显式和隐式标签重叠时，合并后不重复计数"""
    behaviors = [UserBehavior("o1", "like"), UserBehavior("o1", "like")]
    profile = build_user_profile("u3", {"休闲"}, behaviors, OUTFITS, freq_threshold=2.0)
    # merged_tags 是集合，休闲只出现一次
    assert profile.merged_tags == profile.explicit_tags | profile.implicit_tags

def test_is_cold_start_true():
    """无任何标签时，is_cold_start 应为 True"""
    profile = UserProfile("u_cold")
    assert profile.is_cold_start() is True

def test_is_cold_start_false():
    """有显式标签时，is_cold_start 应为 False"""
    profile = UserProfile("u_active", explicit_tags={"休闲"})
    assert profile.is_cold_start() is False


# ── 4. 加权杰卡德（对应文档「三、2. 加权杰卡德」）──────────────────────────────

def test_weighted_jaccard_empty_profile():
    """空画像时加权杰卡德应返回 0.0"""
    profile = UserProfile("u1")
    assert weighted_jaccard(profile, {"休闲"}) == 0.0

def test_weighted_jaccard_no_overlap():
    """无任何标签重叠时应返回 0.0"""
    profile = UserProfile("u1", explicit_tags={"商务"}, implicit_tags=set())
    assert weighted_jaccard(profile, {"运动", "夏季"}) == 0.0

def test_weighted_jaccard_higher_than_basic():
    """显式标签完全匹配时，加权相似度应 ≥ 基础杰卡德（因为显式权重更高）"""
    profile = UserProfile("u1", explicit_tags={"休闲", "夏季"}, implicit_tags=set())
    outfit_tags = {"休闲", "夏季", "校园"}
    basic = jaccard_similarity(profile.merged_tags, outfit_tags)
    weighted = weighted_jaccard(profile, outfit_tags, w_explicit=2.0, w_implicit=1.0)
    assert weighted >= basic

def test_weighted_jaccard_w1_equals_w2_matches_basic():
    """当 w_explicit == w_implicit == 1 时，结果应与基础杰卡德一致"""
    profile = UserProfile("u1", explicit_tags={"休闲"}, implicit_tags={"夏季"})
    outfit_tags = {"休闲", "夏季", "校园"}
    basic = jaccard_similarity(profile.merged_tags, outfit_tags)
    weighted = weighted_jaccard(profile, outfit_tags, w_explicit=1.0, w_implicit=1.0)
    assert abs(weighted - basic) < 1e-9


# ── 5. outfit_recommender 集成测试 ──────────────────────────────────────────

def test_recommend_for_user_cold_start():
    """冷启动：无画像时应按热门度降序"""
    from src.outfit_recommender import recommend_for_user
    outfits = [
        OutfitRecord("o1", "A", ["休闲"], popularity=100),
        OutfitRecord("o2", "B", ["商务"], popularity=50),
    ]
    result = recommend_for_user(profile=None, outfits=outfits, top_n=2)
    assert len(result) == 2
    assert result[0][0].id == "o1"  # 热门度高的排前面

def test_recommend_for_user_with_profile():
    """有画像时应按相似度降序，即使热门度低"""
    from src.outfit_recommender import recommend_for_user
    outfits = [
        OutfitRecord("o1", "高相似", ["休闲", "夏季"], popularity=10),
        OutfitRecord("o2", "低相似", ["商务", "秋季"], popularity=200),
    ]
    profile = UserProfile("u1", explicit_tags={"休闲", "夏季"})
    result = recommend_for_user(profile=profile, outfits=outfits, top_n=2)
    assert result[0][0].id == "o1"  # 相似度高的排前面

def test_recommend_similar_high_low_split():
    """高相似和低相似分组应正确划分"""
    from src.outfit_recommender import recommend_similar
    outfits = [
        OutfitRecord("target", "目标", ["休闲", "夏季", "校园"]),
        OutfitRecord("o1",     "高相似", ["休闲", "夏季", "日常"]),
        OutfitRecord("o2",     "低相似", ["商务", "冬季", "正式"]),
    ]
    result = recommend_similar("target", outfits=outfits, threshold=0.3)
    high_ids = [o.id for o, _ in result["high"]]
    low_ids  = [o.id for o, _ in result["low"]]
    assert "o1" in high_ids
    assert "o2" in low_ids

def test_recommend_similar_missing_target():
    """目标穿搭不存在时，返回空结果"""
    from src.outfit_recommender import recommend_similar
    result = recommend_similar("nonexistent", outfits=[])
    assert result == {"high": [], "low": []}

def test_recommend_similar_excludes_self():
    """相似推荐结果不应包含目标穿搭自身"""
    from src.outfit_recommender import recommend_similar
    outfits = [
        OutfitRecord("target", "目标", ["休闲", "夏季"]),
        OutfitRecord("other",  "其他", ["休闲", "夏季"]),
    ]
    result = recommend_similar("target", outfits=outfits, threshold=0.0)
    all_ids = [o.id for o, _ in result["high"]] + [o.id for o, _ in result["low"]]
    assert "target" not in all_ids


# ── 辅助 ──────────────────────────────────────────────────────────────────────

def pytest_approx(v, rel=1e-6):
    """简单近似比较"""
    class _Approx:
        def __eq__(self, other): return abs(other - v) < rel
    return _Approx()
