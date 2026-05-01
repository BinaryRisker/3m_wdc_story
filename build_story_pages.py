#!/usr/bin/env python3
"""将 story_novel_final.md 转换为带目录的样式 HTML，用于 GitHub Pages"""
import sys
import re
from pathlib import Path
from markdown import Markdown
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent
SRC = PROJECT_ROOT / "docs" / "story_novel_final.md"
OUT = PROJECT_ROOT / "index.html"


def md_to_html(md_text):
    """Convert markdown to HTML and extract heading IDs from rendered output."""
    m = Markdown(extensions=[
        'fenced_code', 'tables', 'toc', 'sane_lists',
        'nl2br', 'extra', 'abbr', 'attr_list', 'def_list', 'footnotes'
    ])
    content_html = m.convert(md_text)
    # Extract headings with their actual IDs from rendered HTML
    headings = []
    for match in re.finditer(
        r'<h([1-4])(?:\s[^>]*)?id="([^"]*)"[^>]*>(.*?)</h\1>',
        content_html, re.DOTALL
    ):
        level = int(match.group(1))
        slug = match.group(2)
        inner = match.group(3)
        # Strip HTML tags to get plain text
        text = re.sub(r'<[^>]+>', '', inner).strip()
        headings.append((level, text, slug))
    return content_html, headings


def build_sidebar(headings):
    """Build a styled collapsible sidebar TOC from headings."""
    # Group: volumes (h1 with "第X卷") contain chapters (h2), standalone h1 are flat items
    volumes = []  # list of {title, slug, children: [{title, slug}]}
    standalone = []  # items before first volume or non-volume h1

    current_volume = None
    for level, text, slug in headings:
        if level == 1:
            is_volume = bool(re.search(r'第[一二三四五六七八九十]+卷', text))
            if is_volume:
                current_volume = {'title': text, 'slug': slug, 'children': []}
                volumes.append(current_volume)
            else:
                current_volume = None
                standalone.append({'title': text, 'slug': slug, 'children': []})
        elif level == 2 and current_volume is not None:
            current_volume['children'].append({'title': text, 'slug': slug})
        elif level == 2:
            standalone.append({'title': text, 'slug': slug, 'children': []})

    html_parts = []

    # Standalone items (序章, 角色谱系, etc.)
    for item in standalone:
        html_parts.append(
            f'<div class="nav-item nav-standalone">'
            f'<a href="#{item["slug"]}" class="nav-link">'
            f'<span class="nav-text">{item["title"]}</span>'
            f'</a></div>'
        )

    # Volume groups
    for vol in volumes:
        child_count = len(vol['children'])
        badge = f'<span class="nav-badge">{child_count}</span>' if child_count else ''
        children_html = ''
        for ch in vol['children']:
            children_html += (
                f'<div class="nav-item nav-chapter">'
                f'<a href="#{ch["slug"]}" class="nav-link">'
                f'<span class="nav-text">{ch["title"]}</span>'
                f'</a></div>'
            )
        html_parts.append(
            f'<div class="nav-group">'
            f'<div class="nav-item nav-volume" onclick="toggleGroup(this)">'
            f'<a href="#{vol["slug"]}" class="nav-link" onclick="event.stopPropagation()">'
            f'<span class="nav-arrow">&#9654;</span>'
            f'<span class="nav-text">{vol["title"]}</span>'
            f'{badge}'
            f'</a></div>'
            f'<div class="nav-children">{children_html}</div>'
            f'</div>'
        )

    return '\n'.join(html_parts)


