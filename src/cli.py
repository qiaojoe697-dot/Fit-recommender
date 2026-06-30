from __future__ import annotations
import argparse
import sys
from src.model import UserPreference
from src.recommender import recommend


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="穿搭推荐系统 — 根据你的偏好推荐服装搭配",
    )
    parser.add_argument(
        "--season", required=True,
        choices=["spring", "summer", "autumn", "winter"],
        help="季节",
    )
    parser.add_argument(
        "--occasion", required=True,
        choices=["casual", "business", "formal", "sporty"],
        help="场合",
    )
    parser.add_argument(
        "--style", required=True,
        choices=["casual", "formal", "sporty", "street"],
        help="风格偏好",
    )
    parser.add_argument(
        "--color", default=None,
        help="颜色偏好（可选，如 white, blue, black）",
    )
    parser.add_argument(
        "--tags", default="",
        help="风格标签偏好（可选，逗号分隔，如 oversized,vintage,denim）",
    )
    parser.add_argument(
        "--top-n", type=int, default=3,
        help="返回推荐数量（默认 3）",
    )
    return parser


def display_outfits(outfits: list, season: str, occasion: str, style: str) -> None:
    """格式化输出推荐结果"""
    print(f"\n🎯 推荐条件: 季节={season}, 场合={occasion}, 风格={style}")
    print("=" * 60)
    print("  7维加权打分：风格×2.5 + 场合×2.0 + 季节×1.5 + 颜色×1.5")
    print("              + 材质×1.0 + 标签×1.0 + 热门度×0.5")
    print("=" * 60)
    
    if not outfits:
        print("😕 没有找到匹配的搭配。请尝试调整搜索条件。")
        return
    
    for i, outfit in enumerate(outfits, 1):
        print(f"\n  #{i}  综合评分: {outfit.score}")
        print(f"       {outfit.reason}")
        
        # 展示材质信息
        materials = list({it.material for it in outfit.items if it.material})
        if materials:
            print(f"       材质: {', '.join(materials)}")
        
        # 展示标签信息
        all_tags = []
        for it in outfit.items:
            all_tags.extend(it.tags)
        if all_tags:
            print(f"       标签: {', '.join(list(set(all_tags))[:6])}")
        
        print(f"  {'-' * 50}")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    
    # 解析标签偏好
    tag_prefs = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    
    pref = UserPreference(
        season=args.season,
        occasion=args.occasion,
        style=args.style,
        color_preference=args.color,
        tag_preferences=tag_prefs,  # 新增：传入标签偏好
        top_n=args.top_n,
    )
    
    try:
        outfits = recommend(pref)
        display_outfits(outfits, args.season, args.occasion, args.style)
    except Exception as e:
        print(f"❌ 推荐过程出错: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
