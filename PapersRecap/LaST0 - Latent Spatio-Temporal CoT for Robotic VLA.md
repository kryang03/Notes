---
tags:
  - paper
  - embodied-ai
  - representation-learning
  - vla
  - latent-reasoning
  - flow-matching
aliases:
  - LaST0
  - Latent Spatio-Temporal CoT
paper-year: 2026
read-date: 2026-06-25
venue: ICML 2026 submission / arXiv
paper-pdf: "[[Papers/LaST0: Latent Spatio-Temporal Chain-of-Thought for Robotic.pdf]]"
related:
  - "[[EmbodiedAI]]"
  - "[[RepresentationLearning]]"
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[WoG - World Guidance for VLA Action Generation]]"
  - "[[WMPO - World Model-based Policy Optimization for VLA]]"
---

# LaST0: Latent Spatio-Temporal Chain-of-Thought for Robotic Vision-Language-Action Model

> [!abstract] 核心贡献
> LaST0 把 VLA 的“先想后做”从显式语言/图像 CoT 转移到连续 latent space：慢速 reasoning expert 自回归生成未来 2D 视觉、3D 几何和机器人本体状态的 latent CoT，快速 acting expert 在共享 attention/KV cache 中读取这些 latent guidance 并用 flow matching 生成高频动作，从而在保持 reason-before-act 的同时显著降低显式 CoT 的推理延迟。

> [!tip] 与理论基础的关联
> - [[EmbodiedAI]] — robotic CoT 可以统一写成 $p(a,Z\mid I,l)=p(a\mid Z,I,l)p(Z\mid I,l)$；LaST0 的关键是把 $Z$ 从语言/图像 token 换成连续物理 latent。
> - [[RepresentationLearning]] — latent CoT 是一种 privileged future representation distillation：训练时用未来 RGB/point cloud/proprio targets，推理时由当前观测自回归预测。
> - [[StochasticProcess]] — acting expert 采用 Flow Matching policy，把连续动作生成建模为从 noised action 到 demonstration action 的速度场回归。
> - [[ControlTheory]] — slow reasoning / fast acting 是分层控制和多速率控制的 VLA 架构化版本；KV cache 让慢变量以低频更新，快变量每步闭环响应。
>
> **核心技术**: Latent CoT, Spatio-Temporal Latent Reasoning, Mixture-of-Transformers, Fast-Slow Control, Flow Matching Action Expert, Privileged 3D Latent Supervision

## 0. 阅读定位与范本价值

LaST0 解决的是 VLA 中一个真实存在的张力：reason-before-act 有助于长程一致性和物理推理，但显式生成语言 CoT 或未来图像太慢，而且语言很难表达连续几何、接触、高频控制状态。

它与 WoG、WMPO 的关系可以这样放：

| 方法 | “未来/世界”如何进入策略 | 主要收益 | 主要风险 |
|------|-------------------------|----------|----------|
| WoG | 把未来观测压成 action-condition tokens，再蒸馏到当前 VLM | 改善 action generation 的未来感知 | condition 不确定性和高精度几何不足 |
| WMPO | 像素 world model 生成 imagined trajectories，GRPO 更新策略 | 从失败中学习，做 policy improvement | model exploitation、reward hacking |
| LaST0 | 慢 expert 生成连续 latent CoT，快 expert 高频动作读取 latent cache | reason-before-act 低延迟化，时序一致性更强 | latent 是否真懂物理难验证；接触/触觉仍弱 |

LaST0 的范本价值在于：它不是单纯“更大 VLA”，而是把推理频率和动作频率拆开。这对灵巧手尤其重要，因为转笔/接触任务中并不是每个控制步都需要重新做高层推理，但每个控制步都需要高频响应。

最低标准对齐：

| 四支柱 | 本文必须回答的具体问题 |
|--------|------------------------|
| 逻辑与价值 | 为什么显式 CoT 既慢又物理表达不足？latent CoT 的 value add 相对 WoG/WMPO/普通 VLA 在哪里？ |
| 原理与理论 | $Z_{\mathrm{GT}}=[z^v_1,z^p_1,z^s_1,\dots]$ 从哪里来？cosine latent loss、Flow Matching action loss、fast-slow MoT 如何衔接？ |
| 实验与验证 | RLBench 82% / 15.4 Hz、真机 Franka 72%、long-horizon 0.66→0.47→0.33、AgileX/TienKung 结果如何证明故事？失败案例又反驳了什么？ |
| 未来与结合 | 对 WMTS/灵巧手，latent CoT 应该换成哪些 tactile/contact/proprio latent？为什么不能把 TienKung 结果直接外推到转笔？ |

