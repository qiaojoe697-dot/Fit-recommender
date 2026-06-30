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
# 颜色搭配知识库（用于套装颜色和谐度加成）
# 基于时尚搭配常识，不是颜色越接近分越高，而是经典搭配分高
# 分值：1.0 = 绝配，0.9 = 非常搭，0.8 = 很搭，0.7 = 还不错
#       0.6 = 一般，0.5 = 同色/不太搭，0.4 = 有点冲突，0.3 = 踩雷
# ---------------------------------------------------------------------------
_COLOR_HARMONY_KB: Dict[str, Dict[str, float]] = {
    "white": {
        "white": 0.5,    # 全白略显单调
        "black": 1.0,    # 黑白经典，永不过时
        "gray": 0.9,     # 白灰高级感
        "blue": 1.0,     # 白蓝清新，夏日首选
        "navy": 1.0,     # 白+藏青，通勤经典
        "beige": 0.9,    # 米白温柔
        "khaki": 0.8,    # 白卡其，休闲风
        "brown": 0.7,    # 白棕复古
        "silver": 0.9,   # 白银科技感
        "red": 0.9,      # 白红醒目
        "pink": 0.9,     # 白粉甜美
        "green": 0.7,    # 白绿清新
        "gold": 0.9,     # 白金贵气
        "purple": 0.8,   # 白紫梦幻
        "orange": 0.7,   # 白橙活力
    },
    "black": {
        "white": 1.0,    # 黑白经典
        "black": 0.6,    # 全黑需要靠材质层次
        "gray": 0.8,     # 黑灰沉稳
        "blue": 0.7,     # 黑蓝一般
        "navy": 0.7,     # 黑藏青太暗沉
        "beige": 0.6,    # 黑米还行
        "khaki": 0.5,    # 黑卡其一般
        "brown": 0.6,    # 黑棕复古
        "silver": 0.9,   # 黑银科技感
        "red": 1.0,      # 黑红绝配，高级感拉满
        "pink": 0.6,     # 黑粉有点冲突
        "green": 0.5,    # 黑绿一般
        "gold": 1.0,     # 黑金YYDS，奢华感
        "purple": 0.8,   # 黑紫神秘
        "orange": 0.6,   # 黑橙运动风
    },
    "gray": {
        "white": 0.9,    # 灰白高级
        "black": 0.8,    # 灰黑沉稳
        "gray": 0.5,     # 同色单调
        "blue": 0.8,     # 灰蓝商务
        "navy": 0.8,     # 灰藏青高级
        "beige": 0.7,    # 灰米温柔
        "khaki": 0.6,    # 灰卡其一般
        "brown": 0.6,    # 灰棕一般
        "silver": 0.9,   # 灰银高级
        "red": 0.5,      # 灰红一般
        "pink": 0.6,     # 灰粉还行
        "green": 0.5,    # 灰绿一般
        "gold": 0.6,     # 灰金还行
        "purple": 0.6,   # 灰紫还行
        "orange": 0.5,   # 灰橙一般
    },
    "blue": {
        "white": 1.0,    # 蓝白清新
        "black": 0.7,    # 蓝黑一般
        "gray": 0.8,     # 蓝灰商务
        "blue": 0.5,     # 全蓝单调
        "navy": 0.7,     # 蓝+藏青有层次
        "beige": 0.7,    # 蓝米还行
        "khaki": 0.8,    # 蓝卡其美式休闲
        "brown": 0.6,    # 蓝棕一般
        "silver": 0.8,   # 蓝银清爽
        "red": 0.5,      # 蓝红有点撞
        "pink": 0.6,     # 蓝粉还行
        "green": 0.5,    # 蓝绿一般
        "gold": 0.7,     # 蓝金还行
        "purple": 0.6,   # 蓝紫还行
        "orange": 0.4,   # 蓝橙撞色，有人爱有人嫌
    },
    "navy": {
        "white": 1.0,    # 藏青+白，通勤经典
        "black": 0.7,    # 藏青+黑太暗沉
        "gray": 0.8,     # 藏青+灰高级
        "blue": 0.7,     # 藏青+蓝有层次
        "navy": 0.5,     # 同色
        "beige": 0.8,    # 藏青+米温柔
        "khaki": 0.9,    # 藏青+卡其，工装风绝配
        "brown": 0.7,    # 藏青+棕复古
        "silver": 0.7,   # 藏青+银还行
        "red": 0.8,      # 藏青+红，学院风
        "pink": 0.5,     # 藏青+粉一般
        "green": 0.6,    # 藏青+绿一般
        "gold": 0.8,     # 藏青+金高级感
        "purple": 0.5,   # 藏青+紫一般
        "orange": 0.5,   # 藏青+橙一般
    },
    "beige": {
        "white": 0.9,    # 米白温柔
        "black": 0.6,    # 米黑还行
        "gray": 0.7,     # 米灰温柔
        "blue": 0.7,     # 米蓝还行
        "navy": 0.8,     # 米+藏青温柔
        "beige": 0.5,    # 同色
        "khaki": 0.9,    # 米+卡其，大地色系
        "brown": 0.9,    # 米棕温柔治愈
        "silver": 0.5,   # 米银一般
        "red": 0.5,      # 米红一般
        "pink": 0.8,     # 米粉温柔甜美
        "green": 0.6,    # 米绿清新
        "gold": 0.7,     # 米金高级感
        "purple": 0.5,   # 米紫一般
        "orange": 0.6,   # 米橙活力
    },
    "khaki": {
        "white": 0.8,    # 卡其+白休闲
        "black": 0.5,    # 卡其+黑一般
        "gray": 0.6,     # 卡其+灰还行
        "blue": 0.8,     # 卡其+蓝，经典美式
        "navy": 0.9,     # 卡其+藏青，工装风
        "beige": 0.9,    # 卡其+米，大地色系
        "khaki": 0.5,    # 同色
        "brown": 0.9,    # 卡其+棕，复古感
        "silver": 0.5,   # 卡其+银一般
        "red": 0.5,      # 卡其+红一般
        "pink": 0.4,     # 卡其+粉有点怪
        "green": 1.0,    # 卡其+绿，军风/工装绝配
        "gold": 0.7,     # 卡其+金还行
        "purple": 0.4,   # 卡其+紫有点怪
        "orange": 0.8,   # 卡其+橙活力满满
    },
    "brown": {
        "white": 0.7,    # 棕白复古
        "black": 0.6,    # 棕黑还行
        "gray": 0.6,     # 棕灰一般
        "blue": 0.6,     # 棕蓝一般
        "navy": 0.7,     # 棕+藏青复古
        "beige": 0.9,    # 棕+米温柔
        "khaki": 0.9,    # 棕+卡其复古
        "brown": 0.5,    # 同色
        "silver": 0.4,   # 棕银不太搭
        "red": 0.5,      # 棕红一般
        "pink": 0.4,     # 棕粉有点怪
        "green": 0.5,    # 棕绿复古
        "gold": 0.7,     # 棕金复古高级
        "purple": 0.4,   # 棕紫不太搭
        "orange": 0.7,   # 棕橙暖色调
    },
    "silver": {
        "white": 0.9,    # 银白科技感
        "black": 0.9,    # 银黑高级
        "gray": 0.9,     # 银灰高级
        "blue": 0.8,     # 银蓝清爽
        "navy": 0.7,     # 银藏青还行
        "beige": 0.5,    # 银米一般
        "khaki": 0.5,    # 银卡其一般
        "brown": 0.4,    # 银棕不太搭
        "silver": 0.5,   # 同色
        "red": 0.6,      # 银红还行
        "pink": 0.6,     # 银粉还行
        "green": 0.4,    # 银绿不太搭
        "gold": 0.5,     # 金银有点冲突
        "purple": 0.6,   # 银紫还行
        "orange": 0.4,   # 银橙不太搭
    },
    "red": {
        "white": 0.9,    # 红白醒目
        "black": 1.0,    # 红黑绝配，高级感
        "gray": 0.5,     # 红灰一般
        "blue": 0.5,     # 红蓝撞色
        "navy": 0.8,     # 红+藏青，学院风
        "beige": 0.5,    # 红米一般
        "khaki": 0.5,    # 红卡其一般
        "brown": 0.5,    # 红棕一般
        "silver": 0.6,   # 红银还行
        "red": 0.5,      # 同色太艳
        "pink": 0.5,     # 红粉有点冲
        "green": 0.3,    # 红绿圣诞感，容易踩雷
        "gold": 0.7,     # 红金喜庆
        "purple": 0.5,   # 红紫一般
        "orange": 0.4,   # 红橙太艳
    },
    "pink": {
        "white": 0.9,    # 粉白甜美
        "black": 0.6,    # 粉黑有点冲突
        "gray": 0.6,     # 粉灰还行
        "blue": 0.6,     # 粉蓝还行
        "navy": 0.5,     # 粉藏青一般
        "beige": 0.8,    # 粉米温柔
        "khaki": 0.4,    # 粉卡其有点怪
        "brown": 0.4,    # 粉棕有点怪
        "silver": 0.6,   # 粉银还行
        "red": 0.5,      # 粉红有点冲
        "pink": 0.5,     # 同色太甜
        "green": 0.3,    # 粉绿土，踩雷
        "gold": 0.6,     # 粉金还行
        "purple": 0.7,   # 粉紫温柔
        "orange": 0.4,   # 粉橙太艳
    },
    "green": {
        "white": 0.7,    # 绿白清新
        "black": 0.5,    # 绿黑一般
        "gray": 0.5,     # 绿灰一般
        "blue": 0.5,     # 绿蓝一般
        "navy": 0.6,     # 绿藏青还行
        "beige": 0.6,    # 绿米清新
        "khaki": 1.0,    # 绿+卡其，工装风绝配
        "brown": 0.5,    # 绿棕复古
        "silver": 0.4,   # 绿银不太搭
        "red": 0.3,      # 绿红圣诞，踩雷
        "pink": 0.3,     # 绿粉土，踩雷
        "green": 0.5,    # 同色
        "gold": 0.6,     # 绿金复古
        "purple": 0.4,   # 绿紫一般
        "orange": 0.5,   # 绿橙一般
    },
    "gold": {
        "white": 0.9,    # 金白贵气
        "black": 1.0,    # 黑金奢华，绝配
        "gray": 0.6,     # 金灰还行
        "blue": 0.7,     # 金蓝还行
        "navy": 0.8,     # 金+藏青高级
        "beige": 0.7,    # 金米高级
        "khaki": 0.7,    # 金卡其还行
        "brown": 0.7,    # 金棕复古
        "silver": 0.5,   # 金银有点冲突
        "red": 0.7,      # 金红喜庆
        "pink": 0.6,     # 金粉还行
        "green": 0.6,    # 金绿复古
        "gold": 0.5,     # 同色太闪
        "purple": 0.6,   # 紫金华丽
        "orange": 0.7,   # 金橙暖色调
    },
    "purple": {
        "white": 0.8,    # 紫白梦幻
        "black": 0.8,    # 紫黑神秘
        "gray": 0.6,     # 紫灰还行
        "blue": 0.6,     # 紫蓝还行
        "navy": 0.5,     # 紫藏青一般
        "beige": 0.5,    # 紫米一般
        "khaki": 0.4,    # 紫卡其有点怪
        "brown": 0.4,    # 紫棕不太搭
        "silver": 0.6,   # 紫银还行
        "red": 0.5,      # 紫红一般
        "pink": 0.7,     # 紫粉温柔
        "green": 0.4,    # 紫绿一般
        "gold": 0.6,     # 紫金华丽
        "purple": 0.5,   # 同色
        "orange": 0.3,   # 紫橙撞色，踩雷
    },
    "orange": {
        "white": 0.7,    # 橙白活力
        "black": 0.6,    # 橙黑运动风
        "gray": 0.5,     # 橙灰一般
        "blue": 0.4,     # 橙蓝撞色
        "navy": 0.5,     # 橙藏青一般
        "beige": 0.6,    # 橙米活力
        "khaki": 0.8,    # 橙+卡其活力
        "brown": 0.7,    # 橙棕暖色调
        "silver": 0.4,   # 橙银不太搭
        "red": 0.4,      # 橙红太艳
        "pink": 0.4,     # 橙粉太艳
        "green": 0.5,    # 橙绿一般
        "gold": 0.7,     # 橙金暖
        "purple": 0.3,   # 橙紫撞色，踩雷
        "orange": 0.5,   # 同色
    },
}

