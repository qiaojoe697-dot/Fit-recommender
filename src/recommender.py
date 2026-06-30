from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Tuple

from src.features import compute_item_score, outfit_color_harmony, style_compatibility_score
from src.model import ClothingItem, Outfit, UserPreference

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# 每个类别保留的候选数量上限（避免组合爆炸）
_MAX_CANDIDATES_PER_CATEGORY = 5


def load_items() -> List[ClothingItem]:
    """从 items.json 加载所有衣物数据"""
    path = _DATA_DIR / "items.json"
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    items = []
    for item_data in raw:
        # 兼容旧数据：新字段可能不存在
        item_data.setdefault("tags", [])
        item_data.setdefault("material", "cotton")
        item_data.setdefault("popularity", 50)
        items.append(ClothingItem(**item_data))
    return items

def filter_items(
    items: List[ClothingItem], pref: UserPreference
) -> List[ClothingItem]:
    """
    初步过滤候选衣物：
    - 必须匹配季节
    - 必须匹配场合
    """
    result = []
    for item in items:
        if pref.season not in item.season:
            continue
        if pref.occasion not in item.occasion:
            continue
        result.append(item)
    return result


def _generate_outfits(
    tops: List[Tuple[float, ClothingItem]],
    bottoms: List[Tuple[float, ClothingItem]],
    shoes: List[Tuple[float, ClothingItem]],
    accessories: List[Tuple[float, ClothingItem]],
    pref: UserPreference,
) -> List[Outfit]:
    """
    生成所有候选搭配组合并打分。

    综合评分 = 单品评分之和 + 颜色整体和谐度加成 + 风格一致性加成
    """
    outfits = []

    for top_score, top in tops:
        for bot_score, bot in bottoms:
            for shoe_score, shoe in shoes:
                base_score = top_score + bot_score + shoe_score
                core_items = [top, bot, shoe]

                # 可选配饰：选分数最高的
                acc_item = None
                if accessories:
                    best_acc = max(accessories, key=lambda x: x[0])
                    acc_score, acc_item = best_acc
                    base_score += acc_score * 0.5
                    core_items.append(acc_item)

                # ① 颜色整体和谐度加成（最多 +2.0 分）
                all_colors = [item.colors for item in core_items]
                harmony = outfit_color_harmony(all_colors)
                color_bonus = harmony * 2.0

                # ② 风格一致性加成：上下装风格越搭分越高（最多 +1.0 分）
                style_bonus = style_compatibility_score(top.style, bot.style) * 1.0

                total = round(base_score + color_bonus + style_bonus, 1)

                reason = _generate_reason(top, bot, shoe, acc_item, total)
                tip = _generate_style_tip(top, bot, shoe, pref)

                outfits.append(Outfit(
                    items=core_items,
                    score=total,
                    reason=reason,
                    style_tip=tip,
                ))

    outfits.sort(key=lambda o: o.score, reverse=True)
    return outfits


def _generate_reason(
    top: ClothingItem,
    bottom: ClothingItem,
    shoes: ClothingItem,
    accessory: ClothingItem | None,
    score: float,
) -> str:
    """生成搭配理由"""
    all_items = [top, bottom, shoes]
    if accessory:
        all_items.append(accessory)

    names = " + ".join(i.name for i in all_items)
    all_colors = list({c for i in all_items for c in i.colors})
    color_note = "、".join(all_colors[:3]) + "色系"
    style_note = f"{top.style}风格"
    return f"{names}（{style_note}，{color_note}搭配，评分{score}）"


def _generate_style_tip(
    top: ClothingItem,
    bottom: ClothingItem,
    shoes: ClothingItem,
    pref: UserPreference,
) -> str:
    """根据场合和风格给出简短穿搭 Tip"""
    tips = {
        ("casual", "casual"):   "日常休闲首选，舒适又百搭，可搭配简约配饰提升质感。",
        ("casual", "street"):   "街头感十足，建议叠穿或加一件外套增加层次感。",
        ("formal", "business"): "商务场合利器，保持整洁熨烫，配皮质公文包更佳。",
        ("formal", "formal"):   "正式场合必备，注意全套颜色协调，配饰宜简不宜繁。",
        ("sporty", "sporty"):   "运动机能风，透气舒适，适合户外和健身场合。",
        ("sporty", "casual"):   "运动休闲混搭，自然随性，适合周末出行。",
        ("street", "casual"):   "街头休闲风，个性张扬，可搭太阳镜或帽子点睛。",
        ("street", "date"):     "约会街头风，时髦有型，搭配一个亮色包包增加活力。",
        ("casual", "date"):     "约会休闲风，清新自然，建议选颜色柔和的配饰。",
        ("formal", "date"):     "约会正式风，优雅得体，香水和精致发型是加分项。",
    }
    key = (pref.style, pref.occasion)
    return tips.get(key, "搭配均衡，适合当前场合，可根据个人喜好微调配饰。")


def recommend(pref: UserPreference) -> List[Outfit]:
    """
    执行推荐主流程：
    过滤 → 打分 → 分组 → 组合 → 排序 → 返回 Top-N
    """
    all_items = load_items()
    candidates = filter_items(all_items, pref)

    # 按类别分组并打分
    grouped: Dict[str, List[Tuple[float, ClothingItem]]] = {
        "top": [], "bottom": [], "shoes": [], "accessory": [],
    }
    for item in candidates:
        score = compute_item_score(item, pref)
        if item.category in grouped:
            grouped[item.category].append((score, item))

    # 每个类别按分数降序，只保留前 N 个候选（避免组合数爆炸）
    for cat in grouped:
        grouped[cat].sort(key=lambda x: x[0], reverse=True)
        grouped[cat] = grouped[cat][:_MAX_CANDIDATES_PER_CATEGORY]

    # 核心类别缺失时无法搭配
    if not grouped["top"] or not grouped["bottom"] or not grouped["shoes"]:
        return []

    all_outfits = _generate_outfits(
        grouped["top"], grouped["bottom"], grouped["shoes"], grouped["accessory"],
        pref,
    )

    return all_outfits[: pref.top_n]
