---
tags:
  - paper
  - interpretability
  - sparsity
  - transformer
aliases:
  - Sparse Transformers Interpretability
  - Weight Sparsity Circuits
paper-year: 2024
read-date: 2026-03-16
venue: OpenAI
paper-pdf: "[[Papers/Weight-sparse transformers have interpretable circuits.pdf]]"
related:
  - "[[RepresentationLearning]]"
  - "[[Optimization]]"
  - "[[InformationTheory]]"
---

# Weight-sparse Transformers Have Interpretable Circuits

> [!note] Foundation 关联
> - **[[RepresentationLearning]]**: 本文核心关于表征的可解释性与解耦 (Section 6: 流形学习与解耦)
> - **[[Optimization]]**: $L_0$ 约束优化与投影梯度下降 (Section 2.4: 稀疏优化)
> - **[[InformationTheory]]**: 信息瓶颈与稀疏表示

> [!abstract] 核心概要
> 通过在训练中强制 Transformer 保持极高的**权重稀疏性**（仅 0.1%-1% 非零权重），迫使模型学习出**解耦的、人类可读的计算回路**，避免稠密模型中的"叠加态"现象，开辟了"事中干预"式可解释性研究路径。

这篇论文 **"Weight-sparse transformers have interpretable circuits"** 来自OpenAI，它直击深度学习理论中最迷人也最困难的领域——**机械可解释性（Mechanistic Interpretability）**。

目前的深度模型像是一个"黑盒"，我们知道它能工作，但不知道*为什么*。这篇论文提出了一种激进的假设：**极度的稀疏性（Sparsity）是解开神经网络内部复杂纠缠的钥匙。**

下面我将为你层层拆解这篇论文。

------

## 1. 核心直觉与宏观定位 (The Big Picture)

- **一句话核心**：通过在训练过程中强制Transformer保持极高的**权重稀疏性**（仅保留约0.1% - 1%的非零权重），迫使模型学习出**解耦的、人类可读的计算回路（Circuits）**，从而避免了稠密模型中常见的"叠加态"（Superposition）现象。
- **直观隐喻**：
  - **稠密模型（Dense Model）** 就像一碗意大利面（Spaghetti Code），所有的神经元都相互连接，牵一发而动全身，你很难找出"哪根面条负责逻辑推理"。
  - **稀疏模型（Sparse Model）** 就像一块精心设计的印刷电路板（PCB），由于连接极其有限，信号必须通过清晰、独立的路径传输。这迫使模型"专款专用"，一个神经元只负责一个明确的概念（如"检测左括号"）。
- **领域定位**：
  - 这是**机械可解释性**领域的重要探索。
  - 它挑战了目前主流的"事后分析"（Post-hoc，如训练完再用Sparse Autoencoder去拆解）范式，提出**"事中干预"（Ab initio）**——即通过改变训练目标，直接训练出可解释的模型。

------

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析：相比 SOTA 的增量

传统的模型压缩（Pruning）主要关注**效率**（推理速度），而本文关注**可解释性**。与最近火热的**稀疏自编码器（SAE）** 相比，SAE 是在一个已经训练好的稠密"黑盒"外挂一个"翻译器"，而本文是直接把"黑盒"变成了"白盒"。

### 关键贡献点

1. 

   **稀疏性即解释性**：证明了在相同的预训练Loss下，稀疏模型的最小功能回路（Minimal Circuit）比稠密模型小约 **16倍** 。这意味着理解模型行为所需的认知负载大幅降低。

2. 

   **回路发现算法（Circuit Discovery）**：提出了一种基于梯度掩码（Gradient-based Masking）的剪枝方法，能从大模型中精确提取出执行特定任务（如Python代码补全）的子图 。

3. 

   **桥接技术（Bridges）**：提出了一种训练辅助线性层（Bridges）的方法，将稀疏模型的激活映射到稠密模型，从而用可解释的稀疏特征来**操纵（Steer）** 稠密模型的行为 。这是连接"可解释研究"与"SOTA模型"的关键一步。

4. 

   **严格的验证体系**：不仅发现了回路，还通过**均值消融（Mean Ablation）** 和**反向剪枝（Inverse Pruning）** 验证了这些回路是任务完成的**必要且充分条件** 。

------

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 数学建模：$L_0$ 约束下的优化

