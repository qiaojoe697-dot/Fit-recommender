"""
profile.py — 用户画像构建模块

实现文档「二、用户画像构成」与「三、相似度计算方法」全部逻辑：
  1. build_implicit_tags()  — 从行为记录中提取高频隐式标签
  2. build_user_profile()   — 合并显式 + 隐式 → UserProfile
  3. jaccard_similarity()   — 基础杰卡德相似度
  4. weighted_jaccard()     — 加权杰卡德相似度（区分显/隐标签）
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Set, Tuple

from src.model import OutfitRecord, UserBehavior, UserProfile

# 行为权重：收藏 > 浏览
_ACTION_WEIGHTS: Dict[str, float] = {
    "view": 1.0,
    "like": 2.0,
}

# 隐式画像：标签加权频次需达到此阈值才纳入画像
_IMPLICIT_FREQ_THRESHOLD = 2.0

# 加权杰卡德默认权重：显式 > 隐式
DEFAULT_EXPLICIT_WEIGHT = 2.0
DEFAULT_IMPLICIT_WEIGHT = 1.0


# ── 1. 隐式画像构建 ────────────────────────────────────────────────────────────

def build_implicit_tags(
    behaviors: List[UserBehavior],
    outfit_map: Dict[str, OutfitRecord],
    freq_threshold: float = _IMPLICIT_FREQ_THRESHOLD,
) -> Set[str]:
    """
    从用户行为中提取高频标签，作为隐式画像。

    步骤：
      1. 遍历每条行为，找到对应穿搭的标签集合
      2. 按行为权重（like > view）累加标签频次
      3. 筛选频次 >= freq_threshold 的标签

    参数：
      behaviors     : 用户行为列表
      outfit_map    : outfit_id → OutfitRecord 的映射字典
      freq_threshold: 入选隐式画像的最低加权频次
    """
    tag_counter: Counter = Counter()

    for behavior in behaviors:
        outfit = outfit_map.get(behavior.outfit_id)
        if outfit is None:
            continue
        weight = _ACTION_WEIGHTS.get(behavior.action, 1.0) * behavior.weight
        for tag in outfit.tag_set():
            tag_counter[tag] += weight

    return {tag for tag, freq in tag_counter.items() if freq >= freq_threshold}


# ── 2. 用户画像合并 ────────────────────────────────────────────────────────────

def build_user_profile(
    user_id: str,
    explicit_tags: Set[str],
    behaviors: List[UserBehavior],
    outfit_map: Dict[str, OutfitRecord],
    freq_threshold: float = _IMPLICIT_FREQ_THRESHOLD,
) -> UserProfile:
    """
    构建完整用户画像。

    - explicit_tags: 用户手动勾选的显式标签（来自个人中心）
    - behaviors:     用户浏览 / 收藏行为列表
    - outfit_map:    穿搭 ID → OutfitRecord 映射

    返回 UserProfile，其 merged_tags = explicit_tags | implicit_tags
    """
    implicit = build_implicit_tags(behaviors, outfit_map, freq_threshold)
    return UserProfile(
        user_id=user_id,
        explicit_tags=set(explicit_tags),
        implicit_tags=implicit,
    )


# ── 3. 基础杰卡德相似度 ───────────────────────────────────────────────────────

def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """
    J(A, B) = |A ∩ B| / |A ∪ B|

    返回值 [0, 1]，1 表示完全相同，0 表示无交集。
    若两个集合均为空，返回 0.0。

    示例：
      A = {休闲, 校园, 夏季}
      B = {休闲, 日常, 夏季}
      J = 2 / 4 = 0.5
    """
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


# ── 4. 加权杰卡德相似度 ───────────────────────────────────────────────────────

def weighted_jaccard(
    profile: UserProfile,
    outfit_tags: Set[str],
    w_explicit: float = DEFAULT_EXPLICIT_WEIGHT,
    w_implicit: float = DEFAULT_IMPLICIT_WEIGHT,
) -> float:
    """
    加权杰卡德相似度，区分显式 / 隐式标签权重。

    计算方式：
      1. 显式重合分  = |explicit_tags ∩ outfit_tags| × w_explicit
      2. 隐式重合分  = |implicit_only ∩ outfit_tags| × w_implicit
         （implicit_only = implicit_tags - explicit_tags，避免重复计算）
      3. 加权总匹配分 = 显式重合分 + 隐式重合分
      4. 加权总标签数 = |explicit_tags| × w_explicit + |implicit_only| × w_implicit
      5. J_加权 = 加权总匹配分 / (加权总标签数 + |outfit_tags - merged_tags|)

    若用户无任何标签，退化为 0.0（触发冷启动热门度排序）。
    """
    if not profile.merged_tags:
        return 0.0

    explicit = profile.explicit_tags
    implicit_only = profile.implicit_tags - profile.explicit_tags  # 去重

    # 加权匹配分
    explicit_match = len(explicit & outfit_tags) * w_explicit
    implicit_match = len(implicit_only & outfit_tags) * w_implicit
    weighted_score = explicit_match + implicit_match

    # 加权总标签分母
    weighted_total = len(explicit) * w_explicit + len(implicit_only) * w_implicit
    # 穿搭中用户画像未覆盖的标签（贡献分母，权重 1.0）
    uncovered = len(outfit_tags - profile.merged_tags)
    denominator = weighted_total + uncovered

    return weighted_score / denominator if denominator > 0 else 0.0
