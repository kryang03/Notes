---
tags:
  - paper
  - reinforcement-learning
  - control-frequency
  - multi-rate-control
  - factored-action
aliases:
  - AP-AC
  - Action-Persistent Actor-Critic
  - Multiple Control Frequencies
paper-year: 2020
read-date: 2026-01-31
paper-pdf: "[[Papers/Reinforcement Learning for Control with Multiple Frequencies.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
---

# Reinforcement Learning for Control with Multiple Frequencies

> [!abstract] 核心概要
> 提出 **AP-AC (Action-Persistent Actor-Critic)** 算法，解决多控制频率问题。不同动作变量有不同持续时间（如机械臂 50Hz + 抓手 10Hz），通过**周期性非平稳策略**直接优化，避免任意平稳策略的次优性。NeurIPS 2020。

> [!tip] 与理论基础的关联
> - [[ControlTheory]] - 多速率采样理论
> - [[ReinforcementLearning]] - 动作持续与 options 框架
> - [[Dynamics]] - 快慢子系统分解
>
> **核心技术**: Factored-Action MDP, Action Persistence, Periodic Non-stationary Policy

---

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**不同动作需要不同控制频率 → 周期性非平稳策略 > 单一平稳策略**

### 直观隐喻
想象你在开手动档汽车：
- **方向盘**：需要高频调整（10Hz）
- **档位**：低频切换（0.1Hz）
- **油门**：中频控制（2Hz）

如果强制所有操作同频率：
- 太快：换档过于频繁（损耗）
- 太慢：转向反应迟钝（危险）

**AP-AC 的方案**：每个动作变量保持自己的"最佳节奏"。

### 领域定位
```
Multi-rate Control Theory
        ↓
Standard RL (single rate)
        ↓
Temporal Abstraction (Options, HRL)
        ↓
Action Persistence (single persistence)
        ↓
████████████████████████████████████████
█  AP-AC (2020)                        █
█  • 多动作变量、多持续时间             █
█  • 周期性非平稳策略                   █
█  • 理论收敛保证                       █
████████████████████████████████████████
        ↓
未来: 自适应控制频率学习
```

---

## 2. 核心创新与贡献 (Contributions & Novelty)

### 问题定义

**Factored-Action MDP**：
$$M = \langle S, A, P, R, \gamma \rangle$$

其中 $A = A^1 \times A^2 \times \cdots \times A^m$ 是分解的动作空间。

**动作持续**：
$$c = (c^1, c^2, \ldots, c^m)$$

$c^k$ 表示第 $k$ 个动作变量的持续时间（以基础时间步为单位）。

**示例**：
- 机械臂关节：$c^{arm} = 1$（50Hz）
- 抓手：$c^{gripper} = 5$（10Hz）

### 核心问题

**定理（非正式）**：由平稳策略诱导的 c-持续策略可能**任意次优**。

**直觉**：当 $c^1 \neq c^2$ 时，最优决策在 $t=0$ 和 $t=c^1$ 时应该不同，因为 $a^2$ 的状态不同。

### Delta 分析

| 方法 | 多持续时间 | 策略类型 | 最优性保证 |
|-----|----------|---------|----------|
| 标准 RL | ❌ | 平稳 | ✅ (同频) |
| 单持续时间 RL | 单一 | 平稳 | ✅ (单持) |
| **AP-AC** | **✅** | **周期非平稳** | **✅** |

### 关键贡献

1. **C1**: 形式化多动作持续时间问题，证明平稳策略的次优性
2. **C2**: 提出 AP-PI 算法，理论保证收敛到最优
3. **C3**: 提出 AP-AC，神经网络实现的可扩展算法

---

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 c-持续策略

**定义**：

给定策略 $\pi = (\pi_t)_{t \geq 0}$，c-持续策略 $\bar{\pi}_c$ 定义为：

$$\bar{\pi}_{c,t}(a | h_t) = \prod_{k=1}^{m} \bar{\pi}_{c,t}^k(a^k | h_t)$$

其中：
$$\bar{\pi}_{c,t}^k(a^k | h_t) = 
\begin{cases}
\pi_t^k(a^k | h_t) & \text{if } t \mod c^k = 0 \\
\delta_{a^k_{t-(t \mod c^k)}}(a^k) & \text{otherwise}
\end{cases}$$

**直觉**：每 $c^k$ 步才重新决定 $a^k$，其余时间保持上次决定。

### 3.2 平稳策略的次优性

**反例构造**：