def build_page(content_html, sidebar_html):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3分钟神探：神经时代</title>
<style>
  /* ===== Themes ===== */
  :root, [data-theme="dark"] {{
    --bg: #0d1117;
    --surface: #161b22;
    --surface-hover: #1c2128;
    --surface-active: #22303e;
    --border: #30363d;
    --text: #c9d1d9;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --accent-dim: #1f6feb33;
    --chapter: #f0883e;
    --font: 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
    --mono: 'Cascadia Code', 'Fira Code', monospace;
    --sidebar-width: 280px;
  }}
  [data-theme="light"] {{
    --bg: #f8f9fa;
    --surface: #ffffff;
    --surface-hover: #f0f1f3;
    --surface-active: #e6e8eb;
    --border: #d0d7de;
    --text: #24292f;
    --text-muted: #636c76;
    --accent: #0969da;
    --accent-dim: #0969da22;
    --chapter: #d47d25;
  }}
  [data-theme="sepia"] {{
    --bg: #f4ecd8;
    --surface: #faf6eb;
    --surface-hover: #ede4ce;
    --surface-active: #e3d8bc;
    --border: #d4c8a8;
    --text: #5c4634;
    --text-muted: #8a7355;
    --accent: #b5732a;
    --accent-dim: #b5732a22;
    --chapter: #a85a1f;
    --font: 'Georgia', 'PingFang SC', 'Microsoft YaHei', 'STSong', 'SimSun', serif;
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
    transition: background 0.3s, color 0.3s;
    overflow-wrap: break-word;
    word-break: break-all;
  }}

  /* ===== Theme Switcher ===== */
  #theme-switcher {{
    display: flex;
    gap: 4px;
    padding: 12px 16px 10px;
    border-bottom: 1px solid var(--border);
  }}
  .theme-btn {{
    flex: 1;
    padding: 5px 0;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: transparent;
    color: var(--text-muted);
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
  }}
  .theme-btn:hover {{ background: var(--surface-hover); color: var(--text); }}
  .theme-btn.active {{
    background: var(--accent);
    color: #fff;
    border-color: var(--accent);
  }}

  /* ===== Sidebar ===== */
  #sidebar {{
    position: fixed;
    top: 0;
    left: 0;
    width: var(--sidebar-width);
    height: 100vh;
    background: var(--surface);
    border-right: 1px solid var(--border);
    z-index: 150;
    display: flex;
    flex-direction: column;
    transition: transform 0.3s ease, background 0.3s;
  }}
  #sidebar.closed {{ transform: translateX(-100%); }}

  .sidebar-header {{
    padding: 14px 16px 10px;
    border-bottom: 1px solid var(--border);
  }}
  .sidebar-header h3 {{
    color: var(--accent);
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.08em;
  }}

  /* ===== Sidebar Navigation ===== */
  .nav-scroll {{
    flex: 1;
    overflow-y: auto;
    padding: 6px 0;
  }}
  .nav-item {{ position: relative; }}
  .nav-link {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 16px;
    color: var(--text-muted);
    text-decoration: none;
    font-size: 13.5px;
    line-height: 1.5;
    transition: all 0.15s;
    border-radius: 0;
    position: relative;
  }}
  .nav-link:hover {{
    background: var(--surface-hover);
    color: var(--text);
  }}
  .nav-link.active {{
    color: var(--accent);
    background: var(--surface-active);
  }}
  .nav-link.active::before {{
    content: '';
    position: absolute;
    left: 0;
    top: 4px;
    bottom: 4px;
    width: 3px;
    background: var(--accent);
    border-radius: 0 2px 2px 0;
  }}

  /* Volume items */
  .nav-volume {{
    cursor: pointer;
  }}
  .nav-volume .nav-link {{
    font-weight: 600;
    color: var(--text);
    font-size: 13.5px;
    padding-left: 12px;
  }}
  .nav-volume .nav-link:hover {{ background: var(--surface-hover); }}
  .nav-volume .nav-link.active {{ color: var(--accent); background: var(--surface-active); }}

  .nav-arrow {{
    display: inline-block;
    font-size: 8px;
    transition: transform 0.2s;
    opacity: 0.5;
    flex-shrink: 0;
    width: 14px;
    text-align: center;
  }}
  .nav-group.expanded .nav-arrow {{ transform: rotate(90deg); opacity: 0.8; }}

  .nav-badge {{
    font-size: 10px;
    background: var(--surface-hover);
    color: var(--text-muted);
    padding: 1px 6px;
    border-radius: 10px;
    margin-left: auto;
    flex-shrink: 0;
  }}

  /* Chapter children container */
  .nav-children {{
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.35s ease;
  }}
  .nav-group.expanded .nav-children {{ max-height: 5000px; }}

  .nav-chapter .nav-link {{
    padding-left: 38px;
    font-size: 13px;
    font-weight: 400;
    color: var(--text-muted);
  }}
  .nav-chapter .nav-link::before {{
    content: '';
    position: absolute;
    left: 24px;
    top: 50%;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--border);
    transform: translateY(-50%);
    transition: background 0.15s;
  }}
  .nav-chapter .nav-link:hover::before {{ background: var(--text-muted); }}
  .nav-chapter .nav-link.active::before {{ background: var(--accent); }}
  .nav-chapter .nav-link.active {{
    color: var(--accent);
    background: var(--surface-active);
  }}

  /* Standalone items (序章, 角色谱系, etc.) */
  .nav-standalone .nav-link {{
    font-weight: 500;
    color: var(--text);
    padding-left: 16px;
  }}

  /* ===== Mobile ===== */
  #sidebar-toggle {{
    display: none;
    position: fixed;
    top: 8px;
    left: 8px;
    z-index: 200;
    width: 40px;
    height: 40px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 20px;
    cursor: pointer;
    align-items: center;
    justify-content: center;
  }}
  #topbar {{
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 48px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    z-index: 190;
    align-items: center;
    padding: 0 12px 0 56px;
    gap: 8px;
  }}
  #topbar .topbar-title {{
    color: var(--accent);
    font-size: 14px;
    font-weight: 600;
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  #topbar .theme-btn {{ padding: 4px 10px; font-size: 11px; }}

  #sidebar-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.4);
    z-index: 140;
  }}
  #sidebar-overlay.open {{ display: block; }}

  @media (max-width: 768px) {{
    #sidebar-toggle {{ display: flex; }}
    #topbar {{ display: flex; }}
    #sidebar {{ width: 270px; transform: translateX(-100%); }}
    #sidebar.open {{ transform: translateX(0); }}
    .main-wrapper {{ margin-left: 0; padding-top: 56px; }}
    .container {{ padding: 1rem 0.8rem 4rem; }}
    header {{ padding: 1.5rem 0 1rem; }}
    header h1 {{ font-size: 1.3rem; }}
    header .subtitle {{ font-size: 0.85rem; }}
    .content h1 {{ font-size: 1.2rem; scroll-margin-top: 56px; }}
    .content h2 {{ font-size: 1.05rem; scroll-margin-top: 56px; }}
    .content h3 {{ scroll-margin-top: 56px; }}
    .content p {{ margin: 0.6rem 0; }}
    .content table {{ font-size: 0.8rem; }}
    .content th, .content td {{ padding: 0.35rem 0.5rem; }}
  }}

  /* ===== Main Content ===== */
  .main-wrapper {{
    margin-left: var(--sidebar-width);
    transition: margin-left 0.3s ease;
  }}
  .container {{
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem 2.5rem 6rem;
  }}
  header {{
    text-align: center;
    padding: 3rem 0 2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
  }}
  header h1 {{
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
  }}
  header .subtitle {{ color: var(--text-muted); font-size: 0.95rem; }}
  header .meta {{ margin-top: 1rem; font-size: 0.85rem; color: var(--text-muted); }}

  .content h1, .content h2, .content h3, .content h4 {{
    color: var(--text);
    font-weight: 600;
    margin: 2rem 0 1rem;
    line-height: 1.4;
    scroll-margin-top: 60px;
  }}
  .content h1 {{
    font-size: 1.5rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    color: var(--accent);
    margin-top: 2.5rem;
  }}
  .content h2 {{
    font-size: 1.2rem;
    color: var(--chapter);
    margin-top: 2rem;
  }}
  .content h3 {{ font-size: 1.05rem; }}
  .content p {{ margin: 0.8rem 0; }}
  .content hr {{ border: none; border-top: 1px solid var(--border); margin: 2rem 0; }}
  .content strong {{ color: var(--text); }}
  .content em {{ color: var(--text-muted); font-style: italic; }}
  .content a {{ color: var(--accent); text-decoration: none; border-bottom: 1px solid var(--accent-dim); }}
  .content a:hover {{ border-bottom-color: var(--accent); }}
  .content ul, .content ol {{ padding-left: 1.5rem; margin: 0.8rem 0; }}
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
  .content pre code {{ background: none; border: none; padding: 0; font-size: 0.85rem; }}
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
  .content th {{ background: var(--surface); color: var(--accent); }}
  .content tr:nth-child(even) td {{ background: var(--surface); }}

  /* Progress bar */
  #progress {{
    position: fixed;
    top: 0; left: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--chapter));
    width: 0%;
    z-index: 300;
    transition: width 0.1s;
  }}

  footer {{
    text-align: center;
    padding: 3rem 0 2rem;
    color: var(--text-muted);
    font-size: 0.8rem;
    border-top: 1px solid var(--border);
    margin-top: 4rem;
  }}

  /* Scrollbar */
  ::-webkit-scrollbar {{ width: 6px; }}
  ::-webkit-scrollbar-track {{ background: var(--bg); }}
  ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}
