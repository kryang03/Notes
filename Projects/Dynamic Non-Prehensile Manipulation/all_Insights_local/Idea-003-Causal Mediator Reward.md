---
tags:
  - insight
  - reinforcement-learning
  - causal-inference
  - reward-design
  - DNPM
aliases:
  - Causal Mediator Reward
  - CMR
  - 因果中介奖励
created: 2026-02-28
status: draft
feasibility: B+
novelty: A
target-venue: NeurIPS/ICML
related:
  - "[[ReinforcementLearning]]"
  - "[[InformationTheory]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[RepresentationLearning]]"
---

# Causal Mediator Reward: Dynamics-Informed Credit Assignment for Long-Horizon Contact-Rich Manipulation

> [!abstract] 核心贡献（一句话）
> 我们将因果推断中的中介分析 (Mediation Analysis) 引入长因果链的动态操作任务，通过识别动力学因果链中的物理中介变量（角速度、接触力、摩擦力）构建 surrogate reward，将 credit assignment 的有效因果窗口从整条链压缩到单步物理传递，在 Light Reward 下实现 HDC 独立无法达到的探索效果。

---

## 1. 问题定义与动机（Intro 故事线）

### 1.1 大背景引入

密集奖励塑形（dense reward shaping）是当前强化学习解决复杂操作任务的默认手段。然而，在动态非紧握操作中，这一策略面临根本性困境：**因果链太长，中间状态的即时评估本身不可靠**。

以 Thumbaround 为例，物理因果链为：
$$\boxed{\text{主动发力} \rightarrow \text{角速度} \rightarrow \text{离心力} \rightarrow \text{接触力} \rightarrow \text{摩擦力} \rightarrow \text{抗重力}}$$

如果在第2步奖励高角速度，策略学到的是 "永远旋转"（reward hacking）；如果只在最后一步给 sparse reward，策略无法归因到底是第1步还是第3步做错了（credit assignment 失败）。**这是一个在 dense 和 sparse 之间都没有好选择的结构性困境。**

### 1.2 现有方法的局限

**局限 1：Shaping Reward 的内在矛盾。** 传统 reward shaping（如奖励旋转速度、waypoint 跟踪）假设每个中间指标的提高都有利于最终成功。但在长因果链中，一个 "好" 的中间状态可能导致 "坏" 的最终结果——**高角速度既可能带来成功的旋转，也可能带来失控的飞出**。Shaping reward 无法区分这两种情况。

**局限 2：HER 的语义失配。** [[Hindsight Experience Replay|HER]] 通过目标重标注将失败转化为成功，但其有效性依赖于目标空间与状态空间的对齐。灵巧操作中，目标是物体的完整轨迹（位姿序列），简单地将 "实际到达的位姿" 重标注为 "目标" 产生大量低质量虚拟目标。

**局限 3：Mediator-Based Reward Design（已有理论但未在机器人学落地）。** 因果推断中的中介分析 (Mediation Analysis) 提供了原理性的框架来处理长因果链中的 credit assignment，但**现有工作仅在离散/低维 MDP 中验证，从未在接触丰富的连续控制任务中应用**。

### 1.3 我们的洞见

> [!tip] Key Insight
> DNPM 的动力学因果链**天然暴露了物理中介变量**（mediators）：角速度、接触力、摩擦力矩——这些不是抽象的隐变量，而是可以从仿真器中直接读取的物理量。
>
> 利用这些物理 mediators 构建 $\tilde{R}(m, s) = \mathbb{E}[R_{final} | M = m, S = s]$（"给定当前状态 $s$ 和中介变量值 $m$，最终成功的条件概率"），不仅能降低 credit assignment 方差（因为条件化后因果窗口缩短），而且能区分 "好的高角速度" 和 "坏的高角速度"——因为我们同时条件化了接触力（一个下游 mediator），而不仅仅是角速度本身。

### 1.4 贡献声明

1. 我们形式化了 DNPM 任务的**动力学因果图**，识别了物体角速度、接触力、摩擦力矩三个层级的物理中介变量
2. 我们提出 **Causal Mediator Reward (CMR)**：从成功/失败经验中学习 mediator-conditioned 的 value estimator $V_M(s, m)$，作为 surrogate reward 指导探索
3. 我们在 Thumbaround 的 Light Reward 设置下验证了 CMR 比 dense shaping 和 HER 都更有效，且与 HDC 形成互补（HDC 改善 landscape 结构，CMR 改善梯度信号质量）

---

## 2. 方法论（Method）

### 2.1 动力学因果图形式化

