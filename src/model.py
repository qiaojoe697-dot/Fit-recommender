from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ClothingItem:
    """一件可推荐的衣物"""

    id: str
    name: str
    category: str        # top / bottom / shoes / accessory
    colors: List[str]    # e.g. ["white", "blue"]
    style: str           # casual / formal / sporty / street
    season: List[str]    # e.g. ["spring", "summer"]
    occasion: List[str]  # e.g. ["casual", "business", "date"]
    tags: List[str] = field(default_factory=list)  # 可选标签，如 ["oversized", "vintage"]


@dataclass
class Outfit:
    """一套完整的穿搭推荐"""

    items: List[ClothingItem]
    score: float
    reason: str = ""
    style_tip: str = ""   # 额外的穿搭建议


@dataclass
class UserPreference:
    """用户的查询条件"""

    season: str
    occasion: str
    style: str
    color_preference: Optional[str] = None
    top_n: int = 3
    gender: Optional[str] = None   # female / male / unisex（为未来扩展预留）
