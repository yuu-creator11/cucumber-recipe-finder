"""
LINEチャット「SNSレシピストック」→ recipes.json 変換スクリプト
実行: python recipe-finder/parse_recipes.py
"""
import re
import json
import os

LINE_CHAT_PATH = os.path.expanduser(
    "~/Downloads/[LINE] SNSレシピストックのトーク.txt"
)
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "recipes.json")

# ──────────────────────────────────────────
# フレーバー・ジャンル自動判定キーワード
# ──────────────────────────────────────────

FLAVOR_KEYWORDS = {
    "ピリ辛": ["ピリ辛", "コチュジャン", "豆板醤", "ラー油", "唐辛子", "一味", "七味",
               "辛", "チリ", "ハリッサ", "タバスコ", "ホットソース", "花椒", "麻辣",
               "わさび", "からし", "柚子胡椒"],
    "さっぱり": ["さっぱり", "酢", "梅", "ポン酢", "レモン", "ライム", "すだち",
                "かぼす", "ゆず", "三杯酢", "甘酢", "柑橘", "甘酒"],
    "こってり": ["マヨ", "マヨネーズ", "チーズ", "バター", "クリーム", "こってり",
                "ガーリックバター", "カルボナーラ", "バーニャ"],
    "旨辛": ["旨辛", "キムチ", "ヤンニョム", "焼肉のたれ", "甘辛"],
    "甘め": ["はちみつ", "みりん", "甘め", "黒蜜", "きなこ", "メープル",
             "砂糖＋", "甘酢"],
    "変わり種": ["チョコ", "バニラ", "シナモン", "ナツメグ", "デザート", "トリュフ",
                "バルサミコ"],
}

GENRE_KEYWORDS = {
    "韓国風": ["コチュジャン", "ヤンニョム", "キムチ", "韓国", "ナムル", "チャンジャ",
              "ビビンバ"],
    "中華風": ["花椒", "四川", "中華", "麻辣", "五香粉", "八角", "豆板醤"],
    "洋風": ["チーズ", "オリーブ", "バジル", "マスタード", "アンチョビ", "ペペロン",
             "カルボナーラ", "バーニャ", "トリュフ", "ディル", "パセリ", "ケッパー"],
    "エスニック": ["ナンプラー", "パクチー", "スイートチリ", "タコス", "ケイジャン",
                  "ハリッサ", "ザアタル", "サンバル", "ガラムマサラ", "クミン"],
    "和風": ["めんつゆ", "白だし", "昆布", "かつお", "土佐酢", "塩麹", "醤油麹",
            "甘酒", "木の芽", "三つ葉", "みょうが", "大葉", "青のり"],
}

SEASON_KEYWORDS = {
    "春": ["桜", "春", "ひなまつり", "みどりの日", "エイプリルフール"],
    "夏": ["冷やし", "ひんやり", "さっぱり夏", "夏", "恵方巻", "夏バテ"],
    "秋": ["秋", "芋", "栗", "きのこ"],
    "冬": ["鍋", "おでん", "温かい", "冬", "お正月", "年末"],
}

EVENT_KEYWORDS = {
    "バレンタイン": ["バレンタイン", "チョコ", "2/14"],
    "節分": ["節分", "恵方巻"],
    "ひなまつり": ["ひなまつり", "3/3"],
    "みどりの日": ["みどりの日", "緑一色"],
    "お正月": ["お正月", "雑煮", "元旦", "年末"],
    "マヨネーズの日": ["マヨネーズの日", "3/1"],
}

CATEGORY_KEYWORDS = {
    "主菜": ["ステーキ", "唐揚げ", "炒め", "焼き", "煮", "揚げ", "どんぶり", "丼"],
    "副菜": ["副菜", "和え物", "浅漬け", "なます", "ナムル", "おひたし"],
    "おつまみ": ["おつまみ", "酒の肴", "ビールに合う", "焼き鳥"],
    "サラダ": ["サラダ", "生野菜"],
    "ご飯もの": ["ライスサラダ", "混ぜごはん", "おにぎり", "雑煮", "恵方巻",
                "寿司", "巻き"],
    "ソース": ["ソース", "タレ", "ドレッシング", "ディップ"],
    "マヨアレンジ": ["マヨネーズ", "マヨ"],
    "たたきアレンジ": ["たたき"],
}