## 1. 问题设定与动机

### 1.1 一句话核心

LaST0 用连续 spatio-temporal latent CoT 替代显式语言/图像 CoT，并用慢速 reasoning expert + 快速 acting expert 的双系统架构，让 VLA 既能“先想”又能保持机器人控制所需的高频响应。

### 1.2 直观隐喻

显式 CoT 像一个人在每一步操作前都要把计划大声念出来：“靠近鸡蛋、插入铲子、抬起、放到面包上”。这有解释性，但慢，而且语言说不清铲子尖端与锅面的毫米级相对位姿。LaST0 更像熟练操作者脑中的运动想象：不是说出每句话，而是在内部形成几步之后的视觉、几何、身体状态预期，然后手部高频执行。

这个隐喻的可证伪点是：如果 latent CoT 真的编码物理未来，它应该在长 horizon 和需要时序一致性的任务上比无 CoT / 显式 CoT 更强；如果它只是额外 token 正则化，那么在 failure cases 中仍会暴露几何高度、接触位置、闭环反馈不足。论文两者都显示了。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验/能力 | 关键局限 |
|----------|---------------------|----------|
| 普通 VLA | 当前图像/语言直接映射动作 | 缺少显式未来状态变量，长程任务容易短视 |
| 显式语言 CoT | 语言计划、文本 reasoning trace | 自回归文本慢；语言通道难表示连续几何、力、接触、机器人本体状态 |
| 未来图像 CoT / visual planning | 生成 future images/subgoals | 比语言更物理，但仍要显式解码图像，延迟和冗余高 |
| WoG-style condition prediction | 压缩未来条件指导动作 | 主要是 action-condition distillation，不提供 fast-slow 控制架构 |
| LaST0 latent CoT | 连续 latent 中预测未来 2D/3D/proprio，慢推理快执行 | latent 可解释性弱；依赖 privileged future targets；对触觉接触仍未充分覆盖 |

LaST0 的 Delta：**不是“CoT 用 latent 表示”这句话，而是把 latent CoT 放进一个多速率 VLA 控制架构中，使 reasoning 更新低频化、action generation 高频化。**

### 1.4 论文贡献

1. 定义 LaST CoT：未来 RGB semantic latent、3D geometric latent、robot proprioception latent 按时间交错组成连续 reasoning sequence。
2. 设计 MoT dual-system：reasoning expert 低频生成 latent CoT，acting expert 高频读取 latent guidance 并输出动作。
3. 用 cosine latent regression 监督 continuous CoT，而不是离散 token likelihood。
4. 用 mixed fast-slow operating ratios 训练，使部署时可在 1:1、1:2、1:4 等频率下切换。
5. 在 RLBench、Franka、AgileX mobile manipulation、TienKung humanoid dexterous hand 上验证性能和速度。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $I_t$ | RGB image, $384\times384\times3$ | 当前相机观测 | 输入不求梯度 | 当前环境视觉 | simulation 用 front-view；真机不同平台相机数不同 |
| $l_t$ | language instruction | 任务输入 | 否 | 语言目标 | 语言只定义任务，不表达低层接触 |
| $a_{t:t+H}$ | action sequence | demonstration label / action expert output | action head 参数带梯度 | 未来动作 | 单臂为 7-DoF SE(3)+gripper；AgileX 为 20-DoF；TienKung 为 26-DoF |
| $Z$ | CoT latent variable | reasoning expert output | 是 | 中间 reasoning state | 与显式 CoT 的文本/图像 token 不同，是连续 embeddings |
| $z_k^v$ | visual latent | future RGB 经 SigLIP-Large | target 不带梯度；reasoning prediction 带梯度 | 第 $k$ 个未来关键帧的语义视觉状态 | future RGB 训练可见，推理时不可见 |
| $z_k^p$ | geometric latent | future point cloud 经 Uni3D | target 不带梯度 | 未来 3D 几何/空间占据 | 预训练中点云由 VGGT 合成，不一定是真实 depth |
| $z_k^s$ | proprioceptive latent | future robot state/action tokenizer | target 不带梯度 | 机器人未来本体状态 | 对 LinkerHand 需替换为关节、触觉、actuator state |
| $Z_{\mathrm{GT}}$ | length $3H$ latent sequence | future targets 交错拼接 | target | latent CoT 监督信号 | 顺序是 $[z_1^v,z_1^p,z_1^s,z_2^v,\dots]$，不是三模态先各自完整展开 |
| $\hat Z$ | predicted latent sequence | slow reasoning expert 自回归输出 | 是 | 推理时内部 future dynamics | 连续回归，不是 softmax token |
| $\kappa$ | update ratio, e.g. 2/4/8 | deployment/training schedule | 否 | slow expert 每 $\kappa$ 步更新一次 | $\kappa$ 太大时 latent guidance 过旧 |
| $I_{\mathrm{slow}}$ | low-frequency observation | slow stream | 输入 | reasoning expert 输入 | 只在 keyframes 触发慢推理 |
| $I_{\mathrm{fast}}$ | high-frequency observation | fast stream | 输入 | acting expert 输入 | 每个控制步进入快 expert |
| KV cache | attention key/value states | slow expert inference result | 推理缓存 | fast expert 读取 latent CoT，不重复慢推理 | 速度提升关键，不是普通前向复用 |
| $A_\tau$ | noised/interpolated action | Flow Matching 中间变量 | 是 | action denoising path | $\tau$ 是 flow time，不是机器人时间 |
| $v_\theta$ | velocity field | acting expert 输出 | 是 | 从 noised action 指向 demonstration action | action expert 的核心训练目标 |

