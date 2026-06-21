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
venue: ICML 2022
paper-pdf: "[[Papers/Reachability Constrained Reinforcement Learning.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[Optimization]]"
---

# Reachability Constrained Reinforcement Learning

> [!abstract] 核心贡献
> 针对"CMDP 的期望累积约束 $\mathbb{E}[\sum\gamma^t c]\le\epsilon$ 只保证**平均**安全、掩盖单步危险，而 CBF/SI 又过度保守"这一瓶颈，提出 **RCRL**：用可达性分析定义**最大可行集** $\mathcal{F}^*=\{s:V_s^*(s)\le0\}$，其中 safety value function $V_s^*=\min_\pi\max_t h(s_t)$ 取**最坏时刻**（max 非 sum）。结构性洞见：**持续安全 ≠ 平均安全——安全约束应是逐点(pointwise)的最坏情况量，而非期望累积量；由此学到的可行集是理论最大的"还有救"集合，性能牺牲最小。**

> [!tip] 与理论基础的关联
> - [[ControlTheory]] - CBF 形式化定义（安全集、Lie 导数、HJ 可达性联系）
> - [[ReinforcementLearning]] - CMDP 与 Lagrangian 方法
> - [[Optimization|拉格朗日对偶理论]] - 本文的 PPO-Lagrangian 和 SAC-Lagrangian 直接依赖对偶分解，将安全约束通过拉格朗日乘子 $\lambda$ 转化为无约束优化
> - [[Optimization|KKT 条件]] - RCRL 的最优可行集边界对应 KKT 互补松弛性：约束活跃当且仅当在可行集边界上
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

### 3.0 变量来源追踪

全文枢纽是 **$V_s=\max_t h$ 的 max（非 sum）**——它把"安全"从期望累积量变成逐点最坏情况量，这是与 CMDP 路线的根本分野。

