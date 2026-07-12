---
name: enhancement-brief
description: 共享增强简报——所有"每 Foundation 一位"的增强 Agent 必须先读本文件。定义统一的领域知识串联（跨模块暗线）、深化标准（顶尖教育学教授级、逻辑不跳步）、跨模块建链的防断链硬规则、以及自评清单。
---

# Foundation 深化增强 · 共享简报 (Enhancement Brief)

> [!important] 所有增强 Agent 先读这三份，再动你负责的那一个 Foundation
> 1. 本简报（统一知识串联 + 硬规则 + 自评清单）
> 2. `/Users/yang/Notes/Notes/CLAUDE.md` §2（叙事风格：母题 / 本节四拍 / 逻辑不跳步 / 角色切换 / 关联优先）
> 3. `/Users/yang/.claude/jobs/6d711e3c/tmp/anchor_index.txt`（全库已验证章节锚点 + 别名；建跨模块链接的目标清单）

## 0. 使命（这一轮要把每个 Foundation 提到什么水准）

现有 Foundation **知识点展开不足、知识点之间的联系不足**，未达"顶尖教育学教授"水准。你的任务不是新增整块主题，而是**把已有每个知识点讲透、把知识点之间织成记忆网**：

- **逻辑不跳步（第一优先级）**：凡出现"由 X 可得 Y""显然""易证""同理"而中间有 ≥1 步省略的地方，补上中间推导。宁多写一句，不让读者脑补。每个公式的每个符号标注物理意义与单位。
- **知识点深化**：每个核心概念补齐"物理直觉 → 严格定义/推导 → 为什么有效 → 失效边界 → 在灵巧操作中的落点"五要素中缺失的部分。演进类算法补"Phase 奠基→发展→前沿"脉络（历史背景/核心创新/局限/代表工作）。
- **联系密度（记忆导向）**：这是本轮重点。每深化一个知识点，就问"它和本库别处的什么强相关"，用 `[[File#精确锚点|别名]]` 织进 §2 的知识网。孤立知识点等于没写。

## 1. 统一领域知识串联（跨 Foundation 暗线 —— 建立联系时优先复用这些）

本库靠少数**反复出现的暗线**把 13 个 Foundation 缝成一体。你在"梳理知识点关系"时，**优先把你的知识点挂到下面某条暗线上**（这是"知识共享"的核心——所有 Agent 共用这套串联，联系才一致、才便于记忆）：

| 暗线 (Leitmotif) | 一句话 | 贯穿的 Foundation |
|:--|:--|:--|
| **对偶性 $J/G/P$** | 手雅可比 $J_h$（关节→接触）、抓取矩阵 $G$（接触→物体）、腱耦合矩阵 $P$（腱→关节）三者数学同构，力闭合/冗余/零空间工具三处复用 | [[Dynamics]] §8 · [[ControlTheory]] §2 · [[ContactMechanics]] §2-3 |
| **价值即 Lyapunov** | RL 的值函数 = 控制论的 Lyapunov 函数；Bellman↔HJB、LQR↔值迭代、Safe RL↔稳定性证书 | [[ControlTheory]] §10-11 · [[ReinforcementLearning]] §2 · [[Optimization]] |
| **认知不确定性三用** | ensemble 分歧 = epistemic 不确定性 = 信息增益：规划里当护栏（别钻模型空子）、探索里当罗盘、课程里当"该学处" | [[WorldModels]] §3,§6.3 · [[StochasticProcess]] §5 · [[InformationTheory]] · [[ReinforcementLearning]] §6.1,§7 |
| **Continuation / 同伦 / 平滑化** | "先解平滑近凸子问题、再逐步引入真难度"：接触平滑（Optimization §5.4）、课程学习（任务分布 $Q_0\to Q_1$）、扩散（噪声→数据） | [[Optimization]] §5 · [[ReinforcementLearning]] 课程 · [[RepresentationLearning]] §2.2 |
| **POMDP → belief → latent** | 部分可观→充分统计量 belief→世界模型 latent（RSSM）；历史窗口是解药 | [[ReinforcementLearning]] §2.1 · [[StochasticProcess]] §2,§4 · [[WorldModels]] §1-2 · [[SignalProcessing]] |
| **采样+加权 统一优化** | CMA-ES（参数空间）、MPPI（控制序列）、策略梯度（动作）同宗：采样→按 fitness/return 加权→挪分布 | [[Optimization]] §4.4 · [[StochasticProcess]] §6 · [[ReinforcementLearning]] §4 |
| **电流 ≠ 关节力矩 / τ 身份错位** | 仿真把 $\tau$ 当输入直接施加；真机 $\tau$ 是电机→FOC→减速器→传动链的输出——机械+电气差异即 Sim-to-Real gap 的物理来源 | [[Actuation]] · [[ReinforcementLearning]] §9 · [[WorldModels]] §5 · [[Dynamics]] §3.1 |
| **接触的非光滑性** | 接触把动力学撕成混合系统 / 互补约束 / 非凸景观，是策略梯度高方差、优化卡死、仿真伪影的共同根 | [[ContactMechanics]] · [[Dynamics]] §6 · [[Optimization]] §3 · [[ReinforcementLearning]] §1.3 |
| **KL 方向决定 covering vs seeking**（2026-07-12 新增第 8 暗线） | 前向 KL→mode-covering→SFT"学会做"（覆盖演示、易均值坍缩）；反向 KL→mode-seeking→RL/RLHF"学会选"（挑高奖励峰） | [[InformationTheory]] §2.3.1 · [[ReinforcementLearning]] §5.0/§5.4.2/§7.4 · [[EmbodiedAI]] §2.3.1(OPD) · [[RepresentationLearning]] §2.2(扩散=覆盖做对) |