将 DNPM 的因果结构建模为有向无环图 (DAG)：

```
    A_t (动作)
    │
    ▼
    M1_t (物体角速度 ω)      ← 第一级 mediator
    │
    ▼
    M2_t (法向接触力 F_n)     ← 第二级 mediator
    │
    ▼
    M3_t (切向摩擦力 F_f)     ← 第三级 mediator
    │
    ▼
    Y_{t+k} (最终成功/失败)   ← 延迟结果
```

其中 $A_t \to M1_t$ 由 $\tau \to \omega$ 的动力学方程描述，$M1_t \to M2_t$ 由离心力 $F_n \propto m\omega^2 r$ 描述，$M2_t \to M3_t$ 由摩擦锥 $F_f \leq \mu F_n$ 描述。

### 2.2 Mediator-Conditioned Value Estimator

**训练阶段 1：收集有标注的 mediator 数据。**

在 HDC + 标准 reward 训练的过程中，记录所有轨迹上的 $(s_t, m_t = (\omega_t, F_{n,t}, F_{f,t}), y = \mathbb{1}[\text{success}])$ 三元组。这些物理量可从 Isaac Gym 的 `gym.get_actor_rigid_body_states()` 接口直接获取。

**训练阶段 2：学习 Mediator Value Network。**

训练一个辅助网络 $V_M: \mathcal{S} \times \mathcal{M} \to [0, 1]$：

$$V_M(s, m) = P(\text{success} | S = s, M = m)$$

使用二分类交叉熵损失：

$$\mathcal{L}_{CMR} = -\mathbb{E}_{(s, m, y)}[y \log V_M(s, m) + (1-y) \log(1 - V_M(s, m))]$$

**训练阶段 3：CMR 作为 surrogate reward。**

将 $V_M$ 的变化量作为 reward shaping：

$$r_{CMR}(s_t, a_t) = \gamma_{CMR} \cdot V_M(s_{t+1}, m_{t+1}) - V_M(s_t, m_t)$$

这满足 PBRS (Potential-Based Reward Shaping) 的条件，因此**不改变最优策略**（Andrew Ng & Stuart Russell, 1999）。

### 2.3 为什么 CMR 优于 Naive Shaping

| 对比维度 | Naive Shaping ($r \propto \omega$) | CMR ($r = \Delta V_M$) |
|---------|----------------------------------|----------------------|
| 区分好/坏高角速度 | ❌ 无法区分 | ✅ 通过条件化接触力区分 |
| 最优策略保持 | ❌ 可能引入偏差 | ✅ PBRS 保证 |
| 适应性 | ❌ 固定手工 reward | ✅ 从数据中学习，自动适应 |
| Reward Hacking | ⚠️ 高风险 | ✅ $V_M$ 编码了最终成功概率，不会被中间指标欺骗 |

### 2.4 CMR + HDC 的协同效应

- **HDC 的贡献**：拉伸 Value Landscape → 更多的成功轨迹进入 $V_M$ 训练集 → $V_M$ 估计更准确
- **CMR 的贡献**：提供高质量梯度信号 → 策略更高效地利用 HDC 创造的平滑 landscape
- **互补性**：HDC 解决 "landscape 太崎岖"，CMR 解决 "梯度太嘈杂"——两者攻击不同瓶颈

### 2.5 实现细节

**需修改的文件**：

| 文件 | 修改内容 |
|------|---------|
| `penspin/tasks/linker_hand_hora.py` | `compute_observations()` 中添加 mediator 提取：物体角速度 $\omega$、接触力 $F_n$、摩擦力 $F_f$ |
| `penspin/tasks/linker_hand_hora.py` | `compute_reward()` 中添加 $r_{CMR}$ 项 |
| `penspin/algo/ppo/ppo_rl_teacher.py` | 在 `train_epoch()` 后添加 $V_M$ 的训练步骤 |
| `configs/task/LinkerHandHora.yaml` | 新增 `task.env.reward.cmr_scale`, `task.env.reward.cmr_update_freq` |

**需新增的文件**：

| 文件 | 内容 |
|------|------|
| `penspin/algo/models/mediator_value.py` | $V_M$ 网络定义（MLP, 输入 = state + mediator, 输出 = success probability） |
| `penspin/utils/mediator_buffer.py` | 存储 $(s, m, y)$ 三元组的 replay buffer |
| `experiments/exp7_CMR/` | CMR 实验脚本 |

**Mediator 提取接口**（Isaac Gym）：

