import json
from pathlib import Path

from src.model import ClothingItem, Outfit, UserPreference

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_clothing_item_creation():
    item = ClothingItem(
        id="test-001",
        name="测试衣物",
        category="top",
        colors=["white"],
        style="casual",
        season=["spring", "summer"],
        occasion=["casual"],
    )
    assert item.id == "test-001"
    assert item.category == "top"
    assert "spring" in item.season


def test_outfit_creation():
    item = ClothingItem(
        id="test-001",
        name="测试衣物",
        category="top",
        colors=["white"],
        style="casual",
        season=["spring"],
        occasion=["casual"],
    )
    outfit = Outfit(items=[item], score=0.85, reason="测试搭配")
    assert outfit.score == 0.85
    assert len(outfit.items) == 1


def test_user_preference_defaults():
    pref = UserPreference(season="summer", occasion="casual", style="street")
    assert pref.top_n == 3
    assert pref.color_preference is None


def test_items_json_loadable():
    path = DATA_DIR / "items.json"
    assert path.exists(), f"{path} not found"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) > 0, "items.json is empty"
    for item in data:
        assert "id" in item
        assert "name" in item
        assert "category" in item
        assert "colors" in item
        assert "style" in item
        assert "season" in item
        assert "occasion" in item


def test_demo_outfits_json_loadable():
    path = DATA_DIR / "demo_outfits.json"
    assert path.exists(), f"{path} not found"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) > 0
    for outfit in data:
        assert "items" in outfit
        assert "reason" in outfit
        assert len(outfit["items"]) >= 2


def test_items_json_has_variety():
    path = DATA_DIR / "items.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    categories = {item["category"] for item in data}
    assert "top" in categories
    assert "bottom" in categories
    assert "shoes" in categories
