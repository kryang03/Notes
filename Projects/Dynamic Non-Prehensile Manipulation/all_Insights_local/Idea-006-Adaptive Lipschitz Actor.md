---
tags:
  - insight
  - reinforcement-learning
  - control-theory
  - network-architecture
  - DNPM
aliases:
  - Adaptive Lipschitz Actor
  - ALA
  - 自适应Lipschitz策略网络
created: 2026-02-28
status: draft
feasibility: A
novelty: B+
target-venue: CoRL/ICRA
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[Optimization]]"
  - "[[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]]"
  - "[[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]]"
  - "[[On Robust Reinforcement Learning with Lipschitz-Bounded Policy Networks]]"
---

# Adaptive Lipschitz Actor: Phase-Aware Action Smoothness for Dynamic Dexterous Manipulation

> [!abstract] 核心贡献（一句话）
> 我们将自适应 Lipschitz 约束引入灵巧操作的策略网络——状态相关的 Lipschitz 常数 $K(s)$ 在稳定接触阶段施加强平滑性（低 $K$，消除动作抖动），在接触切换瞬间释放高响应性（高 $K$，允许急变）——从**网络架构层面**同时解决 PD 力矩模式受限（P1）和 Sim-to-Real 动作抖动（P4），与控制层面的 Idea-001 (PAI) 完全正交。

---

## 1. 问题定义与动机（Intro 故事线）

### 1.1 大背景引入

