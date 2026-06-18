from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set


@dataclass
class ClothingItem:
    """一件可推荐的衣物"""
    id: str
    name: str
    category: str        # top / bottom / shoes / accessory
    colors: List[str]
    style: str           # casual / formal / sporty / street
    season: List[str]
    occasion: List[str]  # casual / business / formal / sporty / date
    tags: List[str] = field(default_factory=list)

    def tag_set(self) -> Set[str]:
        """返回该单品所有标签的集合（style + season + occasion + tags）"""
        return set(self.tags) | {self.style} | set(self.season) | set(self.occasion)


@dataclass
class OutfitRecord:
    """穿搭记录（来自数据库或静态 JSON）"""
    id: str
    name: str
    tags: List[str]      # 穿搭本身携带的标签集合
    popularity: int = 0  # 热门度分数，用于冷启动排序

    def tag_set(self) -> Set[str]:
        return set(self.tags)


@dataclass
class UserBehavior:
    """用户行为记录（用于构建隐式画像）"""
    outfit_id: str
    action: str          # "view" / "like"
    weight: float = 1.0  # view=1.0, like=2.0（收藏权重更高）


@dataclass
class UserProfile:
    """
    完整用户画像
    - explicit_tags: 用户手动勾选的标签（显式）
    - implicit_tags: 从行为中挖掘的高频标签（隐式）
    merged_tags = explicit_tags | implicit_tags（去重合并）
    """
    user_id: str
    explicit_tags: Set[str] = field(default_factory=set)
    implicit_tags: Set[str] = field(default_factory=set)

    @property
    def merged_tags(self) -> Set[str]:
        return self.explicit_tags | self.implicit_tags


@dataclass
class Outfit:
    """推荐引擎输出的搭配结果（ClothingItem 组合，供 Streamlit UI 使用）"""
    items: List[ClothingItem]
    score: float
    reason: str = ""
    style_tip: str = ""


@dataclass
class UserPreference:
    """Streamlit UI / CLI 传入的偏好条件（保持向后兼容）"""
    season: str
    occasion: str
    style: str
    color_preference: Optional[str] = None
    top_n: int = 3
    gender: Optional[str] = None
