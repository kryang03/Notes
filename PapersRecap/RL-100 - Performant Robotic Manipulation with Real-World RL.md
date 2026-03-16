---
tags:
  - paper
  - reinforcement-learning
  - diffusion-policy
  - real-world-rl
  - manipulation
aliases:
  - RL-100
paper-year: 2025
read-date: 2026-03-03
venue: arXiv
paper-pdf: "[[Papers/RL-100: Performant Robotic Manipulation with Real-World.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[ControlTheory]]"
  - "[[EmbodiedAI]]"
---

# RL-100: Performant Robotic Manipulation with Real-World Reinforcement Learning

> [!abstract] 核心贡献
> 提出 **RL-100** 框架，在真实机器人上实现"**模仿学习预训练 → 迭代离线 RL → 在线 RL 微调**"的三阶段 RL 后训练管线。核心创新在于：将 PPO-style 目标统一应用于扩散策略的去噪子MDP中，配合轻量一致性蒸馏压缩至单步推理。在 7 个真实操作任务上达到 **900/900 (100%) 成功率**，在商场部署中连续 7 小时无故障服务，多项任务效率超越人类遥操作。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — PPO 统一离线/在线优化、IQL 优势估计、Offline-to-Online RL
> - [[StochasticProcess]] — DDIM 扩散过程、去噪子MDP、一致性蒸馏
> - [[ControlTheory]] — 单步/动作块控制模式选择、部署延迟优化
> - [[EmbodiedAI]] — 真实世界 RL 工程实践、人类先验对齐
>
> **核心技术**: Diffusion Policy RL, Denoising Sub-MDP, Consistency Distillation, Offline-to-Online PPO

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
在扩散策略的去噪过程中嵌入 PPO 策略梯度，实现"**从人类先验出发 → 对齐部署指标 → 超越人类性能**"的真实世界 RL 后训练恒等式。

### 直观隐喻
制作蛋糕的三层结构：IL 预训练是海绵层（稳定基底），迭代离线 RL 是奶油层（主要改善），在线 RL 是顶部樱桃（最后一英里可靠性）。一致性蒸馏则是将多层蛋糕压缩为可快速享用的版本。

### 领域定位
- **核心问题**: 模仿学习的"模仿天花板" (imitation ceiling) — 性能被示教者技能水平限制
- **解决路径**: 真实世界 RL 后训练突破天花板，同时保留人类先验的安全性和稳定性
- **里程碑**: **首个**在多任务多具身体上实现视觉 RL 后训练并达到 100% 成功率的系统

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 对比方法 | RL-100 优势 |
|---------|-----------|
| 纯 Diffusion Policy (IL) | 突破模仿天花板 → 100% SR |
| Sim-to-Real RL | 无需仿真器，直接在真实世界优化 |
| SERL / HIL-SERL | 更通用（多任务、多具身、多模态） |
| 标准 DPPO | 统一离线/在线 + 一致性蒸馏 |

### 关键贡献点
1. **去噪子MDP 统一 RL 框架** — 将 K 步 DDIM 去噪过程建模为子MDP，PPO 在去噪步上直接优化
2. **三阶段训练**: IL → iterative offline RL (IQL advantages) → online RL (GAE advantages)
3. **一致性蒸馏**: 多步扩散 → 单步一致性策略，满足部署延迟需求
4. **7 任务 100% SR**: 包含动态推、保龄球、倒液、拧螺丝、折衣、榨汁等多种模态

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 去噪子MDP 建模

将扩散策略的 K 步去噪过程嵌入为 MDP 的内层子 MDP:

$$\pi_\theta(x_m | x_t, t \to m) = \mathcal{N}(\mu_\theta(x_t, t \to m), \sigma_{t \to m}^2 I)$$

**DDIM 更新**:
$$\mu_\theta(x_t, t \to m) = \sqrt{\bar{\alpha}_m} \hat{x}_0(x_t, t) + \sqrt{1 - \bar{\alpha}_m - \sigma_{t \to m}^2} \cdot \epsilon_\theta(x_t, t)$$

**子MDP 结构**:
- 状态: $s_k = (a_{\tau_k}, \tau_k, o)$，$a_{\tau_K} \sim \mathcal{N}(0, I)$
- 动作: $u_k = a_{\tau_{k-1}}$ 从去噪子策略采样
- 终端奖励: $R(a_{\tau_0})$ 来自上层环境 MDP

**对数似然**:
$$\log \pi_\theta(x_m | x_t, t \to m) = -\frac{1}{2\sigma_{t \to m}^2} \| x_m - \mu_\theta(x_t, t \to m) \|^2 + C$$

