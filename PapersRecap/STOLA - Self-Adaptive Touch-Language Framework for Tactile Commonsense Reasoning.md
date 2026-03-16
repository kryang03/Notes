---
tags:
  - paper
  - tactile-sensing
  - multimodal
  - mixture-of-experts
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
---

# STOLA: Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning in Open-Ended Scenarios

> [!abstract] 核心贡献
> 首次将 Mixture-of-Experts (MoE) 引入触觉-语言模型，通过动态路由在 token 级别区分并管理触觉与语言模态，在 PhysiClear 和自建 TactileBench 基准上实现 SOTA 触觉常识推理性能。

## 1. 问题设定与动机

触觉常识推理的两大挑战：
1. **模态差异 (Modality Discrepancy)**: 触觉与语言有不同的神经通路，现有模型（如 Octopi）将触觉简单映射到文本表征空间，忽略语义差异
2. **开放场景触觉数据稀缺**: PhysiClear 仅覆盖 3 种物理属性（硬度/粗糙度/凸起度），采用模板化 QA 格式，无法反映真实开放场景

## 2. 核心方法

### 2.1 MoE 架构

- **Touch Encoder**: 支持 GelSight / GelSight Mini 单帧或时序数据
- **Touch-Language Adapter**: 触觉嵌入→LLM 空间映射
- **MoE-enhanced LLM blocks**: 每个 block 中:
  - 共享 Self-Attention（跨模态）
  - MoE 路由器 + 多个 FFN Expert（动态分配 token 级知识）
  - 触觉/语言 token 被路由到不同 expert 组合

### 2.2 两阶段渐进训练

1. **Stage 1**: Adapter 对齐 — 冻结 encoder + LLM，训练 adapter
2. **Stage 2**: 全量微调 — 解冻 MoE experts，端到端优化

### 2.3 TactileBench 数据集

- 8+ 物理属性, 4 交互特征, 多样常识知识
- 自由形式问答（非模板化）
- 3 子任务: FPU (基本属性理解), TIP (触觉交互感知), CDR (常识驱动推理)
- 600 问题, 14 物体, Touch and Go 测试集为基础

## 3. 实验结果

**PhysiClear Benchmark**:
- STOLA 总体准确率 69.80%（Octopi-13B: 67.39%, Touch-LLM: 50.00%）
- Property Scenario Reasoning 子任务: 82.05%（最优）

**TactileBench**:
- FPU: METEOR 31.34, GPT-4 score 8.19（均为最优）
- TIP: METEOR 31.24, GPT-4 score 8.03
- CDR: 与 Octopi-13B 竞争性

## 4. 核心洞见 (Insights)

1. **MoE 适配多模态管理**: route 机制天然适合处理语义差异大的模态 — 在 LLM 内部实现"分而治之"
2. **开放式评估的必要性**: 模板化 QA 无法衡量真实推理能力 → 自由形式 + GPT-4/DeepSeek-R1 评估更合理
3. **触觉作为独立模态**: 与视觉的简单对齐不足 → 需要专门的表征通道，MoE 提供了这一可能

## 5. 与知识体系的联系

### 与 [[SignalProcessing]] 的联系
- 触觉信号的时空编码 → GelSight 时序数据包含丰富的接触动态信息
- 信号→语义的映射本质是触觉信号处理的终极形式

### 与 [[RepresentationLearning]] 的联系
- MoE 实现模态特定的表征路由 → 与 multi-task representation learning 中 task-specific head 的思想类似
- 触觉-语言对齐 → 跨模态表征学习

### 与 [[EmbodiedAI]] 的联系
- Touch-Language Model 是 VLA 范式在触觉维度的延伸
- 触觉常识推理是具身智能"理解物理世界"的关键能力

## 6. 局限与未来方向

- 仅在离线数据集上评估，未集成到机器人操作闭环
- 触觉传感器限于 GelSight 系列，泛化到其他类型（电容/压电）待验证
- MoE expert 数量和路由策略的消融不够充分
- CDR 子任务仍依赖语言先验而非真正的物理推理
