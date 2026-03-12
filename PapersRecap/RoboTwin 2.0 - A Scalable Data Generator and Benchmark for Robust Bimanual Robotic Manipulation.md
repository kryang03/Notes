---
tags:
  - paper
  - bimanual
  - data-generation
  - domain-randomization
  - sim-to-real
  - benchmark
aliases:
  - RoboTwin 2.0
paper-year: 2025
read-date: 2026-03-13
venue: arXiv (SJTU / HKU / Shanghai AI Lab)
related:
  - "[[EmbodiedAI]]"
  - "[[ReinforcementLearning]]"
---

# RoboTwin 2.0 - A Scalable Data Generator and Benchmark with Strong Domain Randomization for Robust Bimanual Robotic Manipulation

> [!abstract] 核心贡献
> 提出 **RoboTwin 2.0**，面向双臂操作的可扩展仿真数据生成框架：(1) MLLM + simulation-in-the-loop 自动生成高质量专家轨迹；(2) 5 轴强域随机化（杂物/光照/背景/桌面高度/语言指令）；(3) RoboTwin-OD 物体库（731 实例，147 类别）；(4) 50 任务 × 5 机器人 benchmark，零样本仿真训练策略相比 10-demo 真实基线提升 228%。

> [!tip] 与理论基础的关联
> - [[EmbodiedAI]] — VLA 模型数据生态，双臂操作基准
> - [[ReinforcementLearning]] — Sim-to-real transfer, domain randomization 实践

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
双臂 VLA 模型的瓶颈是数据——通过 MLLM 自动化编程 + 强域随机化 + 跨构型适配，以仿真数据替代或补充少量真实示教。

### 关键创新
1. **MLLM + Sim-in-the-Loop** — 大语言模型生成任务代码，仿真执行反馈迭代修正，代码生成成功率 71.3%（vs 前代 47.4%）
2. **5 轴结构化域随机化** — 不是简单纹理随机，而是在杂物密度、光照方向、桌面高度等结构性因素上随机化
3. **Embodiment-aware adaptation** — 根据不同机器人 DoF 的抓取策略差异（如低 DoF Piper 侧向抓取 vs 高 DoF Franka 顶部抓取），自动适配操作候选
4. **大规模开源** — 100k+ 轨迹，731 物体，50 任务，5 构型

### 核心发现
- 仅用仿真数据零样本即可获得 228% 的相对提升
- 仿真 + 10 条真实示教混合训练相比纯 10 条真实提升 367%
- 域随机化对 sim-to-real 的贡献远大于数据量增加

## 2. 对灵巧操作的启发 (Implications)

> [!note] DNPM 项目关联
> - RoboTwin 2.0 聚焦双臂而非灵巧手，但其**域随机化策略**和**自动化数据生成管线**可迁移到灵巧手仿真
> - 5 轴域随机化的设计哲学（结构化 > 随机纹理）与 DNPM 中物体物理属性随机化（质量/惯量/摩擦）一致
> - MLLM 生成操作代码的范式未来可扩展到灵巧手任务分解

## 3. 演进脉络定位 (Evolution Context)

```
RoboTwin 1.0 (2024): 基础双臂数据生成
    ↓ + MLLM 代码生成 + 域随机化
本论文: RoboTwin 2.0 (可扩展 + 强域随机化)
    ↓
后续: 跨灵巧手的自动数据生成？
```