> [!warning] 关键约束
> 当 $\sigma_{t \to m} = 0$ 时转移退化为确定性映射，对数似然无定义。因此基于似然的 RL 目标仅应用于方差严格为正的去噪步。

### 3.2 统一 PPO 目标

离线和在线阶段共享同一策略梯度目标:
$$J_i(\pi) = \mathbb{E}_{s \sim \rho_\pi, a \sim \pi_i}\left[\min\left(r(\pi) A(s,a), \text{clip}(r(\pi), 1-\epsilon, 1+\epsilon) A(s,a)\right)\right]$$

| 阶段 | 优势估计 |
|------|---------|
| 离线 (iterative) | $A_{off}(s,a) = Q(s,a) - V(s)$ (IQL-style) |
| 在线 | $A_{on}(s,a) = \text{GAE}(R_t, V)$ |

### 3.3 一致性蒸馏

将 K 步扩散压缩为单步映射:
$$\mathcal{L}_{CD} = d(f_\theta(x_{\tau_{k+1}}, \tau_{k+1}), f_{\theta^-}(x_{\tau_k}, \tau_k))$$

在训练过程中交替 RL 更新和蒸馏更新，确保部署策略与训练策略同步。

## 4. 实验与验证 (Experiments)

### 任务评估

| 任务 | 具身体 | 挑战类型 | SR |
|------|--------|---------|-----|
| Dynamic Push-T | UR5 | 实时响应 | 100% (250/250) |
| Agile Bowling | UR5 | 释放时机控制 | 100% |
| Pouring | Franka+LEAP | 流体控制 | 100% |
| Dynamic Unscrewing | Franka+LEAP | 精密装配 | 100% |
| Soft-towel Folding | 双臂 xArm+Franka | 可变形物体 | 100% |
| Orange Juicing | xArm | 受限空间操作 | 100% |

**总计**: 900/900 试验 100% 成功。商场部署 ~7 小时连续无故障。

### 鲁棒性
- 环境/动力学偏移下 ~90% 零样本迁移
- 积极人为干扰下 ~95% 保持
- Few-shot 适应新变体 86.7%

## 5. 批判性分析 (Critical Analysis)

### 优势
- **工程完整性**: 从训练到部署的全栈方案，解决延迟/鲁棒性/泛化等实际问题
- **理论统一**: 将扩散去噪与 RL 优化在子 MDP 框架下统一
- **部署验证严格**: 250 次连续成功试验 + 7 小时商场部署是令人信服的可靠性证据

### 局限性
- **仍需人类稀疏反馈**: 在线阶段需要人工提供成功信号
- **任务专化训练**: 每个任务需独立训练，无跨任务迁移
- **未涉及高自由度灵巧操作**: LEAP Hand 仅用于抓取/拧螺丝，未针对 in-hand manipulation

### 未来方向
- 将框架扩展至 VLA 基础模型的后训练（连接 WMPO）
- 在灵巧操作 (in-hand rotation) 等接触丰富任务上验证
- 自动奖励信号替代人类反馈

## 6. 对灵巧操作的启发 (Implications)

> [!important] 对 DNPM 项目的核心启发
> 1. **去噪子MDP 是扩散策略 RL 微调的标准框架**: 如果 DNPM 未来采用扩散策略，可直接复用此框架进行 RL 后训练
> 2. **IL→RL 后训练范式**: "从人类先验出发→突破模仿天花板"的思路可类比为"从 sim 策略出发→真实世界微调"
> 3. **一致性蒸馏的实际价值**: 多步扩散→单步推理的压缩方案对高频控制 (>50Hz) 至关重要
> 4. **三阶段预算分配**: 大部分预算分配给 iterative offline RL，仅小量在线预算用于最后一英里 — 实用的资源分配策略
> 5. **与 Idea-001 (PAI) 关联**: RL-100 的统一 PPO 框架可作为 PAI 变阻抗策略的 RL fine-tuning 方案的理论基础

## 7. 演进脉络定位 (Evolution Context)

```
前置工作: Diffusion Policy (Chi 2023) → DPPO (扩散+RL) → SERL/HIL-SERL (真实世界RL)
    ↓
核心聚焦: 扩散策略的真实世界 RL 后训练统一框架
    ↓
本论文: RL-100 — 去噪子MDP + 统一PPO + 一致性蒸馏 → 100% SR
    ↓
后续影响: WMPO (世界模型RL) → VLA Foundation Model 后训练的标准化
```