### 2.2 从 robotic CoT factorization 开始

Robotic CoT 可以抽象成一个中间变量 $Z$：

$$
p(a,Z\mid I_t,l)
=
p(a\mid Z,I_t,l)\,p(Z\mid I_t,l).
$$

显式 CoT 方法把 $Z$ 设为语言 tokens 或未来图像 tokens。这带来两个问题：

1. $p(Z\mid I,l)$ 需要自回归解码离散序列，慢。
2. 语言/图像 token 未必是动作最需要的物理状态，尤其是接触、力、几何、机器人本体。

LaST0 把 $Z$ 定义为连续 latent sequence：

$$
Z=\{z_1,\dots,z_K\},\qquad z_i\in\mathbb{R}^d.
$$

它的监督不是人工文本，而是未来物理状态的 latent targets。

### 2.3 LaST CoT target 从哪里来

对未来 horizon $H$ 中每个 keyframe $k$，LaST0 提取三种 latent：

$$
z_k^v = \operatorname{Pool}(\operatorname{SigLIP}(I_{t+k})),
$$

$$
z_k^p = \operatorname{Pool}(\operatorname{Uni3D}(P_{t+k})),
$$

$$
z_k^s = \operatorname{Tokenizer}(s_{t+k}).
$$

然后按时间交错：

$$
Z_{\mathrm{GT}}
=
[z_1^v,z_1^p,z_1^s,z_2^v,z_2^p,z_2^s,\dots,z_H^v,z_H^p,z_H^s].
$$

这个交错顺序很重要：它强制模型在每个未来时间点同时考虑语义视觉、几何和本体状态，而不是先完整预测视觉、再预测几何、再预测状态。

训练时，sequence 中间位置用 ground-truth latent 替换 `<latent pad>` 做 teacher forcing；推理时，模型从 `<latent start>` 和 `<latent pad>` 开始，自回归填入 latent embeddings。

### 2.4 Latent loss：为什么用 cosine

reasoning expert 预测 $\hat Z=\{\hat z_t\}$，用 cosine similarity 对齐 target：

$$
\mathcal{L}_{\mathrm{latent}}
=
\sum_t
\left(
1-
\frac{\hat z_t\cdot z_t^{\mathrm{GT}}}
{\|\hat z_t\|\,\|z_t^{\mathrm{GT}}\|}
\right).
$$

这意味着模型主要被要求对齐 latent 方向，而非绝对尺度。合理性在于 foundation encoder latent 的尺度未必有稳定物理单位；方向更像语义/几何状态的 embedding identity。风险也在这里：cosine loss 不保证 metric calibration，不能直接把 latent distance 当成真实物理误差。

### 2.5 Acting expert 的 Flow Matching

action expert 采用 flow matching policy。典型构造是从噪声动作 $\epsilon$ 到 demonstration action $A$ 的线性路径：

