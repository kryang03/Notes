---
tags:
  - paper
  - vla
  - world-model
  - embodied-ai
  - representation-learning
  - flow-matching
aliases:
  - WoG
  - World Guidance
paper-year: 2026
read-date: 2026-06-25
venue: arXiv
paper-pdf: "[[Papers/World Guidance: World Modeling in Condition.pdf]]"
related:
  - "[[EmbodiedAI]]"
  - "[[RepresentationLearning]]"
  - "[[StochasticProcess]]"
  - "[[Diffusion Policy: Visuomotor Policy]]"
  - "[[WMPO - World Model-based Policy Optimization for VLA]]"
---

# World Guidance: World Modeling in Condition Space for Action Generation

> [!abstract] 核心贡献
> WoG 提出一种不同于“预测未来视频”或“预测 latent action”的 VLA 世界建模方式：先在训练时把未来观测经冻结视觉 foundation models 和 Q-Former 压缩成动作头可用的 condition tokens $O^c$，再让 VLM 从当前观测中预测这些 condition tokens，使推理时无需真实未来也能获得 future-aware action guidance。

> [!tip] 与理论基础的关联
> - [[RepresentationLearning]] — WoG 的核心是 information bottleneck 式的 action-condition representation：保留对动作有用的未来信息，压掉任务无关像素冗余。
> - [[StochasticProcess]] — Rectified Flow 动作头把噪声动作和真实动作之间的线性路径作为生成过程，目标速度 $v^*=A-\epsilon$ 是方法的动作生成基础。
> - [[EmbodiedAI]] — VLA 后训练不只有 RL/world-model rollout 路线，也可以把未来预测蒸馏为当前观测下的条件表征。
> - [[WMPO - World Model-based Policy Optimization for VLA]] — WMPO 用 world model 生成 imagined trajectories 做 policy improvement；WoG 用 future-condition prediction 改进 single-step/closed-loop action generation，两者是互补而非同义。
>
> **核心技术**: Condition-Space World Modeling, Future Encoder, Q-Former, Rectified Flow Action Head, Future Condition Distillation, Human Video Condition Learning

## 0. 阅读定位与范本价值

WoG 是一篇很适合放在 WMTS/VLA-RL 簇里的论文，因为它提醒我们：**world model 不一定必须显式生成完整未来轨迹。** 对 action generation 来说，真正需要的可能是一个低维、可预测、与动作强相关的未来条件空间。

它与 WMPO 的差异必须先讲清：

| 维度 | WMPO | WoG |
|------|------|-----|
| world model 角色 | 生成完整 imagined trajectories，供 GRPO 做 policy improvement | 生成/蒸馏 action head 的 future condition，供 VLA 直接出动作 |
| 训练信号 | success/failure reward + GRPO advantage | action prediction loss + future condition alignment |
| 未来表示 | pixel-space video rollout | compressed condition tokens $O^c$ |
| 主要风险 | model exploitation、reward hacking、POMDP hidden state | condition space 不充分、未来不可预测、多模态未来被压成单一条件 |
| 对 WMTS 的启发 | world model 可以放大 RL 数据 | future tactile/contact 不一定要全量预测，可压成 action-guidance tokens |

因此这篇的价值不在于“又一个 VLA benchmark 更高”，而在于它提出了一个可迁移的设计问题：**我们到底应该预测未来的什么，才能帮助动作生成？**

最低标准对齐：

| 四支柱 | 本文必须回答的具体问题 |
|--------|------------------------|
| 逻辑与价值 | 为什么 full future prediction 冗余、latent action 又太粗？condition space 的 logical sweet spot 在哪里？ |
| 原理与理论 | 如何从 $P(A\mid z)$ 推到 $P(A,O^c\mid z)=P(A\mid z,O^c)P(O^c\mid z)$？Rectified Flow loss 和 condition alignment 各自监督什么？ |
| 实验与验证 | SIMPLER、真机、encoder ablation、Future Encoder ablation、人类视频/UMI 数据是否真的证明 condition space 有用？哪些任务暴露它的短板？ |
| 未来与结合 | 对灵巧手/WMTS，未来触觉、接触、物体运动是否可以被压成 condition tokens？什么时候必须回到显式动力学或 ensemble world model？ |

## 1. 问题设定与动机

### 1.1 一句话核心

WoG 的核心是：训练时用未来观测构造一个对动作头最有用的低维条件空间，推理时让 VLM 从当前观测中预测这个条件空间，从而把“未来会怎样”的信息蒸馏进当前动作生成。

### 1.2 直观隐喻

