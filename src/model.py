from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ClothingItem:
    """一件可推荐的衣物"""

    id: str
    name: str
    category: str  # top / bottom / shoes / accessory
    colors: List[str]  # e.g. ["white", "blue"]
    style: str  # casual / formal / sporty / street
    season: List[str]  # e.g. ["spring", "summer"]
    occasion: List[str]  # e.g. ["casual", "business"]


@dataclass
class Outfit:
    """一套完整的穿搭推荐"""

    items: List[ClothingItem]
    score: float
    reason: str = ""


@dataclass
class UserPreference:
    """用户的查询条件"""

    season: str
    occasion: str
    style: str
    color_preference: str | None = None
    top_n: int = 3