```python
# 物体角速度 (已存在于 priv_info_buf 的 obj_angvel 字段)
omega = self.object_angvel  # [N, 3]

# 接触力 (从 Isaac Gym 的接触传感器接口)
contact_forces = self.gym.acquire_net_contact_force_tensor(self.sim)
F_n = contact_forces[self.object_indices]  # [N, 3] 法向力

# 摩擦力 (需要从接触法向和切向分解，或直接用总力-法向力)
F_f = contact_forces_tangential  # 需要接触法向信息来分解
```

---

## 3. 实验计划（Experiment Plan）

### 3.0 Stage 0: Grid Search 快速验证（⚡ 优先执行）

> [!important] 算力充足策略
> 先用最简单的手工 mediator reward 验证 "物理中介变量有助于 credit assignment" 的核心假设，无需训练 $V_M$ 网络。

**最小实现**：在 `compute_reward()` 中添加基于 $\omega$ 和 $F_n$ 的简单 shaping reward：
```python
# Mediator-informed shaping (manual version of CMR)
r_mediator = w1 * (omega_norm > omega_threshold).float() * (F_n_norm > fn_threshold).float()
# 只有同时有高角速度和有效接触力才给奖励 —— 这是 CMR 的手工近似
```

| 实验 ID | Reward 配置 | 对照组 | 预期 |
|---------|------------|--------|------|
| GS-3.1 | Heavy Reward + mediator | Heavy Reward | Mediator 减少 hacking |
| GS-3.2 | Light Reward + mediator | Light Reward only | Mediator 开启探索 |
| GS-3.3 | Medium Reward + mediator | Medium Reward | Mediator 改善收敛 |

3 组 × 3 seeds = 9 runs，约 1.5 天 on 8×A100。

**判断标准**：
- 如果 mediator reward 在 Light Reward 下显著改善探索 → 值得实现完整 $V_M$ 学习版 CMR
- 如果 hacking 率下降 → 确认 "mediator 结合” 比 "单独 $\omega$ 奖励" 更好

---

### 3.1 核心消融实验

| 实验 ID | 目的 | 自变量 | 因变量 | 对照组 | 预期结果 |
|---------|------|--------|--------|--------|----------|
| E1.1 | CMR vs Naive Shaping | Reward 类型 | 成功率、hacking 率 | Dense rotation reward | CMR: 更高成功率，接近零 hacking |
| E1.2 | CMR vs HER | Credit assignment 方法 | Light Reward 下的成功率 | HER 重标注 | CMR 优于 HER（目标空间更自然） |
| E1.3 | CMR + HDC vs HDC alone | 是否使用 CMR | 最终成功率 | HDC + Heavy Reward | CMR 在 Light Reward 下达到 Heavy 的效果 |
| E1.4 | Mediator 选择消融 | 使用哪些 mediator | 成功率 | 只用 $\omega$ / 只用 $F_n$ / 全部 | 全部 > 单一 |

### 3.2 三层 Reward 灵敏度实验（直接回应 reviewer 质疑）

| 设置 | 方法 | 对照 |
|------|------|------|
| Heavy Reward | CMR | Dense Shaping, HER, Pure PPO |
| Medium Reward | CMR | Dense Shaping, HER, Pure PPO |
| **Light Reward** | CMR | Dense Shaping, HER, Pure PPO |

**预期关键结论**：CMR 在 Light Reward 下成功率 > Heavy Reward 下的 Naive Shaping。这一结论将直接证明 CMR 解决的是**credit assignment 的结构性问题**，而非简单的 reward 密度问题。

### 3.3 因果分析实验

| 实验 ID | 分析内容 |
|---------|---------|
| E3.1 | 可视化 $V_M(s, m)$ 的等值面 → 是否自然区分了 "安全" 和 "危险" 的高角速度 |
| E3.2 | 对比 CMR 训练的策略 vs Dense Shaping 训练的策略在 spin 阶段的行为差异 |
| E3.3 | 分析 $V_M$ 的 gradient $\nabla_m V_M$ → 哪个 mediator 对最终成功影响最大 |

### 3.4 计算资源估算

- 单次训练: ~4 GPU-hours (A100)（$V_M$ 训练增加 ~20% 开销）
- 消融实验总量: 4 (E1) + 12 (E2: 4方法×3设置) + 3 (E3) = 19 组 × 3 种子 = 57 次训练
- 预计总耗时: ~10 天 (8×A100)

### 3.5 关键指标

