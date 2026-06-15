from __future__ import annotations

import json
from pathlib import Path
from typing import List

from src.features import compute_item_score
from src.model import ClothingItem, Outfit, UserPreference

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_items() -> List[ClothingItem]:
    """从 items.json 加载所有衣物数据"""
    path = _DATA_DIR / "items.json"
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [ClothingItem(**item) for item in raw]


def filter_items(
    items: List[ClothingItem], pref: UserPreference
) -> List[ClothingItem]:
    """根据季节和场合初步过滤候选衣物"""
    result = []
    for item in items:
        if pref.season not in item.season:
            continue
        if pref.occasion not in item.occasion:
            continue
        result.append(item)
    return result


def _generate_outfits(
    tops: List[tuple[float, ClothingItem]],
    bottoms: List[tuple[float, ClothingItem]],
    shoes: List[tuple[float, ClothingItem]],
    accessories: List[tuple[float, ClothingItem]],
) -> List[Outfit]:
    """生成所有可能的搭配组合并打分"""
    outfits = []

    for top_score, top in tops:
        for bot_score, bot in bottoms:
            for shoe_score, shoe in shoes:
                total = top_score + bot_score + shoe_score
                items = [top, bot, shoe]

                # 可选：加入配饰（分数最高的那个）
                if accessories:
                    best_acc = max(accessories, key=lambda x: x[0])
                    acc_score, acc = best_acc
                    total += acc_score * 0.5  # 配饰权重减半
                    items.append(acc)

                reason = _generate_reason(top, bot, shoe, total)
                outfits.append(Outfit(items=items, score=round(total, 1), reason=reason))

    outfits.sort(key=lambda o: o.score, reverse=True)
    return outfits


def _generate_reason(top: ClothingItem, bottom: ClothingItem, shoes: ClothingItem, score: float) -> str:
    """生成搭配理由"""
    style_note = f"{top.style}风格"
    color_note = f"{'与'.join(set(top.colors + bottom.colors + shoes.colors))}色系搭配"
    return f"{top.name} + {bottom.name} + {shoes.name}（{style_note}，{color_note}，评分{score}）"


def recommend(pref: UserPreference) -> List[Outfit]:
    """执行推荐：过滤 → 打分 → 组合 → 排序"""
    all_items = load_items()
    candidates = filter_items(all_items, pref)

    # 按类别分组并打分
    grouped: dict[str, List[tuple[float, ClothingItem]]] = {
        "top": [],
        "bottom": [],
        "shoes": [],
        "accessory": [],
    }
    for item in candidates:
        score = compute_item_score(item, pref)
        if item.category in grouped:
            grouped[item.category].append((score, item))

    # 每个类别按分数降序排列
    for cat in grouped:
        grouped[cat].sort(key=lambda x: x[0], reverse=True)

    # 如果某个核心类别为空，无法搭配
    if not grouped["top"] or not grouped["bottom"] or not grouped["shoes"]:
        return []

    # 生成搭配
    all_outfits = _generate_outfits(
        grouped["top"], grouped["bottom"], grouped["shoes"], grouped["accessory"]
    )

    return all_outfits[: pref.top_n]
