---
tags:
  - paper
  - dexterous-manipulation
  - reinforcement-learning
  - knowledge-transfer
  - sim-to-real
aliases:
  - Dexterous RL with KT
  - RRC 2021
paper-year: 2023
read-date: 2026-02-02
venue: arXiv (RRC Competition)
paper-pdf: "[[Papers/Dexterous Robotic Manipulation using Deep Reinforcement.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Optimization]]"
---

# Dexterous Robotic Manipulation using Deep Reinforcement Learning and Knowledge Transfer

> [!abstract] 核心贡献
> 提出**知识迁移 (Knowledge Transfer)** 方法解决复杂灵巧操作任务：先在简化任务（仅位置控制）上学习策略，再通过 KT 迁移到完整任务（位置+姿态控制），赢得 Real Robot Challenge 2021 Phase 1。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] - HER 处理稀疏奖励
> - [[ReinforcementLearning]] - Sim-to-Real 迁移验证
> - [[Optimization]] - 从简单到复杂的优化策略
>
> **核心技术**: DDPG + HER, Knowledge Transfer, TriFinger Manipulation

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**先学会移动，再学会摆正**——通过知识迁移，将在简化任务（忽略姿态）上学到的操作技能迁移到完整任务（位置+姿态），显著提升学习效率。

### 直观隐喻
像学习写字：先学会控制笔画方向（位置），再练习字体美观（姿态）。将基础能力迁移到更复杂任务比从零学习更高效。

### 领域定位
- **竞赛冠军**: Real Robot Challenge 2021 Phase 1 第一名
- **实用验证**: 仿真训练→真机部署，优于传统控制方法
- **方法贡献**: 知识迁移框架可推广到其他 Actor-Critic 算法

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人方法 | 问题 | 本文解决方案 |
|---------|------|-------------|
| 直接学习完整任务 | 探索困难 | 先简化后迁移 |
| 复杂奖励工程 | 需要领域知识 | 稀疏+距离奖励 |
| 纯仿真验证 | 缺乏真机验证 | 竞赛真机部署 |

### 关键贡献点
1. **简洁奖励设计**: 稀疏目标奖励 + 距离奖励 + HER
2. **知识迁移框架**: 从位置控制任务迁移到位置+姿态任务
3. **竞赛验证**: 真机部署超越所有对手

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 任务分解

**原始任务**: 控制 TriFinger 使方块沿轨迹移动并保持特定姿态

**分解**:
- **源任务** (简单): 仅位置控制，忽略姿态
- **目标任务** (完整): 位置 + 姿态控制

### 3.2 知识迁移机制

```
┌─────────────────────────────────────────┐
│         源任务训练 (位置控制)             │
│  DDPG + HER → Actor_src, Critic_src     │
└─────────────────────────────────────────┘
                    │
          Knowledge Transfer
                    ↓
┌─────────────────────────────────────────┐
│         目标任务训练 (位置+姿态)          │
│  初始化: Actor_tgt ← Actor_src          │
│  扩展状态空间: s' = [s_pos, s_orient]   │
│  继续训练: DDPG + HER                   │
└─────────────────────────────────────────┘
```

**关键技术**:
- Actor 网络权重迁移（低层特征保留）
- 状态空间扩展（添加姿态观测）
- Critic 重新训练（价值函数变化）

### 3.3 奖励函数设计

$$
r = r_{\text{sparse}} + r_{\text{distance}}
$$

其中：
- $r_{\text{sparse}} = \begin{cases} 1 & \text{if goal reached} \\ 0 & \text{otherwise} \end{cases}$
- $r_{\text{distance}} = -\|p_{\text{cube}} - p_{\text{goal}}\|$

**HER 加持**: 将失败轨迹的末态作为虚拟目标重标注

### 3.4 Knowledge Transfer 的数学形式化

设源任务的状态空间 $\mathcal{S}_{\text{src}} \subseteq \mathbb{R}^{d_s}$（仅含位置观测），目标任务 $\mathcal{S}_{\text{tgt}} \subseteq \mathbb{R}^{d_s + d_o}$（追加姿态观测 $d_o$ 维）。

