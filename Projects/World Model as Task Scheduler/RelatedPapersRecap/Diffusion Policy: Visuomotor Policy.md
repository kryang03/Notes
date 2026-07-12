---
tags:
  - paper
  - diffusion-policy
  - imitation-learning
  - visuomotor-policy
  - score-based-model
  - WMTS
aliases:
  - Diffusion Policy
  - Action Diffusion
paper-year: 2023
read-date: 2026-06-15
venue: RSS 2023 / IJRR (extended)
paper-pdf: "[[Diffusion Policy: Visuomotor Policy.pdf]]"
related:
  - "[[StochasticProcess]]"
  - "[[RepresentationLearning]]"
  - "[[EmbodiedAI]]"
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[Final_WMTS]]"
---

# Diffusion Policy: Visuomotor Policy Learning via Action Diffusion

> [!abstract] 核心贡献
> 把 visuomotor 策略表示为**条件去噪扩散过程**：不直接回归一个动作，而是在「未来动作序列」空间里，从高斯噪声出发、以观测为条件、沿着学到的 action-score 梯度场迭代去噪，采样出一段高概率动作 chunk，再用 receding-horizon 闭环执行。它一举同时拿下三件别的策略表示拿不全的东西——多模态、高维动作序列、稳定训练——并在 15 个任务 / 4 个 benchmark 上平均提升 46.9%。

