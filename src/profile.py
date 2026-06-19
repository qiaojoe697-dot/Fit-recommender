"""
profile.py — 用户画像构建 + 杰卡德相似度计算

完整实现文档「二、用户画像构成」与「三、相似度计算方法」：

  1. build_implicit_tags()  — 从行为记录提取高频隐式标签
  2. build_user_profile()   — 合并显式 + 隐式 → UserProfile
  3. jaccard_similarity()   — 基础杰卡德相似度 J(A,B) = |A∩B| / |A∪B|
  4. weighted_jaccard()     — 加权杰卡德相似度（显式权重 w1 > 隐式权重 w2）
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Set

from src.model import OutfitRecord, UserBehavior, UserProfile

# ── 配置常量 ──────────────────────────────────────────────────────────────────

# 行为权重：收藏 > 浏览（对应文档「二、隐式画像」说明）
_ACTION_WEIGHTS: Dict[str, float] = {
    "view": 1.0,   # 浏览：轻度兴趣信号
    "like": 2.0,   # 收藏：强偏好信号
}

# 隐式画像入选阈值：标签加权频次必须达到此值
_IMPLICIT_FREQ_THRESHOLD = 2.0

# 加权杰卡德默认权重（对应文档「三、加权杰卡德」w1=2, w2=1）
DEFAULT_EXPLICIT_WEIGHT = 2.0
DEFAULT_IMPLICIT_WEIGHT = 1.0


# ── 1. 隐式画像构建 ───────────────────────────────────────────────────────────

def build_implicit_tags(
    behaviors: List[UserBehavior],
    outfit_map: Dict[str, OutfitRecord],
    freq_threshold: float = _IMPLICIT_FREQ_THRESHOLD,
) -> Set[str]:
    """
    从用户行为记录中提取高频标签，作为隐式画像。

    对应文档「二、2. 隐式画像」：
      - 统计用户浏览/收藏行为对应穿搭的标签出现频次
      - 选取高频标签（频次 >= freq_threshold）生成隐性偏好

    算法步骤：
      1. 遍历每条行为，找到对应穿搭的标签集合
      2. 按行为权重（like×2, view×1）× 行为自带权重倍数 累加标签频次
      3. 筛选频次 >= freq_threshold 的标签，纳入隐式画像

    Args:
        behaviors      : 用户行为列表
        outfit_map     : outfit_id → OutfitRecord 的映射字典
        freq_threshold : 入选隐式画像的最低加权频次，默认 2.0

    Returns:
        Set[str] — 隐式偏好标签集合
    """
    tag_counter: Counter = Counter()

    for behavior in behaviors:
        outfit = outfit_map.get(behavior.outfit_id)
        if outfit is None:
            continue  # 找不到对应穿搭时跳过，不报错
        # 行为类型权重 × 行为自带权重倍数
        weight = _ACTION_WEIGHTS.get(behavior.action, 1.0) * behavior.weight
        for tag in outfit.tag_set():
            tag_counter[tag] += weight

    return {tag for tag, freq in tag_counter.items() if freq >= freq_threshold}


# ── 2. 用户画像合并 ───────────────────────────────────────────────────────────

def build_user_profile(
    user_id: str,
    explicit_tags: Set[str],
    behaviors: List[UserBehavior],
    outfit_map: Dict[str, OutfitRecord],
    freq_threshold: float = _IMPLICIT_FREQ_THRESHOLD,
) -> UserProfile:
    """
    构建完整用户画像。

    对应文档「二、3. 合并规则」：
      merged_tags = explicit_tags ∪ implicit_tags（去重合并）

    Args:
        user_id       : 用户标识
        explicit_tags : 用户手动勾选的显式标签集合（来自个人中心）
        behaviors     : 用户浏览/收藏行为列表
        outfit_map    : 穿搭 ID → OutfitRecord 映射
        freq_threshold: 隐式标签入选阈值

    Returns:
        UserProfile（merged_tags = explicit ∪ implicit，自动去重）
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
    基础杰卡德相似度。

    对应文档「三、1. 基础公式」：
      J(A, B) = |A ∩ B| / |A ∪ B|

    取值范围 [0, 1]，越接近 1 越相似。
    两集合均为空时返回 0.0。

    示例（文档计算示例原文）：
      A = {休闲, 校园, 夏季}
      B = {休闲, 日常, 夏季}
      交集 = {休闲, 夏季}  → |A∩B| = 2
      并集 = {休闲,校园,夏季,日常} → |A∪B| = 4
      J = 2 / 4 = 0.5

    Args:
        set_a : 第一个标签集合
        set_b : 第二个标签集合

    Returns:
        float — 相似度值 [0, 1]
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
    加权杰卡德相似度（进阶版），区分显式/隐式标签权重。

    对应文档「三、2. 加权杰卡德相似度」：
      1. 设定权重：显式标签权重 w1，隐式标签权重 w2（w1 > w2）
      2. 统计显式重合数 N1、隐式重合数 N2
      3. 加权匹配得分 Score = w1 × N1 + w2 × N2
      4. J_加权 = Score / 总标签加权数

    计算细节：
      - implicit_only = implicit_tags - explicit_tags（避免标签重复计分）
      - 分母 = |explicit| × w1 + |implicit_only| × w2 + |穿搭未覆盖标签| × 1.0
      - 若用户无任何标签，返回 0.0（触发冷启动热门度排序）

    Args:
        profile      : 用户画像（含 explicit_tags / implicit_tags）
        outfit_tags  : 目标穿搭的标签集合
        w_explicit   : 显式标签权重，默认 2.0
        w_implicit   : 隐式标签权重，默认 1.0

    Returns:
        float — 加权相似度值 [0, 1]
    """
    if not profile.merged_tags:
        return 0.0  # 空画像 → 冷启动

    explicit = profile.explicit_tags
    # 隐式-only 集合：去除已在显式中的标签，避免重复计分
    implicit_only = profile.implicit_tags - profile.explicit_tags

    # 加权匹配分（分子）
    explicit_match = len(explicit & outfit_tags) * w_explicit
    implicit_match = len(implicit_only & outfit_tags) * w_implicit
    weighted_score = explicit_match + implicit_match

    # 加权总标签数（分母）
    weighted_total = len(explicit) * w_explicit + len(implicit_only) * w_implicit
    # 穿搭中用户画像未覆盖的标签，权重按 1.0 计入分母
    uncovered = len(outfit_tags - profile.merged_tags)
    denominator = weighted_total + uncovered

    return weighted_score / denominator if denominator > 0 else 0.0
