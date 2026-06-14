---
name: paper-recap-insight
description: Create or refine high-granularity, principle-first research paper recaps from PDFs or existing notes, especially for robotics, embodied AI, reinforcement learning, control, dynamics, representation learning, dexterous manipulation, Sim-to-Real, and Obsidian/PapersRecap knowledge graphs. Use when the user asks to summarize,整理,精读,recap,refine,对齐知识库, or extract insights from a paper PDF or paper-related chat/note; emphasize mathematical principles, variable provenance, conceptual mechanisms, causal ablations, and personalized research implications, while avoiding implementation-code sections.
---

# Paper Recap Insight

Produce paper recaps that match the user's current taste: first-principles, question-driven, theory-heavy, insight-oriented, and connected to the dexterous manipulation knowledge graph. Do not treat the task as a generic summary.

## Mandatory Vault Context

When working inside a vault that contains `.github/skills/`, read the relevant local guidance before writing:

1. `.github/TASK_TRACKER.md` for current knowledge-graph state.
2. `.github/skills/knowledge-graph-management/SKILL.md`, especially PapersRecap granularity and Foundation linking rules.
3. `.github/skills/obsidian-markdown/SKILL.md` if creating/editing Obsidian notes.
4. `.github/skills/json-canvas/SKILL.md` if updating `KnowledgeGraph.canvas`.

If the user provides only a PDF, still inspect nearby `Foundations/`, `PapersRecap/`, `Projects/`, and `KnowledgeGraph.canvas` enough to place the paper in the existing graph. When a PDF or folder of PDFs is involved, use `$pdf` first for metadata, page-level text, rendered PNGs, and layout checks before writing the recap.

For the user's detailed taste rubric, read `references/taste-rubric.md` when calibrating a new recap style, refining an existing recap, or deciding whether the output is deep enough.

## PDF-Only Workflow

1. **Extract metadata and structure**
   - Identify title, year, venue, authors if available, PDF path, abstract, section headings, figures, tables, appendix, and experiment names.
   - Use the PDF skill/probe first when available:
     - global: `python3 /Users/yang/.codex/skills/pdf/scripts/pdf_probe.py "<paper.pdf>" --out "tmp/pdfs/<paper-stem>"`
     - repo-local: `python3 .github/skills/pdf/scripts/pdf_probe.py "<paper.pdf>" --out "tmp/pdfs/<paper-stem>"`
   - Use `pdftotext -layout`, `pdfplumber`, and rendered PNGs together. Extract around equations, tables, figures, and appendix details, not just the abstract.
   - If extracted text is garbled, use rendered pages as the source of truth for title, equations, tables, captions, and numbers.

2. **Find the paper's real object**
   - State the exact problem in one sentence.
   - Identify what the paper treats as the bottleneck: representation, exploration, control, contact, sim-to-real, data, architecture, optimization, or hardware.
   - Name the paper's central bet: what structural assumption makes the method plausible?

3. **Reconstruct prerequisites**
   - List the concepts that must be understood before the method makes sense.
   - For each concept, explain the minimum theory needed from first principles. Do not dump definitions.
   - Link to existing Foundations when available; otherwise add concise background inside the recap and consider Foundation updates.

4. **Derive the method without jumps**
   - Start from the classical formula, objective, graphical model, control law, or learning paradigm the paper modifies.
   - Track every important variable: source stage, shape/domain, physical meaning, whether it is a fixed structure, observed value, computed quantity, supervision signal, or learnable parameter.
   - Explain notation traps: coordinate frames, active/passive transforms, time indices, detach/gradient status if relevant, distribution vs sample, local vs global variables.

5. **Extract the conceptual algorithm, not implementation code**
   - Explain information flow and causal mechanisms in prose, tables, equations, and diagrams.
   - Do **not** include sections such as "minimal PyTorch logic", "core tensor ops", or implementation-only pseudocode unless the user explicitly asks for code.
   - Engineering details are allowed only when they reveal a principle, failure mode, numerical constraint, or experimental bottleneck.