| 指标 | 计算方式 | 意义 |
|-----|---------|------|
| Success Rate | 现有 [METRICS] | 任务完成 |
| Hacking Ratio | reward > 阈值 but success < 10% 的 epoch / total epoch | reward hacking 频率 |
| CMR Accuracy | $V_M$ 在 held-out 数据上的 AUC | mediator value 估计质量 |
| Gradient Signal-to-Noise | $\|\mathbb{E}[\nabla_\theta J]\| / \text{Var}[\nabla_\theta J]$ | credit assignment 效率 |

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解策略 |
|-----|------|------|---------|
| $V_M$ 训练初期数据不足（成功经验太少） | 高 | 高 | 先用 HDC+Dense Reward 预训 $V_M$，再切换到 CMR+Light Reward |
| Mediator 之间存在多重共线性 | 中 | 低 | 使用 dropout + L2 正则化；消融实验验证每个 mediator 的边际贡献 |
| PBRS 条件在近似 $V_M$ 下不严格满足 | 中 | 中 | 用 CMR reward scale 控制影响；监控最优策略是否偏移 |
| Isaac Gym 的接触力提取精度 | 低 | 中 | 使用 `acquire_net_contact_force_tensor` 的刚体净力而非逐接触点力 |

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
| 2026-02-28 | Exp2 TA 奖励搜索 (前置) | ⚡ TA Heavy SR=0.00, Light BASE SR=0.83 > TWC SR=0.72 | 奖励工程极度敏感, CMR surrogate reward 需避免引入过多干扰项 |
| 2026-02-28 | Exp2 TP 奖励搜索 (前置) | TP Medium TWC SR=0.86 最优, Heavy SR=0 (BASE)/0.18 (TWC) | TP 的 mediator 变量 (角速度+waypoint) 在 Medium 奖励中已有很好效果 |
| *待填* | *Stage 0: 手工 mediator reward* | *待运行* | *待定* |

### 迭代记录

**2026-02-28 Exp2 前置发现** (奖励工程敏感度):
- TA Heavy (6种精细 shaping reward) SR=0.00 → 开奖励并非越多越好, 强烈支持 CMR 的核心假设: 需要基于因果链而非启发式奖励
- TA Light (exit_vel + milestone + terminal) SR=0.83 → 简洁但 **物理因果链对齐**的奖励效果最好
- TP Medium (rotate + waypoint) TWC SR=0.86 → waypoint 本身就是一种粗糙的 mediator variable
- **关键启示**: CMR 的 surrogate reward 应该少而精, 每个 mediator variable 都必须在因果链上有明确位置

**下一步服务器方向**:
- [ ] Stage 0 调整: 在 TA Light 基线 (SR=0.83) 上添加单一 mediator reward (角速度 ω), 验证是否能突破 0.83 天花板
- [ ] 对照实验: TA Light + 角速度奖励 vs TA Light + 角速度+接触力奖励 vs TA Light baseline
- [ ] 验证“少而精”假设: 单变量 mediator 是否优于多变量

---

## 7. 知识库关联

### 与 Foundations 的联系
- [[ReinforcementLearning#4.2 奖励工程：稀疏 vs. 密集 vs. 塑形 (Sparse vs. Dense vs. Shaping)]] — CMR 的理论定位：介于 dense 和 sparse 之间的原理性 reward design
- [[InformationTheory#6.1 Empowerment]] — Mediator 的信息论解读：$V_M$ 编码了 mediator 对最终结果的互信息
- [[Dynamics#2.2 Coriolis & Centrifugal Forces (科里奥利力与离心力)]] — 因果链第2步（角速度→离心力→接触力）的物理基础
- [[ContactMechanics#3. 接触建模演变：从点模型到软体模型]] — 因果链第3-4步（接触力→摩擦力）的物理基础

### 与已有论文的联系
- [[Hindsight Experience Replay]] — CMR 的核心 baseline（§3.2 三层 Reward 实验中的对照组）
- [[EUREKA: Human-Level Reward Design via Coding Large Language Models]] — EUREKA 可生成候选 mediator reward 的初始版本
- [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach]] — 探索-利用权衡的理论框架

### 与项目其他 Idea 的联系
- 与 Idea-001 (PAI) 正交：PAI 解决 "怎么控制"，CMR 解决 "怎么评估"——可同一篇论文的两个正交贡献
- 与 Idea-002 (CA-ARP) 互补：CA-ARP 改善探索策略（怎么采样），CMR 改善评估信号（怎么评价）——联合使用效果叠加
- 与 Idea-004 (Convex Safe Set) 关联：Convex Safe Set 可视为 $V_M$ 超过某阈值的 sublevel set 的几何近似
