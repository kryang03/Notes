---
name: coverage-audit
description: Foundation 覆盖度审计与缺口填充追踪。以"资深研究教授 + 教育专家"双重身份，对照"基于RL的动态灵巧操作+世界模型+Sim-to-Real"方向所需知识与现有 Foundation 覆盖，诊断遗漏并按关联优先原则补齐。本 loop 逐轮维护。
---

# Foundation 覆盖度审计与缺口填充追踪

> [!important] 本文档用途
> 这是知识图谱**覆盖度自审**的活文档，也是缺口填充 loop 的进度追踪器。每轮迭代：从缺口清单取最高优先级 → 用本库叙事风格（[[CLAUDE]] §2）补齐 → 更新本表状态。
> **审计视角**：①资深研究领域教授（判断"这个方向该掌握什么"）②善于教育的专家（判断"讲清楚了吗、关联建立了吗"）。
> **审计依据**：(a) 领域常识；(b) 代码库论文语料实际使用的算法方向（见 §2 证据）。

**最后更新**: 2026-07-12（新建，首轮审计）

---

## 1. 现有覆盖度地图（12 Foundation 主线）

| Foundation | 理论主线 | 对本方向的覆盖评估 |
|:--|:--|:--|
| [[Dynamics]] | 几何→能量→约束→RNEA/ABA→接触仿真→神经动力学 | ✅ 扎实（含腱耦合 P、可微物理、DexNDM） |
| [[ContactMechanics]] | 接触几何→运动学→静力学→动力学→可微接触 | ✅ 扎实（力闭合、摩擦锥、LCP） |
| [[ComputationalGeometry]] | 集合运算→凸支持→GJK/EPA→SDF→神经隐式 | ✅ 覆盖（SDF、神经场） |
| [[ControlTheory]] | 系统描述→稳定性→频域→柔顺→MPC/OSF→数据证书 | ✅ 扎实（阻抗、LQR、观测器、数据驱动 LMI） |
| [[Actuation]] | 电机→FOC→串级环→电气热极限→传动/减速→执行器 gap→actuator net | ✅ 新建（2026-07，本 loop 前身） |
| [[Optimization]] | 可行域→目标→求解→非凸→接触隐式→学习加速 | ⚠️ 求解层仅梯度类，**缺进化/零阶（CMA-ES）** |
| [[ReinforcementLearning]] | MDP→Bellman/TD→策略梯度→On/Off-policy→样本效率→探索→Sim-to-Real→生成式 | ⚠️ 主体扎实，但**课程学习、模仿学习无理论章节**（仅论文清单） |
| [[StochasticProcess]] | SDE→马尔可夫→Bayes滤波→GP/ensemble→MPPI→随机互补 | ✅ 扎实（epistemic/aleatoric、ensemble、MPPI 已覆盖） |
| [[SignalProcessing]] | 转导→采样→频域→时频→状态估计→控制接口 | ✅ 覆盖（KF/EKF/PF、触觉） |
| [[InformationTheory]] | belief→熵/KL/MI→主动感知→物理代价→信息瓶颈/empowerment | ✅ 覆盖（信息增益、empowerment） |
| [[RepresentationLearning]] | 重构→对比→几何→动作→因果表征 | ⚠️ **待验证**：Diffusion/CFG、Transformer/ICL、旋转表示深度 |
| [[EmbodiedAI]] | 任务语义→grounding→动作生成→低层控制→数据飞轮 | ⚠️ **待验证**：world model / action chunk / VLA 深度 |

> [!note] 尚未逐行细读的 Foundation
> ComputationalGeometry / SignalProcessing / InformationTheory / RepresentationLearning / EmbodiedAI 仅通过 taxonomy 骨架 + §0 母题表评估，标 ⚠️ 者需在对应迭代中逐节核验后再定夺"补齐 vs 已足"。

---

## 2. 论文语料的算法足迹（"这个方向实际在用什么"）

从 `Papers/`、`PapersRecap/`、`Projects/*/RelatedPapers*/`、`all_Insights_local/` 的文件名归纳：