def detect_tags(text):
    """テキストからフレーバー・ジャンル・季節・イベント・カテゴリを自動検出"""
    flavors, genres, seasons, events, categories = [], [], [], [], []

    for tag, keywords in FLAVOR_KEYWORDS.items():
        if any(k in text for k in keywords):
            flavors.append(tag)

    for tag, keywords in GENRE_KEYWORDS.items():
        if any(k in text for k in keywords):
            genres.append(tag)

    for tag, keywords in SEASON_KEYWORDS.items():
        if any(k in text for k in keywords):
            seasons.append(tag)

    for tag, keywords in EVENT_KEYWORDS.items():
        if any(k in text for k in keywords):
            events.append(tag)

    for tag, keywords in CATEGORY_KEYWORDS.items():
        if any(k in text for k in keywords):
            categories.append(tag)

    if not genres:
        genres = ["和風"]
    if not categories:
        categories = ["副菜"]

    return flavors, genres, seasons, events, categories


def extract_ingredients_key(text):
    """食材キーワードを抽出"""
    ingredient_map = {
        "ツナ": ["ツナ"],
        "チーズ": ["チーズ", "クリームチーズ", "パルメザン", "モッツァレラ"],
        "梅": ["梅肉", "梅干し"],
        "明太子": ["明太", "たらこ"],
        "サバ缶": ["サバ缶", "サバ"],
        "ごま": ["ごま", "白ごま", "黒ごま"],
        "マヨネーズ": ["マヨ", "マヨネーズ"],
        "コチュジャン": ["コチュジャン"],
        "塩昆布": ["塩昆布"],
        "アンチョビ": ["アンチョビ"],
        "ヨーグルト": ["ヨーグルト"],
        "わさび": ["わさび"],
        "にんにく": ["にんにく", "ガーリック"],
        "しょうが": ["しょうが", "ジンジャー"],
        "ごま油": ["ごま油"],
        "醤油": ["醤油"],
        "みそ": ["味噌", "みそ"],
        "ちくわ": ["ちくわ"],
        "豚肉": ["豚", "ポーク"],
        "牛肉": ["牛", "ビーフ", "ステーキ"],
        "鶏肉": ["鶏", "チキン"],
    }
    found = []
    for key, variants in ingredient_map.items():
        if any(v in text for v in variants):
            found.append(key)
    return found


# ──────────────────────────────────────────
# LINEチャットパーサー
# ──────────────────────────────────────────

def parse_line_chat(filepath):
    """LINEチャットをパースしてメッセージリストを返す"""
    with open(filepath, encoding="utf-8") as f:
        raw = f.read()

    lines = raw.splitlines()
    messages = []
    current_date = ""
    i = 0
    time_sender_re = re.compile(r'^(\d{1,2}:\d{2})\t(.+?)\t(.*)')
    date_re = re.compile(r'^\d{4}/\d{2}/\d{2}')

    while i < len(lines):
        line = lines[i]

        if date_re.match(line):
            current_date = line[:10]
            i += 1
            continue

        m = time_sender_re.match(line)
        if not m:
            i += 1
            continue

        msg_time, sender, content = m.group(1), m.group(2), m.group(3)

        # マルチラインメッセージ（引用符で囲まれている）
        if content.startswith('"'):
            content = content[1:]  # 先頭の引用符を除去
            while i + 1 < len(lines):
                i += 1
                next_line = lines[i]
                if next_line.endswith('"') and not next_line.endswith('\\"'):
                    content += "\n" + next_line[:-1]
                    break
                content += "\n" + next_line

        messages.append({
            "date": current_date,
            "time": msg_time,
            "sender": sender,
            "content": content.strip(),
        })
        i += 1

    return messages


# ──────────────────────────────────────────
# レシピ抽出ロジック
# ──────────────────────────────────────────

def extract_full_recipe(content):
    """■ 材料を含む完全レシピを抽出"""
    if "■ 材料" not in content and "● 材料" not in content:
        return None

    # 【〜】形式のタイトルを優先
    title_m = re.search(r'【(.+?)】', content)
    if title_m:
        name = title_m.group(1)
        return {"name": name, "full_recipe": content, "source_type": "full_recipe", "url": None}

    # 先頭行が会話文っぽければスキップ（レシピではない）
    first_line = content.split("\n")[0].strip()
    conversational_starts = ["いいですね", "了解", "ありがとう", "なるほど", "そうですね",
                             "確かに", "すごい", "わかりました", "はい、", "ご要望"]
    if any(first_line.startswith(s) for s in conversational_starts):
        # 🥒タイトル行を探す
        emoji_title = re.search(r'🥒「(.+?)」', content)
        if emoji_title:
            name = emoji_title.group(1)
        else:
            return None  # 会話文でレシピタイトルも不明 → スキップ
    else:
        lines = content.split("\n")
        name = ""
        for line in lines[:3]:
            line = line.strip().strip("【】")
            if line and not line.startswith("■") and not line.startswith("●"):
                name = line
                break
        if not name:
            name = "きゅうりレシピ"

    return {"name": name, "full_recipe": content, "source_type": "full_recipe", "url": None}


