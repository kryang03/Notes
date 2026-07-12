---
tags:
  - paper
  - reinforcement-learning
  - diffusion-policy
  - real-world-rl
  - manipulation
  - offline-to-online-rl
aliases:
  - RL-100
paper-year: 2025
read-date: 2026-06-25
venue: arXiv
paper-pdf: "[[Papers/RL-100: Performant Robotic Manipulation with Real-World.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[ControlTheory]]"
  - "[[EmbodiedAI]]"
  - "[[Diffusion Policy: Visuomotor Policy]]"
  - "[[WMPO - World Model-based Policy Optimization for VLA]]"
---

# RL-100: Performant Robotic Manipulation with Real-World Reinforcement Learning

> [!abstract] 核心贡献
> RL-100 是一个真实机器人扩散策略后训练框架：先用 teleoperation 做 diffusion policy imitation learning，再用 OPE-gated iterative offline RL 在不断扩张的真实 rollout buffer 上保守改进，最后用少量 online PPO 修补长尾失败，并通过 consistency distillation 把多步 DDIM 策略压成单步高频控制器；在七个真实评估任务/子任务上达到 DDIM 400/400 与 CM 500/500，总计 900/900 成功。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — 核心是 offline-to-online RL：离线阶段用 IQL-style $Q-V$ advantage，在线阶段用 GAE，并通过 PPO clipping 保守更新。
> - [[StochasticProcess]] — diffusion denoising 被建模为每个环境动作内部的 K-step sub-MDP；只有 $\sigma_{\tau_k}>0$ 时 Gaussian sub-policy 的 log-likelihood 才合法。
> - [[Diffusion Policy: Visuomotor Policy]] — RL-100 不是替代 Diffusion Policy，而是把 diffusion action sampler 变成可被 policy gradient 微调的策略。
> - [[ControlTheory]] — single-step vs action-chunk control、consistency model 单步推理、30Hz/100Hz+ 控制频率，都是部署级控制约束，而非单纯算法指标。
>
> **核心技术**: Denoising Sub-MDP, PPO over Diffusion Steps, Iterative Offline RL, AM-Q OPE Gate, Online GAE Fine-tuning, Consistency Distillation, Variance Clipping

