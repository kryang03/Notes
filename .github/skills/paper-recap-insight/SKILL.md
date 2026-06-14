---
name: paper-recap-insight
description: Create or refine extreme-granularity, principle-first research paper recaps from PDFs or existing notes, organized around four pillars — 逻辑与价值 (logic/value/story), 原理与理论 (first-principles theory edifice), 实验与验证 (experiments as evidence for the story), 未来与结合 (limitations + integration with the knowledge graph and the user's WMTS/灵巧手 projects). For robotics, embodied AI, RL, control, dynamics, world models, representation learning, dexterous manipulation, Sim-to-Real, tactile/contact, actuator dynamics, and Obsidian/PapersRecap/RelatedPapersRecap knowledge graphs. Use when the user asks to summarize, 整理, 精读, recap, refine, 对齐知识库, or extract insights from a paper PDF or paper-related chat/note. Emphasize mathematical provenance, variable origin, no-jump derivations, causal ablations, and personalized research transfer; avoid implementation-code dumps.
---

# Paper Recap Insight

Produce paper recaps that behave like a research mentor's reconstruction, not an abstract expansion. The gold standard is `Example/Rodrigues Network for Learning Robot Actions.md` (722 lines). Every recap should reach that **question granularity**: not just "what the paper did", but where every variable comes from, why each symbol is written that way, how each formula is derived with no jumps, how each experimental number corroborates the story, and exactly how the method transfers to the user's 灵巧手转笔 / Sim-to-Real / WMTS work.

> **Read the gold standard before writing or refining.** Open `Example/Rodrigues Network for Learning Robot Actions.md` and `references/taste-rubric.md`. The Example *is* the target; this skill is the operating manual for reproducing its depth on any paper.

## The Four Pillars (用户的四个关注点)

Every recap is judged against four questions the user actually asks. These are the backbone — organize thinking around them, and make sure each is answered concretely, not gestured at.

### Pillar 1 — 逻辑与价值 (Logic & Value): how the paper earns its place

> 这篇文章相对于其他文章，逻辑上顺承出来的优势在哪里？Insight 在哪里？Value add 在哪里？它是如何讲好这个故事的？

- State the **exact bottleneck** in one sentence, then the **structural bet** (the assumption that makes the method plausible).
- Build a **现有方法的局限 table**: for each prior paradigm (MLP/GNN/Transformer/analytic/end-to-end/...), name *what prior it injects* and *its specific limitation* — not a generic "prior work is limited".
- Write the **Delta** as a precise increment over the closest baseline ("not X-as-external-loss, but X-as-internal-operator"), not a vague "we are better".
- Give one **直观隐喻** that crystallizes the insight (the Example's CNN↔RodriNet analogy). A good metaphor is falsifiable: it says exactly which structure is fixed and which is learned.
- Separate "the method works" from "the method works *because the benchmark bottleneck happens to be* X".

### Pillar 2 — 原理与理论 (Principles & Theory): build the theoretical edifice from zero

> 从原理的角度出发，它联系到了哪些相关的公式和定理？如何从零基础开始把它们说清楚，构建一个详细的理论大厦？

- **Variable-provenance table is mandatory** (see pattern below). Every important symbol: domain/shape, source stage (robot structure / observation / network output / rollout / computation-graph intermediate), gradient status (detached vs requires_grad), physical-or-algorithmic meaning, and a **trap** column.
- **No-jump derivation**: start from the classical formula/objective/graphical-model/control-law the paper modifies, then reach the paper's equation with every algebraic step shown. The reader should never wonder "where did this term come from". Reconstruct the prerequisite theory from first principles (the Example derives $SO(3)\to\mathfrak{so}(3)\to\exp\to$ Rodrigues $\to$ FK tree composition before touching the neural operator).
- **Notation traps as insight**: coordinate frames, active/passive transforms, time indices vs diffusion/denoising steps, local vs global variables, distribution vs sample, fixed structure vs learnable, dimension/homogeneous-lift mismatches. Explaining a subscript convention (the Example's `${}^P_J T$` "J in P") is often where the real understanding lives.
- Link each formula back to the relevant **Foundation** with the *exact* mathematical correspondence (`[[Dynamics#2.4 ...|Dynamics §2.4]] — this is the math root`), not a decorative link.

### Pillar 3 — 实验与验证 (Experiments & Validation): numbers that prove the story

> 从实验结果来看，它的表现是如何印证它所讲的这个故事的？

- Preserve **real numbers in real tables**: task names, datasets, metrics, baselines, headline results, training setup (optimizer, LR, batch, steps, data sizes). Never paste raw "PDF clue lines" as a substitute for a result table.
- After each table, write the **因果解释**: *why* these numbers support the Pillar-1 story. The Example's killer line — "Rodrigues' test MSE is below every baseline's *train* MSE → the advantage is structural-prior generalization, not fitting capacity" — is the model.
- Every ablation as a **causal chain**: `remove/change A → metric B moves → because mechanism C is disabled/amplified → implication D for using the method`. The point of an ablation table is to identify *which inductive bias* was removed, not "module gone so worse".
- Flag where a result is **confounded** or where the benchmark's bottleneck is not the one the paper claims to solve (the Example: PegInsertion/PlugCharger gains are small because, absent tactile/force, the backbone isn't the bottleneck).

### Pillar 4 — 未来与结合 (Future & Integration): limitations + transfer to the user's world

> 它有哪些 limitation？可以如何与当前的知识库结合？如何与当前我想提出的 project 结合？

- **Limitations across three axes**: 理论维度 (what physics/math it does *not* model — e.g. "kinematics-aware, not dynamics-aware: it does not represent $M(q)\ddot q + C\dot q + g = \tau + J^T\lambda$"), 算法维度 (alternative paradigms compared by assumption + failure mode), 工程/实验维度 (memory, kernels, sim-to-real gaps).
- **Personalized transfer is concrete enough to become an experiment or a rejection reason**: produce at least one of — a direct modification to PPO / Diffusion Policy / world model / controller; a diagnostic experiment with baselines; a reason *not* to use it in contact-rich dexterous manipulation; a Sim-to-Real risk + mitigation. When the method has a key input variable, show *what it becomes in the user's task* (the Example's "$\theta_j$ → a $C_J$-dim joint-local feature of $[\sin q,\cos q,\dot q, a_{t-1}, \tilde a_k, e(t_{diff}), h^{tactile}, h^{object}, h^{task}]$" table).
- **Integration with the knowledge graph**: link ≥2 Foundations with specific correspondence; connect to the WMTS pipeline (latent task generation → PPO Oracle → Diffusion/Flow generalist → Ensemble World Model → real-robot fine-tuning) and to DNPM where relevant. Respect WMTS defaults from `research-insight-critic` (PPO is the default Oracle; tactile/contact and actuator dynamics are first-class; do not inject task labels into dynamics models).

## Mandatory Vault Context

When working inside a vault that contains `.github/skills/`, read the local guidance before writing:

1. `.github/TASK_TRACKER.md` for current knowledge-graph state and any active recap-upgrade batch.
2. `.github/skills/knowledge-graph-management/SKILL.md`, especially §2.3.1 (algorithm granularity standard) and §2.3.2 (PapersRecap refine workflow), plus Foundation linking rules.
3. `.github/skills/research-insight-critic/SKILL.md` for WMTS defaults and routing hints when writing the Pillar-4 transfer.
4. `.github/skills/obsidian-markdown/SKILL.md` if creating/editing Obsidian notes; `.github/skills/json-canvas/SKILL.md` if updating `KnowledgeGraph.canvas`.
5. `references/taste-rubric.md` in this skill when calibrating depth or deciding whether output is deep enough.

Place the paper in the existing graph: inspect nearby `Foundations/`, the relevant `PapersRecap/` or `RelatedPapersRecap/`, `Projects/`, and `KnowledgeGraph.canvas`.

## PDF Workflow (do this before writing)

1. **Probe the PDF with the `pdf` skill first** — never rely on a single `pdftotext` pass:
   - repo-local: `python3 .github/skills/pdf/scripts/pdf_probe.py "<paper.pdf>" --out "tmp/pdfs/<paper-stem>"`
   - global: `python3 /Users/yang/.codex/skills/pdf/scripts/pdf_probe.py "<paper.pdf>" --out "tmp/pdfs/<paper-stem>"`
   - Combine `pdfinfo`, `pdftotext -layout`, `pdfplumber` page text, and `pdftoppm` PNG renders. Read abstract, intro, method, experiments, ablations, limitations, **and appendix** (reward/observation tables, training details often live there).
2. **If extracted text is garbled, the rendered PNGs are the source of truth** for title, equations, tables, captions, numbers. Reconstruct equations from surrounding prose and verify against repeated references in the text.
3. Build an outline from headings, but **write the recap from causal dependencies**, not paper order.
4. Search the extracted text for: equation numbers, `ablation`, `baseline`, `we observe`, `we find`, `fails`, `limitation`, `future work`, `implementation`, `training details`, `dataset`.

## Required Recap Structure

Use this structure (it maps each section to a pillar). Match the Example's depth; adapt section names to the paper, but never drop a pillar.

```markdown
---
tags:
  - paper
  - <domain tags>
aliases:
  - <short name>
paper-year: YYYY
read-date: YYYY-MM-DD
venue: <venue>
paper-pdf: "[[<exact PDF path/name>.pdf]]"
related:
  - "[[Foundation1]]"
  - "[[Foundation2]]"
---

# <Full Paper Title>

> [!abstract] 核心贡献
> <One sentence: method X solves bottleneck Y by structural insight Z.>

> [!tip] 与理论基础的关联
> - [[Foundation#section]] — exact mathematical correspondence
> - [[Foundation#section]] — exact mathematical correspondence
> **核心技术**: <key technique names>

## 0. 阅读定位与范本价值                    ← Pillar 1
<Why this paper matters for the user's graph; what bottleneck it touches in WMTS/DNPM.>

## 1. 问题设定与动机                         ← Pillar 1
### 1.1 一句话核心
### 1.2 直观隐喻
### 1.3 现有方法的局限      (table: 方法 | 注入了什么先验 | 关键局限)
### 1.4 Delta 分析 / 论文贡献

## 2. 核心方法与理论                         ← Pillar 2
### 2.1 变量来源追踪        (provenance table; see pattern)
### 2.2 前置理论从零推导    (classical root rebuilt from scratch, no jumps)
### 2.3 核心公式无跳步推导
### 2.4 概念边界与符号陷阱
### 2.5 信息流/算法机制（无代码）

## 3. 训练、数据与实验                       ← Pillar 3
### 3.1 实验设置        (real table)
### 3.2 关键结果        (real numbers + 因果解释 of how they prove the story)
### 3.3 Ablation 因果链  (A→B→because C→implication D)
### 3.4 工程约束与实验边界

## 4. 核心洞见                               ← Pillar 1 + 4
### 4.1 论文真正的 insight
### 4.2 为什么这个设计有效
### 4.3 什么时候会失效

## 5. 替代方案与理论局限                     ← Pillar 4
### 5.1 理论维度    ### 5.2 算法维度    ### 5.3 工程/实验维度

## 6. 对用户研究的启发                       ← Pillar 4
### 6.1 对灵巧手/转笔/PPO/DP/Sim-to-Real/WMTS 的迁移 (with input-feature table when relevant)
### 6.2 可验证实验建议
### 6.3 不应过度外推的点

## 7. 与知识体系的联系                       ← Pillar 4
### 与 [[Foundation1]] 的联系   (the math chain)
### 与 [[Foundation2]] 的联系

## References
```

For a method that is itself a template/foundational tool, also add (as the Example does):
- a §0 **最低标准表** mapping each pillar to where it lands in this recap, and
- a final **应复刻的提问颗粒度** section anticipating the user's follow-up questions (`用户式追问 | Agent 应主动补充`).

## Worked Patterns

### Formula reconstruction (Pillar 2)
1. Classical starting point. 2. Constraint/observation. 3. Algebraic transformation (every step). 4. Paper's relaxation/parameterization. 5. Meaning of each term. 6. Failure/boundary condition + degenerate case (when does it reduce to the classical method?).

### Variable-provenance table (Pillar 2)
| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|

"来源阶段" ∈ {robot structure/URDF, observation, network output, rollout, computation-graph intermediate, supervision label}. "符号陷阱" = coordinate convention, gradient status, unit, frame, action horizon, distribution vs sample, physical quantity vs latent feature.

### Ablation causal chain (Pillar 3)
`Remove/change A → observed metric B changes → because mechanism C is disabled/amplified → implication D for using the method.`

### Personalized transfer (Pillar 4)
Produce ≥1: a direct modification to PPO/DP/world-model/controller; a diagnostic experiment (with baselines + what would falsify the mechanism); a reason not to use it in contact-rich dexterous manipulation; a Sim-to-Real risk + mitigation. When the method has a key scalar/structural input, write the table of *what it becomes in the user's task*.

## Prohibited / Anti-Patterns (these failed the last draft pass — do not repeat)

- ❌ **Generic filler that fits any paper.** A §"前置理论从零推导" that says "这类方法可以统一写成闭环决策问题…若结构化 X 它在做 Y" is template text, not a derivation. Replace with the *actual* classical theory this paper modifies (DDPM forward/reverse + score matching for Diffusion Policy; Bellman/PPO clip for an RL paper; LCP/contact for a contact paper).
- ❌ **Copy-paste repetition.** Do not repeat the same sentence verbatim across §1.4 / §2.5 / §4.1 / §7. Each section answers a different question.
- ❌ **Pasted "PDF 线索" lines** in place of a real results table. Extract the actual numbers into a table and interpret them causally.
- ❌ **LaTeX corruption.** Verify `\bar\alpha` did not become `arlpha`, `\approx` did not become `pprox`, `\beta`→`eta`, `\theta`→`heta`. Render-check math after writing; a recap with broken formulas fails Pillar 2 outright.
- ❌ **Decorative Foundation links** ("see [[ReinforcementLearning]]") without the specific mathematical correspondence.
- ❌ **Default code dumps.** No "最小 PyTorch 逻辑 / 核心 tensor ops" section unless the user asks. If implementation matters, write it as principle-level dataflow, shape/variable provenance, numerical constraint, or engineering failure mode (the Example's "实现避坑" bullets are the allowed form).
- ❌ Marketing praise without mechanism; "better generalization" without naming the inductive bias that narrows the function class; "physics-informed" without the exact physical structure.

## Knowledge-Graph Alignment

- Standard frontmatter; field names per `knowledge-graph-management §3.5` (`paper-year`, `read-date`, `venue`, `paper-pdf` quoted).
- **Output location**: if the PDF folder has a sibling recap folder (`RelatedPapers/`→`RelatedPapersRecap/`, `Papers/`→`PapersRecap/`), write the `.md` there, not next to the PDF.
- **Filename = PDF basename**, suffix `.pdf`→`.md`, only substituting characters the filesystem forbids.
- Link ≥2 Foundations with specific correspondence; add reverse links in Foundations when the paper contributes a reusable concept; update Canvas only for an algorithmic breakthrough / key challenge / project-relevant connection.
- Validate wikilinks, section anchors, and Canvas JSON after edits (`.github/scan_links.py`, `.github/scan_sections.py`).

## Quality Gate (verify before finishing — tied to the four pillars)

- [ ] **P1** Core contribution = method + bottleneck + structural insight; 现有方法局限 is a per-paradigm table; Delta is precise; one falsifiable metaphor.
- [ ] **P2** Variable-provenance table present with gradient status; every central formula derived from its classical root with no jumps; ≥1 notation trap explained; degenerate/reduction case stated.
- [ ] **P3** Real result tables with headline numbers + training setup; each table has a 因果解释 of how it proves the story; ablations are causal chains; confounds/benchmark-bottleneck flagged.
- [ ] **P4** Limitations across theory/algorithm/engineering; ≥1 concrete transfer to PPO/DP/WMTS/灵巧手 that could become an experiment or rejection reason; ≥2 Foundation links with exact correspondence; no broken links.
- [ ] No generic filler, no copy-paste repetition, no pasted PDF clue lines, no corrupted LaTeX, no default code dump.
- [ ] The recap answers "why this method exists" before "what it does".
