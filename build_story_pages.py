#!/usr/bin/env python3
"""将 story_novel_final.md 转换为带目录的样式 HTML，用于 GitHub Pages"""
import sys
from pathlib import Path
from markdown import Markdown
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent
SRC = PROJECT_ROOT / "docs" / "story_novel_final.md"
OUT = PROJECT_ROOT / "index.html"

def md_to_html_with_toc(md_text):
    m = Markdown(extensions=[
        'fenced_code', 'tables', 'toc', 'sane_lists',
        'nl2br', 'extra', 'abbr', 'attr_list', 'def_list', 'footnotes'
    ])
    content_html = m.convert(md_text)
    toc_html = getattr(m, 'toc', '')
    return content_html, toc_html

def build_page(content_html, toc_html):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3分钟神探：神经时代</title>
<style>
  /* ===== Theme System ===== */
  /* Dark theme (default) */
  :root, [data-theme="dark"] {{
    --bg: #0d1117;
    --surface: #161b22;
    --surface-hover: #1c2128;
    --border: #30363d;
    --text: #c9d1d9;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --accent-dim: #1f6feb33;
    --chapter: #f0883e;
    --font: 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
    --mono: 'Cascadia Code', 'Fira Code', monospace;
    --sidebar-width: 280px;
    --font-size: 16px;
    --line-height: 1.8;
  }}
  /* Light theme */
  [data-theme="light"] {{
    --bg: #f8f9fa;
    --surface: #ffffff;
    --surface-hover: #f0f1f3;
    --border: #d0d7de;
    --text: #24292f;
    --text-muted: #636c76;
    --accent: #0969da;
    --accent-dim: #0969da22;
    --chapter: #d47d25;
    --font: 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
    --mono: 'Cascadia Code', 'Fira Code', monospace;
    --sidebar-width: 280px;
    --font-size: 16px;
    --line-height: 1.8;
  }}
  /* Sepia / Eye-care theme */
  [data-theme="sepia"] {{
    --bg: #f4ecd8;
    --surface: #faf6eb;
    --surface-hover: #ede4ce;
    --border: #d4c8a8;
    --text: #5c4634;
    --text-muted: #8a7355;
    --accent: #b5732a;
    --accent-dim: #b5732a22;
    --chapter: #a85a1f;
    --font: 'Georgia', 'PingFang SC', 'Microsoft YaHei', 'STSong', 'SimSun', serif;
    --mono: 'Cascadia Code', 'Fira Code', monospace;
    --sidebar-width: 280px;
    --font-size: 17px;
    --line-height: 1.9;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    font-size: var(--font-size);
    line-height: var(--line-height);
    min-height: 100vh;
    transition: background 0.3s, color 0.3s;
  }}

  /* Theme Switcher */
  #theme-switcher {{
    display: flex;
    gap: 6px;
    padding: 0.75rem 1rem 0.5rem;
    border-bottom: 1px solid var(--border);
  }}
  .theme-btn {{
    flex: 1;
    padding: 6px 8px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--surface);
    color: var(--text-muted);
    font-size: 0.75rem;
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
  /* Sidebar toggle button */
  #sidebar-toggle {{
    display: none;
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 200;
    width: 44px;
    height: 44px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 1.5rem;
    cursor: pointer;
    align-items: center;
    justify-content: center;
  }}
  /* Sidebar */
  #sidebar {{
    position: fixed;
    top: 0;
    left: 0;
    width: var(--sidebar-width);
    height: 100vh;
    background: var(--surface);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    z-index: 150;
    transition: transform 0.3s ease, background 0.3s;
    display: flex;
    flex-direction: column;
  }}
  #sidebar.closed {{ transform: translateX(-100%); }}
  .sidebar-header {{
    padding: 1rem 1rem 0.75rem;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    background: var(--surface);
    z-index: 1;
  }}
  .sidebar-header h3 {{
    color: var(--accent);
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
  }}
  .toc-container {{
    padding: 0.5rem 0;
    flex: 1;
    overflow-y: auto;
  }}
  .toc-item {{
    padding: 0.3rem 1rem;
    font-size: 0.85rem;
  }}
  .toc-item a {{
    color: var(--text-muted);
    text-decoration: none;
    display: block;
    padding: 0.2rem 0;
    transition: color 0.15s;
    border-radius: 4px;
  }}
  .toc-item a:hover {{ color: var(--accent); background: var(--surface-hover); }}
  .toc-item.level-2 {{ padding-left: 2.5rem; }}
  .toc-item.level-3 {{ padding-left: 3.5rem; font-size: 0.8rem; }}
  /* Main content area */
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
  /* Markdown content styles */
  .content h1, .content h2, .content h3, .content h4 {{
    color: var(--text);
    font-weight: 600;
    margin: 2rem 0 1rem;
    line-height: 1.3;
    scroll-margin-top: 80px;
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
  /* Reading progress bar */
  #progress {{
    position: fixed;
    top: 0; left: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--chapter));
    width: 0%;
    z-index: 300;
    transition: width 0.1s;
  }}
  /* Top nav bar for mobile */
  #topbar {{
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 50px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    z-index: 190;
    align-items: center;
    justify-content: space-between;
    padding: 0 1rem;
  }}
  #topbar .topbar-title {{
    color: var(--accent);
    font-size: 0.9rem;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  /* Mobile theme switcher in topbar */
  #topbar-theme {{
    display: flex;
    gap: 4px;
  }}
  #topbar-theme .theme-btn {{
    padding: 4px 8px;
    font-size: 0.7rem;
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
  /* Mobile styles */
  @media (max-width: 768px) {{
    #sidebar-toggle {{ display: flex; }}
    #topbar {{ display: flex; }}
    #sidebar {{
      width: 260px;
      transform: translateX(-100%);
    }}
    #sidebar.open {{ transform: translateX(0); }}
    .main-wrapper {{ margin-left: 0; padding-top: 50px; }}
    .container {{ padding: 1.5rem 1rem 4rem; }}
    header h1 {{ font-size: 1.5rem; }}
    header {{ padding: 2rem 0 1.5rem; }}
    .content h1 {{ font-size: 1.3rem; margin-top: 2rem; }}
    .content h2 {{ font-size: 1.1rem; }}
  }}
  /* Scrollbar */
  ::-webkit-scrollbar {{ width: 6px; }}
  ::-webkit-scrollbar-track {{ background: var(--bg); }}
  ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}
  /* Active TOC item */
  .toc-item a.active {{ color: var(--accent) !important; font-weight: 600; background: var(--surface-hover); }}
  /* Sidebar overlay */
  #sidebar-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    z-index: 140;
  }}
  #sidebar-overlay.open {{ display: block; }}
