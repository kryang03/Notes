---
tags:
  - insight
  - control-theory
  - impedance
  - DNPM
aliases:
  - Phase-Adaptive Impedance
  - PAI
  - 相位自适应阻抗
created: 2026-02-28
status: draft
feasibility: A
novelty: A
target-venue: RSS/CoRL
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[FACET - Force-Adaptive Control via Impedance Reference Tracking]]"
  - "[[TARC - Time-Adaptive Robotic Control]]"
  - "[[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]]"
---

# Phase-Adaptive Impedance Reference Tracking for Dynamic Non-Prehensile Dexterous Manipulation

> [!abstract] 核心贡献（一句话）
> 我们提出 Phase-Adaptive Impedance (PAI)，将阻抗参考模型跟踪与频率自适应统一，为灵巧手每根手指学习独立的时变阻抗曲线 $(K_p(t), K_d(t), \Delta t)$，在 Thumbaround 和 Triangle Pass 中实现自然的 snap→spin→catch 相位切换，同时消解 HDC 中频率-动力学缩放的混淆变量。

---

## 1. 问题定义与动机（Intro 故事线）

### 1.1 大背景引入

动态非紧握灵巧操作（Dynamic Non-Prehensile Manipulation, DNPM）要求机器人在不完全力闭合的条件下，利用惯性力完成高速物体操控。这类任务——如转笔（Thumbaround）、颠锅、陀螺旋转——需要策略在极短时间窗口内完成从"爆发性发力"到"柔顺滑动"再到"精确捕获"的相位转换。

当前几乎所有基于强化学习的灵巧操作工作都采用固定参数的 PD 位置控制器作为底层执行器：策略输出关节位置目标 $q_{target}$，底层以固定 $K_p$, $K_d$ 将位置误差转化为力矩。这一架构在准静态操作中表现良好，但在动态非紧握任务中暴露了根本性缺陷。

### 1.2 现有方法的局限