**Actor 迁移**：
$$
\theta^{(1)}_{\text{tgt}} = \theta^{(1)}_{\text{src}}, \quad W^{(1)}_{\text{tgt}} = [W^{(1)}_{\text{src}} \;|\; \mathbf{0}_{h \times d_o}]
$$

即第一层权重保留源任务参数，新增的姿态输入列初始化为零——保证迁移瞬间 Actor 输出与源策略一致（warm start），后续训练中新输入通道逐步获得梯度信号。

**Critic 重置**：价值函数因奖励结构改变而失效，Critic 从随机初始化重新训练。

**HER 目标重标注**：
$$
r'(s_t, a_t, g') = -\|p_{\text{achieved},t} - g'\|, \quad g' \sim \{s_{t+k}\}_{k=1}^{T-t}
$$

对每条失败轨迹，从后续到达状态中采样虚拟目标 $g'$，创造额外的正奖励信号，将稀疏奖励的学习转化为稠密反馈。

### 3.5 核心代码逻辑（PyTorch）

```python
# === Knowledge Transfer: Actor 权重迁移 ===
def transfer_actor(actor_src, actor_tgt, orient_dim):
    """将源任务 actor 权重迁移到目标任务 actor"""
    sd_src = actor_src.state_dict()
    sd_tgt = actor_tgt.state_dict()
    # 第一层: 扩展输入维度, 新列零初始化
    W1_src = sd_src['fc1.weight']           # (H, d_s)
    b1_src = sd_src['fc1.bias']             # (H,)
    pad = torch.zeros(W1_src.shape[0], orient_dim)  # (H, d_o)
    sd_tgt['fc1.weight'] = torch.cat([W1_src, pad], dim=1)
    sd_tgt['fc1.bias'] = b1_src.clone()
    # 后续层: 直接复制
    for key in ['fc2.weight', 'fc2.bias', 'fc3.weight', 'fc3.bias']:
        sd_tgt[key] = sd_src[key].clone()
    actor_tgt.load_state_dict(sd_tgt)
    return actor_tgt

# === HER 目标重标注 ===
def her_relabel(episode, k_future=4):
    """Hindsight Experience Replay: future strategy"""
    new_transitions = []
    for t, transition in enumerate(episode):
        future_indices = np.random.choice(
            range(t, len(episode)), size=min(k_future, len(episode)-t), replace=False
        )
        for idx in future_indices:
            new_goal = episode[idx]['achieved_goal']  # 用未来到达状态做虚拟目标
            new_reward = -np.linalg.norm(
                transition['achieved_goal'] - new_goal
            )
            new_transitions.append({**transition, 'goal': new_goal, 'reward': new_reward})
    return new_transitions
```

### 3.6 与传统方法对比

> [!note] 为什么 RL 优于传统控制？
> - TriFinger 是高度非线性的欠驱动系统
> - 传统 IK 在多接触场景下求解困难
> - RL 直接学习状态→动作映射，绕过建模

## 4. 实验与验证 (Experiments)

### 竞赛结果 (RRC 2021 Phase 1)
| 方法 | 位置误差 (m) | 排名 |
|-----|-------------|-----|
| 传统控制方法 | 0.05+ | 2-N |
| **本方法** | **0.02** | **1** |

### 知识迁移效果
| 配置 | 位置误差 | 姿态误差 |
|-----|---------|---------|
| 无 KT 直接学习 | 0.134m | 142° |
| **有 KT** | **0.02m** | **76°** |

### 训练设定
| 参数 | 值 |
|------|------|
| 算法 | DDPG + HER (future strategy, $k=4$) |
| Actor 网络 | MLP $[256, 256, 256]$, ReLU |
| Critic 网络 | MLP $[256, 256, 256]$, ReLU |
| 学习率 | $10^{-3}$ (Adam) |
| Replay Buffer | $10^6$ transitions |
| Batch Size | 256 |
| Discount $\gamma$ | 0.98 |
| 动作噪声 | Gaussian $\sigma=0.1$ |
| 源任务训练 | ~$5 \times 10^5$ steps |
| 目标任务微调 | ~$2 \times 10^5$ steps (有 KT) / $>10^6$ (无 KT) |
| 仿真器 | PyBullet (TriFinger 环境) |
| 动作频率 | 20 Hz |

