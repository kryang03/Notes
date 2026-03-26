---
tags:
  - paper
  - reinforcement-learning
  - variable-time-step
  - embedded-systems
aliases:
  - VTS-RL
  - SEAC
  - MOSEAC
paper-year: 2024
read-date: 2026-01-31
venue: PhD Thesis
paper-pdf: "[[Papers/Elastic Time Step Reinforcement Learnin.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[Optimization]]"
---

# Elastic Time Step Reinforcement Learning (VTS-RL)

> [!abstract] 核心概要
> 提出弹性时间步长 RL 框架，Agent 同时学习“做什么动作”和“动作持续多久”，通过动态调整控制频率大幅降低计算能耗。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] - SAC/PPO 的扩展，Semi-MDP 框架
> - [[ControlTheory]] - 控制频率与系统响应
> - [[Optimization]] - Lyapunov 稳定性证明与多目标优化
>
> **核心技术**: Multi-Objective RL, Adaptive Reward Scaling, Lyapunov Convergence Proof

这份论文集实际上是一篇博士学位论文，整合了作者Dong Wang关于**弹性时间步长强化学习（Elastic Time Step Reinforcement Learning, VTS-RL）** 的四篇核心工作。这套方法论旨在解决传统强化学习在机器人控制中“固定控制频率”带来的计算浪费和性能瓶颈问题。

以下是对这份工作的深度剖析：

---

## 1. 核心直觉与宏观定位 (The Big Picture)

* **一句话核心**：本文提出了一种让AI不仅学习“做什么动作”，还同时学习“动作持续多久”的框架（VTS-RL），通过动态调整控制频率，在保证任务性能的同时，大幅降低计算能耗和推理延迟。
* **直观隐喻**：
* **传统RL（固定频率）**：就像一个强迫症司机，无论是在空旷的高速公路上还是在拥堵的停车场，都死板地每0.1秒踩一次油门或刹车。在高速上这浪费精力（计算资源），在停车场又可能反应太慢。
* **VTS-RL（本文方法）**：像一个老司机。路况简单时，踩一脚油门让车滑行很久（低频控制，省油省力）；路况复杂时，频繁微调方向盘（高频控制，保安全）。


* **领域定位**：
* 这是对 **Continuous Control Reinforcement Learning (连续控制RL)** 的重要扩展。
* 它挑战了经典的 **MDP（马尔可夫决策过程）** 中隐含的“离散且固定时间步长”的假设，向 **Semi-MDP** 或 **Continuous-Time RL** 迈进了一步，专门针对**资源受限的机器人嵌入式系统**（如火星车、无人机）。



---

## 2. 核心创新与贡献 (Contributions & Novelty)

* **Delta 分析 (vs. SOTA)**：
* **vs. 传统 RL (SAC/PPO)**：传统方法只输出动作 ，本文输出动作与持续时间元组 。
* **vs. FiGAR (Action Repetition)**：FiGAR 只是重复执行相同动作  次（逻辑上的跳步），计算图并未真正稀疏化；本文是物理时间上的延展，真正减少了神经网络的前向推理次数（Inference），直接降低 CPU/GPU 负载。
* **vs. CTCO (Continuous Options)**：CTCO 需要调节极其复杂的超参数（如径向基函数）；本文提出的 **MOSEAC** 通过自适应奖励权重，大幅简化了调参难度。


* **关键贡献点**：
1. **SEAC (Soft Elastic Actor-Critic)**：将 SAC 算法扩展，使其能同时输出动作和时间步长，并设计了包含“能量（步数）惩罚”和“时间惩罚”的多目标奖励函数。
2. **MOSEAC (Multi-Objective SEAC)**：针对 SEAC 调参难的问题，设计了自适应的奖励缩放机制（Adaptive ），根据训练曲线自动平衡任务奖励与节能奖励。
3. **理论保证**：基于 **Lyapunov 稳定性理论** 证明了 MOSEAC 在动态超参数下的收敛性。
4. **实机部署验证**：在 AgileX Limo 机器人上部署，证明相比 60Hz 的 SAC，MOSEAC 能节省约 **25%-70%** 的 CPU/GPU 计算资源。



---

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 数学建模：扩展的 MDP

传统的策略  被扩展为联合分布：



其中  是动作向量， 是该动作的持续时间。

### 3.2 核心奖励函数设计 (The Heart of VTS-RL)

