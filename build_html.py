"""
recipes.json を読み込み recipe-finder.html を生成するスクリプト
実行: python3 recipe-finder/build_html.py
"""
import json
import os

RECIPES_PATH = os.path.join(os.path.dirname(__file__), "recipes.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "recipe-finder.html")

with open(RECIPES_PATH, encoding="utf-8") as f:
    recipes = json.load(f)

recipes_json = json.dumps(recipes, ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>きゅうりレシピファインダー</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Round" rel="stylesheet">
<style>
  :root {{
    --c-primary:   #1e7e44;
    --c-primary-d: #155c31;
    --c-primary-l: #d4edda;
    --c-accent:    #f0a500;
    --c-accent-l:  #fff3cd;
    --c-bg:        #f4f8f5;
    --c-surface:   #ffffff;
    --c-text:      #1a2e22;
    --c-muted:     #5c7265;
    --c-border:    #ddeae2;
    --c-header-from: #1e7e44;
    --c-header-to:   #0f5c2e;
    --shadow-sm:   0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
    --shadow-md:   0 4px 12px rgba(30,126,68,.10), 0 1px 3px rgba(0,0,0,.05);
    --shadow-lg:   0 8px 24px rgba(30,126,68,.13);
    --radius-sm:   8px;
    --radius-md:   14px;
    --radius-lg:   20px;
    --font:        'Noto Sans JP', -apple-system, 'Hiragino Sans', sans-serif;
  }}

  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  html {{ scroll-behavior: smooth; }}

  body {{
    font-family: var(--font);
    background: var(--c-bg);
    color: var(--c-text);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }}

  /* ── HEADER ─────────────────────────────── */
  .site-header {{
    background: linear-gradient(135deg, var(--c-header-from), var(--c-header-to));
    color: #fff;
    padding: 18px 16px 14px;
    position: sticky;
    top: 0;
    z-index: 200;
    box-shadow: 0 4px 20px rgba(0,0,0,.18);
  }}

  .header-inner {{
    max-width: 720px;
    margin: 0 auto;
  }}

  .header-title {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }}

  .header-title h1 {{
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: .02em;
    word-break: keep-all;
  }}

  .header-title .icon-leaf {{
    font-size: 1.5rem;
    opacity: .9;
    flex-shrink: 0;
  }}

  .search-wrap {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,.15);
    border: 1.5px solid rgba(255,255,255,.3);
    border-radius: var(--radius-lg);
    padding: 2px 6px 2px 14px;
    transition: background .2s, border-color .2s;
  }}

  .search-wrap:focus-within {{
    background: rgba(255,255,255,.22);
    border-color: rgba(255,255,255,.6);
  }}

  .search-wrap .material-icons-round {{
    color: rgba(255,255,255,.75);
    font-size: 1.15rem;
    flex-shrink: 0;
  }}

  .search-wrap input {{
    flex: 1;
    background: none;
    border: none;
    outline: none;
    color: #fff;
    font-family: var(--font);
    font-size: 0.93rem;
    padding: 8px 4px;
  }}

  .search-wrap input::placeholder {{ color: rgba(255,255,255,.6); }}

  .count-pill {{
    background: var(--c-accent);
    color: #fff;
    border-radius: var(--radius-lg);
    padding: 7px 14px;
    font-size: 0.82rem;
    font-weight: 700;
    white-space: nowrap;
    letter-spacing: .02em;
    box-shadow: 0 2px 6px rgba(240,165,0,.35);
    flex-shrink: 0;
  }}

  /* ── FILTER PANEL ───────────────────────── */
  .filter-panel {{
    background: var(--c-surface);
    border-bottom: 1px solid var(--c-border);
    position: sticky;
    top: 88px;
    z-index: 100;
    box-shadow: 0 2px 8px rgba(0,0,0,.04);
  }}

  .filter-inner {{
    max-width: 720px;
    margin: 0 auto;
    padding: 10px 14px 6px;
  }}

  .filter-row {{
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 7px;
    flex-wrap: wrap;
  }}

  .filter-row-label {{
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--c-muted);
    letter-spacing: .08em;
    text-transform: uppercase;
    white-space: nowrap;
    min-width: 42px;
    padding-top: 3px;
  }}

  .chips {{
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }}

  .chip {{
    display: inline-flex;
    align-items: center;
    gap: 3px;
    padding: 5px 12px;
    border-radius: var(--radius-lg);
    font-size: 0.78rem;
    font-weight: 500;
    cursor: pointer;
    border: 1.5px solid var(--c-border);
    background: var(--c-surface);
    color: var(--c-muted);
    transition: all .18s cubic-bezier(.4,0,.2,1);
    white-space: nowrap;
    -webkit-tap-highlight-color: transparent;
    user-select: none;
  }}

  .chip:hover {{ border-color: var(--c-primary); color: var(--c-primary); }}

  .chip.active {{
    background: var(--c-primary);
    border-color: var(--c-primary);
    color: #fff;
    font-weight: 700;
    box-shadow: 0 2px 8px rgba(30,126,68,.3);
  }}

  .chip.chip-reset {{
    border-color: var(--c-border);
    color: #aaa;
  }}

  .chip.chip-reset.dirty {{
    border-color: #e55;
    color: #e55;
    background: #fff0f0;
  }}

  /* ── CARD LIST ──────────────────────────── */
  .card-list {{
    max-width: 720px;
    margin: 0 auto;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}

  .card {{
    background: var(--c-surface);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    overflow: hidden;
    border: 1px solid var(--c-border);
    transition: box-shadow .2s, transform .15s;
    will-change: transform;
  }}

  .card:hover {{
    box-shadow: var(--shadow-lg);
    transform: translateY(-1px);
  }}

  .card-hd {{
    padding: 14px 16px 11px;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    position: relative;
  }}

  .card-hd::after {{
    content: '';
    position: absolute;
    inset: 0;
    background: var(--c-primary-l);
    opacity: 0;
    transition: opacity .15s;
    pointer-events: none;
  }}

  .card-hd:active::after {{ opacity: 1; }}

  .card-type-dot {{
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
  }}

  .card-type-dot .material-icons-round {{ font-size: 1.2rem; }}

  .dot-full   {{ background: #e8f5e9; color: #2e7d32; }}
  .dot-url    {{ background: #e3f2fd; color: #1565c0; }}
  .dot-idea   {{ background: #fff8e1; color: #f57f17; }}
  .dot-list   {{ background: var(--c-primary-l); color: var(--c-primary); }}

  .card-body {{ flex: 1; min-width: 0; }}

  .card-name {{
    font-size: 0.93rem;
    font-weight: 700;
    color: var(--c-text);
    margin-bottom: 6px;
    line-height: 1.45;
    word-break: break-all;
  }}

  .card-name a {{
    color: var(--c-primary);
    text-decoration: none;
  }}

  .card-name a:hover {{ text-decoration: underline; }}

  .tag-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }}

  .tag {{
    font-size: 0.68rem;
    font-weight: 700;
    padding: 2px 9px;
    border-radius: 6px;
    letter-spacing: .02em;
  }}

  .t-piri   {{ background: #fce4ec; color: #c62828; }}
  .t-sappa  {{ background: #e1f5fe; color: #0277bd; }}
  .t-kotte  {{ background: #fff3e0; color: #e65100; }}
  .t-ama    {{ background: #fffde7; color: #f9a825; }}
  .t-uma    {{ background: #f3e5f5; color: #6a1b9a; }}
  .t-kawa   {{ background: #ede7f6; color: #4527a0; }}
  .t-genre  {{ background: var(--c-primary-l); color: var(--c-primary); }}
  .t-cat    {{ background: #f5f5f5; color: #616161; }}
  .t-event  {{ background: var(--c-accent-l); color: #7b5900; }}

  .card-chevron {{
    color: var(--c-muted);
    margin-top: 5px;
    flex-shrink: 0;
    transition: transform .25s cubic-bezier(.4,0,.2,1);
    opacity: .6;
  }}

  .card-chevron .material-icons-round {{ font-size: 1.1rem; }}

  .card.open .card-chevron {{ transform: rotate(180deg); opacity: 1; }}

  /* ── CARD DETAIL ────────────────────────── */
  .card-detail {{
    max-height: 0;
    overflow: hidden;
    transition: max-height .35s cubic-bezier(.4,0,.2,1);
  }}

  .card.open .card-detail {{ max-height: 600px; }}

  .card-detail-inner {{
    border-top: 1px solid var(--c-border);
    padding: 14px 16px 16px;
  }}

  .card-desc {{
    font-size: 0.84rem;
    color: var(--c-muted);
    margin-bottom: 12px;
    line-height: 1.7;
  }}

  .recipe-body {{
    font-size: 0.8rem;
    line-height: 1.85;
    color: #3a4e3f;
    background: linear-gradient(135deg, #f0f9f2, #e8f5ed);
    border: 1px solid #c8e6c9;
    border-radius: var(--radius-sm);
    padding: 12px 14px;
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 380px;
    overflow-y: auto;
    margin-bottom: 12px;
  }}

  .recipe-body::-webkit-scrollbar {{ width: 5px; }}
  .recipe-body::-webkit-scrollbar-track {{ background: #e8f5ed; }}
  .recipe-body::-webkit-scrollbar-thumb {{ background: #a5d6a7; border-radius: 3px; }}

  .btn-link {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, var(--c-primary), var(--c-primary-d));
    color: #fff;
    text-decoration: none;
    padding: 10px 20px;
    border-radius: var(--radius-lg);
    font-size: 0.85rem;
    font-weight: 700;
    box-shadow: 0 3px 10px rgba(30,126,68,.3);
    transition: box-shadow .2s, transform .15s;
    letter-spacing: .02em;
  }}

  .btn-link:hover {{
    box-shadow: 0 5px 16px rgba(30,126,68,.4);
    transform: translateY(-1px);
  }}

  .btn-link .material-icons-round {{ font-size: 1rem; }}

  .card-meta {{
    font-size: 0.68rem;
    color: #b0bec5;
    margin-top: 10px;
    display: flex;
    align-items: center;
    gap: 4px;
  }}

  .card-meta .material-icons-round {{ font-size: 0.85rem; }}

  /* ── EMPTY STATE ────────────────────────── */
  .empty-state {{
    text-align: center;
    padding: 60px 24px;
    color: var(--c-muted);
  }}

  .empty-state .material-icons-round {{
    font-size: 3.5rem;
    color: #c8e6c9;
    display: block;
    margin-bottom: 14px;
  }}

  .empty-state p {{ font-size: 0.95rem; line-height: 1.8; }}

  /* ── FOOTER ─────────────────────────────── */
  .site-footer {{
    text-align: center;
    padding: 28px 16px;
    font-size: 0.75rem;
    color: #aaa;
  }}

  /* ── SCROLLBAR (desktop) ────────────────── */
  @media (min-width: 600px) {{
    body::-webkit-scrollbar {{ width: 7px; }}
    body::-webkit-scrollbar-track {{ background: var(--c-bg); }}
    body::-webkit-scrollbar-thumb {{ background: #a5d6a7; border-radius: 4px; }}
  }}
</style>
</head>
<body>

<!-- HEADER -->
<header class="site-header">
  <div class="header-inner">
    <div class="header-title">
      <span class="icon-leaf">🥒</span>
      <h1>きゅうりレシピファインダー</h1>
    </div>
    <div style="display:flex;gap:8px;align-items:center;">
      <div class="search-wrap" style="flex:1;">
        <span class="material-icons-round">search</span>
        <input type="search" id="searchInput" placeholder="レシピ名・食材で検索…" autocomplete="off">
      </div>
      <div class="count-pill" id="countBadge">－件</div>
    </div>
  </div>
</header>

<!-- FILTER PANEL -->
<div class="filter-panel">
  <div class="filter-inner">
    <div class="filter-row">
      <span class="filter-row-label">味系統</span>
      <div class="chips" id="flavorChips">
        <span class="chip chip-reset" onclick="resetAll()">
          <span class="material-icons-round" style="font-size:.85rem;">refresh</span>リセット
        </span>
      </div>
    </div>
    <div class="filter-row">
      <span class="filter-row-label">ジャンル</span>
      <div class="chips" id="genreChips"></div>
    </div>
    <div class="filter-row">
      <span class="filter-row-label">行事</span>
      <div class="chips" id="eventChips"></div>
    </div>
    <div class="filter-row">
      <span class="filter-row-label">食材</span>
      <div class="chips" id="ingredientChips"></div>
    </div>
    <div class="filter-row">
      <span class="filter-row-label">種別</span>
      <div class="chips" id="typeChips">
        <span class="chip" data-group="type" data-val="full_recipe" onclick="toggleChip(this)">完全レシピ</span>
        <span class="chip" data-group="type" data-val="url" onclick="toggleChip(this)">外部リンク</span>
        <span class="chip" data-group="type" data-val="idea" onclick="toggleChip(this)">アイデア</span>
        <span class="chip" data-group="type" data-val="list_item" onclick="toggleChip(this)">アレンジ案</span>
      </div>
    </div>
  </div>
</div>

<!-- CARD LIST -->
<div class="card-list" id="cardList"></div>

<footer class="site-footer">
  <span>きゅうりレシピファインダー &mdash; SNSレシピストックより生成</span>
</footer>

<script>
const RECIPES = {recipes_json};

const activeFilters = {{
  flavor: new Set(), genre: new Set(), event: new Set(),
  ingredient: new Set(), type: new Set(),
}};
let searchQuery = "";

// ── チップ定義 ──────────────────────────────
const FLAVOR_DEF = [
  {{v:"ピリ辛",cls:"t-piri"}},{{v:"さっぱり",cls:"t-sappa"}},
  {{v:"こってり",cls:"t-kotte"}},{{v:"甘め",cls:"t-ama"}},
  {{v:"旨辛",cls:"t-uma"}},{{v:"変わり種",cls:"t-kawa"}},
];
const GENRE_DEF  = ["和風","洋風","韓国風","中華風","エスニック"];
const EVENT_DEF  = ["バレンタイン","節分","ひなまつり","みどりの日","お正月","マヨネーズの日"];
const ING_DEF    = ["ごま","梅","チーズ","にんにく","マヨネーズ","ツナ","わさび",
                    "みそ","醤油","明太子","ヨーグルト","コチュジャン","ごま油","アンチョビ"];

function buildChips() {{
  const fc = document.getElementById("flavorChips");
  FLAVOR_DEF.forEach(d => {{
    const c = makeChip(d.v, "flavor", d.cls); fc.appendChild(c);
  }});
  const gc = document.getElementById("genreChips");
  GENRE_DEF.forEach(v => gc.appendChild(makeChip(v, "genre", "t-genre")));
  const ec = document.getElementById("eventChips");
  EVENT_DEF.forEach(v => ec.appendChild(makeChip(v, "event", "t-event")));
  const ic = document.getElementById("ingredientChips");
  ING_DEF.forEach(v => ic.appendChild(makeChip(v, "ingredient", "t-cat")));
}}

function makeChip(val, group, tagCls) {{
  const c = document.createElement("span");
  c.className = `chip ${{tagCls}}`;
  c.dataset.group = group; c.dataset.val = val;
  c.textContent = val;
  c.onclick = () => toggleChip(c);
  return c;
}}

function toggleChip(el) {{
  const {{group, val}} = el.dataset;
  if (el.classList.toggle("active")) activeFilters[group].add(val);
  else activeFilters[group].delete(val);
  syncReset(); render();
}}

function resetAll() {{
  Object.values(activeFilters).forEach(s => s.clear());
  document.querySelectorAll(".chip.active").forEach(c => c.classList.remove("active"));
  searchQuery = ""; document.getElementById("searchInput").value = "";
  syncReset(); render();
}}

function syncReset() {{
  const dirty = Object.values(activeFilters).some(s => s.size > 0) || searchQuery;
  document.querySelector(".chip-reset").classList.toggle("dirty", !!dirty);
}}

// ── フィルタリング ───────────────────────────
function matchesFilters(r) {{
  const q = searchQuery.toLowerCase();
  if (q) {{
    const t = (r.name + " " + r.description + " " + (r.combo||"") +
               (r.ingredients_key||[]).join(" ") + " " + (r.full_recipe||"")).toLowerCase();
    if (!t.includes(q)) return false;
  }}
  const chk = (key, arr) => !activeFilters[key].size || (arr||[]).some(v => activeFilters[key].has(v));
  return chk("flavor",r.flavor) && chk("genre",r.genre) && chk("event",r.events) &&
         chk("ingredient",r.ingredients_key) &&
         (!activeFilters.type.size || activeFilters.type.has(r.source_type));
}}

// ── カード生成 ──────────────────────────────
const TYPE_ICON = {{
  full_recipe: ["description","dot-full"],
  url:         ["link","dot-url"],
  idea:        ["lightbulb","dot-idea"],
  list_item:   ["eco","dot-list"],
}};

const FLAVOR_CLS = {{
  "ピリ辛":"t-piri","さっぱり":"t-sappa","こってり":"t-kotte",
  "甘め":"t-ama","旨辛":"t-uma","変わり種":"t-kawa",
}};

function tag(text, cls) {{
  return `<span class="tag ${{cls}}">${{esc(text)}}</span>`;
}}

function buildCard(r) {{
  const [icon, dotCls] = TYPE_ICON[r.source_type] || ["eco","dot-list"];

  const tags = [
    ...(r.flavor||[]).map(f => tag(f, FLAVOR_CLS[f]||"t-cat")),
    ...(r.genre||[]).map(g => tag(g,"t-genre")),
    ...(r.events||[]).map(e => tag(e,"t-event")),
    ...(r.category||[]).slice(0,2).map(c => tag(c,"t-cat")),
  ].join("");

  const nameHtml = r.url
    ? `<a href="${{r.url}}" target="_blank" rel="noopener">${{esc(r.name)}}</a>`
    : esc(r.name);

  const detail = `
    <div class="card-detail">
      <div class="card-detail-inner">
        ${{r.description ? `<p class="card-desc">${{esc(r.description)}}</p>` : ""}}
        ${{r.full_recipe ? `<div class="recipe-body">${{esc(r.full_recipe)}}</div>` : ""}}
        ${{r.url ? `<a href="${{r.url}}" target="_blank" rel="noopener" class="btn-link">
            <span class="material-icons-round">open_in_new</span>レシピを見る</a>` : ""}}
        ${{r.date ? `<div class="card-meta">
            <span class="material-icons-round">calendar_today</span>${{r.date}}</div>` : ""}}
      </div>
    </div>`;

  const div = document.createElement("div");
  div.className = "card";
  div.innerHTML = `
    <div class="card-hd" onclick="toggleCard(this)">
      <div class="card-type-dot ${{dotCls}}">
        <span class="material-icons-round">${{icon}}</span>
      </div>
      <div class="card-body">
        <div class="card-name">${{nameHtml}}</div>
        <div class="tag-row">${{tags}}</div>
      </div>
      <div class="card-chevron">
        <span class="material-icons-round">expand_more</span>
      </div>
    </div>
    ${{detail}}`;
  return div;
}}

function toggleCard(hd) {{
  hd.closest(".card").classList.toggle("open");
}}

function esc(s) {{
  if(!s) return "";
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}}

// ── レンダリング ────────────────────────────
const ORDER = {{full_recipe:0,url:1,idea:2,list_item:3}};

function render() {{
  const list = document.getElementById("cardList");
  const filtered = RECIPES.filter(matchesFilters);
  document.getElementById("countBadge").textContent = filtered.length + "件";

  if (filtered.length === 0) {{
    list.innerHTML = `<div class="empty-state">
      <span class="material-icons-round">search_off</span>
      <p>条件に合うレシピが見つかりませんでした。<br>フィルターを変えてみてください。</p>
    </div>`;
    return;
  }}

  filtered.sort((a,b) => (ORDER[a.source_type]||9) - (ORDER[b.source_type]||9));
  const frag = document.createDocumentFragment();
  filtered.forEach(r => frag.appendChild(buildCard(r)));
  list.innerHTML = ""; list.appendChild(frag);
}}

document.getElementById("searchInput").addEventListener("input", e => {{
  searchQuery = e.target.value.trim();
  syncReset(); render();
}});

buildChips(); render();
</script>
</body>
</html>"""

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ HTML生成完了: {OUTPUT_PATH}")
print(f"   レシピ数: {len(recipes)}件")