### Sim-to-Real
- 仿真训练策略直接部署
- 无需 Domain Randomization（竞赛环境已标准化）
- 真机与仿真使用相同 TriFinger 硬件接口

### Ablation 因果链

| 去掉什么 | 导致什么 | 因为什么机制 |
|---------|---------|------------|
| 去掉 KT (从零训练完整任务) | 位置误差 0.134m → 0.02m，姿态 142° → 76° | 完整任务状态空间过大，纯探索无法在合理 step 内发现有效策略 |
| 去掉 HER | 收敛极慢或不收敛 | 稀疏奖励下 Actor 梯度近乎为零，无法更新；HER 人工构造正反馈 |
| 去掉 distance reward（仅用稀疏） | 即使有 HER 也收敛更慢 | 距离奖励提供连续梯度信号，引导探索方向 |
| Critic 也迁移（非重置） | 性能下降 | 源任务 Critic 对姿态维度的价值估计错误，warm-start 反而引入偏差 |

## 5. 工程关键细节 (Engineering Tricks)

1. **Critic 重置而非迁移**：源任务 Critic 学到的价值函数不含姿态信息，迁移后会系统性低估姿态误差的代价，导致策略忽略姿态控制
2. **零填充输入扩展**：新增姿态输入列零初始化，确保迁移瞬间网络输出不跳变，避免灾难性遗忘
3. **HER future strategy**：从轨迹后续状态采样虚拟目标（$k=4$），比 random strategy 收敛更快因为 future goals 离当前状态更近、更易学习
4. **动作 clipping**：动作空间归一化到 $[-1, 1]$，防止关节力矩超限损坏电机
5. **竞赛部署技巧**：推理时去除探索噪声（$\sigma=0$），使用 Actor 均值输出

## 6. 批判性分析 (Critical Analysis)

### 优势
- **简洁**: 奖励设计无需复杂工程
- **高效**: KT 大幅提升学习效率
- **实用**: 真机验证，竞赛冠军

### 局限性（三维度分析）

| 维度 | 局限 | 替代方案 |
|------|------|----------|
| **理论** | KT 无理论保证——何时迁移有效取决于源/目标任务的 MDP 相似性，缺乏 transfer gap bound | [[ReinforcementLearning]] 中 Bisimulation Metrics 可度量任务距离；PAC-Bayes Transfer 提供迁移误差上界 |
| **算法** | DDPG 本身有 Q 值高估问题 (overestimation bias)，在复杂接触场景下可能不稳定 | TD3（双 Critic + 延迟更新）或 SAC（熵正则化探索）是更鲁棒的选择 |
| **算法** | 姿态误差仍达 76°——HER 对 $\text{SO}(3)$ 空间的目标重标注不自然（欧拉角不连续） | 使用四元数距离 $d(q_1,q_2) = 1 - |\langle q_1, q_2 \rangle|$ 作为奖励 |
| **工程** | 针对 TriFinger 平台定制，任务分解方案不可直接迁移到其他硬件 | [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]] 框架提供自动化 curriculum，不依赖手工分解 |
| **工程** | 无 Domain Randomization，仅适用于标准化竞赛环境 | 真实部署需加入动力学参数/摩擦/延迟随机化 |

### 对转笔 (Pen-Spinning) / Sim-to-Real 的启发

> [!tip] 可迁移洞见
> 1. **KT 思路直接适用于转笔**：源任务 = 手指接触笔杆并推动旋转（忽略精确角度）；目标任务 = 精确到达目标旋转角度 + 稳定末态。这与本文"先位置后姿态"完全同构
> 2. **HER 对转笔的适配**：转笔的成功判据是旋转角度 $\theta_{\text{achieved}} \approx \theta_{\text{goal}}$，HER 可将"旋转了 90° 但目标是 360°"的失败经验重标注为"旋转 90° 的成功经验"
> 3. **Critic 重置警示**：转笔从慢速迁移到快速时，Critic 必须重置——因为快速旋转中离心力/惯性效应改变了状态价值地形
> 4. **Sim-to-Real gap 预警**：本文在标准化 TriFinger 上无需 DR，但转笔涉及笔-手指接触的摩擦系数高度敏感，必须加入 [[ContactMechanics]] 参数随机化