开车时不需要在脑中渲染未来 3 秒每个像素，也不能只说“往前开”这种粗粒度意图；真正有用的是几个可操作的未来约束：前车会不会刹、左侧有没有空隙、弯道曲率大不大。WoG 做的就是 VLA 版本的这件事：不预测完整视频，而是学一组能直接指导动作头的未来条件 token。

这个隐喻可被 falsify：如果 condition tokens 只捕捉了视觉语义而不包含接触/几何约束，那么在 stack、drawer、dexterous contact 任务上就会失败。论文结果确实显示：WoG 在 trajectory planning 和 pick-and-place 上强，但在精细空间约束任务上提升较小。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验/资源 | 关键局限 |
|----------|---------------------|----------|
| Vanilla VLA | 当前 RGB + language → action | 没有显式未来建模，动作头只能从当前观测隐式推断后果 |
| World Action Model / video prediction | 预测未来图像、视频、深度、光流或 foundation features | 表示丰富但任务无关冗余大；视觉预测误差可能传播到动作空间；训练成本高 |
| Latent Action Model | 把未来动作/动态压成离散或低维 latent | compact，但常像 PCA 一样捕捉最大方差信号，适合高层 motion trend，不足以指导精细动作 |
| Future video + latent action | 同时建模视频和 latent action | 信息多但接口复杂，仍可能被视频重建目标牵着走 |
| WoG condition space | 未来观测只保留 action head 需要的 condition tokens | 依赖 condition space 设计；若未来不可由当前观测预测，Stage II 会退化 |

WoG 的 Delta：**不是预测未来本身，而是把“未来信息”投影到动作生成条件空间，再学习从当前观测预测这个条件空间。**

### 1.4 论文贡献

1. 提出 condition-space world modeling：未来观测不直接作为重建目标，而是作为 action inference pipeline 中的条件表征。
2. 设计两阶段训练：Stage I 用真实未来观测指导动作生成并学习 $O^c$；Stage II 冻结 Future Encoder，让 VLM 预测 $O^c$，推理时自引导。
3. 用 Q-Former 从 DINOv2/SigLIP/Wan VAE 等冻结视觉模型中查询 action-relevant future features，压缩为低维 condition tokens。
4. 在 SIMPLER Google/WidowX、UR5 真机三任务、OOD 变化、人类视频和 UMI 数据上验证 condition-space 未来建模的有效性。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $O_t$ | RGB observation | 当前真实观测 | 对输入不求梯度 | VLA 当前可见环境 | 论文评估时每步只用单帧 RGB；不含 proprio/tactile |
| $l$ | language instruction | 任务输入 | 否 | 指定目标 | 语言不是动力学状态，只是 action condition |
| $z=f(O_t,l)$ | VLM hidden state / action token | Prismatic VLM 输出 | 是 | 当前观测和语言的策略上下文 | 文中用最后 learnable token 表示 $z$ |
| $A_{t:t+T}$ | action sequence，默认 horizon 16 | robot demonstration label | 作为监督标签；动作头参数带梯度 | 未来 $T$ 步动作 | 真机执行时预测 16 步，执行前 8 步 |
| $O_{t:t+T}^{\text{future}}$ | future observations | 训练数据中的未来帧 | 输入本身无梯度 | 训练时可见、推理时不可见的 privileged future | Stage I 用它，Stage II/推理不能用 |
| $F_{\text{DINO}}$ | semantic/discriminative features | 冻结 DINOv2 | 否 | 提供视觉语义、物体/场景表征 | 判别特征未必保留生成/运动细节 |
| $F_{\text{VAE}}$ | generative spatiotemporal features | 冻结 Wan VAE encoder | 否 | 提供轨迹/时序相关的生成特征 | VAE 帮 trajectory planning，不一定最好做精细空间定位 |
| $F_{\text{SigLIP}}$ | semantic alignment features | 冻结 SigLIP | 否 | 提供高层语义对齐 | 在 stack 等空间约束任务更有利 |
| $O^c$ | $N\times D$ condition tokens；默认 $N=16,D=32$ | Future Encoder / Q-Former 输出 | Stage I 中 Future Encoder 可训练；Stage II 作为 frozen target | 未来观测被压缩后的 action-condition space | 不是原始未来图像，也不是 latent action；它是动作头 cross-attention 条件 |
| $f_q(O,l)$ | predicted condition tokens | Stage II 中 VLM hidden states + query embeddings | 是 | 从当前观测预测 $O^c$ | 用 cosine alignment，尺度不应被过度解释 |
| $A_\tau$ | interpolated action | Rectified Flow 中间变量 | 是 | 从噪声动作到真实动作的路径点 | $\tau\in[0,1]$ 是 flow time，不是机器人时间 |
| $\epsilon$ | action noise | 采样 | 否 | flow 起点 $A_0$ | 与 diffusion noise 类似但这里走 ODE/rectified flow |
| $v_\theta$ | velocity field | DiT action head 输出 | 是 | 预测从 $A_\tau$ 到数据方向的速度 | Stage I 条件是 $(z,O^c)$，Stage II 条件只有 $z$ |
| $v^*$ | target velocity | $A-\epsilon$ | 否 | 直线路径上的真实速度 | 若路径定义为 $A_\tau=(1-\tau)\epsilon+\tau A$，速度恒为 $A-\epsilon$ |

