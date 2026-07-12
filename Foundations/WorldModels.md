---
tags:
    - foundation
    - world-models
    - model-based-rl
    - dexterous-manipulation
    - sim-to-real
aliases:
    - 世界模型
    - World Model
    - World Models
    - MBRL
    - Model-Based RL
    - Dreamer
    - RSSM
    - PETS
    - TD-MPC
    - Dyna
created: 2026-07-12
related:
    - "[[ReinforcementLearning]]"
    - "[[Dynamics]]"
    - "[[StochasticProcess]]"
    - "[[Optimization]]"
    - "[[Actuation]]"
    - "[[InformationTheory]]"
---

# 灵巧操作中的世界模型：从想象中的转笔到真机安全调度

# World Models for Dexterous Manipulation: From Imagined Pen-Spinning to Real-World Safe Scheduling

> [!tip] 相关领域
> - [[ReinforcementLearning]] — 世界模型是 Model-Based RL 的引擎（[[ReinforcementLearning#6.1 Model-Based RL：在想象中转笔|§6.1]]）；它把"在真机试错"换成"在想象里试错"，是样本效率的终极杠杆
> - [[Dynamics]] — 世界模型是**学出来的**动力学 $p(s_{t+1}\mid s_t,a_t)$；[[Dynamics#9. 适配层：可微物理与神经动力学|神经动力学 §9]]是它的物理先验版本，二者在"残差 + 结构"上同源
> - [[StochasticProcess]] — 预测必须带**认知不确定性**（[[StochasticProcess#3.1 三类不确定性|epistemic vs aleatoric]]），否则优化器会钻模型的空子；ensemble/PETS 是核心工具
> - [[Optimization]] — 有了模型就能规划：[[Optimization#7. 实时闭环：模型预测控制 (MPC)|MPC]] 在模型里前瞻 $H$ 步；TD-MPC 把它与值函数缝合
> - [[Actuation]] — 高保真世界模型必须把[[Actuation#10. 迁移层 II：数据驱动执行器模型 (Actuator Model)|执行器模型]]与刚体动力学解耦，否则"仿真关节虚拟力矩"的谎言会进入想象
> - [[InformationTheory]] — ensemble 预测**分歧**＝epistemic 不确定性＝信息增益，可反过来驱动**主动学习/课程生成**（本讲 §6 与 WMTS 的核心洞见）
>
> **贯穿母题**：**在脑内转笔 (spinning the pen in imagination)**。策略要学转笔，但真机每次试错都磨损硬件、甚至拧断手指。世界模型是一台**学出来的"脑内物理引擎"**：先在想象里转千百次，把危险探索关在脑内，再上真机。全讲每引入一个概念，都回到这支想象的笔：**"世界模型能可靠地想象这一步吗？它会在哪里骗策略？"**

## 0. 母题与理论大厦构建路线：从想象试错到真机安全调度

> [!abstract] 为什么用"在脑内转笔"做母题？
> [[ReinforcementLearning|无模型 RL]]（SAC/PPO）要在真机上试错百万步——对灵巧手意味着数周时间与不可逆磨损。世界模型的野心是：**把绝大部分试错搬进一个学出来的模型里**。但"脑内引擎"有它自己的病：
> - 高维触觉/视觉观测怎么压成一个**可预测**的紧凑状态？（否则想象一步就误差爆炸）→ 表征层
> - 转笔时手指频繁**遮挡**笔身，单帧看不全 → 想象必须有**记忆**（RSSM）→ 预测层
> - 模型在没见过的接触边界会**自信地瞎编**，优化器专挑这种漏洞 → 想象必须**知道自己不知道**→ 不确定性层
> - 有了模型，是"在想象里练策略"还是"在想象里规划动作"？→ 利用层
> - 想象里转得漂亮、真机上笔飞出去——怎么让脑内引擎**守物理律**？→ 结构层（这正是 [[Final_WMTS|WMTS]] 把 WM 拆成 Actuator + Rigid 的动机）
> - 真机上，怎么用世界模型**兜底**（拦截危险动作）、并用它的**无知**反过来**生成课程**？→ 部署层
>
> 全讲每引入一个概念，都回到这支想象的笔。

世界模型的主线，是把"预测未来"从一个感知问题，提升为一个**可规划、可量化不确定、可安全部署**的决策基础设施。六层大厦，每层回答一个更尖锐的问题：

| 层级 | 关键问题 | 理论工具 | 脑内转笔母题的映射 | 讲稿位置 |
|:--|:--|:--|:--|:--|
| **表征层** | 高维观测怎么压成可预测状态？ | latent state、VAE、重构 vs 对比、RSSM | 触觉+视觉→紧凑 latent | §1 |
| **预测层** | 如何在 latent 里推演未来？ | transition model、RSSM 确定+随机、Transformer/扩散 WM | 想象被遮挡的笔的下一帧 | §2 |
| **不确定性层** | 模型何时在瞎编？ | ensemble/PETS、epistemic vs aleatoric、disagreement | 别在没见过的接触边界瞎想 | §3 |
| **利用层** | 有了模型怎么用？ | Dyna 想象训练 vs MPC 规划 vs Dreamer latent actor-critic | 脑内练策略 / 脑内前瞻 | §4 |
| **结构层** | 怎么让想象物理真实？ | physics-informed、残差、Actuator+Rigid 解耦、显式 vs 隐式 | 让脑内引擎守物理律 | §5 |
| **部署层** | 真机上怎么安全用？ | 安全滤波、dream RL 对抗风险、在线适配、不确定性驱动课程 | 想象兜底真机 + 无知生成课程 | §6 |

> [!important] Foundation 级判断标准（任何世界模型进入本库都要回答四问）
> 1. **在哪个空间预测**（像素 / 隐空间 / 物理状态）？这决定了误差如何累积、能否对齐感知。
> 2. **不确定性怎么建**（单模型熵只抓 aleatoric，ensemble 才抓 epistemic）？没有它，规划=自欺。
> 3. **怎么用**（想象里训策略 / 规划动作 / 二者混合）？
> 4. **物理律怎么进来**（纯数据黑箱 / 残差 / 结构解耦）？这决定了长 horizon 想象会不会"物理穿帮"。

> [!note] 本讲在知识图谱中的位置（依赖 / 被依赖）
> ```
>   [[Dynamics]] ─学出来的 f──┐                    ┌── imagination rollout ──> [[ReinforcementLearning]]
> [[Actuation]] ─actuator model─┤                   │
> [[StochasticProcess]] ─ensemble/epistemic─┼──> 【World Models】 ──规划 H 步──> [[Optimization|MPC]]
>                            │                       │
>          ensemble 分歧=信息增益 <──[[InformationTheory]]┘   └── 认知不确定性驱动课程 ──> 自动课程/主动学习
> ```
> 读法：左侧给世界模型喂动力学结构、执行器映射、不确定性语言；右侧消费它——rollout 进 RL、规划进优化、无知进课程生成。

---

## 1. 表征层：把高维观测压成"可预测"的状态

> [!tip] 本节四拍
> **直觉**（原始像素/360 维触觉太高维，直接预测下一帧＝预测噪声）→ **推导**（latent state + 编码器；重构 vs 对比两条压缩路线）→ **对比**（为预测而压 vs 为重构而压）→ **联系**（与 [[RepresentationLearning]] 的 VAE/对比、[[StochasticProcess]] 的 belief 同一件事）。

世界模型第一步不是预测，而是**压缩**：学一个编码器 $z_t = e_\phi(o_t)$（或 $e_\phi(o_{\le t})$），把高维观测 $o_t$（图像、$5\times12\times6$ 触觉张量）压成低维 latent $z_t$，让"预测未来"在 $z$ 上进行。

**为什么必须先压缩**（不跳步）：若直接学 $p(o_{t+1}\mid o_t,a_t)$，模型要预测每个像素/taxel——其中绝大部分是与决策无关的纹理噪声。预测噪声既浪费容量，又让误差在 rollout 中指数放大。压到 $z$ 上，模型只需预测**决策相关**的少数自由度（笔的位姿、接触状态）。

**两条压缩路线**（对应 [[RepresentationLearning]] 的两大范式）：

| 路线 | 目标 | 代表 | 灵巧操作含义 |
|:--|:--|:--|:--|
| **重构式** | $z$ 要能解码回 $o$（$p(o_t\mid z_t)$） | World Models (Ha 2018)、Dreamer | 信息完整，但可能保留无关细节 |
| **对比/预测式** | $z$ 只需保留**能预测未来**的信息 | TD-MPC、DINO-WM | 更紧凑，直接对齐控制目标 |

> [!important] 世界模型的状态就是一个学出来的 belief（回扣 POMDP）
> [[ReinforcementLearning#2.1 MDP 与 POMDP：把"试错"写成数学|POMDP]] 里的信念 $b_t=p(x_t\mid o_{\le t})$ 是理论理想；世界模型的 latent $z_t$ 就是它的**神经近似**。转笔时手指遮挡笔身——单帧 $o_t$ 是部分可观测的，只有把历史压进 $z_t$ 才能推断被遮挡的笔的位姿。这条线在 §2 的 RSSM 里被兑现。
>
> **谁是这个 belief 更新器的"解析祖先"**：在线性高斯世界里，belief 递推有闭式解——[[SignalProcessing#5. 状态估计：从局部触觉到全局语义|卡尔曼滤波 (KF)]] 就是精确的 $b_t$ 传播，粒子滤波 (PF) 则用样本表达非高斯 $b_t$。世界模型没有解析动力学可用，于是把这台"滤波器"整台**学出来**：编码器 $e_\phi$ 承担 KF 的"更新 (correction)"步（用观测 $o_t$ 修正信念），§2 的转移网络承担"预测 (prediction)"步。换句话说，$z_t$ 不是凭空的 embedding，而是一个**无解析模型可依时的、数据驱动的贝叶斯滤波器的隐状态**——这就是它必须携带记忆、必须带不确定性的根本原因。

---

## 2. 预测层：在 latent 里推演未来

> [!tip] 本节四拍
> **直觉**（有了 $z_t$，学一个"下一步"函数就能想象）→ **推导**（Dyna → 确定性 RNN → RSSM 确定+随机 → Transformer/扩散）→ **对比**（确定性 vs 随机、RNN vs Transformer）→ **联系**（这就是学出来的 [[Dynamics#3.1 操作器方程：$M(q)\ddot q+C(q,\dot q)\dot q+N(q)=\tau$|动力学]]）。

### 2.1 演进脉络：从 Dyna 到 RSSM 到 Transformer 世界模型

**Phase 1 — Dyna (Sutton, 1991)**：最早的"想象训练"。学一个表格式转移模型，用它生成假想经验混进 Q-learning。**核心创新**：真实经验既更新策略、又更新模型，模型再生成更多经验。**局限**：表格模型不能泛化到高维连续状态。

**Phase 2 — PILCO (2011) / 概率模型**：用[[StochasticProcess|高斯过程]]学动力学并解析传播不确定性，样本效率极高。**局限**：GP 随数据量三次方增长，扩展不到高维长序列。

**Phase 3 — World Models (Ha & Schmidhuber, 2018)**：VAE 压视觉 + MDN-RNN 预测 latent。**核心创新**：首次证明可**完全在想象（"dream"）里训练策略**再迁移回真环境。**局限**：确定性 RNN 记忆有限，无显式不确定性。

**Phase 4 — Dreamer / RSSM (2019–2023, DreamerV3)**：**关键创新是 RSSM (Recurrent State-Space Model)** 把 latent 拆成两部分：
$$z_t = (\underbrace{h_t}_{\text{确定性 (RNN hidden)}},\ \underbrace{s_t}_{\text{随机 (stochastic)}}),\qquad h_t = f(h_{t-1}, s_{t-1}, a_{t-1}),\quad s_t \sim p(s_t\mid h_t)$$
- **确定性 $h_t$** 充当**长期记忆**——转笔时凭几帧前的记忆推断被遮挡的笔（解遮挡）；
- **随机 $s_t$** 表达**真正的不确定**（笔可能滑向两个方向）；
- 训练目标是 ELBO：重构 $o_t$ + KL 对齐先验 $p(s_t\mid h_t)$ 与后验 $q(s_t\mid h_t,o_t)$。

> [!important] ELBO 逐步推导：为什么"重构 + KL"恰好逼出一个好滤波器（不跳步）
> 我们想最大化观测序列的对数似然 $\log p_\theta(o_{1:T}\mid a_{1:T})$（单位：nats），但随机状态 $s_{1:T}$ 是隐变量，边缘化的积分 $\int\!\prod_t p(o_t\mid h_t,s_t)\,p(s_t\mid h_t)\,ds_{1:T}$ 高维不可解。**第一步**——引入近似后验 $q_\phi(s_t\mid h_t,o_t)$（即编码器），把积分改写成对 $q$ 的期望：
> $$\log p_\theta(o_{1:T}) = \log\,\mathbb{E}_{q}\!\left[\frac{p_\theta(o_{1:T},s_{1:T})}{q_\phi(s_{1:T})}\right]$$
> **第二步**——对凹函数 $\log$ 用 Jensen 不等式（$\log\mathbb E[X]\ge\mathbb E[\log X]$）把 $\log$ 挪进期望，得到证据下界 (Evidence Lower BOund)：
> $$\log p_\theta(o_{1:T}) \ge \mathbb{E}_{q}\big[\log p_\theta(o_{1:T},s_{1:T}) - \log q_\phi(s_{1:T})\big] =: \mathcal L_{\text{ELBO}}$$
> **第三步**——代入 RSSM 的马尔可夫因子分解 $p_\theta=\prod_t p(o_t\mid h_t,s_t)\,p(s_t\mid h_t)$、$q_\phi=\prod_t q(s_t\mid h_t,o_t)$，逐时刻拆开，恰好分成两项：
> $$\mathcal L_{\text{ELBO}} = \sum_{t=1}^{T}\Big[\underbrace{\mathbb{E}_{q}\big[\log p_\theta(o_t\mid h_t,s_t)\big]}_{\text{(A) 重构项}} \;-\; \underbrace{\mathbb{E}_{q}\big[D_{\mathrm{KL}}\!\big(q_\phi(s_t\mid h_t,o_t)\,\|\,p_\theta(s_t\mid h_t)\big)\big]}_{\text{(B) KL 对齐项}}\Big]$$
> 逐符号（单位均为 nats）：$o_t$＝第 $t$ 帧观测（图像+触觉张量），$h_t$＝确定性记忆，$s_t$＝随机隐态，$q_\phi(s_t\mid h_t,o_t)$＝**看过** $o_t$ 后的后验、$p_\theta(s_t\mid h_t)$＝**没看** $o_t$ 时的先验。
> - **(A) 重构项**逼着 $(h_t,s_t)$ 保留足够信息把 $o_t$ 解码回来——否则 latent 丢了笔的位姿，想象就成了盲猜；
> - **(B) KL 项**逼着"没看观测的先验"去逼近"看了观测的后验"——**这恰好是一次[[StochasticProcess#4.0 贝叶斯滤波的骨架：预测-更新递推（KF→EKF→UKF→PF 一张阶梯）|预测-更新递推]]**：先验 $p(s_t\mid h_t)$ 是纯凭记忆 $h_t$ 外推的**预测步 (prediction)**，后验 $q(s_t\mid h_t,o_t)$ 是吸收新观测后的**更新步 (correction)**，最小化二者 KL＝强迫"闭眼想象"的预测分布向"睁眼修正"的后验看齐。RSSM 因此不是一般 autoencoder，而是一台**用 ELBO 训练出来的贝叶斯滤波器**：KF/PF 在有解析模型时给出闭式的预测-更新，RSSM 在无解析模型时把这对递推整台学出来。

**这正是 §1 结尾"latent＝学出来的 belief"那条线的兑现**：RSSM 就是一个学出来的 belief 更新器。

**Phase 5 — Transformer / 扩散世界模型 (2023–)**：
- **STORM**（[[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning|STORM]]）：用 Transformer 替代 RNN 建长程依赖，注意力比 RNN hidden 记得更远；
- **扩散世界模型**（[[DyWA: Dynamics-adaptive World Action Model|DyWA]]、[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]、[[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]）：用扩散模型建模多峰的 $p(s_{t+1}\mid s_t,a_t)$，捕捉接触分叉（笔滑左/滑右）这种单峰高斯建不了的多模态转移。

> [!note] 世界模型 = 学出来的动力学，与解析动力学互补
> §2 学的 $p(s_{t+1}\mid s_t,a_t)$ 与 [[Dynamics]] 的操作器方程 $M\ddot q+C\dot q+N=\tau$ 是**同一对象的两种来源**：一个从数据学、一个从物理推。§5 会把二者缝起来（physics-informed WM）。

---

## 3. 不确定性层：模型何时在"自信地瞎编"

> [!tip] 本节四拍
> **直觉**（模型在没见过的地方会乱猜，而优化器专挑这种地方）→ **推导**（单模型熵只抓 aleatoric；ensemble 分歧抓 epistemic）→ **对比**（PETS ensemble vs 单一确定性模型）→ **联系**（[[StochasticProcess#3.1 三类不确定性|三类不确定性]]、[[InformationTheory]] 信息增益）。

### 3.1 为什么"规划＝优化"必须先建不确定性

规划本质是在模型里做优化（§4）。若模型在**数据稀疏区**过拟合出不切实际的乐观预测，优化器会**主动利用这个漏洞**，给出在真机上灾难性的动作——这叫 **model exploitation**。转笔的接触/非接触**边界**正是数据最稀疏、epistemic 最高之处。

**两类不确定性必须分清**（回扣 [[StochasticProcess#3.1 三类不确定性|§3.1]]）：
- **Aleatoric（偶然）**：世界本身的随机（笔真的可能滑向两边）——由模型输出分布的**方差/熵**表达；
- **Epistemic（认知）**：模型自己的无知（这个接触构型没见过）——**单模型的输出熵抓不到它**（过拟合时熵很低却极危险）。

### 3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性

**PETS**（[[Deep Dynamics Models for Learning Dexterous Manipulation|Deep Dynamics Models]] 即此思路）训 $M$ 个独立初始化的概率模型 $\{p_{\theta_m}(s_{t+1}\mid s_t,a_t)\}_{m=1}^M$，每个既输出均值也输出方差（抓 aleatoric），而**模型间的分歧**（disagreement）抓 epistemic：
$$u_{epi}(s_t,a_t) = \mathrm{tr}\,\mathrm{Cov}\big(\{\mu_m(s_t,a_t)\}_{m=1}^M\big)$$

> [!note] 为什么"ensemble 分歧"就是[[InformationTheory#2.2 互信息：观测的"切割能力"|信息增益]]（BALD 推导，不跳步）
> 把 $M$ 个成员看成对模型参数 $\theta$ 后验的 $M$ 个样本，我们要问的是：观测"下一状态 $s_{t+1}$"能带来多少关于**模型参数** $\theta$ 的信息？这正是 $s_{t+1}$ 与 $\theta$ 的**互信息**——BALD (Bayesian Active Learning by Disagreement) 目标：
> $$I(s_{t+1};\theta\mid s_t,a_t) = \underbrace{H\big[\mathbb E_{\theta}\,p(s_{t+1}\mid s_t,a_t,\theta)\big]}_{\text{(i) 总预测熵}} - \underbrace{\mathbb E_{\theta}\,H\big[p(s_{t+1}\mid s_t,a_t,\theta)\big]}_{\text{(ii) 平均单模型熵}}$$
> 逐符号：$H[\cdot]$＝微分熵（单位 nats），(i) 是把所有成员**混合后**的预测分布的熵（既含 aleatoric 又含成员分歧），(ii) 是每个成员**各自**熵的均值（纯 aleatoric）。**关键一步**：两者相减，aleatoric 部分抵消，只剩下"成员之间不一致"那部分——**这就是纯 epistemic**。当每个成员近似高斯、方差相近时，(i)−(ii) 主项正比于成员均值 $\{\mu_m\}$ 的散布，即上式的 $\mathrm{tr}\,\mathrm{Cov}(\{\mu_m\})$。所以 `ensemble 分歧 ≈ BALD 互信息 ≈ epistemic 不确定性` 三者本是一物。回到 [[InformationTheory#2.2 互信息：观测的"切割能力"|互信息即"切割能力"]]：分歧大＝这一步观测能大幅"切割"参数假设空间＝信息增益大——这正是 §6.3 把它当"探索罗盘"的信息论根据。

- 规划时把 epistemic 当**罚项**，让策略别盲目闯进高分歧区（安全）；
- **反过来**，把 epistemic 当**奖励**，就得到好奇心/主动学习——这是 §6 与 [[Final_WMTS|WMTS]] 课程生成器的核心（[[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation|Curious Exploration]]、[[Curiosity-Driven Exploration via Latent Bayesian Surprise|Latent Bayesian Surprise]]）。

> [!important] 一个量，两种用法（记忆锚点）
> **ensemble 分歧同时是"安全护栏"和"探索罗盘"**：规划里减去它（别去没把握的地方），课程里加上它（专去没把握的地方学）。这个对偶正是 [[InformationTheory|信息增益]] 的两面——降低认知不确定性既是风险规避的对象，也是主动学习的目标。§6 会把它兑现成 WMTS 的 fitness 函数。

---

## 4. 利用层：想象里"练策略"还是"规划动作"

> [!tip] 本节四拍
> **直觉**（有了会预测的模型，怎么把它变成动作？）→ **推导**（Dyna 训练 / MPC 规划 / Dreamer latent actor-critic 三条路）→ **对比**（谁快、谁稳、谁怕模型误差）→ **联系**（[[Optimization#7. 实时闭环：模型预测控制 (MPC)|MPC]]、[[ReinforcementLearning#4.3 方差控制：从 baseline 到 Advantage，Actor-Critic 的诞生|Actor-Critic]]）。

三种用法，对应"信任模型到什么程度"：

| 用法 | 机制 | 优点 | 怕什么 | 代表 |
|:--|:--|:--|:--|:--|
| **Dyna 式（想象训练）** | 在模型里 rollout 生成假想经验，喂给无模型 RL | 摊薄真实交互 | 长 rollout 误差累积 | Dreamer、[[DayDreamer- World Models for Physical Robot Learning\|DayDreamer]] |
| **MPC 式（在线规划）** | 每步在模型里前瞻 $H$ 步、只执行第一个动作、重规划 | 高频反馈摊薄模型误差 | 每步实时求解成本 | PETS、[[Model-Based Lookahead Reinforcement Learning for in-hand manipulation\|Lookahead RL]] |
| **TD-MPC（混合）** | 短程用模型规划 + 尾部用学到的**值函数**兜底 | 短 horizon 抗误差 + 值函数补长程 | 值函数与模型要协同 | TD-MPC / TD-MPC2 |

**MPC 的核心洞见**（与 [[Optimization#7. 实时闭环：模型预测控制 (MPC)|Optimization §7]] 同一思想）：**重规划频率越高，单次规划精度要求越低**——下一步能修正这一步的错，就像开车频繁看路而非闭眼直行。这把"模型不准"的风险用"高频反馈"摊薄。

**Dreamer 的巧思**：不在真状态、而在**想象的 latent 轨迹**上学 actor-critic，用 **λ-return** 平衡 bootstrap 的偏差与 rollout 的方差（回扣 [[ReinforcementLearning#2.3 估计价值的三种范式：DP → MC → TD（偏差-方差谱）|偏差-方差谱]]）。梯度可**直接穿过可微的世界模型**回传给 actor——这是无模型 RL 没有的"解析优势"。

> [!important] λ-return 在想象 latent 上的 actor-critic（逐步展开）
> 世界模型先从当前 $z_t$ 出发，用转移网络+奖励头 rollout 出一条**想象轨迹** $\{(z_\tau,a_\tau,\hat r_\tau)\}_{\tau=t}^{t+H}$（$H$＝想象步数，量纲：步；$\hat r_\tau$＝奖励头预测的即时回报，单位：reward）。critic $v_\psi(z)$ 学一个 latent 上的值函数。λ-return **自尾向头递推**定义：
> $$V^\lambda_\tau = \hat r_\tau + \gamma\Big[(1-\lambda)\,v_\psi(z_{\tau+1}) + \lambda\,V^\lambda_{\tau+1}\Big],\qquad V^\lambda_{t+H}=v_\psi(z_{t+H})$$
> 逐符号：$\gamma\in[0,1)$＝折扣（无量纲），$\lambda\in[0,1]$＝偏差-方差旋钮。**把递推展开看两端**：$\lambda\!\to\!0$ 时 $V^\lambda_\tau=\hat r_\tau+\gamma v_\psi(z_{\tau+1})$，退化为**单步 TD**（低方差、高偏差，全靠 critic）；$\lambda\!\to\!1$ 时逐层代入把 $v_\psi$ 消掉，退化为**整条想象轨迹的蒙特卡洛回报**（低偏差、高方差）。中间 $\lambda$（Dreamer 用 0.95）在两者间插值——这正是 §2.3 偏差-方差谱在**想象空间**的复用。
> - **critic 更新**：回归目标 $V^\lambda_\tau$，即 $\min_\psi \tfrac12\big(v_\psi(z_\tau)-\mathrm{sg}[V^\lambda_\tau]\big)^2$（$\mathrm{sg}$＝stop-gradient，防止目标反向拖动 critic）；
> - **actor 更新**：直接最大化 $V^\lambda_\tau$。因为 latent 转移与奖励头都**可微**，$\nabla_\theta V^\lambda_\tau$ 可用重参数化**解析地穿过世界模型**回传（Dreamer 的 "dynamics backprop"）——对比无模型 REINFORCE 只能用高方差的 score-function 估计梯度，这是 model-based 的结构性红利。

> [!note] TD-MPC：短程规划 + 值函数"尾部兜底"（补 §4 表格里那一格的推导）
> MPC 式规划最怕长 rollout 的误差累积（§3 model exploitation 的温床），但短 rollout 又"看不远"。TD-MPC 的解法是把规划目标拆成"短程真 rollout + 学到的值函数续尾"：
> $$\max_{a_{t:t+H-1}}\ \mathbb E\Big[\underbrace{\sum_{k=0}^{H-1}\gamma^k\,\hat r(z_{t+k},a_{t+k})}_{\text{短程模型 rollout（}H\text{ 小 → 误差可控）}} \;+\; \underbrace{\gamma^{H}\,Q_\psi\big(z_{t+H},\pi_\theta(z_{t+H})\big)}_{\text{值函数尾部（替代无穷远 rollout）}}\Big]$$
> 逐符号：$H$＝规划视界（通常 3–5 步，量纲：步），$\hat r$＝世界模型奖励头，$Q_\psi$＝学到的动作值函数、$\pi_\theta$＝其配套策略。**为什么这样拆能同时抗误差又看得远**（不跳步）：前半段只让模型走 $H$ 小步，把复利误差 $\propto\!e^{H}$ 压在低位；后半段用 $\gamma^H Q_\psi$ **一步给出**"从 $z_{t+H}$ 起走到无穷远"的期望回报——本该需要长 rollout 才能估的长程价值，被值函数"摊平成一个数"。于是短 rollout 管**近处的精度**、值函数管**远处的视野**，二者分工正是 §2.3 偏差-方差谱在规划里的落点。该优化用 [[Optimization#7.3 基于采样：MPPI（用并行换梯度）|MPPI/CEM]] 在 latent 里采样求解，代价函数尾部换成 $Q_\psi$ 即可。这也解释了表格里 TD-MPC 那一栏的"怕什么"：**值函数与模型必须协同**——若 $Q_\psi$ 与 $\hat r$ 尺度不一致，尾部就会压垮或淹没短程项。

---

## 5. 结构层：怎么让想象"物理真实"

> [!tip] 本节四拍
> **直觉**（纯黑箱世界模型长 horizon 会物理穿帮：能量凭空增加、笔穿过手指）→ **推导**（残差 → 结构先验 → Actuator+Rigid 解耦）→ **对比**（黑箱 vs 物理知情 vs 显式）→ **联系**（[[Dynamics#9. 适配层：可微物理与神经动力学|神经动力学]]、[[Actuation#10. 迁移层 II：数据驱动执行器模型 (Actuator Model)|actuator model]]）。

### 5.1 从黑箱到物理知情

纯数据黑箱世界模型在长 horizon rollout 会累积物理不一致（不守恒、穿透）。三级"注入物理"的方法：

1. **残差学习**：$s_{t+1} = s_t + \Delta t\cdot f_{NN}(s_t,\tau)$——让网络只学**增量**，天然接近积分器（回扣 [[Dynamics#9. 适配层：可微物理与神经动力学|DexNDM 关节级残差]]）。
2. **结构先验**：把解析刚体动力学作为 skip-connection，网络只补它抓不到的接触/摩擦残差。
3. **显式世界模型**：直接重建物体的显式几何/物理参数（[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]），而非纯隐式 latent。

### 5.2 WMTS 的核心结构决策：Actuator + Rigid 解耦

> [!important] 为什么把世界模型拆成两级（[[Final_WMTS|WMTS]] 第四模块的灵魂）
> 灵巧手的"命令→状态"链有两段性质截然不同的物理：
> $$a_t \xrightarrow{\ \text{Actuator Model } f_{act}\ } \hat\tau_{link} \xrightarrow{\ \text{Rigid Dynamic Model } f_{dyn}\ } s_{t+1}$$
> - **Actuator Model** 学"命令→关节力矩"的执行器非线性（电流环带宽、反电动势、Stribeck、温漂、CAN 延迟）——详见 [[Actuation#10. 迁移层 II：数据驱动执行器模型 (Actuator Model)|Actuation §10]]；
> - **Rigid Dynamic Model** 学"力矩→状态演进"的刚体+接触动力学。
>
> **为什么必须解耦**（不跳步）：仿真里 Actuator Model 退化为 identity（$\tau_{sim}\equiv\tau_{link}$），只有 Rigid Model 需要预训练；上真机后**只有 Actuator Model 需要用真机数据微调**（因为刚体物理仿真已对，错的是执行器那段）。这把 [[Actuation#9. 迁移层 I：执行器 Sim-to-Real gap 的完整解剖|执行器 Sim-to-Real gap]] 精确地隔离在一个可单独适配的模块里——这正是"仿真关节虚拟力矩假设"失效的修复方案在世界模型里的落地。

> [!important] 双通道梯度回传：为什么"只调 Actuator、冻结 Rigid"仍能把状态误差归因到执行器（链式法则展开）
> 世界模型是两段复合：$\hat s_{t+1}=f_{dyn}\big(\underbrace{f_{act}(a_t;\theta_{act})}_{\hat\tau_{link}};\ \theta_{dyn}\big)$。真机适配时用状态误差做损失 $L=\tfrac12\|s_{t+1}^{real}-\hat s_{t+1}\|^2$（单位：state²），**只**更新 $\theta_{act}$。梯度按链式法则**穿过冻结的 Rigid 通道**回到 Actuator：
> $$\nabla_{\theta_{act}}L = \underbrace{\frac{\partial L}{\partial \hat s_{t+1}}}_{\text{状态误差}}\cdot \underbrace{\frac{\partial f_{dyn}}{\partial \hat\tau_{link}}}_{\text{Rigid 雅可比（冻结但可微）}}\cdot \underbrace{\frac{\partial f_{act}}{\partial \theta_{act}}}_{\text{可学参数}}$$
> 逐符号：$\hat\tau_{link}$＝预测关节力矩（单位 N·m），中间项 $\partial f_{dyn}/\partial\hat\tau_{link}$ 是刚体模型对力矩的敏感度——物理上约等于**有效惯量的逆 / 接触雅可比**（回扣 [[Dynamics#7.1 拓扑突变与有效惯量|有效惯量]]），它把"下一状态错了多少"翻译成"关节力矩错了多少"。**关键洞察**：因为刚体物理已正确，这个雅可比是一条**可信的信度分配 (credit assignment) 管道**——状态误差 → 经它换算成力矩误差 → 再经 $\partial f_{act}/\partial\theta_{act}$ 归因到执行器参数。于是"前向两段、反向一条链"：既不浪费真机数据重学刚体（$\theta_{dyn}$ 冻结 → 梯度维度小、方差低、样本高效），又让稀缺的真机误差精准落到该修的那段。
> **失效边界（第三条暗线的落点）**：这套解耦的正确性**依赖刚体模型确实对**。若真机上存在未建模接触/摩擦，冻结的 Rigid 雅可比会把本属刚体的误差**错误归因**给 $f_{act}$，把 Actuator Model 越调越坏。这正是 §6.4 为何不能只看 one-step MSE、还要用[[ControlTheory#13. 数据驱动控制：模型不准时如何仍给稳定性证书|数据驱动稳定性证书]]兜底——证书不可行，说明"错的是执行器"这个前提被违背了。这条"$\tau$ 身份错位"暗线贯穿 [[Actuation#10.2 力矩反馈为何"能当输入、不能当目标"|Actuation §10.2]]：仿真拿 $\tau$ 当输入、真机 $\tau$ 是执行器链的输出，解耦就是在世界模型里给这道身份错位单独留一个可微、可适配的接口。

---

## 6. 部署层：真机上的安全兜底与"无知即课程"

> [!tip] 本节四拍
> **直觉**（世界模型上真机，既要当安全网、又要防被策略钻空子）→ **推导**（安全滤波 + dream RL 对抗风险 + 不确定性驱动课程）→ **对比**（乐观利用 vs 保守兜底）→ **联系**（[[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|Sim-to-Real]]、§3 ensemble 分歧、[[InformationTheory]]）。

### 6.1 世界模型作安全调度器（Look-ahead Safety Filter）

真机执行前，先让世界模型在**脑内推演**候选动作块，三重拦截（[[Final_WMTS|WMTS]] 第五模块）：
1. **Ensemble OOD 拦截**：预测分歧极大 → 与已知动力学严重分歧 → 降级安全动作（即使均值预测"没掉落"）；
2. **成功率阈值**：$\hat{\mathcal R}_{succ}<$ 阈值 → 丢弃动作块；
3. **执行器可行性**：Actuator Model 的力矩可行性分数 $\rho_t=\hat\tau_{link}/\tau_{cmd}\ll1$（受 §5 温漂/包络约束）→ 降难度。

[[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL|SafeDreamer]] 把安全约束直接编进 Dreamer 的想象规划——在脑内就把不安全轨迹筛掉。

### 6.2 Dream RL 的对抗性风险

> [!warning] 在想象里练策略的"魔鬼"
> 若冻结世界模型、用 PPO 在想象里狂练（Dream RL），PPO 极其贪婪，可能**数百步内找到世界模型的物理漏洞**，生成对抗性动作（"WM 里完美，真机上拧断手指"）。这是 §3 model exploitation 的极端形态。**解药**：短 horizon rollout + BC 正则（[[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]、[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]] 的做法）。
>
> **BC 正则的本质，是给想象空间抛下一只"数据锚"**：把策略拽回真实数据支撑的分布，正是 [[ReinforcementLearning#7.4 模仿学习与策略蒸馏：把演示收编进统一梯度|模仿学习/策略蒸馏]]里 **AWAC（优势加权 BC）** 的机制——AWAC 在 §5.0 的统一框架里取参考分布 $\pi_0=$ 数据分布，用优势加权在"贴着数据"与"改进策略"间取舍。搬到世界模型里：想象 rollout 提供"改进"的梯度，BC 项提供"别飘出数据支撑区"的锚——短 horizon 限制**外推距离**、BC 锚限制**外推方向**，二者共同封住 PPO 钻模型漏洞的路。没有这只锚，想象里的优化就是在一张"数据稀疏处任意乐观"的地图上做贪心，必然撞上 §3 的 epistemic 陷阱。

### 6.3 无知即课程：认知不确定性反向驱动任务生成

把 §3 的 ensemble 分歧从"安全护栏"翻过来当"探索罗盘"，就得到**自动课程**：
$$R_I(s_t,a_t) = \mathrm{tr}\,\mathrm{Cov}\big(\{\hat s_{t+1}^m\}_{m=1}^M\big)\quad(\text{本质是 Bayesian Active Learning 的信息增益近似})$$
最大化 ensemble 分歧 = 引导系统走向**能最大幅度降低认知不确定性**的区域。[[Final_WMTS|WMTS]] 用它当隐空间任务生成器的 fitness，在"通才没掉落但跟得吃力"的舒适区边缘采样新任务。**这条线把世界模型、不确定性、课程学习缝成一体**——世界模型的无知，恰是课程该去的地方。（这正是 [[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间|RL 自动课程]]里 Learning-Progress / Regret 家族在世界模型里的化身：那里用 GAE 优势幅度当"还能学多少"的代理，这里用 ensemble 分歧当同一个代理，二者都在"能力边界"上采样任务；ensemble 分歧的信息论本质见 [[InformationTheory]]。）

### 6.4 真机在线适配

收集 $\{a_t,\phi_t,\dot\phi_t,\tau_{fb},T_{motor},\text{tactile}\}$，**只微调 Actuator Model**（§5.2 的解耦让这一步高效）。适配好不好，不只看 one-step MSE，还可用 [[ControlTheory#13. 数据驱动控制：模型不准时如何仍给稳定性证书|数据驱动 LMI]] 检查短真机轨迹是否给出稳定性证书——不可行则说明没激发够 latency/温度/stick-slip 模式，应补采而非扩容（详见 [[Actuator2RigidDynamicsModel_gap|L25 硬件分析 §八]]）。

---

## 7. 知识回扣与记忆图：一支想象的笔串起世界模型六层

> [!abstract] 用"在脑内转笔"把全讲复述一遍（刻意复述，为记忆）
> 我们要让灵巧手学转笔，又不想在真机上磨断手指。于是造一台"脑内引擎"。**(§1)** 先把每帧图像 + 360 维触觉压成紧凑 latent $z$——只留决策相关的自由度，否则想象一步就淹没在噪声里；这个 $z$ 就是学出来的 belief。**(§2)** 再学一个"下一步"函数在 $z$ 上推演：从 Dyna 的表格、到 Dreamer 的 RSSM（确定性 $h$ 记住被遮挡的笔、随机 $s$ 表达笔可能滑向两边）、到 Transformer/扩散 WM 建长程与多峰。**(§3)** 但模型在没见过的接触边界会自信地瞎编，优化器专挑这种漏洞——所以训一个 ensemble，用**分歧**抓认知不确定性：它既是安全护栏，又是探索罗盘。**(§4)** 有了模型，或在想象里练策略（Dreamer latent actor-critic），或每步前瞻几步再执行（MPC），或二者混合（TD-MPC）。**(§5)** 可纯黑箱想象久了会物理穿帮，于是注入物理：残差、结构先验，尤其把 WM 拆成 **Actuator + Rigid** 两级——让"仿真关节虚拟力矩"的谎言被隔离在一个上真机后单独微调的模块里。**(§6)** 最后上真机：世界模型在脑内推演候选动作、三重拦截兜底；提防 Dream RL 钻模型漏洞；再把它的**无知**翻过来当课程——ensemble 分歧最大处，正是该去学的地方。**一支想象的笔，转遍了世界模型六层大厦。**

> [!note] 三大记忆支柱 + 一条暗线
> **三支柱**：**先压缩再预测**（latent＝学出来的 belief，别预测噪声）、**分歧即认知不确定性**（一个量，安全与探索两用）、**解耦即可迁移**（Actuator+Rigid 把 Sim-to-Real gap 关进一个模块）。**一条暗线**：**世界模型的价值不在"预测得多准"，而在"知道自己何时不准"**——认知不确定性把预测、安全、探索、课程缝成一体。这条暗线通向 [[Optimization]] 的 model exploitation、[[StochasticProcess]] 的 epistemic、[[InformationTheory]] 的信息增益。

---

## 8. 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文构成世界模型主线的证据链（多数精读笔记在 `Projects/World Model as Task Scheduler/RelatedPapersRecap/`）。

### 世界模型骨干与综述
- [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer/RSSM]] — 隐空间想象 + latent actor-critic（§2、§4 的范本）
- [[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning|STORM]] — Transformer 世界模型（§2 长程依赖）
- [[Deep Dynamics Models for Learning Dexterous Manipulation|Deep Dynamics Models]] — Ensemble dynamics + MPC 的样本高效模型学习（§3 PETS、§4 MPC）
- [[Learning to Model the World: A Survey of World|世界模型综述]] · [[A Step Toward World Models- A Survey on Robotic Manipulation|机器人世界模型综述]]
- [[Robotic World Model: A Neural Network Simulator|Robotic World Model]] — 神经网络仿真器
- [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model|DexNDM]] — 关节级学出来的动力学 = 世界模型的物理先验/残差版（§5 结构层）
- [[FLD: Fourier Latent Dynamics for Structured Motion Representation and Learning|FLD]] — 傅里叶隐空间动力学表征（§1 表征、§2 预测）
- [[World Models Computing the Uncomputable|WM Computing the Uncomputable]] — 世界模型的可计算性边界与动机（§0）

### 扩散 / 像素空间世界模型
- [[DyWA: Dynamics-adaptive World Action Model|DyWA]] · [[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]] · [[DiWA- Diffusion Policy Adaptation with World Models|DiWA]] — 扩散世界模型（§2 多峰转移、§6 策略精修）
- [[WMPO - World Model-based Policy Optimization for VLA|WMPO]] — 像素空间 WM + GRPO 对 VLA 后训练（对接 [[ReinforcementLearning#10.2 世界模型 RL：隐空间 vs 像素空间|RL §10.2]]）

### 安全、真机与在线适配
- [[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL|SafeDreamer]] — 安全约束进想象规划（§6.1）
- [[DayDreamer- World Models for Physical Robot Learning|DayDreamer]] — 真机上直接学世界模型（§4 Dyna）
- [[Finetuning Offline World Models in the Real World|Finetuning Offline WM]] · [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]] — 离线预训练 + 真机微调（§6.4）
- [[Model-Based Lookahead Reinforcement Learning for in-hand manipulation|Lookahead RL]] — in-hand 操作的模型前瞻（§4）
- [[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|WM from Human Videos]] — 从人类视频学灵巧手世界模型
- [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]] — 半结构化动力学模型 = Actuator+Rigid 解耦的运动版（§5.2、§6.4）

### 好奇心 / 不确定性驱动探索（§3、§6.3）
- [[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation|Curious Exploration]] — 结构化世界模型的好奇心探索
- [[Curiosity-Driven Exploration via Latent Bayesian Surprise|Latent Bayesian Surprise]] — 隐空间贝叶斯惊奇作内在奖励

### 项目级（WMTS）
- [[Final_WMTS|World Model as Task Scheduler]] — 五模块流水线：本讲 §5.2 解耦、§6 安全调度与课程生成的项目级母本
- [[Actuator2RigidDynamicsModel_gap|Actuator-to-Rigid Gap]] — Actuator+Rigid 解耦的硬件依据
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-007-Implicit-Explicit-Contact-WM|IECW]] — 解析刚体 + 触觉门控接触残差 WM
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-014-WM-Gradient-Adaptive-DR|WG-ADR]] — 用 WM 输入梯度自适应分配 DR 方差

---

## 9. 结论

世界模型是灵巧操作从"在真机上昂贵试错"走向"在想象里廉价试错"的枢纽，也是 [[Final_WMTS|WMTS]] 项目的智力核心。从表征层的"先压缩再预测"（§1）、预测层的 RSSM 解遮挡（§2）、不确定性层的 ensemble 分歧（§3），到利用层的想象训练/规划三路（§4）、结构层的 Actuator+Rigid 解耦（§5）、部署层的安全兜底与"无知即课程"（§6）：**能预测是入门，能量化认知不确定性是进阶，能把执行器 gap 解耦并让无知反向生成课程，才是通向真机安全自主的钥匙。**

而贯穿始终的暗线，是**"世界模型的价值不在预测得多准，而在知道自己何时不准"**——正是这份可量化的认知不确定性，把 [[ReinforcementLearning|强化学习]]的想象训练、[[Optimization|优化]]的规划、[[StochasticProcess|随机过程]]的 epistemic、[[InformationTheory|信息论]]的信息增益、[[Actuation|执行器]]的 Sim-to-Real 修复，缝进同一台"脑内引擎"。世界模型，是策略在触碰真实世界之前，**先在想象里安全地失败一千次**的地方。
