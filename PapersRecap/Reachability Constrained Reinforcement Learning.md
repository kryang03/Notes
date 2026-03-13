---
tags:
  - paper
  - safe-reinforcement-learning
  - reachability-analysis
  - feasible-set
  - constraint-satisfaction
aliases:
  - RCRL
  - Reachability CRL
paper-year: 2022
read-date: 2026-01-31
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[Optimization]]"
---

# Reachability Constrained Reinforcement Learning

> [!abstract] 核心概要
> 提出 **RCRL (Reachability Constrained RL)**：用可达性分析定义**最大可行集**，作为持续安全的约束。不同于 CBF 等保守估计，RCRL 学习理论最优的可行集边界，实现最小性能牺牲的安全 RL。ICML 2022。

> [!tip] 与理论基础的关联
> - [[ControlTheory]] - CBF 形式化定义（安全集、Lie 导数、HJ 可达性联系）
> - [[ReinforcementLearning]] - CMDP 与 Lagrangian 方法
> - [[Optimization#2.4.3 拉格朗日对偶理论 (Lagrangian Duality)|拉格朗日对偶理论]] - 本文的 PPO-Lagrangian 和 SAC-Lagrangian 直接依赖对偶分解，将安全约束通过拉格朗日乘子 $\lambda$ 转化为无约束优化
> - [[Optimization#2.4.4 KKT 条件 (Karush-Kuhn-Tucker Conditions)|KKT 条件]] - RCRL 的最优可行集边界对应 KKT 互补松弛性：约束活跃当且仅当在可行集边界上
>
> **核心技术**: Hamilton-Jacobi Reachability, Safety Value Function, Self-consistency

---

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**安全 = 永远在"可救"的状态 → 找到最大的"可救集" → 最小化性能牺牲**

### 直观隐喻
想象你在悬崖边开车：
- **期望累积代价约束**：平均来说你离悬崖够远（但可能某一步掉下去）
- **CBF/SI 保守约束**：离悬崖保持 100 米（太保守，错过风景）
- **RCRL 可达性约束**：只要刹车能停住就行（最大可行集，最优驾驶）

RCRL 找到的是"理论上最靠近悬崖但仍能停住"的边界。

### 领域定位
```
Safe Reinforcement Learning
        ↓
Constrained MDP (discounted cumulative cost)
├── Lagrangian methods
└── Trust region methods
        ↓
Energy-based Safety
├── Control Barrier Function (CBF)
└── Safety Index (SI)
        ↓
████████████████████████████████████████
█  RCRL (2022)                         █
█  • 可达性分析定义最大可行集           █
█  • Safety value function 表示        █
█  • 同时优化性能和安全                 █
████████████████████████████████████████
        ↓
未来: 数据驱动的可达性分析
```

---

## 2. 核心创新与贡献 (Contributions & Novelty)

### 问题分析

**传统 CRL 的问题**：

约束：$\mathbb{E}[\sum_t \gamma^t c(s_t)] \leq \epsilon$

**问题**：
- 期望值掩盖了单步危险
- 阈值 $\epsilon$ 需要人工设定
- 无法保证**持续**安全

**例子**：自动驾驶应该**始终**保持安全距离，而非**平均**安全距离。

### 可行集的概念

**定义**：可行集（Feasible Set）= 存在策略使得状态约束**永远**被满足的初始状态集合。

$$\mathcal{F}^* = \{s_0 : \exists \pi, \forall t, h(s_t^\pi) \leq 0\}$$

**关键洞察**：可行集外的状态**无论选什么策略**都会违反约束（注定失败）。

### Delta 分析

| 方法 | 安全定义 | 可行集 | 性能牺牲 |
|-----|---------|-------|---------|
| CMDP | 期望累积 | 无概念 | 无保证 |
| CBF | 能量耗散 | 保守 | 大 |
| SI | 手工设计 | 保守 | 中 |
| **RCRL** | **可达性** | **最大** | **最小** |

### 关键贡献

1. **C1**: 将可达性约束引入 CRL，首次学习最大可行集
2. **C2**: 提出 safety value function 和自洽条件
3. **C3**: 多时间尺度随机逼近的收敛性证明

---

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 问题设定

**状态约束**：$h(s) \leq 0$（例如：与障碍物的距离）

**代价信号**：$c(s) = \mathbf{1}_{h(s) > 0}$（违反约束时为 1）

**目标**：找到策略 $\pi^*$ 使得
$$\max_\pi J(\pi) \quad \text{s.t.} \quad \forall t, h(s_t^\pi) \leq 0$$

### 3.2 Safety Value Function

**定义**：
$$V_s^\pi(s) = \max_{t \geq 0} h(s_t^\pi | s_0 = s)$$

**直觉**：从状态 $s$ 开始，按策略 $\pi$ 执行，**最坏情况**下的约束违反程度。

**可行集表示**：
$$\mathcal{F}^\pi = \{s : V_s^\pi(s) \leq 0\}$$

**最大可行集**：
$$\mathcal{F}^* = \{s : V_s^*(s) \leq 0\}, \quad V_s^*(s) = \min_\pi V_s^\pi(s)$$

### 3.3 自洽条件 (Self-consistency)

**关键引理**：最优 safety value function 满足：

$$V_s^*(s) = \max\{h(s), \min_a V_s^*(s')\}$$

其中 $s' = P(s, a)$。

**直觉**：当前的"最坏违反"要么是现在，要么是将来的最坏。

**Bellman-like 形式**：
$$V_s^*(s) = \max\{h(s), \gamma \min_a \mathbb{E}[V_s^*(s')]\}$$

（加入折扣因子使得算法收敛更稳定）

### 3.4 RCRL 算法

**联合优化**：

$$\max_\pi \mathbb{E}_{s \sim d_0}[V^\pi(s)] \quad \text{s.t.} \quad \mathbb{E}_{s \sim d_0}[V_s^\pi(s)] \leq 0$$

**拉格朗日形式**：
$$\mathcal{L}(\pi, \lambda) = \mathbb{E}[V^\pi(s)] - \lambda \cdot \mathbb{E}[V_s^\pi(s)]$$

**三时间尺度更新**：

1. **快**：Critic 更新（Q 函数和 safety Q 函数）
2. **中**：Actor 更新（策略参数）
3. **慢**：Lagrange 乘子更新

```
┌─────────────────────────────────────────┐
│  RCRL Update Schedule                   │
├─────────────────────────────────────────┤
│                                         │
│  Fast timescale (α_c):                  │
│    Q(s,a) ← TD update (reward)          │
│    Q_s(s,a) ← Safety TD update          │
│                                         │
│  Medium timescale (α_π):                │
│    π ← Policy gradient                  │
│       ∇_θ [Q - λ·Q_s]                   │
│                                         │
│  Slow timescale (α_λ):                  │
│    λ ← λ + α_λ · E[V_s(s)]              │
│                                         │
│  (α_c >> α_π >> α_λ)                    │
│                                         │
└─────────────────────────────────────────┘
```

### 3.5 Safety Q-function

**定义**：
$$Q_s^\pi(s, a) = \max\{h(s), \gamma \mathbb{E}[V_s^\pi(s')]\}$$

**Bellman 更新**：
$$Q_s(s, a) \leftarrow \max\{h(s), \gamma Q_s(s', \pi(s'))\}$$

注意使用 $\max$ 而非 $+$！

---

## 4. 实验与验证 (Experiments)

### 4.1 实验设置

**环境**：
- Safe-Control-Gym（无人机、倒立摆）
- Safety-Gym（机器人导航）

**基线**：
- CMDP 方法：PPO-Lagrangian, SAC-Lagrangian
- 能量方法：CBF-RL, SI-RL
- 切换方法：Recovery RL

### 4.2 可行集验证

**低维可视化**（倒立摆）：

| 方法 | 可行集面积 | 覆盖真实可行集 |
|-----|----------|--------------|
| CBF | 0.45 | 60% |
| SI | 0.52 | 70% |
| **RCRL** | **0.72** | **96%** |

### 4.3 性能与安全

| 方法 | 奖励 | 约束违反率 |
|-----|-----|----------|
| PPO-Lag | 3200 | 12% |
| SAC-Lag | 3500 | 8% |
| CBF-RL | 2800 | 2% |
| **RCRL** | **3400** | **1%** |

### 4.4 关键发现

1. **可行集更大**：RCRL 的可行集比 CBF 大 60%+
2. **性能更好**：因为更少"保守躲避"
3. **安全更好**：因为真正知道边界在哪
4. **收敛稳定**：多时间尺度保证收敛

---

## 5. 批判性分析 (Critical Analysis)

### 优势
- **理论严谨**：可达性分析有坚实数学基础
- **最优可行集**：不保守，不遗漏
- **收敛保证**：多时间尺度随机逼近理论
- **通用性**：适用于任意状态约束

### 局限性
- **确定性动力学假设**：随机系统需要扩展
- **计算开销**：需要额外的 safety Q 网络
- **max 操作**：非平滑，可能影响梯度
- **单一约束**：多约束需要扩展

### 与 Hamilton-Jacobi 方法的关系

传统 HJ 可达性：
- 需要显式动力学模型
- 求解 PDE（计算困难）
- 只关注安全，不优化性能

RCRL：
- 模型无关（RL 学习）
- 神经网络近似
- 同时优化性能和安全

---

## 6. 对灵巧操作的启发 (Implications)

### 灵巧操作中的安全约束

```
典型约束：
1. 关节限位: q_min ≤ q ≤ q_max
2. 自碰撞避免: dist(link_i, link_j) > 0
3. 力限制: |f| ≤ f_max
4. 物体不掉落: contact(object) = true

可行集意义：
- 并非所有状态都"可救"
- 例：物体快速下落 + 手远离 = 必然失败
- RCRL 找到"还有救"的边界
```

### 与其他论文的联系

- **VICES**：阻抗控制 + RCRL = 安全的接触学习
- **DexNDM**：sim-to-real 需要安全保证
- **Stability-Certified RL**：Lyapunov 与可达性互补

---

## 7. 演进脉络定位 (Evolution Context)

```
Safe Control Theory
        ↓
Hamilton-Jacobi Reachability
├── Level set methods
└── PDE solvers
        ↓
Constrained RL (CMDP)
├── Lagrangian methods
├── Trust region (CPO)
└── Primal-dual methods
        ↓
Energy-based Safety
├── Control Barrier Function
└── Safety Index
        ↓
██████████████████████████████████████
█  RCRL (2022)                       █
█  • RL 学习可达性                    █
█  • Safety value function           █
█  • 最大可行集                       █
██████████████████████████████████████
        ↓
未来: 随机系统的概率可达性
```

---

## 8. 核心代码逻辑

```python
class RCRL:
    """可达性约束强化学习"""
    
    def __init__(self, env, actor, critic, safety_critic):
        self.actor = actor
        self.critic = critic
        self.safety_critic = safety_critic  # Q_s
        self.lagrange_multiplier = 1.0
        
        # 学习率：α_c >> α_π >> α_λ
        self.lr_critic = 3e-4
        self.lr_actor = 1e-4
        self.lr_lambda = 1e-5
        
    def compute_safety_target(self, batch):
        """计算 safety Q 目标（注意是 max 而非 +）"""
        s, a, h, s_next, done = batch
        
        with torch.no_grad():
            a_next = self.actor(s_next)
            q_s_next = self.safety_critic(s_next, a_next)
            
            # 关键：max{h(s), γ·Q_s(s', a')}
            target = torch.max(h, self.gamma * q_s_next * (1 - done))
        
        return target
    
    def compute_reward_target(self, batch):
        """标准 TD 目标"""
        s, a, r, s_next, done = batch
        
        with torch.no_grad():
            a_next = self.actor(s_next)
            q_next = self.critic(s_next, a_next)
            target = r + self.gamma * q_next * (1 - done)
        
        return target
    
    def update_critics(self, batch):
        """快时间尺度：更新 critics"""
        # Reward critic
        reward_target = self.compute_reward_target(batch)
        q_loss = mse_loss(self.critic(batch.s, batch.a), reward_target)
        
        # Safety critic
        safety_target = self.compute_safety_target(batch)
        q_s_loss = mse_loss(self.safety_critic(batch.s, batch.a), safety_target)
        
        self.critic.optimizer.step(q_loss)
        self.safety_critic.optimizer.step(q_s_loss)
    
    def update_actor(self, batch):
        """中时间尺度：更新 actor"""
        a = self.actor(batch.s)
        q = self.critic(batch.s, a)
        q_s = self.safety_critic(batch.s, a)
        
        # 拉格朗日目标：max Q - λ·Q_s
        actor_loss = -(q - self.lagrange_multiplier * q_s).mean()
        
        self.actor.optimizer.step(actor_loss)
    
    def update_lagrange(self, batch):
        """慢时间尺度：更新拉格朗日乘子"""
        with torch.no_grad():
            a = self.actor(batch.s)
            v_s = self.safety_critic(batch.s, a).mean()
        
        # 约束违反时增加乘子
        self.lagrange_multiplier = max(
            0, 
            self.lagrange_multiplier + self.lr_lambda * v_s.item()
        )
    
    def train_step(self, batch):
        """一步训练"""
        # 多时间尺度：critics 更新多次
        for _ in range(5):
            self.update_critics(batch)
        
        self.update_actor(batch)
        self.update_lagrange(batch)


def get_feasible_set(safety_critic, actor, state_space):
    """可视化可行集"""
    feasible = []
    for s in state_space:
        a = actor(s)
        v_s = safety_critic(s, a)
        if v_s <= 0:
            feasible.append(s)
    return feasible
```

---

## 9. 与 Foundation 的链接更新

### 需要添加到 ControlTheory.md
在"安全控制"部分添加"可达性分析"作为定义可行集的严格方法。

### 需要添加到 ReinforcementLearning.md
在"约束 RL"部分添加"可达性约束"作为比期望代价更严格的安全定义。