### 2.2 从普通 VLA action generation 开始

普通 VLA 在当前观测和语言编码后，直接建模：

$$
z=f(O_t,l),\qquad
P(A_{t:t+T}\mid z).
$$

这个形式的问题是：未来世界状态对动作很关键，但并没有被显式建模。比如 pick-and-place 中，动作需要知道“如果沿这条轨迹走，会不会撞到 plate 里的已有物体”；fold towel 中，动作需要知道“这个释放时机会让布角落在哪里”。这些都是未来条件。

一个朴素扩展是直接预测未来观测：

$$
P(O_{t:t+T}^{\text{future}}\mid z),
\quad
P(A_{t:t+T}\mid z,O_{t:t+T}^{\text{future}}).
$$

但完整 future observations 含有大量与动作无关的信息，如背景纹理、光照、非交互物体细节。用它作为目标，会把模型容量花在不必要重建上。

WoG 的关键替换是定义一个压缩条件：

$$
O^c = E_\psi\!\left(F_{\text{frozen}}(O_{t:t+T}^{\text{future}}), z\right),
$$

其中 $E_\psi$ 是 Q-Former-based Future Encoder。目标不是保留全部未来，而是保留足以指导 action head 的 future condition。

### 2.3 条件空间的概率分解

训练时若有未来条件 $O^c$，动作生成可以写成：

$$
P(A_{t:t+T}\mid z,O^c).
$$

推理时没有未来观测，因此必须从当前 $z$ 预测 $O^c$。论文将完整推理写为：

$$
P(A_{t:t+T},O^c\mid z)
=
P(A_{t:t+T}\mid z,O^c)P(O^c\mid z).
$$

这在形式上是 chain rule，但 WoG 的实质假设更强：**在给定当前观测和语言后，未来 action-relevant condition 是可预测到足够精度的。** 如果环境高度随机、遮挡严重、接触状态隐藏，$P(O^c\mid z)$ 会是多峰或高熵分布；此时单一 predicted condition 可能变成平均未来，动作头反而会犹豫或失真。

因此 WoG 的 condition space 要同时满足两个要求：

1. **Sufficient for action**：$O^c$ 对 $A$ 有高信息量，即 $I(O^c;A\mid z)$ 高。
2. **Predictable from current observation**：$O^c$ 对 $z$ 不应过度不可预测，即 $H(O^c\mid z)$ 不能太高。

完整视频 prediction 往往违反第 2 点，因为未来像素细节难预测；latent action 往往违反第 1 点，因为过度压缩后缺少精细控制信息。WoG 的 condition space 是在这两个要求之间找中点。

### 2.4 Stage I: World Guidance

Stage I 使用真实未来观测作为 privileged information：

1. 当前观测和语言经 VLM 得到 $z$。
2. 未来观测经冻结 DINOv2/SigLIP/Wan VAE 得到 features。
3. Q-Former 用 learnable queries 从这些 features 中提取 $O^c$。
4. DiT action head 在 $(z,O^c)$ 条件下用 Rectified Flow 预测动作。

Rectified Flow 的路径定义为：

$$
A_\tau=(1-\tau)\epsilon+\tau A,\qquad \tau\in[0,1],
$$

其中 $\epsilon$ 是噪声动作，$A$ 是 demonstration action。对 $\tau$ 求导：

$$
\frac{dA_\tau}{d\tau}
=
A-\epsilon.
$$

所以 target velocity 是：

$$
v^*=A-\epsilon.
$$

Stage I 的 loss 是：

$$
\mathcal{L}_I
=
\mathbb{E}_{\tau,A}
\left[
\left\|
v_\theta(A_\tau,\tau,z,O^c)-v^*
\right\|_2^2
\right].
$$

这一步的意义不是让模型推理时依赖未来图像，而是先“发现”一个对动作头有用的未来条件空间。Future Encoder 在这里可训练，因此 $O^c$ 会被 action loss 塑形，而不只是视觉模型的普通特征。

### 2.5 Stage II: World Inference

Stage II 冻结 Future Encoder 和视觉 projectors，让它们定义稳定的 target condition space。然后训练 VLM 从当前观测预测 $O^c$：

$$
\hat O^c=f_q(O,l).
$$