$$
A_\tau=(1-\tau)\epsilon+\tau A,\qquad \tau\in[0,1].
$$

目标速度为：

$$
v^*=\frac{dA_\tau}{d\tau}=A-\epsilon.
$$

action expert 学：

$$
\mathcal{L}_{\mathrm{flow}}
=
\mathbb{E}_{\tau,A,\epsilon}
\left[
\|v_\theta(A_\tau,\tau,I_{\mathrm{fast}},Z)-v^*\|_2^2
\right].
$$

这里 $Z$ 来自 slow reasoning expert 的 latent CoT cache。这个式子解释了“推理”和“动作”的接口：reasoning expert 不直接输出动作，而是输出一个未来物理状态条件；acting expert 在当前高频观测和 latent condition 下生成动作速度场。

### 2.6 Mixture-of-Transformers 双系统

LaST0 初始化自 Janus-Pro，使用 DeepSeek-LLM 1.5B backbone。它把 decoder-only transformer 改造成两个专家：

| 组件 | 频率 | 输入 | 输出 | 参数/信息流 |
|------|------|------|------|-------------|
| Slow reasoning expert | 低频，$t\bmod\kappa=0$ | language + low-frequency observation | latent CoT $Z$ | 自回归 latent reasoning |
| Fast acting expert | 高频，每个控制步 | high-frequency observation + cached latent CoT | action sequence / velocity field | flow matching action generation |
| Shared attention context | 跨专家共享 | latent tokens + action tokens | long-context interaction | fast expert 可 attend 到 latent CoT 和 language goal |
| KV cache | 推理缓存 | slow expert 的 key/value states | fast steps 复用 | 避免每个控制步重跑 slow expert |

一个细节需要纠正旧稿的简化说法：论文不是简单“共享 QKV 注意力矩阵”。原文说 MoT 对非 embedding 组件引入 task-specific parameter sets，包括 FFN、attention projections 和 LayerNorm，同时维持共享 global self-attention context。真正共享的是统一 token sequence / attention context，使两个专家能交互；参数上是双专家特化。

### 2.7 训练 recipe

主文描述为 large-scale pretraining + downstream SFT；图 2c 更细地展示了 staged recipe：

| 阶段 | Reason expert | Action expert | 监督 |
|------|---------------|---------------|------|
| Stage 1 | frozen | large-scale pretrain | action loss |
| Stage 2 | SFT | frozen | latent loss |
| Stage 3 | frozen | SFT | action loss |

同时主文说明 downstream 中会优化 slow reasoning 的 $\mathcal{L}_{\mathrm{latent}}$ 与 fast acting 的 $\mathcal{L}_{\mathrm{flow}}$，并用 mixed fast-slow ratios (1:1, 1:2, 1:4) 暴露不同更新延迟。理解上可以把它看成：**先让动作专家有基本控制能力，再让 reasoning expert 学物理 latent，最后让动作专家适配 latent cache 和多频率执行。**

大规模预训练数据：400K trajectories / 28M frames，来自 OXE、DROID、RoboMIND 等。一个重要工程细节是：预训练阶段用 VGGT 为所有 frames 生成 synthetic 3D point clouds，作为早期 $z^p$ 几何 latent。这增强了 3D awareness，但也意味着 3D target 的真实性受 monocular reconstruction 质量限制。

## 3. 训练、数据与实验

### 3.1 RLBench simulation 设置

| 项目 | 设置 |
|------|------|
| Benchmark | RLBench / CoppeliaSim |
| Tasks | 10 个 manipulation tasks |
| Robot | Franka Panda |
| Observation | 单 front-view RGB $384\times384$，point cloud 1024 points，language，proprio state |
| Demos | 每任务 100 trajectories，motion planner waypoints |
| Training | SFT 300 epochs，AdamW，8 NVIDIA A800 |
| Evaluation | 每任务 20 rollouts，3 seeds，报告 mean success rate + variance |
| Speed measurement | NVIDIA RTX 4090 |

### 3.2 RLBench 主结果

| Model | Mean S.R. | Inference speed |
|-------|-----------|-----------------|
| OpenVLA | 0.40 ± 0.02 | 6.3 Hz |
| SpatialVLA | 0.46 ± 0.03 | 7.9 Hz |
| CogACT | 0.61 ± 0.04 | 9.8 Hz |
| CoT-VLA | 0.66 ± 0.03 | 1.1 Hz |
| $\pi_0.5$ | 0.65 ± 0.04 | 13.8 Hz |
| HybridVLA | 0.74 ± 0.04 | 6.1 Hz |
| LaST0 | 0.82 ± 0.03 | 15.4 Hz |