# ---------------------------------------------------------------------------
# 材质-季节适配度（新增打分维度）
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
# 材质、标签相关函数（新增）
# ===========================================================================

def material_season_fit(material: str, season: str) -> float:
    """材质与季节的适配度 [0, 1]"""
    row = _MATERIAL_SEASON_FIT.get(material, {})
    return row.get(season, 0.6)  # 未知材质给中性分


def tag_match_score(item_tags: List[str], pref_tags: List[str]) -> float:
    """标签匹配度：重合标签数 / 用户偏好标签数"""
    if not pref_tags:
        return 0.5  # 无偏好标签时给中性分
    if not item_tags:
        return 0.0
    overlap = len(set(item_tags) & set(pref_tags))
    return overlap / len(pref_tags)


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
    权重说明：
      style      ×2.5  风格最重要，决定整体气质
      occasion   ×2.0  场合必须匹配
      season     ×1.5  季节匹配
      color      ×1.5  颜色偏好
      material   ×1.0  材质季节适配
      tags       ×1.0  语义标签匹配
      popularity ×0.5  热门度参考
    """
    score = 0.0
    
    # 风格精确匹配 (权重 2.5)
    score += _match_score(item.style, pref.style) * 2.5
    
    # 场合匹配 (权重 2.0)
    score += _overlap_score(item.occasion, pref.occasion) * 2.0
    
    # 季节匹配 (权重 1.5)
    score += _overlap_score(item.season, pref.season) * 1.5
    
    # 颜色偏好匹配 (权重 1.5)
    score += best_color_match(item.colors, pref.color_preference) * 1.5
    
    # 材质季节适配 (权重 1.0) —— 新增
    score += material_season_fit(item.material, pref.season) * 1.0
    
    # 标签匹配 (权重 1.0) —— 新增
    score += tag_match_score(item.tags, pref.tag_preferences) * 1.0
    
    # 热门度 (权重 0.5) —— 新增，归一化到 [0,1]
    score += (item.popularity / 100.0) * 0.5
    
    return score