</style>
</head>
<body>
<div id="progress"></div>
<button id="sidebar-toggle" onclick="toggleSidebar()">&#9776;</button>
<div id="sidebar-overlay" onclick="toggleSidebar()"></div>
<div id="topbar">
  <span class="topbar-title">3分钟神探：神经时代</span>
  <button class="theme-btn" data-theme="dark" onclick="setTheme('dark')">深</button>
  <button class="theme-btn" data-theme="light" onclick="setTheme('light')">浅</button>
  <button class="theme-btn" data-theme="sepia" onclick="setTheme('sepia')">护</button>
</div>
<div id="sidebar">
  <div id="theme-switcher">
    <button class="theme-btn active" data-theme="dark" onclick="setTheme('dark')">深色</button>
    <button class="theme-btn" data-theme="light" onclick="setTheme('light')">浅色</button>
    <button class="theme-btn" data-theme="sepia" onclick="setTheme('sepia')">护眼</button>
  </div>
  <div class="sidebar-header"><h3>目 录</h3></div>
  <div class="nav-scroll">
    {sidebar_html}
  </div>
</div>
<div class="main-wrapper">
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
</div>
<script>
  // Theme
  function setTheme(t) {{
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('story-theme', t);
    document.querySelectorAll('.theme-btn[data-theme]').forEach(b =>
      b.classList.toggle('active', b.getAttribute('data-theme') === t)
    );
  }}
  const saved = localStorage.getItem('story-theme');
  if (saved) {{ document.documentElement.setAttribute('data-theme', saved); }}
  setTheme(document.documentElement.getAttribute('data-theme') || 'dark');

  // Sidebar toggle
  function toggleSidebar() {{
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('sidebar').classList.toggle('closed');
    document.getElementById('sidebar-overlay').classList.toggle('open');
  }}

  // Collapsible volume groups
  function toggleGroup(el) {{
    const group = el.closest('.nav-group');
    group.classList.toggle('expanded');
  }}

  // Progress bar
  window.addEventListener('scroll', () => {{
    const pct = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight) * 100;
    document.getElementById('progress').style.width = pct + '%';
  }});

  // Active heading tracking + auto-expand
  const navLinks = document.querySelectorAll('.nav-scroll .nav-link');
  const headings = document.querySelectorAll('.content h1[id], .content h2[id], .content h3[id]');

  const obs = new IntersectionObserver(entries => {{
    entries.forEach(entry => {{
      if (!entry.isIntersecting) return;
      const id = entry.target.id;
      navLinks.forEach(l => l.classList.remove('active'));
      const active = document.querySelector(`.nav-link[href="#${{id}}"]`);
      if (!active) return;
      active.classList.add('active');
      // Auto-expand parent volume
      const group = active.closest('.nav-group');
      if (group && !group.classList.contains('expanded')) {{
        group.classList.add('expanded');
      }}
      // Scroll sidebar to show active item
      const scroll = active.closest('.nav-scroll');
      if (scroll) {{
        const top = active.offsetTop - scroll.offsetTop - scroll.clientHeight / 3;
        if (top > scroll.scrollTop || top < scroll.scrollTop - scroll.clientHeight / 2) {{
          scroll.scrollTo({{ top: Math.max(0, top), behavior: 'smooth' }});
        }}
      }}
    }});
  }}, {{ rootMargin: '-80px 0px -60% 0px' }});
  headings.forEach(h => obs.observe(h));

  // Expand first volume on load
  const firstGroup = document.querySelector('.nav-group');
  if (firstGroup) firstGroup.classList.add('expanded');
</script>
</body>
</html>"""


def main():
    if not SRC.exists():
        print(f"Error: {SRC} not found")
        sys.exit(1)

    md_text = SRC.read_text(encoding="utf-8")
    content_html, headings = md_to_html(md_text)
    sidebar_html = build_sidebar(headings)
    page = build_page(content_html, sidebar_html)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"Built: {OUT} ({len(page)} bytes)")


if __name__ == "__main__":
    main()
