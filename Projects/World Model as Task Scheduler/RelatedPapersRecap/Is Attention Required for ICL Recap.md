---
tags: [paper, in-context-learning, transformer, WMTS]
aliases: [Attention for ICL]
paper-year: 2024
related: ["[[RepresentationLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[IS ATTENTION REQUIRED FOR ICL - EXPLORING THE RELATIONSHIP BETWEEN MODEL ARCHITECTURE AND IN-CONTEXT LEARNING ABILITY.pdf]]"
---
# Is Attention Required for ICL?
> [!abstract] 核心贡献
> 系统分析不同架构（Attention vs MLP vs State-Space）的 In-Context Learning 能力差异。发现 Attention 并非 ICL 的必要条件。

## 与 WMTS 关联
- **WM 架构选择参考**：WMTS WM 需要在线适应（ICL-like），论文证明 SSM/MLP 也能实现
- 如果 Attention 不是必须的 → WMTS 可用更轻量架构（MLP Ensemble）实现在线适应
- ICL 视角审视 WMTS WM 的历史窗口 $H$：是否在"学习适应"而非"记忆"
