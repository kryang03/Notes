---
tags:
  - paper
  - world-model
  - conceptual
  - vision-essay
  - WMTS
aliases:
  - World Models Essay
  - Computing the Uncomputable
paper-year: 2025
read-date: 2026-06-15
venue: 业界愿景随笔 (General Intuition; co-written w/ Pim De Witte)
paper-pdf: "[[World Models Computing the Uncomputable.pdf]]"
related:
  - "[[EmbodiedAI]]"
  - "[[ReinforcementLearning]]"
  - "[[Final_WMTS]]"
---

# World Models: Computing the Uncomputable（愿景随笔）

> [!abstract] 核心贡献（一篇随笔，非研究论文）
> 这是一篇**业界愿景随笔**（General Intuition，与 Pim De Witte 合写），不是研究论文——**无方法、无实验、无公式推导**。它的价值是一个有力的**概念框架**：World Model 把"动态、难以大规模仿真的情形（如模拟整座球场上千人的随机群体行为，传统引擎 O(N)~O(N²)）"压缩成神经网络的**一次固定成本前向**，即"**computing the uncomputable**"；而把 WM 与 video model 区分开的关键是 **action**——video model 被动预测下一帧 $P(x_{t+1}\mid x_t)$（像旁观的梦），World Model 按干预预测下一状态 $P(s_{t+1}\mid s_t,a_t)$（像可塑造剧情的清醒梦）。**对 WMTS，它只在"动机/框架"层面有用（为什么用 WM、动作条件化、实时恒定成本对高频控制的意义），绝不能当技术证据引用——它是有推广意图的愿景文，作者自己都承认 WM 定义尚不清晰、炒作将至。**

> [!tip] 与理论基础的关联
> - [[EmbodiedAI]] — WM 作为物理世界控制的路径；"观察-计算-决策-行动"的具身循环。
> - [[ReinforcementLearning]] — 动作条件化 $P(s_{t+1}\mid s_t,a_t)$ 是 MDP 转移核的本质。
> - [[WorldModels]] — 本随笔的"动作条件化 + 固定成本想象"正是 [[WorldModels]] 大厦的**动机层**措辞；但它系统回避了 [[WorldModels#3. 不确定性层：模型何时在"自信地瞎编"]]（固定成本≠准确），仅可作动机引用、不作技术依据。
> - [[Final_WMTS]] — **仅供 WMTS 动机段引用**：action-conditioned WM、固定成本实时推理；不作技术依据。
>
> **核心论点**: Action-conditioned 预测 $P(s_{t+1}\mid s_t,a_t)$ vs video $P(x_{t+1}\mid x_t)$；固定成本前向"算不可算"；WM 作为新基础模型类别（>LLM for 空间时序）

## 0. 阅读定位与范本价值（含文体判定）

> [!warning] 这是愿景随笔，不是论文
> 本文是公司愿景文（General Intuition），**无方法/实验/可证伪结果**，含融资与行业站队叙事（LeCun AMI $1.03B、Fei-Fei Li World Labs $1B+、DeepMind、NVIDIA Jim Fan）。作者自承"WM 定义尚不清晰""六个月内人人自称 World Model 公司"。因此本 recap 的首要任务是**文体判定 + 批判隔离**：把可用的概念框架抽出来，明确它不能作技术证据。

它在知识库里的角色：**WMTS 动机段的措辞与直觉来源**——"为什么 WM 能做传统仿真做不到的事""动作为什么是关键"。技术上一切回到已 recap 的真论文（[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]/[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]/[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]] 等）。

## 1. 核心论点与价值（逻辑与价值）

### 1.1 一句话核心
传统引擎仿真复杂场景成本随复杂度爆炸（O(N)~O(N²)）、耗时不可预测；机器人却必须在**恒定时间内**响应任意复杂场景。World Model 把"难仿真的动态"吸收进网络权重，推理时是**固定成本前向**——于是"算不可算"，且实时性对机器人成立。

### 1.2 关键概念（值得 WMTS 借的三点）
1. **Action 作为压缩**：动作携带足够信息去 unroll 未来状态，直到下一动作更新——这把"显式模拟每个交互"换成"动作条件化的一步预测"。
2. **固定成本实时推理**：场景再复杂，前向 pass 成本不变——对高频灵巧控制（CAN 1Mbps、毫秒级）这是真需求。
3. **video vs world 的区分**：$P(x_{t+1}\mid x_t)$（被动旁观梦）vs $P(s_{t+1}\mid s_t,a_t)$（可干预清醒梦）——$a_t$ 是分界。

### 1.3 论点的可疑处（critical thinking）
- "固定成本"≠"准确"：前向成本恒定，但**预测精度**在 OOD/复杂接触处仍崩（这正是 ensemble/不确定性要解决的，随笔避而不谈）。
- "算不可算"是修辞：WM 不是计算不可计算函数，而是用学习的摊销近似替代显式仿真——**近似有误差**（model-exploitation），随笔不提。
- 行业叙事 + 融资信号 ≠ 科学证据。

### 1.4 Delta（相对真 WM 论文）
本文**没有方法增量**；它的"增量"是把 WM 的价值主张用直觉语言讲清楚（imagination 恒定成本、动作条件化、新基础模型类别）。技术内容是对 [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]] 系 $P(s_{t+1}\mid s_t,a_t)$ 的通俗复述。

## 2. 概念框架（原理与理论 → 概念，无方法）