任务级结果：

| Task | Best baseline | LaST0 |
|------|---------------|-------|
| Close box | CoT-VLA 0.95 | 0.95 |
| Close laptop lid | $\pi_0.5$/HybridVLA 0.95 | 0.95 |
| Toilet seat down | CoT-VLA/HybridVLA 1.00 | 1.00 |
| Sweep to dustpan | HybridVLA 0.90 | 0.80 |
| Close fridge | $\pi_0.5$/HybridVLA 1.00 | 0.85 |
| Phone on base | CogACT/CoT-VLA/HybridVLA 0.50 | 0.75 |
| Umbrella out | CogACT 0.55 | 0.75 |
| Frame off hanger | $\pi_0.5$ 0.80 | 0.70 |
| Wine at rack | $\pi_0.5$ 0.75 | 0.85 |
| Water plants | CoT-VLA/HybridVLA 0.50 | 0.60 |

因果解释：

- LaST0 的 mean 0.82 比最强 baseline HybridVLA 0.74 高 8 点，同时速度 15.4 Hz 比 CoT-VLA 1.1 Hz 快约 14 倍。这个组合直接支持论文主张：latent CoT 保留 reason-before-act 的收益，同时避免显式 CoT 的延迟。
- 它并非每个任务都赢。Sweep、Close fridge、Frame off hanger 低于最强 baseline，说明 latent CoT 不是万能；某些任务可能更依赖具体动作先验或视觉几何细节。
- CoT-VLA 速度 1.1 Hz 是显式 CoT 的硬伤；$\pi_0.5$ 速度 13.8 Hz 接近 LaST0，但成功率 0.65 低很多。LaST0 的真正卖点是速度-成功率 Pareto 改善。

### 3.3 Ablation 因果链

| Ablation | 真实结果 | 因果解释 |
|----------|----------|----------|
| 只用 image latent | 74% | 视觉语义足以支持部分操作，但缺少几何/本体状态 |
| 只用 point cloud latent | 76% | 3D geometry 对操作强，但缺少语义/机器人状态仍不完整 |
| 只用 robot state latent | 75% | proprio 对 action coherence 强，但没有环境语义/几何 |
| all modalities | 82% | 三者互补，支持“物理 latent 需要多视图” |
| 0 latent tokens | 68% | 没有 latent decision state，推理容量不足 |
| 1 token per modality | 82% | 极少 token 已足以形成有效 latent CoT |
| 更多 tokens | 无显著提升 | 关键未来物理信息可 compact 表达，更多 token 不一定有用 |
| temporal coverage 0→4 steps | 68%→82% | 长一点的未来 coverage 提升时序一致性 |
| beyond 4 steps | 无显著提升 | 过长未来对当前 action 边际收益小 |
| frequency 1:1/1:2/1:4 | 75-79% | 适中延迟下 slow/fast 协作可行 |
| frequency 1:8 | 74% | latent guidance 更新太慢，cache 过旧 |
| mixed ratio training | 82%，测试用 1:4 | 多频训练提升部署鲁棒性 |

这组 ablation 是论文最有说服力的部分：它不是只说 latent CoT 有用，而是证明了“多模态 + 适度 temporal coverage + mixed frequency”共同构成了 LaST0 的收益。

### 3.4 Real-world 主结果

真机每任务 200 teleoperation demonstrations；每任务 15 rollouts，重复 3 次不同 tabletop positions。

Franka single/dual-arm：

| Model | Wipe whiteboard | Press stamp | Place dish on rack | Place egg on bread | Scoop popcorn | Open pot pick corn | Mean |
|-------|-----------------|-------------|--------------------|--------------------|---------------|--------------------|------|
| SpatialVLA | 0.60 | 0.67 | 0.30 | 0.20 | 0.27 | 0.40 | 0.41 |
| $\pi_0.5$ | 0.60 | 0.73 | 0.60 | 0.47 | 0.53 | 0.60 | 0.59 |
| CoT-VLA | 0.53 | 0.60 | 0.66 | 0.33 | 0.33 | 0.53 | 0.50 |
| LaST0 | 0.73 | 0.93 | 0.80 | 0.66 | 0.66 | 0.53 | 0.72 |