</style>
</head>
<body>
<div id="progress"></div>
<button id="sidebar-toggle" onclick="toggleSidebar()">&#9776;</button>
<div id="sidebar-overlay" onclick="toggleSidebar()"></div>
<div id="topbar">
  <span class="topbar-title">3分钟神探：神经时代</span>
  <div id="topbar-theme">
    <button class="theme-btn" data-theme="dark" onclick="setTheme('dark')" title="深色">深</button>
    <button class="theme-btn" data-theme="light" onclick="setTheme('light')" title="浅色">浅</button>
    <button class="theme-btn" data-theme="sepia" onclick="setTheme('sepia')" title="护眼">护</button>
  </div>
</div>
<div id="sidebar">
  <div id="theme-switcher">
    <button class="theme-btn active" data-theme="dark" onclick="setTheme('dark')" title="深色模式">深色</button>
    <button class="theme-btn" data-theme="light" onclick="setTheme('light')" title="浅色模式">浅色</button>
    <button class="theme-btn" data-theme="sepia" onclick="setTheme('sepia')" title="护眼模式">护眼</button>
  </div>
  <div class="sidebar-header">
    <h3>目 录</h3>
  </div>
  <div class="toc-container">
    <div class="toc-item"><a href="#">返回顶部</a></div>
{toc_html}
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
  // Theme management
  function setTheme(theme) {{
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('story-theme', theme);
    updateThemeButtons();
  }}

  function updateThemeButtons() {{
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    document.querySelectorAll('.theme-btn[data-theme]').forEach(btn => {{
      btn.classList.toggle('active', btn.getAttribute('data-theme') === current);
    }});
  }}

  // Restore theme from localStorage
  const savedTheme = localStorage.getItem('story-theme');
  if (savedTheme) {{
    document.documentElement.setAttribute('data-theme', savedTheme);
  }}
  updateThemeButtons();

  // Toggle sidebar
  function toggleSidebar() {{
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    sidebar.classList.toggle('open');
    sidebar.classList.toggle('closed');
    overlay.classList.toggle('open');
  }}

  // Reading progress bar
  window.addEventListener('scroll', () => {{
    const scrolled = window.scrollY;
    const total = document.documentElement.scrollHeight - window.innerHeight;
    document.getElementById('progress').style.width = (scrolled / total * 100) + '%';
  }});

  // Active TOC item highlighting
  const tocItems = document.querySelectorAll('.toc-item a[href^="#"]');
  const sections = document.querySelectorAll('.content h1[id], .content h2[id], .content h3[id]');
  const observer = new IntersectionObserver((entries) => {{
    entries.forEach(entry => {{
      if (entry.isIntersecting) {{
        tocItems.forEach(item => item.classList.remove('active'));
        const id = entry.target.getAttribute('id');
        const activeItem = document.querySelector(`.toc-item a[href="#${{id}}"]`);
        if (activeItem) activeItem.classList.add('active');
      }}
    }});
  }}, {{ rootMargin: '-80px 0px -60% 0px' }});
  sections.forEach(section => observer.observe(section));

  // Back to top link
  const backToTop = document.querySelector('.toc-item a[href="#"]');
  if (backToTop) {{
    backToTop.addEventListener('click', (e) => {{
      e.preventDefault();
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }});
  }}
</script>
</body>
</html>"""

def main():
    if not SRC.exists():
        print(f"Error: {SRC} not found")
        sys.exit(1)

    md_text = SRC.read_text(encoding="utf-8")
    content_html, toc_html = md_to_html_with_toc(md_text)
    page = build_page(content_html, toc_html)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"Built: {OUT} ({len(page)} bytes)")

if __name__ == "__main__":
    main()
