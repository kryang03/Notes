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

正常的机器人环境是一个 MDP：$\mathcal{M} = (S, A, P, R, \gamma)$。 在这里，策略需要在状态 $s_t$ 输出动作 $a_t$。 但当使用扩散模型生成 $a_t$ 时，生成过程本身是一个包含了 $K$ 个子步骤的马尔可夫链。将扩散策略的 K 步去噪过程嵌入为 MDP 的内层子 MDP:

$$\pi_\theta(x_m | x_t, t \to m) = \mathcal{N}(\mu_\theta(x_t, t \to m), \sigma_{t \to m}^2 I)$$

**DDIM 更新**:
$$\mu_\theta(x_t, t \to m) = \sqrt{\bar{\alpha}_m} \hat{x}_0(x_t, t) + \sqrt{1 - \bar{\alpha}_m - \sigma_{t \to m}^2} \cdot \epsilon_\theta(x_t, t)$$

**子MDP 结构**:
- 状态: $s_k = (a_{\tau_k}, \tau_k, o)$，$a_{\tau_K} \sim \mathcal{N}(0, I)$，其中 $a^{\tau_k}$ 是第 $k$ 步的带噪动作，$\tau_k$ 是扩散时间步，$o$ 是环境观测。
- 动作: $u_k = a_{\tau_{k-1}}$ 从去噪子策略采样
- **子策略 (DDIM 采样)**：每一步去噪都可以看作是一个带有方差 $\sigma_{\tau_k}$ 的高斯子策略：$\pi_\theta(a^{\tau_{k-1}} | a^{\tau_k}, \tau_k) = \mathcal{N}(\mu_\theta, \sigma_{\tau_k}^2 I)$。
- **子奖励**：在子 MDP 的中间步骤奖励为 0，只有当达到 $\tau_0$ 产出真实动作 $a_t$ 并与环境交互后，才获得环境的终端奖励 $R(a^{\tau_0})$

**对数似然**:
$$\log \pi_\theta(x_m | x_t, t \to m) = -\frac{1}{2\sigma_{t \to m}^2} \| x_m - \mu_\theta(x_t, t \to m) \|^2 + C$$
> [!warning] 关键约束
> 当 $\sigma_{t \to m} = 0$ 时转移退化为确定性映射，对数似然无定义，RL 就没法探索。因此基于似然的 RL 目标仅应用于方差严格为正的去噪步，RL-100 强制截断方差：$\tilde{\sigma}_k = \text{clip}(\sigma_k, \sigma_{min}, \sigma_{max})$（如设定在 $[0.01, 0.8]$），既保证在去噪的最后阶段（快要生成最终动作时），系统依然保留微小的随机性，防止早熟收敛（Premature convergence），为 PPO 提供微调的梯度空间，又防止在去噪早期产生破坏性的过度探索。
### 3.2 统一 PPO 目标

离线和在线阶段共享同一策略梯度目标，**将宏观时间步 $t$ 计算出的 Task Advantage $A_t$ 共享给产生该动作的所有 $K$ 个去噪步骤**:
$$J_i(\pi) = \mathbb{E}_{s \sim \rho_\pi, a \sim \pi_i}\left[\min\left(r(\pi) A(s,a), \text{clip}(r(\pi), 1-\epsilon, 1+\epsilon) A(s,a)\right)\right]$$

| 阶段 | 优势估计 |
|------|---------|
| 离线 (iterative) | $A_{off}(s,a) = Q(s,a) - V(s)$ (IQL-style) |
| 在线 | $A_{on}(s,a) = \text{GAE}(R_t, V)$ |
- 在**迭代离线 RL**阶段，策略不能与环境交互。作者利用离线数据集 $D$ 训练基于 IQL（Implicit Q-Learning）的 Critic，从而估算离线优势：$A^{off}_t = Q(s_t, a_t) - V(s_t)$。
  RL-100 的离线阶段没有任何与环境的交互 。为了在完全不查询 OOD 动作的情况下评估策略的好坏，作者引入了 IQL 风格的 Critic 。 IQL 的核心思想是**期望分位数回归（Expectile Regression）**。它只利用数据集中实际存在的 $(s, a)$ 对来更新价值函数，避免了对未见动作的评估。
  在 RL-100 中，离线阶段的优势函数被定义为：