Long-horizon place egg on bread:

| Model | Step 1 | Step 2 | Step 3 |
|-------|--------|--------|--------|
| SpatialVLA | 0.20 | 0.07 | 0.00 |
| $\pi_0.5$ | 0.47 | 0.20 | 0.07 |
| CoT-VLA | 0.33 | 0.13 | 0.07 |
| LaST0 | 0.66 | 0.47 | 0.33 |

Mobile / dexterous tasks:

| Model | Arrange dishes | Sort spoon | Open drawer | Place button |
|-------|----------------|------------|-------------|--------------|
| $\pi_0.5$ | 0.47 | 0.20 | 0.67 | 0.53 |
| CoT-VLA | 0.33 | 0.13 | 0.53 | 0.40 |
| LaST0 | 0.67 | 0.27 | 0.87 | 0.60 |

因果解释：

- Franka mean 0.72，比 $\pi_0.5$ 的 0.59 高 13 点，符合 abstract “tabletop +13%”。
- Long-horizon 三连执行中，LaST0 0.66→0.47→0.33，gap 随 horizon 拉大；这最能证明 latent CoT 的 temporally coherent state tracking，而不是单步动作更强。
- Mobile arrange dishes 0.67 vs $\pi_0.5$ 0.47，说明 fast-slow latent guidance 能扩到更大 action space。
- TienKung Open drawer 0.87、Place button 0.60 优于 baselines，但需要谨慎：这不是 LinkerHand 式 in-hand dynamic manipulation，而是 humanoid arms + ROHand dexterous hands 做 drawer/button，且只用 head RGB observation，无 tactile。

### 3.5 失败案例

Appendix E 的三个 failure cases 很重要：

| Failure | 表现 | 说明 |
|---------|------|------|
| Wipe whiteboard | 机械臂高度没有压到白板，擦除不完全 | latent CoT 没有可靠闭环感知接触高度/擦除结果 |
| Arrange dishes | 双臂放第二个盘子时碰撞，导致第一个盘子移位 | 空间高度/相对位置估计仍会错，尤其 bimanual collision |
| Open drawer | dex hand 没有前移到把手，拉取失败 | 精细 manipulator-object contact position 仍是短板 |

这些失败不是语言推理错误，而是几何、接触、反馈不足。它们提醒我们：latent CoT 的“物理推理”仍主要来自视觉/点云/proprio latent，不等于可验证的接触动力学模型。

## 4. 核心洞见

### 4.1 论文真正的 insight

LaST0 的真正 insight 是：**robotic reasoning 的中间变量 $Z$ 应该是一个面向控制的连续物理 latent，而不是人类可读的文本。**

显式 CoT 的解释性对机器人不一定是最优目标。机器人真正需要的是：未来物体在哪里、接触会不会发生、自己的关节/末端状态将如何变化、这些状态如何影响下一个动作。LaST0 用未来 2D/3D/proprio latent 作为监督，直接把 $Z$ 拉向这些物理变量。

### 4.2 为什么有效

LaST0 的收益来自三层结构：

1. **Representation layer**：用 future visual/geometric/proprio targets 监督 latent CoT，使 reasoning state 物理化。
2. **Temporal layer**：未来多个 keyframes 交错展开，使 latent 不是单帧静态描述，而是短期动态轨迹。
3. **Control-frequency layer**：slow expert 低频更新 latent，fast expert 高频读取 cache，避免每步重推理。

这三层缺一不可。只有 latent 没有 temporal coverage，会短视；只有 temporal coverage 没有 fast-slow cache，会慢；只有 fast-slow 没有物理 latent，就只是分层网络。

### 4.3 什么时候会失效

1. **触觉/接触主导**：如果任务成败取决于不可见接触力、摩擦、剪切，RGB/point cloud/proprio latent 可能不够。
2. **synthetic 3D target 错误**：预训练中 VGGT 生成的点云若对透明/反光/遮挡物体错误，$z^p$ 会注入错误几何。
3. **cache 过旧**：1:8 frequency 下降到 74%，说明慢推理更新太慢会让 latent guidance 滞后。
4. **动作空间仍偏 end-effector / low-dimensional hand**：TienKung 26-DoF 包含双臂和每手 6 个 dex hand delta joint，不等于复杂高维多指触觉控制。
5. **没有 RL/self-correction**：LaST0 仍主要是 imitation/SFT 路线，不能像 WMPO/RL-100 那样从真实失败 reward 中自我改进。

