import pytest

from src.model import UserPreference
from src.recommender import filter_items, load_items, recommend


def test_load_items_has_reasonable_count():
    items = load_items()
    assert 10 <= len(items) <= 50


def test_load_items_has_all_categories():
    items = load_items()
    cats = {i.category for i in items}
    assert cats == {"top", "bottom", "shoes", "accessory"}


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


def test_recommend_returns_outfits():
    pref = UserPreference(season="summer", occasion="casual", style="casual", top_n=3)
    outfits = recommend(pref)
    assert len(outfits) > 0
    assert len(outfits) <= 3
    for outfit in outfits:
        assert len(outfit.items) >= 3  # 至少 top + bottom + shoes
        assert outfit.score > 0


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


def test_recommend_empty_for_no_match():
    """当某个核心类别无候选衣物时返回空列表"""
    # winter + sporty: 有 top 和 bottom，但 shoes 为空 → 无法搭配
    pref = UserPreference(season="winter", occasion="sporty", style="sporty")
    outfits = recommend(pref)
    assert isinstance(outfits, list)
    assert len(outfits) == 0


def test_filter_items_all_match_criteria():
    """过滤后的所有衣物必须同时匹配 season 和 occasion"""
    items = load_items()
    pref = UserPreference(season="winter", occasion="business", style="formal")
    filtered = filter_items(items, pref)
    assert len(filtered) > 0
    for item in filtered:
        assert pref.season in item.season
        assert pref.occasion in item.occasion


def test_recommend_top_n_respected():
    pref = UserPreference(season="summer", occasion="casual", style="casual", top_n=1)
    outfits = recommend(pref)
    assert len(outfits) <= 1