$$A^{off}(s, a) = Q_\psi(s, a) - V_\psi(s)$$
	**$Q_\psi(s, a)$**：评估在状态 $s$ 下采取具体动作 $a$（数据集中的动作）的累积回报 。
	**$V_\psi(s)$**：评估状态 $s$ 的整体基线价值 。在 IQL 中，$V(s)$ 通常拟合的是该状态下表现最好的那部分动作的价值（上分位数）。
    
    如果 $A^{off}(s, a) > 0$，说明当前动作 $a$ 比该状态的平均高水准还要好；如果 $A^{off}(s, a) < 0$，说明这个动作相对次优。这个信号随后被“广播”给生成该动作 $a$ 的所有 $K$ 个扩散去噪步骤，引导 PPO 增加或减少生成该轨迹的概率 。
    
- 在**在线 RL**阶段，策略可以交互。作者使用 GAE（Generalized Advantage Estimation）来平衡方差和偏差：$A^{on}_t = \text{GAE}(\lambda, \gamma; r_t, V_\psi)$。
### 3.3 一致性蒸馏

将 K 步扩散压缩为单步映射:
$$\mathcal{L}_{CD} = d(f_\theta(x_{\tau_{k+1}}, \tau_{k+1}), f_{\theta^-}(x_{\tau_k}, \tau_k))$$

在训练过程中交替 RL 更新和蒸馏更新，确保部署策略与训练策略同步。
### 3.4算法实现与逻辑

1. **模仿学习初始化**：用人类演示数据 $\mathcal{D}_0$ 预训练视觉编码器 $\phi$ 和 Diffusion 策略 $\pi_\theta$。
    - **Rollout 方式**：人类操作员佩戴 Apple Vision Pro（用于 3D 灵巧手）或使用手柄（用于 2D 平面任务）遥控机器人完成任务 。
    - **数据形态**：收集同步的视觉/本体感觉观测 $o_t, q_t$ 和动作 $a_t$ 序列，构成初始演示数据集 $\mathcal{D}_0$ 。此阶段模型纯粹在进行监督学习，完全不与环境发生自主交互 。
2. **保守的 OPE（离线策略评估）门控机制**：在离线更新时，如何知道更新后的策略 $\pi$ 真的比上一代 $\pi_i$ 好？如果盲目部署会弄坏机器人。作者使用 AM-Q 进行无环境交互的评估：只有当 $\hat{J}^{AM-Q}(\pi) - \hat{J}^{AM-Q}(\pi_i) \ge \delta$ 时，才接受候选策略。
    - 首先在当前数据集 $\mathcal{D}_m$ 上进行纯离线的 PPO 更新，得到一个更好的候选策略 。
    - 通过 OPE（离线策略评估）确认新策略确实变强后，**将新策略部署到真实机器人上进行 Rollout**，收集新的交互轨迹 $\mathcal{D}_{new}$ 。
    - 将新轨迹合并进数据集（$\mathcal{D}_{m+1} \leftarrow \mathcal{D}_m \cup \mathcal{D}_{new}$），然后**重新在扩增的数据集上训练模仿学习（IL）模型**，以防止策略分布偏移并保持扩散模型的多模态表达能力 。