**局限 1：固定 PD 的力矩表达上限严重受限。** 在 Thumbaround 的训练后力矩图中（见 RSS26.pdf 第15页），关节实际位移极小，策略的 "位置控制" 实质上是在通过 PD 间接输出力矩。然而，固定 $K_p$, $K_d$ 无法表达 "先硬后软"、"振荡式" 等动力学任务所需的力矩模式——这正是 [[ControlTheory#3.1.1 从 PID 到计算力矩：精确线性化的诱惑与局限 (From PID to Computed Torque)]] 中指出的 PD 的本质缺陷。

**局限 2：频率-动力学缩放的混淆。** HDC 通过 $\alpha$ 缩放让物理世界变慢，但 reviewer 质疑其优势是否仅来自等效更高的控制频率。这一混淆的根源在于：在当前框架中，控制频率和动力学参数是耦合的——改变频率同时改变了 PD 控制器的响应特性。

**局限 3：现有变阻抗工作的适用范围有限。** VICES ([[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks|VICES]]) 仅验证了末端空间的变阻抗；FACET ([[FACET - Force-Adaptive Control via Impedance Reference Tracking|FACET]]) 验证了阻抗参考模型跟踪但仅在腿式机器人的低维关节空间；TARC ([[TARC - Time-Adaptive Robotic Control|TARC]]) 实现了频率自适应但未与阻抗控制结合。**三者的交叉——多指灵巧手上的时变阻抗 + 频率自适应——完全空白。**

### 1.3 我们的洞见

> [!tip] Key Insight
> 动态非紧握操作的不同运动相位对底层控制器的需求截然不同：
> - **Snap 相位**：需要高 $K_p$（刚性发力）、短 $\Delta t$（高频精确时序）
> - **Spin 相位**：需要低 $K_p$（柔顺滑动）、长 $\Delta t$（低频节省决策预算）
> - **Catch 相位**：需要中 $K_p$（精确但不硬撞）、短 $\Delta t$（高频闭环）
>
> 这些需求**不应由人工设计**——它们应该从任务本身的动力学结构中被策略自主学习。
> 而阻抗参考模型跟踪恰好提供了一个**物理上自洽、数学上可微、策略上可学习**的统一框架。

### 1.4 贡献声明

1. 我们提出 **Phase-Adaptive Impedance (PAI)**：首次将阻抗参考模型跟踪扩展到 21-DoF 多指灵巧手，为每根手指学习独立的时变阻抗参数 $(q_{des}^{(j)}, K_p^{(j)}, K_d^{(j)}, \Delta t^{(j)})$
2. 我们将 PAI 与 HDC 的 $\alpha$-curriculum 结合，**从根本上消解频率-动力学缩放的混淆变量**：控制频率由策略自适应决定（TARC 机制），与 $\alpha$ 缩放的动力学效应完全解耦
3. 我们在 Thumbaround 和 Triangle Pass 两个 DNPM 基准上验证了 PAI 相比固定 PD 和全局变阻抗的显著优势，并展示了策略自然涌现的相位切换阻抗曲线

---

## 2. 方法论（Method）

### 2.1 问题形式化

将灵巧操作建模为连续动作空间 MDP $\mathcal{M} = (\mathcal{S}, \mathcal{A}, P, R, \gamma)$。

**核心改变在于动作空间 $\mathcal{A}$ 的重新定义**：

| 框架 | 动作空间 $\mathcal{A}$ | 底层执行 |
|------|----------------------|---------|
| 传统固定 PD | $a = \Delta q \in \mathbb{R}^{21}$ | $\tau = K_p(q + a \cdot \text{AS} - q) - K_d \dot{q}$ |
| VICES 变阻抗 | $a = (x_{des}, K) \in \mathbb{R}^{27}$ | 末端空间阻抗控制 |
| **PAI（本文）** | $a = \{(q_{des}^{(j)}, K_p^{(j)}, K_d^{(j)}, \Delta t^{(j)})\}_{j=1}^{N_f} \in \mathbb{R}^{4 \times N_f}$ | 逐指阻抗参考模型跟踪 |

其中 $N_f$ 是手指分组数。对 LinkerHand (21 DoF)，自然分组为 5 组（每指 ≈ 4 DoF），$\dim(\mathcal{A}) = 4 \times 5 = 20$，与原始位控维度（21）几乎相同。

### 2.2 核心算法：逐指阻抗参考模型

对每个手指组 $j$，定义阻抗参考模型（参考 FACET 框架）：

$$M_{ref}^{(j)} \ddot{e}^{(j)} + K_d^{(j)} \dot{e}^{(j)} + K_p^{(j)} e^{(j)} = f_{ext}^{(j)}$$

其中 $e^{(j)} = q_{des}^{(j)} - q^{(j)}$ 是跟踪误差，$f_{ext}^{(j)}$ 是该指估计的外部接触力（可从 PD 力矩差反推），$M_{ref}^{(j)}$ 固定为中等惯性（简化搜索空间）。

**力矩输出**：

$$\tau^{(j)} = K_p^{(j)}(t) \cdot e^{(j)}(t) - K_d^{(j)}(t) \cdot \dot{q}^{(j)}(t) + \hat{f}_{ff}^{(j)}(t)$$

其中前馈项 $\hat{f}_{ff}^{(j)}$ 由参考模型的动态响应生成（这是 FACET 相比 VICES 的核心优势——参考模型能**主动响应外力**）。

**频率自适应（TARC 机制）**：

策略同时输出每个手指组的动作持续时间 $\Delta t^{(j)} \in [\Delta t_{min}, \Delta t_{max}]$。在 $\Delta t^{(j)}$ 期间，该手指组的阻抗参考模型持续运行（200Hz PD 底层不中断），但策略不更新该组的参数。

$$\text{控制循环:} \quad \forall j, \text{ if } t \mod \Delta t^{(j)} = 0: \text{ update } (q_{des}^{(j)}, K_p^{(j)}, K_d^{(j)}, \Delta t^{(j)}) \text{ from } \pi_\theta$$

### 2.3 PAI + HDC 的统一框架

HDC 的 $\alpha$ 缩放改变动力学参数（重力、速度），PAI 的频率自适应让策略自主选择控制频率。两者**正交解耦**：

- $\alpha$ 控制**物理难度**（环境参数）
- $\Delta t^{(j)}$ 控制**决策频率**（策略参数）

在 $\alpha < 1$ 的慢速空间中，策略自然倾向选择较大的 $\Delta t$（因为物理演化慢，不需要高频决策），随着 $\alpha \to 1$，策略被迫学习在关键时刻（接触切换）缩短 $\Delta t$。

**这从根本上消解了频率-动力学混淆：** 因为频率不再是外部超参数，而是策略自主决策的一部分。reviewer 无法再质疑 "优势来自高频率"，因为频率是被学习出来的。

### 2.4 实现细节

**需修改的文件**：

| 文件 | 修改内容 |
|------|---------|
| `penspin/tasks/linker_hand_hora.py` | `pre_physics_step()`: 将 action 解析为 $(q_{des}, K_p, K_d, \Delta t)$ 四元组；逐指应用阻抗参考模型计算力矩 |
| `penspin/algo/models/models.py` | `TeacherActorCritic`: Actor 输出维度从 21 改为 $4 \times N_f = 20$；添加 $K_p$, $K_d$ 的 sigmoid 输出归一化 |
| `penspin/utils/time_warping.py` | 添加 per-finger $\Delta t$ 追踪逻辑 |
| `configs/task/LinkerHandHora.yaml` | 新增 `task.env.controller.mode: "PAI"` 配置项；$K_p$ 范围 `[0.5, 50]`，$K_d$ 范围 `[0.01, 5]`，$\Delta t$ 范围 `[1, 20]`（以仿真步为单位） |

**需新增的文件**：

| 文件 | 内容 |
|------|------|
| `penspin/utils/impedance_ref_model.py` | 阻抗参考模型类：接收 $(q_{des}, K_p, K_d, f_{ext})$，在 200Hz 下积分参考轨迹，输出力矩 |
| `experiments/exp5_PAI/` | PAI 消融实验脚本（见 §3） |

---

## 3. 实验计划（Experiment Plan）

### 3.0 Stage 0: Grid Search 快速验证（⚡ 优先执行）

> [!important] 算力充足策略
> 8×A100 可随时使用。在实现完整 PAI 框架之前，先用**暴力 Grid Search 验证核心假设**："不同运动相位需要不同 $K_p$"。

**假设验证**：如果人工在不同 $\alpha$ 阶段设置不同固定 $K_p$，是否已经比全局固定 $K_p$ 更好？

| 实验 ID | $K_p$ | $K_d$ | 说明 | 预期 |
|---------|-------|-------|------|------|
| GS-1.1 | 2 | 0.1 | 极低刚度（纯柔顺）| Snap 失败，但 Spin/Catch 可能更稳 |
| GS-1.2 | 5 | 0.5 | 低刚度 | 适合 Spin 阶段 |
| GS-1.3 | 12 | 1.0 | 当前默认 | Baseline |
| GS-1.4 | 25 | 2.0 | 高刚度 | 适合 Snap 阶段 |
| GS-1.5 | 50 | 5.0 | 极高刚度（近似力控）| Snap 极强但可能接触不稳 |

**执行方式**：
```bash
# 5 个 Kp × 1 个 AS（当前默认） × 3 seeds = 15 runs
# 在 8×A100 上并行，约 6 小时完成
for kp in 2 5 12 25 50; do
  for seed in 42 123 456; do
    python train.py task.env.controller.pgain=$kp seed=$seed ...
  done
done
```

**判断标准**：
- 如果高 $K_p$ 在 snap 阶段成功率显著更高，低 $K_p$ 在 catch 阶段更稳 → **核心假设成立**，值得实现完整 PAI
- 如果所有 $K_p$ 表现差异不大 → 需重新审视 PAI 的动机

**进阶 Grid Search**（Stage 0.5，如果 Stage 0 假设成立）：
- 在 TWC 的不同 $\alpha$ 阶段使用不同 $K_p$（手动阶梯式切换）
- $\alpha < 0.5$: $K_p = 5$; $0.5 \leq \alpha < 0.8$: $K_p = 12$; $\alpha \geq 0.8$: $K_p = 25$
- 对比全程固定 $K_p = 12$ → 验证 "相位感知的刚度" 是否有收益

---

### 3.1 核心消融实验

| 实验 ID | 目的 | 自变量 | 因变量 | 对照组 | 预期结果 |
|---------|------|--------|--------|--------|----------|
| E1.1 | PAI vs 固定 PD | 控制器类型 | 成功率、收敛速度 | 固定 PD (当前方法) | PAI 成功率 +10-15%，收敛速度 +30% |
| E1.2 | PAI vs 全局变阻抗 | 阻抗调参粒度 | 成功率、力矩多样性 | VICES (全局 $K_p$) | PAI 在 catch 阶段成功率显著更高 |
| E1.3 | 逐指 vs 全局阻抗 | 参数共享方式 | 成功率 | 5指共享 $(K_p, K_d)$ | 逐指优于全局（每指角色不同） |
| E1.4 | 频率自适应 vs 固定频率 | $\Delta t$ 是否可学习 | 成功率、计算效率 | 固定 $\Delta t=10$ | 自适应在关键时刻高频，整体更高效 |
| E1.5 | PAI + HDC vs HDC alone | 是否使用 PAI | 在 $\alpha$=1 下的最终成功率 | 纯 HDC + 固定 PD | PAI + HDC 联合优于 HDC 单独 |

### 3.2 频率混淆消解实验（回应 reviewer）

| 实验 ID | 目的 | 设计 |
|---------|------|------|
| E2.1 | 证明 HDC+PAI 的优势不来自频率 | 在 PAI 框架下锁定 $\Delta t = \text{const}$，仅用 $\alpha$ 缩放 → 得到 HDC 的"纯物理效应" |
| E2.2 | 证明频率自适应独立有价值 | 在 $\alpha = 1$（无课程）下仅启用 $\Delta t$ 自适应 → 得到频率的"纯频率效应" |
| E2.3 | 交叉验证 | HDC + 固定 $\Delta t$ vs HDC + PAI → 量化两者交互效应 |

### 3.3 涌现分析实验

| 实验 ID | 目的 | 分析方法 |
|---------|------|---------|
| E3.1 | 可视化涌现的阻抗曲线 | 记录训练后策略在成功轨迹上的 $K_p^{(j)}(t)$ → 是否自然分为高/低/中三相位 |
| E3.2 | 分析频率分配 | 记录 $\Delta t^{(j)}(t)$ 的时间分布 → 是否在接触切换时缩短 |
| E3.3 | 力矩 pattern 对比 | 对比 PAI vs 固定 PD 的力矩 FFT 频谱 → PAI 是否释放了更丰富的频率成分 |

### 3.4 计算资源估算

- 单次训练: ~3-4 GPU-hours (A100)，因动作空间维度几乎不变
- 消融实验总量: 5 (E1) + 3 (E2) + 3 (E3) = 11 组 × 3 种子 = 33 次训练
- 预计总耗时: ~5 天 (8×A100 并行)

### 3.5 关键指标

| 指标 | 计算方式 | 意义 |
|-----|---------|------|
| Success Rate | 现有 [METRICS] 指标 | 任务完成能力 |
| Phase Impedance Variance | $\text{Var}_{t}[K_p^{(j)}(t)]$ 在成功轨迹上 | 策略是否学会相位切换 |
| Frequency Budget | $\sum_j \frac{1}{\Delta t^{(j)}}$ 的时间平均 | 计算效率 |
| Torque Spectral Entropy | 力矩 FFT 的信息熵 | 力矩表达多样性 |

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解策略 |
|-----|------|------|---------|
| $K_p$ 搜索空间过大导致训练不稳定 | 中 | 高 | 分阶段训练：先固定 $K_p$ 训练位控策略，再放开 $K_p$ 微调 |
| 逐指异步 $\Delta t$ 导致观测不对齐 | 低 | 中 | 使用零阶保持器在异步间填充最新观测 |
| 阻抗参考模型引入额外计算开销 | 低 | 低 | 参考模型积分器可并行化，开销 < 5% |
| 力矩表达自由度增加但探索更难 | 中 | 中 | 用当前固定 PD 训好的策略做 warm start |

---

---

## 6. 动态迭代日志

> [!note] 🔄 实验结果追踪（与远端服务器同步）
> 本节用于记录实验结果和迭代决策。远端服务器 Agent 将实验结果写入 `_ExperimentResultsAll.md`，
> 本地 Agent 在每次会话中检查新增结果后更新本节。
>
> **结果来源**: `_ExperimentResultsAll.md` 中关联本 Idea 的 `[EXP-*]` 条目

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| 2026-02-28 | 历史 TP Kp×AS 搜索 (前置) | ⚡ TP 最优 Kp=3.5~8.5, Kp>12 SR急降; 固定 Kd 不充分 | PAI 的 Kp 搜索应始于 Kp=2~15, 且 Kd 必须独立 |
| 2026-02-28 | Exp2 TP Reward (前置) | TP Medium TWC SR=0.86 (Kp=12, AS=0.8) | 当前固定 Kp=12 已能训练, PAI 需证明时变 Kp 可进一步提升 |
| *待填* | *Stage 0 Grid Search* | *待运行* | *待定* |

### 迭代记录

**2026-02-28 前置实验数据汇总**:
- 历史 TP Kp 扫描确认了“不同 Kp 值对训练效果影响极大”的假设基础: Kp=3.5 SR=0.23 vs Kp=16 SR~0
- 但历史数据 Kd 未作为独立维度, 且缺少“不同相位需不同 Kp”的直接证据
- Exp2 TP Medium TWC 在 Kp=12 获得 SR=0.86, 说明当前固定 Kp 已有不错的基线
- **Stage 0 重点调整**: 需要证明时变 Kp 可以在 SR=0.86 基线上进一步提升, 而非仅从 0 开始证明 Kp 重要性 (已有数据)

**下一步服务器方向**:
- [ ] 等待 Exp3a (Alpha 直接训练) 完成 → 提供 SR vs α 曲线，明确不同物理难度下的基线
- [ ] 启动 PAI Stage 0: 在 TP Medium TWC 基线上，对比固定 Kp=12 vs 手动设定的相位自适应 Kp (snap:Kp=20, spin:Kp=5, catch:Kp=15)
- [ ] Exp1 精细搜索: Kp×Kd×AS 三维网格，Kd 作为独立轴

---

## 7. 知识库关联

### 与 Foundations 的联系
- [[ControlTheory#3.2 解决方案 I：阻抗控制 (Impedance Control) —— 调节动态关系]] — PAI 的理论根基：阻抗控制将环境交互建模为弹簧-质量-阻尼系统
- [[ControlTheory#3.1.1 从 PID 到计算力矩：精确线性化的诱惑与局限 (From PID to Computed Torque)]] — 解释为什么固定 PD 在动态任务中力矩表达受限
- [[Dynamics#2.2 Coriolis & Centrifugal Forces (科里奥利力与离心力)]] — 高惯性状态中 $C(q, \dot{q})\dot{q}$ 项需要时变阻抗来适应
- [[ContactMechanics]] — 接触切换时刻的阻抗需求突变

### 与已有论文的联系
- [[FACET - Force-Adaptive Control via Impedance Reference Tracking]] — PAI 的直接理论先驱，本文将其从腿式机器人扩展到灵巧手
- [[TARC - Time-Adaptive Robotic Control]] — $\Delta t$ 自适应的思想来源，本文将其与阻抗结合
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] — VICES 是末端空间的变阻抗，PAI 是关节空间逐指的变阻抗

### 与项目其他 Idea 的联系
- 与 Idea-002 (Autoregressive Exploration) 互补：PAI 改善了动作空间的表达力，ARP 改善了探索策略——可联合使用
- 与 Idea-003 (Causal Mediator Reward) 正交：PAI 解决 "怎么控制"，Mediator Reward 解决 "怎么评估"——可同一篇论文
