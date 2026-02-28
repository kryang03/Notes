---
tags:
  - index
  - insight
  - DNPM
aliases:
  - DNPM Insights Index
  - 研究洞见索引
created: 2026-02-28
updated: 2026-02-28
---

# DNPM Research Insights Index

> [!abstract] 定位
> 本索引汇总了基于知识图谱全量分析（11 个 Foundations × 57 篇 PapersRecap × 项目痛点）交叉碰撞生成的原创研究 Idea。
> 每个 Idea 均经过**痛点-理论-文献三角定位**和**可行性评估**，配有完整故事线、方法论和实验计划。
>
> **动态迭代说明**：每个 Idea 文档包含"动态迭代日志"节，用于记录实验结果和迭代决策。所有 Idea 均包含"Stage 0: Grid Search 快速验证"——利用 8×A100 集群先用暴力方法快速验证核心假设，再推进完整实现。

> [!important] 🔄 远端服务器同步机制 (MergeBuffer 中转模式)
> 本地 `all_Insights_local/` 与远端 `all_Insights_server/` 通过 **MergeBuffer** 双向同步：
> - **本地→远端**：Idea 文档、CodeStructure 同步至服务器
> - **远端→本地**：实验结果通过 `MergeBuffer/all_Insights_server/` 中转回本地
> - 本地 Agent 处理后删除 MergeBuffer 中的服务器内容

---

## 📊 实验进度总览 (2026-02-28 更新)

| 实验板块 | 状态 | runs | 关键发现 | 影响的 Idea |
|---------|------|------|---------|----------|
| Smoke Test | ✅ 完成 | 8 | 8卡并行调度正常 | 全部 |
| Exp2: TA 奖励搜索 | ✅ 完成 | 24 | ⚡ Light BASE SR=0.83 > TWC; Heavy SR=0 | 003, 006 |
| Exp2: TP 奖励搜索 | ✅ 完成 | 24 | ⚡ Medium TWC SR=0.86 最优; Reduced TWC降方差19× | 001, 007 |
| Exp3a: Alpha 直接训练 | 🔄 运行中 | 16 | 待完成 | 001, 007 |
| 历史 Kp×AS 搜索 | ✅ 完成 | ~100+ | ⚡ TP 最优 Kp=3.5~8.5; Kd未独立搜索 | 001 |
| Exp1: Kp×AS 精细搜索 | ⏳ 待启动 | — | — | 001, 006 |
| Exp3b: 频率对齐 | ⏳ 待启动 | — | — | 001 |
| Exp4: 变阻抗 | ⏳ 待启动 | — | — | 001 |

> [!warning] ⚡ Exp2 核心发现摘要
> 1. **TA: 简洁奖励 + BASE 最优** — Light BASE SR=0.83, TWC 在 TA 上无显著优势
> 2. **TP: Medium TWC 最优** — SR=0.86, α→1.0, TWC 展现决定性优势
> 3. **Heavy 奖励普遍失败** — 过多 shaping reward 导致 reward hacking
> 4. **TWC 降方差显著** — TP Reduced TWC 方差降 19×, 但 TA 上 TWC 方差反而更大

---

## 优先级总览

| ID | 标题 | 核心贡献 | 可行性 | 新颖性 | 与HDC关系 | 优先级 | 目标会议 | Stage 0 耗时 |
|----|------|---------|--------|--------|----------|--------|---------|------------|
| 001 | [[Idea-001-Phase-Adaptive Impedance\|Phase-Adaptive Impedance]] | 多指独立时变阻抗 + 频率自适应统一框架 | A | A | 互补协同 | **P0** | RSS/CoRL | ~1天 |
| 002 | [[Idea-002-Autoregressive Exploration\|Autoregressive Exploration]] | 接触自适应时间相关探索噪声 | A | B+ | 直接增强 | **P0** | CoRL/ICRA | ~6h |
| 007 | [[Idea-007-Dual Orthogonal Curriculum\|Dual Orthogonal Curriculum]] | 物理难度 × 状态难度双正交课程 + ZVF 门控 | A | B+ | **直接嵌入HDC** | **P0** | RSS/CoRL | ~6h |
| 006 | [[Idea-006-Adaptive Lipschitz Actor\|Adaptive Lipschitz Actor]] | 状态自适应 Lipschitz 约束消除动作抖动 | A | B+ | 互补协同 | **P0→P1** | CoRL/ICRA | ~6h |
| 003 | [[Idea-003-Causal Mediator Reward\|Causal Mediator Reward]] | 基于因果中介变量的动力学感知奖励 | B+ | A | 独立成文 | **P1** | NeurIPS/ICML | ~1.5天 |
| 004 | [[Idea-004-Convex Safe Set Bootstrapping\|Convex Safe Set]] | 成功经验的几何 Bootstrapping | B | A | 互补协同 | **P1** | RSS/CoRL | ~1.5天 |
| 005 | [[Idea-005-Test-Time Contact Adaptation\|Test-Time Contact Adaptation]] | 部署时在线接触参数辨识与策略适应 | B | A | 后续延展 | **P2** | CoRL/ICRA | ~2天 |

