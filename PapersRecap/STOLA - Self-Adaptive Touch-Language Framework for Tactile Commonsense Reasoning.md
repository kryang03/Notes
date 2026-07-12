---
tags:
  - paper
  - tactile-sensing
  - multimodal
  - mixture-of-experts
  - embodied-ai
aliases:
  - STOLA
  - SToLa
paper-year: 2026
read-date: 2026-03-13
venue: AAAI 2026
paper-pdf: "[[Papers/STOLA- Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning in Open-Ended Scenarios.pdf]]"
related:
  - "[[SignalProcessing]]"
  - "[[RepresentationLearning]]"
  - "[[EmbodiedAI]]"
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
---

# STOLA: Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning in Open-Ended Scenarios

> [!abstract] 核心贡献
> STOLA 把 Mixture-of-Experts 引入 touch-language LLM：触觉图像/视频先经 TLV-Link touch encoder 与 linear adapter 变成 tactile tokens，再与 language tokens 拼接进入 Vicuna-7B v1.5；LLM 内部把原 dense FFN upcycle 成 MoE experts，并用 top-k routing 在 token 级动态分配 tactile/text token，从而缓解“触觉被粗暴当成语言子模态”的 modality discrepancy；同时构建 600-question TactileBench，用 free-form QA 覆盖 8 类物理属性、4 类交互特征和 commonsense reasoning。

> [!tip] 与理论基础的关联
> - [[SignalProcessing]] — GelSight/GelSight Mini 的 tactile image/video 是接触形变的光学信号；STOLA 把它编码为 patch tokens，再进入语言模型。
> - [[RepresentationLearning]] — MoE routing 是动态表征解耦：每个 token 根据内容选择 expert，而不是把触觉和语言压进同一个 FFN。
> - [[EmbodiedAI]] — 触觉常识推理是 VLA/具身模型缺失的一环，但本文仍是离线 QA，不是闭环控制。
> - [[ReinforcementLearning]] — 对 WMTS/PPO 的价值在于 tactile state annotation、failure diagnosis、reward shaping，而不是直接输出动作。
> - [[ControlTheory]] — 对灵巧手而言，触觉语义必须最终落到接触状态、滑移、力控/阻抗调节，而 STOLA 目前未建模控制闭环。
>
> **核心技术**: Touch-Language Model, Mixture-of-Experts, Tactile Commonsense Reasoning, TactileBench, Two-Stage Training, LoRA, Sparse Upcycling

## 0. 阅读定位与范本价值

STOLA 这篇论文容易被误读成“把 MoE 套到触觉 LLM 上”。更准确的读法是：它抓住了 touch-language 模型的一个结构性矛盾——**触觉和语言可以被映射到同一个 hidden dimension，但这不等于它们应该被同一个 FFN 以同一种方式处理。**

对你的 LinkerHand / WMTS / 转笔研究，它的价值不在于“让灵巧手用语言回答触觉问题”，而在于三个更具体的问题：

1. tactile tokens 是否会在 multimodal backbone 中被 language tokens 淹没；
2. 是否需要 contact/phase/modality-specific experts 来处理触觉、本体、视觉、任务语言；
3. 离线 tactile commonsense 能否转化为可执行的 contact diagnostics、failure classifier、reward signal。

最低标准映射：

| 四支柱 | 本文 recap 的落点 | 必须抓住的判断 |
|---|---|---|
| 逻辑与价值 | §1, §4 | STOLA 的故事是“触觉不是语言子模态；需要 token-level 专家分流” |
| 原理与理论 | §2 | 从 tactile video patch tokens、adapter、LLM CE loss、MoE router、load balancing 逐步推导 |
| 实验与验证 | §3 | Table 1-4 + routing visualization 证明 MoE/LoRA/Stage I 各自的作用，同时暴露 CDR 和 13B 局限 |
| 未来与结合 | §5-§7 | 对 LinkerHand 应迁移为 tactile-contact expert routing，而不是照搬 GelSight QA 模型 |

## 1. 问题设定与动机

### 1.1 一句话核心

STOLA 认为现有 touch-language 模型把 tactile embedding 直接塞进 LLM 并共享同一套 FFN，会掩盖触觉与语言的语义差异；因此它用 MoE 在 LLM 内部让不同 tokens 动态选择不同 experts。

### 1.2 直观隐喻

把触觉接入 LLM 不是“把盲文翻译成文字再交给一个语文老师”。触觉像一个材料科学家、机器人操作员和语言解释者共同参与的会议：

