---
tags:
  - paper
  - curiosity
  - bayesian-surprise
  - exploration
  - WMTS
aliases:
  - Latent Bayesian Surprise
  - LBS
paper-year: 2022
read-date: 2026-06-15
venue: AAAI 2022 (Ghent University; Mazzaglia, Verbelen)
paper-pdf: "[[Curiosity-Driven Exploration via Latent Bayesian Surprise.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[Final_WMTS]]"
---

# LBS: Curiosity-Driven Exploration via Latent Bayesian Surprise

> [!abstract] 核心贡献
> 提出 **Latent Bayesian Surprise (LBS)** 好奇奖励：用 latent 动力学模型的**后验 vs 先验信念之差（Bayesian surprise）**作内在动机，在 latent 空间算 → 比参数空间 Bayesian surprise（VIME）**算力大降**。关键优势：**抗 NoisyTV 问题**——基于预测误差/surprisal 的好奇（ICM）会被白噪声电视吸引（随机 = 高预测误差 = 假"有趣"），而 Bayesian surprise 对**纯随机转移**（不更新信念、无新信息）给**低奖励** → 不追逐不可约随机性。连续控制 + 视频游戏上 competitive，且对随机转移 resilient。**对 WMTS：它给 Probe 队列一个关键原则——探索应求 epistemic（可约、可学）不确定，而非 aleatoric（不可约噪声）；转笔有真实接触噪声，Probe 若用裸预测误差会陷 NoisyTV，应用 Bayesian surprise / ensemble disagreement（[[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation|CEE-US]]）这类 epistemic 信号。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — 内在动机/好奇奖励；探索。
> - [[StochasticProcess]] — Bayesian surprise（后验 vs 先验 KL）；latent 变分动力学模型。
> - [[Final_WMTS]] — **Probe 求 epistemic 非 aleatoric**（抗 NoisyTV）；与 CEE-US ensemble epistemic 一致。
>
> **核心技术**: Latent Bayesian Surprise (后验 vs 先验信念差), latent 变分动力学, 抗 NoisyTV, 算力低, 内在奖励

## 0. 阅读定位与价值

LBS 给 WMTS 的探索/Probe 补上**关键的"信号选型"原则**：好奇该追 **epistemic（可约、可学）**不确定，而非 **aleatoric（不可约随机）**。它与 [[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation|CEE-US]]（ensemble epistemic）互证、与 [[Prioritized Level Replay|PLR]]（学习潜力）同向。读它要抓 **NoisyTV 问题 + Bayesian surprise 的解**：后验-先验信念差只在"有新信息可学"时高，纯噪声不给奖励。

## 1. 问题设定与价值（逻辑与价值）

### 1.1 一句话核心
好奇（内在动机）助探索，但**基于预测误差/surprisal 的好奇陷 NoisyTV**——白噪声电视预测误差高、被误判最有趣。LBS 用 **Bayesian surprise（后验 vs 先验信念差）**：纯随机转移不更新信念→低奖励，抗 NoisyTV，且在 latent 空间算省算力。

### 1.2 直观隐喻
预测误差好奇像"哪儿看不准就去哪"——会被永远看不准的白噪声电视黏住（不可约随机）。Bayesian surprise 像"哪儿能让我**更新认知**就去哪"——看一眼白噪声并不会让你学到任何可泛化的东西（信念没变），所以不去；而真正能更新世界观的新现象才吸引你。可证伪含义：Bayesian surprise 优于预测误差的场景是"**环境有不可约随机**"时（转笔接触噪声正是）；确定性环境两者近似。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 内在信号 | 关键局限 |
|---|---|---|
| 预测误差/surprisal（ICM） | 模型预测误差 | **NoisyTV**：陷不可约随机 |
| 参数空间 Bayesian surprise（VIME） | 参数后验 vs 先验 | 算力贵 |
| count/RND 新颖性 | 状态新颖 | 新颖≠有用 |
| **LBS** | **latent 后验 vs 先验信念差** | latent 模型质量依赖；仿真/游戏（非真机灵巧） |

### 1.4 Delta 分析
精确增量：(1) **Bayesian surprise 移到 latent 空间** → 算力大降（vs VIME 参数空间）；(2) 证明**抗 NoisyTV**（随机转移低奖励）；(3) latent 变分动力学模型实现。把"预测误差好奇（陷 NoisyTV）/参数 Bayesian surprise（贵）"换成"廉价且抗噪的 latent Bayesian surprise"。

## 2. 核心方法（原理与方法：Latent Bayesian Surprise）

### 2.1 核心机制（无跳步）
- **latent 变分动力学模型**：随机 latent 变量建动力学。
- **Bayesian surprise**：观测新数据后，latent 变量的**后验 vs 先验信念之差**（KL）= 内在奖励。
- **抗 NoisyTV**：纯随机转移**不携带可更新信念的新信息** → 后验≈先验 → 低 surprise → 不奖励噪声。只有"能更新对动力学理解"的转移才高奖励。
- latent 空间算 → 廉价。

