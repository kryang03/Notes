---
tags:
  - paper
  - reinforcement-learning
  - theory
aliases:
  - Unified RL Classification
  - On-Off-Policy Unified
paper-year: 2025
read-date: 2026-03-25
venue: Blog (Kun Lei)
paper-pdf: "[[Papers/Unified Policy Evaluation & Improvement (On_Off-Policy).pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Optimization]]"
---

# Unified Policy Evaluation & Improvement (On/Off-Policy)

> [!abstract] 核心贡献
> 提出以"数据来源 (Data Source)"和"更新调度 (Update Schedule)"两个正交维度对 RL 算法进行统一分类的理论框架，证明了 PPO/SAC/IQL/AWAC 等看似不同的算法在数学底层同源——差异仅在于目标分布的采样策略和 KL 散度正则化的参照系选择。为机器人基础模型的训练策略提供了理论指导。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — 为 PPO/SAC/IQL/AWAC 提供统一分类学（数据源 $w$ × $\pi_{ref}$ 参照系两轴）
> - [[Optimization]] — Trust Region = KL 约束 $\pi_{ref}=\pi^k$；统一提升式是带 KL 正则的策略优化
>
> **核心技术**: 统一 Policy Eval/Improve 方程, Data Source × Update Schedule 两轴, $\pi_{ref}$ 参照系选择

