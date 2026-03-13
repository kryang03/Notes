---
tags:
  - paper
  - vla
  - human-in-the-loop
  - dexterous-manipulation
  - post-training
aliases:
  - DexHiL
paper-year: 2026
read-date: 2026-03-13
venue: arXiv (CASIA / SJTU / Shanghai AI Lab)
related:
  - "[[EmbodiedAI]]"
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
---

# DexHiL: A Human-in-the-Loop Framework for Vision-Language-Action Model Post-Training in Dexterous Manipulation

> [!abstract] 核心贡献
> 提出 **DexHiL**，首个面向灵巧操作的**臂-手协同 Human-in-the-Loop VLA 后训练**框架。通过干预感知数据采样策略（优先纠正性片段）+ 实时人类干预接口，将 VLA 模型从离线 SFT 基线上提升 25% 平均成功率。采用 MoT (Mixture-of-Transformers) 架构，基于 Being-H0.5 权重初始化。

> [!tip] 与理论基础的关联
> - [[EmbodiedAI#2.5 VLA Post-Training]] — HiL 后训练范式：从纯 SFT 到在线干预
> - [[ReinforcementLearning#5. Sim-to-Real]] — DAgger 循环 + 干预感知重加权
> - [[RepresentationLearning]] — MoT 快慢专家架构的动作生成
>
> **核心技术**: Intervention-Aware Sampling, DAgger Loop, MoT Architecture, Two-Stage Hand Retargeting

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
纯离线 VLA 微调在灵巧操作中因协变量偏移和高维动作空间收敛困难而瓶颈明显；DexHiL 通过实时人类干预 + 干预感知数据重加权，以极少的在线数据大幅突破性能天花板。

### 领域定位
- **VLA 后训练前沿**: Offline SFT → Online RL (WMPO/GRPO) → **Interactive HiL (DexHiL)**
- **核心挑战**: 灵巧手高维动作空间（多指）+ 接触密集 + 执行分布与臂运动显著不同
- **关键突破**: 干预感知权重 $w(o, a, c)$ 使策略优先学习纠错行为而非重复成功行为

## 2. 核心创新与贡献 (Contributions & Novelty)

### 关键贡献点
1. **首个臂-手协同 HiL 框架** — 单系统内同时支持臂和灵巧手的实时人类干预
2. **干预感知数据采样** — 在线数据中优先采样人类纠正片段，解决离线数据中成功行为重复但转折行为稀疏的问题
3. **两阶段手部重定向** — 先训练 4 指网络，再训练拇指网络，提升遥操作精度
4. **DAgger 循环训练** — Warm-up (离线 SFT) → DAgger Loop (在线干预 + 重加权训练) 的两阶段流程

### 实验结果
- 3 轮在线迭代后，两个灵巧任务分别提升 20% 和 30% 成功率（vs 等量离线数据基线）
- 消融验证：干预感知权重机制是性能提升的主导因素

## 3. 对灵巧操作的启发 (Implications)

**与 DNPM 的关联**: DexHiL 的 HiL 范式为 RL 训练后的策略精调提供了一种互补路径——如 DNPM 项目中的 TWC 课程学习在达到性能平台后，可引入 HiL 干预来突破瓶颈。

## 4. 演进脉络定位 (Evolution Context)

```
VLA Offline SFT (OpenVLA, π₀)
    ↓ 性能天花板
VLA Online RL Post-Training (WMPO, GRPO)
    ↓ 灵巧操作适配困难
本论文: DexHiL (Human-in-the-Loop Post-Training)
    ↓
后续影响: HiL + RL 混合后训练
```