- 语言 token 需要处理语义、问答、常识；
- 触觉 token 需要处理粗糙度、硬度、弹性、形变、抓握感；
- 二者需要交流，但不应该被同一个“通用办公室”统一处理。

STOLA 的 MoE 像给会议设置多个专业小组：router 决定某个 token 该去哪个 expert。这个类比的关键不是“专家越多越好”，而是 **token-level routing 能否形成可解释的 modality preference**。论文的 Figure 4/5 正是在验证这一点。

### 1.3 现有方法的局限

| 方法 | 注入了什么先验 | 关键局限 |
|---|---|---|
| Touch-LLM | 把 touch embeddings 对齐到 image/text embedding，再用 LLM 做 QA | 触觉作为外接模态，内部处理仍偏语言/视觉；不支持 PhysiClear 的 interleaved tactile temporal signals |
| Octopi | Vicuna-based tactile-language model，处理 PhysiClear 五类模板任务 | tactile/text 共享 dense FFN；数据主要围绕 hardness/roughness/bumpiness 的模板 QA |
| CLIP-style tactile alignment | 让触觉靠近视觉/文本语义空间 | 对齐后仍没有解决触觉 token 的专门处理路径 |
| 普通 multimodal LLM adapter | adapter 粗对齐后交给 LLM | 容易把 modality discrepancy 推给 LLM 自己消化 |
| 模板化 tactile benchmark | 准确率清晰，可控 | 难评估真实开放场景中 free-form tactile commonsense reasoning |

### 1.4 Delta 分析

STOLA 的 Delta 有两条：

1. **模型 Delta**：不是只在输入端做 touch-language alignment，而是在 LLM block 内部把 FFN 改成 MoE，让 token 在每层动态选择专家。
2. **数据 Delta**：不是只在 PhysiClear 三个属性上做模板问答，而是构建 TactileBench：8 physical properties、4 interactive characteristics、600 free-form questions、每题 3-5 ground-truth answers。

论文故事讲得好的地方：它没有只说 MoE 提升整体分数，还可视化了不同 experts 对 tactile/text token 的偏好。也就是说，它尝试证明提升来自 modality management，而不是纯参数量或训练数据偶然性。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 空间/类型 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $X_{\mathrm{touch}}$ | $\mathbb R^{N\times H\times W\times C}$ | tactile input | 否 | GelSight/GelSight Mini image/video，$C=3$ | 对 LinkerHand taxel tensor 不是同构输入 |
| $N$ | frame count | tactile video | 否 | 时间帧数；static image 被当成 single-frame video | 后续 average pooling 会弱化时序顺序 |
| $P$ | patch token length | touch encoder output | 否 | 每帧 tactile patch token 数，约 $HW/14^2$ | 不是语言 token 数；取决于 tactile image resolution |
| $Z$ | $\mathbb R^{N\times P\times C'}$ | touch encoder | 是/encoder 多数冻结 | frame-level tactile tokens | 论文抽取文字中 $C$ 与 hidden dim 容易混淆 |
| $Z'$ | $\mathbb R^{P\times C'}$ | temporal aggregation | 是 | video-level tactile token sequence | frame average pooling 不等于显式 temporal model |
| $V$ | $\mathbb R^{P\times D}$ | touch-language adapter | 是 | LLM hidden size 下的 tactile pseudo-tokens | 只做 coarse alignment，不等于语义等价 |
| $T$ | $\mathbb R^{M\times D}$ | word embedding | 部分冻结 | text request / instruction tokens | Stage II 不调整 word embedding |
| $x$ | $\mathbb R^D$ | MoE layer input token | 是 | 某个 tactile 或 text token 的 hidden state | router 不直接知道 modality label，只看 hidden state |
| $W_r$ | $\mathbb R^{D\times K}$ | router parameters | 是 | token-to-expert logits | $K=4$ experts；top-k 稀疏激活 |
| $E_i$ | FFN expert | Stage I FFN replicated/upcycled | 是 | 第 $i$ 个 expert transformation | experts 初始来自 dense FFN 复制，不是从零随机专家 |
| $P_i(x)$ | router probability | MoE routing | 是 | token 选择 expert $i$ 的权重 | 非 top-k experts 被 mask，不参与计算 |
| $F_i$ | token assignment fraction | auxiliary loss | 计算图/统计 | expert $i$ 被选中的 token 比例 | 用于防止 expert collapse |
| $G_i$ | mean router probability | auxiliary loss | 是 | router 给 expert $i$ 的平均概率 | 与 $F_i$ 一起做 load balancing |
| $Y$ | response tokens | LLM output / supervision | 监督标签 | tactile QA 的自然语言回答 | open-ended answer 不适合只用 exact match |