**各 Foundation 的贯穿母题（引用他人母题可增强联系感）**：Dynamics=挥转偏心螺丝刀 · ContactMechanics=夹稳弹珠 · ControlTheory=插销入孔 · Actuation=一个力矩指令的旅程 · Optimization=伸手抓杯倒水 · RL=指间转笔 · WorldModels=在脑内转笔 · StochasticProcess=未知摩擦推冰球 · InformationTheory=主动触摸 · RepresentationLearning=从像素/触觉到可控状态 · EmbodiedAI=一只红杯子。

## 2. 跨模块建链 —— 防断链硬规则（断链是本库头号质量问题）

> [!danger] 引用 `[[File#章节]]` 前必须验证章节存在
> 1. **优先查** `anchor_index.txt`（已列全库精确章节标题），或对目标文件 `grep -nE '^#{2,3} ' Foundations/X.md` 现验。
> 2. 章节标题**逐字复制**（含全角标点、LaTeX 如 `$P$`、破折号）。
> 3. 不确定就用泛化链接 `[[File]]`（无锚点，永不断链）或 `[[File|别名]]`。
> 4. 论文/项目链接用 basename（不带 `.md`），可加 `|别名`；含花体撇号 `’`(U+2019) 等特殊字符要原样复制。

## 3. 分工与边界（避免多 Agent 互相踩踏）

- **只编辑你负责的那一个 `Foundations/X.md`**。不要碰 taxonomy / README / CLAUDE / 其它 Foundation 文件。
- 若你发现"应在**别的** Foundation 加一条反向链接指向你"，**不要去改那个文件**——写进你返回的 change-log 的"建议反链"清单，由主 Agent 统一施加（避免并发写冲突）。
- **只增补/深化，绝不删除**现有知识内容（保守删除原则）。可重排/补步，但不丢信息。
- 保持中英双语、callout、公式规范与本库一致。

## 4. 自评清单（返回前逐项确认）

```
[ ] 逻辑无跳步：每处"显然/易证/由此可得"都已补中间步骤
[ ] 每个新公式的每个符号都标了物理意义（+单位）
[ ] 深化的知识点覆盖：直觉→定义/推导→为什么有效→失效边界→灵巧操作落点
[ ] 新增 ≥3 条跨 Foundation 联系，且都挂在 §1 某条暗线上
[ ] 所有 [[File#锚点]] 已 grep 验证存在（否则降级为 [[File]]）
[ ] 未删除任何原有知识；未编辑其它文件
[ ] 风格与母题/本节四拍一致
```

## 5. 返回格式（change-log，务必简洁，供主 Agent 评估）

```
### 负责: Foundations/X.md
- 深化点1: <哪一节/知识点> — <补了什么推导/展开> (逻辑跳步修复: 是/否)
- 深化点2: ...
- 新增联系: [[A#锚]]←→本节<点>（挂在哪条暗线）; ...（列全部新链，标注已 grep 验证）
- 建议反链（请主 Agent 在他处施加）: 在 [[Y]] 的<某节> 加指向 [[X#新锚]] 的链接
- 自评清单: 全过/存疑项
- 净增行数 ~N；未删除原内容
```
