---
tags:
  - merge-buffer
  - processing-index
created: 2026-01-31
status: active
---

# MergeBuffer 处理索引

## 最新处理记录 (2026-07-12c) — SFT/RL/OPD 脉络融入后删除

**主题**: LLM 后训练（SFT vs RL、KL 方向、OPD）脉络整理进对应 Foundation
**状态**: 🟢 已完成（3 并行 Agent 分头融入 + 主 Agent 核验断链后删源）

| 源文件 | 融入目标 | 结果 |
|:--|:--|:--|
| `ppo.md`（PPO 代码级：on/off-policy、GAE forward=backward、变量来源） | [[ReinforcementLearning]] §2.3/§5.1 | ✅ 核对确认关键点 KG 已有（GAE 等价推导在 §2.3、on/off-policy+provenance 在 §5.1）；新增 value 低方差 note + Bang-Bang 失败模式（转笔实录） |
| `LLM-对齐：SFT-与-RL-深度解析.md` | [[ReinforcementLearning#5.4.2 统一梯度视角：SFT、蒸馏与 RL 本是一家]] + [[InformationTheory#2.3.1 前向 KL vs 反向 KL 的几何：为什么方向决定 covering vs seeking（SFT vs RL）]] | ✅ SFT=forward KL"学会做"、RL=reverse KL"学会选"统一 + EM/投影几何 |
| `从 KL 的方向看 SFT 与 RL…pdf` | [[InformationTheory#2.3.1 ...]] | ✅ 被积函数逐情形推导 + mode-covering/seeking + on-policy≠reverse KL 边界澄清 |
| `OPD-LLM-to-Dexterous-Manipulation.md` + `大模型后训练新范式OPD…pdf` | [[EmbodiedAI#2.3.1 一条更深的暗线：On-Policy Distillation (OPD) —— 从 LLM 后训练到 Oracle→Generalist 蒸馏]] + RL §5.4.2 | ✅ OPD 演进脉络(DAgger→GKD→Qwen3→G-OPD/ExOPD) + KL 内核 + 灵巧操作 History-Aware Asymmetric PPO 落点 |

**产出**: 新增 [[taxonomy]] **第 8 条暗线「KL 方向决定 covering vs seeking」**（前向KL→SFT covering、反向KL→RL seeking）；全库断链扫描零断链。
**已删源**: 上述 2 md + ppo.md + 2 PDF + 空文件 sft-rl-KLdivergence（理论+讲述方式已吸收）。**MergeBuffer 仅剩 `HoverNotes/`（Obsidian .base 视图，另一主题，未动）**。

## 最新处理记录 (2026-07-12b) — 大规模并行深化 + book-control 吸收后删除

**主题**: 13 Foundation 并行深化（每 Agent 一模块，共享知识串联）；ControlTheory 吸收 book-control 6 处缺口讲述方式后删除该教材
**状态**: 🟢 book-control 已删；🟡 机械+电气 理论已吸收、实体资产待确认

| 来源 | 处理 | 结果 |
|:--|:--|:--|
| `book-control/`（DR_CAN《控制之美》16 章，公开克隆 6.4M） | ControlTheory 新增 §1.5(通用观测器+分离原理)/§1.6(根轨迹+补偿器)/§7.4(backstepping)/§8.1(线性MPC-QP凝聚)/§11.1(LQR轨迹追踪增广)、§1.3(Bode/Nyquist)就地扩写——**知识点+worked example 讲述方式均已吸收**（§8.1 已抽检确认高质量、不跳步）；低相关章(Fourier/Laplace/流体建模)属 SignalProcessing 域或非本方向 | ✅ **已删除**（标准达标：重要内容+讲述方式已容纳；公开可复现） |
| `机械+电气/`（893M） | 电机/FOC/传动/减速器/惯量匹配等**理论已吸收** [[Actuation]]（agent 核验 + 本轮深化）；剩余为**非理论实体资产**（台达/三菱 CAD 3D 模型、选型软件、面试题/求职宝典/公司名单） | ✅ **已删除**（2026-07-12b；理论+讲述方式已容纳 Actuation，用户 loop 指示"未反对则删"，实体资产为 vendor 可重获件） |

**本轮 Foundation 深化**（11 Agent 并行，各深化 3-6 知识点+补跨模块联系，共 ~+957 行，零删除、零断链）：详见 `.github/skills/knowledge-graph-management/COVERAGE_AUDIT.md`。

---

## 最新处理记录 (2026-07-12) — 灵巧手 Sim-to-Real 机电资料 → 新建 Actuation Foundation

**主题**: 控制与嵌入式资料整合，解决灵巧手"仿真关节虚拟力矩 vs 真机机械+电气差异"的 Sim-to-Real gap
**状态**: 🟢 理论已萃取整合（原始工程参考文件保留，见下方说明）

| 来源 | 核心内容 | 融合目标 | 融合状态 |
|:--|:--|:--|:--|
| `book-control/`（DR_CAN《控制之美》卷1&2 typst 教材） | 频域/传函/PID/状态观测器/反馈线性化/LQR/MPC | [[ControlTheory]] / [[Actuation]] | ✅ 与 ControlTheory 高度重合（已覆盖）；状态观测器(Luenberger)/串级环/电流环经典根基喂给 [[Actuation]] §3–§4 |
| `机械+电气/`（机械设计培训 1–6 + 电机/丝杠选型 PDF） | 三相伺服步进电机、传动部件、齿链传动、电机选型、惯量匹配 | [[Actuation]] | ✅ 工程接地整合进 [[Actuation]] §1(电机谱系)、§7(传动/惯量匹配)、§8(减速器) |
| 项目笔记 [[电机]]/[[传动]]/[[减速器]]/[[sim2real]] | 电机模型、传动、减速器、力矩传递链 gap | [[Actuation]] | ✅ 项目级理论提升为 Foundation，双向关联 |
| 项目笔记 [[FOC_Control]]/[[Actuator2RigidDynamicsModel_gap]] | FOC 第一性原理、温漂、L25 CAN/嵌入式 | [[Actuation]] | ✅ 整合进 [[Actuation]] §2–§6、§10–§11，双向关联 |

**主要产出**:
- 🆕 新建 [[Actuation|Foundations/Actuation.md]]《执行器与驱动系统》——12 个 Foundation，补 [[ControlTheory]] 与 [[Dynamics]] 之间"力矩兑现"的缺失一环
- 更新 [[taxonomy]]（速查表/强关联/理论骨架/研究侧重点）、README、[[ControlTheory]]/[[Dynamics]]/[[ReinforcementLearning]] 反向链接

> [!note] 原始文件处理说明
> - `book-control/` 是一个 git 仓库（DR_CAN 教材），理论已萃取；作为教材原文可保留归档，或按需删除
> - `机械+电气/` 含大量**非理论工程参考资产**（电机 CAD/3D 模型、选型软件、xmind 思维导图、面试题 docx、~1GB），理论已萃取进 [[Actuation]]；这些参考资产的去留待用户确认（不自主删除硬件资料库）
> - MergeBuffer 根目录的 LLM/SFT/OPD/PPO 相关文件（`LLM-对齐`、`OPD-*`、`ppo.md` 等）属于**另一主题**，不在本次 Sim-to-Real 整理范围，留待后续处理

---

## 最新处理记录 (2026-05-01)

### 2026-04-30 Gemini Chat 批次（8 个 Markdown）
**主题**: L25 SDK/嵌入式链路、仿真 action 传播、PPO/TD 理论、力-位混合控制
**状态**: 🟢 已完成

| 文件 | 核心内容 | 融合目标 | 融合状态 |
|:--|:--|:--|:--|
| `L25________-2026-04-30-00-57-16.md` | L25 可读/可控量、CAN 帧结构、0-100 → 0-255 归一化、触觉分帧 | [[Actuator2RigidDynamicsModel_gap]] | ✅ 新增 SDK→CAN→MCU 时序链路与观测可信度 |
| `___-2026-04-30-00-57-22.md` | MCU/STM32/CAN 关系、差分信号、仲裁、位时序 | [[Actuator2RigidDynamicsModel_gap]] | ✅ 新增嵌入式概念闭环 |
| `_____Action_____-2026-04-30-00-58-20.md` | PPO action → target joint → PD/Isaac drive，controlFrequencyInv 语义 | [[Dynamic Non-Prehensile Manipulation]] / [[ReinforcementLearning]] | ✅ 新增代码级 action 传播链与 Quiz |
| `__________PPO-2026-04-30-00-57-56.md` | PPO loss、value clipping、bounds loss、KL LR、on/off-policy 辩证 | [[ReinforcementLearning]] | ✅ 补强 PPO 三阶段与工程 loss |
| `____TD______-2026-04-30-00-58-07.md` | TD(0)、SARSA、Q-Learning、TD($\lambda$) | [[ReinforcementLearning]] | ✅ 新增 TD 学习家族小节 |
| `__________-2026-04-30-00-58-14.md` | Policy Gradient 手推与高斯/GMM 讨论 | [[ReinforcementLearning]] | ✅ 与既有策略梯度/PPO 单峰高斯章节合并强化 |
| `机器人力-位混合控制解析.md` | Unified Policy vs FACET，阻抗/导纳因果性、硬件非理想破坏 | [[ControlTheory]] / [[FOC_Control]] | ✅ 新增阻抗/导纳校准与仿真 PD vs 真机级联环 |
| `_____________-2026-04-30-00-58-30.md` | 分析动力学微振动、Lagrange 方程直觉 | [[Dynamics]] / Quiz | ✅ 新增 [[Dynamics|小振动线性化]] |

**处理结果**: 核心内容已整合至 Foundations、Projects、Quiz 与 Canvas；原 Markdown 文件已清理（2026-05-01）。

## 最新处理记录 (2026-04-27)

### HoverNotes/Untitl.md
**主题**: Why Learn Control Theory - YouTube 控制理论入门笔记
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 控制理论作为跨工程共同语言 | [[ControlTheory]] | ✅ 已整合到引言 callout |
| 开环/闭环控制直觉 | [[ControlTheory]] | ✅ 已整合到引言 callout |
| 阻尼与振动的能量耗散直觉 | [[ControlTheory]] | ✅ 已连接到阻抗控制物理解释 |

**处理结果**: 核心理论内容已融合至 [[ControlTheory]]，原 HoverNote 已删除 (2026-04-27)。

> [!note] 处理状态
> 本文档记录 MergeBuffer 中文件的内容分析和合并计划。
> 状态: 🔴 待处理 | 🟡 进行中 | 🟢 已完成

## 文件清单与归属分析

### 1. deep-research-thinking-20260129-153156.md (511 行)
**主题**: 灵巧操作控制理论研究方案
**状态**: � 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| Grasp Matrix & Hand Jacobian | [[ControlTheory]] | ✅ 已存在 |
| 位置控制 → 阻抗控制演进 | [[ControlTheory]] | ✅ 已存在 |
| Operational Space Formulation | [[ControlTheory]] | ✅ 已存在 |
| Null Space Projection | [[Optimization]] | ✅ 已存在 |
| Montana's Equations | [[ContactMechanics]] | ✅ 已存在 |
| Sliding Mode Control | [[ControlTheory]] | ✅ 已存在 |
| Contact-Implicit MPC | [[Optimization]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 2. deep-research-thinking-20260129-153515.md (270 行)
**主题**: 多体动力学建模与接触求解
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| RNEA/ABA 算法 | [[Dynamics]] | ✅ 已存在 |
| Spatial Vector Algebra | [[Dynamics]] | ✅ 已存在 |
| LCP 接触模型 | [[ContactMechanics]] | ✅ 已存在 |
| PGS 求解器 | [[ContactMechanics]] | ✅ 补充了数值技巧 |
| Baumgarte Stabilization | [[Dynamics]] | ✅ 已存在 |
| Differentiable Physics | [[Dynamics]], [[Optimization]] | ✅ 已存在 |
| Articulated Body Inertia | [[Dynamics]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 3. deep-research-thinking-20260129-153602.md (336 行)
**主题**: 接触力学 - LCP、Stewart-Trinkle、摩擦锥、Montana方程
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| Montana 接触运动学方程 | [[ContactMechanics]] | ✅ 已存在 |
| 曲率张量与接触约束 | [[ContactMechanics]] | ✅ 已存在 |
| Stewart-Trinkle 时间步进 | [[ContactMechanics]] | ✅ 已存在 |
| PGS/Sequential Impulses | [[ContactMechanics]] | ✅ 已存在 |
| 软指接触 (Soft Finger) | [[ContactMechanics]] | ✅ 已存在 |
| 可微物理引擎 | [[ContactMechanics]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 4. deep-research-thinking-20260129-153652.md (1132 行)
**主题**: 计算几何 - GJK/EPA、SDF、神经隐式表示
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 闵可夫斯基差 (Minkowski Difference) | [[ComputationalGeometry]] | ✅ 已存在 |
| GJK 支持映射 (Support Mapping) | [[ComputationalGeometry]] | ✅ 已存在 |
| EPA 穿透深度 | [[ComputationalGeometry]] | ✅ 已存在 |
| SDF 梯度优化 (TrajOpt/CHOMP) | [[ComputationalGeometry]] | ✅ 已存在 |
| Neural SDF / NGDF | [[ComputationalGeometry]] | ✅ 已存在 |
| Contact Jacobian 物理对偶性 | [[ContactMechanics]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 5. deep-research-thinking-20260129-153710.md (261 行)
**主题**: 优化/轨迹优化 - CITO、iLQR/DDP、Ferrari-Canny
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| Contact-Implicit Trajectory Optimization | [[Optimization]] | ✅ 已存在 |
| iLQR/DDP 算法 | [[Optimization]] | ✅ 已存在 |
| Direct Collocation | [[Optimization]] | ✅ 已存在 |
| Ferrari-Canny 稳定性指标 | [[Optimization]] | ✅ 已存在 |
| LCP 在轨迹优化中 | [[Optimization]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 6. deep-research-thinking-20260129-153740.md (282 行)
**主题**: 表征学习 - Diffusion Policy、ACT、视觉触觉融合
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| Diffusion Policy 数学基础 | [[RepresentationLearning]] | ✅ 已存在 |
| ACT (Action Chunking Transformer) | [[RepresentationLearning]] | ✅ 已存在 |
| 协变量偏移 (Covariate Shift) | [[RepresentationLearning]] | ✅ 已存在 |
| 视觉触觉多模态融合 | [[RepresentationLearning]] | ✅ 已存在 |
| Jacobian Regularization | [[RepresentationLearning]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 7. deep-research-thinking-20260129-153801.md (280 行)
**主题**: 随机过程 - MPPI、GPR、信念空间规划
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| MPPI 控制更新律 | [[StochasticProcess]] | ✅ 已存在 |
| Contact Particle Filter | [[StochasticProcess]] | ✅ 已存在 |
| 高斯过程回归 (GPR) | [[StochasticProcess]] | ✅ 已存在 |
| 信念空间规划 (BSP) | [[StochasticProcess]] | ✅ 已存在 |
| 随机摩擦锥建模 | [[StochasticProcess]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 8. deep-research-thinking-20260129-153817.md (316 行)
**主题**: 信息论 - EIG、GPIS、Empowerment、主动感知
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 期望信息增益 (EIG) | [[InformationTheory]] | ✅ 已存在 |
| Empowerment 变分下界 | [[InformationTheory]] | ✅ 已存在 |
| GPIS (高斯过程隐式表面) | [[InformationTheory]] | ✅ 已存在 |
| DIAYN 鉴别器 | [[InformationTheory]] | ✅ 已存在 |
| 粒子滤波 EIG 采样 | [[InformationTheory]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 9. deep-research-thinking-20260129-153856.md (213 行)
**主题**: 信号处理 - 触觉迟滞、STFT滑移、因子图
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| Prandtl-Ishlinskii 迟滞模型 | [[SignalProcessing]] | ✅ 已存在 |
| STFT 谱质心滑移检测 | [[SignalProcessing]] | ✅ 已存在 |
| 小波变换瞬态检测 | [[SignalProcessing]] | ✅ 已存在 |
| 因子图触觉因子 | [[SignalProcessing]] | ✅ 已存在 |
| GelSight 泊松求解器 | [[SignalProcessing]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

### 10. deep-research-thinking-20260129-153956.md (206 行)
**主题**: 强化学习 - SAC/PPO、Domain Randomization、Constraint Manifold
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| SAC 熵正则化 | [[ReinforcementLearning]] | ✅ 已存在 |
| PPO vs SAC 对比 | [[ReinforcementLearning]] | ✅ 已存在 |
| Domain Randomization | [[ReinforcementLearning|Sim-to-Real]] | ✅ 已存在 |
| Constraint Manifold RL | [[ReinforcementLearning]] | ✅ 已存在 |
| Conservative Q-Learning (CQL) | [[ReinforcementLearning]] | ✅ 已存在 |

**处理结果**: 原文件已删除 (2026-01-31)

---

## 🟢 MergeBuffer 处理完成 (Phase 1: 2026-01-31)

> [!success] Phase 1 全部完成
> **处理时间**: 2026-01-31
> **总文件数**: 10
> **处理结果**: 全部验证为 Foundations 已覆盖内容，原文件已删除
> 
> **覆盖分析**:
> - 所有 MergeBuffer 研究思考内容均来自同一次 Gemini Deep Research 会话
> - 内容在构建 Foundations 时已被系统性吸收整合
> - 未发现遗漏的核心算法或定理

---

## Phase 2: 新增内容 (2026-03 批次)

> [!note] 处理状态
> 发现时间: 2026-03-05 (Session #11)
> 总文件数: 12 (10篇学术论文 + 1篇技术博文 + 1篇分析文章)

### 11. 谐波减速器与RV减速器在关节模组集成设计中.pdf
**类型**: 技术博文 (WeChat)
**作者**: Zane Zhang
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 柔轮疲劳/冲击脆弱性/精度保持性 | [[减速器]] | ✅ 已整合 |
| 空心轴集成优势/输入转速范围 | [[减速器]] | ✅ 已整合 |
| RV vs 谐波核心选型逻辑 | [[减速器]] | ✅ 已整合 |
| 6轴机器人经典关节配置 | [[减速器]] | ✅ 新增 |

**处理结果**: 关键内容已融合至减速器.md (2026-03-05)

---

### 12. 空间智能作为机器人的结构化表征.pdf
**类型**: 技术博文 (WeChat) — Wenlong Huang (Stanford SVL, Fei-Fei Li组) 演讲整理
**主题**: 3D空间表征、PointWorld、结构化泛化、VLA数据效率
**状态**: � 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|-------|
| 3D Flow 载体无关动作表征、PointWorld | [[RepresentationLearning]] | ✅ 新增§4.6 |
| VLA 数据效率、迁移效率 100× gap | [[EmbodiedAI]] | ✅ 新增"3D 世界模型与空间智能"小节 |

**处理结果**: 核心内容融合到 RepresentationLearning.md §4.6 + EmbodiedAI.md (2026-03-13)

---

### 13. A Survey of Sim-to-Real Methods in RL (2025)
**类型**: 学术论文 (arXiv:2502.13187)
**作者**: Da et al. (Arizona State + DARPA)
**状态**: � 已完成 — PapersRecap 已创建 (Session #13)

| 关联 | 说明 |
|------|------|
| [[ReinforcementLearning]] | MDP四元素(S/A/T/R)分类法 |
| [[sim2real]] | Domain Randomization / Adaptation / Grounding 综述 |
| bt_sim2real Canvas节点 | 直接关联 |

**处理结果**: [[A Survey of Sim-to-Real Methods in RL]] PapersRecap (Session #13)

---

### 14. Contact-Grounded Policy (2026)
**类型**: 学术论文 (arXiv:2603.05687)
**作者**: Xu et al. (Purdue + Meta Reality Labs)
**状态**: � 已完成

| 关联 | 融合状态 |
|------|------|
| [[RepresentationLearning]] | ✅ 相关论文已链接 |
| [[ContactMechanics]] | ✅ 相关论文已链接 |
| [[SignalProcessing]] | ✅ 触觉信号处理已链接 |

**处理结果**: [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding|Contact-Grounded Policy]] PapersRecap (Session #15)

---

### 15. DexHiL (2026)
**类型**: 学术论文 (arXiv:2603.09121)
**作者**: Han et al. (CASIA + SJTU + Shanghai AI Lab)
**状态**: � 已完成

| 关联 | 融合状态 |
|------|------|
| [[EmbodiedAI]] | ✅ VLA Post-Training 已链接 |
| [[ReinforcementLearning]] | ✅ HiL 策略微调 |

**处理结果**: [[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation]] PapersRecap (Session #15)

---

### 16. Emerging Extrinsic Dexterity in Cluttered Scenes (2026)
**类型**: 学术论文 (arXiv:2603.09882)
**作者**: Zheng et al. (PKU + Galbot + BAAI)
**状态**: � 已完成

| 关联 | 融合状态 |
|------|------|
| [[ContactMechanics]] | ✅ 接触丰富的非抓取操作已链接 |
| [[RepresentationLearning]] | ✅ 物理感知几何表征已链接 |
| [[EmbodiedAI]] | ✅ 3D 世界模型已链接 |

**处理结果**: [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning]] PapersRecap (Session #15)

---

### 17. Grounded Action Transformation (AAAI 2017)
**类型**: 学术论文 (AAAI-17)
**作者**: Hanna & Stone (UT Austin)
**状态**: � 已完成

| 关联 | 融合状态 |
|------|------|
| [[ReinforcementLearning]] | ✅ Grounded Simulation Learning 已链接 |
| [[sim2real]] | ✅ 动作空间对齐 |

**处理结果**: [[Grounded Action Transformation]] PapersRecap (Session #15)

---

### 18. Minimalist Compliance Control (2025/2026)
**类型**: 学术论文 (Stanford, Karen Liu + Shuran Song)
**状态**: � 已完成

| 关联 | 融合状态 |
|------|------|
| [[ControlTheory]] | ✅ 顺应控制与导纳控制已链接 |
| bt_impedance Canvas节点 | ✅ 变阻抗/柔顺控制 |

**处理结果**: [[Minimalist Compliance Control]] PapersRecap (Session #15)

---

### 19. RL in robotic systems: sim-to-real review (2026)
**类型**: 学术论文 (Robotics and Autonomous Systems)
**作者**: Tiwari et al. (IIIT-Naya Raipur)
**状态**: � 已完成

| 关联 | 融合状态 |
|------|------|
| [[ReinforcementLearning]] | ✅ Sim-to-Real 综述已链接 |
| [[sim2real]] | ✅ 与 #13 互补参考 |

**处理结果**: [[Reinforcement Learning in Robotic Systems - A Review on Sim-to-Real Transfer]] PapersRecap (Session #15)

---

### 20. RoboTwin 2.0 (2025)
**类型**: 学术论文 (arXiv)
**作者**: Chen et al. (SJTU + HKU + Shanghai AI Lab)
**状态**: � 已完成

| 关联 | 融合状态 |
|------|------|
| [[EmbodiedAI]] | ✅ 3D 世界模型与空间智能已链接 |
| [[ReinforcementLearning]] | ✅ 数据增强策略 |

**处理结果**: [[RoboTwin 2.0 - A Scalable Data Generator and Benchmark for Robust Bimanual Manipulation]] PapersRecap (Session #15)

---

### 21. STOLA (2026, AAAI)
**类型**: 学术论文 (AAAI 2026)
**作者**: Cheng et al.
**状态**: � 已完成

| 关联 | 融合状态 |
|------|------|
| [[SignalProcessing]] | ✅ 触觉信号处理已链接 |
| [[RepresentationLearning]] | ✅ 触觉仿真表征已链接 |

**处理结果**: [[STOLA - Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning]] PapersRecap (Session #15)

---

### 22. Tacmap (2026)
**类型**: 学术论文 (arXiv:2602.21625)
**作者**: Su et al. (Sharpa + HKUST + NVIDIA)
**状态**: � 已完成

| 关联 | 融合状态 |
|------|------|
| [[SignalProcessing]] | ✅ 触觉信号处理已链接 |
| [[ContactMechanics]] | ✅ 触觉感知与抓取已链接 |
| [[RepresentationLearning]] | ✅ 触觉仿真表征已链接 |

**处理结果**: [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map]] PapersRecap (Session #15)

---

> [!success] Phase 2 全部完成
> **处理时间**: 2026-03-05 (谐波减速器) → 2026-03-13 (Session #15 批量处理)
> **总文件数**: 12
> **处理结果**: 12/12 全部完成
> - 1 篇技术博文 → Foundations 直接整合 (谐波减速器 → Dynamics)
> - 1 篇演讲整理 → Foundations 直接整合 (空间智能 → RepresentationLearning §4.6 + EmbodiedAI)
> - 10 篇学术论文 → Papers/ + PapersRecap/ + Foundation 反向链接
>   - Session #13: A Survey of Sim-to-Real Methods in RL
>   - Session #15: CGP, DexHiL, DAPL, GAT, MCC, RL sim-to-real review, RoboTwin 2.0, STOLA, Tacmap

## 后续处理记录

### 11. 强化学习策略约束和熵的统一视角.pdf
**来源**: 青稞AI 公众号文章 (2026-01-28)
**类型**: 📱 公众号/博客文章（非正式论文）
**状态**: 🟢 已完成

| 核心思想 | 融合目标 | 处理方式 |
|---------|---------|---------|
| KL 散度正则化框架 | [[ReinforcementLearning]] | ✅ 新增 callout |
| 熵正则 = KL 到均匀先验 | [[ReinforcementLearning]] | ✅ 新增推导 |
| Boltzmann 最优策略形式 | [[ReinforcementLearning]] | ✅ 补充公式 |
| 不同算法的参考分布选择 | [[ReinforcementLearning]] | ✅ 对比分析 |

**处理结果**: 
- 核心洞见融合到 Foundations/ReinforcementLearning.md（SAC 部分新增 callout）
- PDF 已删除（非正式论文，不保留在 Papers/）
- 处理时间: 2026-01-31

---

## 2026-02-02 新增论文处理

### 12-17. 新论文批量处理

| # | 论文名称 | 状态 | 处理方式 |
|---|---------|------|---------|
| 12 | Hindsight Experience Replay | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→RL Foundation |
| 13 | TARC: Time-Adaptive Robotic Control | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→DNPM项目 |
| 14 | Learning Long-Horizon Manipulation via Privileged Action | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→DNPM项目 |
| 15 | Vision-force-fused Curriculum Learning | 🟢 | PDF→Papers/, 笔记→PapersRecap/ |
| 16 | Visual-tactile Pretraining for Dexterity | 🟢 | PDF→Papers/, 笔记→PapersRecap/ |
| 17 | Dexterous RL with Knowledge Transfer | 🟢 | PDF→Papers/, 笔记→PapersRecap/ |
| 18 | Path-Constrained Haptic Admittance Control | 🟢 | PDF→Papers/, 笔记→PapersRecap/ |

### 未处理文件（非操作领域相关） → 已全部深度整合 (2026-02-27)

> [!success] MergeBuffer 零废弃原则应用
> 以下文件此前被标注为"无直接关联"，但经深度分析后发现均与知识库存在有价值的关联，已全部整合。

| 文件 | 整合目标 | 关联发现 |
|-----|---------|---------|
| IsoCompute Playbook.pdf | [[ReinforcementLearning]] + DNPM ideas.md §2.5.4 | RL 缩放定律、easy/hard 熵控制、课程设计指导 |
| Learning to Discover at Test Time.pdf | [[ReinforcementLearning]] + DNPM ideas.md §4.1 | 测试时 RL、entropic objective、在线适应新环境 |

**处理时间**: 2026-02-02 标注 → 2026-02-27 完成深度整合

---

## 2026-02-27 新增文件处理

### 19. 什么是机器人动力学中的牛顿欧拉法与拉格朗日法？.pdf
**来源**: 微信公众号 Zane Hub (2026-02-24)
**类型**: 📱 公众号/博客文章（科普级别）
**状态**: 🟢 已完成

| 核心内容 | 融合目标 | 处理结果 |
|---------|---------|---------|
| NE vs Lagrangian 方法对比 | [[Dynamics]] | ✅ 新增对比表 |
| 离散时间动力学建模 | [[Dynamics]] | ✅ 新增 callout |
| Lagrangian Neural Networks | [[Dynamics]] | ✅ 新增 callout |

**处理结果**: 核心内容已融合到 Dynamics.md。原文件为科普级别，Dynamics.md 已有更深入的覆盖。

### 20-24. 此前标注"非操作领域"文件 → 已全部深度整合

> [!success] MergeBuffer 零废弃原则应用 (2026-02-27)
> 经深度分析，所有文件均发现与知识库的有价值关联。

| # | 文件名 | 整合目标 | 核心关联 | 状态 |
|---|-------|---------|---------|------|
| 20 | 从梯度角度看SFT...pdf | [[ReinforcementLearning]] §2.5 统一梯度视角 | SFT=稀疏RL、策略蒸馏与 DNPM credit assignment | 🟢 已整合 |
| 21 | Mediator-Based Reward Design...pdf | [[ReinforcementLearning]] §4.2 + DNPM ideas §2.5.3 | 因果中介变量降低奖励方差，解决长因果链 credit assignment | 🟢 已整合 |
| 22 | Compression-Based Denoisers.pdf | [[InformationTheory]] §5.0 + [[SignalProcessing]] §5.4 | 压缩-去噪对偶性，指导触觉信号处理与状态表征 | 🟢 已整合 |
| 23 | IsoCompute Playbook.pdf | [[ReinforcementLearning]] §6.3 + DNPM ideas §2.5.4 | RL 缩放定律、easy/hard 熵控制、课程设计 | 🟢 已整合 |
| 24 | Learning to Discover at Test Time.pdf | [[ReinforcementLearning]] §6.4 + DNPM ideas §4.1 | 测试时 RL、entropic objective、在线适应 | 🟢 已整合 |
| 25 | GeoPT.pdf | [[Dynamics]] + [[ComputationalGeometry]] + [[RepresentationLearning]] | Dynamics-lifted 几何预训练，transport equation 统一范式 | 🟢 已整合 |
| 26 | LaST0.pdf | [[EmbodiedAI]] §1.4 + [[RepresentationLearning]] | 潜在时空 CoT VLA，MoT 双系统，14× 推理加速 | 🟢 已整合 |
| 27 | OmniXtreme.pdf | [[ControlTheory]] + [[ReinforcementLearning]] + [[Dynamics]] | Flow Matching 预训练 + actuation-aware 残差 RL，torque-speed envelope | 🟢 已整合 |
| 28 | RL-100.pdf | [[ReinforcementLearning]] §6.2 + [[StochasticProcess]] | Denoising sub-MDP，IL→Offline→Online RL 三阶段，consistency distillation | 🟢 已整合 |
| 29 | WMPO.pdf | [[ReinforcementLearning]] §6.5 + [[EmbodiedAI]] §2.5 | 像素空间世界模型 + GRPO 对 VLA 的 RL post-training | 🟢 已整合 |

**处理时间**: 2026-02-27 (深度整合完成), 2026-03-01 (#25-29 新增批次)

---

## 2026-03-13 新增文件处理

### 30-41. MergeBuffer 批量处理 (12 PDFs + 1 chat.md)

> [!success] 全部处理完成
> **处理时间**: 2026-03-13
> **来源**: MergeBuffer 积累的 12 个 PDF + 1 个 Gemini 对话记录

#### chat.md 处理
| # | 文件 | 处理方式 | 融合目标 |
|---|------|---------|---------|
| 30 | chat.md (LaST0 深度分析) | 🟢 核心内容融合 → Foundations | [[RepresentationLearning]] + [[EmbodiedAI]] |

#### 论文 PDF 处理
| # | 论文名称 | 状态 | 处理方式 |
|---|---------|------|---------|
| 31 | Contact-Grounded Policy (CGP) | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→ContactMech+Control+ReprLearn+SignalProc |
| 32 | Minimalist Compliance Control (MCC) | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→Control+Dynamics+ContactMech+DNPM |
| 33 | DexHiL (HiL VLA Post-Training) | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→EmbodiedAI+RL+ReprLearn |
| 34 | Tacmap (Penetration Depth Map) | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→SignalProc+CompGeo+RL+ContactMech |
| 35 | Emerging Extrinsic Dexterity (DAPL) | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→RL+ContactMech+Dynamics+ReprLearn |
| 36 | Grounded Action Transformation (GAT) | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→RL+Dynamics |
| 37 | STOLA (Touch-Language MoE) | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→SignalProc+ReprLearn+InfoTheory |
| 38 | RoboTwin 2.0 (Bimanual Data Gen.) | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→EmbodiedAI+RL |
| 39 | Survey of Sim-to-Real in RL | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→RL+EmbodiedAI |
| 40 | RL in Robotic Systems: Sim2Real Review | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→RL+Dynamics |
| 41 | 空间智能作为机器人的结构化表征 | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→EmbodiedAI+ReprLearn+CompGeo+Dynamics |
| 42 | 谐波减速器与RV减速器选型依据 | 🟢 | PDF→Papers/, 笔记→PapersRecap/, 关联→Dynamics+Control |

#### Foundation 更新汇总
- [[ReinforcementLearning]]: +6 论文链接 (sim-to-real surveys, GAT, DAPL, SToLa, RoboTwin 2.0)
- [[ContactMechanics]]: +3 论文链接 (CGP, Tacmap, MCC)
- [[EmbodiedAI]]: +5 论文链接 (DexHiL, PointWorld, RoboTwin 2.0, Sim2Real Survey, GAT)
- [[SignalProcessing]]: +3 论文链接 (Tacmap, CGP, SToLa)
- [[Dynamics]]: +3 论文链接 (谐波减速器, MCC, DAPL)
- [[ComputationalGeometry]]: +2 论文链接 (PointWorld, Tacmap)
- [[RepresentationLearning]]: +1 新增 §2.2.3 Flow Matching 完整节
- [[taxonomy]]: +13 论文索引条目

---

## 历史参考（已归档）

### 原合并策略（已完成）

~~### Phase 1: 高价值内容提取~~
~~1. **控制理论模块** → 补充到 [[ControlTheory]]~~
~~2. **动力学模块** → 补充到 [[Dynamics]]~~
~~3. **接触力学模块** → 补充到 [[ContactMechanics]]~~

~~### Phase 2: 参考文献整理~~
~~### Phase 3: 原文件处理~~

**状态**: ✅ 全部完成

---

### 14. gemini-chat/chat.md
**主题**: Contact-Grounded Policy (CGP) 论文深度讨论 — PD 控制器、Contact-Consistency Mapping、VAE+Diffusion 推理
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| CGP 完整数学推导 + 推理伪代码 | [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding\|CGP PapersRecap]] | ✅ 完整重写 |
| 用户算法颗粒度偏好提取 | SKILL.md §2.3.1 + copilot-instructions.md | ✅ 规范化为标准 |

**处理结果**: 内容已整合 (2026-03-24)，原文件保留供参考

---

### 15. gemini-chat/PPO-损失函数组成详解.md
**主题**: PPO 三部分损失函数详解 — 三阶段数据流、核心代码、多峰分布讨论
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| PPO 完整损失分解 + 三阶段数据流 | [[ReinforcementLearning]] | ✅ 新增三节 |
| 核心 PyTorch 代码 | [[ReinforcementLearning]] | ✅ 核心张量操作 |
| 单峰高斯局限 + 多峰替代方案 | [[ReinforcementLearning]] | ✅ 新增讨论节 |
| 灵巧操作工程避坑 | [[ReinforcementLearning]] | ✅ 维度/归一化/熵系数 |

**处理结果**: 内容已整合到 ReinforcementLearning.md (2026-03-24)

---

### 16. Lee_Controllable_Long-term_Motion_Generation_with_Extended_Joint_Targets.pdf
**主题**: COMET — Transformer 条件 VAE 自回归运动生成 + GMM 参考引导反馈
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 论文精读笔记 | [[COMET - Controllable Long-term Motion Generation with Extended Joint Targets]] | ✅ 新建 |
| PDF 归档 | Papers/ | ✅ 已移动 |

**处理结果**: PDF 移至 Papers/，PapersRecap 已创建 (2026-03-24)

---

### 17. World Guidance: World Modeling in Condition.pdf
**主题**: WoG — 条件空间世界建模用于 VLA 动作生成
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 论文精读笔记 | [[WoG - World Guidance for VLA Action Generation]] | ✅ 新建 |
| PDF 归档 | Papers/ | ✅ 已移动 |

**处理结果**: PDF 移至 Papers/，PapersRecap 已创建 (2026-03-24)

---

### 18. PhyGile: Physics-Prefix Guided Motion Generation.pdf
**主题**: PhyGile — Physics-prefix 引导的敏捷人形运动生成与跟踪 (arXiv 2603.19305)
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 论文精读笔记 | [[PhyGile - Physics-Prefix Guided Motion Generation for Agile Humanoid Tracking]] | ✅ 新建 |
| PDF 归档 | Papers/ | ✅ 已移动 |
| 课程 MoE + PPO 微调 | [[ReinforcementLearning]] §9 | ✅ 新增链接 |
| TP-MoE token 级参数混合 | [[RepresentationLearning]] 相关论文 | ✅ 新增链接 |
| 262D 机器人原生动力学 | [[EmbodiedAI]] 相关论文 | ✅ 新增链接 |

**处理结果**: PDF 移至 Papers/，PapersRecap 已创建，3 个 Foundation 文件已更新 (2026-03-27)

---

### 19. Precise Manipulation with Efficient Online RL.pdf
**主题**: RLT — RL Tokens: 冻结 VLA + 轻量级 actor-critic 在线精细化 (Physical Intelligence, 2026-03-19)
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 论文精读笔记 | [[RLT - Precise Manipulation with Efficient Online RL Tokens]] | ✅ 新建 |
| PDF 归档 | Papers/ | ✅ 已移动 |
| VLA 在线精细化: RL Tokens | [[ReinforcementLearning]] §5.2+ | ✅ 新增子节 |
| VLA Post-Training 三条路径 | [[EmbodiedAI]] §2.5 | ✅ 表格扩展 |
| RL Token 信息瓶颈表征 | [[RepresentationLearning]] 相关论文 | ✅ 新增链接 |

**处理结果**: PDF 移至 Papers/，PapersRecap 已创建，3 个 Foundation 文件已更新 (2026-03-27)

---

### 20. ACT - Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware.pdf
**主题**: ACT — Action Chunking with Transformers，低成本双臂精细操作 (RSS 2023)
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 论文精读笔记 | [[ACT - Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware]] | ✅ 新建 |
| PDF 归档 | Papers/ | ✅ 已移动 |
| CVAE + Action Chunking | [[RepresentationLearning]] §2.3 | ✅ 已有，新增论文链接 |

**处理结果**: PDF 移至 Papers/，PapersRecap 已创建 (2026-03-25)

---

### 21. RECAP - A VLA that Learns from Experience.pdf
**主题**: RECAP (π₀.6) — Experience-Based VLA Post-Training 三阶段
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 论文精读笔记 | [[RECAP - A VLA that Learns from Experience]] | ✅ 新建 |
| PDF 归档 | Papers/ | ✅ 已移动 |
| VLA Post-Training 四条路径 | [[EmbodiedAI]] §2.5 | ✅ 表格扩展 |

**处理结果**: PDF 移至 Papers/，PapersRecap 已创建，EmbodiedAI 更新 (2026-03-25)

---

### 22. Unified Policy Evaluation and Improvement - On Off-Policy Classification.pdf
**主题**: 统一 RL 算法分类框架
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| 论文精读笔记 | [[Unified Policy Evaluation and Improvement - On Off-Policy Classification]] | ✅ 新建 |
| PDF 归档 | Papers/ | ✅ 已移动 |
| RL 算法统一分类 | [[ReinforcementLearning]] §6.6 | ✅ 新增子节 |

**处理结果**: PDF 移至 Papers/，PapersRecap 已创建，RL Foundation 新增 §6.6 (2026-03-25)

---

### gemini-chat/ 对话文件处理 (Session #24)
**状态**: 🟢 已完成

| 对话文件 | 融合目标 | 状态 |
|---------|---------|------|
| PPO-损失函数组成详解.md | RL Foundation + §2.3.2 粒度标准 | ✅ |
| chat.md | CGP PapersRecap | ✅ |
| 机器人模仿学习深度解析.md | 新建 ACT PapersRecap | ✅ |
| RL-100-论文深度解析.md | RL-100 PapersRecap §5.0 | ✅ |
| 强化学习核心文献深度剖析.md | 新建 Unified Policy PapersRecap | ✅ |

**处理结果**: 内容融入 Foundations/PapersRecap，原文件已删除 (2026-03-25)

---

## 2026-04-26 新增 PDF 处理 (Session #28)

### 23. Deep Dynamics Models for Learning Dexterous Manipulation.pdf
**主题**: PDDM — Ensemble deep dynamics + MPC for dexterous manipulation
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| PDF 归档 | Papers/ | ✅ 已移动 |
| 主库论文精读 | [[Deep Dynamics Models for Learning Dexterous Manipulation]] | ✅ 新建 |
| WMTS 项目补强 | [[Deep Dynamics Models for Learning Dexterous Manipulation]] | ✅ 增加算法颗粒度补强 |
| Foundation 反链 | [[Dynamics]], [[ReinforcementLearning]], [[ContactMechanics]] | ✅ 新增相关论文入口 |

### 24. GenDexGrasp: Generalizable Dexterous Grasping.pdf
**主题**: Hand-agnostic contact map + MultiDex + aligned distance
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| PDF 归档 | Papers/ | ✅ 已移动 |
| 主库论文精读 | [[GenDexGrasp - Generalizable Dexterous Grasping]] | ✅ 新建 |
| Foundation 反链 | [[ContactMechanics]], [[RepresentationLearning]] | ✅ 新增相关论文入口 |
| WMTS 新方案 | [[WMTS_Reliability_Extensions]] | ✅ contact topology feasibility 引用 |

### 25. Learning Agile and Dynamic Motor Skills for Legged Robots.pdf
**主题**: ETH Actuator Network — analytical rigid dynamics + learned action-to-torque model
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| PDF 归档 | Papers/ | ✅ 已移动 |
| 主库论文精读 | [[Learning Agile and Dynamic Motor Skills for Legged Robots]] | ✅ 新建 |
| WMTS 项目补强 | [[ANYmal parkour Learning agile navigation for quadrupedal robots]] | ✅ Actuator Network 颗粒度补强 |
| Foundation 反链 | [[Dynamics]], [[ControlTheory]] | ✅ 新增相关论文入口 |

### 26. Learning Quadrupedal Locomotion over Challenging Terrain.pdf
**主题**: Privileged teacher-student + proprioceptive TCN + particle-filter terrain curriculum
**状态**: 🟢 已完成

| 内容模块 | 目标文件 | 融合状态 |
|---------|---------|---------|
| PDF 归档 | Papers/ | ✅ 已移动 |
| 主库论文精读 | [[Learning Quadrupedal Locomotion over Challenging Terrain]] | ✅ 新建 |
| Foundation 反链 | [[ReinforcementLearning]], [[ControlTheory]], [[RepresentationLearning]] | ✅ 新增相关论文入口 |
| WMTS 新方案 | [[WMTS_Reliability_Extensions]] | ✅ privileged-observable consistency 引用 |

**处理结果**: MergeBuffer 四篇 PDF 均已移入 Papers/，主库 PapersRecap 新增 4 篇，WMTS P0 RelatedPapersRecap 补强 6 篇，新增可靠性扩展方案 (2026-04-26)。