6. **Keep experimental evidence quantitative**
   - Preserve key task names, datasets, metrics, training/evaluation setup, baselines, and headline numbers.
   - For each ablation: write the chain "remove/change A -> metric B changes -> because mechanism C".
   - Separate "method works" from "method works only because the benchmark bottleneck is X".

7. **Write the user's personalized insight layer**
   - Connect the paper to dexterous manipulation, pen spinning, PPO/RL, Diffusion Policy, Sim-to-Real, tactile/contact, actuator dynamics, or current Projects when relevant.
   - Include concrete migration designs and failure boundaries.
   - State when not to use the method.

8. **Align the knowledge graph**
   - Add standard frontmatter.
   - Choose output location from local convention: if the PDF folder has a sibling recap folder such as `RelatedPapersRecap/`, write the `.md` recap there, not next to the PDF.
   - Preserve the PDF basename exactly for recap filenames unless the user says otherwise: `Paper Name.pdf` -> `Paper Name.md`.
   - Link at least two relevant Foundations with specific mathematical/algorithmic correspondence.
   - Add reverse links in Foundations when the paper contributes a reusable concept.
   - Update Canvas only if the paper adds an algorithmic breakthrough, key technical challenge, or project-relevant connection.
   - Validate wikilinks, section links, and Canvas JSON after edits.

## Required Recap Structure

Use this structure unless an existing local template is stricter:

```markdown
---
tags:
  - paper
  - <domain>
aliases:
  - <short name>
paper-year: YYYY
read-date: YYYY-MM-DD
venue: <venue>
paper-pdf: "[[path/to/paper.pdf]]"
related:
  - "[[Foundation1]]"
  - "[[Foundation2]]"
---

# <Full Paper Title>

> [!abstract] 核心贡献
> <One sentence: method X solves bottleneck Y by structural insight Z.>

> [!tip] 与理论基础的关联
> - [[Foundation#section]] — exact correspondence
> - [[Foundation#section]] — exact correspondence

## 0. 阅读定位与范本价值
<Why this paper matters for the user's knowledge graph or research taste.>

## 1. 问题设定与动机
### 1.1 一句话核心
### 1.2 直观隐喻
### 1.3 现有方法的局限
### 1.4 Delta 分析

## 2. 核心方法与理论
### 2.1 变量来源追踪
### 2.2 前置理论从零推导
### 2.3 论文核心公式/机制无跳步推导
### 2.4 概念边界与符号陷阱
### 2.5 信息流/算法机制（无代码）

## 3. 训练、数据与实验
### 3.1 实验设置
### 3.2 关键结果
### 3.3 Ablation 因果链
### 3.4 工程约束与实验边界

## 4. 核心洞见
### 4.1 论文真正的 insight
### 4.2 为什么这个设计有效
### 4.3 什么时候会失效

## 5. 替代方案与理论局限
### 5.1 理论维度
### 5.2 算法维度
### 5.3 工程/实验维度

## 6. 对用户研究的启发
### 6.1 对灵巧手/转笔/PPO/DP/Sim-to-Real 的迁移
### 6.2 可验证实验建议
### 6.3 不应过度外推的点

## 7. 与知识体系的联系
### 与 [[Foundation1]] 的联系
### 与 [[Foundation2]] 的联系

## References
```

## Prohibited Default Content

Do not include by default:

- "最小 PyTorch 逻辑如下，只保留核心 tensor ops"
- code-first implementation sections
- defensive code snippets
- long reproduction scripts
- boilerplate summaries that do not explain the principle
- marketing-style praise without mechanism

If the paper's implementation is important, write it as principle-level dataflow, shape/variable provenance, numerical constraint, or engineering failure mode.

## Quality Gate

Before finishing, check:

- The recap can answer "why this method exists" before "what it does".
- Every central formula has a derivation path or conceptual origin.
- Every important variable has source and meaning.
- Ablations are causal, not a pasted table.
- The user's research implications are concrete enough to become an experiment or a rejection reason.
- There are at least two Foundation links and no newly introduced broken links.
- Any Canvas update parses and has no dangling edges.
