---
tags:
  - paper
  - reinforcement-learning
  - world-model
  - vla
  - embodied-ai
  - robotics
aliases:
  - WMPO
  - World Model-based Policy Optimization
paper-year: 2025
read-date: 2026-06-25
venue: arXiv
paper-pdf: "[[Papers/WMPO: World Model-based Policy Optimization for.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[RepresentationLearning]]"
  - "[[StochasticProcess]]"
  - "[[Diffusion Policy: Visuomotor Policy]]"
  - "[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation]]"
  - "[[DiWA- Diffusion Policy Adaptation with World Models]]"
---

# WMPO: World Model-based Policy Optimization for Vision-Language-Action Models

> [!abstract] 核心贡献
> WMPO 把 VLA 的 RL 后训练从真实机器人交互搬到一个经过 policy-behavior alignment 的像素空间视频世界模型中：用真实初始帧启动、用当前 VLA 采样 action chunk、用 world model 生成完整 trial、用二值 reward model 评估成功，再用 GRPO 在 imagined trajectories 上做 on-policy policy optimization。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#10.2 世界模型 RL：隐空间 vs 像素空间]] — WMPO 的核心取舍恰是"像素空间 vs 隐空间"：为复用 VLA 预训练视觉编码器，rollout observation 解码回像素域，而非 Dreamer 式 latent imagination。经典 Dyna / PPO clipped ratio / REINFORCE baseline-advantage 是其数学根。
> - [[WorldModels#4. 利用层：想象里"练策略"还是"规划动作"]] — WMPO 属"在想象里练策略"分支（imagined GRPO），而非 CEM/MPPI 式在想象里规划动作。
> - [[WorldModels#6.1 世界模型作安全调度器（Look-ahead Safety Filter）]] — reward model 判完整 trial 成败、dynamic sampling 过滤无信息组，本质是用 WM look-ahead 给 policy update 做筛选；但 WMPO 只有单 WM、无 ensemble，落到 **认知不确定性三用暗线** 就缺一条护栏（§5.2 指出需并入 ensemble epistemic 才能安全 Solve/Probe/Reject）。
> - [[StochasticProcess]] — action-conditioned video diffusion 近似 $p_\phi(I_{i:i+K}\mid I_{i-c:i},a_{i:i+K})$，noisy-frame conditioning 把条件分布扩宽到自回归会遇到的 noisy frames。
> - [[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器]] — pixel-space rollout 让 VLA 预训练视觉编码器继续在自己的输入域工作，避免 latent WM 与 VLA feature space 接口错位。
> - [[EmbodiedAI#1.3 三种动作输出范式（横向对比）]] — VLA 后训练从 imitation 走向 experience-driven / self-correction；WMPO 是 RECAP、DexHiL、RL-100、World4RL、DiWA 之间的一条世界模型路线。
>
> **核心技术**: Pixel-Space Video World Model, Policy Behavior Alignment, Imagined On-Policy GRPO, Dynamic Sampling, Noisy-Frame Conditioning, Frame-Level Action Control

## 0. 阅读定位与范本价值

这篇文章对当前知识库的价值，不在于它已经解决了 dexterous manipulation，而在于它把一个非常关键的论证闭环写清楚了：

1. VLA 通过 imitation learning 得到强先验，但它只会复制成功演示，缺少失败边界和 recovery 行为。
2. 真实世界 RL 可以补上失败学习，但对大模型策略而言太贵、太慢、太危险。
3. 如果有一个足够可信的 world model，就可以把 on-policy RL 的 rollout 成本从物理世界转移到模型世界。
4. 对 VLA 来说，world model 不能只输出某个内部 latent，因为 VLA 的视觉能力来自 web-scale image pretraining；rollout 必须回到像素域，才能被现有 VLA 直接消费。

因此 WMPO 的故事是：**不是“world model 替代环境”这个老命题本身新，而是“为 VLA 后训练选择 pixel-space world model，并用 policy behavior data 对齐失败分布，使 GRPO 可以在想象中做 on-policy 更新”这个组合新。**

最低标准对齐：

| 四支柱 | 本文必须回答的具体问题 |
|--------|------------------------|
| 逻辑与价值 | 为什么 VLA 的 bottleneck 是 failure distribution，而不是只缺更多 demonstration？为什么 pixel-space 是相对 latent world model 的关键 delta？ |
| 原理与理论 | 如何从 IL 的 covariate shift 推到 model-based RL，再推到 imagined GRPO？每个符号到底来自图像、语言、动作 chunk、world model、reward model 还是 policy update？ |
| 实验与验证 | MimicGen、generalization、real-world ALOHA 的数字是否真的证明“想象中的 on-policy RL”优于真实 GRPO/DPO？哪些关键模块没有被严格 ablate？ |
| 未来与结合 | 对 WMTS，哪些机制可迁移，哪些必须重做为 tactile/contact/proprioceptive、ensemble、不确定性约束的 semi-structured world model？ |

## 1. 问题设定与动机

### 1.1 一句话核心

WMPO 用一个 action-conditioned pixel video world model 生成当前 VLA 的 imagined rollouts，然后用 GRPO 从这些 rollouts 的成功/失败差异中训练 VLA，使策略获得 imitation learning 很难产生的 self-correction 行为。

### 1.2 直观隐喻

一个只看过标准答案的学生，遇到错误中间步骤时不知道如何补救；真实 RL 是让他在真实实验台上反复犯错，代价高；WMPO 是先训练一个足够像真实实验台的“视频实验室”，再让学生在这个实验室里从相同初始条件反复试错。关键要求是：这个视频实验室必须会复现学生自己的错误，而不是只会播放老师的成功演示。

这个隐喻可被 falsify：如果 world model 只在 expert/success distribution 上准确，而在 policy failure states 上失真，那么它给 GRPO 的 advantage 就会变成错误监督，训练会朝模型漏洞而不是真实 recovery 行为前进。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验/资源 | 关键局限 |
|----------|---------------------|----------|
| VLA imitation learning | 大规模成功 demonstration，视觉语言预训练 | 只拟合 expert state-action distribution；遇到 collision、misalignment、timeout 等 OOD state 时没有 recovery 数据 |
| Human-in-the-loop post-training | 人类 intervention / correction 作为失败边界监督 | 样本质量高，但需要人持续介入，不容易把 rollout 数量扩到 on-policy RL 需要的规模 |
| Real-world GRPO/PPO | 从真实机器人交互中学习成功/失败 | 对大 VLA 的 group rollouts 和 repeated initial states 成本极高；硬件磨损和安全风险高 |
| Offline preference / DPO | 复用固定数据，构造成败偏好对 | 可重复利用数据，但 policy update 后的数据分布不会同步刷新，容易停在静态数据覆盖的边界 |
| Latent world model / Dreamer | 用 compact latent dynamics 降低 rollout 成本 | latent 是 world model 自己的计算坐标，不一定与 VLA 预训练视觉特征对齐；若直接让 VLA 读 latent，需要新接口或重新训练 |
| Task-specific simulator | 显式几何/物理仿真 | 构建和校准成本高，长尾真实视觉、物体材质、机器人误差难覆盖 |

WMPO 的 Delta：**不是简单地“用世界模型做 RL”，而是把 VLA 的输入域当成一等公民，选择生成 pixel observations，并用 policy rollouts 对齐 world model 的 failure distribution。**

### 1.4 论文贡献

1. **Pixel-space imagined RL**：world model 内部可以使用 diffusion/VAE latent，但给 VLA policy 的 rollout observation 回到图像域，使 VLA 的预训练视觉能力继续有效。
2. **Policy Behavior Alignment**：world model 先在 OXE 轨迹上预训练，再用当前 base policy 收集的真实 rollouts 微调，以覆盖失败和 suboptimal states。
3. **Complete-trial autoregressive generation**：不是只预测短 horizon 再做 dense reward，而是生成完整 trial，让 reward model 判断 success/failure，减少 reward hacking。
4. **Noisy-frame conditioning + frame-level action control**：前者处理长自回归视频漂移，后者处理 action chunk 与生成帧之间的对齐。
5. **Imagined GRPO**：从同一个真实初始状态在 world model 内采样 $G$ 条轨迹，使用组内相对成功率构造 advantage；物理世界很难做到这种 repeated rollout，world model 使它变便宜。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $g$ | language instruction | 任务输入/真实环境 | 否 | 指定 VLA 要完成的操作目标 | 在 WMTS 中不能让语言标签污染物理 dynamics；它应是 policy/reward 条件，不是接触动力学本体 |
| $I_i$ | image frame | 真实相机或 world model 生成 | 生成阶段对 policy update 视为采样结果 | 第 $i$ 帧图像 observation | 论文省略 proprioception 和 wrist camera，这对 dexterous/contact 是很强限制 |
| $s_t$ | state-level observation | $s_t=(I_{t-c:t},g)$ 或多帧状态 | 采样状态，不对 $s_t$ 求策略梯度 | VLA 在第 $t$ 个决策步看到的条件 | 论文脚注区分 frame index $i$ 与 state index $t$；一个 state 包含多帧 |
| $a_t$ | $\mathbb{R}^{K\times D}$ action chunk | VLA policy output | 对 $\log\pi_\theta(a_t\mid s_t)$ 求梯度 | 长度 $K$ 的动作块，每个动作 $D$ DoF | 每维离散成 256 bins，因此概率是 token 分类概率，不是连续 Gaussian 密度 |
| $a_t^{i,j}$ | discrete token | action chunk 第 $i$ 个动作、第 $j$ 个 DoF | 是，通过对应 token log-prob | 组成 action chunk 的原子动作 token | $i$ 在 Eq. 3 是 chunk 内时间，不是 trajectory id |
| $\pi_\theta$ | VLA policy | OpenVLA-OFT SFT 后继续优化 | 是 | 从图像/语言到 action chunk 的策略 | update 时 trajectory 来自 $\pi_{\theta_{\text{old}}}$，目标优化新 $\theta$ |
| $\theta_{\text{old}}$ | old policy parameters | 每轮 rollout 前冻结 | 否，reference log-prob detached | 生成 imagined trajectories 的行为策略 | PPO/GRPO ratio 的 denominator 必须 detach，否则 ratio 失去 off-policy correction 意义 |
| $p_\phi$ | video world model | OXE pretrain + policy behavior fine-tune | policy update 时冻结；world-model training 时更新 | 近似 $p(I_{i:i+K}\mid I_{i-c:i},a_{i:i+K})$ | 叫 pixel-space，但 diffusion 仍在 VAE latent 中运行，关键是 decode 后喂给 VLA |
| $R_\psi$ | binary reward model | real trajectories 训练 | policy update 时冻结 | 判断完整 trajectory 是否成功 | 是 learned classifier，不是真实 reward；可能被 world model artifacts 欺骗 |
| $\tau_i$ | imagined trajectory | $\pi_{\theta_{\text{old}}}$ 与 $p_\phi$ 交替 rollout | 作为采样数据 | 第 $i$ 条想象轨迹，含 states/actions/frames | trajectory id $i$ 与 frame index $i$ 易混 |
| $R_i$ | $\{0,1\}$ | $R_\psi(\tau_i)$ | 否 | 第 $i$ 条轨迹成功/失败标签 | 稀疏二值信号，无法表达接触进展、稳定性、能耗 |
| $G$ | group size，论文为 8 | GRPO hyperparameter | 否 | 同一初始状态下采样的轨迹数 | 若组内全成功或全失败，advantage 方差为 0，需要 dynamic sampling |
| $\hat A_i$ | scalar advantage | group rewards 归一化 | 否 | 第 $i$ 条 trajectory 相对组内平均水平的优劣 | 它不是 critic 估计的 $A(s,a)$，而是 trajectory-level normalized return |
| $r_{i,t}(\theta)$ | scalar ratio | policy update 计算 | 是 | 新旧策略在第 $i$ 条轨迹第 $t$ 步 action 上的概率比 | clipping 是稳定 update，不是解决 world model bias |
| $P$ | 128 或 1280 real rollouts | 真实环境数据预算 | 否 | 用于 policy behavior alignment 和 baselines 的真实轨迹数 | 表中 $P$ 不是 transition 数，而是完整 real trajectories |

### 2.2 从 imitation learning 的失败开始

VLA imitation learning 通常最小化 expert 数据上的 negative log-likelihood：

$$
\mathcal{L}_{\text{IL}}(\theta)
=-\mathbb{E}_{(s,a^*)\sim \mathcal{D}_{E}}
\left[\log \pi_\theta(a^*\mid s)\right].
$$

这个目标有两个隐含条件：

1. 训练时状态 $s$ 来自 expert state distribution $\rho_E(s)$。
2. 测试时策略产生的状态也最好仍在 $\rho_E(s)$ 附近。

但 closed-loop robot policy 的真实执行分布是由策略自己诱导的：

$$
\rho_{\pi_\theta}(s_{t+1})
=\int \rho_{\pi_\theta}(s_t)\pi_\theta(a_t\mid s_t)P_{\text{real}}(s_{t+1}\mid s_t,a_t)\,ds_t\,da_t.
$$

只要某一步动作有小偏差，下一步状态就可能离开 expert distribution。此后 IL loss 没有告诉策略应该如何 recover，因为 expert demonstration 数据通常不包含“撞歪了以后怎么重新对准”。这就是 WMPO 文章开头的核心瓶颈：**VLA 缺少的不是再多一个成功动作样本，而是失败分布上的决策信号。**

### 2.3 从真实 RL 到 world-model RL：Dyna 视角

真实目标可以写成 trajectory distribution 下的 expected return：

$$
J_{\text{real}}(\theta)
=\mathbb{E}_{\tau\sim \rho_{\theta,P_{\text{real}}}}
\left[R(\tau)\right],
$$

其中轨迹分布分解为：

$$
\rho_{\theta,P_{\text{real}}}(\tau)
=\rho_0(s_0)\prod_{t=0}^{T}
\pi_\theta(a_t\mid s_t)P_{\text{real}}(s_{t+1}\mid s_t,a_t).
$$

model-based RL 的替换是学习一个 $p_\phi$ 来近似 $P_{\text{real}}$：

$$
\rho_{\theta,p_\phi}(\tau)
=\rho_0(s_0)\prod_{t=0}^{T}
\pi_\theta(a_t\mid s_t)p_\phi(s_{t+1}\mid s_t,a_t),
$$

并优化：

$$
J_{\phi}(\theta)
=\mathbb{E}_{\tau\sim \rho_{\theta,p_\phi}}
\left[R_\psi(\tau)\right].
$$

这一步的收益是样本效率，代价是 model bias。若 reward 有界 $|R(\tau)|\le R_{\max}$，则有一个基本警告：

$$
\left|J_{\text{real}}(\theta)-J_{\phi}(\theta)\right|
\le
2R_{\max}\,
D_{\mathrm{TV}}\!\left(
\rho_{\theta,P_{\text{real}}},\rho_{\theta,p_\phi}
\right)
+ \text{reward-model error}.
$$

这个不等式解释了 Policy Behavior Alignment 为什么不是工程小技巧，而是理论上必要：world model 只在 expert/success distribution 上准，并不保证在 $\rho_{\pi_\theta}$ 的失败状态上准。WMPO 用当前 policy 收集真实 rollouts 再 fine-tune $p_\phi$，本质上是在减小当前策略分布下的 trajectory-level model error。

### 2.4 为什么是 pixel-space world model

VLA policy 不是一个从任意 latent 到动作的通用函数。它通常包含一个在大规模图像/视频/语言数据上预训练的视觉编码器：

$$
z^{\text{VLA}}_t=f_{\text{VLA}}(I_t,g),\qquad
a_t\sim \pi_\theta(\cdot\mid z^{\text{VLA}}_t).
$$

若 world model 输出自己的 latent $z^{\text{WM}}_t$，就出现接口问题：

$$
z^{\text{WM}}_t \in \mathcal{Z}_{\text{WM}}
\quad \not\equiv \quad
f_{\text{VLA}}(I_t,g)\in \mathcal{Z}_{\text{VLA}}.
$$

要让 VLA 用 $z^{\text{WM}}$，至少需要一个 adapter 或重新训练视觉接口；这会破坏“复用 VLA 预训练视觉知识”的初衷。WMPO 的选择是让 world model 生成图像：

$$
\hat I_{i:i+K}\sim p_\phi(I_{i:i+K}\mid I_{i-c:i},a_{i:i+K}),
$$

再把 $\hat I$ 送回 VLA 原本的视觉输入域。

注意一个符号陷阱：论文说 pixel-based predictions，但模型架构仍使用 SDXL 2D VAE 和 diffusion latent。关键不在于每一步计算都在 raw pixels，而在于 **policy optimization 的 observation interface 是 pixels**。这点与 Dreamer/RSSM 的 latent imagination 有本质区别。

### 2.5 从 REINFORCE/PPO 推到 GRPO objective

如果一个 trajectory 的终端 reward 是 $R_i\in\{0,1\}$，最朴素的 policy gradient 为：

$$
\nabla_\theta J(\theta)
=
\mathbb{E}
\left[
\sum_{t=0}^{T}
\nabla_\theta \log\pi_\theta(a_{i,t}\mid s_{i,t})
\left(R_i-b\right)
\right].
$$

$b$ 是 baseline，用于降低方差。WMPO 使用 GRPO 的组内 baseline：从同一个初始状态采样 $G$ 条 imagined trajectories，计算：

$$
\mu_G=\frac{1}{G}\sum_{i=1}^{G}R_i,\qquad
\sigma_G=\sqrt{\frac{1}{G}\sum_{i=1}^{G}(R_i-\mu_G)^2},
$$

于是 trajectory-level advantage 是：

$$
\hat A_i=\frac{R_i-\mu_G}{\sigma_G}.
$$

若 $G$ 条轨迹全成功或全失败，则 $\sigma_G=0$，所有 trajectory 没有相对优劣。这就是 dynamic sampling 的数学原因：不是为了“数据更漂亮”，而是为了避免 sparse binary reward 下 advantage 消失。

接着引入 PPO-style ratio：

$$
r_{i,t}(\theta)
=
\frac{\pi_\theta(a_{i,t}\mid s_{i,t})}
{\pi_{\theta_{\text{old}}}(a_{i,t}\mid s_{i,t})}.
$$

因为动作是长度 $K$、每个动作 $D$ 个维度、每维 256-bin 的离散 token，old-policy log probability 需要按 chunk 内所有 token 求和：

$$
\log \pi_{\theta_{\text{old}}}(a_t\mid s_t)
=
\sum_{i=1}^{K}\sum_{j=1}^{D}
\log \pi_{\theta_{\text{old}}}(a_t^{i,j}\mid s_t).
$$

最终目标是 clipped surrogate：

$$
J(\theta)
=
\mathbb{E}
\left[
\frac{1}{G}\sum_{i=1}^{G}\frac{1}{T}\sum_{t=0}^{T}
\min\left(
r_{i,t}(\theta)\hat A_i,\,
\operatorname{clip}(r_{i,t}(\theta),1-\epsilon_{\text{low}},1+\epsilon_{\text{high}})\hat A_i
\right)
\right].
$$

这就是 WMPO 的核心训练逻辑：world model 提供可重复、低成本的 on-policy rollouts；GRPO 只通过 sampled action 的 log-prob 更新 policy，不需要对视频生成过程反传。

### 2.6 世界模型的数据流

| 阶段 | 输入 | 输出 | 目的 | 关键风险 |
|------|------|------|------|----------|
| OXE pretraining | 大规模 robot trajectories | 初始 video world model | 学到广义 robot-object visual dynamics | OXE 多为成功演示，failure underrepresented |
| Policy Behavior Alignment | base policy 的真实 rollouts，含失败 | downstream-aligned $p_\phi$ | 对齐当前策略分布 | 若 rollout 太少或任务太窄，failure mode 仍覆盖不足 |
| Autoregressive trial generation | $c=4$ 条件帧 + action chunk $K=8$ | 完整 imagined trial | 支持终端 success reward | 自回归误差累积，长 horizon 漂移 |
| Noisy-frame conditioning | 训练时给 condition frames 加 50/1000 diffusion noise | 对 noisy generated frames 更稳健 | 让训练分布接近生成时分布 | 噪声太小不鲁棒，太大会破坏条件信息 |
| Frame-level action control | 每帧 action 经 MLP 生成 AdaLN modulation | action-frame 对齐的视频生成 | 避免动作与帧错位 | 只对视觉对齐有帮助，不保证物理接触力正确 |
| Reward model | full trajectory 的 sliding clips | binary success probability | 自动打分，避免人工 reward shaping | learned reward 可能识别视觉假象，不等同真实任务成功 |

## 3. 训练、数据与实验

### 3.1 实验设置

| 项目 | 设置 |
|------|------|
| Base policy | OpenVLA-OFT，经 imitation learning fine-tune |
| 省略输入 | robot proprioceptive state 和 wrist camera，论文为简化全部省略 |
| Action chunk | $K=8$，每维离散为 256 bins |
| World model conditioning | $c=4$ 条件帧，预测下一个 $K=8$ frames |
| Simulation benchmark | MimicGen: Coffee_D0, StackThree_D0, ThreePieceAssembly_D0, Square_D0 |
| Base-policy demos | 每个 simulation task 300 expert trajectories |
| Evaluation | 每个 simulation task 128 initial states，报告 success rate |
| Rollout budget | $P=128$ 和 $P=1280$ real trajectories |
| Real-world platform | Cobot Mobile ALOHA |
| Real-world task | Insert the square into the stick，clearance 5 mm |
| Real-world data | 200 expert demos 训练 base policy，再收集 128 policy trajectories 用于 WMPO |
| Real-world evaluation | 30 trials |

训练资源与超参数：

| 组件 | 关键超参数 |
|------|------------|
| OpenVLA-OFT SFT | 8 H100 GPUs |
| World model / policy optimization | 32 H100 GPUs |
| World model optimizer | AdamW $(\beta_1=0.9,\beta_2=0.999)$ |
| World model LR / batch / clip | $10^{-4}$ / 128 / 0.1 |
| World model steps | pretrain 12,000,000；fine-tune 3,000,000 |
| EMA / weight decay / target | 0.9999 / 0.0 / $\epsilon$ prediction |
| GRPO LR / batch / group | $5\times10^{-6}$ / 64 / $G=8$ |
| GRPO mini-batch / clip | 128 / $\epsilon_{\text{low}}=0.20,\epsilon_{\text{high}}=0.28$ |
| GRPO temperature | 1.6 |

### 3.2 MimicGen 主结果

| Rollout budget $P$ | Method | Coffee | StackThree | ThreePieceAssembly | Square | Mean |
|--------------------|--------|--------|------------|--------------------|--------|------|
| - | Base policy | 43.8 | 46.9 | 19.5 | 24.2 | 33.6 |
| 128 | GRPO | 38.3 | 52.3 | 17.2 | 25.0 | 33.2 |
| 128 | DPO | 43.8 | 53.9 | 23.4 | 28.1 | 37.3 |
| 128 | WMPO | 61.7 | 56.3 | 37.5 | 32.8 | 47.1 |
| 1280 | GRPO | 47.7 | 54.7 | 20.3 | 25.8 | 37.1 |
| 1280 | DPO | 52.3 | 57.0 | 26.7 | 33.6 | 42.4 |
| 1280 | WMPO | 75.0 | 64.1 | 46.1 | 45.3 | 57.6 |

因果解释：

- $P=128$ 时，WMPO mean 47.1，比 DPO 37.3 高 9.8 点，比 real-world GRPO 33.2 高 13.9 点。这个结果支持“world model 让 on-policy update 的有效 rollout 数远超真实 rollout budget”。
- $P=1280$ 时，WMPO mean 57.6，比 DPO 42.4 高 15.2 点，比 GRPO 37.1 高 20.5 点。更重要的是 margin 随预算增大而扩大，说明 WMPO 能把更多 policy behavior data 转化为更准的 world model 和更多 imagined rollouts；DPO 虽能复用数据，但被固定偏好数据限制。
- GRPO 在 $P=128$ 下甚至低于 base policy，说明直接把大 VLA 放到真实 sparse reward on-policy RL 里，rollout 数和 batch 结构不够时会不稳定。附录也指出，大 batch 64 对 GRPO 稳定性重要，但一次 update 至少需要 $64\times8=512$ real trajectories，且 dynamic sampling 还会过滤全成/全败组。

这里最强的证据不是“WMPO 最高”，而是 **同样真实 rollout budget 下，WMPO 把真实数据用于校准模型，再在模型内制造大量可控的 on-policy comparisons**。这正是它的逻辑优势。

### 3.3 Generalization 结果

| Method | Position disruption | Background disruption | Texture disruption | Mean |
|--------|---------------------|-----------------------|--------------------|------|
| Base policy | 14.1 | 46.1 | 10.9 | 23.7 |
| GRPO | 15.6 | 47.7 | 10.9 | 24.7 |
| DPO | 16.4 | 34.4 | 7.8 | 19.5 |
| WMPO | 22.3 | 50.0 | 16.4 | 29.6 |

因果解释：

- DPO 的 mean 19.5 低于 base 23.7，尤其 background/texture disruption 明显下降，说明 preference-style offline update 可能强化了训练数据中的视觉捷径，而不一定学到可迁移操作策略。
- WMPO 在三类 shift 上都最高，mean 29.6。论文解释为 world model rollouts 帮助策略学习更 generalizable 的 recovery/interaction strategy。
- 但这个表也暴露边界：WMPO 的 absolute success 仍不高，position disruption 只有 22.3。它证明的是相对改进，不是已经解决开放世界泛化。

### 3.4 Real-world 与 qualitative 证据

| Real-world task | Base policy | DPO | WMPO |
|-----------------|-------------|-----|------|
| Insert square into stick, 30 trials | 53% | 60% | 70% |

这组结果说明 WMPO 不是只在 MimicGen simulator 中有效；在 5 mm clearance 的真实 ALOHA 插入任务上，WMPO 相对 base 提升 17 点，相对 DPO 提升 10 点。

论文还给了两个 qualitative 证据：

1. **Self-correction**：Square 任务中，base policy 碰撞后继续把 square 往 stick 上推，直到 timeout；WMPO 学会 lift、realign、再 insert。
2. **Shorter successful trajectories**：WMPO 成功轨迹更短，说明它减少 stuck behavior，不只是把成功率提高一点。

这些 qualitative 证据与主故事强相关：如果 WMPO 真的从 imagined failures 中学习，那么最应该出现的行为不是“动作更像 expert”，而是 expert demonstration 中很少见的 recovery。

### 3.5 Lifelong learning

论文在 StackThree 上迭代执行：

1. 收集 $P=128$ real trajectories。
2. 用这些 trajectories 做 policy behavior alignment。
3. 在 world model 内做 WMPO。
4. 用更新后的 policy 再收集下一批 trajectories。

结果曲线显示 WMPO 能稳定继续提升，而 DPO 迭代不稳定；base policy 需要更多 human expert trajectories 才能作为参照。这个实验支持一个重要观点：**WMPO 的数据飞轮依赖 policy 自己产生的新分布，而不是无限增加 expert demonstrations。**

但这里也要批判：论文没有给每轮精确数值表，只给曲线；因此 recap 中不能把 lifelong learning 当成已充分量化的强结论，只能视为支持性证据。

### 3.6 Ablation 与证据缺口

论文没有给出完整的 component ablation table。它声称 Policy Behavior Alignment、noisy-frame conditioning、frame-level action control、2D VAE、complete-trial generation 都重要，但主文主要通过整体结果和机制解释支撑，而非逐项移除验证。

可从已有结果得到的因果链如下：

| 证据 | 观测结果 | 支持的机制 | 仍缺什么 |
|------|----------|------------|----------|
| WMPO vs real GRPO | $P=1280$ mean 57.6 vs 37.1 | world model 提供足够多 imagined on-policy comparisons，缓解真实 rollout 稀缺 | 没有直接报告 imagined rollout 数量与性能曲线 |
| WMPO vs DPO | $P=1280$ mean 57.6 vs 42.4 | on-policy group comparisons 比固定 offline preference 更能跟随策略分布更新 | 没有与更强 offline RL / diffusion-policy RL 做充分比较 |
| Generalization | WMPO mean 29.6，DPO 19.5 | imagined rollouts 可能降低视觉捷径依赖，学习 interaction strategy | 绝对成功率仍低，shift 种类有限 |
| Self-correction figure | collision 后 lift/realign/insert | failure-state data 提供 recovery 行为 | qualitative case，缺少 self-correction 发生率统计 |
| Reward model F1 | 各任务 F1 > 0.95 | binary success classifier 足以区分成功/失败，减轻 reward hacking | F1 在 real generated rollouts 上是否仍可靠没有完全展开 |
| Real-world ALOHA | 53/60/70 | 方法可转到真实细粒度插入任务 | 只有一个真实任务、30 trials、无 tactile/proprio |

这部分是 critical reading 的关键：WMPO 的主论证很强，但并不是每个模块都已经被严格证明。对我们做 WMTS，不能照搬所有 design choice，而要把缺失 ablation 变成自己的实验计划。

## 4. 核心洞见

### 4.1 论文真正的 insight

WMPO 的真正 insight 是：**VLA 后训练里的 world model 不只是动态模型，而是一个“可复位、可重复、可产生失败对比”的 policy improvement environment。**

这和传统 video prediction 的评价标准不同。一个视频模型看起来清晰不够，它必须满足：

1. 对当前 policy 的 action distribution 准。
2. 对 failure states 准。
3. 能从同一 initial state 生成多条有成败差异的 trajectories。
4. 生成结果能被 reward model 可靠评价。
5. 生成的 observations 仍处在 VLA 视觉编码器可理解的输入域。

如果这五点不成立，GRPO 的 advantage 可能只是对模型幻觉的过拟合。

### 4.2 为什么这个设计有效

WMPO 的设计有一个清楚的 causal stack：

`policy behavior rollouts`
→ 让 world model 看见当前策略的失败分布
→ imagined trajectories 中出现成功/失败混合组
→ GRPO 获得非零 normalized advantage
→ policy 增加导致成功 trajectory 的动作概率，降低失败 trajectory 的动作概率
→ policy 学到 IL 数据中缺失的 self-correction
→ 新 policy 产生新分布，继续 alignment。

这个 stack 里最脆弱的环节是 world model fidelity。只要 $p_\phi$ 对接触结果、遮挡、物体卡住等关键事件不准，后面的 advantage 就会变成错误梯度。

### 4.3 什么时候会失效

1. **隐藏状态主导任务**：如果成功/失败取决于图像中不可见的力、接触法向、摩擦状态、手指微滑移，仅用 image sequence 定义 $S=I\times G$ 就不够。
2. **world model 单点错误可被策略利用**：policy 可能找到让 $R_\psi$ 判断成功、但真实物理不成功的视频模式。
3. **binary reward 太稀疏**：对长 horizon dexterous task，只有 success/failure 会让 credit assignment 过粗。
4. **动作空间不匹配**：论文只做 discretized action tokens；对 flow-matching VLA、torque control、高频 hand control 需要新的 probability accounting。
5. **计算成本压倒收益**：32 H100、12M pretrain steps、3M fine-tune steps 说明它是大算力路线，不是轻量机器人实验室默认可复现路线。

## 5. 替代方案与理论局限

### 5.1 理论维度

论文显式假设机器人状态可由 image observations 定义，并把更复杂 POMDP 留给 future work。这个假设对桌面 ALOHA 插入可能勉强成立，但对灵巧手转笔非常危险：

$$
s_t \neq I_{0:t}
\quad\text{when contact force, tactile shear, object angular velocity, actuator delay are hidden.}
$$

在 DNPM/WMTS 中，真实状态至少应包含：

$$
x_t = (q_t,\dot q_t,\tau_t,h_t^{\text{tactile}},o_t^{\text{pose}},\omega_t^{\text{object}},\lambda_t^{\text{contact}},\eta_t^{\text{actuator}}),
$$

其中很多量只能通过 belief state 估计，不能从单路外部 RGB 中稳定恢复。WMPO 的 image-only MDP 是一个强简化，不应被默认为通用机器人世界模型设定。

### 5.2 算法维度

| 方案 | 相对 WMPO 的优势 | 相对 WMPO 的问题 |
|------|------------------|------------------|
| Real-world RL / RL-100 | reward 来自真实环境，无 model exploitation | 样本贵，on-policy batch 难，硬件风险高 |
| RECAP / DexHiL | correction/intervention 直接来自人类失败边界判断 | 需要人参与，难以无限扩展 rollout |
| Dreamer / latent world model | rollout 便宜，latent dynamics 更紧凑 | 与 VLA pixel visual encoder 不对齐，且 latent fidelity 对细粒度接触不透明 |
| World4RL / DiWA | 更接近 diffusion policy / robotic policy refinement | 若单 world model、缺少不确定性约束，仍有模型欺骗风险 |
| Ensemble model-based RL | 可显式估计 epistemic uncertainty，做 conservative update | 训练和 rollout 成本更高，视频级 ensemble 更昂贵 |

WMPO 选择了 pixel fidelity 和 VLA compatibility，但没有解决 model uncertainty。对 WMTS 来说，单一 world model 不足以支撑安全的 Solve/Probe/Reject 决策。

### 5.3 工程与实验维度

1. **硬件成本高**：world model 和 policy optimization 使用 32 H100，不是轻量 pipeline。
2. **真实验证窄**：真实机器人只展示一个 ALOHA 插入任务，30 trials；对多物体、多材质、长 horizon、接触丰富任务的证据不足。
3. **省略 proprioception/wrist camera**：这简化了 VLA 输入，但也让结论不覆盖许多真实 dexterous 场景。
4. **模块消融不足**：缺少去掉 Policy Behavior Alignment、noisy-frame conditioning、frame-level action control、2D VAE 的逐项数字。
5. **reward model 是 learned binary classifier**：F1 > 0.95 是好信号，但生成视频分布上的 reward hacking 仍需 adversarial 检查。

## 6. 对用户研究的启发

### 6.1 对 WMTS 的迁移：可借鉴的是范式，不是纯像素模型

WMTS 当前核心管线是：

`latent task generation → PPO Oracle → Diffusion/Flow generalist → ensemble world model → real-robot fine-tuning`

WMPO 可以被放进这条线的两个位置：

1. **作为 generalist policy 的后训练器**：把 PPO Oracle 或 diffusion/flow generalist 放入 world model 中，做 imagined GRPO / advantage-weighted update。
2. **作为数据飞轮机制**：真实 hand rollout 不直接用于大规模 RL，而先用于校准 world model 和 reward model，再让 model 生成更多 failure-boundary comparisons。

但 WMTS 不应照搬 image-only pixel video world model。更合理版本是：

| WMPO 变量 | WMTS 中应替换成什么 | 原因 |
|-----------|---------------------|------|
| $I_{0:c}$ 外部图像帧 | RGB/wrist + joint state + tactile history + object pose belief | 灵巧手接触状态常被遮挡，触觉和 proprioception 是 first-class state |
| $g$ language instruction | latent task descriptor / skill condition | 任务条件可进入 policy/reward，但 dynamics 应尽量保持物理因果独立 |
| $a_t\in\mathbb{R}^{K\times D}$ discretized action chunk | 16+5 DoF hand command chunk，含 position/velocity/torque 或 residual action | LinkerHand 的 actuator dynamics 和 CAN latency 影响真实转移 |
| $p_\phi$ single video WM | ensemble semi-structured world model: neural latent + contact/tactile head + actuator model | 需要 epistemic uncertainty，不能只相信单模型视频 |
| $R_\psi(\tau)\in\{0,1\}$ | terminal success + tactile/contact progress + energy/safety cost | 转笔等任务 credit assignment 不能只靠二值成功 |
| GRPO group from same $s_0$ | 从同一 latent task / same object state 采样多条 rollout | 可用于估计策略在同一初态下的成败分布 |
| Dynamic sampling | Solve/Probe/Reject 数据采样：保留有信息量的混合组 | 全成/全败组对 policy improvement 信息少，但对 curriculum/uncertainty 仍可能有用 |

### 6.2 可验证实验建议

1. **PBA 必要性实验**  
   训练两个 WMTS world models：一个只用 PPO Oracle 成功轨迹，一个加入 current policy failure rollouts。固定 policy update 算法，比较 imagined success 与 real success 的 calibration。若 failure-aligned WM 在失败预测 F1、uncertainty calibration 和 downstream improvement 上更好，则支持 WMPO 的核心机制。

2. **Pixel vs structured latent 对照**  
   在同一 manipulation task 上比较三种 observation interface：pure pixel video WM、latent RSSM WM、semi-structured tactile/proprio WM。关键指标不是生成图像质量，而是 real rollout improvement 和 contact-event prediction。若 pure pixel 在 contact transition 上失败，就说明 WMPO 的 pixel argument 对 VLA 有效，但对灵巧接触不充分。

3. **Reward granularity 实验**  
   比较 binary success reward、tactile progress reward、contact-stability reward、ensemble LCB reward。若 binary reward 学到短期视觉投机，而 tactile/contact reward 提升真实稳定性，则说明 WMTS 必须超越 WMPO 的二值 reward。

4. **Model exploitation 检测**  
   在 imagined GRPO 后，把 policy 在 ensemble 中 disagreement 高的 states 单独拉出来真实验证。若高 disagreement 区域真实失败率显著高，则必须引入 conservative update 或 Reject 机制。

### 6.3 不应过度外推的点

- 不应把“pixel-space 对 VLA 有利”外推为“所有机器人 world model 都应该是 pixel video”。对 LinkerHand 转笔，触觉剪切、关节速度、摩擦状态、actuator delay 很可能比像素纹理更关键。
- 不应把 WMPO 的 success-rate 提升理解为 world model 已经学会物理。它可能只在短程、视觉可判别、低接触复杂度的任务上足够准。
- 不应忽视计算预算。若 WMTS 要走 world model 路线，必须明确哪些模块用大模型，哪些用结构化低维模型，否则系统会被视频生成成本拖垮。
- 不应只用 learned binary reward。对 dexterous manipulation，真正难的是中间接触状态是否朝正确 basin 演化。

## 7. 与知识体系的联系

### 7.1 与 [[ReinforcementLearning]] 的联系

WMPO 是 Dyna-style model-based RL 在 VLA 上的现代版本：用 $p_\phi$ 替换真实 transition，用 imagined trajectories 更新 policy。它同时使用 PPO/GRPO 的 clipped ratio 来稳定更新：

$$
r_t(\theta)=\frac{\pi_\theta(a_t\mid s_t)}
{\pi_{\theta_{\text{old}}}(a_t\mid s_t)}.
$$

区别在于，classic Dyna 多用于低维状态或 tabular/continuous control；WMPO 的状态是 image-language observation，模型是 video diffusion，reward 是 learned trajectory classifier。

### 7.2 与 [[StochasticProcess]] 的联系

world model 近似的是条件随机过程：

$$
I_{i:i+K}\sim p_\phi(I_{i:i+K}\mid I_{i-c:i},a_{i:i+K}).
$$

autoregressive rollout 实际上反复组合这个条件分布：

$$
p_\phi(I_{0:N}\mid I_{0:c},a_{0:N})
=
\prod_i p_\phi(I_{i:i+K}\mid I_{i-c:i},a_{i:i+K}).
$$

noisy-frame conditioning 的作用，是让训练条件分布覆盖 generated frames 的噪声，而不是只覆盖 clean real frames。这对应 sequential prediction 中典型的 exposure bias 问题。

### 7.3 与 [[RepresentationLearning]] 的联系

WMPO 的 pixel-space 论证是一个 representation-interface 论证：如果 policy 的能力来自 $f_{\text{VLA}}(I)$，则 world model 最好输出 $I$，而不是让 policy 读一个不同坐标系中的 $z^{\text{WM}}$。这和 Part A 中 Dreamer/DayDreamer 的 latent imagination 形成清晰张力：

- Dreamer：为 RL efficiency 学一个 compact latent state。
- WMPO：为复用 VLA 视觉先验，把 rollout observation 解码回 pixel domain。
- WMTS：应在二者之间取中间路线，保留 task-relevant tactile/proprio/contact latent，同时保持必要的视觉可解释接口。

### 7.4 与 [[Diffusion Policy: Visuomotor Policy]] / World4RL / DiWA 的联系

Diffusion Policy 解决的是 action distribution multimodality，WMPO 解决的是 policy improvement signal 来自哪里。World4RL 和 DiWA 都在尝试用 world model 做 policy refinement；WMPO 的独特之处是明确服务于 VLA，并把 pixel-space interface 和 GRPO group sampling 作为主轴。

对 WMTS 的结论是：**可把 WMPO 视为 VLA-scale imagined RL 的正例，但必须把 Part A 的 ensemble uncertainty、SafeDreamer 的 cost、MoDem/FOWM 的 conservative model-based update、DexSim/DexWM 的 contact/tactile结构化监督合并进来。**

## References

- Zhu et al., 2025. *WMPO: World Model-based Policy Optimization for Vision-Language-Action Models*.
- Hafner et al., 2020. *Dream to Control: Learning Behaviors by Latent Imagination*.
- Jiang et al., 2025. *World4RL: Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation*.
- DiWA, 2025. *Diffusion Policy Adaptation with World Models*.
- Schulman et al., 2017. *Proximal Policy Optimization Algorithms*.
- Shao et al., 2024. *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models*.
- Yu et al., 2025. *DAPO: An Open-Source LLM Reinforcement Learning System at Scale*.
