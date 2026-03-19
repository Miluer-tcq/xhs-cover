# xhs-cover

A lightweight Claude Code skill for generating Xiaohongshu (小红书) cover images locally with pure Pillow.

It turns a title, subtitle, tag, and short step list into a styled `1242x1660` PNG cover without Playwright or Chromium.

## Features

- Pure Pillow rendering
- No browser dependency
- Works well for 小红书封面 / 首图 / cover image / thumbnail
- Simple install: just `SKILL.md` + `scripts/cover.py`

## Repository layout

```text
xhs-cover/
├─ SKILL.md
└─ scripts/
   └─ cover.py
```

## Install

### Option 1: install globally

Copy or clone this repository into:

```bash
~/.claude/skills/xhs-cover
```

### Option 2: install for one project only

Copy or clone this repository into:

```bash
<your-project>/.claude/skills/xhs-cover
```

## Dependency

Install Pillow:

```bash
pip install pillow
```

Or:

```bash
uv pip install pillow
```

## Usage

After the skill is installed, ask Claude Code things like:

- 帮我做一个小红书封面
- 给这篇笔记生成首图
- Generate an XHS cover for this post
- Create a cover image with 4 steps and a comparison box

You can also run the bundled script directly:

```bash
python scripts/cover.py "AI做小红书封面终于不用熬夜了" \
  --subtitle "纯 Pillow 生成，更稳更省依赖" \
  --tag "封面优化" \
  --steps "提炼标题重点" "自动生成排版" "补齐视觉元素" "导出 PNG 直接发布" \
  --hl-left "4小时" \
  --hl-right "15分钟" \
  --hl-left-label "手工排版反复改" \
  --hl-right-label "AI 协作快速成图" \
  -o ./cover.png
```

## Output

- Format: PNG
- Resolution: `1242 x 1660`
- Style: notebook-style Xiaohongshu cover

## Notes

- Keep cover text short for the best layout.
- The generator auto-wraps and auto-shrinks text when needed.
- Windows users will get the best Chinese rendering if Microsoft YaHei is available.
