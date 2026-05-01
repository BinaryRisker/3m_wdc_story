#!/usr/bin/env python3
"""将 story_novel_final.md 转换为带样式的 HTML，用于 GitHub Pages"""
import sys
from pathlib import Path
from markdown import Markdown
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "docs" / "story_novel_final.md"
OUT = PROJECT_ROOT / "story-site" / "index.html"

def md_to_html(md_text):
    m = Markdown(extensions=[
        'fenced_code', 'tables', 'toc', 'sane_lists',
        'nl2br', 'extra', 'abbr', 'attr_list', 'def_list', 'footnotes'
    ])
    return m.convert(md_text)

def build_page(content_html):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3分钟神探：神经时代</title>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --accent-dim: #1f6feb33;
    --chapter: #f0883e;
    --font: 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
    --mono: 'Cascadia Code', 'Fira Code', monospace;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    font-size: 16px;
    line-height: 1.8;
    min-height: 100vh;
  }}
  .container {{
    max-width: 760px;
    margin: 0 auto;
    padding: 2rem 1.5rem 6rem;
  }}
  header {{
    text-align: center;
    padding: 4rem 0 3rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 3rem;
  }}
  header h1 {{
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
  }}
  header .subtitle {{
    color: var(--text-muted);
    font-size: 0.95rem;
  }}
  header .meta {{
    margin-top: 1rem;
    font-size: 0.85rem;
    color: var(--text-muted);
  }}
  /* Markdown content styles */
  .content h1, .content h2, .content h3, .content h4 {{
    color: #e6edf3;
    font-weight: 600;
    margin: 2rem 0 1rem;
    line-height: 1.3;
  }}
  .content h1 {{
    font-size: 1.6rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    color: var(--accent);
  }}
  .content h2 {{
    font-size: 1.3rem;
    color: var(--chapter);
  }}
  .content h3 {{ font-size: 1.1rem; }}
  .content p {{ margin: 0.8rem 0; }}
  .content hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
  }}
  .content strong {{ color: #e6edf3; }}
  .content em {{ color: var(--text-muted); font-style: italic; }}
  .content a {{
    color: var(--accent);
    text-decoration: none;
    border-bottom: 1px solid var(--accent-dim);
  }}
  .content a:hover {{ border-bottom-color: var(--accent); }}
  .content ul, .content ol {{
    padding-left: 1.5rem;
    margin: 0.8rem 0;
  }}
  .content li {{ margin: 0.3rem 0; }}
  .content blockquote {{
    border-left: 3px solid var(--chapter);
    padding: 0.5rem 1rem;
    margin: 1.5rem 0;
    background: var(--surface);
    border-radius: 0 4px 4px 0;
    color: var(--text-muted);
  }}
  .content code {{
    font-family: var(--mono);
    background: var(--surface);
    padding: 0.15rem 0.4rem;
    border-radius: 3px;
    font-size: 0.88em;
    border: 1px solid var(--border);
  }}
  .content pre {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
    overflow-x: auto;
    margin: 1rem 0;
  }}
  .content pre code {{
    background: none;
    border: none;
    padding: 0;
    font-size: 0.85rem;
  }}
  .content table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    font-size: 0.9rem;
  }}
  .content th, .content td {{
    border: 1px solid var(--border);
    padding: 0.5rem 0.75rem;
    text-align: left;
  }}
  .content th {{
    background: var(--surface);
    color: var(--accent);
  }}
  .content tr:nth-child(even) td {{ background: var(--surface); }}
  /* Chapter divider */
  .content hr + h1,
  .content hr + h2 {{
    margin-top: 0.5rem;
  }}
  /* Scrollbar */
  ::-webkit-scrollbar {{ width: 6px; }}
  ::-webkit-scrollbar-track {{ background: var(--bg); }}
  ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}
  /* Reading progress bar */
  #progress {{
    position: fixed;
    top: 0; left: 0;
    height: 2px;
    background: var(--accent);
    width: 0%;
    z-index: 100;
    transition: width 0.1s;
  }}
  /* Footer */
  footer {{
    text-align: center;
    padding: 3rem 0 2rem;
    color: var(--text-muted);
    font-size: 0.8rem;
    border-top: 1px solid var(--border);
    margin-top: 4rem;
  }}
  @media (max-width: 600px) {{
    .container {{ padding: 1rem 1rem 4rem; }}
    header h1 {{ font-size: 1.5rem; }}
  }}
</style>
</head>
<body>
<div id="progress"></div>
<div class="container">
  <header>
    <h1>3分钟神探：神经时代</h1>
    <div class="subtitle">—— 全剧情小说体纪事 ——</div>
    <div class="meta">新长安2077 · 零号计划 · 意识觉醒</div>
  </header>
  <div class="content">
    {content_html}
  </div>
  <footer>
    <p>最后更新：{datetime.now().strftime('%Y-%m-%d')} · 3分钟神探</p>
  </footer>
</div>
<script>
  // Reading progress bar
  window.addEventListener('scroll', () => {{
    const scrolled = window.scrollY;
    const total = document.documentElement.scrollHeight - window.innerHeight;
    document.getElementById('progress').style.width = (scrolled / total * 100) + '%';
  }});
</script>
</body>
</html>"""

def main():
    if not SRC.exists():
        print(f"Error: {SRC} not found")
        sys.exit(1)

    md_text = SRC.read_text(encoding="utf-8")
    content_html = md_to_html(md_text)
    page = build_page(content_html)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"Built: {OUT} ({len(page)} bytes)")

if __name__ == "__main__":
    main()