def extract_365_list(content):
    """365パターンリスト（番号付き）を個別アイテムとして抽出"""
    items = []

    # リストのカテゴリブロック検出
    category_re = re.compile(
        r'[【\[①②③④⑤⑥⑦⑧⑨⑩].*?[】\]]|'
        r'🧂|🌿|🧀|🌶|🍋|🍯|✅'
    )

    base_name = ""
    current_category_tag = ""

    # ベースとなるレシピ名を先頭から検出
    if "マヨネーズ" in content[:100] or "マヨ" in content[:100]:
        base_name = "きゅうりマヨ"
    elif "たたき" in content[:100]:
        base_name = "たたききゅうり"
    else:
        base_name = "きゅうりアレンジ"

    # カテゴリブロック行をマッピング
    cat_map = {}
    lines = content.split("\n")
    for line in lines:
        stripped = line.strip()
        if category_re.search(stripped) and len(stripped) < 50:
            current_category_tag = stripped.strip("【】[]🧂🌿🧀🌶🍋🍯✅").strip()
            # カテゴリラベルを整理
            current_category_tag = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩]\s*', '', current_category_tag)
            current_category_tag = current_category_tag.strip()

        # 番号付きアイテム行: `1.	醤油` or `\t1.\t醤油`
        item_m = re.match(r'\s*(\d+)\.\s+(.+)', stripped)
        if item_m:
            num = int(item_m.group(1))
            flavor_combo = item_m.group(2).strip()
            # ダッシュや説明除去
            flavor_combo = re.split(r'[（(]', flavor_combo)[0].strip()
            if flavor_combo:
                cat_map[num] = {"combo": flavor_combo, "cat_label": current_category_tag}

    for num, info in cat_map.items():
        combo = info["combo"]
        full_name = f"{base_name} — {combo}"
        flavors, genres, seasons, events, categories = detect_tags(combo)
        ingredients = extract_ingredients_key(combo)
        items.append({
            "name": full_name,
            "description": f"{base_name}のアレンジ: {combo}",
            "full_recipe": None,
            "source_type": "list_item",
            "url": None,
            "list_base": base_name,
            "combo": combo,
            "cat_label": info["cat_label"],
            "flavor": flavors,
            "genre": genres,
            "season": seasons,
            "events": events,
            "category": ["アレンジ案"],
            "ingredients_key": ingredients,
        })

    return items


def is_365_list(content):
    """365パターンリストかどうか判定"""
    numbered_lines = len(re.findall(r'^\s*\d+\.\s+', content, re.MULTILINE))
    return numbered_lines > 20


