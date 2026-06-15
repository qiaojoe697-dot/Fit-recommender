from __future__ import annotations

from typing import Dict, List, Optional

from src.model import ClothingItem, UserPreference

# ---------------------------------------------------------------------------
# 颜色相似度矩阵（0=不搭, 1=完全一样）
# 新增：red, pink, green, navy, gold, purple, orange
# 基于色彩搭配常识与时尚规律定义
# ---------------------------------------------------------------------------
_COLOR_SIMILARITY: Dict[str, Dict[str, float]] = {
    "white": {
        "white": 1.0, "black": 0.7, "gray": 0.8, "blue": 0.8,
        "beige": 0.9, "khaki": 0.7, "brown": 0.6, "silver": 0.8,
        "red": 0.7, "pink": 0.8, "green": 0.6, "navy": 0.8,
        "gold": 0.7, "purple": 0.6, "orange": 0.6,
    },
    "black": {
        "white": 0.7, "black": 1.0, "gray": 0.8, "blue": 0.7,
        "beige": 0.6, "khaki": 0.5, "brown": 0.6, "silver": 0.8,
        "red": 0.8, "pink": 0.6, "green": 0.6, "navy": 0.7,
        "gold": 0.8, "purple": 0.7, "orange": 0.6,
    },
    "gray": {
        "white": 0.8, "black": 0.8, "gray": 1.0, "blue": 0.7,
        "beige": 0.7, "khaki": 0.6, "brown": 0.6, "silver": 0.9,
        "red": 0.5, "pink": 0.6, "green": 0.5, "navy": 0.7,
        "gold": 0.6, "purple": 0.6, "orange": 0.5,
    },
    "blue": {
        "white": 0.8, "black": 0.7, "gray": 0.7, "blue": 1.0,
        "beige": 0.6, "khaki": 0.7, "brown": 0.5, "silver": 0.6,
        "red": 0.5, "pink": 0.5, "green": 0.5, "navy": 0.8,
        "gold": 0.5, "purple": 0.6, "orange": 0.5,
    },
    "beige": {
        "white": 0.9, "black": 0.6, "gray": 0.7, "blue": 0.6,
        "beige": 1.0, "khaki": 0.8, "brown": 0.8, "silver": 0.5,
        "red": 0.5, "pink": 0.6, "green": 0.5, "navy": 0.6,
        "gold": 0.7, "purple": 0.5, "orange": 0.6,
    },
    "khaki": {
        "white": 0.7, "black": 0.5, "gray": 0.6, "blue": 0.7,
        "beige": 0.8, "khaki": 1.0, "brown": 0.8, "silver": 0.5,
        "red": 0.5, "pink": 0.4, "green": 0.7, "navy": 0.6,
        "gold": 0.6, "purple": 0.4, "orange": 0.6,
    },
    "brown": {
        "white": 0.6, "black": 0.6, "gray": 0.6, "blue": 0.5,
        "beige": 0.8, "khaki": 0.8, "brown": 1.0, "silver": 0.4,
        "red": 0.5, "pink": 0.4, "green": 0.5, "navy": 0.5,
        "gold": 0.7, "purple": 0.4, "orange": 0.7,
    },
    "silver": {
        "white": 0.8, "black": 0.8, "gray": 0.9, "blue": 0.6,
        "beige": 0.5, "khaki": 0.5, "brown": 0.4, "silver": 1.0,
        "red": 0.6, "pink": 0.6, "green": 0.4, "navy": 0.6,
        "gold": 0.5, "purple": 0.6, "orange": 0.4,
    },
    "red": {
        "white": 0.7, "black": 0.8, "gray": 0.5, "blue": 0.5,
        "beige": 0.5, "khaki": 0.5, "brown": 0.5, "silver": 0.6,
        "red": 1.0, "pink": 0.5, "green": 0.4, "navy": 0.7,
        "gold": 0.7, "purple": 0.5, "orange": 0.4,
    },
    "pink": {
        "white": 0.8, "black": 0.6, "gray": 0.6, "blue": 0.5,
        "beige": 0.6, "khaki": 0.4, "brown": 0.4, "silver": 0.6,
        "red": 0.5, "pink": 1.0, "green": 0.3, "navy": 0.5,
        "gold": 0.6, "purple": 0.6, "orange": 0.4,
    },
    "green": {
        "white": 0.6, "black": 0.6, "gray": 0.5, "blue": 0.5,
        "beige": 0.5, "khaki": 0.7, "brown": 0.5, "silver": 0.4,
        "red": 0.4, "pink": 0.3, "green": 1.0, "navy": 0.5,
        "gold": 0.6, "purple": 0.5, "orange": 0.5,
    },
    "navy": {
        "white": 0.8, "black": 0.7, "gray": 0.7, "blue": 0.8,
        "beige": 0.6, "khaki": 0.6, "brown": 0.5, "silver": 0.6,
        "red": 0.7, "pink": 0.5, "green": 0.5, "navy": 1.0,
        "gold": 0.6, "purple": 0.5, "orange": 0.5,
    },
    "gold": {
        "white": 0.7, "black": 0.8, "gray": 0.6, "blue": 0.5,
        "beige": 0.7, "khaki": 0.6, "brown": 0.7, "silver": 0.5,
        "red": 0.7, "pink": 0.6, "green": 0.6, "navy": 0.6,
        "gold": 1.0, "purple": 0.6, "orange": 0.7,
    },
    "purple": {
        "white": 0.6, "black": 0.7, "gray": 0.6, "blue": 0.6,
        "beige": 0.5, "khaki": 0.4, "brown": 0.4, "silver": 0.6,
        "red": 0.5, "pink": 0.6, "green": 0.5, "navy": 0.5,
        "gold": 0.6, "purple": 1.0, "orange": 0.4,
    },
    "orange": {
        "white": 0.6, "black": 0.6, "gray": 0.5, "blue": 0.5,
        "beige": 0.6, "khaki": 0.6, "brown": 0.7, "silver": 0.4,
        "red": 0.4, "pink": 0.4, "green": 0.5, "navy": 0.5,
        "gold": 0.7, "purple": 0.4, "orange": 1.0,
    },
}

