---
tags:
  - paper
  - tactile
  - touch-language
  - mixture-of-experts
  - commonsense-reasoning
aliases:
  - STOLA
  - SToLa
paper-year: 2026
read-date: 2026-03-13
venue: AAAI 2026
related:
  - "[[SignalProcessing]]"
  - "[[RepresentationLearning]]"
  - "[[InformationTheory]]"
---

# STOLA - Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning in Open-Ended Scenarios

> [!abstract] 核心贡献
> 提出 **SToLa**，首个将 **Mixture of Experts (MoE)** 引入触觉-语言多模态融合的框架，通过 token 级路由动态分配触觉/语言模态的专家网络，解决传统方法将触觉简单映射为视觉/语言子空间的模态鸿沟问题。同时构建首个开放场景触觉常识推理数据集（8种物理属性 + 4种交互特征 + 自由形式问答）。

> [!tip] 与理论基础的关联
> - [[SignalProcessing]] — 触觉时序信号编码，GelSight/GelSight Mini 传感器处理
> - [[RepresentationLearning]] — MoE 架构的模态解耦，touch encoder 设计
> - [[InformationTheory]] — 模态鸿沟的信息论分析，专家路由的信息分配
>
> **核心技术**: Mixture of Experts, Touch-Language Alignment, Progressive Training

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
触觉和语言是语义本质不同的模态——不应简单对齐到同一空间，而应通过 MoE 动态路由让不同专家处理不同模态 token。

### 关键创新
1. **MoE 触觉-语言管理** — 每个 Transformer block 中共享 self-attention + MoE FFN，路由器根据 token 来源（触觉/语言）分配专家
2. **两阶段渐进训练** — Stage 1: 固定 LLM，训练 touch encoder + adapter; Stage 2: 解冻 MoE 层，联合优化
3. **开放场景数据集** — 超越 PhysiClear 的模板化 QA，构建自由形式触觉常识推理 benchmark

### 局限性
- 依赖 GelSight 系列传感器，对其他触觉传感器（如 Digit、电容触觉）的泛化性未验证
- 常识推理任务偏静态（属性识别），缺乏操作过程中的动态触觉推理

## 2. 对灵巧操作的启发 (Implications)

> [!note] 与灵巧操作的连接
> - **触觉理解的基础设施**: SToLa 的 MoE 架构为未来"触觉→操作决策"通路提供参考——MoE 可扩展到处理触觉+本体感觉+视觉的三模态融合
> - **DNPM 的间接关联**: 非紧握操作对触觉的依赖度低于紧握操作，但在接触检测和滑动感知方面，触觉-语言理解可辅助高层任务规划
> - **与 [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Penetration Depth Map|Tacmap]] 互补**: Tacmap 解决触觉的底层表征 (sim-to-real)，SToLa 解决触觉的高层理解 (commonsense reasoning)

## 3. 演进脉络定位 (Evolution Context)

```
Touch-LLM (Yang et al. 2024): 对比学习对齐触觉→VLM
    ↓
Octopi (Yu et al. 2024): PhysiClear + 模板 QA
    ↓
本论文: SToLa (MoE 动态路由 + 开放场景)
    ↓
后续: 操作指导的触觉推理 (从"是什么" → "该怎么做")
```