## 5. 替代方案与理论局限

### 5.1 理论维度

LaST0 的 latent CoT factorization 是合理的：

$$
p(a,Z\mid I,l)=p(a\mid Z,I,l)p(Z\mid I,l).
$$

但它并不保证 $Z$ 是 sufficient statistic。理想上需要：

$$
p(a\mid I,l,Z)\approx p(a\mid I,l,\text{future physical state}),
$$

而论文用 cosine latent loss 和 success rate 间接验证这个近似。对 contact-rich dexterous manipulation，future physical state 包括接触模式、切向力、物体角速度、actuator lag，这些没有进入 $Z_{\mathrm{GT}}$。

### 5.2 算法维度

| 路线 | 相对 LaST0 的优势 | 相对 LaST0 的问题 |
|------|-------------------|-------------------|
| 显式语言 CoT | 可解释、人类可读 | 慢，物理表达瓶颈 |
| WoG condition space | 更直接地把未来条件蒸馏到动作头 | 没有多速率 reasoning/acting 架构 |
| WMPO imagined RL | 能从失败 reward 中学习 recovery | 需要高保真 world model，计算大 |
| Latent world model / Dreamer | 可做 rollout/planning/value learning | latent 与 VLA/action head interface 需要设计 |
| 结构化 contact model | 对触觉/接触更可信 | 需要传感器、状态估计和物理建模成本 |

### 5.3 工程与实验维度

1. 真实任务数量多，但每任务 15 rollouts ×3，仍属于中等规模验证。
2. 失败案例暴露闭环接触反馈不足，尤其高度、碰撞、handle 接触位置。
3. 预训练点云来自 VGGT 合成，3D latent 的真实几何可靠性要逐任务验证。
4. 论文没有把 tactile/force 放入 latent CoT；对灵巧手转笔是主要缺口。
5. LaST0 的速度优势在 RTX 4090 / 1:4 ratio 下测得；部署到实际低算力机器人控制栈还需系统延迟评估。

## 6. 对用户研究的启发

### 6.1 对 WMTS / 灵巧手转笔的迁移

LaST0 对 WMTS 最有价值的不是“用语言 CoT 换 latent CoT”，而是 **低频任务/物理推理 + 高频动作执行** 的接口设计。

| LaST0 变量 | WMTS / LinkerHand 转笔中应替换成什么 | 原因 |
|------------|--------------------------------------|------|
| $z_k^v$ future visual latent | object pose / pen axis / visual tracking latent | 视觉仍有用，但不是唯一状态 |
| $z_k^p$ future point cloud latent | pen geometry + contact candidate set + hand-object relative pose | 转笔关键是接触几何，而非通用点云语义 |
| $z_k^s$ future proprio latent | $q,\dot q,a_{t-1}$, actuator state, CAN latency belief | 手指动态和延迟会改变接触结果 |
| latent CoT $Z$ | future contact-mode / slip-risk / angular-velocity latent | 需要预测未来接触相位和物体旋转趋势 |
| slow expert | latent task scheduler / contact-phase planner | 低频更新任务相位和未来 contact plan |
| fast expert | PPO Oracle / diffusion-flow generalist / low-level controller | 高频输出 16+5 DoF action 或 residual action |
| KV cache | cached contact-plan latent | 让高频控制无需每步重跑大模型 |

一个可落地的 WMTS 变体：

1. 从 PPO Oracle 和仿真 rollouts 中提取未来 $H$ 步 tactile/contact/proprio/object-state targets。
2. 构造 $Z_{\mathrm{GT}}=[z^o_1,z^{contact}_1,z^{prop}_1,\dots]$。
3. 训练 slow expert 预测 latent contact CoT。
4. 训练 fast action expert 在当前 tactile/proprio observation + cached CoT 下输出 action chunk。
5. 用 ensemble world model 估计 latent CoT 的不确定性；uncertainty 高则 Probe/Reject，不让 fast expert 盲信 cache。

### 6.2 可验证实验建议

1. **Modalities ablation for dexterous contact**  
   比较 visual-only、proprio-only、tactile-only、contact-geometry、all modalities 的 latent CoT。若 tactile/contact latent 加入后 slip recovery 显著改善，说明 LaST0 的多模态 latent 思路适合转笔。