同时，action head 在没有真实未来条件输入的情况下，只用 $z$ 预测动作。loss 为：

$$
\mathcal{L}_{II}
=
\mathbb{E}_{\tau,A}
\left[
\left\|
v_\theta(A_\tau,\tau,z)-v^*
\right\|_2^2
\right]
+1-S\!\left(O^c,f_q(O,l)\right),
$$

其中 $S[\cdot,\cdot]$ 是 cosine similarity。

这里有一个容易误读的点：Stage II 不是在推理时仍把 predicted $O^c$ cross-attend 到 action head；论文描述是 future condition 被 decoupled from action head，成为 VLM 的 prediction target，从而把 future-condition knowledge 蒸馏进 VLM hidden representation。也就是说，$O^c$ 更像一个 auxiliary predictive representation，而不是推理时显式传入的外部 future plan。

### 2.6 架构细节

| 设计 | PDF 细节 | 理论意义 |
|------|----------|----------|
| Future sampling | 默认 16 action steps horizon，未来视觉以动作序列 1/4 频率采样，即 4 frames | 不重建全帧率未来，降低冗余 |
| Future Encoder | $N=16$ learnable query tokens，输出 $D=32$ condition dimension | 强信息瓶颈，迫使 token 只保留动作相关未来 |
| Frozen encoders | DINOv2、SigLIP、Wan VAE 可组合 | 利用 foundation visual priors，减少从机器人数据学视觉表征的压力 |
| Stage II query | 取 VLM last 4 hidden tokens，用 16 learnable queries cross-attend，再投到 32 维 | 从当前上下文中预测未来条件 |
| Action head | DiT + Rectified Flow | 多步动作生成，速度场监督比传统 diffusion 更直接 |
| Human videos | 无标注视频可只监督 condition prediction；有标注子集可同时监督 action | 将“未来条件”与 embodiment-specific action 部分拆开 |

## 3. 训练、数据与实验

### 3.1 Simulation 设置

| 项目 | 设置 |
|------|------|
| Simulator | SIMPLER |
| Robots | Google Robot, WidowX |
| Evaluation input | closed-loop，每步只给 single RGB observation |
| Baselines | $\pi_0$, $\pi_0$-FAST, OpenVLA, GR00T-N1, Moto, UniVLA, DeFI, VITA, ViPRA |
| Pretraining | OXE Stage I 100k steps，global batch 1024 |
| Stage II simulation training | Bridge + Fractal 50k steps，batch 1024 |
| Real-world action horizon | 预测 16 步，执行前 8 步 |

### 3.2 SIMPLER Google Robot 主结果

| Model | Visual Matching Avg | Variant Aggregation Avg | Overall Avg |
|-------|---------------------|-------------------------|-------------|
| $\pi_0$ | 58.8% | 54.8% | 56.8% |
| $\pi_0$-FAST | 61.9% | 59.0% | 60.5% |
| OpenVLA | 32.7% | 39.8% | 33.8% |
| GR00T-N1 | 45.0% | 51.5% | 48.4% |
| Moto | 59.2% | - | - |
| VITA | 57.4% | - | - |
| DeFI | 51.2% | 45.4% | 48.3% |
| WoG | 78.0% | 60.7% | 69.4% |

关键任务数字：

| Model | VM Pick Coke | VM Move Near | VM Drawer | VA Pick Coke | VA Move Near | VA Drawer |
|-------|--------------|--------------|-----------|--------------|--------------|-----------|
| $\pi_0$-FAST | 75.3% | 67.5% | 42.9% | 77.6% | 68.2% | 31.3% |
| DeFI | 54.2% | 60.7% | 38.6% | 53.9% | 58.2% | 24.0% |
| WoG | 89.0% | 82.5% | 62.5% | 87.9% | 75.0% | 19.3% |

因果解释：

- WoG 在 Visual Matching 平均 78.0%，比 $\pi_0$-FAST 61.9 高 16.1 点，说明 condition-space future guidance 对接近真实分布的动作生成有强增益。
- Move Near 是最支持主故事的任务：VM 82.5、VA 75.0，都高于 strong baselines。它需要 collision avoidance 和 trajectory planning，正好对应“未来条件帮助动作头”的机制。
- VA Drawer 上 WoG 只有 19.3，低于 $\pi_0$-FAST 的 31.3。论文解释为 drawer/stack 类任务需要精细相对位置和空间约束，当前 backbone 分辨率不足。这是一个重要反证：condition space 能放大已有视觉先验，但不能凭空提供高精度几何。

### 3.3 SIMPLER WidowX 主结果

