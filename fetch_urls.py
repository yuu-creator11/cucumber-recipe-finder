"""
recipes.json の外部URLからレシピ名・説明を取得して更新するスクリプト
実行: python recipe-finder/fetch_urls.py
事前: pip install requests beautifulsoup4
"""
import json
import os
import time
import re

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ 依存パッケージが見つかりません。以下を実行してください:")
    print("   pip install requests beautifulsoup4")
    exit(1)

RECIPES_PATH = os.path.join(os.path.dirname(__file__), "recipes.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SKIP_DOMAINS = ["instagram.com", "tiktok.com", "twitter.com", "x.com",
                "chatgpt.com", "yahoo.co.jp/search"]


def should_skip(url):
    return any(d in url for d in SKIP_DOMAINS)


def fetch_recipe_info(url):
    """URLからタイトルとdescriptionを取得"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # タイトル取得 (og:title → title タグ の順)
        og_title = soup.find("meta", property="og:title")
        title = (og_title["content"] if og_title and og_title.get("content")
                 else (soup.title.string if soup.title else ""))
        title = title.strip() if title else ""

        # description 取得
        og_desc = soup.find("meta", property="og:description")
        desc = (og_desc["content"] if og_desc and og_desc.get("content")
                else "")
        desc = desc.strip() if desc else ""

        # クリーンアップ: サイト名部分を除去
        for suffix in [" | クラシル", " - Cookpad", " | Nadia", " | デリッシュキッチン",
                       " | E・レシピ", " - 楽天レシピ", " | DELISH KITCHEN"]:
            title = title.replace(suffix, "").strip()

        # きゅうり関連でなければスキップ
        if title and (
            "きゅうり" in title or "胡瓜" in title or
            "cucumber" in title.lower() or desc
        ):
            return title, desc[:120]
        elif title:
            return title, desc[:120]
        return None, None

    except Exception as e:
        return None, None


def main():
    with open(RECIPES_PATH, encoding="utf-8") as f:
        recipes = json.load(f)

    url_items = [r for r in recipes if r.get("source_type") == "url"]
    print(f"🔗 URLレシピ数: {len(url_items)}件")

    updated = 0
    for i, recipe in enumerate(url_items):
        url = recipe.get("url", "")
        if not url or should_skip(url):
            print(f"  [{i+1}/{len(url_items)}] スキップ: {url[:60]}")
            continue

        print(f"  [{i+1}/{len(url_items)}] 取得中: {url[:60]}", end="", flush=True)
        title, desc = fetch_recipe_info(url)

        if title:
            recipe["name"] = title
            if desc:
                recipe["description"] = desc
            print(f" → {title[:40]}")
            updated += 1

            # フレーバー・食材を再判定（タイトル情報が増えたので）
            from parse_recipes import detect_tags, extract_ingredients_key
            text = title + " " + desc
            flavors, genres, seasons, events, categories = detect_tags(text)
            if flavors:
                recipe["flavor"] = flavors
            if genres and genres != ["和風"]:
                recipe["genre"] = genres
            if seasons:
                recipe["season"] = seasons
            if events:
                recipe["events"] = events
            if ingredients := extract_ingredients_key(text):
                recipe["ingredients_key"] = ingredients
        else:
            print(" → 取得失敗")

        time.sleep(0.8)  # サーバー負荷軽減

    with open(RECIPES_PATH, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完了: {updated}件のURLレシピ名を更新 → {RECIPES_PATH}")


if __name__ == "__main__":
    main()