> [!note] 簇内坐标与暗线（模仿学习 · 数据生成 · 真机 RL · 人机协作）
> **簇内互链（Delta）**
> - vs [[SERL - A Software Suite for Sample-Efficient Robotic Reinforcement Learning|SERL]] / [[HIL-SERL - Precise and Dexterous Robotic Manipulation via Human-in-the-Loop Reinforcement Learning|HIL-SERL]]：都真机 RL 收口；RL-100 把 diffusion 去噪链当 **denoising sub-MDP** 做 PPO + offline→online + 一致性蒸馏，**无需人类在线**，SERL/HIL-SERL 是 off-policy RLPD（+人类纠正）。
> - vs [[RLT - Precise Manipulation with Efficient Online RL Tokens|RLT]]：都在生成式策略上做在线 RL；RL-100 **微调整个 diffusion 去噪链**，RLT **冻结 VLA 只学残差 token**（轻量 actor-critic，15 分钟）。
> - vs [[ACT - Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware|ACT]]：RL-100 把 chunked (diffusion) action 接入真机 RL，**突破 ACT 的 imitation ceiling**。
>
> **Foundation 精确锚点**（已 grep 验证）
> - [[ReinforcementLearning#9.3 真机高效 RL：把"模仿×强化"缝合线收口|RL §9.3]] — IL→Offline→Online 三阶段是"模仿×强化"缝合的完整迁移路径（§9.3 已点名 RL-100）。
> - [[ReinforcementLearning#10.1 扩散策略：多峰分布的终极解（兑现 §5.1.2 的伏笔）|RL §10.1]] — RL-100 = **reward-aligned diffusion prior**，兑现"扩散策略被 RL 微调"的伏笔。
>
> **暗线**：**模仿×强化缝合线** §9.3 / §10.1 节点；**POMDP→belief→latent**——去噪 latent 序列 + 3D point cloud 是 belief 的隐空间近似（$\sigma_{\tau_k}>0$ 才有 log-likelihood）。

## 0. 阅读定位与范本价值

RL-100 是 VLA/robot policy 后训练谱系中的“真机 RL 强证据”论文。它和 WMPO 的区别很尖锐：

| 路线 | Rollout 从哪里来 | Reward/advantage 从哪里来 | 风险 |
|------|------------------|---------------------------|------|
| RL-100 | 真实机器人，先离线 buffer 后在线交互 | IQL/OPE/GAE + 人类稀疏成功信号 | 真机成本、安全、reset、任务专化 |
| WMPO | pixel world model imagined trajectories | reward model + GRPO group advantage | model exploitation、reward hacking |
| RECAP/DexHiL | 真实 experience / human correction | correction/preference/intervention weighting | 人类介入成本 |

这篇对知识库的价值不只是“100% 成功率”，而是它给出了一个可复用的算法模板：**怎样把扩散策略的 K 步去噪过程改写成可做 PPO 的 sub-MDP，并用离线到在线的训练预算分配把真机风险压到可接受范围。**

最低标准对齐：

| 四支柱 | 本文必须回答的具体问题 |
|--------|------------------------|
| 逻辑与价值 | 为什么纯 IL 有 imitation ceiling？为什么真实 RL 能突破但必须被离线/OPE/方差/蒸馏约束包起来？ |
| 原理与理论 | DDIM 去噪如何变成 Gaussian sub-policy？为什么 $\sigma>0$ 是 PPO log-likelihood 的必要条件？环境 advantage 如何广播到 K 个 denoising steps？ |
| 实验与验证 | 70.6→91.1→100 的三阶段提升是否对应论文故事？900/900 是怎么组成的？zero/few-shot/perturbation/efficiency 是否支持部署级主张？ |
| 未来与结合 | 对 WMTS/灵巧手，哪些部分可直接复用，哪些必须换成 tactile/contact reward、ensemble safety、actuator-aware controller？ |

## 1. 问题设定与动机

### 1.1 一句话核心

RL-100 从 diffusion imitation policy 出发，把每个动作的 denoising chain 当成一个内部 sub-MDP，用 PPO-style objective 在离线和在线阶段统一优化真实机器人成功率、效率和鲁棒性，再用 consistency model 消除多步 diffusion 的部署延迟。

### 1.2 直观隐喻

IL 像跟着师傅学动作：起步稳，但上限被师傅的速度、保守性和偶发错误限制。真实 RL 像自己上机练习：可以超过师傅，但盲目试错会摔坏设备。RL-100 的工程智慧是先让机器人在已有 buffer 里“复盘练习”，只在 OPE gate 认为策略变好时再上机，最后用少量在线练习修补最难的失败边界。

这个隐喻可被实验检验：如果 iterative offline RL 是主力，那么 success rate 应该从 IL 的中等水平提升到接近完美；如果 online RL 是最后一公里，那么它的增益应集中在 90%+ 后的 rare failures；如果 consistency distillation 只负责部署延迟，那么它应保持成功率但显著提高频率。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验/能力 | 关键局限 |
|----------|---------------------|----------|
| Diffusion Policy / DP3 imitation | 多模态动作分布、人类示教策略 | 受示教者 skill 和 conservatism 限制；不能直接优化 success/time/robustness |
| Sim-to-Real RL | 大量仿真探索 | 视觉和动力学 gap；任务/物体/接触校准成本高 |
| Naive real-world RL | 真实 reward，能突破 IL | 样本低效、硬件风险高、reset/安全/人工审批成本大 |
| SERL / HIL-SERL | off-policy learning + reset + human intervention | 常依赖 action-space shaping 和较低维/短 horizon 任务；对 full SE(3)、deformable、dynamic tasks 不够通用 |
| DPPO-style diffusion RL | diffusion policy 可被 RL 优化 | 真实部署还需要 offline-to-online budget、OPE gate、低延迟蒸馏和表示稳定 |

RL-100 的 Delta：**把扩散策略 RL 从一个算法组件，推进成“IL → OPE-gated iterative offline RL → online fine-tuning → consistency deployment”的真机系统。**

### 1.4 论文贡献

1. 将 diffusion denoising chain 建模为每个环境 timestep 内部的 K-step sub-MDP，使 PPO 可作用于 denoising sub-policies。
2. 离线/在线共享 PPO-style objective，但 advantage 来源不同：offline 用 IQL-style $Q-V$，online 用 GAE。
3. 用 AM-Q OPE gate 接受/拒绝离线候选策略，避免直接部署退化策略。
4. 迭代数据扩张：offline RL 改进策略 → rollout 收集新数据 → IL retraining 吸收新数据并保持多模态。
5. 用 consistency distillation 把 K-step DDIM 压成 one-step policy，实测 Skip-Net CM 378 Hz。
6. 在真实任务上展示部署级可靠性：900/900，mall juicing 约 7 小时零失败，扰动下平均 95%。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $s_t$ | environment state | MDP 抽象 | 通常不可直接观测 | 真实机器人状态 | 和 diffusion timestep $t$ 容易混；论文后面用 $\tau_k$ 区分 |
| $o_t$ | RGB 或 3D point cloud | 相机/点云观测 | encoder 可训练或冻结 | 视觉输入 | RL-100 真机主要用 3D point clouds，2D 只是支持/仿真 ablation |
| $q_t$ | proprioception | robot sensors | 输入 | 关节/夹爪等本体状态 | 对灵巧手需扩展为触觉、actuator state、latency belief |
| $c_t$ | conditioning vector | 最近 $n_o$ 帧 $\phi(o_i,q_i)$ 拼接 | 是 | diffusion policy 条件 | 通常 $n_o=2$ |
| $a_t^{\tau_0}$ | clean action/action chunk | policy 最终输出 / demonstration target | action head 带梯度 | 环境执行动作 | single-step 或 chunk，chunk size 通常 8-16 |
| $a_t^{\tau_k}$ | noisy action at denoising step | diffusion forward/noise sampling | 是 | denoising sub-MDP state 的核心变量 | 上标 $\tau_k$ 是 diffusion index，不是幂 |
| $\epsilon_\theta$ | predicted noise | denoiser output | 是 | DDPM/DDIM 参数化 | RL-100 发现 $\epsilon$-prediction 比 $x_0$-prediction 更利于 RL 探索 |
| $\hat x_0$ | predicted clean sample | DDIM closed form | 是 | 从 noisy action 估计 clean action | 早期 $\bar\alpha_t$ 小时，$\epsilon$ 参数化会放大 variance |
| $\mu_\theta$ | DDIM Gaussian mean | closed-form from $\epsilon_\theta$ | 是 | sub-policy mean | 网络不直接输出 mean，而是通过 DDIM 公式计算 |
| $\sigma_{\tau_k}$ | denoising variance | schedule / clipped | 否 | sub-policy stochasticity | $\sigma=0$ 时 log-likelihood 不存在，不能用于 PPO |
| $u_k=a^{\tau_{k-1}}$ | sub-MDP action | denoising step sample | 是 | 从 noisy action 采样更干净 action | 不是机器人动作，是内部去噪动作 |
| $A_t$ | environment-level advantage | offline: IQL $Q-V$；online: GAE | critic 参数带梯度，policy update 视为权重 | 当前环境动作好坏 | 同一个 $A_t$ 被广播到所有 K 个 denoising steps |
| $r_k(\pi)$ | importance ratio | PPO update | 是 | 新旧 denoising sub-policy 概率比 | 每个 denoising step 单独 ratio |
| $\hat J_{\mathrm{AM-Q}}$ | OPE score | learned transition + Q | 用于 gate | 判断候选策略是否可部署 | 是保守安全阀，不是真实环境 guarantee |
| $C_w$ | consistency model | student policy | 是 | 单步噪声到动作映射 | 通过 stop-gradient 跟踪 diffusion teacher |

### 2.2 Diffusion Policy 从监督学习开始

Diffusion Policy 对动作 $x_0$ 加噪：

$$
x_t=\sqrt{\bar\alpha_t}x_0+\sqrt{1-\bar\alpha_t}\epsilon,\qquad
\epsilon\sim\mathcal{N}(0,I).
$$

denoiser 训练目标是预测噪声：

$$
\mathcal{L}_{\mathrm{IL}}(\theta)
=
\mathbb{E}_{x_0,t,\epsilon}
\left[
\|\epsilon-\epsilon_\theta(x_t,t,c)\|_2^2
\right].
$$

在机器人策略中，$x_0$ 是动作或 action chunk，condition $c_t$ 来自最近视觉/本体观测：

$$
c_t=[\phi(o_i,q_i)]_{i=t-n_o+1}^{t}.
$$

这一步只是 imitation learning。它能学到人类先验，但 objective 仍是“像示教动作”，不是“更快、更稳、更鲁棒地完成任务”。

### 2.3 DDIM 去噪如何变成 sub-policy

给定 noisy action $x_t$，DDIM 先估计 clean sample：

$$
\hat x_0(x_t,t)
=
\frac{x_t-\sqrt{1-\bar\alpha_t}\epsilon_\theta(x_t,t)}
{\sqrt{\bar\alpha_t}}.
$$

从 diffusion time $t$ 跳到更早的 $m<t$，DDIM mean 是：

$$
\mu_\theta(x_t,t\to m)
=
\sqrt{\bar\alpha_m}\hat x_0(x_t,t)
+
\sqrt{1-\bar\alpha_m-\sigma_{t\to m}^2}\,
\epsilon_\theta(x_t,t).
$$

随机 DDIM update：

$$
x_m=\mu_\theta(x_t,t\to m)+\sigma_{t\to m}\epsilon_{t\to m},
\qquad \epsilon_{t\to m}\sim\mathcal{N}(0,I).
$$

只要 $\sigma_{t\to m}>0$，这就是一个 Gaussian sub-policy：

$$
\pi_\theta(x_m\mid x_t,t\to m)
=
\mathcal{N}\left(\mu_\theta(x_t,t\to m),\sigma_{t\to m}^2I\right).
$$

对应 log-likelihood：

$$
\log\pi_\theta(x_m\mid x_t,t\to m)
=
-
\frac{1}{2\sigma_{t\to m}^2}
\|x_m-\mu_\theta(x_t,t\to m)\|^2
+C.
$$

关键约束：

$$
0\le \sigma_{t\to m}\le \sqrt{1-\bar\alpha_m}.
$$

如果 $\sigma_{t\to m}=0$，transition 退化为 deterministic Dirac mapping，Gaussian density 不存在，PPO 的 log-prob ratio 也就不合法。这就是 RL-100 做 variance clipping 的理论原因。

### 2.4 Denoising sub-MDP

对每个环境 timestep $t$，从初始噪声 $a_t^{\tau_K}\sim\mathcal{N}(0,I)$ 开始，经过 K 步去噪：

$$
a_t^{\tau_{k-1}}
\sim
\pi_\theta(\cdot\mid a_t^{\tau_k},\tau_k,o_t),
\qquad k=K,\dots,1.
$$

把它写成 sub-MDP：

| sub-MDP 元素 | 定义 |
|--------------|------|
| initial state | $s_K=(a^{\tau_K},\tau_K,o)$ |
| state | $s_k=(a^{\tau_k},\tau_k,o)$ |
| action | $u_k=a^{\tau_{k-1}}$ |
| transition | $s_{k-1}=(u_k,\tau_{k-1},o)$ |
| reward | 中间为 0，最终 $a^{\tau_0}$ 与真实环境交互后得到 $R_t$ |

环境奖励只在 clean action 执行后出现，但该动作由 K 个 denoising sub-actions 共同生成。因此 RL-100 把同一个 environment-level advantage $A_t$ 分配给所有 denoising steps。

### 2.5 PPO objective 如何作用到 K 个去噪步

第 $i$ 轮 PPO 中，RL-100 对每个 denoising step 计算 ratio：

$$
r_k(\pi)
=
\frac{\pi(a^{\tau_{k-1}}\mid s_k)}
{\pi_i(a^{\tau_{k-1}}\mid s_k)}.
$$

统一目标：

$$
J_i(\pi)
=
\mathbb{E}
\left[
\sum_{k=1}^{K}
\min\left(
r_k(\pi)A_t,\,
\operatorname{clip}(r_k(\pi),1-\epsilon,1+\epsilon)A_t
\right)
\right].
$$

这里最重要的是 $A_t$ 的来源：

| 阶段 | 数据来源 | advantage | 作用 |
|------|----------|-----------|------|
| Offline RL | 固定数据集 $D_m$ | $A_t^{\mathrm{off}}=Q_\psi(s_t,a_t)-V_\psi(s_t)$，IQL-style | 不与环境交互，保守重加权已有数据中的动作 |
| Online RL | 当前策略真实 rollout | $A_t^{\mathrm{on}}=\operatorname{GAE}(\lambda,\gamma;r_t,V_\psi)$ | 修补离线数据覆盖不到的长尾失败 |

离线阶段看似“用 PPO 做 offline RL”很危险，但 RL-100 用三层约束把它锁在数据流形附近：

1. 起点是 IL policy，接近行为数据。
2. advantage 来自 IQL-style critic，只评估数据中的 $(s,a)$。
3. PPO clipping 限制候选策略远离旧策略。

### 2.6 OPE gate 与 iterative data expansion

离线更新得到候选策略后，RL-100 不直接部署，而是用 AM-Q 做 offline policy evaluation：

$$
\hat J_{\mathrm{AM-Q}}(\pi)
=
\mathbb{E}_{(s,a)\sim(\hat T,\pi)}
\left[
\sum_{t=0}^{H-1}Q_\psi(s_t,a_t)
\right].
$$

只有当：

$$
\hat J_{\mathrm{AM-Q}}(\pi)-\hat J_{\mathrm{AM-Q}}(\pi_i)
\ge
\delta
$$

时才接受候选策略。论文实践中设：

$$
\delta=0.05|\hat J_{\mathrm{AM-Q}}(\pi_i)|.
$$

接受后部署策略收集新 rollout，合并到数据集，再重新做 IL：

$$
D_{m+1}=D_m\cup D_{\mathrm{new}},
\qquad
\pi_{m+1}^{\mathrm{IL}}=\operatorname{BC}(D_{m+1}).
$$

重新 IL 的作用不是倒退，而是把 human demos 和 RL-improved rollouts 蒸馏回一个稳定、多模态的 diffusion policy，缓解纯 RL update 的分布漂移。

### 2.7 Consistency distillation

多步 diffusion 推理慢，部署时尤其伤害 dynamic tasks。RL-100 训练 consistency student $C_w$：

$$
\mathcal{L}_{\mathrm{CD}}
=
\mathbb{E}
\left[
\left\|
C_w(x^\tau,\tau)
-
\operatorname{sg}\left[\Psi_\phi(x^\tau,\tau\to0)\right]
\right\|_2^2
\right],
$$

其中 $\Psi_\phi$ 是 K-step diffusion teacher，$\operatorname{sg}$ 表示 stop-gradient。总目标：

$$
\mathcal{L}_{\mathrm{total}}
=
\mathcal{L}_{\mathrm{RL}}
+\lambda_{\mathrm{CD}}\mathcal{L}_{\mathrm{CD}}.
$$

推理时：

$$
a^{\tau_0}=C_w(a^{\tau_K},\tau_K\mid o).
$$

这一步不是为了提高最终 success rate，而是为了把决策模型从控制瓶颈中移除。论文报告 Skip-Net CM 3.9M 参数达到 378 Hz，U-Net CM 39.2M 参数达到 133 Hz，而 DPPO 约 30 Hz、DSRL 约 35 Hz。

### 2.8 Variance clipping 与 $\epsilon$-prediction

RL-100 约束 stochastic DDIM variance：

$$
\tilde\sigma_k=\operatorname{clip}(\sigma_k,\sigma_{\min},\sigma_{\max}),
$$

实践中 $\sigma_{\min}=0.01,\sigma_{\max}=0.8$ 常用于 Adroit/MuJoCo/real single-action，$\sigma_{\max}=0.1$ 用于 Meta-World 和 real chunk-action。

逻辑：

- $\sigma$ 太大：早期探索破坏性强，可能产生 OOD 动作和安全问题。
- $\sigma$ 太小：后期 deterministic，log-likelihood 退化，PPO 没有有效探索空间。

论文还比较 $\epsilon$-prediction 与 $x_0$-prediction。由于：

$$
\hat x_0=
\frac{x_t-\sqrt{1-\bar\alpha_t}\epsilon_\theta(x_t,t)}
{\sqrt{\bar\alpha_t}},
$$

reverse 早期 $\bar\alpha_t$ 小，$\epsilon$ prediction 会放大 $\hat x_0$ variance。监督学习中这可能是坏事；但在线 RL 中，它提供结构化探索。实测 Adroit-Door 上 $\epsilon$-prediction 最终成功率约 1.0，而 sample/$x_0$ prediction 约 0.6。

## 3. 训练、数据与实验

### 3.1 任务设置

| Task | Control mode | Embodiment | Modality / challenge |
|------|--------------|------------|----------------------|
| Dynamic Push-T | Single-step | UR5 + 3D-printed end-effector | moving goal pose, perturbations |
| Agile Bowling | Single-step | UR5 + 3D-printed end-effector | high-speed release timing |
| Pouring | Single-step | Franka + LeapHand | fluids/granular flow control |
| Dynamic Unscrewing | Action-chunk | Franka + LeapHand | precision assembly, torque/pose regulation |
| Soft-towel Folding | Action-chunk | xArm + Franka + Robotiq | deformable cloth, dual-arm coordination |
| Orange Juicing - Placing | Action-chunk | xArm + Robotiq | confined-space deformable manipulation |
| Orange Juicing - Removal | Action-chunk | xArm + Robotiq | slippery deformed orange in narrow cavity |

论文有时把 Orange Juicing 作为一个 task family，有时把 Placing/Removal 分开评估；900/900 是按 Table 3 的七个评估行加总。

### 3.2 主成功率结果

| Task | DP-2D | DP3 | Iterative Offline RL | Online RL (DDIM) | Online RL (CM) |
|------|-------|-----|----------------------|------------------|----------------|
| Dynamic Push-T | 40 (20/50) | 64 (32/50) | 90 (45/50) | 100 (50/50) | 100 (50/50) |
| Agile Bowling | 14 (7/50) | 80 (40/50) | 88 (44/50) | 100 (50/50) | 100 (50/50) |
| Pouring | 42 (21/50) | 48 (24/50) | 92 (46/50) | 100 (50/50) | 100 (50/50) |
| Soft-towel Folding | 46 (23/50) | 68 (34/50) | 94 (47/50) | 100 (50/50) | 100 (250/250) |
| Dynamic Unscrewing | 82 (41/50) | 70 (35/50) | 94 (47/50) | 100 (50/50) | 100 (50/50) |
| Orange Juicing - Placing | 78 (39/50) | 88 (44/50) | 94 (47/50) | 100 (100/100) | 100 (50/50) |
| Orange Juicing - Removal | 48 (24/50) | 76 (38/50) | 86 (43/50) | 100 (50/50) | - |
| Mean | 50.0 | 70.6 | 91.1 | 100.0 | 100.0 over six CM tasks |

因果解释：

- DP3 70.6 vs DP-2D 50.0：3D point cloud representation already matters, especially for contact/geometry.
- Iterative Offline RL 91.1：最大提升来自离线后训练，而不是在线硬冲。Pouring 48→92，Unscrewing 70→94，是最强证据。
- Online DDIM 400/400：在线阶段把 91.1 推到 100，符合“last-mile reliability”叙事。
- CM 500/500：蒸馏保持 100% 成功率，并在 Soft-towel Folding 做到 250/250 consecutive trials。
- CM 未评估 Juicing-Removal：原因是 IK-induced pose discontinuities 在 tight/slippery contact 中会被 one-step CM 的 noise sensitivity 放大，出于安全未测。这是论文主动暴露的工程边界。

900/900 的组成：

$$
400/400\ \text{(DDIM over seven rows)}
+
500/500\ \text{(CM over six rows)}
=
900/900.
$$

### 3.3 Zero-shot / few-shot / disturbance

Zero-shot dynamics/environment shift：

| Variation | Success |
|-----------|---------|
| Pouring (Water) | 90 |
| Push-T (Changed surface) | 100 |
| Push-T (Interference Objects) | 80 |
| Bowling (Changed Surface) | 100 |
| Folding (Unseen shape) | 80 |
| Average | 90.0 |

Few-shot adaptation after 1-3 hours：

| Variation | Success |
|-----------|---------|
| Pour (New Container) | 60 |
| Folding (Changed Object) | 100 |
| Bowling (Inverted pin) | 100 |
| Average | 86.7 |

Physical disturbances：

| Task / disturbance | Success |
|--------------------|---------|
| Folding Stage 1: Grasping | 90 |
| Folding Stage 2: Pre-folding | 90 |
| Unscrewing | 100 |
| Push-T whole stage | 100 |
| Average | 95.0 |

因果解释：

- zero-shot 90% 说明 RL-100 不是只记住 nominal initial positions；但 Push-T interference 80 和 folding unseen 80 也说明分布外鲁棒性不是完美。
- few-shot Pour new container 只有 60，说明几何/容器变化仍可能需要更多适应，不应把 86.7 平均理解成“任意新变体都稳”。
- disturbance 95% 强化了 closed-loop RL 的价值：真实扰动恢复不是 IL demos 中容易覆盖的部分。

### 3.4 效率与部署

| 指标 | 数字 |
|------|------|
| Orange Juicing - Placing wall-clock | CM 9.2s vs DDIM 10.2s vs DP-2D 10.6s |
| Dynamic Push-T throughput | RL-100 DDIM 20 successful episodes per unit time vs expert 17 vs beginners 13 |
| Dynamic Push-T all-trial episode length | DP-2D 822 → DP3 658 → RL-100 Offline 382 → RL-100 DDIM 322 steps |
| Mall juicing | zero-shot shopping mall deployment, about 7 hours without failure |
| Online RL convergence | Agile Bowling reaches consistent 100% after about 120 on-policy episodes |
| Human demo budget | average 115 demos / 1.8 h per task |
| Iterative offline rollout budget | average 566 episodes / 6.5 h per task |
| Online rollout budget | average 434 episodes / 5.6 h per task |
| Total data collection | 804 human episodes / 12.5 h; 3965 offline rollouts / 45.3 h; 3037 online rollouts / 39.5 h |

这个表是对“真实世界 RL 可行”的重要校准：它确实比大规模人工示教更省人，但不是零成本。平均每任务仍有约 1000 条自主 rollout 和数小时真机时间。

### 3.5 Simulation 与 ablation

Simulation 结果支持泛化到标准 RL benchmarks：

- MuJoCo locomotion：HalfCheetah-medium-v2 return 约 10,000，比 DPPO 4,500 高 2.2×，比 DSRL 3,000 高 3.3×。
- Adroit：Door/Hammer 接近 100% success，DPPO 在约 0.9，ReinFlow 在 Hammer 低于 0.6。
- Meta-World Peg-Insert-Side：RL-100 稳定 1.0，ReinFlow 不超过 0.2。

关键 ablations：

| Ablation | 结果/趋势 | 机制 |
|----------|-----------|------|
| 2D vs 3D | 3D learns faster and higher on Adroit Door | point cloud ROI/crop 隔离 handle/contact surfaces，credit assignment 更干净 |
| diffusion noise clipping | moderate clip 0.8 best；0.1 under-explores；no clip oscillates | 平衡探索与安全 |
| CM vs DDIM | learning curves / final success nearly identical, CM K× faster | distillation 保留 teacher 行为，消除多步 latency |
| ReconVIB vs no ReconVIB / frozen encoder | Recon+VIB 最稳；无正则或冻结都差 | RL fine-tuning 中 representation 需要适度适应又不能漂移 |
| $\epsilon$ vs $x_0$ | $\epsilon$ 約 1.0 success vs $x_0$ 約 0.6 | $\epsilon$ 参数化提供结构化探索，避免 premature convergence |

## 4. 核心洞见

### 4.1 论文真正的 insight

RL-100 的真正 insight 是：**扩散策略的去噪过程本身就是一个可优化的短 horizon stochastic policy，而不是只用于采样的黑盒。**

一旦把每个 denoising transition 写成 Gaussian sub-policy，PPO 就不再只对最终动作做粗粒度更新，而是可以把同一个 task advantage 注入到生成动作的所有内部步骤。这样 diffusion policy 的多模态生成能力和 RL 的任务优化目标被接在了一起。

### 4.2 为什么有效

有效性来自四层防护和增益：

1. **IL base**：人类先验给出低风险起点。
2. **Iterative offline RL**：用真实 rollout buffer 中的数据做大部分提升，减少在线风险。
3. **OPE gate + variance clipping**：防止退化策略和破坏性探索直接上机。
4. **Online + CM**：在线修补长尾失败，CM 把策略变成高频部署版本。

这不是单一算法胜利，而是“训练预算、策略表示、评价 gate、控制延迟”共同对齐。

### 4.3 什么时候会失效

1. **奖励难以自动给出**：论文需要人类 sparse success signals when needed；对复杂长程任务，奖励标注本身可能成为瓶颈。
2. **reset/安全成本高**：真实 RL 仍需要多次 rollout、reset、审批；任务越危险成本越高。
3. **状态部分可观测**：无触觉/力反馈的任务中，contact hidden state 可能让 IQL/GAE advantage 噪声变大。
4. **任务专化**：目前是按任务训练/评估，不是一个跨任务 VLA foundation policy。
5. **CM 对不连续动作敏感**：Juicing Removal 未测 CM 就是边界案例。

## 5. 替代方案与理论局限

### 5.1 理论维度

把环境 advantage $A_t$ 广播到 K 个 denoising steps 是一种 practical credit assignment：

$$
A_t \rightarrow \{a^{\tau_K}\to a^{\tau_{K-1}}\to\dots\to a^{\tau_0}\}.
$$

它合理，因为所有 denoising steps 共同产生最终动作；但它也粗糙，因为无法区分哪一个去噪 step 对成功/失败贡献最大。对接触丰富任务，可能需要更细的 denoising-step diagnostic 或 action-dimension-wise credit。

### 5.2 算法维度

| 路线 | 相对 RL-100 的优势 | 相对 RL-100 的问题 |
|------|-------------------|-------------------|
| Pure IL / Diffusion Policy | 简单稳定，无真机探索风险 | imitation ceiling，无法优化部署指标 |
| WMPO | 用世界模型降低真机 rollout 成本 | model bias 和 reward model hacking |
| SERL/HIL-SERL | 成熟真机 RL 工具链，human correction 强 | 常有 action shaping / 任务范围限制 |
| Offline RL only | 真机风险低 | 难覆盖长尾失败，停在 90% 左右 |
| Online RL only | 最直接优化真实 reward | 样本贵且不安全，需要好初始化 |

### 5.3 工程与实验维度

1. 900/900 很强，但来自多个任务/策略版本合计；CM 未覆盖 Juicing Removal。
2. 平均每任务仍约 1.8h 人类示教 + 6.5h iterative rollout + 5.6h online rollout，不是“廉价到可忽略”。
3. 主要是任务专用策略，未来扩展到 multi-task VLA 仍是 future work。
4. 真实系统大量依赖工程限制、保守 operating limits、人工信号与 resets。
5. Pouring/Folding/Unscrewing 虽涉及 LeapHand/软物体/流体，但还不是动态 in-hand manipulation 或触觉密集 dexterity。

## 6. 对用户研究的启发

### 6.1 对 WMTS / 灵巧手的迁移

RL-100 对 WMTS 最直接的贡献是：如果 generalist policy 采用 Diffusion/Flow action head，那么 RL fine-tuning 不应只在 action output 上做黑盒 PPO，而应进入 denoising/generation process 本身。

| RL-100 组件 | WMTS 中的对应设计 | 修改原因 |
|-------------|------------------|----------|
| IL base | sim/PPO Oracle + human teleop + successful rollouts 初始化 generalist | 保留安全先验，避免真机盲探索 |
| Denoising sub-MDP PPO | 对 diffusion/flow generalist 的生成 steps 做 advantage-weighted update | 让 task reward 影响动作生成内部过程 |
| Offline IQL advantage | 用 replay buffer / world-model-validated rollouts 估计 $Q-V$ | 先用离线数据吃掉大部分提升 |
| AM-Q OPE gate | ensemble world model + conservative LCB gate | 对灵巧手必须显式估计 model uncertainty |
| Online GAE | 少量真实 LinkerHand rollout 修补失败边界 | 最后校准真实摩擦、延迟、触觉 |
| Consistency distillation | 多步 diffusion/flow → 单步或少步 high-frequency controller | 转笔需要低 latency，不能每步长 denoise |
| Recon/VIB | tactile/proprio/object-state reconstruction + information bottleneck | 防止 RL 梯度破坏接触表征 |

### 6.2 可验证实验建议

1. **Denoising sub-MDP on dexterous policy**  
   在仿真转笔中训练 diffusion action policy，然后比较 action-output PPO vs denoising-step PPO。若 denoising PPO 更稳定或更会保留多模态动作，应复用 RL-100 框架。

2. **Tactile/contact advantage**  
   不只用 terminal success，而加入 tactile slip、contact mode、object angular velocity progress reward。测试二值 reward vs tactile-shaped advantage 是否改善 credit assignment。

3. **Variance clipping sweep**  
   对手指动作设置不同 $\sigma_{\max}$。转笔中早期大探索可能直接丢笔，可能需要 phase-dependent clipping，而不是全程 0.8/0.1。

4. **CM safety check**  
   RL-100 的 CM 在 Juicing Removal 因不连续/滑腻接触未测。转笔也有快速接触切换，必须比较 DDIM、few-step sampler、CM 在真实触觉扰动下的失败模式。

5. **OPE gate with ensemble**  
   用 ensemble world model 评估候选策略，只有 LCB improvement 超过阈值才上真机。这里可把 Part A 的 MoDem/FOWM/SafeDreamer 线接进来。

### 6.3 不应过度外推的点

- RL-100 证明真实 RL 后训练可达部署级可靠性，但不是证明“纯真机 RL 可以随便做”。它靠的是 IL base、OPE、离线为主、保守探索和工程限制。
- 100% success 是任务 suite 内结果，不等于开放世界泛化。
- LeapHand 出现在 Pouring/Unscrewing 中，但不是高自由度 in-hand rotation；对 DNPM 仍需要额外实验。
- Consistency distillation 的单步策略可能放大动作不连续处的风险，不能无脑用于接触切换密集任务。

## 7. 与知识体系的联系

### 7.1 与 [[ReinforcementLearning]] 的联系

RL-100 是 offline-to-online PPO 的一个强工程化实例。它把：

$$
A^{\mathrm{off}}(s,a)=Q(s,a)-V(s)
$$

和：

$$
A^{\mathrm{on}}=\operatorname{GAE}(\lambda,\gamma;r,V)
$$

放进同一个 clipped surrogate。区别只在 advantage estimator，不在 policy objective。这种统一性非常适合 WMTS：先用离线/world-model数据保守更新，再用少量真实 rollout 做 GAE。

### 7.2 与 [[StochasticProcess]] 的联系

DDIM stochastic update 的 Gaussian interpretation 是全篇数学支点：

$$
\pi_\theta(x_m\mid x_t,t\to m)
=
\mathcal{N}(\mu_\theta,\sigma^2I).
$$

没有正方差，就没有 density；没有 density，就没有 policy gradient ratio。这个细节比“Diffusion + PPO”口号重要得多。

### 7.3 与 [[Diffusion Policy: Visuomotor Policy]] 的联系

Diffusion Policy 展示了动作分布建模优势；RL-100 展示了如何让这个分布模型被真实 reward 改写。可以理解为：

`Diffusion Policy = expressive action prior`

`RL-100 = reward-aligned diffusion action prior`

对 WMTS，前者解决动作多模态，后者解决如何突破 imitation/simulation ceiling。

### 7.4 与 WMPO 的联系

WMPO 和 RL-100 是同一目标的两端：

- RL-100：真实 rollout 昂贵但 reward 真实。
- WMPO：imagined rollout 便宜但 world/reward model 有偏。

WMTS 的合理路线可能是中间态：先用 ensemble world model 做 conservative imagined RL，再用 RL-100 式少量真实 online fine-tuning 校准最后一公里。

## References

- Lei et al., 2025. *RL-100: Performant Robotic Manipulation with Real-World Reinforcement Learning*.
- Chi et al., 2023. *Diffusion Policy: Visuomotor Policy Learning via Action Diffusion*.
- Ze et al., 2024. *3D Diffusion Policy*.
- Schulman et al., 2017. *Proximal Policy Optimization Algorithms*.
- Kostrikov et al., 2022. *Implicit Q-Learning*.
- Song et al., 2023. *Consistency Models*.
- Luo et al., 2024/2025. *SERL / HIL-SERL*.