```
状态: s0 → s1 → s2 → s3 (terminal)
动作: a = (a1, a2), 每个 ∈ {0, 1}
持续: c = (2, 3)

最优轨迹:
t=0: a=(1,1), s0 → s1
t=1: a=(1,1), s1 → s2  (a1 可变, a2 持续)
t=2: a=(0,1), s2 → s3  (a1 可变, a2 持续)
     到达终点, 奖励 100

问题:
- t=0 时需要 a1=1 (去 s1)
- t=2 时需要 a1=0 (去 s3)
- 平稳策略在 s2 只能选一个 a1 → 无法同时满足
```

### 3.3 周期性非平稳策略

**关键洞察**：最优 c-持续策略是**周期性**的。

周期 $T = \text{lcm}(c^1, c^2, \ldots, c^m)$

**策略参数化**：

$$\pi_t^k(a^k | s) = \pi^k_{\phi(t,k)}(a^k | s)$$

其中 $\phi(t, k) = t \mod c^k$ 索引周期内的"相位"。

### 3.4 Action-Persistent Policy Iteration (AP-PI)

**算法**：

1. **策略评估**：计算 $Q^{\bar{\pi}_c}(s, a)$
2. **策略改进**：对每个相位 $\phi$ 和动作变量 $k$：
   $$\pi^k_\phi(s) \leftarrow \arg\max_{a^k} \mathbb{E}[Q^{\bar{\pi}_c}(s, a)]$$

**时间复杂度**：$O(|S|^2 |A| T)$，仅比标准 PI 多 $|A|$ 因子。

### 3.5 Action-Persistent Actor-Critic (AP-AC)

**网络架构**：

```
┌─────────────────────────────────────────┐
│  AP-AC Network Architecture             │
├─────────────────────────────────────────┤
│                                         │
│  State s                                │
│     │                                   │
│     ▼                                   │
│  ┌─────────────┐                        │
│  │ Shared      │                        │
│  │ Backbone    │                        │
│  └──────┬──────┘                        │
│         │                               │
│    ┌────┴────┐                          │
│    │         │                          │
│    ▼         ▼                          │
│  ┌─────┐  ┌─────┐                       │
│  │ π^1 │  │ π^2 │  ... (per action var) │
│  │     │  │     │                       │
│  │ φ=0 │  │ φ=0 │                       │
│  │ φ=1 │  │ φ=1 │                       │
│  │ ... │  │ ... │  (per phase)          │
│  └─────┘  └─────┘                       │
│                                         │
└─────────────────────────────────────────┘
```

**实现细节**：
- 每个动作变量 $k$ 有 $c^k$ 个策略头
- 根据当前相位 $\phi(t, k)$ 选择对应头
- Critic 是标准的 Q 网络

---

## 4. 实验与验证 (Experiments)

### 4.1 实验设置

**任务**：

1. **修改的 MuJoCo 任务**
   - HalfCheetah: 躯干 + 腿部控制分离
   - Ant: 不同腿不同频率
   
2. **交通控制仿真 (SUMO)**
   - 多路口信号灯
   - 不同路口不同切换频率

**基线**：
- 标准 SAC（忽略多频率）
- 快速重复（高频动作重复）
- 最低频率（所有动作用最低频率）

### 4.2 主要结果

| 任务 | SAC | Fast-Repeat | Low-Freq | **AP-AC** |
|-----|-----|-------------|----------|----------|
| HalfCheetah-MF | 5200 | 4800 | 3900 | **6100** |
| Ant-MF | 3800 | 3500 | 2900 | **4600** |
| Traffic | 78% | 72% | 65% | **85%** |

### 4.3 关键发现

1. **多频率任务上显著优势**：AP-AC 比所有基线高 15-25%
2. **策略确实是非平稳的**：可视化显示不同相位策略不同
3. **收敛稳定**：尽管策略空间更大，训练依然稳定
4. **频率差异越大效果越明显**

---

## 5. 批判性分析 (Critical Analysis)

### 优势
- **理论完备**：证明了最优性和收敛性
- **通用框架**：适用于任意分解的动作空间
- **实用性强**：时间复杂度增长温和
- **无需手动设计**：自动学习每个相位的策略

### 局限性
- **频率需预先指定**：$c$ 向量需要人工设定
- **周期固定**：不能动态调整控制频率
- **策略空间增大**：$T$ 大时参数量显著增加
- **离散时间**：未处理连续时间情况

### 与其他方法的对比

| 方法 | 多频率 | 时间抽象层级 | 频率学习 |
|-----|-------|------------|---------|
| Options | 间接 | 高 | ❌ |
| FiGAR | 单一 | 中 | ❌ |
| **AP-AC** | **直接** | **低** | **❌** |
| Elastic Time Step RL | 单一 | 低 | ✅ |

