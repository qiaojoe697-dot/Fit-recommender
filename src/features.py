from __future__ import annotations
from typing import Dict, List, Optional
from src.model import ClothingItem, UserPreference

# ---------------------------------------------------------------------------
# 颜色相似度矩阵（用于单品颜色偏好匹配）
# 0=不搭, 1=完全一样
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
        "white": 0.6, "black": 0.5, "gray": 0.5, "blue": 0.5,
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
# 颜色搭配知识库（用于套装颜色和谐度加成）
# 基于时尚搭配常识，不是颜色越接近分越高，而是经典搭配分高
# 分值：1.0 = 绝配，0.9 = 非常搭，0.8 = 很搭，0.7 = 还不错
#       0.6 = 一般，0.5 = 同色/不太搭，0.4 = 有点冲突，0.3 = 踩雷
# ---------------------------------------------------------------------------
_COLOR_HARMONY_KB: Dict[str, Dict[str, float]] = {
    "white": {
        "white": 0.5, "black": 1.0, "gray": 0.9, "blue": 1.0,
        "navy": 1.0, "beige": 0.9, "khaki": 0.8, "brown": 0.7,
        "silver": 0.9, "red": 0.9, "pink": 0.9, "green": 0.7,
        "gold": 0.9, "purple": 0.8, "orange": 0.7,
    },
    "black": {
        "white": 1.0, "black": 0.6, "gray": 0.8, "blue": 0.7,
        "navy": 0.7, "beige": 0.6, "khaki": 0.5, "brown": 0.6,
        "silver": 0.9, "red": 1.0, "pink": 0.6, "green": 0.5,
        "gold": 1.0, "purple": 0.8, "orange": 0.6,
    },
    "gray": {
        "white": 0.9, "black": 0.8, "gray": 0.5, "blue": 0.8,
        "navy": 0.8, "beige": 0.7, "khaki": 0.6, "brown": 0.6,
        "silver": 0.9, "red": 0.5, "pink": 0.6, "green": 0.5,
        "gold": 0.6, "purple": 0.6, "orange": 0.5,
    },
    "blue": {
        "white": 1.0, "black": 0.7, "gray": 0.8, "blue": 0.5,
        "navy": 0.7, "beige": 0.7, "khaki": 0.8, "brown": 0.6,
        "silver": 0.8, "red": 0.5, "pink": 0.6, "green": 0.5,
        "gold": 0.7, "purple": 0.6, "orange": 0.4,
    },
    "navy": {
        "white": 1.0, "black": 0.7, "gray": 0.8, "blue": 0.7,
        "navy": 0.5, "beige": 0.8, "khaki": 0.9, "brown": 0.7,
        "silver": 0.7, "red": 0.8, "pink": 0.5, "green": 0.6,
        "gold": 0.8, "purple": 0.5, "orange": 0.5,
    },
    "beige": {
        "white": 0.9, "black": 0.6, "gray": 0.7, "blue": 0.7,
        "navy": 0.8, "beige": 0.5, "khaki": 0.9, "brown": 0.9,
        "silver": 0.5, "red": 0.5, "pink": 0.8, "green": 0.6,
        "gold": 0.7, "purple": 0.5, "orange": 0.6,
    },
    "khaki": {
        "white": 0.8, "black": 0.5, "gray": 0.6, "blue": 0.8,
        "navy": 0.9, "beige": 0.9, "khaki": 0.5, "brown": 0.9,
        "silver": 0.5, "red": 0.5, "pink": 0.4, "green": 1.0,
        "gold": 0.7, "purple": 0.4, "orange": 0.8,
    },
    "brown": {
        "white": 0.7, "black": 0.6, "gray": 0.6, "blue": 0.6,
        "navy": 0.7, "beige": 0.9, "khaki": 0.9, "brown": 0.5,
        "silver": 0.4, "red": 0.5, "pink": 0.4, "green": 0.5,
        "gold": 0.7, "purple": 0.4, "orange": 0.7,
    },
    "silver": {
        "white": 0.9, "black": 0.9, "gray": 0.9, "blue": 0.8,
        "navy": 0.7, "beige": 0.5, "khaki": 0.5, "brown": 0.4,
        "silver": 0.5, "red": 0.6, "pink": 0.6, "green": 0.4,
        "gold": 0.5, "purple": 0.6, "orange": 0.4,
    },
    "red": {
        "white": 0.9, "black": 1.0, "gray": 0.5, "blue": 0.5,
        "navy": 0.8, "beige": 0.5, "khaki": 0.5, "brown": 0.5,
        "silver": 0.6, "red": 0.5, "pink": 0.5, "green": 0.3,
        "gold": 0.7, "purple": 0.5, "orange": 0.4,
    },
    "pink": {
        "white": 0.9, "black": 0.6, "gray": 0.6, "blue": 0.6,
        "navy": 0.5, "beige": 0.8, "khaki": 0.4, "brown": 0.4,
        "silver": 0.6, "red": 0.5, "pink": 0.5, "green": 0.3,
        "gold": 0.6, "purple": 0.7, "orange": 0.4,
    },
    "green": {
        "white": 0.7, "black": 0.5, "gray": 0.5, "blue": 0.5,
        "navy": 0.6, "beige": 0.6, "khaki": 1.0, "brown": 0.5,
        "silver": 0.4, "red": 0.3, "pink": 0.3, "green": 0.5,
        "gold": 0.6, "purple": 0.4, "orange": 0.5,
    },
    "gold": {
        "white": 0.9, "black": 1.0, "gray": 0.6, "blue": 0.7,
        "navy": 0.8, "beige": 0.7, "khaki": 0.7, "brown": 0.7,
        "silver": 0.5, "red": 0.7, "pink": 0.6, "green": 0.6,
        "gold": 0.5, "purple": 0.6, "orange": 0.7,
    },
    "purple": {
        "white": 0.8, "black": 0.8, "gray": 0.6, "blue": 0.6,
        "navy": 0.5, "beige": 0.5, "khaki": 0.4, "brown": 0.4,
        "silver": 0.6, "red": 0.5, "pink": 0.7, "green": 0.4,
        "gold": 0.6, "purple": 0.5, "orange": 0.3,
    },
    "orange": {
        "white": 0.7, "black": 0.6, "gray": 0.5, "blue": 0.4,
        "navy": 0.5, "beige": 0.6, "khaki": 0.8, "brown": 0.7,
        "silver": 0.4, "red": 0.4, "pink": 0.4, "green": 0.5,
        "gold": 0.7, "purple": 0.3, "orange": 0.5,
    },
}