---

## ⚡ Stage 0 Grid Search 执行计划

> [!important] 8×A100 集群全力运转计划
> 先用 Stage 0 Grid Search 并行验证所有 P0 Ideas 的核心假设，再根据结果决定深入方向。

```
Week 1 (Day 1-2): 并行启动全部 P0 Stage 0
├── GS-002: 固定 β AR-1 (15 runs, 6h)          → 验证 "时间相关噪声有用"
├── GS-007: 固定 δ 初始化混合 (15 runs, 6h)     → 验证 "成功状态初始化加速探索"
├── GS-006: 全局 K Lipschitz (15 runs, 6h)       → 验证 "动作平滑性有益"
└── GS-001: Kp Grid Search (20 configs, ~1天)     → 验证 "不同相位需要不同 Kp"

Week 1 (Day 3-4): 分析结果，启动验证通过的 Stage 0.5
├── 根据 GS-002 结果决定 CA-ARP 的 β 范围
├── 根据 GS-007 结果推进 ZVF 门控测试
├── 根据 GS-006 结果决定 K(s) 的自适应方案
└── 根据 GS-001 结果决定 PAI 的优先级

Week 2: 实现验证通过的完整算法
Week 3-4: 核心消融实验 + 论文撰写
```

---

## 痛点-Idea 对应矩阵

| 痛点 | 001 | 002 | 003 | 004 | 005 | 006 | 007 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| P1: PD 力矩 pattern 受限 | ✅ **核心** | | | | | ✅ | |
| P2: 频率-动力学混淆 | ✅ | | | | | | ✅ |
| P3: 稀疏奖励探索失效 | | ✅ | ✅ **核心** | ✅ | | | ✅ **核心** |
| P4: Sim-to-Real 频域错位 | ✅ | | | | ✅ **核心** | ✅ **核心** | |
| P5: 高惯性状态不可归因 | | ✅ | ✅ | ✅ **核心** | | | |

---

## 正交性与组合矩阵

> [!tip] 最强组合
> **DOC + CA-ARP + ALA** = 双轴课程（去哪里探索）+ 时间相关噪声（如何探索）+ 平滑策略（稳定执行），三者完全正交且全部 P0 优先级。

| | 001 PAI | 002 CA-ARP | 003 CMR | 004 CSS | 005 TTCA | 006 ALA | 007 DOC |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **001 PAI** | — | ✅ 互补 | ✅ 正交 | ⚡ 部分 | ✅ 兼容 | ✅ 正交 | ✅ 兼容 |
| **002 CA-ARP** | | — | ✅ 互补 | ✅ 正交 | ✅ 兼容 | ✅ 兼容 | ✅ **正交叠加** |
| **003 CMR** | | | — | ⚡ 关联 | ✅ 正交 | ✅ 正交 | ✅ 正交 |
| **004 CSS** | | | | — | ✅ 正交 | ✅ 兼容 | ⚡ **互补替代** |
| **005 TTCA** | | | | | — | ✅ 增强 | ✅ 兼容 |
| **006 ALA** | | | | | | — | ✅ 兼容 |
| **007 DOC** | | | | | | | — |

*✅=可同时使用 | ⚡=有重叠但各有侧重 | —=自身*

---

## 理论基础覆盖

| Foundation | 001 | 002 | 003 | 004 | 005 | 006 | 007 |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| [[ControlTheory]] | ✅ | | | | | ✅ | |
| [[ReinforcementLearning]] | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| [[Dynamics]] | ✅ | | ✅ | | ✅ | | |
| [[ContactMechanics]] | ✅ | ✅ | ✅ | | ✅ | | |
| [[Optimization]] | | | | ✅ | | ✅ | ✅ |
| [[InformationTheory]] | | | ✅ | ✅ | | | |
| [[StochasticProcess]] | | ✅ | | | | | |
| [[SignalProcessing]] | | ✅ | | | ✅ | | |
| [[RepresentationLearning]] | | | ✅ | | ✅ | | |
| 覆盖数 | 4 | 4 | 5 | 3 | 5 | 3 | 3 |

---

## 新增文献关联（第二轮扫描发现）

本轮新发现的高价值文献与 Idea 的对应：

| 论文 | 最相关 Idea | 贡献 |
|------|-----------|------|
| [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control\|LipsNet]] | **Idea-006 (ALA)** | 自适应 Lipschitz 约束的直接理论来源 |
| [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]] | **Idea-007 (DOC)** | ZVF 门控机制 + 演示状态初始化 |
| [[Learning Human-like Finger Gaiting on an Anthropomorphic Hand\|Finger Gaiting]] | **Idea-007 (DOC)** | 路径点初始化有效性的直接证据 |
| [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration\|DemoSpeedup]] | Idea-007 (DOC) | 熵标定难度阶段 |