论文的核心目标是在保证模型能力的同时最小化参数数量。数学上，这是一个带约束的优化问题：

$$\min_{\theta} \mathcal{L}_{\text{task}}(\theta) \quad \text{s.t.} \quad \|\theta\|_0 \le k$$

其中 $\|\theta\|_0$ 是 $L_0$ 范数（非零元素的个数），$k$ 是目标参数量。

### 3.2 核心机制：Top-K 投影与激活稀疏化

由于 $L_0$ 范数不可导，作者没有使用 $L_1$ 惩罚（Lasso），而是采用了 [[Optimization]] 中**投影梯度下降（Projected Gradient Descent）** 的变体：

1. 

   **权重稀疏（Weight Sparsity）**：在每次 SGD/AdamW 更新后，强制将权重矩阵 $W$ 中绝对值最小的一部分元素置为 0 。

   $$W \leftarrow W \odot \mathbb{I}(|W| \ge \text{Top}_k(|W|))$$

   - **原理溯源**：这利用了 **Lottery Ticket Hypothesis** 的直觉，即大模型中存在极小的子网络能维持性能。

2. 

   **激活稀疏（Activation Sparsity）**：除了权重，作者还强制中间激活值（Activation）稀疏，使用了 `AbsTopK` 激活函数 。

   $$\text{AbsTopK}(x, k) = x \odot \mathbb{I}(|x| \ge \text{Top}_k(|x|))$$

   - **物理意义**：这迫使神经元只有在信号非常强时才激活，减少了"多义性"（Polysemanticity），即 [[RepresentationLearning]] 中一个神经元在不同上下文中代表不同含义的现象。

### 3.3 回路发现算法 (Circuit Pruning)

为了找到特定任务的回路，作者定义了一个掩码优化问题。对于模型中的每个节点 $i$（神经元或Attention Head），学习一个参数 $\tau_i$ ：

$$\text{Node}_i \leftarrow \text{Node}_i \odot \sigma(\tau_i)$$

这里 $\sigma$ 是 Heaviside阶跃函数（Step Function）。为了使其可导，反向传播时使用 **Sigmoid 替代梯度（Surrogate Gradient）**，类似于 Straight-Through Estimator。

**损失函数**：

$$\mathcal{L}_{\text{prune}} = \mathcal{L}_{\text{task}} + \lambda \sum_i \sigma(\tau_i)$$

这就需要在"完成任务"和"回路极简"之间通过 $\lambda$ 进行权衡。

------

## 4. 算法实现与逻辑 (Methodology & Implementation)

我将为你梳理模型训练与回路提取的核心逻辑。

### 4.1 整体架构与数据流

模型主体是标准的 Decoder-only Transformer（类似 GPT-2），但有两个关键修改：

1. 

   **归一化**：使用 `RMSNorm` 且不带可学习的缩放参数（为了保持稀疏权重的独立性）。

2. **激活函数**：将标准的 GELU 替换或补充为 `AbsTopK` 。

**数据流向（Training Loop）**：

Python

```
# 伪代码：稀疏训练核心逻辑
optimizer = AdamW(model.parameters(), lr=lr)

for step, batch in enumerate(dataloader):
    # 1. 前向传播
    # 注意：层与层之间使用了 AbsTopK 激活函数强制激活稀疏
    loss = model(batch)
    
    # 2. 反向传播
    loss.backward()
    
    # 3. 权重更新
    optimizer.step()
    
    # 4. 强制 L0 约束 (关键 Trick)
    # 对每个权重矩阵，保留绝对值最大的 k 个元素，其余置零
    with torch.no_grad():
        for name, param in model.named_parameters():
            if 'weight' in name:
                threshold = torch.kthvalue(param.abs().flatten(), 
                                           k=total_elements - target_k).values
                mask = param.abs() >= threshold
                param.data *= mask # 硬剪枝
                
    # 5. L0 Annealing (退火)
    # 训练初期允许稠密，逐渐减少 target_k 直到目标稀疏度
    target_k = update_schedule(step) 
```

### 4.2 关键 Trick [重点]

- 

  **$L_0$ 退火 (Annealing)**：不能一开始就稀疏训练。作者让模型从全稠密开始，在前 50% 的训练步数内线性减少 $L_0$ 直到目标值 。这对于防止模型坍缩至关重要。