def extract_url_ideas(content):
    """テキストアイデア（短文）を抽出 — レシピ関連のみ"""
    stripped = content.strip()
    if len(stripped) > 200:
        return None
    if stripped.startswith("http"):
        return None
    if "[写真]" in stripped or "[スタンプ]" in stripped:
        return None
    if len(stripped) < 5:
        return None

    # システム・操作系メッセージを除外
    if "がメッセージの送信を取り消しました" in stripped:
        return None
    if "が" in stripped[:10] and ("追加" in stripped or "変更" in stripped):
        return None

    # 材料行・手順行の断片を除外
    if stripped.startswith(("•", "・", "→", "↑", "⸻", "---", "⁨", "*", "＊")):
        return None
    if re.match(r'^\s*\d+\.\s', stripped):
        return None
    if re.search(r'[:：]\s*(少々|適量|大さじ|小さじ|ml|g|本|枚|缶|個)', stripped):
        return None
    # カロリー数値の断片（100倍シリーズの断片）
    if re.search(r':\s*\d+kcal|kcal$|\d+〜\d+kcal', stripped):
        return None

    # AIレスポンスの冒頭・末尾フレーズ
    ignore_prefixes = ["了解", "どれ行きます", "次どうしますか", "必要なら次",
                       "ここまでで", "👉", "続きについて", "ご希望に合わせて",
                       "いいですね", "なるほど", "確かに", "方向を変えて",
                       "■ まとめ", "■ ポイント", "この企画で", "もし「売る」",
                       "完全に遊び", "もしテーマ決め"]
    if any(stripped.startswith(p) for p in ignore_prefixes):
        return None

    # 会話・反応・意見（レシピ情報でない）
    non_recipe_phrases = [
        "美味しそう", "作ってあれば一本ペロッと",
        "どうでしょうか？", "どうでしょう？",
        "なんて、", "なかなか直近では",
        "さかえの料理長さんに頼めば", "作ってもらえたら販促",
        "みやぞんの番組のレシピ", "みやぞんの番組",
        "全部美味しそう", "10パターン作っちゃう",
        "きゅうり毎日食べてほしい", "作ってあれば",
        "シャカシャカきゅうりをシリーズ化",
        "勝手に、毎週日曜日をシャカシャカサンデー",
        "西田のきゅうり✖️SNS会", "西田のきゅうりを食べてみた",
        "きゅうり入れてみた", "バジルソースが足りないのか",
        "2025年は麻辣湯がトレンド", "キーマカレーはひき肉を使うなら",
        "こちらのレシピをベースにアレンジ案をまとめました",
        "イメージはこんな感じ",
        "もし「売る」前提なら",
        "この企画で当たりやすいのは",
    ]
    if any(p in stripped for p in non_recipe_phrases):
        return None

    # カレンダーメモ（日付のみ）
    if re.match(r'^\d+/\d+\s+(節分|バレンタイン|ねこの日|マヨネーズの日|ひなまつり)', stripped):
        return None

    # 経済・市場分析の断片
    market_phrases = ["ブロッコリーを作る人が増える", "天気が順調", "たくさんとれる",
                      "ブロッコリーが安くなる", "消費者が安いブロッコリー",
                      "きゅうりの価格は上がらない", "豚、鶏、魚も焼いて、ソースをかける"]
    if any(p in stripped for p in market_phrases):
        return None

    # マーケティング・イベント告知
    marketing_phrases = ["#西尾においでん", "顔出しパネルの写真を投稿したら",
                         "SNSレシピストック", "エイプリルフールねた",
                         "豚、鶏、魚も焼いて"]
    if any(p in stripped for p in marketing_phrases):
        return None

    # 単語断片（Wasabi / Bacon 等、英語のみ1〜2語）
    if re.match(r'^[A-Za-z]+$', stripped) or re.match(r'^[A-Za-z]+ [A-Za-z]+$', stripped):
        return None

    # きゅうり占いのフレーズ
    fortune_phrases = ["きゅうりを折った時の断面", "できるよ。いわゆる正式な占い",
                       "スパッと気持ちよく折れる", "グニャっと曲がってから",
                       "種がきれいに整ってる", "みずみずしくてツヤがある",
                       "星っぽく見える", "ハートっぽい", "完全に遊びだけど"]
    if any(p in stripped for p in fortune_phrases):
        return None

    # 「に」で始まるような明らかな断片
    if re.match(r'^[にをはがもへ]', stripped):
        return None

    # コメント・感想系（レシピ名でない）
    comment_phrases = [
        "焼肉の定番にしたい", "これにきゅうりも追加",
        "玉子、ツナ、ウィンナー、など、",
        "きゅうりを芯にして、衣と油でカロリーを稼ぐタイプ",
        "きゅうりを\"器\"にして中に高カロリー詰め込む",
        'きゅうりを"器"にして中に高カロリー詰め込む',
        "きゅうり＋濃厚ごまだれ＋肉で一気に稼ぐ",
        "きゅうりを\"フルーツ枠\"に偽装",
        'きゅうりを"フルーツ枠"に偽装',
        "麺＋油で確実に100倍突破",
        "きゅうりをポキッと折った断面を観察して",
    ]
    if any(p in stripped for p in comment_phrases):
        return None

    # きゅうり占いの番号付き項目
    if re.match(r'^[①②③④⑤⑥]\s+(種の形|水分の多さ|折れ方|断面の形)', stripped):
        return None

    # 末尾に閉じ括弧だけ残っているケースをクリーンアップ
    stripped = stripped.rstrip("】")

    return stripped if stripped else None