当前灵巧操作的 RL 策略通常使用标准 MLP 作为 Actor 网络。标准 MLP 对输入状态的微小变化可能产生剧烈的动作响应——即 Lipschitz 常数 $K = \sup_{s \neq s'} \frac{\|a(s) - a(s')\|}{\|s - s'\|}$ 无上界约束。在灵巧操作中，这导致了两个严重问题：

1. **训练中的力矩抖动**：策略在相邻时间步产生剧烈变化的动作，被 PD 控制器转化为高频力矩脉冲。这些脉冲在接触丰富的环境中放大不稳定性，是 reward hacking（高速旋转不停）的诱因之一。
2. **Sim-to-Real 的动作 gap**：仿真中可以容忍的高频动作变化在真机上由于通讯延迟、执行器饱和等因素被严重畸变，导致策略迁移后性能悬崖式下降。

### 1.2 现有方法的局限

**局限 1：动作平滑正则化是全局的。** 现有方法（如动作变化率惩罚 $\|a_t - a_{t-1}\|^2$）对所有状态施加相同的平滑约束。但在 Thumbaround 中，snap 阶段**需要**急剧的动作变化（食指弹射笔），而 spin 阶段**需要**超平滑的动作（维持脆弱接触）。全局正则化无法兼顾两者。

**局限 2：固定 PD 参数隐式限制了力矩模式。** 如 [[ControlTheory#3.1.1 从 PID 到计算力矩：精确线性化的诱惑与局限]] 所析，固定 $K_p$, $K_d$ 的 PD 控制器无法产生"先硬后软"的力矩序列。但 Idea-001 (PAI) 的解决路径是修改控制层——这需要大量工程改动并引入新的超参数搜索空间。

**局限 3：LipsNet ([[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control|LipsNet]]) 证明了自适应 Lipschitz 的价值，但仅在低维单体控制中验证。** LipsNet 的 Monotone Gradient Network (MGN) 在 CartPole 和机械臂任务上消除了动作抖动，但未在高维多指灵巧操作中应用，且其状态依赖的 $K(s)$ 机制未与接触模式对齐。

### 1.3 我们的洞见

> [!tip] Key Insight
> 动态操作中策略需要的**不是全局的平滑或全局的灵活——而是随运动相位变化的局部 Lipschitz 约束**：
> - **Spin 阶段**：笔在旋转，接触脆弱 → $K(s)$ 低 → 动作超平滑 → 任何抖动都可能打破接触
> - **Snap 阶段**：需要爆发性发力 → $K(s)$ 高 → 允许动作急变 → 释放力矩表达自由度
> - **Catch 阶段**：需要精确但不硬撞 → $K(s)$ 中等 → 既精确又不过冲
>
> 关键创新：这种 $K(s)$ 不需要人工设计——让网络自身学习何时平滑、何时锐利。
> MGN (Monotone Gradient Network) 的架构天然支持 $K$ 的梯度可微调节，与 PPO 端到端兼容。

### 1.4 贡献声明

1. 我们首次将**自适应 Lipschitz 约束**引入多指灵巧操作的策略网络，实现状态依赖的动作平滑度
2. 我们设计了**接触模式感知的 $K(s)$ 调节器**：从触觉观测自动推断当前运动相位所需的 Lipschitz 上界
3. 我们在 Thumbaround 上验证了 ALA 从**纯架构层面**改善了训练稳定性（减少 hacking）和 Sim-to-Real 鲁棒性（减少动作 gap），且与 Idea-001 (PAI) 可叠加使用

---

## 2. 方法论（Method）

### 2.1 问题形式化

设策略网络 $\pi_\theta: \mathcal{S} \to \mathcal{A}$ 为参数化映射。标准 MLP 的 Lipschitz 常数由权重矩阵的谱范数之积决定：

$$K(\pi_\theta) \leq \prod_{l=1}^{L} \|W_l\|_2$$

这是一个全局上界，无法随状态 $s$ 变化。

**ALA 的核心目标**：构造策略网络使得对于任意 $s, s' \in \mathcal{S}$：

$$\|\pi_\theta(s) - \pi_\theta(s')\| \leq K_\theta(s) \cdot \|s - s'\|$$

其中 $K_\theta(s)$ 是由网络自身学习的**局部 Lipschitz 常数**，在不同状态取不同值。

### 2.2 核心架构：MGN + K-Head

基于 LipsNet 的 Monotone Gradient Network (MGN) 架构，Actor 网络由两部分组成：

**Part 1: K-Head（Lipschitz 调节器）**

一个轻量级网络从状态中推断当前需要的 Lipschitz 常数：

$$K(s) = K_{min} + (K_{max} - K_{min}) \cdot \sigma(f_K(s))$$

其中 $f_K: \mathcal{S} \to \mathbb{R}$ 是一个小型 MLP（2层，64维），$\sigma$ 是 sigmoid。$K_{min} \approx 0.5$（超平滑），$K_{max} \approx 20$（高响应）。

**输入特征**（利用已有观测空间中的信息，零额外传感器）：
- 物体角速度 $\omega_{obj}$（来自 `priv_info_buf`）→ 高 $\omega$ 暗示 spin 阶段 → 低 $K$
- 触觉变化率 $\|\Delta c_t\|$（来自 `tactile_hist_buf`）→ 接触模式切换 → 高 $K$
- TWC 阶段标记（来自 `obs_buf`）→ pretension/snap/spin/catch → 不同 $K$

**Part 2: Constrained Actor（Lipschitz 受限的动作网络）**

核心：对 Actor MLP 的每一层权重矩阵进行**逐层谱归一化**（Spectral Normalization），将谱范数限制为 $K(s)^{1/L}$：

$$W_l^{SN} = \frac{K(s)^{1/L}}{\|W_l\|_2} \cdot W_l$$

这确保了：

$$K(\pi_\theta) \leq \prod_{l=1}^{L} K(s)^{1/L} = K(s)$$

### 2.3 训练目标

PPO 的 clipped objective 保持不变。额外添加一个**Lipschitz 正则化辅助损失**：

$$\mathcal{L}_{lip} = \lambda_{lip} \cdot \mathbb{E}_s\left[\max\left(0, K(s) - K_{target}(s)\right)\right]$$

其中 $K_{target}(s)$ 的定义：
- 如果状态处于稳定接触（$\|\Delta c_t\| < \epsilon$）：$K_{target} = K_{min}$
- 如果状态处于接触切换或自由运动：$K_{target} = K_{max}$

这不是硬约束，而是软引导——让网络知道"什么时候应该平滑"，但最终的 $K(s)$ 由端到端学习决定。

### 2.4 与 Idea-001 (PAI) 的正交性

| 维度 | Idea-001 (PAI) | Idea-006 (ALA) |
|------|---------------|----------------|
| 改变的层级 | **控制层**（PD → 阻抗参考模型） | **策略网络架构**（MLP → Lipschitz MLP） |
| 解决的问题 | 力矩 pattern 上限（P1） | 动作平滑度控制（P1+P4） |
| 代码改动量 | 大（新增 impedance_ref_model.py） | 小（修改 models.py 的 Actor 层） |
| 超参数 | $K_p$ 范围, $K_d$ 范围, $\Delta t$ 范围 | $K_{min}$, $K_{max}$, $\lambda_{lip}$ |
| 可组合性 | **可与 ALA 同时使用**：ALA 确保策略输出平滑，PAI 将平滑输出转化为更丰富的力矩 |

### 2.5 实现细节

**需修改的文件**：

| 文件 | 修改内容 |
|------|---------|
| `penspin/algo/models/models.py` | `TeacherActorCritic` 的 Actor 层：添加谱归一化 + K-Head 分支 |
| `penspin/algo/models/block.py` | `MLP` 类添加 `spectral_norm=True` 选项 + 动态缩放 |
| `penspin/algo/ppo/ppo_rl_teacher.py` | `calc_gradients()` 中添加 $\mathcal{L}_{lip}$ 辅助损失 |
| `configs/train/LinkerHandHora.yaml` | 新增 `train.ppo.lip_lambda`, `train.ppo.lip_k_min`, `train.ppo.lip_k_max` |

**代码改动量估计**：~200 行（对比 Idea-001 的 ~800 行），无需新增文件。

---

## 3. 实验计划（Experiment Plan）

### 3.0 Stage 0: Grid Search 快速验证（⚡ 优先执行）

> [!important] 算力充足策略
> ALA 的代码改动极小，可以在 **1 天内**完成 Stage 0 验证。先测试**全局固定 Lipschitz 约束**对训练的影响。

**最小实现**：在 `models.py` 的 Actor MLP 中对每层添加 `torch.nn.utils.spectral_norm()`，并乘以全局 $K$：

```python
# 在模型初始化时
for layer in self.actor_mlp:
    if hasattr(layer, 'weight'):
        torch.nn.utils.spectral_norm(layer)
```

| 实验 ID | 全局 $K$ | 动作特性 | 预期 |
|---------|---------|---------|------|
| GS-6.1 | $\infty$ (无约束, 当前) | Baseline | 基线 |
| GS-6.2 | 50 | 弱约束 | 略微减少抖动 |
| GS-6.3 | 10 | 中等约束 | 平衡点可能最优 |
| GS-6.4 | 5 | 强约束 | 显著平滑但可能限制 snap |
| GS-6.5 | 1 | 极强约束 | 过于平滑，snap 失败 |

**执行方式**：
```bash
# 5 个 K × 3 seeds = 15 runs
# 在 8×A100 上并行，约 6 小时完成
for k in inf 50 10 5 1; do
  for seed in 42 123 456; do
    python train.py train.ppo.lip_k_global=$k seed=$seed ...
  done
done
```

**判断标准**：
- 如果存在某个 $K \in [5, 50]$ 使成功率优于 $K=\infty$ → **强烈支持**自适应 $K(s)$ 的方向
- 如果 $K=10$ 比 $K=\infty$ 好但比 $K=50$ 差 → snap 需要高 $K$，spin 需要低 $K$ → **恰好**支持状态自适应
- 如果所有约束都不如无约束 → 可能 Isaac Gym 的 PD 控制器已经提供了隐式平滑，ALA 需要重新评估

**进阶 Grid Search**（Stage 0.5）：
- 如果全局 $K$ 有效，测试**分阶段 $K$**：
  - 前 50M steps（主要是 snap 探索）：$K=50$
  - 后 50M steps（收敛精调）：$K=10$

### 3.1 核心消融实验

| 实验 ID | 目的 | 自变量 | 因变量 | 对照组 | 预期结果 |
|---------|------|--------|--------|--------|----------|
| E1.1 | ALA vs 无约束 MLP | 网络架构 | 成功率、hacking 率 | 标准 MLP | ALA 减少 hacking 50%+ |
| E1.2 | ALA vs 全局 $K$ | 是否自适应 | 成功率 | 固定 $K$ 的 SN | ALA 在所有相位表现更好 |
| E1.3 | ALA vs 动作惩罚 | 平滑机制 | 成功率 | $\|a_t-a_{t-1}\|^2$ 惩罚 | ALA 不牺牲 snap 性能 |
| E1.4 | ALA + PAI vs PAI alone | 架构 + 控制联合 | 成功率 | PAI 单独 | 联合 > 单独 |

### 3.2 Sim-to-Real 相关验证

| 实验 ID | 目的 | 方法 |
|---------|------|------|
| E2.1 | 动作平滑度量化 | 对比 ALA vs Baseline 的动作功率谱密度（PSD），ALA 应在高频段显著衰减 |
| E2.2 | 仿真中模拟真机延迟 | 添加 1-3 步随机延迟，对比 ALA vs Baseline 的性能衰减 |
| E2.3 | 仿真中模拟执行器饱和 | 限制力矩变化率 $\|d\tau/dt\| < \tau_{slew}$，对比性能 |

### 3.3 涌现分析

| 实验 ID | 分析内容 |
|---------|---------|
| E3.1 | 可视化 $K(s)$ 在成功轨迹上的时间变化 → 是否与 snap/spin/catch 对齐 |
| E3.2 | 分析 K-Head 学到的特征权重 → 哪些观测维度对 $K$ 影响最大 |

### 3.4 计算资源估算

- Stage 0: 15 runs × 3h = ~6 小时（8×A100）
- 消融实验: 4 (E1) + 3 (E2) + 2 (E3) = 9 组 × 3 种子 = 27 次训练
- 预计总耗时: ~4 天 (8×A100)

### 3.5 关键指标

| 指标 | 计算方式 | 意义 |
|-----|---------|------|
| Success Rate | 现有 [METRICS] | 任务完成 |
| Hacking Ratio | reward > 阈值 but success < 10% | 动作抖动诱发的 hacking |
| Action PSD | 动作序列的功率谱密度 | 平滑度的频域量化 |
| $K(s)$ Phase Alignment | $K(s)$ 与 snap/spin/catch 标注的互信息 | 相位感知能力 |
| Delay Robustness | 成功率在 1-3 步延迟下的衰减率 | Sim-to-Real 潜力 |

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解策略 |
|-----|------|------|---------|
| 谱归一化增加计算开销 | 低 | 低 | Power iteration 仅需 1 步，开销 <3% |
| $K_{min}$ 过低导致 snap 动作被压制 | 中 | 高 | K-Head 允许 snap 阶段自动提高 $K$；Stage 0 Grid Search 确定安全范围 |
| K-Head 学习慢于主策略 | 中 | 中 | 预热：前 10M steps 固定 $K=K_{max}$，之后启用 K-Head |
| 与 PPO 的 clipping 机制交互 | 低 | 中 | 监控 importance ratio 分布，必要时增大 clip epsilon |

---

## 5. 与已有 Idea 的联合策略

### 5.1 ALA + PAI (Idea-001) 联合

```
输入 s → K-Head → K(s) → 谱归一化 Actor → (q_des, Kp, Kd, Δt) → 阻抗参考模型 → 力矩 τ
               ↓
         ALA 确保策略输出平滑（网络层面）
               ↓
         PAI 将平滑输出转化为丰富力矩（控制层面）
```

理论上，ALA 的平滑性保证让 PAI 的阻抗参数 $(K_p, K_d)$ 变化更渐进，避免阻抗参考模型的激励信号突变。

### 5.2 ALA + CA-ARP (Idea-002) 联合

ALA 约束的是**均值** $\mu_\theta(s)$ 的平滑性，CA-ARP 控制的是**噪声** $\epsilon_t$ 的时间相关性。两者作用在动作生成的不同成分上，完全兼容。

---

## 6. 动态迭代日志

> [!note] 🔄 实验结果追踪（与远端服务器同步）
> 本节用于记录实验结果和迭代决策。远端服务器 Agent 将实验结果写入 `_ExperimentResultsAll.md`，
> 本地 Agent 在每次会话中检查新增结果后更新本节。
>
> **结果来源**: `_ExperimentResultsAll.md` 中关联本 Idea 的 `[EXP-*]` 条目

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| 2026-02-28 | Exp2 TA/TP Heavy 失败分析 (前置) | ⚡ Heavy (6种 shaping) SR=0.00, 疑似 reward hacking | ALA 的动作平滑性约束可能缓解 reward hacking |
| *待填* | *Stage 0: 全局 K Grid Search* | *待运行* | *待定* |

### 迭代记录

**2026-02-28 Exp2 前置发现** (Reward Hacking 与动作平滑性):
- TA Heavy SR=0.00 (TWC 和 BASE 均失败) → 过多的 shaping reward 可能导致策略进入 reward hacking plateau
- 假设: reward hacking 的一个机制是策略通过**快速抨动**在多个 shaping reward 间切换, 拿到每个奖励的少量回报
- ALA 的动作平滑性约束可以**规制抨动行为**, 迫使策略学习更平滑的动作序列

**下一步服务器方向**:
- [ ] 新增 Stage 0 变体: 在 TA Heavy 配置下测试 ALA (全局 K 约束), 看能否将 SR 从 0 提升到有意义的值
- [ ] 对比: TA Heavy + ALA vs TA Heavy baseline (SR=0) → 如果能成功，是 ALA 价值的强力证据
- [ ] 同时在 TA Light 配置下测试 ALA，看能否在 SR=0.83 基线上进一步提升

---

## 7. 知识库关联

### 与 Foundations 的联系
- [[ControlTheory#3.2 解决方案 I：阻抗控制 (Impedance Control) —— 调节动态关系]] — Lipschitz 约束与阻抗的联系：低 $K(s)$ 等价于高柔顺性（低等效刚度）
- [[Optimization#2.6 非凸优化景观理论 (Nonconvex Optimization Landscapes)]] — Lipschitz 约束改善 loss landscape 的平滑性，有利于优化
- [[ReinforcementLearning#2.5 PPO]] — 谱归一化与 PPO 的 trust region 机制兼容性分析

### 与已有论文的联系
- [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] — **直接理论先驱**，本文将其从低维单体控制扩展到高维多指操作，并引入接触模式感知
- [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] — 结构感知的偏梯度界理论，为 K-Head 的逐指分解提供启发
- [[On Robust Reinforcement Learning with Lipschitz-Bounded Policy Networks]] — Lipschitz 约束提升 RL 鲁棒性的理论保证

### 与项目其他 Idea 的联系
- 与 Idea-001 (PAI) **正交互补**：ALA 从架构层面平滑动作，PAI 从控制层面丰富力矩——两者可叠加
- 与 Idea-002 (CA-ARP) **兼容**：ALA 约束均值平滑性，CA-ARP 约束噪声时间结构
- 与 Idea-005 (TTCA) **增强**：ALA 的平滑策略在真机上更能容忍参数不确定性