> [!tip] 与理论基础的关联
> - [[StochasticProcess#6.4 扩散策略 = 学出来的逆向 SDE：把 §2 的 SDE 倒过来跑]] — DDPM 前向加噪/反向去噪、score function、Langevin dynamics、SDE 生成视角；本文把动作分布建成扩散过程。
> - [[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器]] — 本文是该节的算法原型；DDPM 前向边缘/反向后验的补严推导见 [[RepresentationLearning#2.2.1 DDPM 前向边缘与反向后验的显式推导（补严）]]，噪声预测↔score matching 等价见 [[RepresentationLearning#2.2.2 噪声预测 $\epsilon_\theta$ ↔ denoising score matching 的等价（补严）]]，条件化对应 [[RepresentationLearning#2.2.3 Classifier-Free Guidance：用观测"引导"多峰采样的贝叶斯推导]]。
> - [[ReinforcementLearning#10.1 扩散策略：多峰分布的终极解（兑现 §5.1.2 的伏笔）]] — 与 EBM/IBC 隐式策略的对偶（Eq 6-8），以及 RL refinement（DiWA/World4RL 在此之上做适配，见 [[ReinforcementLearning#10.2 世界模型 RL：隐空间 vs 像素空间]]）。
> - [[ControlTheory]] — §4.5 证明线性系统下 DP 退化为 LQR 反馈 $a=-Ks$（Eq 9），给扩散策略一个控制论 sanity check。
> - [[EmbodiedAI]] — visuomotor imitation learning 的 action backbone 范式。
> - [[Final_WMTS]] — DP 是 WMTS 流水线里的低层 action prior / generalist，由 ensemble world model 负责筛选/微调 chunk。
>
> **暗线定位**：DP 的 $K$ 步去噪（噪声→数据）是 **Continuation / 同伦 / 平滑化** 暗线在动作生成上的一支——与课程学习的任务分布 $Q_0\to Q_1$、接触优化的 [[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）]]、[[ReinforcementLearning#Phase 1 — 手工课程与 continuation：先解平滑子问题]] 同宗：都先解"平滑近凸子问题"再逐步逼近真难度。
>
> **核心技术**: Conditional DDPM, Action-Sequence Diffusion, Score Matching, Receding-Horizon Control, FiLM Visual Conditioning, Time-series Diffusion Transformer, DDIM 加速

## 0. 阅读定位与范本价值

这篇是 WMTS 五模块流水线（latent task generation → PPO Oracle → **Diffusion/Flow generalist** → ensemble world model → real-robot fine-tuning）里 generalist 一环的奠基论文。读它的目的不是"知道 DP 很强"，而是要彻底想清楚两件事：

1. **为什么"把动作建成分布"比"回归一个动作"在物理上更对**——这是 WMTS 用 DP 当 generalist、而不是用 MLP 回归的根本理由。
2. **DP 的哪些自由度是结构、哪些是黑箱**——决定了 world model 应该在 DP 的哪一层介入（筛 chunk?改 score?改 noise schedule?）。

它在知识库中的角色：把 [[StochasticProcess]] 里的扩散/score 理论，落到机器人动作生成上的最干净案例；同时是 [[ReinforcementLearning]] 中"为什么 IBC 不稳而扩散稳"这一理论问题的标准答案。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心

人类示范天然是**多模态**的：同一个视觉状态，绕障可以左绕也可以右绕、推 T 块可以从左推也可以从右推。MSE 回归会把这些模式**平均**，平均出来的动作往往直接撞向障碍物——是物理上不可执行的"模式间插值"。DP 不回归动作，而是学动作分布的 score，从而能在一次 rollout 里**承诺到某一个模式**。

### 1.2 直观隐喻

把动作空间想成一个有多个山谷的能量地形（每个山谷是一种合法行为）。

- **回归策略**：报告"所有山谷的质心"——质心常落在山脊上（撞障碍）。
- **GMM/分类策略**：事先声明"有几个山谷"，数错了就 mode collapse。
- **Diffusion Policy**：放一个粒子从随机位置出发，沿能量负梯度（score）做带噪的梯度下降（Langevin）。不同的随机初始化把粒子带进不同山谷——**每次 rollout 干净地落进一个谷底**，而不是谷间插值。

这个隐喻是可证伪的：它断言 DP 的优势集中在"同一状态有多个合法动作"的任务上，而在单模态任务上不应有大优势。Fig 3 的 Push-T 多模态轨迹正是这个断言的直接证据。

### 1.3 现有方法的局限（每种范式注入了什么先验 / 关键局限）

| 策略表示 | 形式 | 注入的先验 | 关键局限 |
|---|---|---|---|
| 显式回归 (BC-MLP) | $a=F_\theta(o)$，MSE | 状态→动作是单值函数 | 多模态被平均成不可执行动作；高精度任务差 |
| 离散化分类 (BeT) | $p(a\mid o)$ over bins | 动作可量化 | bin 数随维度指数增长；量化误差；长程多模态难承诺 |
| 混合高斯 (LSTM-GMM/MDN) | $\sum_i \pi_i\mathcal N(\mu_i,\Sigma_i)$ | 模式数已知且固定 | 必须预设模式数；mode collapse；超参敏感 |
| 隐式/能量 (IBC) | $p_\theta(a\mid o)=e^{-E_\theta(o,a)}/Z$ | 用能量刻画多模态 | 归一化常数 $Z$ 不可解 → 负采样估计 → **训练不稳**（Eq 7） |
| 自回归 | $\prod_t p(a_t\mid a_{<t})$ | 动作时序因果 | 误差沿时间累积 |
| **Diffusion Policy** | 条件去噪 $\epsilon_\theta(O,A^k,k)$ | 动作分布 = 可被 score 描述的分布 | 推理需多步去噪（延迟）；不含力/触觉 |

### 1.4 Delta 分析

DP 不是"再加一个生成式 head"。它的精确增量是：**唯一一个同时拿到 (多模态 + 高维动作序列 + 稳定训练) 三者的表示**，靠两个结构决定：

1. **学 score 而非学密度**（绕开不可解的 $Z$，见 §2.4）——这是相对 IBC 的决定性 Delta，把"表达力强但训练不稳"变成"表达力强且训练稳"。
2. **生成的是动作序列 + receding-horizon 执行**——相对单步策略的 Delta，让长程时序一致与闭环响应兼得。

## 2. 核心方法与理论（原理与理论：从零构建扩散策略）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $O_t$ | 最近 $T_o$ 帧观测 | 传感器→视觉 encoder | 观测；encoder 参数 learned | 条件上下文，每次推理只编码一次 | 是**条件**不是被生成量；不进联合分布 |
| $A_t=a_{t:t+T_p}$ | 动作序列，$T_p$ 步 | 示范(训练)/采样器(推理) | target(训练)/computed(推理) | 待生成的动作 chunk | 只执行前 $T_a$ 步（receding horizon）；动作多为位置/末端位姿，**不是力矩** |
| $k$ | 标量 $1..K$ | 噪声调度 | 固定 | 去噪迭代步 | **不是机器人真实时间 $t$**；训练 $K$ 步、DDIM 推理更少步 |
| $\epsilon^k$ | 与 $A$ 同形 | $\mathcal N(0,I)$ 采样 | 固定样本 | 注入噪声（训练目标） | 分布 vs 样本 |
| $\epsilon_\theta(O_t,A^k_t,k)$ | 动作形状 | 去噪网络 | learned (requires_grad) | 预测噪声 $\approx -$score | 近似的是**负 score**，不是动作本身 |
| $\bar\alpha_k,\alpha,\gamma,\sigma$ | 标量 | 噪声调度 | 固定 | 信号/噪声混合比 + 步长 | $\alpha$ 略小于 1 提稳；调度用 Square Cosine |
| $T_o,T_p,T_a$ | 标量 | 设计 | 固定 | 观测/预测/执行 horizon | $T_a\le T_p$；$T_a{=}8$ 多数任务最优 |

### 2.2 前置理论从零推导：DDPM 是什么，为什么去噪等于跟随 score

**目标**：建模数据分布 $p(x^0)$（这里 $x^0$ 是干净动作序列），但高维多模态分布直接建模困难。DDPM 的思路是把"难采样的分布"拆成"一串容易的高斯条件"。

**(1) 前向加噪过程**（固定、无参数），逐步把数据打成高斯噪声：

$$
q(x^k\mid x^{k-1})=\mathcal N\!\big(\sqrt{1-\beta_k}\,x^{k-1},\,\beta_k I\big).
$$

记 $\alpha_k=1-\beta_k$，$\bar\alpha_k=\prod_{s=1}^{k}\alpha_s$。高斯叠加可得**闭式**一步到位：

$$
q(x^k\mid x^0)=\mathcal N\!\big(\sqrt{\bar\alpha_k}\,x^0,\,(1-\bar\alpha_k)I\big)
\quad\Longleftrightarrow\quad
x^k=\sqrt{\bar\alpha_k}\,x^0+\sqrt{1-\bar\alpha_k}\,\epsilon,\;\;\epsilon\sim\mathcal N(0,I).
$$

直觉：$\bar\alpha_k$ 从 1 单调降到 0，$x^k$ 从"几乎是数据"平滑过渡到"纯噪声"。

**(2) 反向去噪过程**（待学）：学 $p_\theta(x^{k-1}\mid x^k)=\mathcal N(\mu_\theta(x^k,k),\sigma_k^2 I)$。DDPM 的关键参数化是**让网络预测被加进去的噪声 $\epsilon$**，而不是直接预测均值：

$$
\mu_\theta(x^k,k)=\frac{1}{\sqrt{\alpha_k}}\Big(x^k-\frac{\beta_k}{\sqrt{1-\bar\alpha_k}}\,\epsilon_\theta(x^k,k)\Big).
$$

**(3) 训练损失**：把上面闭式的 $x^k$ 代入，最小化"预测噪声 vs 真噪声"的 MSE，即本文 **Eq 3**：

$$
\mathcal L=\mathrm{MSE}\big(\epsilon^k,\;\epsilon_\theta(x^0+\epsilon^k,k)\big),
\qquad
(\text{严格写法 } \epsilon_\theta(\sqrt{\bar\alpha_k}x^0+\sqrt{1-\bar\alpha_k}\epsilon^k,k)).
$$

论文指出：最小化 Eq 3 等价于最小化数据分布 $p(x^0)$ 与模型分布之间 KL 的变分上界（VLB）。

**(4) 采样**：从 $x^K\sim\mathcal N(0,I)$ 出发迭代

$$
x^{k-1}=\frac{1}{\sqrt{\alpha_k}}\Big(x^k-\frac{\beta_k}{\sqrt{1-\bar\alpha_k}}\epsilon_\theta(x^k,k)\Big)+\sigma_k z,\;z\sim\mathcal N(0,I).
$$

本文把这一步压缩记成 **Eq 1**：$x^{k-1}=\alpha\big(x^k-\gamma\,\epsilon_\theta(x^k,k)+\mathcal N(0,\sigma^2 I)\big)$，其中 $\alpha,\gamma,\sigma$ 都是 $k$ 的函数（noise schedule）。

**(5) 去噪 = 跟随 score（理论枢纽）**：对前向闭式求 score，

$$
\nabla_{x^k}\log q(x^k\mid x^0)=-\frac{x^k-\sqrt{\bar\alpha_k}x^0}{1-\bar\alpha_k}=-\frac{\epsilon}{\sqrt{1-\bar\alpha_k}}.
$$

因此 $\epsilon_\theta(x^k,k)\approx-\sqrt{1-\bar\alpha_k}\,\nabla_{x^k}\log q(x^k)$——**预测噪声就是在估计负 score**。于是 Eq 1 的去噪步本质是 Langevin/带噪梯度上升，本文 **Eq 2** 把它写成 $x'=x-\gamma\nabla E(x)$：在能量地形上做梯度下降。这正是 §1.2 隐喻的数学形式。

### 2.3 从 DDPM 到 Visuomotor Policy：两处改造，无跳步

DDPM 原本用于图像生成（$x$ 是图像、无条件）。变成策略要改两点：

- **改 1：输出 = 动作序列。** $x^0\to A_t=a_{t:t+T_p}$，即一段未来动作。这样多模态发生在"轨迹级"，并天然适配高维输出空间（扩散模型在图像上已证明对高维 scalable）。
- **改 2：以观测为条件。** 用 DDPM 近似**条件**分布 $p(A_t\mid O_t)$，而不是像 Diffuser(Janner) 那样建联合 $p(A_t,O_t)$ 再 inpaint。条件化后采样不需要推断未来状态，推理更快、精度更高。本文 **Eq 4/5**：

$$
A_t^{k-1}=\alpha\big(A_t^k-\gamma\,\epsilon_\theta(O_t,A_t^k,k)+\mathcal N(0,\sigma^2 I)\big),
\qquad
\mathcal L=\mathrm{MSE}\big(\epsilon^k,\epsilon_\theta(O_t,A_t^0+\epsilon^k,k)\big).
$$

关键工程含义：$O_t$ **不参与去噪过程的加噪**，视觉特征每次推理只提取一次（不随 $k$ 反复编码）→ 大幅降推理延迟、支持视觉 encoder 端到端训练。

**Closed-loop = receding horizon**：每次预测 $T_p$ 步，只执行前 $T_a$ 步再重规划（warm-start 下一次推理）。$T_a$ 太小→反应慢且对延迟敏感；$T_a$ 太大→开环段长、对扰动脆弱。这把"长程一致 vs 闭环响应"做成一个可调旋钮（§3.3 ablation 给出 $T_a{=}8$ 最优）。

### 2.4 概念边界与符号陷阱（为什么扩散稳、IBC 不稳）

这是 DP 相对 IBC 的理论核心，也是最容易被一句"扩散更强"糊弄过去的地方。

隐式策略（IBC）用 EBM 表示动作分布（**Eq 6**）：

$$
p_\theta(a\mid o)=\frac{e^{-E_\theta(o,a)}}{Z(o,\theta)},\qquad Z(o,\theta)=\int e^{-E_\theta(o,a)}\,da .
$$

$Z$ 是对动作的积分、不可解，训练只能用 InfoNCE 负采样近似（**Eq 7**），负采样不准 → 训练不稳。

扩散策略绕开 $Z$：它不估密度，估 score。对 Eq 6 取对动作的对数梯度（**Eq 8**）：

$$
\nabla_a\log p(a\mid o)=-\nabla_a E_\theta(a,o)-\underbrace{\nabla_a\log Z(o,\theta)}_{=\,0}\approx-\epsilon_\theta(a,o).
$$

**关键**：$Z(o,\theta)$ **不依赖 $a$**，所以 $\nabla_a\log Z=0$。score 里那个不可解的常数项被求导直接消掉了——这就是为什么扩散训练（Eq 5）既不需要也不涉及 $Z$，从而**稳定**。一句话：IBC 想要密度（要 $Z$），DP 只要 score（$Z$ 的梯度为 0）。

符号陷阱清单：
- `state`/`observation` 在很多策略论文里是 latent/privileged，本文 $O_t$ 是真实图像+本体感觉。
- `action` 不是力矩；DP 默认输出**位置/末端位姿**（§4.2 证明位置控制显著优于速度控制）。
- 去噪步 $k$ 与机器人时间 $t$ 完全无关；$K_{\text{train}}{=}100$ 而 DDIM $K_{\text{infer}}{=}10$。

### 2.5 信息流/算法机制（无代码）

1. 最近 $T_o$ 帧观测 → 视觉 encoder（per-view 独立、ResNet-18 改 spatial-softmax + GroupNorm）→ 观测特征 $O_t$（只算一次）。
2. 从高斯噪声动作序列 $A_t^K$ 出发，去噪网络 $\epsilon_\theta$ 在 $O_t$ 条件下迭代 $K$ 步预测噪声并相减，得到 $A_t^0$。
   - **CNN backbone**：1D temporal CNN，$O_t$ 与步嵌入 $k$ 通过 **FiLM** 逐通道调制；开箱即用、对超参不敏感；但对高频/急变动作序列因卷积低频偏置而偏弱。
   - **Transformer backbone**（minGPT）：动作 token + 因果 mask，$O_t$ 经 cross-attention 注入；适合高速/急变任务，但更挑超参。
3. 取 $A_t^0$ 前 $T_a$ 步执行，闭环重规划。
4. 评估用成功率 / IoU / 多阶段子目标完成率检验"结构化为分布"是否真的减少了多模态平均与误差累积。

## 3. 训练、数据与实验（实验与验证：数字如何印证故事）

### 3.1 实验设置

| 维度 | 内容 |
|---|---|
| benchmark | Robomimic(5 任务,9 变体,PH/MH)、Push-T、Multimodal Block Push、Franka Kitchen；共 15 任务 / 4 benchmark |
| 观测 | state-based 与 image-based 两套；图像用 2 帧历史 |
| 动作 | 2–14 DoF；DP 用**位置控制**，baseline 用各自最佳（多为速度控制） |
| 训练 | state 4500 epoch / image 3000 epoch；report 最后 10 个 checkpoint 均值，3 seeds × 50 init（共 1500 次） |
| 噪声调度 | Square Cosine (iDDPM) 最佳 |
| 推理 | DDIM：训练 100 步、推理 10 步 → 3080 上 0.1s 延迟 |
| baseline | LSTM-GMM (BC-RNN)、IBC、BeT |

### 3.2 关键结果与因果解释

**仿真 BC benchmark（Table 1 state / Table 2 visual，max / 末10均值）**：

| Backbone | Lift ph | Can ph | Square ph | Transport mh | ToolHang ph | Push-T |
|---|---|---|---|---|---|---|
| LSTM-GMM | 1.00/0.96 | 1.00/0.91 | 0.95/0.73 | 0.62/0.20 | 0.67/0.31 | 0.67/0.61 |
| IBC | 0.79/0.41 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.90/0.84 |
| BeT | 1.00/0.96 | 1.00/0.89 | 0.76/0.52 | 0.38/0.14 | 0.58/0.20 | 0.79/0.70 |
| **DP-C** | 1.00/0.98 | 1.00/0.96 | 1.00/0.93 | **0.68/0.46** | 0.50/0.30 | **0.95/0.91** |
| **DP-T** | 1.00/1.00 | 1.00/1.00 | 1.00/0.89 | **1.00/0.84** | **1.00/0.87** | 0.95/0.79 |

平均 +46.9%。**因果解释**：
- 提升最大的是 **Transport（双臂、长程协调）和 ToolHang（高精度）**——这些任务里"同一状态多个合法动作 + 长时序"最严重，正中 DP 的两个结构（多模态 + 动作序列）。Lift/Can 这种简单任务大家都接近满分，DP 优势小——与 §1.2 隐喻的可证伪断言一致。
- **IBC 在多数任务直接 0.00**：不是表达力不够，而是训练不稳（§2.4 的 $Z$ 问题），印证"绕开 $Z$"才是关键。

**长程多模态（Table 4，multi-stage）**：Block Push p2、Kitchen p4 这类"以任意顺序完成不同子目标"的指标，DP 比 baseline **+32%（BlockPush p2）/ +213%（Kitchen p4）**。因果：长程多模态是"不同子目标顺序"的组合爆炸，回归/单模态策略无法承诺顺序，DP 用轨迹级分布承诺一条连贯子目标序列。

**真实世界**：Push-T DP **0.8 IoU / 0.95 成功** vs IBC 0.14–0.19 / LSTM-GMM 0.20–0.25；Mug Flip（贴近运动学极限的 3D 旋转）DP **0.9** vs LSTM-GMM **0.0**；Sauce Pour DP **0.74 IoU/0.79** vs LSTM-GMM 0.06/0.00；双臂 Egg Beater 55% / Mat Unrolling 75% / Shirt Folding 75%。因果：真实任务普遍带 idle action（停顿）与多阶段切换，单步/单模态策略易过拟合 idle 而卡死，DP 的轨迹分布对此鲁棒。

### 3.3 Ablation 因果链

- **Action horizon（Fig 5 左）**：$T_a$ 从 1 增大 → 性能升（时序一致、抗 idle）；过大 → 性能掉（开环段长、反应慢）。`改变 $T_a$ → 一致性/响应性此消彼长 → $T_a{=}8$ 为多数任务最优`。
- **延迟鲁棒（Fig 5 右）**：`位置控制 + receding horizon → 延迟 ≤4 步仍保持峰值；速度控制对延迟更敏感（误差累积）`。这条直接支撑 §4.2"位置控制优于速度控制"。
- **位置 vs 速度（Fig 4）**：`换成位置控制 → DP 反而更好`。因果：多模态在位置控制下更显著、且位置控制不累积误差，DP 同时吃到这两点红利，而 baseline 反而在位置控制下变差。
- **网络架构**：CNN 开箱即用；`动作急变/高频 → CNN 因低频卷积偏置变差 → 换 Transformer 恢复`，但 Transformer 挑超参。
- **训练稳定（Fig 6）**：IBC 训练误差平滑下降但评估成功率剧烈震荡（选 checkpoint 困难）；DP 平稳——再次指向 $Z$ 问题。
- **视觉 encoder（Table 5）**：端到端从头训 > 用 frozen 预训练 encoder；finetune 预训练 encoder（小 lr）最佳（CLIP ViT-B/16 达 98%）。因果：DP 偏好与主流预训练不同的视觉表征，所以"端到端"比"借现成表征"更重要。

### 3.4 工程约束与实验边界

- **推理延迟 vs 高频控制**：去噪多步推理 + 真实控制频率冲突；DDIM 把推理压到 10 步 / 0.1s（3080）才让闭环可行。WMTS 若上灵巧手高频接触任务，这是头号约束（需 DDIM/consistency distillation）。
- **无力/触觉**：所有任务靠视觉+本体感觉，没有接触力建模；高速接触任务迁移前必须补 tactile/proprioceptive。
- **位置控制依赖**：结论建立在位置/末端位姿动作上；若底层是力矩或阻抗接口，需重新评估。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 论文真正的 insight

**把策略从"函数"升级为"分布"，并且只学这个分布的 score（梯度场）而不学密度本身。** 学 score 让不可解的归一化常数 $Z$ 的梯度恒为 0 而被消掉——这一步把"能量模型表达力强但训练不稳"变成"扩散表达力强且训练稳"。这才是 DP 压过 IBC 的根因，"模型更大/更新"都是表象。

### 4.2 为什么这个设计有效

不是容量更大，而是把难泛化的自由度收进了更合理的结构：(1) 多模态交给随机初始化 + Langevin 采样，自然落进不同 basin；(2) 高维交给"动作序列"，扩散在高维上 scalable；(3) 长程一致 + 闭环交给 receding horizon；(4) 训练稳定交给 score（消 $Z$）。四个瓶颈各自被一个结构吸收。

### 4.3 什么时候会失效

- 高频/高速控制：去噪延迟跟不上。
- 缺触觉/力：视觉相似但接触不同的状态，score 场会混淆（同一图像、不同接触，去噪到同一动作）。
- 强非线性 plant/policy：§4.5 指出此时预测未来动作本身又变成多模态难题。
- 示范质量差：BC 的固有上限，DP 继承（→ 需 RL refinement）。

## 5. 替代方案与理论局限（未来与结合）

### 5.1 理论维度

DP 学的是 $p(A\mid O)$ 的 score，是**行为克隆**，不含奖励/价值/动力学。它不知道 $p(O'\mid O,A)$（world model），也不优化回报。**§4.5 的控制论极限（Eq 9）**给了精确边界：线性系统 $s_{t+1}=As_t+Ba_t+w_t$、模仿线性反馈 $a=-Ks$、$T_p{=}1$ 时，最优去噪器

$$
\epsilon_\theta(s,a,k)=\tfrac{1}{\sigma_k}[a+Ks],\qquad\text{DDIM 收敛到 } a=-Ks .
$$

即 DP 在线性极限下退化为 LQR——这说明 DP 没有超出"模仿一个（可能多模态的）反馈律"的范畴；真正的最优控制/探索仍要靠 RL/MPC。

### 5.2 算法维度

| 替代 | 优点 | 缺点 | 与 DP 关系 |
|---|---|---|---|
| BC-MLP 回归 | 简单、单步快 | 多模态平均 | DP 的 baseline 下界 |
| IBC (EBM) | 多模态表达力强 | $Z$ 不可解 → 不稳 | DP = "学 score 版的 IBC"，消掉 $Z$ |
| BeT/VQ | 离散多模态 | bin 爆炸/量化误差 | DP 用连续 score 替代离散 |
| Diffuser (建联合+inpaint) | 可做 planning | 需推断未来状态、慢 | DP 改成条件分布，免推状态 |
| Flow Matching / Consistency | 推理更快 | 训练/实现更复杂 | DP 的加速替代（WMTS 可用以解延迟） |

### 5.3 工程/实验维度

- 推理步数是延迟瓶颈 → DDIM/consistency/flow。
- 视觉 encoder 偏好端到端，不要盲目套预训练。
- GroupNorm + EMA（不是 BatchNorm），否则与 DDPM 的 EMA 冲突。
- 位置控制 + receding horizon 是性能与抗延迟的关键组合，迁移时不要随手换成速度/单步。

## 6. 对用户研究的启发（未来与结合：迁移到灵巧手/转笔/WMTS）

### 6.1 对 WMTS / 灵巧手转笔 / PPO / Sim-to-Real 的迁移

| 位置 | 用法 | 适合场景 | 风险/对策 |
|---|---|---|---|
| WMTS generalist（核心定位） | DP 作低层 action prior，ensemble world model 对 DP 采样的 chunk 做筛选/微调（DiWA/World4RL 路线） | 从 Oracle/示范蒸馏多模态灵巧动作 | 推理慢→DDIM/consistency；chunk 要与 contact phase 对齐 |
| PPO Oracle 蒸馏目标 | 用 PPO 专家轨迹训 DP generalist，再交给 world model | 把 PPO 的单峰高斯探索结果固化成多模态 prior | DP 是 IL，不解决探索；探索仍归 PPO |
| 转笔动作生成 | 动作 chunk = 一段转笔相位（snap/spin/catch） | 多模态指法（左旋/右旋）需承诺单一模式 | 缺触觉时 score 混淆→必须把 tactile 进 $O_t$ |

**对转笔的具体 value-add**：转笔同一手姿可左旋可右旋，回归策略会输出"两者平均"的废动作；DP 能在一次 rollout 承诺一个旋向。这正是 §1.2 隐喻在转笔上的实例。

### 6.2 可验证实验建议

- 最小手内重定向/转笔环境，比较三组：PPO-MLP actor（单峰）、DP generalist、DP 但**打乱 $O_t$ 里的接触通道**（负对照）。看 DP 的多模态优势是否依赖接触信息。
- $T_a$ 扫描（1/4/8/16）× 真实控制延迟注入，复刻 Fig 5，确认灵巧手上 receding horizon 的最优窗口。
- 记录 failure mode：掉笔、打滑、动作饱和、world model 对 DP chunk 过度自信。

### 6.3 不应过度外推的点

- 不要因为 DP 在视觉操作/双臂上强，就默认它能处理多指高速接触——它没有力/触觉、推理慢。
- 不要把 DP 当 world model 或 planner：它只建 $p(A\mid O)$，不建动力学、不优化回报（§5.1 的 LQR 边界）。
- WMTS 里 DP 是 generalist，**不是** task scheduler，也不替代 PPO Oracle 的探索。

## 7. 与知识体系的联系

### 与 [[StochasticProcess]] 的联系
DP 是扩散/score 理论在动作空间的落地（[[StochasticProcess#6.4 扩散策略 = 学出来的逆向 SDE：把 §2 的 SDE 倒过来跑]]）：前向 $q(x^k\mid x^0)=\mathcal N(\sqrt{\bar\alpha_k}x^0,(1-\bar\alpha_k)I)$、去噪 = Langevin（Eq 1/2）、$\epsilon_\theta\approx-$score。可与 MPPI/路径积分（[[StochasticProcess#6.2 物理根：自由能最小化与重要性采样]]）对照：两者都在"动作/轨迹分布上采样"，但 MPPI 用 reward 加权重要性采样、DP 用学来的 score。

### 与 [[RepresentationLearning]] 的联系
DP 正是 [[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器]] 的算法原型：把模仿学习从"均值回归"升级为"分布建模"，用去噪迭代当轨迹优化器解决多峰与协变量漂移。§2.2 的 EBM→score 消 $Z$ 推导（[[RepresentationLearning#2.2.2 噪声预测 $\epsilon_\theta$ ↔ denoising score matching 的等价（补严）]]）与本文 §2.4 是同一件事的两处讲法。

### 与 [[ReinforcementLearning]] 的联系
§2.4 给出 EBM/IBC 与扩散的对偶（[[ReinforcementLearning#10.1 扩散策略：多峰分布的终极解（兑现 §5.1.2 的伏笔）]]）：隐式策略要 $Z$（Eq 6-7，不稳），扩散学 score 消 $Z$（Eq 8，稳）。DP 是 IL，RL refinement（[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]、[[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]）在其上加回报优化，属 [[ReinforcementLearning#10.2 世界模型 RL：隐空间 vs 像素空间]]。

### 与 [[ControlTheory]] 的联系
§4.5 / Eq 9：线性系统 + $T_p{=}1$ 下 DP 退化为 LQR 反馈 $a=-Ks$。这给扩散策略一个控制论下界，也说明它不超出"模仿反馈律"的范畴。

### 与 [[EmbodiedAI]] 的联系
DP 是 visuomotor IL 的 action backbone 范式：视觉条件 + 动作序列 + 闭环，是 VLA/操作策略的标准低层组件之一。

### 与 [[Final_WMTS]] 的联系
DP 占据 WMTS 流水线的 generalist 槽位：PPO Oracle 探索 → DP 蒸馏成多模态 prior → ensemble world model 筛/调 chunk → 真机微调。延迟与缺触觉是迁移到灵巧手的两大约束。

## References
- 原始 PDF：[[Diffusion Policy: Visuomotor Policy.pdf]]
- 关键前作：DDPM (Ho et al. 2020)、iDDPM 噪声调度 (Nichol & Dhariwal 2021)、DDIM (Song et al. 2021)、IBC (Florence et al. 2021)、Diffuser (Janner et al. 2022)、score-based (Song & Ermon 2019)
- 项目入口：[[Final_WMTS]]
- 簇内关系（Delta）：
  - vs [[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]：DP 是纯 BC 动作扩散（只学 $p(A\mid O)$）；DiWA 在其上套 world model，用 PPO 在 dream 里精炼 DP（加回报优化）。
  - vs [[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]：同为"WM 精炼 DP"，但 World4RL 把 WM 从 RSSM 换成扩散转移模型，且明确压 model-exploitation。
  - vs [[Beyond Human Demonstrations- Diffusion-Based Reinforcement Learning to Generate Data for VLA Training|Diffusion RL for VLA Data]]：DP 从人类示范 BC 训练；后者用 diffusion RL 自动生成低方差数据反过来训 generalist，胜过人类数据。
  - vs [[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]]：DP 直接回归动作；DexWM 把灵巧 WM 当 MPC planner，zero-shot 超 DP 50%+，指出"BC 直接出动作"泛化弱。
- 相关 recap：[[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]、[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]、[[Beyond Human Demonstrations- Diffusion-Based Reinforcement Learning to Generate Data for VLA Training|Diffusion RL for VLA Data]]