### 2.2 输入统一：从 tactile video 到 LLM tokens

STOLA 的输入不是直接“触觉向量 + 文本”。给定 tactile video：

$$
X_{\mathrm{touch}}\in \mathbb R^{N\times H\times W\times C},
\qquad C=3.
$$

Touch encoder 对每一帧独立编码，得到 frame-level tactile tokens：

$$
Z=
\left[
[z_{11},\dots,z_{1P}],
\dots,
[z_{N1},\dots,z_{NP}]
\right]
\in \mathbb R^{N\times P\times C'}.
$$

其中每个 tactile token 对应一个 $14\times14$ patch，因此：

$$
P \simeq \frac{H W}{14^2}.
$$

为了统一 image 和 video，static tactile image 被看成 $N=1$ 的 video。对多帧 video，论文采用类似 ViFi-CLIP 的 frame average pooling，得到：

$$
Z'\in\mathbb R^{P\times C'}.
$$

再通过 touch-language adapter：

$$
V=f_{\mathrm{touch}}(Z')\in\mathbb R^{P\times D}.
$$

文本 instruction 通过 word embedding：

$$
T=f_{\mathrm{text}}(X_{\mathrm{text}})
=
[t_1,\dots,t_M]\in\mathbb R^{M\times D}.
$$

最后把 tactile tokens 和 text tokens 拼接后送入 LLM。

关键陷阱：这里的 adapter 只是把 tactile tokens 放到 LLM hidden dimension $D$，并不意味着触觉语义已经变成语言语义。STOLA 的 MoE 正是为了解决 adapter 之后仍存在的 modality discrepancy。

### 2.3 系统公式：touch encoder + adapter + LLM

论文将整体写为：

$$
Y
=
\mathrm{LLM}_\phi
\left(
\mathrm{Proj}_\lambda(\mathrm{Enc}_\omega(X_{\mathrm{touch}})),
X_{\mathrm{text}}
\right),
$$

其中：

| 符号 | 含义 | 训练状态 |
|---|---|---|
| $\mathrm{Enc}_\omega$ | TLV-Link touch encoder | Stage I/II 中保持不变 |
| $\mathrm{Proj}_\lambda$ | linear touch-language adapter | Stage I 训练；Stage II 继续训练 |
| $\mathrm{LLM}_\phi$ | Vicuna-7B v1.5 with MoE blocks | Stage I 冻结；Stage II LoRA + MoE fine-tune |

这和旧稿中“Phi-2 / ResNet / 10+20 epochs”的说法不同。PDF 明确写的是 TLV-Link encoder、linear adapter、Vicuna-7B v1.5，训练配置见 Table 8：Stage I/II 都是 1 epoch，batch size 16，learning rate 分别为 $5\times10^{-4}$ 和 $2\times10^{-5}$。

### 2.4 MoE router 从零推导

普通 Transformer block 的 FFN 对所有 tokens 使用同一个函数：

$$
h'=\mathrm{FFN}(h).
$$

这隐含假设：tactile token 和 language token 可以被同一种非线性 transformation 处理。STOLA 改成 $K$ 个 experts：

$$
\{E_i\}_{i=1}^{K}.
$$

对某个 token hidden state $x\in\mathbb R^D$，router 先算 expert logits：

$$
q=xW_r\in\mathbb R^K.
$$

Top-k mask 保留最大的 $k$ 个 logits，非 top-k logits 设为 $-\infty$，再 softmax：

$$
P(x)=\mathrm{Softmax}(\mathrm{TopK}(q,k)).
$$

于是 MoE 输出：

$$
\mathrm{MoE}(x)=
\sum_{i=1}^{K}P_i(x)E_i(x),
$$

但实际上只有 top-k experts 的 $P_i(x)$ 非零。STOLA 使用 4 experts；论文图示和文字强调 tactile/text tokens 会形成不同 routing preference。

退化情形：

- 若 $K=1$，MoE 退化为普通 FFN；
- 若所有 tokens 总选同一个 expert，MoE 等价于容量更大的单一路径，失去 modality specialization；
- 若按 modality hard-code experts，则失去自适应性；STOLA 选择的是由 hidden state 学出的 soft routing。

### 2.5 Load balancing loss：为什么需要防止 expert collapse

如果只优化生成回答的 cross-entropy，router 可能把大多数 tokens 都送到少数 experts。STOLA 引入 Switch Transformer 式 auxiliary loss：

$$
\mathcal L_{\mathrm{aux}}
=
\alpha K\sum_{i=1}^{K}F_iG_i.
$$

其中 $F_i$ 是 expert $i$ 被分配到的 token 比例：

$$
F_i=
\frac{1}{P+M}
\sum_{x}
\mathbf 1\{\arg\max P(x)=i\},
$$

$G_i$ 是 router 对 expert $i$ 的平均 probability：

$$
G_i=
\frac{1}{P+M}
\sum_x
P_i(x).
$$

总目标：

$$
\mathcal L_{\mathrm{total}}
=
\mathcal L_{\mathrm{CE}}
+
\mathcal L_{\mathrm{aux}}.
$$

直观解释：CE 让模型答对问题，auxiliary loss 让 router 不要只依赖一个 expert。对触觉-语言任务，这个辅助项的意义是让 experts 有机会分化出 tactile/text preference。

### 2.6 两阶段训练为什么必要

#### Stage I: Tactile Token Adaptation for LLM

Stage I 不启用 MoE，只训练 adapter，让 LLM 先学会把 tactile pseudo-tokens 当作可读输入。目标是 teacher-forcing 的 token-level CE：

$$
\mathcal L_{\mathrm{CE}}
=
-
\mathbb E
\left[
\log \pi_\theta(Y_i|V,T_{<i})
\right].
$$

训练数据来自 Touch100k 的 touch-language pairs，任务像 touch-to-text generation。

#### Stage II: End-to-end Fine-tuning with MoE

Stage II：

- touch encoder 继续冻结；
- word embedding 不调整；
- adapter 继续训练；
- LLM self-attention 用 LoRA fine-tune；
- FFN 从 dense upcycle 成 sparse MoE；
- 加入 $\mathcal L_{\mathrm{aux}}$。

Table 8 训练配置：

| 配置 | Stage I | Stage II |
|---|---:|---:|
| Optimizer | Adam | Adam |
| Learning rate | $5\times10^{-4}$ | $2\times10^{-5}$ |
| Weight decay | 0.001 | 0.001 |
| Epochs | 1 | 1 |
| Warmup ratio | 0.1 | 0.1 |
| Scheduler | Linear | Linear |
| Batch size per GPU | 16 | 16 |
| Max token length | 512 | 512 |
| Unfreeze LLM | no | yes |
| Enable MoE | no | yes |

### 2.7 TactileBench 数据集：不是只换评测指标

TactileBench 的设计目标是把 tactile QA 从模板化属性选择推到 free-form reasoning。数据构造：

| 维度 | 内容 |
|---|---|
| Base source | Touch and Go material classification test set |
| Question count | 600 questions |
| Objects | 14 objects |
| Answers | 每题 3-5 ground-truth answers |
| Task split | FPU 50%, TIP 30%, CDR 20% |
| Physical properties | material, elasticity, roughness, mass, hardness, sharpness, texture, bumpiness |
| Interactive characteristics | graspability, prickliness, bendability, malleability |
| Evaluation | METEOR + GPT-4 + DeepSeek-R1 |

三个子任务：

| 子任务 | 含义 | 对机器人有什么价值 |
|---|---|---|
| FPU | Fundamental Property Understanding | 从触觉识别硬度、粗糙度、质地等 |
| TIP | Tactile Interaction Perception | 判断 graspability、刺痛感、可弯曲性、可塑性等交互属性 |
| CDR | Commonsense-Driven Reasoning | 结合触觉属性与常识判断用途/行为 |

重要限制：TactileBench 的问答由 GPT-4o 辅助生成并人工校验，ground truth 不是直接由力/接触物理测量得到。因此它评估的是 tactile-language commonsense alignment，不是严格物理参数估计。

## 3. 训练、数据与实验

### 3.1 实验设置

| 项 | 设置 |
|---|---|
| Base LLM | Vicuna-7B v1.5 |
| Touch encoder | TLV-Link tactile representation model |
| Adapter | linear projection |
| MoE | Stage I dense FFN replicated/upcycled into experts；router top-k activation |
| Fine-tuning | Stage II self-attention 用 LoRA；FFN 替换为 MoE |
| Hardware | Nvidia A100-80G |
| Batch size | 16 |
| Stage I data | Touch100k touch-language pairs |
| Stage II data | video-based PhysiClear + self-constructed tactile instruction dataset |
| Generated instruction data | 5K unique touch-language instruction-following data |

### 3.2 Table 1：整体指标是否支持 STOLA 的故事

| Model | PhysiClear CIDEr | PhysiClear B@4 | PhysiClear METEOR | TactileBench METEOR | TactileBench GPT-4 | TactileBench DeepSeek-R1 |
|---|---:|---:|---:|---:|---:|---:|
| Touch-LLM | - | - | - | 17.92 | 6.88 | 7.06 |
| Octopi-7B | 138.60 | 64.16 | 77.63 | 21.47 | 6.91 | 7.17 |
| Octopi-13B | 141.20 | 64.33 | 77.79 | 28.83 | 7.85 | 7.97 |
| STOLA | **195.03** | **68.03** | **82.58** | **30.27** | **8.02** | **8.12** |

因果解释：

- STOLA 7B 在 PhysiClear 上大幅超过 Octopi-13B，尤其 CIDEr +53.83，说明提升不是简单来自 LLM 参数规模。
- TactileBench 上 STOLA 也高于 Octopi-13B，但差距更小，说明 open-ended reasoning 中 13B language prior 仍然有帮助。
- Touch-LLM 无法评估 PhysiClear，是因为它不支持 tactile temporal signals 与 text interleaving，这正是 STOLA “统一 static image / video tactile input”的价值。

### 3.3 Table 2：PhysiClear subtasks 不是全面碾压

| Model | PC | PSS | POM | PSR | OPD Combined | Hardness | Roughness | Bumpiness |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Random | 33.33 | 33.33 | 16.67 | 50.00 | 3.70 | 33.33 | 33.33 | 33.33 |
| Octopi-7B | 48.10 | 74.67 | 44.39 | 69.57 | 47.37 | 71.05 | 73.68 | 81.58 |
| Octopi-13B | 55.06 | **84.00** | **60.43** | 67.39 | **55.26** | **73.68** | 78.95 | 78.95 |
| STOLA | **62.28** | 74.86 | 57.32 | **69.80** | 48.72 | 61.54 | **82.05** | **82.05** |

因果解释：

- STOLA 在 Property Comparison 和 Property Scenario Reasoning 上最好，支持 MoE 对跨模态比较/场景推理有帮助。
- PSS、POM、OPD Combined 上 Octopi-13B 仍更强，说明 STOLA 不是全面支配；某些模板化选择/描述任务可能更吃语言模型规模或 Octopi 的数据/格式适配。
- 旧稿把 “82.05% 是 PSR” 写错了；82.05 出现在 roughness/bumpiness 的 OPD 属性列，PSR 是 69.80。

### 3.4 Table 3：TactileBench 三类开放任务

| Model | FPU METEOR | FPU GPT-4 | FPU DeepSeek | TIP METEOR | TIP GPT-4 | TIP DeepSeek | CDR METEOR | CDR GPT-4 | CDR DeepSeek |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Touch-LLM | 15.49 | 7.01 | 7.16 | 17.27 | 6.42 | 6.51 | 24.98 | 7.24 | 7.67 |
| Octopi-7B | 21.87 | 6.65 | 7.04 | 22.55 | 7.13 | 7.15 | 18.82 | 7.26 | 7.52 |
| Octopi-13B | 29.70 | 7.81 | 7.96 | 29.89 | 7.81 | 7.87 | 25.04 | **8.00** | **8.15** |
| STOLA | **31.34** | **8.19** | **8.28** | **31.24** | **8.03** | **7.97** | **26.15** | 7.61 | 7.96 |

因果解释：

- FPU/TIP 上 STOLA 全面领先，支持它对 tactile property 和 interaction perception 的建模更好。
- CDR 上 STOLA 的 METEOR 最高，但 GPT-4/DeepSeek-R1 评分低于 Octopi-13B，说明真正 commonsense-driven reasoning 可能更依赖语言常识规模，而不只是 tactile modality routing。
- 这对机器人很关键：触觉属性识别和交互感知更接近传感器 grounding；高层 commonsense 仍可能被语言模型 prior 主导。

### 3.5 Table 4：Ablation 的因果链

| Model | PhysiClear CIDEr | B@4 | METEOR | TactileBench METEOR | GPT-4 | DeepSeek-R1 |
|---|---:|---:|---:|---:|---:|---:|
| STOLA | **195.03** | **68.03** | **82.58** | **30.27** | **8.02** | **8.12** |
| w/o MoE | 176.79 | 66.46 | 81.55 | 28.71 | 7.44 | 7.57 |
| w/o LoRA | 166.71 | 64.46 | 80.39 | 29.32 | 7.95 | 7.97 |
| w/o Stage I | 172.52 | 64.47 | 80.55 | 29.27 | 7.72 | 7.89 |

Ablation causal chains:

- **w/o MoE → TactileBench METEOR 30.27→28.71, GPT-4 8.02→7.44**：触觉/语言 token 回到共享 FFN，modality-specific processing 消失，开放 QA 下降明显。
- **w/o LoRA → PhysiClear CIDEr 195.03→166.71**：只改 FFN/MoE 而不适配 self-attention，跨模态 token interaction 不够，说明 attention 也需要低秩适配。
- **w/o Stage I → PhysiClear CIDEr 195.03→172.52**：没有先让 adapter 把 tactile tokens 对齐到 LLM 可读空间，Stage II 的 MoE 一开始就处理混乱输入，训练不稳。

### 3.6 Routing visualization 证明了什么

论文 Figure 4/5 分析了 MoE routing：

- tactile tokens 倾向分配给 experts 3 and 4；
- text tokens 在浅层倾向 expert 2 + another expert；
- deeper layers 中 text tokens 也更常与 expert 3 组合；
- token pathways 显示专家不是随机使用，而形成 modality preference。

这部分是 STOLA 最有 insight 的证据：如果只是 Table 1 提升，我们只能说 MoE 增加了容量；routing visualization 则支持“MoE 学到了 tactile/text token 的处理分工”这一机制解释。

## 4. 核心洞见

### 4.1 STOLA 的真正 insight

STOLA 的核心 insight 是：

$$
\text{shared embedding space}
\neq
\text{shared processing pathway}.
$$

Adapter 解决的是“能否把 tactile input 放进 LLM hidden space”；MoE 解决的是“进入同一 hidden space 后，tactile/text tokens 是否应该经过同一种 FFN”。这两个问题必须分开。

### 4.2 为什么 MoE 在这里合理

MoE 对 STOLA 合理，不是因为 MoE 是大模型趋势，而是因为 tactile-language 输入天然存在 token heterogeneity：

| Token 类型 | 需要处理的信息 | 为什么共享 FFN 不理想 |
|---|---|---|
| tactile patch token | 形变、纹理、硬度、粗糙度、接触局部模式 | 低层统计和语言 token 差异大 |
| tactile temporal aggregate | 动态交互痕迹、滑动/压缩趋势 | frame pooling 已经压缩时序，后续需要专门补偿 |
| text question token | 问题语义、属性类别、推理指令 | 更接近 LLM 原生能力 |
| response token | 自然语言生成 | 需要语言流畅性和事实一致性 |

Router 允许模型对这些 token 动态分配 experts，而不是固定“触觉走 A、语言走 B”。这点对开放场景重要，因为一些 token 既携带 tactile grounding，也服务语言推理。

### 4.3 最需要保留的批判

STOLA 没有证明“触觉常识推理 = 触觉控制能力”。它证明的是，在离线 QA 中，MoE 可以改善 touch-language reasoning。真正用于机器人，还缺三步：

1. 将 tactile QA 表征接到 contact state estimation；
2. 将 contact state 接到 policy / world model / reward；
3. 在闭环控制中验证触觉语义是否减少 slip、drop、over-force、wrong contact mode。

## 5. 替代方案与理论局限

### 5.1 理论维度

STOLA 的 MoE 是 modality-level specialization，但并没有直接建模接触力学：

$$
f_n,\ f_t,\ \mu,\ \delta,\ \dot \delta,\ \mathrm{slip}
$$

这些物理变量不会显式出现在模型中。GelSight 图像包含接触形变，但 STOLA 只通过数据驱动 encoder 把它映射到 hidden tokens，并没有从接触模型推导 hardness/roughness/slip。

所以它是 tactile semantic representation，不是 tactile dynamics model。

### 5.2 算法维度

| 局限 | 影响 |
|---|---|
| 只做 7B，没有 13B STOLA | 某些 CDR/模板任务仍被 Octopi-13B 超过，语言 prior 的作用未充分分离 |
| expert 数量固定为 4 | 缺少 scaling law；不知道 task expert、sensor expert、contact-mode expert 的最优数量 |
| frame average pooling | 对动态触觉顺序建模弱，可能丢失 slip onset / stick-slip temporal pattern |
| dataset GPT-generated | ground truth 可能带语言常识偏见；不等于真实力学测量 |
| open-ended scoring 依赖 GPT-4/DeepSeek | 评估本身受 LLM judge 偏好影响 |

### 5.3 工程/实验维度

- 传感器主要是 GelSight / GelSight Mini；LinkerHand 的 tactile tensor 不是视觉式 GelSight 图像，需要重新设计 encoder。
- 实验没有机器人闭环控制，不知道回答质量是否提升 manipulation success。
- 没有触觉噪声、传感器老化、接触位置偏移、实时延迟等硬件扰动评估。
- MoE 带来参数和 routing 复杂度；在实时控制中需要测量 latency。

## 6. 对用户研究的启发

### 6.1 对 LinkerHand / 转笔的直接迁移

STOLA 不应被直接拿来做“转笔问答”。更合理的迁移是 tactile-contact expert router：

| STOLA 元件 | LinkerHand / WMTS 对应物 | 修改方式 |
|---|---|---|
| GelSight tactile tokens | LinkerHand tactile tensor / fingertip taxel history | 设计 taxel encoder，保留时序和手指局部性 |
| text question tokens | task phase / language instruction / scheduler token | 从 QA prompt 改为 phase-conditioned control context |
| MoE experts | contact-mode experts | 专家按 stick / slip / rolling / free-space / recovery 等模式分化 |
| load balancing | anti-collapse regularizer | 防止策略只依赖视觉或本体，忽视触觉 |
| free-form answer | diagnostic latent / failure label / reward feature | 不一定生成自然语言，可输出 contact state embedding |

对转笔任务，触觉 token 应该包含：

$$
h_j^t
=
f_{\mathrm{tactile}}
\left(
\tau_{j,t-L:t},
q_{j,t-L:t},
\dot q_{j,t-L:t},
a_{j,t-L:t}
\right),
$$

其中 $\tau_j$ 是第 $j$ 个手指/区域的 tactile history，$q,\dot q,a$ 提供本体和动作上下文。仅靠当前触觉帧很难判断滑移是否正在发生。

### 6.2 对 WMTS 的使用位置

STOLA 类模块可以放在三个位置：

| 位置 | 作用 | 风险 |
|---|---|---|
| World model observation encoder | 把触觉压成 contact-aware latent | 若训练目标只是 reconstruction，可能学不到任务相关接触 |
| PPO / Diffusion Policy backbone | 为 actor/denoiser 提供 tactile-contact experts | routing latency 和 on-policy stability 需要实测 |
| Failure classifier / reward model | 把 slip、unstable grasp、over-force 翻译成 reward or termination signal | 离线 QA 数据不够，必须用机器人 rollouts 标注 |

最务实的第一步不是训练 tactile LLM，而是训练一个小型 MoE tactile encoder：

$$
(\tau_{t-L:t}, q_{t-L:t}, a_{t-L:t})
\rightarrow
\{p_{\mathrm{slip}}, p_{\mathrm{stable}}, p_{\mathrm{overforce}}, h_{\mathrm{contact}}\}.
$$

### 6.3 可验证实验建议

| 实验 | 设计 | 证伪条件 |
|---|---|---|
| tactile MoE vs shared FFN | 同样输入下比较 contact-state classifier / policy success | MoE routing 不形成 contact-mode preference，或成功率不升 |
| frame pooling vs temporal encoder | 用 average pooling、TCN、Transformer 比较 slip onset detection | average pooling 同样好，则 STOLA 的视频处理足够 |
| modality collapse test | 训练 visual+proprio+tactile policy，mask tactile 看性能变化 | mask tactile 几乎不掉，说明触觉没被使用 |
| reward shaping from tactile labels | 用 slip/stable labels shaping PPO | 若 reward 被模型误判污染，策略可能学会规避传感而非改善接触 |
| expert interpretability | 可视化不同 contact phase 的 router distribution | 若 router 只按 token position 而非 contact mode 分流，机制不成立 |

### 6.4 不应过度外推的点

- STOLA 的 “commonsense reasoning” 与控制中的 contact dynamics 是两件事。
- GelSight 视觉触觉与 LinkerHand 阵列触觉的 inductive bias 不同，encoder 不能直接复用。
- CDR 子任务更多依赖语言常识，不能当作机器人物理推理能力证明。
- MoE 的收益来自 routing + training strategy + data；单独加 experts 未必有用。

## 7. 与知识体系的联系

### 7.1 与 [[SignalProcessing]] 的联系

GelSight tactile image 是接触形变的光学信号，STOLA 把局部 patch 当成 tokens。对 LinkerHand，等价问题是把 taxel time series 变成 contact tokens。区别在于：GelSight 更像局部图像，LinkerHand tactile 更像多通道稀疏压力场。

### 7.2 与 [[RepresentationLearning]] 的联系

STOLA 是动态表征分解：不是固定每个 modality 一个 head，而是每层每个 token 选择 experts。它与普通 multimodal alignment 的差别是，alignment 后仍保留 modality-specific computation。

### 7.3 与 [[EmbodiedAI]] 的联系

触觉是 embodied AI 中少数真正依赖物理接触的模态。STOLA 证明 tactile-language reasoning 可以用 LLM 框架推进，但也提醒我们：语言回答不是具身能力的终点，必须接回感知-动作闭环。

### 7.4 与 [[ReinforcementLearning]] 的联系

在 RL 中，触觉语义最有价值的形式不是自然语言答案，而是 state abstraction 和 reward/failure signal。STOLA 的 MoE router 可以启发 PPO actor/critic 的 multimodal backbone，但 PPO 的 advantage、logprob、exploration 问题仍独立存在。

### 7.5 与 [[ControlTheory]] 的联系

对灵巧手，触觉最终要服务于接触稳定性和控制律切换：检测 slip、调阻抗、限制力、触发 regrasp。STOLA 没有这些控制闭环，因此只能作为触觉表征层的参考，而不是控制算法。

### 7.6 簇内定位与暗线锚点（触觉操作簇）

在“触觉表征丰富度谱”上，STOLA 位于**语义/语言最右端**：触觉被升维成 language token 求 open-ended 推理，但尚未闭环控制。它是全簇里唯一“把触觉转成语义”而非“转成控制观测”的一篇。

| 簇内对照 | Delta（本文相对它） |
|---|---|
| [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] | 谱的两极：Touch Dexterity 把触觉压到 1-bit 求 sim-to-real 稳（丢信息换鲁棒）；STOLA 把触觉升到 language token 求语义推理（加语义换 reasoning）。 |
| [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map]] / [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] | 都在问“触觉该被转成什么中间量”：Tacmap→penetration geometry，AnyRotate→物理特征 $(P,F)$，STOLA→language/semantic tokens。前两者服务 control observation，STOLA 服务 offline reasoning。 |
| [[Visual-tactile Pretraining for Humanlike Manipulation Dexterity]] | 都做触觉表征预训练：VT 用 masked reconstruction 学 contact-relevant attention 供 PPO；STOLA 用 MoE routing 学 modality-specific 处理供 LLM QA。 |