| Model | Grasp Avg | Success Avg |
|-------|-----------|-------------|
| $\pi_0$ | 40.1% | 27.1% |
| $\pi_0$-FAST | 48.3% | 32.1% |
| OpenVLA | 7.8% | 1.1% |
| GR00T-N1 | 49.5% | 36.5% |
| UniVLA | 77.5% | 45.6% |
| ViPRA | 71.9% | 62.5% |
| WoG | 85.4% | 63.5% |

任务分解：

| Task | Metric | Best baseline | WoG |
|------|--------|---------------|-----|
| Put Spoon on Towel | Success | ViPRA 66.7% | 79.2% |
| Stack Green on Yellow | Success | ViPRA 54.2% | 33.0% |
| Put Carrot on Plate | Success | UniVLA 55.6% | 50.0% |
| Put Eggplant in Basket | Success | ViPRA 79.2% | 91.7% |

因果解释：

- WoG 的 overall success 63.5% 只比 ViPRA 62.5% 高 1 点，但 grasp avg 85.4% 明显最高。这说明 WoG 很擅长改善 grasp/approach 这类 trajectory-planning-heavy 阶段。
- Stack Green on Yellow 成功率 33.0%，显著低于 ViPRA 54.2%。这再次说明：condition tokens 对粗到中等精度的 future guidance 有效，但对精细堆叠相对位姿，当前表示仍不足。
- 因此不能把 WoG 总结成“全面超过 video prediction”。更准确的结论是：**WoG 在动作相关未来条件可由 foundation encoders 捕捉时很强；在高精度几何约束上仍需要专门空间机制。**

### 3.4 Encoder configuration ablation

| Encoder config | Google Overall Avg | WidowX Grasp Avg | WidowX Success Avg |
|----------------|--------------------|------------------|--------------------|
| WoG (DINOv2) | 69.5% | 68.8% | 49.0% |
| WoG (DINOv2 + SigLIP) | 69.4% | 85.4% | 63.5% |
| WoG (DINOv2 + Wan VAE) | 70.9% | 86.4% | 58.4% |

因果解释：

- DINOv2+Wan VAE 在 Google 上最高 70.9，说明 generative/spatiotemporal features 对 trajectory planning 有帮助。
- DINOv2+SigLIP 在 WidowX success 最高 63.5，尤其 Stack Green on Yellow 33.0 vs DINOv2+Wan VAE 29.2，说明高层语义对某些空间约束任务有帮助。
- 没有一个 encoder 组合全面解决细粒度几何；这支持论文自己的 limitation：foundation visual features 的能力边界会成为 condition space 的边界。

### 3.5 Future Encoder ablation

| Variant | Google Overall Avg | WidowX Grasp Avg | WidowX Success Avg |
|---------|--------------------|------------------|--------------------|
| WoG w/o Future Enc. | 66.7% | 75.0% | 57.3% |
| WoG w/o Future Enc. in Stage-II | 66.7% | 71.8% | 57.3% |
| WoG w. Future Enc. | 70.9% | 86.4% | 58.4% |

因果链：

`去掉 Future Encoder`
→ Google overall 70.9 降到 66.7，WidowX grasp avg 86.4 降到 75.0
→ 因为模型不再把 frozen vision features 查询/压缩成 action-relevant condition，而是直接对齐高维未压缩特征
→ 说明低维 condition bottleneck 不只是省算力，它在筛选动作相关未来信息。

但也要注意：WidowX success avg 只从 57.3 提到 58.4，提升很小。这说明 Future Encoder 更明显改善 grasp/trajectory 阶段，对 placement success 的贡献有限。

### 3.6 Real-world UR5 结果

真机平台：UR5 + Robotiq 2F-85，top-down Intel RealSense D435/L515，但本文只用 D435。每个任务每方法 20 trials。

| Model | Microwave ID | P&P ID | P&P Background | P&P Novel Object | Fold ID | Fold Background | Fold Light | Fold Novel Object |
|-------|--------------|--------|----------------|------------------|---------|-----------------|------------|-------------------|
| UniVLA | 80% | 25% | 25% → 20% | 25% → 10% | 20% | 20% → 20% | 20% → 10% | 20% → 10% |
| VPP | 90% | 55% | 55% → 30% | 55% → 15% | 45% | 45% → 30% | 45% → 20% | 45% → 30% |
| WoG | 100% | 60% | 60% → 55% | 60% → 40% | 60% | 60% → 50% | 60% → 35% | 60% → 50% |

因果解释：

- Microwave 100% 显示 condition guidance 对 articulated rotational dynamics 有效。
- P&P novel object 从 ID 60 降到 40，但仍明显优于 VPP 的 15 和 UniVLA 的 10，说明 frozen visual priors + condition compression 提升了外观变化下的迁移。
- Fold light change 60→35 是最难场景，但仍优于 VPP 45→20。光照变化说明 condition space 并非完全免疫视觉 shift，只是相对更稳。