- 

  **Bigram Table**：作者显式添加了一个稠密的 Bigram 表（词表大小 $\times$ 词表大小），直接处理相邻词的统计规律 。

  - *原因*：这样可以释放稀疏 Transformer 的容量，让它专注于更复杂的逻辑，而不是去死记硬背"New"后面常跟"York"。

- 

  **死神经元重启**：尽管论文提到死神经元是个问题，但他们通过保持梯度的稠密（不剪枝梯度，只剪枝权重）来缓解优化困难 。

------

## 5. 实验与局限性分析 (Experiments & Discussion)

### 5.1 核心结论

实验在预训练的 Python 代码模型上进行，设计了 20 个特定的微任务（如预测括号嵌套深度、引号闭合等）。

**训练设定详情**:

| 项目 | 详情 |
|------|------|
| **模型规模** | 6M / 66M / 131M 参数（稠密基准），对应非零参数 ~60K / 660K / 1.3M |
| **预训练数据** | The Stack v2 Python 子集 |
| **训练 tokens** | ~22B tokens (6M), ~82B tokens (131M) |
| **稀疏度** | 99% - 99.9% 权重稀疏 |
| **优化器** | AdamW，带 $L_0$ 退火 schedule |
| **退火策略** | 前 50% steps 从稠密线性退火至目标稀疏度 |
| **辅助组件** | 稠密 Bigram Table (词表²) |

1. **回路极其精简**： 展示了对于同样的 Loss，稀疏模型所需的回路大小比稠密模型小 16 倍。

2. **可解释性可视化**：

   - 

     **括号计数任务**：发现了一个仅由 7 个节点和 4 条边组成的回路，清晰地利用 Attention Head 进行计数和阈值判断  。

   - 

     **引号闭合任务**：定位到了具体的神经元负责"检测双引号"和"检测单引号" 。

3. **Bridges 的有效性**： 展示了可以通过修改稀疏模型的激活，经由 Bridge 映射后，成功控制稠密模型的输出（例如让稠密模型误以为当前在单引号字符串内）。

### 5.2 局限性与弱点 (Critical Analysis)

- 

  **训练效率悖论**：虽然模型参数是稀疏的，但在 GPU 上，非结构化稀疏（Unstructured Sparsity）无法利用 Tensor Core 加速。实际上，训练稀疏模型通常比训练同等大小的稠密模型**更慢、更费算力** 。

- **性能代偿 (Trade-off)**：稀疏模型在同等参数量下的性能弱于稠密模型。为了达到相同的 Loss，稀疏模型需要更多的总参数（尽管非零参数很少）。

- 

  **规模限制**：实验仅限于小型模型（~千万参数级）和简单任务。这套方法能否扩展到 GPT-4 级别的模型处理自然语言的复杂语义，仍是未知数 。

- 

  **多义性残留**：即使在如此高的稀疏度下，部分神经元仍然表现出多义性（Polysemanticity），说明稀疏可能不是解开叠加态的唯一条件 。

### 5.3 Ablation 因果分析

| 消融条件 | 效果 | 因果机制 |
|---------|------|--------|
| 去除 $L_0$ 退火（直接高稀疏） | 训练坍缩，所有神经元死亡 | 稀疏约束过强时梯度流被截断 → 类似 [[Optimization]] 中投影梯度法的可行域过小导致无法收敛 |
| 去除 Bigram Table | Loss 显著上升 | 稀疏网络被迫用有限容量编码低级统计规律 → 挤占高级逻辑推理的参数预算 |
| 去除激活稀疏（仅保留权重稀疏） | 多义性增加，回路不够清晰 | 权重稀疏限制连接拓扑，激活稀疏限制信号并行度 → 两者协同才能迫使单神经元单功能 |
| 替换 AbsTopK 为 ReLU | 回路可解释性下降 | ReLU 仅截断负值，仍允许大量弱正激活 → 不足以消除 polysemanticity |
| 增大模型规模（66M→131M） | 相同稀疏度下回路更清晰 | 更多参数 → 更多"彩票"(lottery tickets) 可选 → [[InformationTheory]] 中信道容量增加使编码更高效 |

------

## 6. 知识图谱与延伸思考 (Knowledge Graph & Future)