唯一的"公式"是两个对比表达：
$$
\text{Video model（被动）: } P(x_{t+1}\mid x_t),\qquad \text{World model（干预）: } P(s_{t+1}\mid s_t,a_t).
$$
其余是类比（清醒梦 vs 普通梦、球场上千人模拟、人类恒定努力想象）。**无 latent 结构、无训练目标、无规划算法**——这些都在真论文里。故本节只记录：本文把"动作条件化"和"固定成本想象"作为 WM 的定义性特征，与库内 Dreamer/PDDM 的 $P(s'\mid s,a)$ 一致，但**不提供如何学准、如何抗误差**。

## 3. 证据状态（实验与验证 → 诚实记账）

> [!important] 无实验、无可证伪结论
> 本文不含任何实验、benchmark、消融或定量结果。其"证据"是**行业信号**（巨额融资、知名人物背书）与**直觉类比**。按知识库标准，这**不构成技术验证**。任何关于 WM 性能/可行性的主张，须回到 [[A Step Toward World Models- A Survey on Robotic Manipulation|综述]] 与单篇实证（[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]] 的 FVD、[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]] 的真机成功率等）。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 真正可取的 insight
**WM 相对传统仿真的本质优势是"把难仿真的动态摊销进权重，换取推理时的固定成本与实时性"，而动作条件化 $P(s_{t+1}\mid s_t,a_t)$ 是它区别于被动 video model 的定义性特征。** 这两点是 WMTS 动机段的好措辞。

### 4.2 为什么这个框架有传播力
用清醒梦 vs 普通梦、球场模拟等强类比，把抽象的 model-based 价值讲得直觉化；点出实时恒定成本这一机器人真痛点。

### 4.3 它回避/失效的地方
- 精度与 model-exploitation：固定成本不保证准确，随笔完全不提（而这是 WMTS 的核心难题）。
- 接触/触觉/灵巧高速：完全未涉及。
- 定义模糊 + 炒作：作者自承。

## 5. 局限与替代（未来与结合）
- **作为引用**：仅可在 WMTS"动机/愿景"段引为直觉，**不可**作方法/性能依据。
- **替代来源**：技术主张一律改引综述 + 单篇实证（[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]/[[Finetuning Offline World Models in the Real World|FOWM]]/[[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]]）。
- **批判保留**：固定成本 ≠ 准确；"算不可算"是修辞而非计算理论。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS 的（有限）用处
| 用途 | 可取处 | 注意 |
|---|---|---|
| 动机段措辞 | "固定成本实时推理""动作条件化""算不可算" | 标注为愿景，不引为证据 |
| 实时性论证 | 高频灵巧控制需恒定成本前向 | 但需配 ensemble 保精度 |
| video vs world 区分 | $a_t$ 是分界 | 与 [[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]] 的 NWM/PEVA 对照一致 |

**核心论证（critical thinking）**：这篇随笔对 WMTS 的真正用处只有一处——**给"为什么用 World Model"提供有力的直觉措辞**（固定成本实时推理、动作条件化、清醒梦类比）。但它系统性回避了 WMTS 的**全部核心难题**：精度、model-exploitation、接触/触觉、不确定性。换言之，**它讲的是 WM 的"卖点"，WMTS 要解决的是 WM 的"难点"**。把它放进知识库的正确方式是：动机段可引其直觉，但任何技术决策都必须由真论文（ensemble-LCB、结构化物理、autoregressive 训练）支撑。**它也是一面镜子**：提醒我在 WMTS 论文里**不要落入同样的修辞陷阱**——不要用"算不可算"这类口号代替"在转笔上 WM 预测误差多大、ensemble 如何抑制 model-exploitation"的硬证据。

### 6.2 可行动项
- WMTS 动机段：可借"固定成本实时推理 + 动作条件化"一句，立即接真论文证据。
- 自检清单：凡 WMTS 文稿出现 WM 价值主张，确保有单篇实证支撑，不止愿景。

### 6.3 不应做的事
- 不引本文作性能/可行性证据。
- 不沿用"算不可算"等修辞替代定量分析。

## 7. 与知识体系的联系

### 与 [[EmbodiedAI]] 的联系
"观察-计算-决策-行动"的具身循环；WM 作为物理世界控制路径的愿景表达。

### 与 [[ReinforcementLearning]] 的联系
动作条件化 $P(s_{t+1}\mid s_t,a_t)$ 即 MDP 转移核；与 model-based RL 的 $P(s'\mid s,a)$ 一致，但本文不涉及学习/规划算法。

### 与 [[WorldModels]] 的联系
本随笔只触及 [[WorldModels]] 大厦的**动机层**：动作条件化（$a_t$ 是 world model 区别于被动 video model 的分界）+ 固定成本实时想象。但它系统回避 [[WorldModels#3. 不确定性层：模型何时在"自信地瞎编"]]（固定成本≠准确，OOD/接触处仍崩）与 [[WorldModels#5. 结构层：怎么让想象"物理真实"]]（无物理结构）——恰是 WMTS 的核心难题。可引其直觉措辞，技术决策一律回真论文（[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]] 的 ensemble、[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]] 的 LCB）。

### 与 [[Final_WMTS]] 的联系
仅供 WMTS 动机段引用（固定成本实时、动作条件化）；技术决策回真论文；亦为反面镜：WMTS 须用硬证据而非口号。

## References
- 原始 PDF：[[World Models Computing the Uncomputable.pdf]]（General Intuition 愿景随笔）
- 技术依据改引：[[A Step Toward World Models- A Survey on Robotic Manipulation|综述]]、[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]、[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]、[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]、[[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]]
- 项目入口：[[Final_WMTS]]