### 2.2 概念边界与符号陷阱
- Bayesian surprise（信念更新）≠ surprisal/预测误差（unpredictability）——前者抗噪。
- 测 **epistemic**（可约，信念可更新）而非 **aleatoric**（不可约随机）。
- latent 空间（vs VIME 参数空间）→ 廉价。
- 依赖 latent 模型质量。

## 3. 实验与验证
- 连续控制 + 视频游戏：competitive SOTA，算力低。
- **抗随机转移**：随机环境下不被噪声吸引（NoisyTV resilient）。**因果**：随机转移不更新信念→低奖励。
- 边界：latent 模型依赖；仿真/游戏。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 真正的 insight
**好奇该用 Bayesian surprise（后验 vs 先验信念更新）而非预测误差（surprisal）——前者只奖励能更新认知（epistemic）的转移、不奖励不可约随机（aleatoric），从而抗 NoisyTV；移到 latent 空间还省算力。** 一句话：**追"能学到东西"（信念更新）而非"看不准"（预测误差）。**

### 4.2 为什么有效
(1) Bayesian surprise 测信念更新 = 真信息增益；(2) 随机转移不更新信念→不奖励（抗 NoisyTV）；(3) latent 空间廉价。

### 4.3 什么时候会失效
- latent 模型差 → 信念估计不准。
- 确定性环境 → 与预测误差近似（无 NoisyTV 优势）。
- 真机灵巧高维（游戏/连续控制相对简单）。

## 5. 替代方案与局限（未来与结合）
- 好奇信号谱：预测误差（ICM，陷 NoisyTV）、count/RND、参数 Bayesian surprise（VIME，贵）、**LBS（latent，抗噪廉价）**、ensemble disagreement（[[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation|CEE-US]]，也 epistemic）。
- 局限：latent 模型依赖、仿真。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM 的迁移

| WMTS 模块 | LBS 对应 | 迁移设计 |
|---|---|---|
| **Probe 信号选型** | Bayesian surprise（epistemic） | WMTS Probe 求 **epistemic**（可学）不确定，**非 aleatoric**（接触噪声）；用 Bayesian surprise / ensemble disagreement |
| 抗 NoisyTV | 随机转移低奖励 | 转笔接触噪声 = NoisyTV 风险；Probe 别陷不可约随机配置 |
| 信号来源 | latent 后验-先验 | WMTS 用 ensemble disagreement（CEE-US）或 latent surprise |

**核心论证（critical thinking）**：LBS 给 WMTS 的 Probe 队列一个**决定性的信号选型原则**：探索/好奇必须求 **epistemic（可约、可学）**不确定，而非 **aleatoric（不可约随机）**。这对转笔尤其关键——**转笔有真实的接触噪声/随机性（aleatoric）**，如果 WMTS 的 Probe 用裸预测误差（surprisal）选"最不可预测"的配置去探索，会陷入 NoisyTV：把算力浪费在**本质随机、学不动**的配置上。LBS 的解（Bayesian surprise：后验 vs 先验信念更新）与 [[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation|CEE-US]] 的解（ensemble disagreement）都正确地**只奖励 epistemic**——ensemble 在 aleatoric 噪声上会一致（不 disagree），只在 epistemic 缺口 disagree，所以 WMTS 用 **ensemble disagreement 作 Probe 信号天然抗 NoisyTV**，LBS 给了 Bayesian 形式的同等保证。**结论**：WMTS scheduler 的 Probe = 朝 **ensemble disagreement / Bayesian surprise（epistemic）**高的转笔配置探索，**显式排除 aleatoric 噪声**——这是对 [[Prioritized Level Replay|PLR]] "学习潜力"的精化（学习潜力 = epistemic 可约部分，非 aleatoric）。边界：游戏/连续控制，转笔接触噪声更复杂，epistemic/aleatoric 分离更难。

### 6.2 可验证实验建议
- Probe 信号对比：转笔上 ensemble disagreement / Bayesian surprise vs 裸预测误差，测是否陷 NoisyTV（接触噪声配置）。
- epistemic/aleatoric 分离：验证 ensemble disagreement 在接触噪声上是否一致（不误判）。

### 6.3 不应过度外推的点
- 游戏/连续控制 ≠ 转笔接触；epistemic/aleatoric 分离更难。
- latent 模型质量决定信念估计。
- 确定性环境无 NoisyTV 优势。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
内在动机/好奇奖励；探索；抗 NoisyTV 的内在 bonus。

### 与 [[StochasticProcess]] 的联系
Bayesian surprise（后验 vs 先验 KL）；latent 变分动力学模型；epistemic vs aleatoric 区分。

### 与 [[Final_WMTS]] 的联系
Probe 求 epistemic 非 aleatoric（抗 NoisyTV）；与 CEE-US ensemble disagreement 一致；精化 PLR 学习潜力（=epistemic 可约部分）。

## References
- 原始 PDF：[[Curiosity-Driven Exploration via Latent Bayesian Surprise.pdf]]（Ghent，AAAI 2022）
- ensemble epistemic（同向）：[[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation|CEE-US]]
- 学习潜力：[[Prioritized Level Replay|PLR]]
- 项目入口：[[Final_WMTS]]