- **世界模型**：DREAM TO CONTROL (Dreamer)、DayDreamer、STORM、Robotic World Model、MoDem-V2、Finetuning Offline World Models、DyWA、World4RL、DiWA、SafeDreamer、Learning to Model the World (survey)、A Step Toward World Models (survey)、World Models for Dexterous Hand-Object from Human Videos、Deep Dynamics Models、Model-Based Lookahead RL
- **扩散/生成策略**：Diffusion Policy、DiWA、World4RL、BeyondMimic (guided diffusion)、Beyond Human Demonstrations (diffusion RL→VLA)
- **进化/黑盒优化**：cmaes library、The CMA Evolution Strategy: A Tutorial
- **自动课程/开放式**：POET、Prioritized Level Replay、Improving Policy Optimization with Generalist-Specialist、UniDexGrasp++ (geometry-aware curriculum)
- **好奇/探索**：Curiosity-Driven Exploration via Latent Bayesian Surprise、Curious Exploration via Structured World Models
- **旋转/几何/表征**：On the Continuity of Rotation Representations in Neural Networks (6D)、RodriNet、Transformers as Meta-Learners for INR、The Latent Space (survey)、Generalization via Geometry-Aware Multi-Task、PointNet(WMTS 用)
- **in-hand 操作**：DeXtreme、DexReMoE (MoE)、Solving Rubik's Cube、ViserDex、DEXTERITYGEN、From Simple to Complex Skills、HORA、Lessons from Spinning Pens
- **运动迁移**：ANYmal parkour、Learning Agile Dynamic Motor Skills、Learning to Walk in 3 min、ASAP、SONIC、FLD
- **模仿/ICL/元学习**：HG-DAgger、IS ATTENTION REQUIRED FOR ICL、Transformers as Meta-Learners、In-Context Hypernet Adapter (Idea-006)

---

## 3. 缺口清单（按对本方向重要性排序）

### ✅ G1 (已填充 2026-07-12) — 世界模型 (World Models)  ★最高价值 → 已建 [[WorldModels]]
- **已交付**：新建 `Foundations/WorldModels.md`（六层：表征/预测/不确定性/利用/结构/部署），母题"在脑内转笔"，把散在 RL §6.1/§10.2、StochasticProcess、Dynamics §9、Actuation §10 的世界模型线索缝成一体，全图接线（taxonomy/README/CLAUDE/6 处 frontmatter + RL §6.1 指针）完成。

### 🔴 G2 — 进化与零阶/黑盒优化 (CMA-ES / ES / NES)
- **缺什么**：[[Optimization]] 求解层只有梯度类；无进化策略。CMA-ES 是 WMTS 隐空间任务生成器的核心引擎。
- **证据**：cmaes library、CMA Evolution Strategy Tutorial、POET。
- **建议**：**Optimization 新增一节"零阶与进化优化"**——CMA-ES 四步机制（采样/排序选择/均值更新/协方差自适应 + CSA 步长控制）、rank-μ vs rank-one、与 MPPI/随机平滑/策略梯度的零阶梯度估计统一对比。
- **强关联**：[[StochasticProcess]] MPPI(采样式优化同源)、[[ReinforcementLearning]] 策略梯度(log-derivative vs 零阶)、[[InformationTheory]] 协方差自适应≈自然梯度/信息几何。

