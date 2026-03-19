---
name: xhs-cover
description: >
  Generate Xiaohongshu (Little Red Book) cover images locally with pure Pillow.
  Use this whenever the user asks for 小红书封面、首图、cover image、thumbnail、social post graphic,
  especially when they want a fast local PNG without browser or Playwright.
  Turn a title, subtitle, tag, and 3-5 short steps into a styled 1242x1660 cover image.
compatibility: Claude Code with Bash/Read. Requires Python and Pillow.
---

# XHS Cover Generator

Use the bundled `scripts/cover.py` generator instead of writing a new cover renderer from scratch.
Resolve the script path relative to this skill folder instead of assuming a fixed install location.

## When to use this skill

Use this skill when the user wants any of the following:
- 小红书封面 / 首图
- Xiaohongshu cover / XHS cover
- cover image / thumbnail / social post graphic
- a fast local image generator with low dependencies
- a browser-free alternative to Playwright/Chromium rendering

## What to collect

Required:
- `title`

Optional:
- `subtitle`
- `tag`
- `steps` (prefer 3-5 short items)
- `footer`
- `hl-left`
- `hl-right`
- `hl-left-label`
- `hl-right-label`
- `output`

If the user gives only a rough request, infer sensible defaults and continue.
Only ask follow-up questions when the title or desired output path is unclear.

## How to generate

1. Use the bundled `scripts/cover.py`.
2. Save the PNG in the current project unless the user asked for another location.
3. Prefer concise text. If text is too long, shorten it rather than forcing overflow.
4. If the user asks for multiple options, generate 2-3 variants by changing emphasis, tag, steps, or comparison copy.
5. If the user asks to tweak visual style, keep the existing notebook-style layout unless they explicitly want a new template.

## Command pattern

Resolve the absolute path to this skill's `scripts/cover.py`, then run it with Python.
Do not assume the skill is always installed in a project-local `.claude/skills/` path.

Example command shape:

```bash
python <absolute-path-to-this-skill>/scripts/cover.py "标题" --subtitle "副标题" --tag "效率干货" --steps "步骤1" "步骤2" "步骤3" -o ./cover.png
```

Useful options:
- `--footer`
- `--hl-left`
- `--hl-right`
- `--hl-left-label`
- `--hl-right-label`
- `--seed`
- `-o` / `--output`

## Example

```bash
python <absolute-path-to-this-skill>/scripts/cover.py "AI做小红书封面终于不用熬夜了" \
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

## Dependency

```bash
uv pip install pillow
```

Or:

```bash
pip install pillow
```