> [!note] 精确锚点与「价值即 Lyapunov」暗线
> - [[ReinforcementLearning#2.2 值函数与 Bellman 方程]] — 本文「统一 Policy Evaluation」就是 Bellman 最小二乘拟合 $\hat Q^{k+1}=\arg\min_Q\mathbb{E}_w[(r+\gamma\mathbb{E}\hat Q-Q)^2]$，数据源 $w$ 决定 on/off-policy。
> - [[ControlTheory#10.4 被动性与"价值即 Lyapunov"]] — 统一框架里 $\pi_{ref}$ 参照系（$\pi^k$/Uniform/$\mu$）统一了信任域/探索/保守；正定代价下这套值迭代收敛的 $Q$ 即 Lyapunov 对象，为下游 safe-RL 的稳定证书提供底座。
> - **簇内 Delta**：$\pi_{ref}=\text{Uniform}$（最大熵）正是 [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach|Exploration vs Exploitation]] 证明的 Gaussian 熵正则最优；与 [[Dynamic Reinforcement Learning for Actors|Dynamic RL]] 的「Lyapunov 标尺」是同一探索↔利用权衡的两种语言（KL 参照系 vs Lyapunov 指数）。

## 1. 问题设定与动机

### 1.1 核心洞察（一句话 + 直观隐喻）
**一句话**：所有 Actor-Critic 算法都可以用统一的 Policy Evaluation + Policy Improvement 公式表达，差异仅在于数据分布 $w$ 和参考策略 $\pi_{ref}$ 的选择。

**隐喻**：
- **Data Source**（数据源）= 用什么录像学投篮：自己刚投的（On-policy）、过去所有的（Off-policy）、纯看乔丹的（Offline）
- **Update Schedule**（更新调度）= 反思频率：随堂测验（Iterative）、大型模拟考（Multi-step）、闭门造车一个月（One-step）

### 1.2 现有方法的局限
- 过往文献将 On/Off-policy/Offline RL 视为截然不同的流派，缺乏统一的理论视角
- 实践中选择算法缺乏系统性指导，尤其在机器人数据飞轮场景下

## 2. 核心方法/理论

### 2.0 核心符号溯源

理论统宗的"变量来源追踪"。枢纽：**$w$（数据源）与 $\pi_{ref}$（KL 参照系）是两个正交轴**——前者定 on/off-policy，后者定算法身份。

| 符号 | 类型 | 来源 | 意义 | 陷阱 |
|------|------|------|------|------|
| $w$ | 分布 | 数据源 | 评估的状态-动作分布 | On=$d^{\pi^k}$、Off/Offline=$d^\mu$（需 IS 修正）|
| $\pi_{ref}$ | 策略 | **选择** | KL 正则参照系 | **决定算法身份**：$\pi^k$/Uniform/$\mu$ |
| $\hat{Q}^k$ | 值函数 | 学习 | 第 $k$ 代 Q | — |
| $\beta$ | scalar | 超参 | KL 惩罚系数 | 极难调，需动态衰减 |
| $\pi^k$ | 策略 | 第 $k$ 代 | 当前策略 | — |
| "step" | 策略代差 | 调度 | **一次完整 Eval+Improve 循环** | **非 env step / grad step**——三态调度的关键定义 |
| IS 权重 | scalar | off-policy 修正 | 重要性采样比 | **必须截断**否则 Q 梯度爆炸 |

### 2.1 关键创新点（Delta 分析）
1. **大统一数学方程**：将几乎所有现代 Actor-Critic 方法归入同一组公式
2. **更新调度三态论**：Iterative / Multi-step / One-step 三种模式的清晰定义与权衡分析
3. **机器人落地指导**：Data Flywheel 场景下 Multi-step $\to$ Iterative 的最优路径

### 2.2 数学框架

**统一策略评估**：
$$
\hat{Q}^{k+1} = \arg \min_{Q} \mathbb{E}_{(s,a) \sim w} \left[ \left( r + \gamma \mathbb{E}_{s'} \mathbb{E}_{a' \sim \pi^k} [\hat{Q}(s',a')] - Q(s,a) \right)^2 \right]
$$
- On-policy：$w = d^{\pi^k}$（当前策略分布），直接采样/Expected SARSA
- Off-policy/Offline：$w = d^\mu$（行为策略分布），需 IS 修正（TD(λ), V-trace, IQL)

**统一策略提升**：
$$
\pi^{k+1} = \arg \max_\pi \mathbb{E}_{s \sim \rho, a \sim \pi} [\hat{Q}^{k+1}(s,a)] - \beta \mathbb{E}_s [D_{KL}(\pi \| \pi_{ref})]
$$

**关键特例推导**：
| 设定 | $\pi_{ref}$ | 效果 |
|------|-------------|------|
| PPO/TRPO | $\pi^k$（旧策略） | Trust Region — 新策略不偏离旧策略太远 |
| SAC | Uniform（均匀分布） | $D_{KL}(\pi \| \text{Uniform}) = -\mathcal{H}(\pi)$ → 最大熵目标 |
| BRAC/AWAC | $\mu$（行为策略） | 保守约束 — 只在见过的动作范围内优化 |

### 2.3 更新调度三态

**"Step" 的精确定义**：不是 env step 或 gradient step，而是**策略代差 (Generations of Policy)** — 一次完整的 Evaluate + Improve 循环。

| 模式 | 策略代差数 | 特点 | 类比 |
|------|-----------|------|------|
| **Iterative** (PPO/SAC) | ~10000 | 高频交互、小步快跑 | 随堂测验 |
| **Multi-step** (Data Flywheel) | ~3-5 | 大规模数据+安全门控 | 大型模拟考 |
| **One-step** (纯 Offline) | 1 | 极端保守、无试错 | 闭门造车 |

**PPO 为什么归为 Iterative**：PPO 的 minibatch + epoch 循环只构成"一个绿色圆圈"（一次 Evaluate+Improve）。$num\_envs \times horizon\_length$ 数据 → 切 minibatch → K epoch SGD → **清空 Buffer** → 下一轮。整个训练重复几千到几万次此循环，故为 Iterative。

### 2.4 核心代码逻辑

```python
# 统一 RL 训练框架伪代码
for iteration in range(num_iterations):
    # Axis 1: Data Source
    if mode == "on-policy":
        data = rollout_environment(current_policy)
        w_dist, pi_ref = current_policy, current_policy
    elif mode == "offline":
        data = load_from_fixed_dataset()
        w_dist, pi_ref = behavior_policy, behavior_policy
    
    # Axis 2: Update Schedule (schedule_steps 决定模式)
    for step in range(schedule_steps):
        # Policy Evaluation
        target_q = r + gamma * E_[a'~pi]{Q(s', a')}
        q_loss = MSE(Q_net(s, a), target_q)
        update(Q_net, q_loss)
        
        # Policy Improvement
        actor_loss = -(Q_net(s, Actor(s)) - beta * KL(Actor, pi_ref))
        update(Actor, actor_loss)
```

### 2.5 概念边界与符号陷阱

- **"step" = 策略代差 (Generations)**，非 env step / grad step——三态调度（Iterative ~10000 / Multi-step ~3-5 / One-step 1）的关键定义。
- **$w$（数据源）vs $\pi_{ref}$（KL 参照）两轴正交**：on/off-policy 由 $w$ 定、算法身份由 $\pi_{ref}$ 定。
- **PPO 是 Iterative**：minibatch+epoch 只构成一个 Eval+Improve 圈，清空 buffer 后重复几千次。
- **$\pi_{ref}=\text{Uniform}\Rightarrow$ 最大熵**（$D_{KL}(\pi\|U)=-\mathcal{H}(\pi)$）= SAC。
- **IS 权重必须截断**：否则 off-policy evaluation 的 Q 梯度爆炸。
- **KL 假设可解析**：高维连续空间可能不精确（§5 理论局限）。

## 3. 训练与实验细节

### 3.1 理论验证
- 本文为理论统宗文章，无传统实验
- 引用 RL-100、Uni-O4、BPPO 作为各调度模式的实际验证

### 3.2 核心结论
- **机器人基础模型 (GEN-0, π0.5)**：Multi-step 是最优折中 — 比 Iterative 稳定（不 Crash），比 One-step 上限高（不保守）
- **Data Flywheel 最佳实践**：大规模 Multi-step 离线更新 $\to$ 逼近瓶颈后切换为 Iterative Online RL 突破人类上限

## 4. 工程关键细节 (Engineering Tricks)
- **重要性权重截断**：Off-policy Evaluation 中 IS 权重必须截断，否则 Q 网络梯度爆炸
- **$\beta$ 超参数**：统一公式中的 KL 惩罚系数极难调，通常需要随训练动态衰减
- **行为策略估计**：Offline RL 中准确拟合多模态的 $\mu$ 本身就是无监督学习难题

## 5. 核心洞见 (Insights)

### 5.1 理论局限性深度分析
- **理论**：统一框架假设 KL 散度可解析计算，对高维连续空间可能不精确
- **算法**：$\pi_{ref}$ 的选择在实践中极度依赖任务性质，不存在通用最优
- **工程**：Multi-step 的"安全门控"在真实机器人部署中仍需大量人工监督

### 5.2 与用户研究的启发
- 当前用户的 PPO 转笔训练 = 典型 Iterative RL — 高频交互，每轮清空 Buffer
- 若考虑真机部署，应采用 Multi-step 路线：先仿真中 Iterative PPO 练到收敛 → 真机上做几轮安全 Multi-step 微调 → 最后少量 Online RL 突破 Sim-to-Real gap

> [!note] RL 算法统一框架：知识库所有 Actor-Critic 的分类学锚点
> 本文给出**元框架**，把知识库里所有用 RL 的 recap 归位到 **(数据源 $w$) × ($\pi_{ref}$ 参照系)** 两轴。最深的 insight 是 **$\pi_{ref}$ 三种选择统一了"信任域 / 探索 / 保守"**：
>
> | $\pi_{ref}$ | 算法 | 效果 | 知识库对应 |
> |------|------|------|----------|
> | $\pi^k$（旧策略） | PPO/TRPO | 信任域 | in-hand / control-freq 簇大量用 PPO |
> | Uniform | SAC | 最大熵 $-\mathcal{H}(\pi)$ | = [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach\|Exploration vs Exploitation]] 证明的 Gaussian 熵正则最优 |
> | $\mu$（行为策略） | BRAC/AWAC/IQL | 保守约束 | offline / safe RL |
>
> **跨簇 insight**：这把探索/稳定性簇的"熵正则探索"（$\pi_{ref}$=Uniform）与 safe-RL 的"保守约束"（$\pi_{ref}=\mu$）统一为**同一个 KL 正则的参照系选择**——探索与保守不是对立，而是 $\pi_{ref}$ 谱的两端（Uniform 最探索、$\mu$ 最保守、$\pi^k$ 居中）。这与 [[Dynamic Reinforcement Learning for Actors|Dynamic RL]] 的"Lyapunov 标尺（探索↔利用）"是**同一权衡的两种数学语言**（KL 参照系 vs Lyapunov 指数）。更新调度三态（Iterative/Multi-step/One-step）则对应 sim-to-real 训练流程（[[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]] IL→Offline→Online）。

## 6. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
- 为 RL Foundation 中 PPO/SAC/IQL 等算法提供了统一的分类学视角
- 三态调度论直接指导灵巧手 Sim-to-Real 的训练策略选择

### 与 [[Optimization]] 的联系
- Trust Region 在统一框架中表现为 KL 约束的 $\pi_{ref} = \pi^k$
- Multi-step 类似于优化中的"大步 + 安全检查"策略

## 7. 局限与未来方向

### 7.1 论文自身局限
- 理论概述性质，缺乏新实验验证
- 对 Model-Based RL 和 World Model 方向未涉及

### 7.2 对灵巧手转笔 / Sim-to-Real 的启发
- 仿真训练（Iterative PPO）→ 真机微调（Multi-step with safety gates）→ 在线 RL 突破上限
- 这与 [[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]] 的 IL → Offline RL → Online RL 流程呼应

## References
- [[RL-100 - Performant Robotic Manipulation with Real-World RL]]
- [[Autoregressive Policies for Continuous Control Deep Reinforcement Learning]]