为了兼顾任务完成度（Task）、时间效率（Time）和计算能耗（Energy/Steps），作者设计了如下标量化奖励函数：

* ** (Task Reward)**：环境给予的原始任务奖励（如到达终点 +100）。
* ** (Time-based Scaling)**：时间缩放因子。为了鼓励快速完成动作，定义为 。动作持续越久，单步奖励的“密度”可能越低（取决于具体设计，文中意在平衡长短步长）。
* ** (Energy Penalty)**：**这是关键**。这是一个常数惩罚（Step Penalty）。因为每一个 Step 意味着一次计算，扣除  会迫使 Agent 尽可能减少 Step 的总数量（即变相鼓励使用更长的  来覆盖路程，除非为了避障必须细微操作）。
* ** (Adaptive Weight)**：用于动态平衡上述两项的权重。

### 3.3 MOSEAC 的自适应机制与 Lyapunov 证明

为了解决  难以手动设定的问题，MOSEAC 根据平均奖励的趋势（斜率 ）动态调整它。

**调整逻辑**：



同时， 被截断在  之间。

**Lyapunov 稳定性证明**：
作者构造了一个 Lyapunov 候选函数  来证明参数调整过程是稳定的：



通过推导 ，证明在  达到  或系统收敛时，，从而保证了算法不会因为参数动态变化而发散。这是处理**非平稳奖励函数（Non-stationary Reward）** 的一种理论尝试。

### 3.4 难点攻克：物理惯性与马尔可夫性

**难点**：改变动作持续时间  会破坏物理环境的马尔可夫性。例如，施加 10N 力持续 0.1s 和持续 1.0s，下一时刻的速度完全不同。
**解法**：作者将**上一时刻的动作和持续时间**  显式地加入到当前状态  中。即：



这使得 Agent 能感知当前的“惯性”状态，恢复了马尔可夫性质。

---

## 4. 算法实现与逻辑 (Methodology & Implementation)

### 4.1 整体架构

数据流向如下：

1. **Input**: 状态向量（例如 Robot Position, Velocity）+ 历史动作信息。
2. **Network (Actor)**:
* 主干：多层全连接网络（MLP）或 CNN（针对图像输入）。
* **分支输出 1 (Action Head)**: `Tanh` 激活，输出动作 （如油门、转向）。
* **分支输出 2 (Duration Head)**: `Sigmoid` 或 `Relu6` 激活，映射到 。


3. **Environment Integration**:
* 接收 。
* 物理引擎执行：在  时间内，持续施加 。
* 返回：累积的  和 这一段时间内的 。



### 4.2 核心逻辑伪代码 (MOSEAC)

```python
# 初始化 Actor, Critic, alpha_m, alpha_epsilon
alpha_m = 1.0
alpha_epsilon = 0.1

while training:
    # 1. 采样与交互
    state = env.get_state()
    # 同时预测动作和持续时间
    action, duration = actor_network(state) 
    
    # 2. 与环境交互（执行时长为 duration）
    next_state, reward_raw, done = env.step(action, duration)
    
    # 3. 计算 MOSEAC 奖励
    # R_tau = D_min / duration
    reward = alpha_m * reward_raw * (D_min / duration) - alpha_epsilon
    
    replay_buffer.add(state, action, duration, reward, next_state)
    
    # 4. SAC 更新风格 (Critic & Actor)
    loss_Q = calc_critic_loss(batch)
    loss_pi = calc_actor_loss(batch) # 注意熵正则化也包含 duration 维度
    
    # 5. MOSEAC 自适应调整 (每隔 k_update 步)
    if time_to_update_params:
        slope = calculate_reward_trend(recent_rewards)
        if slope < 0: # 性能下降
            alpha_m = min(alpha_m + psi, alpha_max)
            # alpha_epsilon 随 alpha_m 增加而减少，保证平衡
            alpha_epsilon = update_epsilon(alpha_m)

```

### 4.3 核心 PyTorch 代码逻辑

