---
tags:
  - paper
  - reinforcement-learning
  - variable-time-step
  - control-frequency
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

> [!abstract] 核心贡献
> 针对"传统 RL 隐含固定控制频率 → 简单路况浪费算力、复杂路况反应不足"这一瓶颈，提出**弹性时间步长 RL**：让策略同时输出"做什么动作 $a$"和"该动作持续多久 $\tau$"，把控制频率变成可学的决策维度。核心是 SEAC/MOSEAC——在 SAC 上加 duration head + 含"步数(能量)惩罚"的多目标奖励，并用 **Lyapunov 稳定性**证明自适应权重下的收敛。结构性洞见：**控制频率不该是固定超参，而应随状态动力学复杂度自适应——在真机上这直接转化为 25%–70% 的算力节省（真实推理次数减少，而非逻辑跳步）。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — SAC 最大熵框架的扩展；把 MDP 推广到 **Semi-MDP**（动作带持续时间 $\tau$，折扣变 $\gamma^\tau$）
> - [[ControlTheory#3. 技术演进：从刚性位置控制到柔顺力控制|ControlTheory §3]] — 变频控制 = 自适应采样率；低复杂度段降频、高动态段升频以满足 Nyquist 约束
> - [[Optimization]] — 多目标奖励的加权和标量化 + Lyapunov 候选函数 $L(\alpha_m)=(\alpha_m-\alpha_m^*)^2$ 证明非平稳权重不发散
>
> **核心技术**: SEAC (Soft Elastic Actor-Critic), MOSEAC (Multi-Objective, 自适应奖励缩放), Lyapunov 收敛证明, Semi-MDP

> 这是作者 Dong Wang 关于弹性时间步长 RL 的博士论文（整合四篇工作），旨在解决机器人控制中"固定控制频率"带来的算力浪费与性能瓶颈。

## 1. 问题设定与动机 ← 逻辑与价值

### 1.1 一句话核心
让 AI 不仅学"做什么动作"，还同时学"动作持续多久"，通过动态调整控制频率，在保任务性能的同时大幅降算力与推理延迟。

### 1.2 直观隐喻
- **传统 RL（固定频率）**：强迫症司机，无论空旷高速还是拥堵车场，都死板地每 0.1s 踩一次油门——高速浪费算力、车场反应过慢。
- **VTS-RL**：老司机。路况简单时一脚油门滑行很久（低频，省算力）；路况复杂时频繁微调（高频，保安全）。

### 1.3 领域定位与现有方法局限
对连续控制 RL 的扩展，挑战经典 MDP "离散且固定时间步"的隐含假设，向 Semi-MDP / 连续时间 RL 迈进，专攻**资源受限嵌入式机器人**（火星车、无人机）。

| 方法 | 注入的假设 | 关键局限 |
|------|-----------|----------|
| 传统 RL (SAC/PPO) | 固定 $\Delta t$ | 只输出 $a$，频率人工设定、全程不变 |
| FiGAR (action repetition) | 重复动作 $n$ 次 | 仅**逻辑**跳步，计算图未稀疏化，前向推理次数不减 |
| CTCO (continuous options) | option 终止函数 | 超参极复杂（径向基等），调参难 |
| **本文 VTS-RL** | $\tau$ 作为可学输出 | — |

### 1.4 Delta 分析
- **vs SAC/PPO**：传统只输出动作 $a$；本文输出元组 $(a,\tau)$。
- **vs FiGAR**：FiGAR 重复同一动作 $n$ 次（逻辑跳步），计算图未稀疏；本文是**物理时间延展**，真正减少神经网络前向推理次数 → 直接降 CPU/GPU 负载。
- **vs CTCO**：CTCO 调参复杂；MOSEAC 用自适应奖励权重 $\alpha_m$ 大幅简化调参。

## 2. 核心方法与理论 ← 原理与理论

### 2.1 变量来源追踪

VTS-RL 的全部精妙在 $\tau$（actor 输出的连续持续时间）与状态增广 $\tilde s_t$（恢复马尔可夫性）这两处。

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $s_t$ | $\mathbb{R}^{d_s}$ | 观测 | 否（输入） | 原始状态（位置/速度等） | 单独不足以恢复马尔可夫性 |
| $a_t$ | $\mathbb{R}^{d_a}$ | actor 输出（tanh） | 是（策略） | 动作向量 | — |
| $\tau_t$ | $[\tau_{min},\tau_{max}]$ | actor 输出（sigmoid 映射） | 是（策略） | **动作持续时间** | 连续量，非 PFQI 的离散 $k$ |
| $\tilde{s}_t$ | $[s_t,a_{t-1},\tau_{t-1}]$ | **构造**（状态增广） | 否 | 含"惯性"的增广状态 | 不增广则 $\tau$ 破坏马尔可夫性 |
| $R_{task}$ | scalar | 环境 | 否 | 原始任务奖励 | — |
| $R_\tau=D_{min}/\tau$ | scalar | 计算 | 否 | 时间缩放因子 | $\tau$ 越大单步奖励密度越低 |
| $\alpha_\epsilon$ | scalar | 超参/自适应 | 否 | **每步常数能量惩罚** | 驱动减少 Step 总数的关键项 |
| $\alpha_m$ | scalar | **自适应**（按 reward 斜率） | 否（非梯度） | 任务/节能平衡权重 | 非平稳；需 Lyapunov 保证不发散 |
| $\psi$ | scalar | 超参 | 否 | $\alpha_m$ 调整步长 | "套娃"超参（§5） |
| $\gamma^\tau$ | scalar | 推导 | 否 | Semi-MDP 折扣 | 随 $\tau$ 指数衰减 → 长步长 myopic |

### 2.2 数学建模：扩展的 MDP / Semi-MDP

传统策略 $\pi(a\mid s)$ 被扩展为动作与持续时间的联合分布：
$$\pi(a,\tau\mid s),\qquad a\in\mathcal{A},\ \tau\in[\tau_{min},\tau_{max}].$$
其中 $a$ 是动作向量，$\tau$ 是该动作的持续时间。这使问题从离散固定步 MDP 变为 Semi-MDP（见 §6 的 Bellman 推广）。

### 2.3 核心奖励函数设计 (The Heart of VTS-RL)

为兼顾任务完成度、时间效率与计算能耗，设计标量化多目标奖励：
$$R = \alpha_m\cdot R_{task}\cdot R_\tau - \alpha_\epsilon.$$

- **$R_{task}$ (Task Reward)**：环境原始任务奖励（如到达终点 +100）。
- **$R_\tau = D_{min}/\tau$ (Time-based Scaling)**：时间缩放因子。动作持续 $\tau$ 越久，单步奖励密度越低，以平衡长短步长。
- **$\alpha_\epsilon$ (Energy Penalty)**：**关键**。每个 Step 意味着一次推理计算，扣常数 $\alpha_\epsilon$ 迫使 Agent 减少 Step 总数（变相鼓励更长 $\tau$ 覆盖路程，除非避障需细微操作）。
- **$\alpha_m$ (Adaptive Weight)**：动态平衡任务奖励与节能项。

### 2.4 MOSEAC 的自适应机制与 Lyapunov 证明

为解决 $\alpha_m$ 难手动设定的问题，MOSEAC 按平均奖励趋势（斜率 $\nabla\bar{R}$）动态调整：当 $\nabla\bar{R}<0$（性能下降）时
$$\alpha_m \leftarrow \min(\alpha_m+\psi,\ \alpha_{max}),$$
同时 $\alpha_\epsilon$ 通过 sigmoid 与 $\alpha_m$ 反向绑定（$\alpha_\epsilon=1/(1+e^{\alpha_m})$），防止两参数"打架"。

**Lyapunov 稳定性证明**：构造候选函数
$$L(\alpha_m)=(\alpha_m-\alpha_m^*)^2,$$
推导 $\dot{L}=2(\alpha_m-\alpha_m^*)\dot{\alpha}_m\le 0$，证明在 $\alpha_m$ 达 $\alpha_{max}$ 或系统收敛时 $\dot L\le0$，从而算法不因参数动态变化而发散——这是处理**非平稳奖励**的理论尝试。

### 2.5 难点攻克：物理惯性与马尔可夫性

**难点**：改变 $\tau$ 会破坏马尔可夫性——施加 10N 力持续 0.1s 与 1.0s，下一时刻速度完全不同，但裸状态 $s_t$ 无法区分。
**解法**：将上一时刻动作与持续时间显式加入状态：
$$\tilde{s}_t = [\,s_t,\ a_{t-1},\ \tau_{t-1}\,].$$
使 Agent 感知"惯性"状态，恢复马尔可夫性质（§5 消融显示去掉它性能 −30%+）。

### 2.6 概念边界与符号陷阱

- **$\tau$ 是连续可学输出**（actor 的 duration head），区别于 [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning|PFQI]] 的离散全局固定 $k$——这是本簇"状态依赖 vs 全局固定"分野的核心（§7）。
- **状态必须增广** $(a_{t-1},\tau_{t-1})$，否则变长步破坏马尔可夫性。
- **$\alpha_m$ 是非梯度更新**，按 reward 斜率调整 → 奖励非平稳 → 需 Lyapunov 保证收敛。
- **open-loop 盲区**：变长步内 Agent 不重新决策，过长 $\tau$ 在动态环境致命 → $\tau_{max}$ 是安全关键（§5 消融）。
- **"真实推理减少" vs FiGAR "逻辑跳步"**：本文减少的是神经网络前向次数（省真实算力），FiGAR 只是重复动作、推理次数不变。

## 3. 算法实现与逻辑 ← 实验与验证（机制）

### 3.1 整体架构
1. **Input**：增广状态 $\tilde s_t$（状态 + 历史 $a_{t-1},\tau_{t-1}$）。
2. **Actor**：MLP/CNN 主干 → 两个分支：Action Head（`tanh` 输出 $a$）、Duration Head（`sigmoid` 映射到 $[\tau_{min},\tau_{max}]$）。
3. **Environment**：接收 $(a,\tau)$，物理引擎在 $\tau$ 时间内持续施加 $a$，返回累积 $R_{task}$ 与该段末状态。

### 3.2 核心逻辑（principle-level，含 shape）

```python
class MOSEACActor(nn.Module):
    """同时输出动作和持续时间"""
    def __init__(self, obs_dim, act_dim, d_min, d_max):
        super().__init__()
        self.backbone = nn.Sequential(nn.Linear(obs_dim, 256), nn.ReLU(),
                                       nn.Linear(256, 256), nn.ReLU())
        self.action_head = nn.Linear(256, act_dim)
        self.duration_head = nn.Linear(256, 1)
        self.d_min, self.d_max = d_min, d_max

    def forward(self, obs):                              # obs = 增广状态 (B, obs_dim)
        h = self.backbone(obs)
        action = torch.tanh(self.action_head(h))         # (B, act_dim)
        duration = self.d_min + (self.d_max - self.d_min) * torch.sigmoid(
            self.duration_head(h))                        # (B, 1) ∈ [d_min, d_max]
        return action, duration

def moseac_reward(r_task, dt, d_min, alpha_m, alpha_eps):
    return alpha_m * r_task * (d_min / dt) - alpha_eps   # R = α_m·R_task·(D_min/τ) − α_ε

def adaptive_update(alpha_m, reward_history, psi, alpha_max):
    slope = (reward_history[-1] - reward_history[-10]) / 10
    if slope < 0:                                        # 性能下降 → 提任务权重
        alpha_m = min(alpha_m + psi, alpha_max)
    alpha_eps = 1.0 / (1.0 + torch.exp(torch.tensor(alpha_m)))  # 与 α_m 反向绑定
    return alpha_m, alpha_eps
```

### 3.3 关键 Trick
- **Duration Mapping**：网络输出须线性映射到物理时间（如 Trackmania 的 $[\tau_{min},\tau_{max}]$）。
- **Sigmoid Linkage**：$\alpha_\epsilon$ 经 sigmoid 与 $\alpha_m$ 绑定反向变化，防止两参数互相抵消。

## 4. 实验与验证 ← 实验与验证

### 4.1 核心结论与资源占用

| 指标 | SAC (60Hz 固定) | MOSEAC (变频) | 含义 |
|------|-----------------|---------------|------|
| 步数 (Steps) | 基线 | **减少 ~3–4 倍** | CPU 唤醒次数大幅下降 |
| CPU 使用率 | 31.4% | **11.4%** | 嵌入式可行 |
| GPU 使用率 | 27.8% | **2.8%** | 近 10× 降低 |
| 总算力节省 | — | **25%–70%** | AgileX Limo 实机验证 |

> [!important] 数字如何印证故事
> GPU 27.8%→2.8% 的近 10× 降低直接来自"真实推理次数减少"——这是 §1.4 中"vs FiGAR 不是逻辑跳步而是物理延展"论断的硬证据：若像 FiGAR 那样只重复动作，前向次数不变、GPU 占用不会降。学习曲线（wall-clock）未显著慢于 SAC，说明扩展的时间维度探索代价被"跳过无效步"补偿。

### 4.2 Ablation 因果链

| 去掉/改变 A | 结果 B | 因果机制 C | 启示 D |
|---------|---------|----------|--------|
| 去 $\alpha_\epsilon$（能量惩罚） | 步数不降，无节省 | Agent 无动机选长步长 | 节能必须显式入奖励 |
| 去自适应 $\alpha_m$ | 性能波动大、训练不稳 | 任务/节能目标失衡 | 自适应权重是稳定性关键 |
| 去 duration head | 退化为标准 SAC | 无时间步自适应能力 | $\tau$ 输出是方法本体 |
| 去历史注入 $(a_{t-1},\tau_{t-1})$ | 性能 −30%+ | 马尔可夫性被破坏（§2.5） | 状态增广不可省 |
| $\tau$ clip 范围扩大 | 安全性下降、偶发碰撞 | 过长 open-loop 盲区 | $\tau_{max}$ = 安全响应时间上界 |

## 5. 替代方案与理论局限 ← 未来与结合

| 维度 | 局限 | 替代方案 |
|------|------|----------|
| **理论** | 奖励标量化假设多目标可线性组合，忽略帕累托前沿非凸；Lyapunov 证明依赖 $\alpha_m$ 有界但未给 $\alpha_{max}$ 选取准则 | 约束优化 (CMDP) 避免权重调参；Hamilton-Jacobi RL 处理连续时间 |
| **算法** | 自适应 $\psi$ 本身仍是超参（"套娃"）；稀疏奖励下 $\mathcal{A}\times[\tau_{min},\tau_{max}]$ 探索空间扩大 | duration 作为 option 终止条件 (Option-Critic)；课程学习逐步开放 $\tau$ 范围 |
| **工程** | 变长步内 Agent "盲"（open-loop），动态环境中过长 $\tau$ 致命；标准 Gym 接口不支持变步长 | open-loop 期加安全中断 (guardian policy)；限 $\tau$ 上界为安全响应时间 |

## 6. 与知识体系的联系 ← 未来与结合

### 与 [[ReinforcementLearning]] 的联系
VTS-RL 把标准 MDP 扩展为 Semi-MDP。标准 Bellman：
$$Q^\pi(s,a)=r(s,a)+\gamma\sum_{s'}P(s'\mid s,a)V^\pi(s').$$
Semi-MDP 中（持续时间 $\tau$）变为：
$$Q^\pi(s,a,\tau)=\int_0^\tau\gamma^t r(s_t,a)\,dt+\gamma^\tau V^\pi(s_\tau).$$
折扣 $\gamma^\tau$ 随持续时间指数衰减——长步长等价更强的 myopic bias（这与 PFQI 的 $\gamma^k$ 视野缩短同源）。

### 与 [[ControlTheory]] 的联系
变频控制对应自适应采样率。Shannon 采样定理要求 $f_s\ge 2f_{\max}$；VTS-RL 在低动力学复杂度段自动降 $f_s$（增大 $\tau$）、高频动态段升 $f_s$，实现**自适应 Nyquist 约束**——与 PFQI 把 persistence 解释为 ZOH 离散化是同一控制论根。

### 与 [[Optimization]] 的联系
多目标奖励是加权和标量化 $\min_\pi\,-J_{task}(\pi)+\lambda J_{energy}(\pi)$；Lyapunov 候选 $L(\alpha_m)=(\alpha_m-\alpha_m^*)^2$ 的 $\dot L\le0$ 保证自适应权重不发散，是 Lyapunov 方法在非平稳优化中的应用。

## 7. 跨方法对比与簇定位 ← 未来与结合

| 维度 | VTS-RL/MOSEAC | [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning\|PFQI]] | [[Reinforcement Learning for Control with Multiple Frequencies\|AP-AC]] | FiGAR |
|-----|--------------|------|------|-------|
| 时间步 | 连续可变 $\tau$ | 离散固定 $k$ | 多变量各自固定 | 离散重复 $n$ |
| 学习频率 | ✅ 端到端 | ✖ 网格搜索离线选 | ✖ 预设 | ✖ 学重复数 |
| 理论保证 | Lyapunov 收敛 | Bellman 收缩 + 损失界 | 最优性证明 | 无 |
| 计算节省 | ✅ 真实推理减少 | ✅ 值函数层面 | 部分 | ✖ 仅逻辑跳步 |
| 状态依赖 | ✅ $\tau(s)$ | ✖ 全局 $k$ | 部分 | ✖ |
| 适用场景 | 嵌入式部署 | Batch/离线 | 异构执行器 | Atari 等 |

> [!note] 在 control frequency 簇中的定位（与 [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning#6.4 领域级综述：control frequency / time-step 簇（本篇为理论锚点）|PFQI §6.4 簇综述]] 互参）
> VTS-RL 是该簇"**状态依赖频率**"一极的代表：它把 PFQI 的全局固定 $k$ 放松为 actor 端到端学出的 $\tau(s)$，换来真机算力大降。但代价正是簇综述指出的张力——**它丢了 PFQI 那种 Bellman 收缩的强保证**，只有 Lyapunov 这种对"参数不发散"的较弱保证（不保证收敛到最优频率）。于是 VTS-RL 与 PFQI 恰好标定了簇的两端：PFQI = 有界但僵、VTS-RL = 灵活但弱保证。**簇空白（状态依赖 + 强保证）= 二者的合取**，也是 WMTS 调度粒度可贡献理论之处。

## 8. 对用户研究的启发（灵巧手转笔 / Sim-to-Real）

1. **变时间步对转笔的意义**：转笔中接触/非接触阶段动力学复杂度差异巨大——snap 发力瞬间需高频，空中飞行段可降频。VTS-RL 的 $\tau(s)$ 能自动学出这种分配（对应 PFQI §9 的状态依赖 $k^*(s)$，但这里是端到端学的连续版）。
2. **计算效率**：Isaac Gym 并行仿真中，变时间步可在不牺牲策略质量下显著减训练墙钟时间。
3. **工程注意**：$\tau$ 的 clip 上界对灵巧手尤为关键——否则可能跳过关键接触事件（与 §2.6 open-loop 盲区一致）。

## References
- [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning]] — 离散全局 persistence 的理论锚点（见其 §6.4 簇综述）
- [[Reinforcement Learning for Control with Multiple Frequencies]] — 多频率/异构执行器控制
- SAC (Haarnoja et al. 2018) — 基石；CTCO (Karimi et al. IROS 2023) / FiGAR (Sharma et al. 2017) — 主要对比对象
