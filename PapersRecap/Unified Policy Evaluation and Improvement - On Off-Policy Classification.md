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