| 变量 | 类型/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $s$ | $\mathbb{R}^{d_s}$ | 观测 | 否（输入） | 状态 | — |
| $h(s)$ | scalar | **设计**（约束函数） | 否 | 状态约束（如负的障碍距离），$\le0$ 安全 | 设计 $h$ 是把任务安全需求形式化的关键 |
| $c(s)=\mathbf{1}_{h>0}$ | $\{0,1\}$ | 计算 | 否 | 二值违约代价 | 二值，非连续代价 |
| $V_s^\pi(s)=\max_t h(s_t^\pi)$ | scalar | 学习（safety critic） | 否（评估） | 沿 $\pi$ 的**最坏**约束违反 | **max 非 sum**——捕捉最坏时刻 |
| $V_s^*=\min_\pi V_s^\pi$ | scalar | 学习 | 否 | 最优 safety value | 最大可行集的判据 |
| $\mathcal{F}^*=\{s:V_s^*\le0\}$ | 集合 | 导出 | — | **最大可行集** | 集外状态"注定失败"（无论何策略都违约），非仅"危险" |
| $Q_s^\pi(s,a)$ | scalar | 学习（max-Bellman） | 是 | safety Q | Bellman 用 $\max\{h,\gamma Q_s'\}$ 非 $+$ |
| $\lambda$ | scalar | **慢**时间尺度 | 否 | 拉格朗日乘子 | 截断 $[0,\lambda_{max}]$ 防淹没 reward |
| $\pi$ | 策略 | **中**时间尺度 | 是 | 策略 | 三尺度 $\alpha_c\gg\alpha_\pi\gg\alpha_\lambda$ |

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

### 3.6 概念边界与符号陷阱

- **$V_s=\max_t h$ 用 max 非 sum**：最坏时刻 vs 平均（CMDP）——持续安全的数学本体；§4.5 消融"max→sum 安全大幅下降"直接验证。
- **safety Q Bellman 用 max 非 $+$**：$Q_s=\max\{h(s),\gamma Q_s(s',a')\}$，递推最坏违反、不累加。
- **三时间尺度 $\alpha_c\gg\alpha_\pi\gg\alpha_\lambda$**：critic 快、actor 中、乘子慢；同速→乘子振荡训练不稳（§4.5）。
- **可行集外 = "注定失败"**：不是"危险"，而是无论何策略都会违约（不可救）——可达性视角的独特语义。
- **max 不可微**：实践用 smooth-max（softmax，温度 $\tau{=}0.1$）近似。
- **KKT 互补松弛** $\lambda^*\cdot\mathbb{E}[V_s^{\pi^*}]=0$：最优策略要么在可行集边界（$\lambda^*>0$）、要么约束不活跃（$\lambda^*=0$）。
- **确定性动力学假设**：随机系统需概率可达性扩展（§5 局限）。

## 4. 实验与验证 (Experiments)

### 4.1 实验设置

**环境**：
- Safe-Control-Gym（无人机、倒立摆）
- Safety-Gym（机器人导航）

**基线**：
- CMDP 方法：PPO-Lagrangian, SAC-Lagrangian
- 能量方法：CBF-RL, SI-RL
- 切换方法：Recovery RL

### 4.1.1 训练细节

| 超参数 | PPO-RCRL | SAC-RCRL |
|--------|----------|----------|
| 策略网络 | 2×256 MLP + Tanh | 2×256 MLP + ReLU |
| Safety Q 网络 | 同 Reward Q 结构 | 同 Reward Q 结构 |
| 学习率 (critic) $\alpha_c$ | 3e-4 | 3e-4 |
| 学习率 (actor) $\alpha_\pi$ | 1e-4 | 1e-4 |
| 学习率 (Lagrange) $\alpha_\lambda$ | 1e-5 | 1e-5 |
| 折扣因子 $\gamma$ | 0.99 | 0.99 |
| 训练步数 | 1M | 1M |
| Critic 更新/Actor 更新 | 5:1 | 1:1 (soft update) |

**监督信号**：Reward $r(s,a)$ + 二值化安全代价 $c(s) = \mathbf{1}_{h(s)>0}$

**数据来源**：on-policy (PPO) / replay buffer 1M (SAC)

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

### 4.5 Ablation 因果链分析

| 去掉的组件 | 结果变化 | 因果机制 |
|-----------|---------|----------|
| max → sum ($Q_s$ 用加法) | 安全性大幅下降 | sum 允许“平均安全”掩盖单步危险，max 才能捕捉最坏情况 |
| 去掉多时间尺度 → 同速更新 | Lagrange 乘子振荡，训练不稳定 | $\lambda$ 更新太快 → critic 未收敛时乘子已变化 → 策略优化方向错误 |
| $\gamma$ 从 0.99→0.9 | 可行集缩小 ~30% | 过度折扣使远期危险被低估，边界向内收缩 |
| Safety Q → 累积代价 Q | 约束违反率从 1%→12% | 累积代价允许“偶尔违约但平均合格”，失去持续安全保证 |

### 4.6 工程关键细节 (Engineering Tricks)

- **max 操作的梯度问题**：$Q_s = \max\{h(s), \gamma Q_s(s',a')\}$ 中 max 不可微，实践中用 smooth-max $\text{softmax}(x,y) = \log(e^x + e^y)$ 近似，温度参数 $\tau=0.1$
- **Lagrange 乘子稳定性**：$\lambda$ 截断到 $[0, \lambda_{\max}]$（一般 $\lambda_{\max}=100$），防止无限增长导致 reward 信号完全被淉没
- **Safety Q 初始化**：用 $h(s)$ 的值初始化 safety Q 网络（而非随机初始化），加速可行集边界的学习
- **多约束扩展**：多个 $h_i(s)$ 对应多个 $Q_{s,i}$ 和 $\lambda_i$，取 $\max_i Q_{s,i}$ 作为综合安全指标

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

### 6.1 与用户研究的启发（灵巧手转笔 / Sim-to-Real）

1. **可行集 → 转笔安全边界**：转笔中「笔已经飞出可控范围」的状态对应可行集外。Safety value function $V_s^*(s) \leq 0$ 可定义「笔还能被接住」的状态边界
2. **关节限位保护**：$h(s) = \max_i(|q_i| - q_{i,\max})$ 可直接作为状态约束，RCRL 学习「还能回到安全关节角」的最大集合
3. **Sim-to-Real 安全层**：在仿真中训练 safety Q，部署时作为安全过滤器叠加在 sim-to-real 策略之上，只拒绝 $V_s > 0$ 的动作
4. **局限**：转笔的接触动力学高度随机，$h(s)$ 的设计需要结合触觉信号实时估计

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

## 9. 与知识体系的联系

### 与 Foundation 的数学联系

**与 [[ControlTheory]] 的数学联系 — Hamilton-Jacobi 可达性**：

本文的 safety value function $V_s^*(s) = \min_\pi \max_{t \geq 0} h(s_t^\pi)$ 是 HJ 可达性分析的离散时间版本。经典 HJ PDE $\min\{\partial_t V + H(x, \nabla V), V(x) - l(x)\} = 0$ 中，$l(x)$ 对应 $h(s)$，$\partial_t V + H$ 对应 Bellman 更新。RCRL 用神经网络替代了 PDE 求解器。

**与 [[Optimization]] 的数学联系 — 拉格朗日对偶**：

RCRL 的约束优化 $\max_\pi J(\pi) \;\text{s.t.}\; \mathbb{E}[V_s^\pi] \leq 0$ 通过强对偶 $\min_\lambda \max_\pi \{J(\pi) - \lambda V_s^\pi\}$ 转化为鞍点问题。KKT 互补松弛性 $\lambda^* \cdot \mathbb{E}[V_s^{\pi^*}] = 0$ 意味着：最优策略要么在可行集边界上（$\lambda^* > 0$），要么安全约束不活跃（$\lambda^* = 0$）。

### 跨方法对比（补充）

| 维度 | RCRL | [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective\|Stability-Cert. RL]] | [[Safe Model-based Reinforcement Learning with Stability Guarantees\|Lyapunov RL]] | [[On Robust Reinforcement Learning with Lipschitz-Bounded Policy Networks\|Lipschitz RL]] |
|------|------|------------------------------|--------------------------|----------------------------|
| 安全定义 | 可行集内可达 | $\mathcal{L}_2$ 增益有界 | 吸引域前向不变 | 输出 Lip 有界 |
| Model-free? | ✅ | ✖ (LTI) | ✖ (GP) | ✅ |
| 最优可行集 | ✅ | N/A | 保守 (GP) | N/A |
| 多约束 | 可扩展 | N/A | 困难 | N/A |
| 计算额外开销 | Safety Q 网络 | SDP 离线 | GP $O(n^3)$ | Cayley $O(n^3)$/层 |