3. **一致性模型蒸馏 (Consistency Distillation)**： 为了将 $K$ 步的生成压缩为 $1$ 步部署，模型同时维护一个 Consistency Model 学生网络 $C_w$。在 PPO 微调 Diffusion 老师的同时，加入蒸馏损失：
	    标准的 On-policy 强化学习。策略直接在环境中与物理世界交互，利用 GAE 实时计算优势函数 $A^{on}_t$ 。因为之前的离线迭代已经把成功率推到了很高（例如 90%+），此阶段的 Rollout 主要是为了修正那些在离线数据中罕见的“长尾失败”情况，也就是最后的“微调” 。
    $$\mathcal{L}_{total} = \mathcal{L}_{RL} + \lambda_{CD} \cdot \mathbb{E} \left[ \| [cite_start]C_w(x^\tau, \tau) - \text{sg}[\pi_\theta(x^\tau, \tau \to 0)] \|_2^2 \right]$$
    
    _这里用了 Stop-Gradient (`sg`)，确保教师模型 $\pi_\theta$ 能专心通过 RL 变强，而学生网络只需负责“克隆”教师的输入输出映射。_
    

**关键工程 Trick**：

- **冻结编码器防止灾难性遗忘**：在离线 RL 时，固定从 IL 中预训练的视觉编码器 $\phi^{IL}$，只更新任务特定的头部，保证了表征的稳定性。
- **引入 VIB 与重构损失**：在可以微调特征提取的在线阶段，加入了 $\mathcal{L}_{recon}$ (点云 Chamfer 距离) 和 $\mathcal{L}_{KL}$ (变分信息瓶颈)，以此维持特征的三维空间一致性。

### 3.5 核心伪代码

```python
# Denoising Sub-MDP PPO (核心 tensor ops)
def ppo_denoising_update(obs, policy, critic, noise_sched, K, phase="online"):
    a_noisy = torch.randn(B, action_dim)          # a^{τ_K} ~ N(0,I)
    log_probs = []
    for k in reversed(range(K)):                   # K 步 DDIM 去噪
        tau = noise_sched.tau[k]
        eps_pred = policy.eps_net(a_noisy, tau, obs)  # ε_θ(x_t, t)
        alpha_bar = noise_sched.alpha_bar[tau]
        alpha_bar_prev = noise_sched.alpha_bar[tau - 1]
        x0_hat = (a_noisy - (1 - alpha_bar).sqrt() * eps_pred) / alpha_bar.sqrt()
        mu = alpha_bar_prev.sqrt() * x0_hat \
             + (1 - alpha_bar_prev - sigma_k**2).sqrt() * eps_pred
        sigma_k = tau.float().clamp(min=0.01, max=0.8)  # 截断方差
        a_next = mu + sigma_k * torch.randn_like(mu)
        log_probs.append(-0.5 * ((a_next - mu) / sigma_k).pow(2).sum(-1)
                         - sigma_k.log().sum())
        a_noisy = a_next
    # Task-level advantage → 广播至所有 K 步
    if phase == "offline":
        A = critic.q(obs, a_next) - critic.v(obs)  # IQL advantage
    else:
        A = critic.gae(obs, a_next)                 # GAE advantage
    total_logp = torch.stack(log_probs).sum(0)      # 合并 K 步对数概率
    ratio = (total_logp - total_logp_old.detach()).exp()
    loss = -torch.min(ratio * A,
                      ratio.clamp(1 - eps, 1 + eps) * A).mean()
    return loss

# 一致性蒸馏 (交替更新)
def consistency_distill(teacher, student, a_noisy, tau):
    with torch.no_grad():
        target = teacher.denoise_to_zero(a_noisy, tau)   # sg[π_θ(x^τ, τ→0)]
    pred = student(a_noisy, tau)                         # C_w(x^τ, τ)
    return F.mse_loss(pred, target)
```

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
- **终极可靠性**：在七个实机任务中，纯 IL (DP3) 只有 70.6% 的平均成功率。RL-100 的离线层将其拔高到 91.1%，而最终加上在线层后，达到了惊人的 100% (400/400 测试均成功)。
- **高频与低延迟**：通过蒸馏，一致性模型版本 (RL-100 CM) 将推理帧率从 30 Hz (基于 DDIM) 提升到了 **378 Hz**，同时依然维持了 100% 成功率。 推理时间的骤降（例如桔子榨汁任务每回合从 10.6s 降至 9.2s）使其运行效率直接超越了人类专家。
### 鲁棒性
- 环境/动力学偏移下 ~90% 零样本迁移
- 积极人为干扰下 ~95% 保持
- Few-shot 适应新变体 86.7%

