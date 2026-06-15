from src.features import (
    best_color_match,
    color_similarity,
    compute_item_score,
    outfit_color_harmony,
    style_compatibility_score,
)
from src.model import ClothingItem, UserPreference


def _make_item(**kwargs) -> ClothingItem:
    defaults = dict(
        id="t1", name="test", category="top",
        colors=["white"], style="casual",
        season=["summer"], occasion=["casual"], tags=[],
    )
    defaults.update(kwargs)
    return ClothingItem(**defaults)


# ── 颜色相似度 ────────────────────────────────────────────

def test_color_similarity_identical():
    assert color_similarity("white", "white") == 1.0
    assert color_similarity("black", "black") == 1.0
    assert color_similarity("red", "red") == 1.0


def test_color_similarity_compatible():
    assert color_similarity("white", "beige") >= 0.7
    assert color_similarity("black", "gray") >= 0.7
    assert color_similarity("black", "red") >= 0.7   # 黑红经典配色


def test_color_similarity_unknown_returns_zero():
    assert color_similarity("white", "neon") == 0.0


def test_new_colors_exist():
    """新增颜色都有定义"""
    for color in ["red", "pink", "green", "navy", "gold", "purple", "orange"]:
        assert color_similarity(color, color) == 1.0


# ── 颜色偏好匹配 ──────────────────────────────────────────

def test_best_color_match_no_preference():
    item = _make_item(colors=["white", "blue"])
    assert best_color_match(item.colors, None) == 0.5


def test_best_color_match_empty_colors():
    assert best_color_match([], "white") == 0.0


def test_best_color_match_exact():
    item = _make_item(colors=["white", "blue"])
    assert best_color_match(item.colors, "white") == 1.0


def test_best_color_match_picks_best():
    item = _make_item(colors=["white", "blue"])
    score = best_color_match(item.colors, "beige")
    assert score == 0.9   # white-beige=0.9, blue-beige=0.6 → best=0.9


# ── 套装颜色和谐度 ────────────────────────────────────────

def test_outfit_color_harmony_single_item():
    assert outfit_color_harmony([["white"]]) == 0.5


def test_outfit_color_harmony_same_color():
    score = outfit_color_harmony([["white"], ["white"], ["white"]])
    assert score == 1.0


def test_outfit_color_harmony_classic_combo():
    # 黑白搭配经典，应有较高和谐度
    score = outfit_color_harmony([["black"], ["white"], ["black"]])
    assert score >= 0.7


def test_outfit_color_harmony_empty_fallback():
    assert outfit_color_harmony([]) == 0.5


# ── 风格兼容性 ────────────────────────────────────────────

def test_style_compatibility_same():
    assert style_compatibility_score("casual", "casual") == 1.0
    assert style_compatibility_score("formal", "formal") == 1.0


def test_style_compatibility_casual_street():
    # casual 和 street 相对兼容
    assert style_compatibility_score("casual", "street") >= 0.6


def test_style_compatibility_formal_sporty():
    # formal 和 sporty 不搭
    assert style_compatibility_score("formal", "sporty") < 0.3


# ── 单品评分 ──────────────────────────────────────────────

def test_compute_item_score_full_match():
    item = _make_item(colors=["blue"], style="casual",
                      season=["summer"], occasion=["casual"])
    pref = UserPreference(season="summer", occasion="casual", style="casual")
    score = compute_item_score(item, pref)
    # style(2.5) + occasion(2.0) + season(1.0) + color(0.5×1.5=0.75) = 6.25
    assert score == 6.25


def test_compute_item_score_no_match():
    item = _make_item(colors=["blue"], style="formal",
                      season=["winter"], occasion=["business"])
    pref = UserPreference(season="summer", occasion="casual", style="casual")
    score = compute_item_score(item, pref)
    # style(0) + occasion(0) + season(0) + color(0.5×1.5=0.75) = 0.75
    assert score == 0.75


def test_compute_item_score_with_color_pref():
    item = _make_item(colors=["black"], style="casual",
                      season=["summer"], occasion=["casual"])
    pref = UserPreference(season="summer", occasion="casual",
                          style="casual", color_preference="black")
    score = compute_item_score(item, pref)
    # style(2.5) + occasion(2.0) + season(1.0) + color(1.0×1.5=1.5) = 7.0
    assert score == 7.0