```python
class MOSEACActor(nn.Module):
    """MOSEAC Actor: 同时输出动作和持续时间"""
    def __init__(self, obs_dim, act_dim, d_min, d_max):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Linear(obs_dim, 256), nn.ReLU(),
            nn.Linear(256, 256), nn.ReLU()
        )
        self.action_head = nn.Linear(256, act_dim)
        self.duration_head = nn.Linear(256, 1)
        self.d_min, self.d_max = d_min, d_max

    def forward(self, obs):
        h = self.backbone(obs)                           # (B, 256)
        action = torch.tanh(self.action_head(h))         # (B, act_dim)
        duration = self.d_min + (self.d_max - self.d_min) * torch.sigmoid(
            self.duration_head(h)
        )                                                # (B, 1)
        return action, duration


def moseac_reward(r_task, duration, d_min, alpha_m, alpha_eps):
    """R = alpha_m * r_task * (d_min / dt) - alpha_eps"""
    r_time = d_min / duration                            # 时间缩放因子
    return alpha_m * r_task * r_time - alpha_eps


def adaptive_update(alpha_m, alpha_eps, reward_history, psi, alpha_max):
    """自适应调整 alpha_m 和 alpha_eps"""
    slope = (reward_history[-1] - reward_history[-10]) / 10
    if slope < 0:
        alpha_m = min(alpha_m + psi, alpha_max)
    alpha_eps = 1.0 / (1.0 + torch.exp(torch.tensor(alpha_m)))
    return alpha_m, alpha_eps
```

### 4.4 关键 Trick

* **Duration Mapping**: 神经网络输出通常是无界的或归一化的，必须将其线性映射到物理时间 。例如 Trackmania 中是 。
* **Sigmoid Linkage**:  不是独立调整的，而是通过 Sigmoid 函数与  绑定反向变化，防止两个参数“打架”。

---

## 5. 实验与局限性分析 (Experiments & Discussion)

### 5.1 核心结论

1. **能效提升**：在 Trackmania 游戏和 Limo 机器人上，MOSEAC 相比固定频率的 SAC，**步数（Steps）减少了约 3-4 倍**。这意味着在真实部署中，CPU 唤醒次数大幅减少。
2. **资源占用**：
* CPU 使用率：SAC (60Hz) 31.4% -> MOSEAC 11.4%。
* GPU 使用率：SAC (60Hz) 27.8% -> MOSEAC 2.8%。
* **结论**：这是极其惊人的优化，直接让低端嵌入式芯片跑复杂 RL 成为可能。


3. **学习曲线**：虽然引入了时间维度增加了探索空间，但 MOSEAC 的收敛速度（Wall-clock time）并没有显著慢于 SAC，甚至因为跳过了无效步长，在某些任务上更快。

### 5.2 Ablation 因果链分析

| 去掉组件 | 结果变化 | 因果机制 |
|---------|---------|--------|
| 去掉 alpha_eps (能量惩罚) | 步数不降，计算无节省 | Agent 无动机选择长步长 |
| 去掉自适应 alpha_m | 性能波动大，训练不稳定 | 任务/节能目标失衡 |
| 去掉 duration head | 退化为标准 SAC | 无时间步自适应能力 |
| 去掉历史注入 (a_{t-1}, dt_{t-1}) | 性能 -30%+ | 马尔可夫性被破坏 |
| dt clip 范围扩大 | 安全性下降，偶发碰撞 | 过长 open-loop 区间 |

### 5.3 局限性深度分析

**理论层面**：
- 奖励标量化假设多目标可线性组合，忽略了帕累托前沿的非凸性
- Lyapunov 证明依赖于 alpha_m 有界假设，但未给出最优 alpha_max 的选取准则
- **替代方案**：约束优化（CMDP）可避免权重调参；Hamilton-Jacobi RL 可处理连续时间

**算法层面**：
- 自适应 psi 本身仍是超参数（“套娃”问题）
- 稀疏奖励下探索空间扩大（A × [d_min, d_max]），加剧探索难度
- **替代方案**：将 duration 作为 option 的终止条件（Option-Critic），或用课程学习逐步开放 duration 范围

**工程层面**：
- 变长步内 Agent 是“盲”的（Open-loop），过长 dt 在动态环境中致命
- 物理引擎需改造以支持变步长 step，标准 Gym 接口不兼容
- **替代方案**：在 open-loop 期间加入安全检查中断（guardian policy），或限制 dt 上界为安全响应时间

---

## 6. 知识图谱与延伸思考 (Knowledge Graph & Future)

### 6.1 前置知识

* **Soft Actor-Critic (SAC)**: 必须熟练掌握 SAC 的最大熵原理，因为 SEAC/MOSEAC 是建立在 SAC 之上的。
* **Lyapunov Stability**: 用于理解为什么动态改变超参数不会导致训练崩塌。
* **Reactive Programming**: 理解“按需响应”的编程思想。

### 6.2 相关文献推荐