### 3.7 Training-stage ablation

| Model | Microwave ID | P&P ID | P&P Background | P&P Novel Object | Fold ID | Fold Background | Fold Light | Fold Novel Object |
|-------|--------------|--------|----------------|------------------|---------|-----------------|------------|-------------------|
| Vanilla VLA | 90% | 45% | 45% → 45% | 45% → 40% | 40% | 40% → 25% | 40% → 10% | 40% → 30% |
| WoG w/o cotrain | 95% | 45% | 45% → 45% | 45% → 35% | 30% | 30% → 30% | 30% → 10% | 30% → 30% |
| WoG | 100% | 60% | 60% → 55% | 60% → 40% | 60% | 60% → 50% | 60% → 35% | 60% → 50% |

因果链：

`去掉 Stage II condition supervision`
→ WoG w/o cotrain 接近或低于 Vanilla VLA，Fold ID 甚至 30% < 40%
→ 说明 Stage I 的 future-guided action training 不能自动保证推理时可用
→ 必须显式训练 VLM 预测 future condition，才能把 privileged future information 蒸馏回当前观测表示。

这是 WoG 最关键的 ablation：它证明论文的核心不是“训练时偷看未来图像”，而是“把未来条件变成当前 VLM 可预测的内部表征”。

### 3.8 Human video 与 UMI 数据

Human data 设置：

- 自采 PICO 4 Ultra Enterprise 人类操作数据：650k trajectories，总 1,920 hours。
- 其中 220 hours 有 action annotation，占约 11%；其余 89% 只作为 unlabeled videos。
- 无标注 human videos 可在 Stage II 只监督 condition prediction；有标注子集可在两阶段加入 action supervision。

| Strategy | P&P ID | P&P Background | P&P Novel Object | Fold ID | Fold Background | Fold Light | Fold Novel Object |
|----------|--------|----------------|------------------|---------|-----------------|------------|-------------------|
| w/o human data | 60% | 60% → 55% | 60% → 40% | 60% | 60% → 50% | 60% → 35% | 60% → 50% |
| w. human videos only | 70% | 70% → 70% | 70% → 35% | 50% | 50% → 45% | 50% → 30% | 50% → 45% |
| w. human videos/actions | 70% | 70% → 70% | 70% → 45% | 65% | 65% → 60% | 65% → 45% | 65% → 50% |

因果解释：

- P&P 中，unannotated human videos already help：ID 60→70，background OOD 55→70。人手 pick-and-place 的未来物体运动与机器人相似，所以 condition prediction 可以迁移。
- Fold 中，只用 unannotated human videos 反而 60→50。人手折布的灵活性和机器人夹爪折布的动作-条件关系不同，condition space mismatch 会伤害 robot policy。
- 加入 220h action-annotated human subset 后，Fold ID 65、background 60、light 45，说明少量 action alignment 能把 human future conditions 重新锚到 robot action space。

UMI 数据：

| Added data | P&P success | Fold success |
|------------|-------------|--------------|
| Robot-only WoG | 60% | 60% |
| +120 UMI trajectories | 85% | 80% |

UMI 的强结果说明 condition space 对 egocentric observation 和不同 embodiment 有一定鲁棒性。但它也提出一个研究问题：UMI 数据是在最终 fine-tuning 阶段加入，不能证明 condition space 完全 embodiment-invariant，只能证明它有可迁移潜力。

## 4. 核心洞见

### 4.1 论文真正的 insight

WoG 真正的 insight 是：**未来预测的目标空间应该由 action head 需要什么来定义，而不是由传感器能重建什么来定义。**

这句话把它和 video prediction 区分开。一个未来视频模型可能很清晰，但如果它把容量花在桌布纹理和背景光照上，对 action generation 反而是噪声。WoG 通过 Q-Former bottleneck 和 action loss，让未来表示围绕动作头的需求形成。

### 4.2 为什么有效

WoG 的有效性来自三层耦合：

1. **未来观测 → condition tokens**：使用 frozen foundation encoders 保留视觉先验，Q-Former 压缩掉冗余。
2. **condition tokens → action head**：Stage I 让 $O^c$ 直接参与 Rectified Flow 动作生成，因此 $O^c$ 被塑造成 action-useful representation。
3. **当前观测 → condition tokens**：Stage II 用 cosine alignment 让 VLM 学会从当前 $z$ 中预测未来条件，使推理时无需真实未来。

这比普通 auxiliary future prediction 更强，因为 auxiliary target 的空间不是外部指定的 image/depth/video，而是由 action-generation pipeline 内生定义。

### 4.3 什么时候会失效

