"""
outfit_recommender.py — 基于穿搭库的推荐引擎

完整实现文档「四、各场景推荐逻辑」：

  场景1：recommend_for_user()  首页个性化推荐（用户 → 穿搭）
    - 有画像用户：按杰卡德相似度从高到低排序
    - 冷启动用户：按穿搭热门度降序（未登录/新用户/无偏好）

  场景2：recommend_similar()   详情页相似推荐（穿搭 → 穿搭，10高+10低）
    - 以目标穿搭标签为基准，遍历计算杰卡德相似度
    - 高相似度组（≥ 阈值）：取前10套
    - 低相似度组（< 阈值）：取前10套
    - 每组内部按相似度降序

数据来源（双模式，由环境变量控制）：
  默认：读取本地 data/outfits.json（零依赖，模拟数据库接口）
  扩展：设置 OUTFIT_API_URL 环境变量后，自动从外部 HTTP API 拉取
        若 API 不可用，自动降级到本地 JSON，保障服务可用性

切换示例（无需修改代码）：
  export OUTFIT_API_URL=http://your-backend/api/outfits
  streamlit run web/app.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.model import OutfitRecord, UserProfile
from src.profile import jaccard_similarity, weighted_jaccard

# ── 配置 ──────────────────────────────────────────────────────────────────────

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# 外部 API 地址（不设置则走本地 JSON）
_OUTFIT_API_URL: str = os.environ.get("OUTFIT_API_URL", "")

# 详情页相似推荐：高/低组各取多少条（对应文档「四、场景2」10高+10低规则）
_SIMILAR_HIGH_COUNT = 10
_SIMILAR_LOW_COUNT  = 10

# 高/低相似度分界阈值（可在 Streamlit Tab3 中由用户实时调整）
_DEFAULT_THRESHOLD = 0.3


# ── 数据加载接口（JSON 模拟数据库 / 外部 API 双模式）────────────────────────

def load_outfits() -> List[OutfitRecord]:
    """
    加载穿搭数据。

    优先级：
      1. 设置了 OUTFIT_API_URL → 从 HTTP API 拉取
      2. 未设置 → 读取本地 data/outfits.json（模拟数据库）

    API 期望返回格式：
      [
        { "id": "o001", "name": "清新校园风",
          "tags": ["休闲", "校园", "夏季"], "popularity": 320 },
        ...
      ]

    Returns:
        List[OutfitRecord]
    """
    if _OUTFIT_API_URL:
        return _load_from_api(_OUTFIT_API_URL)
    return _load_from_json()


def _load_from_json() -> List[OutfitRecord]:
    """从本地 JSON 文件加载穿搭数据（默认模式）"""
    path = _DATA_DIR / "outfits.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [
        OutfitRecord(
            id=d["id"],
            name=d["name"],
            tags=d.get("tags", []),
            popularity=d.get("popularity", 0),
        )
        for d in raw
    ]


def _load_from_api(url: str) -> List[OutfitRecord]:
    """
    从外部 HTTP API 拉取穿搭数据。
    若 API 不可用（超时/报错），自动静默降级到本地 JSON。
    """
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=5) as resp:
            raw = json.loads(resp.read().decode())
        return [
            OutfitRecord(
                id=d["id"],
                name=d["name"],
                tags=d.get("tags", []),
                popularity=d.get("popularity", 0),
            )
            for d in raw
        ]
    except Exception:
        return _load_from_json()  # 静默降级


def build_outfit_map(outfits: List[OutfitRecord]) -> Dict[str, OutfitRecord]:
    """构建 outfit_id → OutfitRecord 的查找字典"""
    return {o.id: o for o in outfits}


# ── 场景1：首页个性化推荐（用户 → 穿搭）────────────────────────────────────

def recommend_for_user(
    profile: Optional[UserProfile],
    outfits: Optional[List[OutfitRecord]] = None,
    top_n: int = 10,
    use_weighted: bool = True,
    w_explicit: float = 2.0,
    w_implicit: float = 1.0,
) -> List[Tuple[OutfitRecord, float]]:
    """
    首页个性化推荐：用户 → 穿搭。

    对应文档「四、场景1」完整逻辑：
      1. 读取用户合并后的完整标签集合（profile.merged_tags）
      2. 遍历系统内所有穿搭，逐个计算杰卡德相似度
      3. 排序规则：
         - 登录且有偏好/行为的用户 → 按相似度从高到低
         - 未登录/新用户/无任何偏好与行为 → 按穿搭热门度降序（冷启动）

    Args:
        profile      : 用户画像。None 或 merged_tags 为空时触发冷启动
        outfits      : 穿搭列表。None 时自动调用 load_outfits() 加载
        top_n        : 返回推荐数量上限
        use_weighted : True → 加权杰卡德；False → 基础杰卡德
        w_explicit   : 显式标签权重（仅 use_weighted=True 时生效）
        w_implicit   : 隐式标签权重（仅 use_weighted=True 时生效）

    Returns:
        [(OutfitRecord, score), ...]  按分数降序，score 为相似度或热门归一化值
    """
    if outfits is None:
        outfits = load_outfits()

    # ── 冷启动分支：无画像或画像为空 ─────────────────────────────────────────
    if profile is None or profile.is_cold_start():
        max_pop = max((o.popularity for o in outfits), default=1) or 1
        ranked = sorted(outfits, key=lambda o: o.popularity, reverse=True)
        return [(o, round(o.popularity / max_pop, 4)) for o in ranked[:top_n]]

    # ── 个性化推荐分支：按杰卡德相似度排序 ───────────────────────────────────
    scored: List[Tuple[OutfitRecord, float]] = []
    for outfit in outfits:
        if use_weighted:
            score = weighted_jaccard(profile, outfit.tag_set(), w_explicit, w_implicit)
        else:
            score = jaccard_similarity(profile.merged_tags, outfit.tag_set())
        scored.append((outfit, round(score, 4)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]


# ── 场景2：详情页相似推荐（穿搭 → 穿搭，10高+10低）────────────────────────

def recommend_similar(
    target_outfit_id: str,
    outfits: Optional[List[OutfitRecord]] = None,
    high_count: int = _SIMILAR_HIGH_COUNT,
    low_count: int  = _SIMILAR_LOW_COUNT,
    threshold: float = _DEFAULT_THRESHOLD,
) -> Dict[str, List[Tuple[OutfitRecord, float]]]:
    """
    详情页相似推荐：穿搭 → 穿搭（10高+10低）。

    对应文档「四、场景2」完整逻辑：
      1. 获取当前查看穿搭的标签集合，作为基准集
      2. 遍历系统内其他穿搭，逐一计算与基准集的杰卡德相似度
      3. 分组筛选：
         - 高相似度组：相似度 >= threshold，取前 high_count 套
         - 低相似度组：相似度 <  threshold，取前 low_count  套
      4. 每组内部按相似度降序排列

    Args:
        target_outfit_id : 目标穿搭的 ID
        outfits          : 穿搭列表。None 时自动加载
        high_count       : 高相似度组最大返回数量，默认 10
        low_count        : 低相似度组最大返回数量，默认 10
        threshold        : 高/低相似度分界阈值，默认 0.3

    Returns:
        { "high": [(OutfitRecord, score), ...],
          "low":  [(OutfitRecord, score), ...] }
    """
    if outfits is None:
        outfits = load_outfits()

    outfit_map = build_outfit_map(outfits)
    target = outfit_map.get(target_outfit_id)
    if target is None:
        return {"high": [], "low": []}

    target_tags = target.tag_set()
    high: List[Tuple[OutfitRecord, float]] = []
    low:  List[Tuple[OutfitRecord, float]] = []

    for outfit in outfits:
        if outfit.id == target_outfit_id:
            continue  # 排除自身
        score = round(jaccard_similarity(target_tags, outfit.tag_set()), 4)
        if score >= threshold:
            high.append((outfit, score))
        else:
            low.append((outfit, score))

    # 每组内部按相似度降序（对应文档「五、3. 排序规则」）
    high.sort(key=lambda x: x[1], reverse=True)
    low.sort(key=lambda x: x[1], reverse=True)

    return {
        "high": high[:high_count],
        "low":  low[:low_count],
    }