1. **[CTCO] "Dynamic decision frequency with continuous options" (Karimi et al., IROS 2023)**:
* *关系*：这是本文最大的竞争对手（Baseline），思路相似但实现不同（CTCO 基于 Option 框架），对比阅读能理解不同流派的优劣。


2. **[FiGAR] "Learning to Repeat: Fine Grained Action Repetition for Deep Reinforcement Learning" (Sharma et al., 2017)**:
* *关系*：早期的类似思想，但仅限于重复动作。本文是 FiGAR 在连续物理时间上的进化版。


3. **"Soft Actor-Critic Algorithms and Applications" (Haarnoja et al., 2018)**:
* *关系*：基石论文，复现本文前必须手撸一遍 SAC。



### 6.3 复现建议 (Pitfalls)

* **物理引擎的坑**：在 Gym 或 MuJoCo 中复现时，**千万注意 `env.step()` 的实现**。标准的 step 通常是固定的 `dt`。你需要修改底层环境 wrapper，使其支持传入 `duration`，并在内部循环执行物理积分直到达到该 duration。
* **时间归一化**：输入到网络的“上一帧持续时间”必须归一化（例如除以 ），否则网络权重极易由于数值范围差异而不稳定。
* ** 的截断**：如果不加  限制，自适应机制可能会让  无限增长，导致 Reward Explosion，梯度爆炸。务必加上 Clip。

---

## 6. 与知识体系的联系（含数学关联）

### 与 [[ReinforcementLearning]] 的联系

VTS-RL 将标准 MDP 扩展为 Semi-MDP。标准 Bellman 方程：
$$Q^\pi(s, a) = r(s,a) + \gamma \sum_{s'} P(s'|s,a) V^\pi(s')$$
在 Semi-MDP 中变为（持续时间 $\tau$）：
$$Q^\pi(s, a, \tau) = \int_0^\tau \gamma^t r(s_t, a) dt + \gamma^\tau V^\pi(s_\tau)$$
折扣因子 $\gamma^\tau$ 随持续时间指数衰减——长步长等价于更强的 myopic bias。

### 与 [[ControlTheory]] 的联系

变频控制对应自适应采样率控制。Shannon 采样定理要求：
$$f_s \geq 2 f_{\max}$$
VTS-RL 在低动力学复杂度段自动降低 $f_s$（增大 $\tau$），在高频动态段提高 $f_s$，实现自适应 Nyquist 约束。

### 与 [[Optimization]] 的联系

多目标奖励本质是加权和标量化：
$$\min_{\pi} \; -J_{task}(\pi) + \lambda \cdot J_{energy}(\pi)$$
Lyapunov 候选函数 $L(\alpha_m) = (\alpha_m - \alpha_m^*)^2$ 的 $\dot{L} \leq 0$ 保证自适应权重不发散，这是 Lyapunov 方法在非平稳优化中的应用。

## 7. 跨方法对比

| 维度 | VTS-RL/MOSEAC | [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning\|PFQI]] | [[Reinforcement Learning for Control with Multiple Frequencies\|AP-AC]] | FiGAR |
|-----|--------------|------|------|-------|
| 时间步 | 连续可变 | 离散固定 k | 多变量各自固定 | 离散重复 n |
| 学习频率 | ✅ 端到端 | ✖ 网格搜索 | ✖ 预设 | ✖ 学习重复数 |
| 理论保证 | Lyapunov 收敛 | Bellman 收缩 | 最优性证明 | 无 |
| 计算节省 | ✅ 真实推理减少 | ✅ 值函数层面 | 部分 | ✖ 仅逻辑跳步 |
| 多动作变量 | ✖ | ✖ | ✅ | ✖ |
| 适用场景 | 嵌入式部署 | Batch/离线 | 异构执行器 | Atari 等 |

---

这篇论文的核心价值不在于算法的微创新，而在于它切实地解决了 **Robot Learning** 中“算力受限”这一痛点，具有很高的工程参考价值。

## 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **变时间步对转笔的意义**: 转笔中接触/非接触阶段的动力学复杂度差异巨大——snap 发力瞬间需要高频控制，空中自由飞行阶段可降低频率。VTS-RL 的自适应时间步可自动学习这种分配
2. **计算效率**: Isaac Gym 并行仿真中，变时间步可在不牺牲策略质量的前提下显著减少训练墙钟时间
3. **工程注意**: 时间步的 Clip 上限对于灵巧手尤为重要，否则可能导致跳过关键接触事件