---

## 6. 对灵巧操作的启发 (Implications)

### 机器人系统中的多频率

```
典型灵巧操作系统：

1. 视觉感知: 30 Hz
   - 物体追踪、姿态估计

2. 高层规划: 10 Hz
   - 任务切换、策略选择

3. 手臂控制: 100 Hz
   - 末端轨迹跟踪

4. 手指控制: 500 Hz
   - 精细力控制

5. 触觉反馈: 1000 Hz
   - 滑动检测、接触力

AP-AC 可以统一处理这些不同频率！
```

### 与其他论文的联系

- **VICES**：阻抗增益可以低频更新，位置高频更新
- **DexNDM**：关节级动力学可有不同更新频率
- **Elastic Time Step RL**：学习单一动作的持续时间，AP-AC 处理多动作

---

## 7. 演进脉络定位 (Evolution Context)

```
Multi-rate Control (Classical)
        ↓
Temporal Abstraction in RL
├── Options Framework (Sutton, 1999)
├── HAM (Parr & Russell, 1998)
└── MAXQ (Dietterich, 2000)
        ↓
Action Persistence / Repetition
├── FiGAR (2017): 学习重复次数
└── Control Frequency Adaptation (2020)
        ↓
██████████████████████████████████████
█  AP-AC (2020)                      █
█  • 多动作变量多持续时间             █
█  • 周期性非平稳策略                 █
█  • 理论最优性保证                   █
██████████████████████████████████████
        ↓
未来: 自适应频率学习
```

---

## 8. 核心代码逻辑

```python
class ActionPersistentActorCritic:
    """多频率控制的 Actor-Critic"""
    
    def __init__(self, state_dim, action_dims, persistences):
        """
        action_dims: [dim_1, dim_2, ...] 每个动作变量的维度
        persistences: [c_1, c_2, ...] 每个动作变量的持续时间
        """
        self.c = persistences
        self.T = lcm(*persistences)  # 周期
        
        # 每个动作变量、每个相位一个策略头
        self.actors = nn.ModuleDict()
        for k, (dim, c_k) in enumerate(zip(action_dims, persistences)):
            self.actors[f'a{k}'] = nn.ModuleList([
                PolicyHead(state_dim, dim) 
                for phi in range(c_k)
            ])
        
        self.critic = QNetwork(state_dim, sum(action_dims))
        
    def get_action(self, state, t, prev_actions):
        """
        根据时间步 t 和之前动作，返回当前动作
        """
        actions = []
        for k, c_k in enumerate(self.c):
            phi = t % c_k  # 当前相位
            if phi == 0:
                # 决策时刻：从策略采样
                a_k = self.actors[f'a{k}'][0](state).sample()
            else:
                # 持续时刻：保持之前动作
                a_k = prev_actions[k]
            actions.append(a_k)
        
        return actions
    
    def update(self, batch):
        """SAC 风格的更新，考虑动作持续"""
        states, actions, rewards, next_states, dones, timesteps = batch
        
        # Critic 更新（标准 SAC）
        with torch.no_grad():
            next_actions = [self.get_action(s, t+1, a) 
                          for s, t, a in zip(next_states, timesteps, actions)]
            target_q = rewards + gamma * self.critic(next_states, next_actions)
        
        q_loss = mse_loss(self.critic(states, actions), target_q)
        
        # Actor 更新（按相位分组）
        actor_loss = 0
        for k, c_k in enumerate(self.c):
            for phi in range(c_k):
                # 只更新该相位的样本
                mask = (timesteps % c_k) == phi
                if mask.sum() > 0:
                    new_actions = self.actors[f'a{k}'][phi](states[mask])
                    actor_loss -= self.critic(states[mask], new_actions).mean()
        
        return q_loss, actor_loss


# 使用示例
env = MultiRateEnv(
    arm_freq=100,    # 手臂 100Hz
    gripper_freq=20  # 抓手 20Hz
)

# base_freq = 100Hz, 所以 c_arm=1, c_gripper=5
agent = ActionPersistentActorCritic(
    state_dim=env.state_dim,
    action_dims=[7, 1],  # 7 DoF 手臂, 1 DoF 抓手
    persistences=[1, 5]
)
```

---

## 9. 与 Foundation 的链接更新

### 需要添加到 ControlTheory.md
在"多速率采样"部分添加"RL 中的多频率控制"作为学习方法的新范式。

### 需要添加到 ReinforcementLearning.md
在"时间抽象"部分添加"动作持续"作为与 Options 互补的方法。