2. **Frequency ratio sweep**  
   在转笔中测试 $\kappa=1,2,4,8$。如果接触切换阶段需要 $\kappa=1/2$，自由旋转阶段 $\kappa=4/8$ 足够，就说明应做 TARC-style adaptive frequency，而不是固定 1:4。

3. **Privileged future distillation sanity check**  
   Stage I 给模型看未来接触状态，Stage II 只从当前 tactile/proprio 预测。真实验证时检查 predicted contact latent 是否提前预警滑移/丢笔。

4. **Failure-case driven evaluation**  
   专门设计高度错误、接触位置偏移、双指碰撞、延迟扰动测试。LaST0 原文失败案例已经告诉我们：这些不是附带问题，而是 latent reasoning 的核心压力测试。

5. **与 WMPO/RL-100 结合**  
   LaST0 只提供 latent reasoning 和动作生成，不提供从失败 reward 中学习的闭环。可先用 LaST-style latent CoT 初始化 policy，再用 WMPO/real-world RL 在失败边界上微调。

### 6.3 不应过度外推的点

- TienKung dex hand 结果不能直接等价于 LinkerHand 转笔。它没有触觉，任务是 drawer/button，不是动态 in-hand manipulation。
- Latent CoT 不是可解释物理模型。它可能关注正确区域并提高成功率，但不保证学到 $M(q)\ddot q+C(q,\dot q)\dot q+g(q)=\tau+J^T\lambda$ 这类动力学结构。
- 3D latent 的质量受 synthetic point cloud / Uni3D target 限制。对透明、细长、快速旋转物体要重新验证。
- Flow Matching action expert 解决动作分布生成，不解决真实系统辨识、actuator delay 和 contact uncertainty。

## 7. 与知识体系的联系

### 7.1 与 [[RepresentationLearning]] 的联系

LaST0 是 privileged multimodal latent distillation：

$$
(I_{t+k},P_{t+k},s_{t+k})
\xrightarrow{\text{frozen encoders}}
(z_k^v,z_k^p,z_k^s)
\xrightarrow{\text{cosine supervision}}
\hat Z.
$$

它的 representation 目标不是重建未来，而是提供 action expert 可读取的 future physical latent。和 WoG 相比，WoG 的 condition space 是 action head 中的 compact condition；LaST0 的 latent CoT 是可自回归、可缓存、可跨频率读取的 spatio-temporal latent sequence。

### 7.2 与 [[ControlTheory]] 的联系

fast-slow 架构对应多速率控制：

$$
f_{\mathrm{reason}}=\frac{1}{\kappa}f_{\mathrm{act}}.
$$

当 $\kappa$ 增大，计算成本下降，但 latent guidance 变旧；当 $\kappa$ 太小，推理成本上升。LaST0 的 mixed-ratio training 是让 policy 对不同 $\kappa$ 都鲁棒，但从转笔角度，更理想的是根据接触相位动态选择 $\kappa$。

### 7.3 与 [[StochasticProcess]] / Flow Matching 的联系

acting expert 的动作生成是连续随机生成模型的一种 ODE 化形式。相比 DDPM 多步去噪，flow matching 的直线路径更适合实时控制，但也要求速度场在 action manifold 上稳定。对高维手部动作，应额外检查动作平滑性、关节限位、actuator bandwidth。

### 7.4 与 WMTS 的组合位置

LaST0 可以成为 WMTS 中 generalist policy 的架构骨架：

`latent task generation → slow latent CoT / task scheduler → fast action expert → ensemble world model validation → real-robot fine-tuning`

但它必须补上三块：

1. tactile/contact latent targets；
2. ensemble uncertainty / model disagreement；
3. RL/self-correction 信号。

这样它才会从“强 VLA imitation architecture”变成真正适合灵巧手动态操作的 world-model/task-scheduler 系统。

## References

- Liu et al., 2026. *LaST0: Latent Spatio-Temporal Chain-of-Thought for Robotic Vision-Language-Action Model*.
- Black et al., 2024/2025. *$\pi_0$ / $\pi_0.5$ Vision-Language-Action Models*.
- Zhao et al., 2025. *CoT-VLA*.
- Qu et al., 2025. *SpatialVLA*.
- Liu et al., 2025. *HybridVLA*.
- Su et al., 2026. *World Guidance: World Modeling in Condition Space for Action Generation*.