### 6.1 前置知识

- **Transformer Architecture**: 尤其是 GPT-2 变体。
- **Mechanistic Interpretability**: 了解 **Superposition Hypothesis** (Anthropic) 是理解为何要稀疏化的理论基础。
- **Pruning / Sparse Training**: 理解 $L_0$ norm, Straight-Through Estimator (STE)。

### 6.2 推荐文献

1. 

   **"Toy Models of Superposition" (Elhage et al., 2022)**:  必读。解释了为什么神经网络会产生不可解释的纠缠特征（为了压缩信息），是本文理论的出发点。

2. 

   **"Sparse Autoencoders (SAEs)" (Various, e.g., Cunningham et al., 2023)**:  目前解释性领域的主流竞品。对比阅读可以理解 "Post-hoc" vs "Ab initio" 的优劣。

3. 

   **"The Lottery Ticket Hypothesis" (Frankle & Carbin, 2019)**:  稀疏子网络存在的理论基石。

### 6.3 复现建议与"坑"

如果你打算复现这篇论文：

1. **不要尝试手写稀疏 CUDA 核函数**：除非你是高性能计算专家。直接使用 PyTorch 的 Masking 模拟稀疏性即可（虽然慢，但逻辑正确）。
2. **$L_0$ 退火是关键**：如果你一开始就设定 99% 稀疏度，模型不仅不收敛，所有神经元都会"死亡"。必须使用论文图 11  中的 Schedule。
3. **RMSNorm 的位置**：注意它是 Pre-Norm 配置，且为了不仅对权重做归一化，要小心处理 Scale 参数。

### 6.4 与 Foundation 的数学联系

**与 [[Optimization]] 的联系**:
$L_0$ 约束优化 $\min_\theta \mathcal{L}(\theta)$ s.t. $\|\theta\|_0 \le k$ 是 NP-hard 的组合优化问题。Top-K 投影是对 $L_0$ ball 的正交投影，等价于贪心近似：
$$\text{Proj}_{L_0 \le k}(\theta) = \theta \odot \mathbb{I}(|\theta| \ge \text{Top}_k(|\theta|))$$
这是 [[Optimization]] 中投影梯度下降（PGD）框架的特例，收敛性依赖于目标函数的受限光滑性。

**与 [[InformationTheory]] 的联系**:
稀疏表示与最小描述长度（MDL）原则直接相关。一个 99.9% 稀疏的模型用更少的 bits 编码同样的功能 → 信息瓶颈 $I(X; T)$ 被显式压缩，迫使 $T$ 保留与任务最相关的信息。

**与 [[RepresentationLearning]] 的联系**:
Superposition hypothesis 认为稠密网络将 $N > d$ 个特征叠加到 $d$ 维空间中。稀疏化等价于限制每层的有效维度，迫使表征从 superposition 退化为 monosemantic → 与表征解耦问题同构。

### 6.5 跨方法对比

| 维度 | 权重稀疏 (本文) | SAE (Post-hoc) | Probing | Activation Patching |
|------|----------------|----------------|---------|-------------------|
| **时机** | 训练时（Ab initio） | 训练后 | 训练后 | 训练后 |
| **目标** | 直接可解释模型 | 解释稠密模型 | 定位信息 | 定位因果节点 |
| **规模** | 小模型 (~100M) | 大模型适用 | 大模型适用 | 大模型适用 |
| **保真度** | 回路 = 实际计算 | 重建近似 | 线性探针限制 | 因果但粒度粗 |
| **效率代价** | 训练更慢（非结构化稀疏） | 额外训练 SAE | 训练探针 | 枚举开销 |

------

**导师总结**：这篇论文非常精彩地展示了"与其事后试图理解一团乱麻，不如一开始就强迫它长得井井有条"。虽然工业界因效率问题可能不会立刻采用这种训练方式，但它为我们理解 Transformer 内部的算法结构提供了最清晰的样本。

## 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **策略网络的可解释性**: 在转笔的 RL 策略调试中，稀疏 Transformer 可帮助理解「哪些关节的特征对决策影响最大」——可诊断策略失败模式
2. **稀疏性与实时推理**: 手上部署时推理延迟至关重要，稀疏权重可显著减少推理时间
3. **局限**: 本文重心在 NLP，向控制策略的迁移需进一步验证