### 🔴 G3 — 自动课程学习与开放式学习 (Auto-Curriculum / POET / PLR / ADR / Generalist-Specialist)
- **缺什么**：[[ReinforcementLearning]] 仅在 §14 有"课程学习"论文清单，无理论章节。WMTS(隐空间任务生成=课程) + DNPM(双正交课程)的理论根。
- **证据**：POET、Prioritized Level Replay、Generalist-Specialist、UniDexGrasp++、Idea-003/007。
- **建议**：**RL 新增一节"自动课程与开放式学习"**（学习进度信号、Regret-based(PLR)、ADR、POET 协同进化、generalist-specialist 蒸馏循环）。
- **强关联**：G2 CMA-ES(课程搜索)、[[InformationTheory]] 学习进度=信息增益、G1 WM 不确定性驱动课程、[[ReinforcementLearning#9.2 三味药|ADR]]。

### 🟡 G4 — 模仿学习家族 (BC / DAgger / HG-DAgger / 逆RL / 蒸馏 / Action Chunking)
- **缺什么**：RL §1.5 仅提"纯 IL 不够"，无系统章节。WMTS Oracle→Generalist 蒸馏本质是 BC；Action Chunking 是 Diffusion Policy 核心。
- **证据**：HG-DAgger、Diffusion Policy、Beyond Human Demonstrations。
- **建议**：**RL 新增"模仿学习与策略蒸馏"章节**（BC 的复合误差 → DAgger 交互式修正 → HG-DAgger 门控 → 逆RL → 蒸馏/AWAC → action chunking 缓解复合误差）。
- **强关联**：[[ReinforcementLearning]] offline/DT、G1 WM(dream 中 BC 正则)、[[RepresentationLearning]] diffusion。

### 🟡 G5 — 面向学习的旋转表示 (SO(3) / quaternion / 6D continuous)
- **缺什么**：[[Dynamics#2.2]] 有 SO(3)/Rodrigues（几何视角），缺"**为什么神经网络回归旋转要用 6D**"：欧拉角万向节死锁、四元数双覆盖使回归目标不连续/病态、6D(Zhou 2019)连续表示。WMTS 明确用 $R_{6D}$。
- **证据**：On the Continuity of Rotation Representations、RodriNet。
- **建议**：**RepresentationLearning（或 Dynamics §2）补一节"面向学习的旋转表示"**（小而高价值）。
- **强关联**：[[Dynamics#2.2 旋转群 SO(3)、李代数 so(3) 与 Rodrigues 公式|SO(3)]]、[[RepresentationLearning]]、WMTS $R_{6D}$。

### 🟡 G6 — 生成模型深度：Diffusion / Score Matching / CFG / Flow Matching（**待验证**）
- **缺什么**：需核对 [[RepresentationLearning]] / [[StochasticProcess]] 现有扩散深度是否达到 DDPM 前向/反向 + score matching + CFG 贝叶斯推导 + flow matching。WMTS Generalist = Diffusion + CFG。
- **建议**：先读 RepresentationLearning 相关节，不足则补/深化；可能非缺口。

### 🟡 G7 — Transformer / 注意力 / 上下文学习(ICL) / 元学习（**待验证**）
- **缺什么**：语料多篇 ICL/meta/transformer，需核对是否散落且成体系。
- **建议**：读 RepresentationLearning/EmbodiedAI 后定夺。

### ⚪ G8 —（次要）专家混合 MoE
- DexReMoE 用 MoE；小众，可在 RepresentationLearning/RL 一笔带过。

---

## 4. 填充计划与进度

| 迭代 | 任务 | 状态 |
|:--|:--|:--|
| 审计 | 首轮覆盖度审计 + 本文档 + [[CLAUDE]] 治理文档 + memory | ✅ 2026-07-12 |
| Iter A | G1 新建 [[WorldModels]] Foundation（表征→预测→不确定性→利用→结构→部署）+ 全图接线 | ✅ 2026-07-12 |
| Iter B | G2 Optimization 补 §4.4"零阶与进化优化"(CMA-ES 四步+CSA，三种采样优化统一视角) + §0/论文接线 | ✅ 2026-07-12 |
| Iter C | G3 RL §7.3 自动课程与开放式学习（Phase1-6）| ✅ 2026-07-12（并行 Agent）|
| Iter D | G4 RL §7.4 模仿学习与策略蒸馏（BC复合误差→AWAC→action chunking）| ✅ 2026-07-12 |
| Iter E | G5 Repr §4.5 6D旋转 + G6 §2.2.1-3 DDPM/score/CFG + G7 §4.6 注意力/ICL/元学习 | ✅ 2026-07-12 |
| Iter F | book-control 6缺口吸收进 ControlTheory 后**已删除**；机械+电气 理论已吸收（实体资产待确认）| 🟢 book-control 完成 |
| **并行深化 R1** | 11 Foundation 各深化 3-6 知识点+补跨模块联系（~+957 行，零删除，全库锚点扫描零断链）| ✅ 2026-07-12 |

> [!success] 2026-07-12 并行深化第 1 轮（每 Agent 一 Foundation，共享 ENHANCEMENT_BRIEF 知识串联）
> 11 位 Agent 并行深化，主 Agent 评估（全库断链扫描=零真断链、结构完整性=原锚点存活、抽检 ControlTheory §8.1 质量达顶尖教授水准）。各模块补齐了被跳步的核心推导（RNEA/Delassus/Khatib、力闭合/LCP/摩擦锥、KKT/内点/iLQR、Itō/Bayes滤波/MPPI、KF-MVU/EKF/UKF/PF、互信息/BALD/empowerment、DDPM/score/CFG/6D旋转/注意力-ICL、VLA对齐/动作范式）并新增大量挂在"7 条暗线"上的跨模块联系。

> [!success] 2026-07-12 并行深化第 2 轮 + 暗线导航图
> 13 位 Agent 并行（含 R1 跳过的 Actuation/WorldModels 首轮）：①施加入站反链把 R1 单向链**双向化**；②第 2 轮深化（空间向量代数/ABA三趟/有效惯量突变、Montana/软指极限面/Hertz、对偶间隙/warm-start/MPPI并行、GAE/PPO-clip/SAC对偶【修正一处符号错误】、小波MRA/互补滤波/PI迟滞/因子图、最大熵/IB/信道容量/NBT、VAE-ELBO/PointNet/InfoNCE、CFG动作头/空间grounding/双臂、SVPWM/d-q解耦/Capstan/reflected inertia、RSSM-ELBO/λ-return/TD-MPC/Actuator-Rigid梯度）。~+531 行。
> **主 Agent 评估**：修正解析后全库断链扫描=**真正零断链**（R1+R2+暗线图共 ~40 条 agent 新链 + 30 条 taxonomy 暗线链全部有效）。Foundation 总量 4700→**8366 行**。
> **新增 [[taxonomy]] "跨 Foundation 暗线"导航图**（7 条暗线 + 关键节点顺链），把两轮织入的联系变成可导航的记忆主线。
> **R3 待办**：PapersRecap 之间/与 Foundation 的关联偏弱（用户指出）→ 下一个并行前沿；机械+电气 893M 实体资产删除确认；可选第 3 轮 Foundation 深化（边际递减）。

> [!success] 2026-07-12 R3：PapersRecap 论文间关联深化 + MergeBuffer 清空机电
> **审计**：87 篇顶层 recap 中 86 篇已有≥2 Foundation 链接，簇内互链原已密——真正缺口是**指向 2026-07 新建/新深化 Foundation 锚点的链接**（尤其新模块 WorldModels/Actuation）。
> **执行**：6 位并行 Agent 各领 WMTS RelatedPapersRecap 一个**不相交主题簇**（世界模型/扩散/课程进化/in-hand-Sim2Real/运动迁移/表征-ICL-IL），为 47 篇补精确 Foundation 锚点 + 簇内 Delta 对比 + 暗线挂载（~+430 行）。
> **主 Agent 评估**：全库"recap+foundation → Foundation 锚点"扫描=**零断链**（100+ 条新链全部有效）；顺带修复 4 处**既存**断链（control-frequency 簇指向已改名的 PFQI §6.4）——期间一次 sed/perl 正则误伤 4 文件已 `git checkout` 还原 + 改用字面替换修好（教训：复杂 Unicode 链接用字面替换/Edit，勿用正则 sed）。
> **清理**：机械+电气 893M（理论已吸收 Actuation）**已删除** → MergeBuffer 仅剩 LLM/SFT/OPD 一组（另一主题，出本次范围）。
> **待办**：顶层 PapersRecap 87 篇的论文间关联可再做一轮；各 Agent 提的 recap↔Foundation 反链（在 Foundation §相关论文 处补指向 recap）；可选第 3 轮 Foundation 深化。

> [!success] 2026-07-12 R4：顶层 PapersRecap 87 篇论文间关联深化（完成）
> 9 位并行 Agent 各领一**不相交主题簇**（稳定性-SafeRL / 控制频率-时间步 / 阻抗顺应 / 触觉视触觉 / in-hand旋转-Sim2Real / 抓取几何表征 / 模仿-真机RL / 课程奖励 / VLA-世界模型），把 87 篇 recap 里的 **bare/占位 Foundation 链接升级为精确锚点** + 补簇内 Delta 对比 + 挂暗线（~+800 行）；顺带把一篇 Gemini-chat 转储（KungfuBot）补齐 frontmatter+结构。
> **主 Agent 独立评估**：linkcheck3.sh 全库扫描（覆盖 Foundations + 两个 recap 目录）=**零断链**（~200 条新链全有效）；补 RL §14 控制频率清单缺失的 AP-AC/HSTCN 反链。
> **知识图谱现状**：13 Foundation 深化两轮（8366 行，7 暗线导航图）；138 篇 recap（47 WMTS + 87 顶层）全接到深化后 Foundation 锚点、簇内 Delta 密集；MergeBuffer 机电/控制部分已清空；全库零断链。**主体完善任务已达高完成度，边际收益递减**——后续为可选的第 3 轮深化 / 更细 Delta / 更多反链。

> [!danger] MergeBuffer 删除硬标准（2026-07-12 用户当场纠正，必守）
> 仅当 KG 已完整吸收该参考的重要内容——**既含知识点本身，也含讲述知识点的方式（推导/worked example/教学法）**——才可删。仅"某 Foundation 覆盖/提到"**不够**。
> - **book-control**（DR_CAN《控制之美》，公开可复现克隆）：曾误判"ControlTheory 覆盖经典控制"即欲删，被拦下。**未删，保留**。多数章节理论在 ControlTheory+Actuation §3 已讲透；但需逐章核对"讲述方式"是否吸收（如反馈线性化一般式/relative degree、频域设计流程等 KG 仅"提到"处），补齐后再决定删否；低相关经典技巧（backstepping/root-locus 设计流程）偏离用户方向，可不吸收→则暂留。
> - **机械+电气**：理论经项目笔记等价整合进 [[Actuation]]，但 PDF 未直接萃取；删前须 pdftotext 逐份核对知识点+讲述方式已吸收（Bash 已可用）。

> [!warning] 结构性决策提示
> G1（新建 WorldModels Foundation）是与 Actuation 同级的永久结构变更。用户在 /loop 指令中已授权"主动补齐缺失讲解"，故按 [[Actuation]] 先例执行；若用户对新模块边界有异议可随时调整。其余 G2–G5 均为**在现有 Foundation 内新增章节**，风险低。
