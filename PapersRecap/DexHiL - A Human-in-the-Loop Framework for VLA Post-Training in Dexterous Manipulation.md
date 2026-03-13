---
tags:
  - paper
  - manipulation
  - vla
  - human-in-the-loop
aliases:
  - DexHiL
paper-year: 2026
read-date: 2026-03-13
venue: arXiv
related:
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[RepresentationLearning]]"
  - "[[ControlTheory]]"
---

# DexHiL: A Human-in-the-Loop Framework for Vision-Language-Action Model Post-Training in Dexterous Manipulation

> [!abstract] 核心贡献
> 首个将 Human-in-the-Loop (HiL) 范式应用于灵巧操作 VLA 模型后训练的完整框架，通过干预感知加权机制（intervention-aware weighting）使纠正性数据在训练中获优先级，平均成功率比纯离线微调提升 25%。

## 1. 问题设定与动机

VLA 模型在灵巧操作的后训练阶段面临三重挑战：
1. **高维动作空间收敛困难**：多指接触动力学使策略收敛极为困难
2. **样本效率瓶颈**：离线数据集被重复成功数据主导
3. **遥操作精度不足**：外骨骼等传统接口无法精确映射高 DOF 手部运动

现有 VLA 后训练策略（SFT on offline dataset）无法弥补高维末端执行器控制与接触丰富操作间的鸿沟。

## 2. 核心方法

### 2.1 模块化遥操作系统

- **手臂遥操作**: ArUco 标记追踪 + Franka Panda 7-DOF
- **灵巧手重定向**: 模块化设计 — 4 个手指网络 + 1 个拇指网络独立训练
- **硬件**: Franka Research 3 + DexHand021 灵巧手 + Manus 手套 + RealSense D455/D435

### 2.2 DexHiL 后训练框架

**三阶段流程**:
1. **Warm-up**: 60 条离线轨迹全量微调 Being-H0.5 VLA（Flow Matching 动作头）
2. **Online HiL Loop**: 每轮部署 → 人类发现失败即介入 → 聚合数据 $D_i \leftarrow D_{i-1} \cup D_i'$
3. **Data Filtering**: 仅保留从最后一次介入到任务完成的片段，避免多次介入导致的动作不连贯

### 2.3 干预感知加权机制

通过重要性采样重新加权：

$$w(o, a, c) = \frac{P^*(c)}{P(c)}$$

设定 $P^*(\text{intervention}) = 0.5$，使稀疏的干预数据获得与大量正常数据对等的梯度贡献。结合 Flow Matching 损失：

$$\ell_{\text{IL}}(\theta; o, a) = \mathbb{E}_{t, x_t} \| v_\theta(x_t, t, o) - u_t(a | x_0) \|_2^2$$

## 3. 实验结果

| 方法 | Tissue Extraction (R3) | Plush Toy Grasping (R3) |
|------|:---:|:---:|
| **DexHiL** | **19/20 (95%)** | **13/20 (65%)** |
| DAgger* | 16/20 (80%) | 4/20 (20%) |
| Offline Baseline | 15/20 (75%) | 7/20 (35%) |

- 每次介入片段仅需 ~3s（离线收集 ~10s），总人力时间减少 35%
- 3 轮训练后，Tissue Extraction 接近完美成功率

## 4. 核心洞见 (Insights)

1. **干预数据的高信息密度**: 人类纠正性演示携带的梯度信号远高于重复性成功数据 → 与 [[ReinforcementLearning#2.3 Deep Q-Networks|DQN]] 中 prioritized replay 的思想类似
2. **Flow Matching 适配灵巧操作**: 比 diffusion policy 在灵巧手高维空间中更自然 — 速度场预测框架 $v_\theta$ 直接学习噪声到动作的映射
3. **模块化手指重定向**: 上下独立网络降低了 DOF 映射维度，回避了高维联合重定向的困难
4. **Loss spike 是学习信号**: 每轮 HiL 后 loss 出现尖峰表明引入了关键的 OOD 纠正状态

## 5. 与知识体系的联系

### 与 [[EmbodiedAI]] 的联系
- Being-H0.5 作为 VLA backbone → 灵巧操作后训练范式的验证
- 与 π0、OpenVLA 等 VLA 家族属于同一代际，但 DexHiL 聚焦后训练而非预训练

### 与 [[ReinforcementLearning]] 的联系
- DAgger 框架的灵巧操作扩展 — 干预感知加权可视为 "带重要性采样的 DAgger"
- 介入数据与 "expert demonstrations" 在 IL 理论中的角色平行

### 与 [[ControlTheory]] 的联系
- 遥操作系统设计中的运动学重定向精度直接决定后训练数据质量

## 6. 局限与未来方向

- 仅在 2 个任务上验证（tissue extraction, plush toy grasping），复杂多步任务效果待测
- 需人类实时监督 → 自主的失败检测+恢复仍是开放问题
- 3 轮训练可能不够展示饱和/退化趋势
- 灵巧手遥操作精度仍为瓶颈（仅 Manus 手套→DexHand021 映射）