# ---------------------------------------------------------------------------
# 材质-季节适配度（打分维度3）
# 轻薄材质适合夏天，厚重材质适合冬天
# ---------------------------------------------------------------------------
_MATERIAL_SEASON_FIT: Dict[str, Dict[str, float]] = {
    "cotton":    {"spring": 0.9, "summer": 1.0, "autumn": 0.8, "winter": 0.5},
    "linen":     {"spring": 0.8, "summer": 1.0, "autumn": 0.5, "winter": 0.2},
    "wool":      {"spring": 0.5, "summer": 0.2, "autumn": 0.8, "winter": 1.0},
    "knit":      {"spring": 0.6, "summer": 0.3, "autumn": 0.9, "winter": 1.0},
    "denim":     {"spring": 0.9, "summer": 0.7, "autumn": 0.9, "winter": 0.6},
    "leather":   {"spring": 0.6, "summer": 0.3, "autumn": 0.8, "winter": 0.9},
    "silk":      {"spring": 0.8, "summer": 1.0, "autumn": 0.6, "winter": 0.3},
    "polyester": {"spring": 0.8, "summer": 0.9, "autumn": 0.7, "winter": 0.5},
}

# ---------------------------------------------------------------------------
# 版型相似度矩阵（打分维度5，替代标签匹配）
# 版型之间的相似程度：完全一样得1分，接近的得0.6-0.8，差异大的得0.2-0.4
# ---------------------------------------------------------------------------
_FIT_SIMILARITY: Dict[str, Dict[str, float]] = {
    "oversized": {
        "oversized": 1.0,   # 宽松 = 宽松
        "regular":   0.6,   # 宽松 → 常规，有差异
        "slim":      0.3,   # 宽松 → 修身，差异大
        "skinny":    0.2,   # 宽松 → 紧身，差异很大
        "wide-leg":  0.8,   # 宽松 ↔ 阔腿，感觉接近
    },
    "regular": {
        "oversized": 0.6,
        "regular":   1.0,   # 常规 = 常规
        "slim":      0.7,   # 常规 → 修身，比较接近
        "skinny":    0.4,   # 常规 → 紧身，有差异
        "wide-leg":  0.5,   # 常规 → 阔腿，差异中等
    },
    "slim": {
        "oversized": 0.3,
        "regular":   0.7,
        "slim":      1.0,   # 修身 = 修身
        "skinny":    0.8,   # 修身 → 紧身，很接近
        "wide-leg":  0.2,   # 修身 → 阔腿，差异大
    },
    "skinny": {
        "oversized": 0.2,
        "regular":   0.4,
        "slim":      0.8,
        "skinny":    1.0,   # 紧身 = 紧身
        "wide-leg":  0.1,   # 紧身 → 阔腿，差异极大
    },
    "wide-leg": {
        "oversized": 0.8,
        "regular":   0.5,
        "slim":      0.2,
        "skinny":    0.1,
        "wide-leg":  1.0,   # 阔腿 = 阔腿
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


# ===========================================================================
# 颜色相关函数
# ===========================================================================

def color_similarity(c1: str, c2: str) -> float:
    """返回两种颜色的相似度 [0, 1]（用于单品颜色偏好匹配）"""
    row = _COLOR_SIMILARITY.get(c1, {})
    return row.get(c2, 0.0)


def color_harmony(c1: str, c2: str) -> float:
    """查颜色搭配知识库，返回两种颜色的搭配和谐度 [0, 1]（用于套装和谐度）"""
    if c1 == c2:
        return 0.5  # 同色不给高分，避免单调
    # 双向查找
    if c1 in _COLOR_HARMONY_KB and c2 in _COLOR_HARMONY_KB[c1]:
        return _COLOR_HARMONY_KB[c1][c2]
    if c2 in _COLOR_HARMONY_KB and c1 in _COLOR_HARMONY_KB[c2]:
        return _COLOR_HARMONY_KB[c2][c1]
    return 0.4  # 未知组合给中性偏低分


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
    基于「颜色搭配知识库」：统计所有颜色对中命中知识库的平均得分。
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
            # 取两件单品颜色间最高和谐度
            best = max(
                color_harmony(c1, c2)
                for c1 in c1_list
                for c2 in c2_list
            )
            pairs.append(best)
    
    return sum(pairs) / len(pairs) if pairs else 0.5


# ===========================================================================
# 材质、版型相关函数
# ===========================================================================

def material_season_fit(material: str, season: str) -> float:
    """材质与季节的适配度 [0, 1]"""
    row = _MATERIAL_SEASON_FIT.get(material, {})
    return row.get(season, 0.6)  # 未知材质给中性分


def fit_match_score(item_fit: str, pref_fit: Optional[str]) -> float:
    """
    版型匹配度：用户偏好版型与单品实际版型的相似度 [0, 1]
    替代原来的标签匹配，更具体、更有实际意义
    """
    if pref_fit is None:
        return 0.5  # 无版型偏好时给中性分
    row = _FIT_SIMILARITY.get(pref_fit, {})
    return row.get(item_fit, 0.3)  # 未知版型给偏低分


# ===========================================================================
# 风格、匹配辅助函数
# ===========================================================================

def _match_score(item_value: str, pref_value: str) -> float:
    return 1.0 if item_value == pref_value else 0.0


def _overlap_score(item_list: List[str], pref_value: str) -> float:
    """pref_value 是否在 item 的列表字段中"""
    return 1.0 if pref_value in item_list else 0.0


def style_compatibility_score(style1: str, style2: str) -> float:
    """两种风格的搭配和谐度"""
    return _STYLE_COMPATIBILITY.get(style1, {}).get(style2, 0.0)


# ===========================================================================
# 单品打分主函数（7维加权打分）
# ===========================================================================

def compute_item_score(item: ClothingItem, pref: UserPreference) -> float:
    """
    计算单件衣物与用户偏好的匹配分（7维加权打分）。
    
    7个维度及权重：
      ① 风格匹配      ×2.5  风格最重要，决定整体气质
      ② 场合匹配      ×2.0  场合必须匹配
      ③ 季节匹配      ×1.5  季节适配
      ④ 颜色匹配      ×1.5  颜色偏好
      ⑤ 材质季节适配  ×1.0  材质与季节的适配度
      ⑥ 版型匹配      ×1.0  版型偏好匹配（原标签匹配改为版型）
      ⑦ 热门度        ×0.5  参考大众选择
    """
    score = 0.0
    
    # ① 风格精确匹配 (权重 2.5)
    score += _match_score(item.style, pref.style) * 2.5
    
    # ② 场合匹配 (权重 2.0)
    score += _overlap_score(item.occasion, pref.occasion) * 2.0
    
    # ③ 季节匹配 (权重 1.5)
    score += _overlap_score(item.season, pref.season) * 1.5
    
    # ④ 颜色偏好匹配 (权重 1.5)
    score += best_color_match(item.colors, pref.color_preference) * 1.5
    
    # ⑤ 材质季节适配 (权重 1.0)
    score += material_season_fit(item.material, pref.season) * 1.0
    
    # ⑥ 版型匹配 (权重 1.0) —— 替代原来的标签匹配
    score += fit_match_score(item.fit, pref.fit_preference) * 1.0
    
    # ⑦ 热门度 (权重 0.5) —— 归一化到 [0,1]
    score += (item.popularity / 100.0) * 0.5
    
    return score
