"""
model.py — 全系统数据结构定义

对应文档「二、用户画像构成」数据模型：
  - OutfitRecord   : 穿搭记录（来自 JSON 数据库）
  - UserBehavior   : 用户行为记录（浏览/收藏），用于构建隐式画像
  - UserProfile    : 完整用户画像（显式 + 隐式 + 合并）
  - ClothingItem   : 单品记录（供单品搭配推荐模块使用）
  - Outfit         : 单品搭配推荐输出结果
  - UserPreference : 单品搭配推荐的查询条件
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set


# ── 穿搭库相关 ────────────────────────────────────────────────────────────────

@dataclass
class OutfitRecord:
    """
    穿搭记录（来自 data/outfits.json 或外部 API）

    对应文档「一、数据表搭建」的穿搭表字段：
      id         : 穿搭唯一标识
      name       : 穿搭名称
      tags       : 穿搭标签集合（纯中文，如 ["休闲","夏季","校园"]）
      popularity : 热门度分数，用于冷启动排序
    """
    id: str
    name: str
    tags: List[str]
    popularity: int = 0

    def tag_set(self) -> Set[str]:
        """返回标签集合（去重），供杰卡德相似度计算使用"""
        return set(self.tags)


# ── 用户行为 & 画像 ───────────────────────────────────────────────────────────

@dataclass
class UserBehavior:
    """
    用户行为记录（对应文档「一、步骤2」的数据埋点）

    action : "view"（浏览）/ "like"（收藏）
    weight : 行为权重倍数（默认 1.0，外部可覆盖）
    """
    outfit_id: str
    action: str       # "view" / "like"
    weight: float = 1.0


@dataclass
class UserProfile:
    """
    完整用户画像（对应文档「二、用户画像构成」）

    explicit_tags : 用户主动勾选的标签（显式画像）
    implicit_tags : 从浏览/收藏行为中挖掘的高频标签（隐式画像）
    merged_tags   : 两者取并集去重，作为最终相似度计算输入
    """
    user_id: str
    explicit_tags: Set[str] = field(default_factory=set)
    implicit_tags: Set[str] = field(default_factory=set)

    @property
    def merged_tags(self) -> Set[str]:
        """显式 ∪ 隐式，自动去重"""
        return self.explicit_tags | self.implicit_tags

    def is_cold_start(self) -> bool:
        """是否为冷启动用户（无任何偏好数据）"""
        return len(self.merged_tags) == 0


# ── 单品搭配推荐相关 ──────────────────────────────────────────────────────────

@dataclass
class ClothingItem:
    """
    单件衣物数据（来自 data/items.json）
    category : top / bottom / shoes / accessory
    style    : casual / formal / sporty / street
    season   : 适用季节列表，如 ["spring", "summer"]
    occasion : 适用场合列表，如 ["casual", "date"]
    material : 材质，如 cotton/wool/denim/leather 等
    popularity : 热门度分数
    tags     : 可选语义标签列表，如 ["oversized"]
    """
    id: str
    name: str
    category: str
    colors: List[str]
    style: str
    season: List[str]
    occasion: List[str]
    material: str = "cotton"  # 新增：材质，默认棉质
    popularity: int = 50      # 新增：热门度，默认50
    tags: List[str] = field(default_factory=list)
    def tag_set(self) -> Set[str]:
        """返回该单品所有语义标签的集合"""
        return set(self.tags) | {self.style} | set(self.season) | set(self.occasion)


@dataclass
class Outfit:
    """单品搭配推荐结果"""
    items: List[ClothingItem]
    score: float
    reason: str = ""
    style_tip: str = ""


@dataclass
class UserPreference:
    """单品搭配推荐的查询条件"""
    season: str
    occasion: str
    style: str
    color_preference: Optional[str] = None
    tag_preferences: List[str] = field(default_factory=list)  # 新增：用户偏好标签
    top_n: int = 3
    gender: Optional[str] = None