# ---------------------------------------------------------------------------
# 风格兼容性矩阵：两种风格混搭时的和谐度
# 1.0 = 同款风格，0.0 = 完全不搭
# ---------------------------------------------------------------------------
_STYLE_COMPATIBILITY: Dict[str, Dict[str, float]] = {
    "casual":  {"casual": 1.0, "formal": 0.3, "sporty": 0.6, "street": 0.7},
    "formal":  {"casual": 0.3, "formal": 1.0, "sporty": 0.1, "street": 0.2},
    "sporty":  {"casual": 0.6, "formal": 0.1, "sporty": 1.0, "street": 0.5},
    "street":  {"casual": 0.7, "formal": 0.2, "sporty": 0.5, "street": 1.0},
}


def color_similarity(c1: str, c2: str) -> float:
    """返回两种颜色的搭配和谐度 [0, 1]"""
    row = _COLOR_SIMILARITY.get(c1, {})
    return row.get(c2, 0.0)


def best_color_match(item_colors: List[str], pref_color: Optional[str]) -> float:
    """衣物颜色与用户偏好色的最佳匹配分数"""
    if pref_color is None:
        return 0.5  # 无色偏好时给中性分
    if not item_colors:
        return 0.0
    return max(color_similarity(c, pref_color) for c in item_colors)


def outfit_color_harmony(items_colors: List[List[str]]) -> float:
    """
    计算一套搭配中所有单品之间的颜色整体和谐度。
    取所有两两组合的平均相似度。
    """
    if len(items_colors) < 2:
        return 0.5

    pairs = []
    for i in range(len(items_colors)):
        for j in range(i + 1, len(items_colors)):
            c1_list = items_colors[i]
            c2_list = items_colors[j]
            if not c1_list or not c2_list:
                continue
            # 取两件单品颜色间最高相似度
            best = max(
                color_similarity(c1, c2)
                for c1 in c1_list
                for c2 in c2_list
            )
            pairs.append(best)

    return sum(pairs) / len(pairs) if pairs else 0.5


def _match_score(item_value: str, pref_value: str) -> float:
    return 1.0 if item_value == pref_value else 0.0


def _overlap_score(item_list: List[str], pref_value: str) -> float:
    """pref_value 是否在 item 的列表字段中"""
    return 1.0 if pref_value in item_list else 0.0


def style_compatibility_score(style1: str, style2: str) -> float:
    """两种风格的搭配和谐度"""
    return _STYLE_COMPATIBILITY.get(style1, {}).get(style2, 0.0)


def compute_item_score(item: ClothingItem, pref: UserPreference) -> float:
    """
    计算单件衣物与用户偏好的匹配分。

    权重说明：
      style   ×2.5  风格最重要，决定整体气质
      occasion ×2.0  场合必须匹配
      season   ×1.0  季节匹配
      color    ×1.5  颜色偏好（比原来更重要）
    """
    score = 0.0

    # 风格精确匹配 (权重 2.5)
    score += _match_score(item.style, pref.style) * 2.5

    # 场合匹配 (权重 2.0)
    score += _overlap_score(item.occasion, pref.occasion) * 2.0

    # 季节匹配 (权重 1.0)
    score += _overlap_score(item.season, pref.season) * 1.0

    # 颜色偏好匹配 (权重 1.5)
    score += best_color_match(item.colors, pref.color_preference) * 1.5

    return score