## 7. 与知识体系的联系 (Foundation Connections)

### 与 [[ReinforcementLearning]] 的联系

本文使用的 DDPG 是 Off-Policy Actor-Critic 演进线（[[ReinforcementLearning]]）的起点。其 Bellman 更新：

$$
y_t = r_t + \gamma Q_{\theta'}(s_{t+1}, \mu_{\phi'}(s_{t+1}))
$$

DDPG 的 Q 值高估问题在接触丰富场景下尤为严重——偶尔碰撞导致观测异常，$\max Q$ 更新逻辑放大误差。本文未使用 TD3/SAC 的修正，这也解释了姿态控制 76° 的较大残余误差。

HER 的本质是将目标条件 RL $\pi(a|s,g)$ 的稀疏奖励转化为稠密奖励，其信息论解释：HER 增大了经验回放中 $(s,a,r>0)$ 三元组的互信息 $I(S; A | R > 0)$，加速 Critic 收敛。

### 与 [[Optimization]] 的联系

知识迁移的核心是**优化地形的重用**：源任务的策略 $\pi_{\text{src}}$ 处于其 loss landscape 的一个局部最优——在目标任务中，如果扩展后的 loss landscape 与源任务在共享子空间上高度相似，则 warm start 跳过了前期的随机探索阶段。

数学上，设源任务目标 $J_{\text{src}}(\theta)$ 和目标任务目标 $J_{\text{tgt}}(\theta')$，KT 的条件是：

$$
\nabla_{\theta_{\text{shared}}} J_{\text{tgt}} \bigg|_{\theta=\theta^*_{\text{src}}} \approx \mathbf{0}
$$

即源最优参数在目标任务的共享参数子空间上梯度接近零——warm start 有效。当源/目标任务差异过大时此条件不满足，迁移甚至可能 negative transfer。

## 8. 跨方法对比 (Cross-Method Comparison)

| 维度 | 本文 (DDPG+HER+KT) | [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]] | [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch\|AnyRotate]] |
|------|-----------|-----------|------------|
| 核心算法 | DDPG + HER | PPO + Auto-Curriculum | PPO + 触觉 |
| Curriculum 方式 | 手工 KT（源→目标） | 自动从 demo 附近生成初始状态 | 重力方向随机化 |
| 稀疏奖励处理 | HER 目标重标注 | Demo-guided initial state distribution | Dense reward |
| 姿态控制 | 76° 误差（较差） | 精细 in-hand rotation | 任意轴旋转 |
| Sim-to-Real | 标准化环境直接部署 | Domain Randomization | DR + 触觉 |
| 可推广性 | 需手工设计源任务 | 只需少量 demo | 需触觉硬件 |
| 适用场景 | 有明确可分解子任务 | 通用灵巧操作 | 需要触觉反馈的旋转 |

> [!note] 启示
> 本文的 KT 可视为一种手工 curriculum：先简后难。[[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots|DemoStart]] 将此自动化，AnyRotate 则用传感器丰富化替代了 curriculum 设计。三者代表了「简化任务」「自动课程」「丰富感知」三种应对复杂灵巧操作的正交策略。

## 9. 演进脉络定位 (Evolution Context)

```
前置工作:
├── DDPG (2015) - 连续控制基础 Actor-Critic
├── HER (2017) - 稀疏奖励解决方案
├── TriFinger 平台 (2020) - 标准化灵巧手硬件
└── Curriculum Learning (Bengio 2009) - 由易到难训练范式

本论文: Dexterous RL + KT (RRC 2021)

后续发展:
├── DemoStart (2024) - 自动化 curriculum 取代手工 KT
├── AnyRotate (2024) - 触觉驱动的 in-hand rotation
├── DexNDM (2025) - 关节级神经动力学弥合 sim-real gap
└── 自适应 KT - 自动发现可迁移技能（开放问题）
```

---

**参考文献**:
- Wang, Q. et al. "Dexterous Robotic Manipulation using Deep Reinforcement Learning and Knowledge Transfer for Complex Sparse Reward-based Tasks." arXiv:2205.09683, 2023.
