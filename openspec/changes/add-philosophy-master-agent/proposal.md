## Why

Many users have烦恼与困惑（人际、工作、意义、选择、痛苦与欲望），需要一个能以“哲学视角 + 可执行建议”来疏理问题、澄清价值与行动方向的对话型 AI。现在我们已有聊天类 Agent 体系，可以快速引入“哲学大师”并复用现有的认证与流式对话体验。

## What Changes

- Add a new chat-style AI agent: **Philosophy Master**（哲学大师）
  - 从多种哲学流派/角度为用户答疑解惑：东方/西方、儒家、禅宗/佛教、斯多葛、存在主义、尼采、康德、叔本华、唯心/唯物等
  - 面向“烦恼/困惑/两难选择”，输出：哲学分析（概念澄清、价值辨析、视角转换）+ 可执行方案（行动建议、练习、反思问题）
  - 支持“讲故事/寓言/典故”模式：用哲学故事说明道理（并给出可迁移的原则）
  - 支持风格与流派预设：用户可选择“流派/角度/语气/深度”（例如：禅宗式简练点拨、儒家式修身齐家、西方古典论证、存在主义式自我选择等）
  - 支持流式输出（streaming），体验与现有聊天一致
- Add an entry in the frontend: Philosophy Master page (agent card + route + navigation)
- Add minimal docs/runbook entry for the new agent

**Extra useful functions (suggested)**

- “多视角对照”输出：同一问题给出 2-3 个流派的解读对比（优缺点与适用情境）
- “每日一则”哲学短练习：一句箴言 + 一个当日练习 + 一个反思问题
- “阅读清单”模式：给出入门阅读路线（按主题/难度/流派），并说明为什么推荐
- Safety boundaries: 对自伤/极端风险、严重心理危机提供谨慎回应与求助建议（非医疗/非心理治疗替代）

## Capabilities

### New Capabilities

- `philosophy-master-agent`: A chat agent that provides philosophical analysis, stories, and actionable guidance; supports selectable schools/lenses and streaming responses.

### Modified Capabilities

- *(none)*

## Impact

- **Backend**
  - New endpoints under `/api/v1/` for philosophy master chat (and streaming variant)
  - New service module for the agent prompts, style/lens selection, and response formatting
  - Auth: reuse existing JWT auth dependencies
- **Frontend**
  - New view/page for the Philosophy Master agent (chat UI, presets for school/lens/style)
  - Home page: show Philosophy Master as an agent card
  - Nav menu: add Philosophy Master entry
- **Dependencies**
  - Reuse existing LLM provider and streaming mechanism; no new external services required

