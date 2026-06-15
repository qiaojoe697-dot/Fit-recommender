import pytest
from src.model import UserPreference
from src.recommender import filter_items, load_items, recommend


def test_load_items_has_reasonable_count():
    items = load_items()
    assert 10 <= len(items) <= 100


def test_load_items_has_all_categories():
    items = load_items()
    cats = {i.category for i in items}
    assert cats == {"top", "bottom", "shoes", "accessory"}


def test_load_items_tags_default_empty():
    """所有衣物都有 tags 字段（默认空列表）"""
    items = load_items()
    for item in items:
        assert isinstance(item.tags, list)


def test_filter_items_by_summer_casual():
    items = load_items()
    pref = UserPreference(season="summer", occasion="casual", style="casual")
    filtered = filter_items(items, pref)
    assert len(filtered) > 0
    for item in filtered:
        assert "summer" in item.season
        assert "casual" in item.occasion


def test_filter_items_by_winter_formal():
    items = load_items()
    pref = UserPreference(season="winter", occasion="formal", style="formal")
    filtered = filter_items(items, pref)
    assert len(filtered) > 0
    for item in filtered:
        assert "winter" in item.season
        assert "formal" in item.occasion


def test_filter_items_date_occasion():
    """新增 date 场合能正确过滤"""
    items = load_items()
    pref = UserPreference(season="spring", occasion="date", style="casual")
    filtered = filter_items(items, pref)
    assert len(filtered) > 0
    for item in filtered:
        assert "date" in item.occasion


def test_recommend_returns_outfits():
    pref = UserPreference(season="summer", occasion="casual", style="casual", top_n=3)
    outfits = recommend(pref)
    assert len(outfits) > 0
    assert len(outfits) <= 3
    for outfit in outfits:
        assert len(outfit.items) >= 3
        assert outfit.score > 0


def test_recommend_has_style_tip():
    """每个搭配都应有穿搭建议"""
    pref = UserPreference(season="summer", occasion="casual", style="casual", top_n=2)
    outfits = recommend(pref)
    for outfit in outfits:
        assert isinstance(outfit.style_tip, str)
        assert len(outfit.style_tip) > 0


def test_recommend_scores_descending():
    pref = UserPreference(season="summer", occasion="casual", style="casual", top_n=5)
    outfits = recommend(pref)
    scores = [o.score for o in outfits]
    assert scores == sorted(scores, reverse=True)


def test_recommend_winter_formal():
    pref = UserPreference(season="winter", occasion="formal", style="formal", top_n=3)
    outfits = recommend(pref)
    assert len(outfits) > 0
    for outfit in outfits:
        assert outfit.score > 0


def test_recommend_date_occasion():
    """约会场合能正常推荐"""
    pref = UserPreference(season="spring", occasion="date", style="casual", top_n=3)
    outfits = recommend(pref)
    assert len(outfits) > 0


def test_recommend_empty_for_no_match():
    pref = UserPreference(season="winter", occasion="sporty", style="sporty")
    outfits = recommend(pref)
    assert isinstance(outfits, list)
    assert len(outfits) == 0


def test_recommend_top_n_respected():
    pref = UserPreference(season="summer", occasion="casual", style="casual", top_n=1)
    outfits = recommend(pref)
    assert len(outfits) <= 1


def test_recommend_with_color_preference():
    """颜色偏好不影响正常推荐流程"""
    pref = UserPreference(
        season="autumn", occasion="casual", style="casual",
        color_preference="black", top_n=3,
    )
    outfits = recommend(pref)
    assert len(outfits) > 0