1. **未来是多模态的**：同一当前图像下可能有多种合理未来，单一 $O^c$ 预测会平均化。
2. **关键状态不可见**：触觉剪切、接触法向、摩擦、关节弹性、物体内部应力如果不在 RGB 中，$P(O^c\mid z)$ 就学不到。
3. **foundation encoder 缺少空间精度**：Stack/Drawer 的弱项说明，condition space 不能凭空补 encoder 不具备的几何能力。
4. **human-to-robot condition mismatch**：Fold 上无标注 human videos 伤害性能，说明 embodiment/action grounding 缺失时，未来条件可能转错。
5. **没有显式不确定性**：模型预测 condition，但没有告诉 action head “这个未来条件我不确定”。对安全控制是问题。

## 5. 替代方案与理论局限

### 5.1 理论维度

WoG 的 sufficient condition 叙事很漂亮，但需要更严格地理解：

$$
O^c \text{ sufficient for action}
\quad \Rightarrow \quad
P(A\mid z,O^c)\approx P(A\mid z,O^{\text{future}}).
$$

这只是经验目标，不是定理。Q-Former 的 $N=16,D=32$ bottleneck 能否保留动作需要的全部未来信息，取决于任务结构、encoder 能力、数据覆盖和 action head。对接触丰富任务，未来条件可能必须包含力/触觉/物体状态，而不是 RGB feature compression。

### 5.2 算法维度

| 路线 | 优势 | 风险 |
|------|------|------|
| WoG condition space | 低冗余，直接服务 action head，适合从无标注视频学未来条件 | 不建模真实转移，不提供 rollout/reward；condition 不确定性不可见 |
| WMPO imagined RL | 能产生 on-policy improvement signal，学习 self-correction | 需要高保真 world model 和 reward model，易 model exploitation |
| Full video prediction policy | 可解释、可视化未来 | 冗余大，重建目标不一定服务动作 |
| Latent action model | compact，跨 embodiment 潜力大 | 动作精度可能不足，latent 与低层控制脱节 |
| Structured/contact model | 对物理约束更可靠 | 需要建模成本和传感器/状态估计 |

### 5.3 工程与实验维度

1. SIMPLER 和 UR5 结果强，但离 dexterous hand 还有距离：没有多指接触、没有触觉、没有高频 torque/position 控制。
2. 真实实验每任务每方法 20 trials，适合初步验证，不足以作为安全泛化证据。
3. Stage II 的 condition prediction 用 cosine similarity，未报告 calibration 或 uncertainty。
4. Fine geometry 是明确短板：Stack、Drawer、精确相对位姿任务表现不稳定。
5. Human video transfer 有条件：无标注视频对 P&P 有利，对 Fold 有害；不能简单相信“更多人类视频一定更好”。

## 6. 对用户研究的启发

### 6.1 对 WMTS 的迁移：未来触觉/接触条件空间

WMTS 不一定需要让 world model 预测完整未来视觉/触觉序列。可以借鉴 WoG，把未来接触演化压成 action head 的 condition tokens：

| WoG 概念 | WMTS 可替换版本 | 为什么有用 |
|----------|----------------|------------|
| Future RGB observations | 未来 tactile patches、joint trajectories、object pose belief、contact events | 灵巧手任务的未来关键不是像素，而是接触是否进入正确 basin |
| Frozen visual encoders | tactile encoder + proprio encoder + object-state encoder + geometry/contact encoder | foundation visual priors 不足以处理手内接触 |
| Q-Former Future Encoder | cross-attention over future sensory rollout tokens | 从 PPO Oracle / simulation rollout 中抽取 action-relevant future condition |
| $O^c$ condition tokens | contact-guidance tokens: slip risk、contact mode、object angular velocity trend、stability margin | 比完整 tactile video 更紧凑，更适合指导 Diffusion/Flow generalist |
| Stage I future-guided action | 用 privileged future rollout 条件训练 action flow head | 相当于 teacher forcing：让 policy 先知道“好未来长什么样” |
| Stage II condition distillation | 只从当前 observation/history 预测 contact-guidance tokens | 推理时不偷看未来，但保留未来约束知识 |

一个具体 WMTS 版本：

1. PPO Oracle 在仿真中生成成功/失败 rollouts。
2. 对每条 rollout 的未来 $H$ 步，提取 tactile/contact/proprio/object tokens。
3. Q-Former 压成 $O^c_{\text{contact}}$。
4. Diffusion/Flow generalist 在 $(h_t,O^c_{\text{contact}})$ 条件下生成 action chunk。
5. 冻结 Future Encoder，让 policy 从当前 history $h_t=(q,\dot q,\text{tactile},\text{vision},a_{t-1})$ 预测 $O^c_{\text{contact}}$。
6. 真机部署只用当前传感器，condition prediction 作为 internal future belief。