def build_recipes(messages):
    """メッセージリストからレシピデータを構築"""
    recipes = []
    recipe_id = 1
    seen_urls = set()
    seen_ideas = set()

    for msg in messages:
        content = msg["content"]
        if not content:
            continue

        # ── 完全レシピ（材料・作り方付き）
        # 先頭100文字にレシピタイトルらしき内容があるか確認
        header = content[:100]
        has_recipe_title = ("きゅうり" in header or "胡瓜" in header or
                            "【" in header or "レシピ" in header)
        if ("■ 材料" in content or "● 材料" in content) and has_recipe_title:
            extracted = extract_full_recipe(content)
            if extracted:
                flavors, genres, seasons, events, categories = detect_tags(content)
                ingredients = extract_ingredients_key(content)
                recipes.append({
                    "id": recipe_id,
                    **extracted,
                    "description": "",
                    "flavor": flavors,
                    "genre": genres,
                    "season": seasons,
                    "events": events,
                    "category": categories if categories else ["副菜"],
                    "ingredients_key": ingredients,
                    "date": msg["date"],
                })
                recipe_id += 1

        # ── 365パターンリスト
        elif is_365_list(content):
            items = extract_365_list(content)
            for item in items:
                item["id"] = recipe_id
                item["date"] = msg["date"]
                recipes.append(item)
                recipe_id += 1

        # ── URLリンク
        elif content.startswith("http"):
            url = content.strip()
            if url not in seen_urls:
                seen_urls.add(url)
                flavors, genres, seasons, events, categories = detect_tags(url)
                recipes.append({
                    "id": recipe_id,
                    "name": url_to_label(url),
                    "description": "",
                    "full_recipe": None,
                    "source_type": "url",
                    "url": url,
                    "flavor": [],
                    "genre": [],
                    "season": [],
                    "events": [],
                    "category": ["外部リンク"],
                    "ingredients_key": [],
                    "date": msg["date"],
                })
                recipe_id += 1

        # ── テキストアイデア
        else:
            # URLを含む場合はURLを分離
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("http"):
                    if line not in seen_urls:
                        seen_urls.add(line)
                        recipes.append({
                            "id": recipe_id,
                            "name": url_to_label(line),
                            "description": "",
                            "full_recipe": None,
                            "source_type": "url",
                            "url": line,
                            "flavor": [],
                            "genre": [],
                            "season": [],
                            "events": [],
                            "category": ["外部リンク"],
                            "ingredients_key": [],
                            "date": msg["date"],
                        })
                        recipe_id += 1
                elif len(line) >= 5 and line not in seen_ideas:
                    # 短いアイデアメモ
                    idea = extract_url_ideas(line)
                    if idea and idea not in seen_ideas:
                        seen_ideas.add(idea)
                        flavors, genres, seasons, events, categories = detect_tags(idea)
                        ingredients = extract_ingredients_key(idea)
                        recipes.append({
                            "id": recipe_id,
                            "name": idea[:60],
                            "description": idea if len(idea) > 60 else "",
                            "full_recipe": None,
                            "source_type": "idea",
                            "url": None,
                            "flavor": flavors,
                            "genre": genres,
                            "season": seasons,
                            "events": events,
                            "category": categories if categories else ["アイデア"],
                            "ingredients_key": ingredients,
                            "date": msg["date"],
                        })
                        recipe_id += 1

    return recipes


def url_to_label(url):
    """URLからドメインベースのラベルを生成"""
    domain_map = {
        "cookpad.com": "🍳 Cookpad レシピ",
        "kurashiru.com": "🏠 クラシル レシピ",
        "oceans-nadia.com": "👩‍🍳 Nadia レシピ",
        "delishkitchen.tv": "🎬 デリッシュキッチン レシピ",
        "recipe.rakuten.co.jp": "🛍 楽天レシピ",
        "park.ajinomoto.co.jp": "🧂 味の素レシピ",
        "kewpie.co.jp": "🥚 キユーピー レシピ",
        "daidokolog.pal-system.co.jp": "🌿 大地を守る会 レシピ",
        "youtu.be": "▶️ YouTube 動画",
        "youtube.com": "▶️ YouTube 動画",
        "instagram.com": "📸 Instagram",
        "tiktok.com": "🎵 TikTok",
        "twitter.com": "🐦 Twitter/X",
        "x.com": "🐦 Twitter/X",
    }
    for domain, label in domain_map.items():
        if domain in url:
            return label
    return "🔗 外部レシピリンク"


def main():
    print(f"📖 読み込み中: {LINE_CHAT_PATH}")
    messages = parse_line_chat(LINE_CHAT_PATH)
    print(f"   メッセージ数: {len(messages)}")

    recipes = build_recipes(messages)
    print(f"   レシピ件数: {len(recipes)}")

    source_counts = {}
    for r in recipes:
        st = r.get("source_type", "unknown")
        source_counts[st] = source_counts.get(st, 0) + 1
    for st, count in sorted(source_counts.items()):
        print(f"   [{st}]: {count}件")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 保存完了: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
