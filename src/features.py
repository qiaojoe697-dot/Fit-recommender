from __future__ import annotations

from typing import Dict, List

from src.model import ClothingItem, UserPreference

# ---------------------------------------------------------------------------
# 颜色相似度矩阵（0=不相似, 1=完全一样）
# 基于色系和搭配常识定义
# ---------------------------------------------------------------------------
_COLOR_SIMILARITY: Dict[str, Dict[str, float]] = {
    "white":   {"white": 1.0, "black": 0.6, "gray": 0.7, "blue": 0.7, "beige": 0.8, "khaki": 0.7, "brown": 0.6, "silver": 0.7},
    "black":   {"white": 0.6, "black": 1.0, "gray": 0.8, "blue": 0.7, "beige": 0.5, "khaki": 0.5, "brown": 0.6, "silver": 0.7},
    "gray":    {"white": 0.7, "black": 0.8, "gray": 1.0, "blue": 0.6, "beige": 0.6, "khaki": 0.6, "brown": 0.6, "silver": 0.8},
    "blue":    {"white": 0.7, "black": 0.7, "gray": 0.6, "blue": 1.0, "beige": 0.5, "khaki": 0.6, "brown": 0.5, "silver": 0.5},
    "beige":   {"white": 0.8, "black": 0.5, "gray": 0.6, "blue": 0.5, "beige": 1.0, "khaki": 0.8, "brown": 0.7, "silver": 0.5},
    "khaki":   {"white": 0.7, "black": 0.5, "gray": 0.6, "blue": 0.6, "beige": 0.8, "khaki": 1.0, "brown": 0.7, "silver": 0.5},
    "brown":   {"white": 0.6, "black": 0.6, "gray": 0.6, "blue": 0.5, "beige": 0.7, "khaki": 0.7, "brown": 1.0, "silver": 0.5},
    "silver":  {"white": 0.7, "black": 0.7, "gray": 0.8, "blue": 0.5, "beige": 0.5, "khaki": 0.5, "brown": 0.5, "silver": 1.0},
}


def color_similarity(c1: str, c2: str) -> float:
    """返回两种颜色的相似度得分 [0, 1]"""
    row = _COLOR_SIMILARITY.get(c1, {})
    return row.get(c2, 0.0)


def best_color_match(item_colors: List[str], pref_color: str | None) -> float:
    """衣物颜色与用户偏好色的最佳匹配分数"""
    if pref_color is None:
        return 0.5  # 无色偏好时给中性分
    if not item_colors:
        return 0.0
    return max(color_similarity(c, pref_color) for c in item_colors)


def _match_score(item_value: str, pref_value: str) -> float:
    return 1.0 if item_value == pref_value else 0.0


def _overlap_score(item_list: List[str], pref_value: str) -> float:
    """pref_value 是否在 item 的列表字段中"""
    return 1.0 if pref_value in item_list else 0.0


def compute_item_score(item: ClothingItem, pref: UserPreference) -> float:
    """
    计算单件衣物与用户偏好的匹配分。
    分数越高越匹配。
    """
    score = 0.0

    # style 精确匹配 (权重 2)
    score += _match_score(item.style, pref.style) * 2.0

    # occasion 匹配 (权重 2)
    score += _overlap_score(item.occasion, pref.occasion) * 2.0

    # season 匹配 (权重 1)
    score += _overlap_score(item.season, pref.season) * 1.0

    # color 和谐度 (权重 1)
    score += best_color_match(item.colors, pref.color_preference) * 1.0

    return score