> [!note] 安全 RL 子簇定位与新 insight（与 [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective|Stability-Cert RL §6.1 四证书表]] 互参）
> RCRL 在安全 RL 子簇占"**可行集/可达性**"格（其余三格：IQC/$\mathcal{L}_2$=Stability-Cert RL、Lyapunov 吸引域=[[Safe Model-based Reinforcement Learning with Stability Guarantees|Berkenkamp]]、Lipschitz 架构=[[On Robust Reinforcement Learning with Lipschitz-Bounded Policy Networks|Lipschitz RL]]）。把四者按"安全的数学对象"排开，RCRL 揭示一个更根本的二分：
> **① 期望型 vs 最坏情况型安全**：CMDP-Lagrangian 用 $\mathbb{E}[\sum\gamma^t c]\le\epsilon$（期望累积，允许偶尔违约）；RCRL 用 $V_s=\max_t h$（逐点最坏，要求恒不违约）。**这是 safe RL 最根本的约束类型分野**，决定"安全"是统计保证还是逐点保证——对灵巧手接触/转笔这类"一次失误即掉落"的任务，必须用最坏情况型。
> **② 与 Stability-Cert RL 互补**：RCRL 管"状态可行性"（state 不进不可救集）、Stability-Cert RL 管"输入-输出稳定性"（扰动→增益有界）——一个约束 state、一个约束 I/O map，可叠加成更完整安全栈。
> **③ 接 Lyapunov 标尺**：$V_s$ 是 HJ 可达性的 RL 版，与 Stability-Cert RL 同属"安全"半轴，但 RCRL 只要求"可达安全集"、不要求全局稳定——是比 Lyapunov 稳定更**宽松**的安全概念（允许在可行集内自由运动）。这提示安全的强度也有谱：可行集(最宽) ⊃ Lyapunov 稳定 ⊃ $\mathcal{L}_2$ 增益有界。