**精确 Foundation 锚点（把 §7.1/§7.2 的泛链落实）**：

- [[RepresentationLearning#5. 多模态融合：视触觉的交响|RepresentationLearning §5]]：STOLA 的 MoE token routing 是 §5 融合谱系里“shared embedding ≠ shared pathway”的一支——对齐后仍保留 modality-specific computation。
- [[SignalProcessing#3. 视觉触觉传感 (VTS)：把触觉变成视觉问题|SignalProcessing §3]]：GelSight patch token 的物理来源就是 §3 的 VTS 光学信号（接触形变→图像）。

**暗线挂载（主动感知：触觉→物理属性语义）**：STOLA 的 FPU/TIP 子任务本质是把触觉映射到 hardness/roughness/graspability 等物理属性，对应 [[InformationTheory#3.3 扩展到物理属性：摩擦图与刚度图|InformationTheory §3.3]] 的“触觉估计物理属性图”。若把 contact-mode experts 接回控制，则是 POMDP belief 的 modality-specialized 编码器（参见 [[ReinforcementLearning#2.1 MDP 与 POMDP：把"试错"写成数学|ReinforcementLearning §2.1]]）。

---

## 8. 应主动追问的颗粒度

| 用户式追问 | recap 应主动补充 |
|---|---|
| “STOLA 为什么不是普通 adapter？” | Adapter 只做输入对齐；MoE 在 LLM 内部做 token-level processing 分流 |
| “MoE 公式里的 $F_i,G_i$ 是什么？” | $F_i$ 是 token assignment fraction，$G_i$ 是 mean router probability，用于 load balancing |
| “实验证明 MoE 还是只证明参数更多？” | Table 4 证明 w/o MoE 下降；Figure 4/5 routing preference 支持 modality specialization |
| “它和灵巧手有什么关系？” | 关系不是 QA，而是 tactile-contact expert routing、failure classifier、reward/contact latent |
| “它的局限是什么？” | 离线 QA、GelSight 特定、GPT-generated data、CDR 仍受语言 prior 主导、无控制闭环 |

## References

- Cheng, N. et al. **STOLA: Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning in Open-Ended Scenarios**. AAAI 2026.
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]]
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]]
- [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map]]
- [[Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture]]
- [[SignalProcessing]]
- [[RepresentationLearning]]
- [[EmbodiedAI]]
- [[ReinforcementLearning]]
- [[ControlTheory]]
