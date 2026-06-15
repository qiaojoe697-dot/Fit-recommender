from src.features import (
    best_color_match,
    color_similarity,
    compute_item_score,
)
from src.model import ClothingItem, UserPreference


def test_color_similarity_identical():
    assert color_similarity("white", "white") == 1.0
    assert color_similarity("black", "black") == 1.0


def test_color_similarity_compatible():
    assert color_similarity("white", "beige") >= 0.7
    assert color_similarity("black", "gray") >= 0.7


def test_color_similarity_asymmetric_default():
    """不存在的颜色返回 0"""
    assert color_similarity("white", "neon") == 0.0


def test_best_color_match_no_preference():
    item = ClothingItem(
        id="t1", name="test", category="top",
        colors=["white", "blue"], style="casual",
        season=["summer"], occasion=["casual"],
    )
    assert best_color_match(item.colors, None) == 0.5


def test_best_color_match_empty_colors():
    """空颜色列表不崩溃"""
    assert best_color_match([], "white") == 0.0


def test_best_color_match_exact():
    item = ClothingItem(
        id="t1", name="test", category="top",
        colors=["white", "blue"], style="casual",
        season=["summer"], occasion=["casual"],
    )
    score = best_color_match(item.colors, "white")
    assert score == 1.0


def test_best_color_match_best():
    item = ClothingItem(
        id="t1", name="test", category="top",
        colors=["white", "blue"], style="casual",
        season=["summer"], occasion=["casual"],
    )
    score = best_color_match(item.colors, "beige")
    # white-beige = 0.8, blue-beige = 0.5 → best = 0.8
    assert score == 0.8


def test_compute_item_score_full_match():
    item = ClothingItem(
        id="t1", name="test", category="top",
        colors=["blue"], style="casual",
        season=["summer"], occasion=["casual"],
    )
    pref = UserPreference(season="summer", occasion="casual", style="casual")
    score = compute_item_score(item, pref)
    # style(2) + occasion(2) + season(1) + color(0.5 no pref) = 5.5
    assert score == 5.5


def test_compute_item_score_no_match():
    item = ClothingItem(
        id="t1", name="test", category="top",
        colors=["blue"], style="formal",
        season=["winter"], occasion=["business"],
    )
    pref = UserPreference(season="summer", occasion="casual", style="casual")
    score = compute_item_score(item, pref)
    # style(0) + occasion(0) + season(0) + color(0.5 no pref) = 0.5
    assert score == 0.5


def test_compute_item_score_partial_match():
    item = ClothingItem(
        id="t1", name="test", category="top",
        colors=["blue"], style="casual",
        season=["spring", "summer"], occasion=["casual", "business"],
    )
    pref = UserPreference(season="summer", occasion="business", style="casual")
    score = compute_item_score(item, pref)
    # style(2) + occasion(2) + season(1) + color(0.5 no pref) = 5.5
    assert score == 5.5
