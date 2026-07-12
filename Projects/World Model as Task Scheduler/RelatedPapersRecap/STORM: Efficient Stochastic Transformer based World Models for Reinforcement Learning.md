---
tags:
  - paper
  - world-model
  - transformer
  - model-based-rl
  - sample-efficiency
  - WMTS
aliases:
  - STORM
  - Stochastic Transformer-based World Model
paper-year: 2023
read-date: 2026-06-15
venue: NeurIPS 2023 (arXiv 2310.09615, BIT / 黄高 Tsinghua)
paper-pdf: "[[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[Final_WMTS]]"
---

# STORM: Efficient Stochastic Transformer based World Models for RL

> [!abstract] 核心贡献
> 把 [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]/DreamerV3 的"latent imagination 训 actor-critic"骨架保留，**把序列模型从 GRU 换成 GPT 式 Transformer**，并配 **categorical VAE**（单个随机 latent token 表示一帧 + 把动作与 latent 融成一个 token）。这套 Stochastic Transformer 在 Atari 100k 上拿到 **126.7% 平均人类归一化分**（不用 lookahead/MCTS 的新纪录），且 1.85 小时游戏经验只需单卡 RTX 3090 训 **4.3 小时**（V100 上 11.9 FPS，快于 DreamerV3 的 9.3、远快于 IRIS 的 0.7）。**它对 WMTS 不是任务迁移（是 Atari 离散像素游戏、无接触无连续控制），而是 world-model 主干的设计与效率参照：Transformer 注意力显式保留历史、单随机 token 省算力、categorical 随机性抑制 autoregressive 误差累积与"追逐虚拟目标"——后者正对应贯穿 DiWA/World4RL 的 model-exploitation 主题。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — model-based RL；纯 imagination 内训 actor-critic（沿用 DreamerV3 的 λ-return + reinforce + 百分位归一化 + EMA critic）。
> - [[StochasticProcess]] — categorical VAE（32×32）+ straight-through 梯度；dyn/rep KL 拆分；随机 latent 序列。
> - [[WorldModels#2.1 演进脉络：从 Dyna 到 RSSM 到 Transformer 世界模型]] — STORM 正是这条演进脉络的**Transformer 世界模型**终点（Dreamer 的 RNN-RSSM → STORM 的 GPT 序列主干）；categorical 随机性抗 autoregressive 误差累积对应 [[WorldModels#3. 不确定性层：模型何时在"自信地瞎编"]]。
> - [[Final_WMTS]] — **WMTS ensemble world model 的"主干选型"参照**：序列模型用 Transformer 而非 RNN，单随机 token，随机性抗误差累积。
>
> **核心技术**: GPT-like Transformer 序列模型, Categorical VAE (32×32, 单 token), Action-Latent 融合 token, symlog two-hot reward, dyn/rep KL 平衡, λ-return imagination, KV cache

## 0. 阅读定位与范本价值

STORM 在知识库里是 **WM 主干的"架构 + 效率"参照**，**不是**机器人/接触论文——它跑 Atari 100k（26 个 2D 离散动作像素游戏）。所以读它的正确姿势不是问"能否迁到灵巧手"，而是问"**WMTS 的 world model 序列主干该用什么、为什么**"。

它直接坐在 [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]→DreamerV3 这条线后面，只改一件事——**把 GRU 换成 Transformer**，并清理了 IRIS（多 token 慢）、TWM（obs/action/reward 三 token、Transformer-XL）、TransDreamer（直接替换但缺基准证据）的设计冗余。它的价值=用一张对照表（Table 1）+ Atari 实测，告诉你"高效的 Transformer WM 该长什么样"。它与库内"Transformer 作为序列/表征引擎"的一族（IS ATTENTION REQUIRED FOR ICL、Transformers as Meta-Learners）互为印证。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
model-based RL 靠 world model 想象提样本效率，但**想象是 autoregressive 的、会累积预测误差**，误差大时 agent 会"追逐虚拟目标"。STORM 主张：用 **Transformer**（强序列建模 + 可并行 + 长程依赖）+ **categorical VAE 的随机性**（抑制误差累积、增鲁棒）来造一个又准又快的 WM，从而在极少样本（100k）下刷新非 lookahead 方法的纪录。

### 1.2 直观隐喻
RNN（GRU）像"用一个不断被覆写的小本子记历史"——久了会忘、且只能逐格写（不能并行）；Transformer 像"摊开整段历史用注意力随时回看"——移动物体的速度/方向一望即知，且整段并行训练。再给 latent 加一点"受控随机噪声"（categorical VAE），等于让梦境别太死板地一路推到虚假目标上。

可证伪含义：Transformer 的优势应集中在"**需要回看历史、有多个/大的运动物体**"的场景（Atari 的 Amidar/MsPacman/Chopper/Gopher 实测最强）；而"单个小运动物体"（Pong/Breakout）上 autoencoder + 采样随机性反而拖累——这条强弱边界论文如实给出。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 序列模型 / 表征 | 关键局限 |
|---|---|---|
| SimPLe | LSTM / Binary-VAE | RNN 慢；有限样本下性能低 |
| DreamerV3 | **GRU** / Categorical-VAE | RNN 递归不可并行 → 训练慢；长程依赖弱 |
| IRIS | Transformer / VQ-VAE（**4×4=16 token**） | 多 token 时空注意力 → 训练极慢（0.7 FPS） |
| TWM | Transformer-XL / Categorical | obs/action/reward **三独立 token** → token 多、异质注意力伤性能 |
| TransDreamer | Transformer 直替 GRU | 缺公认基准/有限样本下的证据 |
| **STORM** | **GPT-like Transformer / Categorical-VAE（单 token）** | Atari 离散像素；小运动物体弱；像素重构对接触/力不敏感 |

### 1.4 Delta 分析
精确增量 = **在 DreamerV3 骨架上把 GRU 换成 vanilla GPT-Transformer + 三处极简化**：(1) **单个**随机 latent token 表示一帧（vs IRIS 16 token）；(2) **obs 与 action 融成一个 token**（action mixer，vs TWM 三 token）；(3) **重构不使用历史 hidden state**（vs Dreamer/TransDreamer），降低分布动力学学习难度。结果是又快（11.9 FPS）又准（126.7%）。

## 2. 核心方法与理论（原理与理论：Transformer WM 怎么搭）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $o_t,\hat o_t$ | 图像 | 环境 / decoder | 观测 / 重构 | Atari 帧 | 像素重构，对接触无感 |
| $z_t\sim Z_t$ | categorical（32×32） | encoder $q_\phi$ | learned（straight-through） | 单 token 随机 latent | 离散随机，非高斯 |
| $a_t$ | 离散动作 (≤18) | 策略 | 选择 | Atari 动作 | **离散**：无 analytic value gradient |
| $e_t=m_\phi(z_t,a_t)$ | 单 token | action mixer | learned | obs+action 融合 token | 一帧一 token（高效关键） |
| $h_t=f_\phi(e_{1:t})$ | hidden | GPT Transformer | learned | 因果注意力历史摘要 | causal mask；推理用 KV cache |
| $\hat Z_{t+1}=g_\phi^D(h_t)$ | prior 分布 | dynamics 头 | learned | 预测下一 latent | imagination 时从 **prior** 采，非 posterior |
| $\hat r_t,\hat c_t$ | 标量 / 布尔 | reward/continuation 头 | learned | symlog two-hot 奖励 / 终止 | 奖励用分类式回归 |
| $s_t=[z_t,h_t]$ | agent state | 拼接 | — | actor/critic 输入 | latent + 注意力摘要 |
| $G_t^\lambda,V_\psi,\pi_\theta$ | λ-return / 价值 / 策略 | imagination | learned | DreamerV3 式 AC | 见 §2.3 |

### 2.2 world model 结构与损失（无跳步，Eq 1-5）

**结构（Eq 1-2）**：
$$
\text{encoder: } z_t\sim q_\phi(z_t\mid o_t)=Z_t,\quad \text{decoder: } \hat o_t=p_\phi(z_t),
$$
$$
\text{action mixer: } e_t=m_\phi(z_t,a_t),\quad \text{序列: } h_{1:T}=f_\phi(e_{1:T}),
$$
$$
\text{dynamics: } \hat Z_{t+1}=g_\phi^D(h_t),\quad \text{reward: } \hat r_t=g_\phi^R(h_t),\quad \text{continuation: } \hat c_t=g_\phi^C(h_t).
$$
$f_\phi$ 是 GPT 式 Transformer（causal mask，$e_t$ 只看 $e_{1..t}$）。categorical $Z_t$ 用 32 类别×32 class，straight-through 保梯度。

**损失（Eq 3-5）**：$\;L(\phi)=\frac1{BT}\sum_{n,t}\big[L^{rec}+L^{rew}+L^{con}+\beta_1 L^{dyn}+\beta_2 L^{rep}\big]$（$\beta_1{=}0.5,\beta_2{=}0.1$）：
- $L^{rec}=\|\hat o_t-o_t\|^2$（重构）；
- $L^{rew}=L^{sym}(\hat r_t,r_t)$（**symlog two-hot**，把回归转成分类，跨环境尺度一致——承自 DreamerV3）；
- $L^{con}$ = continuation 的 BCE；
- **dyn/rep KL 拆分（关键）**：
$$
L^{dyn}=\max\!\big(1,\ \mathrm{KL}[\,\mathrm{sg}(q_\phi(z_{t+1}\mid o_{t+1}))\ \|\ g_\phi^D(\hat z_{t+1}\mid h_t)\,]\big),
$$
$$
L^{rep}=\max\!\big(1,\ \mathrm{KL}[\,q_\phi(z_{t+1}\mid o_{t+1})\ \|\ \mathrm{sg}(g_\phi^D(\hat z_{t+1}\mid h_t))\,]\big).
$$
$L^{dyn}$ 让**序列模型去逼近 encoder 的后验**（学预测），$L^{rep}$ 让 encoder 的输出被预测**弱牵引**（别让动力学太难学）；stop-grad + 不同权重 = DreamerV3 的 KL-balancing，free-bits=1。

### 2.3 agent 学习（纯 imagination，Eq 6-10，沿用 DreamerV3）
从 replay 取短 context → 算后验 $Z_t$ → **想象时从 prior $\hat Z_t$ 采** $z_t$（KV cache 加速）。state $s_t=[z_t,h_t]$；critic $V_\psi(s_t)\approx\mathbb E[\sum_k\gamma^k r_{t+k}]$；actor $a_t\sim\pi_\theta$。
- **actor（Eq 7a）**：reinforce 式 $-\mathrm{sg}\!\big(\frac{G_t^\lambda-V_\psi}{\max(1,S)}\big)\ln\pi_\theta - \eta H(\pi_\theta)$；
- **critic（Eq 7b）**：回归 $G_t^\lambda$ + EMA 正则；
- **λ-return（Eq 8）** $G_t^\lambda=r_t+\gamma c_t[(1-\lambda)V_\psi(s_{t+1})+\lambda G_{t+1}^\lambda]$；
- **归一化 $S$（Eq 9）** = batch 内 $G_t^\lambda$ 的 95% 与 5% 分位差；**EMA critic（Eq 10）** 稳训练。

> 符号陷阱：Atari 动作**离散**，所以这里是 **reinforce（score-function）梯度**，不是 Dreamer 连续控制的 analytic value gradient——别误以为 STORM 穿 dynamics 反传。

### 2.4 概念边界与符号陷阱
- STORM 的 "world model" = **像素级 latent imagination**（重构帧 + 预测下一 latent），不是 [[DyWA: Dynamics-adaptive World Action Model|DyWA]] 的一步任务状态回归，也不是 [[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]] 的像素扩散——同名不同义。
- imagination 时从 **prior** 采（不看观测），与 Dreamer 一致。
- categorical 随机性是论文反复强调的"抗误差累积/抗追逐虚拟目标"机制——**stochasticity 当正则**。
- 单 token / 不用历史 hidden 重构是**效率与可学性**的取舍，非性能上限。

## 3. 训练、数据与实验（实验与验证）

### 3.1 实验设置
Atari 100k：26 游戏、100k 交互步（=400k 帧，4 帧跳，≈1.85h 游戏）。人类归一化分 $\tau=(A-R)/(H-R)$。5 seeds，每 2500 步存 checkpoint，20 episode 评测。**不与 MCTS/lookahead（MuZero/EfficientZero）比**——目标是改进 WM 本身。

### 3.2 关键结果与因果解释
- **平均 126.7%（中位 58%）**，非 lookahead 新纪录；优于 DreamerV3、IRIS、TWM、SimPLe（Fig 1）。
- **效率（V100 FPS）**：STORM **11.9** > DreamerV3 9.3 ≫ TWM 5.6 ≫ IRIS 0.7、SimPLe 0.5。**因果**：单 token + vanilla Transformer + 并行训练，避开 IRIS 多 token、TWM 三 token 的注意力开销与 RNN 的串行。
- **强弱边界（Table 2 因果）**：大/多运动物体（Amidar 205、Chopper 1888、Gopher 8240）**最强**——`注意力显式保留运动物体历史 → 易推速度/方向`；单个小运动物体（Breakout 16 vs IRIS 84、Pong）**弱**——`autoencoder 难抓小物体 + 采样随机性扰乱注意力权重`。
- **Freeway w/o traj → 0**：去掉引导轨迹后纯探索学不出（稀疏奖励 + 随机探索难），提示 WM 不解决探索本身。

### 3.3 Ablation / 对照因果链（Table 1 即设计消融）
- `GRU→Transformer`：并行 + 长程 → 更快更准。
- `多 token（IRIS）→ 单 token`：去掉时空注意力开销 → FPS 飙升。
- `三 token（TWM）→ obs+action 融合单 token`：避免异质 token 间注意力互扰。
- `用历史 hidden 重构（Dreamer）→ 不用`：降低分布动力学学习难度。
- `去 categorical 随机性 → autoregressive 误差累积、追逐虚拟目标`（论文动机级论证）。

### 3.4 工程约束与实验边界
- Atari 2D 离散像素游戏：**无连续控制、无接触/力、无 sim-to-real**。
- 像素重构算力非零；小运动物体是已知弱项。
- 纯 imagination 训 agent，但不解决探索（Freeway 需引导轨迹）。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 论文真正的 insight
**在 Dreamer 式 latent-imagination 骨架里，用 vanilla GPT-Transformer + 单个 categorical 随机 token 取代 GRU，既显著提速又提分**——证明 WM 的瓶颈很大程度在**序列主干的并行性与历史可回看性**，而随机性（categorical VAE）是抑制 autoregressive 误差累积、防"追逐虚拟目标"的关键正则。

### 4.2 为什么这个设计有效
(1) Transformer 注意力显式保留历史 → 运动物体的速度/方向易推；(2) 可并行 → 训练快；(3) 单 token + 不用历史 hidden → 省算力、降学习难度；(4) categorical 随机性 → 抗误差累积；(5) symlog two-hot + dyn/rep KL 平衡 → 跨环境稳定（DreamerV3 遗产）。

### 4.3 什么时候会失效
- 单个小运动物体：autoencoder 抓不住 + 采样随机扰动注意力。
- 纯探索难题（稀疏奖励无引导）：WM 不解决探索。
- 像素重构对**接触/力**不敏感：不能直接服务接触密集任务。

## 5. 替代方案与理论局限（未来与结合）

### 5.1 理论维度
STORM 是 latent-imagination model-based RL：性能受 WM 保真度与 autoregressive 误差限；categorical 随机性是经验性正则，非形式化误差界。Atari 离散动作下用 reinforce，不涉及连续控制的 analytic gradient 风险。

### 5.2 算法维度
| 方法 | 优点 | 缺点 | 与 STORM 关系 |
|---|---|---|---|
| DreamerV3（GRU） | 通用、稳 | RNN 串行慢、长程弱 | STORM 的骨架来源，换主干 |
| IRIS（Transformer+VQ，多 token） | 高保真 token | 极慢（0.7 FPS） | STORM 用单 token 提速 |
| TWM（Transformer-XL，三 token） | 长上下文 | token 多、异质注意力 | STORM 融合单 token |
| MuZero/EfficientZero（MCTS） | lookahead 强 | 算力高 | STORM 不比，可叠加 |

### 5.3 工程/实验维度
像素重构算力、小物体弱项、探索不解决、离散动作设定是主要边界；接触/触觉/连续控制全未覆盖。

## 6. 对用户研究的启发（未来与结合：WMTS 的 WM 主干选型）

### 6.1 对 WMTS / 灵巧手的迁移（架构层，非任务层）

| WMTS 模块 | STORM 对应 | 迁移设计 |
|---|---|---|
| **Ensemble world model 主干** | GPT-Transformer 序列模型 | WMTS 的 WM 用 Transformer 而非 RNN：注意力回看**接触事件/触觉序列**历史，推接触建立-断开的时序 |
| latent 表示 | 单 categorical token | 灵巧手 latent 需编码**接触/力**；可保留单 token 高效性，但表征要含触觉 |
| 抗误差累积 | categorical 随机性 | WMTS 用 **ensemble disagreement + 随机性**双管抑制 autoregressive 误差与 model-exploitation |
| 推理效率 | KV cache | 高频灵巧手 WM rollout 需同样的推理加速 |

**核心论证（critical thinking）**：STORM 给 WMTS 的是**主干工程**而非任务证据。三条可直接用：(1) **Transformer > RNN**——WMTS 的 WM 要在长接触序列上回看历史，注意力比 GRU 合适，且可并行训练；(2) **单随机 token 的效率**——但灵巧手的"一帧"必须把**接触/力/本体**编码进去，否则像 STORM 在小物体上失手一样，会在精细接触上失真；(3) **随机性抗误差累积**——STORM 用 categorical 噪声，WMTS 更该用 **ensemble**（多个 WM 的 disagreement 既抗误差累积又给 uncertainty，正是 DiWA/World4RL 单 WM 缺的）。**但必须警惕过度外推**：STORM 是 2D 离散像素游戏、像素重构、reinforce——它**没有**接触、力、连续控制、sim-to-real，其 126.7% 与灵巧手难度不可比。WMTS 取其主干思想，不取其任务结论。

### 6.2 可验证实验建议
- WM 主干 A/B：在手内任务上对照 **GRU-WM vs Transformer-WM（含触觉序列 token）**，测长接触序列的预测保真与 rollout 误差累积。
- 随机性 vs ensemble：对照 STORM 式单 WM-categorical 噪声 vs WMTS ensemble，测想象-真实回报 gap 与 model-exploitation。
- KV cache 加速：测 Transformer-WM 在灵巧手控制频率下的 rollout 推理延迟是否可接受。

### 6.3 不应过度外推的点
- Atari 像素游戏成绩**不能**外推到接触密集连续控制。
- 单 token 像素 latent 对接触/力不敏感，灵巧手需触觉一等输入。
- categorical 随机性是正则，不等价于 WMTS 需要的**可量化 uncertainty**（要 ensemble）。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
model-based RL 纯 imagination 训 actor-critic：λ-return（Eq 8）+ reinforce actor（Eq 7a，离散）+ 百分位归一化 + EMA critic——DreamerV3 的算法在 Transformer WM 上的实例。

### 与 [[StochasticProcess]] 的联系
categorical VAE（32×32）+ straight-through 梯度；dyn/rep KL 拆分（Eq 5）是 ELBO/KL-balancing；想象从 prior 采，随机 latent 序列建模。

### 与 [[WorldModels]] 的联系
STORM 是 [[WorldModels#2.1 演进脉络：从 Dyna 到 RSSM 到 Transformer 世界模型]] 里 **RSSM→Transformer** 那一跳的代表——把 [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]] 的 GRU 换成 GPT 序列主干，注意力显式回看历史。它用 categorical 随机性抑制 autoregressive 误差累积、防"追逐虚拟目标"，是 [[WorldModels#3. 不确定性层：模型何时在"自信地瞎编"]] 的**随机性正则**一路（区别于 WMTS 要的 ensemble/可量化 uncertainty）；训策略仍在 [[WorldModels#4. 利用层：想象里"练策略"还是"规划动作"]] 的 Dream-RL 一支内。

### 与 [[Final_WMTS]] 的联系
WMTS ensemble world model 的"序列主干 + 表征 + 抗误差累积"工程参照：Transformer 回看历史、单随机 token 高效、随机性/ensemble 抑制 autoregressive 误差与 model-exploitation。

## References
- 原始 PDF：[[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning.pdf]]（NeurIPS 2023，arXiv 2310.09615）
- 骨架来源：[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]/DreamerV3（GRU、λ-return、symlog two-hot、KL balancing）
- 对照 Transformer WM：IRIS（VQ-VAE 多 token）、TWM（Transformer-XL 三 token）、TransDreamer
- 同主题（Transformer 序列/表征）：库内 "IS ATTENTION REQUIRED FOR ICL?"、[[Transformers as Meta-Learners for Implicit Neural Representations]]
- 项目入口：[[Final_WMTS]]