### 6.2 可验证实验建议

1. **Full future tactile prediction vs condition tokens**  
   比较三种辅助目标：预测完整未来 tactile map、预测 object pose sequence、预测 Q-Former contact condition tokens。指标不只看 auxiliary loss，而看真实转笔成功率、slip recovery、contact transition prediction。

2. **Condition dimension sweep**  
   扫 $N,D$，观察是否出现 WoG 式“过小不充分、过大冗余难预测”的 U-shaped 曲线。若没有，说明 condition bottleneck 没有真正成为动作相关表示。

3. **Privileged future distillation**  
   Stage I 给 action head 看未来 contact tokens，Stage II 蒸馏到当前 history。比较只做 action BC、只做 future prediction、两阶段 WoG-style distillation。

4. **Human video/hand video transfer sanity check**  
   对人手转笔视频，只用无动作标注 future condition prediction 可能像 Fold 一样伤害机器人。必须加少量 retargeted/action-aligned data 或用 hand-object contact abstraction 降低 embodiment mismatch。

5. **Uncertainty-aware condition prediction**  
   让 $P(O^c\mid h_t)$ 输出分布或 ensemble，而不是单点 condition。若 uncertainty 高，则交给 WMTS 的 Probe/Reject 机制，而不是强行动作生成。

### 6.3 不应过度外推的点

- WoG 不是物理 world model。它不预测可 rollout 的 transition，也不提供 RL reward，只是 action-generation condition。
- WoG 的 condition space 仍由视觉 foundation encoders 决定；对 tactile/contact 缺失的任务，它不会自动学到隐藏物理。
- 人类视频不是免费午餐。P&P 受益，Fold 在无动作标注时受损，这对灵巧手非常关键。
- 精细几何任务是短板。若 WMTS 的核心是转笔的接触相位和微小角速度修正，必须加入结构化状态和接触监督。

## 7. 与知识体系的联系

### 7.1 与 [[RepresentationLearning]] 的联系

WoG 是 action-conditioned representation learning 的例子。它不是让 representation 尽可能重建输入，而是让 representation 对下游 action generation sufficient：

$$
\min I(O^c;O^{\text{future}}_{\text{irrelevant}})
\quad \text{while keeping}\quad
I(O^c;A\mid z)\ \text{high}.
$$

这和 generic self-supervised feature learning 不同：representation 的好坏由动作头和 closed-loop robot performance 判定。

### 7.2 与 [[StochasticProcess]] 的联系

Rectified Flow 将动作生成写成 deterministic ODE 路径：

$$
A_\tau=(1-\tau)\epsilon+\tau A,\qquad
\frac{dA_\tau}{d\tau}=A-\epsilon.
$$

相比 DDPM 的 stochastic denoising，Rectified Flow 的路径更直，推理可更快。这对高频或低延迟机器人控制有现实意义，但它只解决 action distribution sampling，不解决 world dynamics fidelity。

### 7.3 与 [[EmbodiedAI]] 的联系

WoG 提供了一条 VLA world modeling 的第三路线：

- full world/video prediction：显式但冗余；
- latent action：紧凑但粗；
- condition-space world modeling：面向 action head 的未来条件。

这条路线特别适合作为 VLA action head 的辅助训练目标，而不是替代所有 model-based RL。

### 7.4 与 WMPO / WMTS 的组合

一个有潜力的组合是：

1. 用 WoG-style condition distillation 训练 generalist policy 的 future-aware action head。
2. 用 WMPO-style imagined rollouts 或 WMTS ensemble world model 产生 policy improvement data。
3. 用 SafeDreamer/MoDem/FOWM 的 uncertainty/cost 机制过滤不可信 imagined states。
4. 对灵巧手，把 condition 从视觉未来换成 contact/tactile/proprio future。

这会形成一条更合理的 WMTS 技术路线：**WoG 解决“动作头应该被什么未来信息指导”，WMPO 解决“policy improvement signal 从哪里来”，ensemble/contact model 解决“这个未来信息能不能被物理相信”。**

## References

- Su et al., 2026. *World Guidance: World Modeling in Condition Space for Action Generation*.
- Hu et al., 2025. *Video Prediction Policy: A Generalist Robot Policy with Predictive Visual Representations*.
- Bu et al., 2025. *UniVLA: Learning to Act Anywhere with Task-Centric Latent Actions*.
- Chi et al., 2023. *Diffusion Policy: Visuomotor Policy Learning via Action Diffusion*.
- Zhu et al., 2025. *WMPO: World Model-based Policy Optimization for Vision-Language-Action Models*.