### Ablation 因果链

| 去掉组件 | SR 变化 | 因果机制 |
|---------|---------|--------|
| 去掉在线 RL 阶段 | 100% → 91.1% | 离线数据无法覆盖长尾失败场景（如罕见物体姿态），在线交互提供分布外纠正信号 |
| 去掉离线 RL 阶段 | 91.1% → 70.6% (IL only) | 纯 IL 受限于示教者技能水平（模仿天花板），离线 RL 通过 IQL 优势重加权突破上限 |
| 去掉一致性蒸馏 | SR 不变但延迟 12× | DDIM K 步推理 (30Hz) → 单步一致性模型 (378Hz)；高频任务（如动态推）必须单步 |
| 去掉方差截断 ($\sigma_{min}$=0) | SR 显著下降 | 去噪末期退化为确定性映射 → 对数似然无定义 → PPO 梯度消失 → 无法探索 |
| 去掉 OPE 门控 | 安全风险 | 无离线评估直接部署 → 劣化策略损坏机器人；AM-Q 门控确保单调改进 |
| 冻结编码器 → 解冻 | 离线 SR 下降 | 离线数据有限，视觉编码器在 RL 梯度下遗忘 IL 阶段习得的空间表征 → 灾难性遗忘 |

## 5. 批判性分析 (Critical Analysis)

### 5.0 深层机制解析（来自深度讨论）

**为什么 PPO（On-policy 算法）能用于离线阶段？**
1. **起点锚定**：IL 预训练后 $\pi_\theta \approx \pi_\beta$（行为策略）
2. **IQL 安全评估**：Critic 只在数据集中真实存在的 $(s,a)$ 上计算优势，避免 OOD 高估
3. **Clip = 隐式保守正则**：$\text{clip}(r, 1-\epsilon, 1+\epsilon)$ 限制新策略偏离旧策略 → 旧策略紧贴数据分布 → 新策略被"软锁死"在数据流形上

**$\epsilon$-prediction vs $x_0$-prediction 的结构化探索**：
- $\hat{x}_0 = \frac{x_t - \sqrt{1-\bar{\alpha}_t}\epsilon_\theta}{\sqrt{\bar{\alpha}_t}}$，乘子 $\frac{1}{\sqrt{\bar{\alpha}_t}}$ 在去噪早期（$\bar{\alpha}_t$ 小时）极大
- 结果：$\epsilon$-prediction 在去噪早期自带方差放大效应 → **宏观探索（跨模态跳跃）**
- 去噪后期：$\bar{\alpha}_t \to 1$，乘子缩小 → **微观调整（精细 1° 角度修正）**
- 这种"从大到小"的结构化探索是 $x_0$-prediction（方差恒定、探索平坦）所不具备的

**Consistency Model 不会"学到平均值"**：
- CM 输入包含纯噪声 $a^{\tau_K} \sim \mathcal{N}(0,I)$ — 充当**隐变量模式选择器**
- 不同初始噪声 → Probability Flow ODE 落入不同山谷 → 不同动作模态
- 蒸馏 Loss 中 CM 和 Diffusion 老师接收**相同的初始噪声** → 学到的是确定性的噪声→动作映射
- PPO 梯度只更新 Diffusion 老师 $\pi_\theta$，CM 通过 stop-gradient 同步跟踪

**网络如何用同一套权重处理 K 种不同意义的去噪**：
- 时间步 $\tau_k$ 通过正弦位置编码 → MLP → 注入每层隐藏层（AdaGN/门控）
- 虽然权重相同，但时间步特征激活不同神经元通路
- 网络只输出预测噪声 $\epsilon_\theta$，均值 $\mu_\theta$ 由闭式解计算；方差 $\sigma_{\tau_k}^2$ 由调度表预设（不需网络预测）

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
