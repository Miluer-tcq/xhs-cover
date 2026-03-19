# xhs-cover

一个轻量的小红书封面生成 Skill，使用纯 Pillow 在本地生成封面图。

它可以把标题、副标题、标签和步骤文案生成为一张 `1242x1660` 的小红书风格 PNG 封面，
不依赖 Playwright，也不需要 Chromium。

## 功能特点

- 纯 Pillow 渲染
- 无浏览器依赖
- 适合小红书封面 / 首图 / cover image / thumbnail
- 文件结构简单，便于直接安装为 Claude Code Skill

## 仓库结构

```text
xhs-cover/
├─ README.md
├─ SKILL.md
└─ scripts/
   └─ cover.py
```

## 安装方式

### 方式 1：手动安装到 Claude Code

#### 全局安装

把仓库复制或克隆到：

```bash
~/.claude/skills/xhs-cover
```

#### 项目内安装

把仓库复制或克隆到：

```bash
<你的项目>/.claude/skills/xhs-cover
```

例如：

```bash
git clone https://github.com/Miluer-tcq/xhs-cover.git ~/.claude/skills/xhs-cover
```

或者：

```bash
git clone https://github.com/Miluer-tcq/xhs-cover.git ./.claude/skills/xhs-cover
```

### 方式 2：把仓库链接直接发给 AI 帮你安装

如果你使用的 AI / agent 支持安装 Skill，可以直接把这个仓库链接发给它：

```text
https://github.com/Miluer-tcq/xhs-cover
```

例如你可以直接对 AI 说：

```text
帮我安装这个 skill 到当前项目：
https://github.com/Miluer-tcq/xhs-cover
```

或者：

```text
请把这个 GitHub 项目安装成 Claude Code skill：
https://github.com/Miluer-tcq/xhs-cover
```

## 依赖

安装 Pillow：

```bash
pip install pillow
```

或者：

```bash
uv pip install pillow
```

## 使用方式

安装完成后，可以直接对 Claude Code 说：

- 帮我做一个小红书封面
- 给这篇笔记生成首图
- 生成一张小红书风格封面图
- 做一个带步骤卡片和对比框的封面

也可以直接运行脚本：

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

## 输出说明

- 格式：PNG
- 尺寸：`1242 x 1660`
- 风格：手账风 / 小红书封面风格

## 说明

- 文案尽量简短，排版效果会更好。
- 生成器会自动换行、自动缩放，尽量避免内容溢出。
- 在 Windows 上，如果系统有微软雅黑字体，中文显示效果会更稳定。
