---
tags:
  - paper
  - manipulation
  - non-prehensile
  - extrinsic-dexterity
  - representation-learning
aliases:
  - DAPL
  - Emerging Extrinsic Dexterity
paper-year: 2026
read-date: 2026-03-13
venue: arXiv
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[ComputationalGeometry]]"
---

# Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning

> [!abstract] 核心贡献
> 提出 DAPL（Dynamics-Aware Policy Learning）框架，通过学习物理世界模型的动力学表征来条件化 RL 策略，使 extrinsic dexterity 在杂乱场景中自然涌现，无需手工设计的接触启发式或复杂奖励塑形。在 Dense 场景中成功率（44.56%）是几何方法 CORN（22.22%）的 2 倍。

## 1. 问题设定与动机

杂乱场景中的非抓取操作（pushing, sliding, toppling）需要选择性地利用或回避环境接触 — 即 **extrinsic dexterity**。已有方法的核心缺陷：

- **几何方法** (CORN, UniCORN): 仅建模静态形状，缺乏动力学推理 → 密集杂乱下失败
- **模型基规划**: 需精确物体位姿、不可扩展至复杂场景
- **通用 RL**: 接触采样效率低，难以学到选择性接触策略

## 2. 核心方法

### 2.1 Dynamics-Aware Policy Learning (DAPL) 框架

两阶段解耦设计 + 课程式迭代：

**Stage 1 — World Model 预训练**:
- **物理场景表征**: 每个点 $x_i = (p_i, m_i, v_i)$ — 位置 + 质量 + 速度
- **Patch-based Transformer**: FPS → kNN patch → PointNet 嵌入 → ViT → MLP 解码
- **训练目标**: 点级动力学预测（位置 + 速度）

$$\mathcal{L}_{\text{dyn}} = \sum_i \| \hat{p}_i^{t+1} - p_i^{t+1} \|_2^2 + \lambda \| \hat{v}_i^{t+1} - v_i^{t+1} \|_2^2$$

- **方差正则化**: $\mathcal{L}_{\text{var}} = \| \text{Std}\{\hat{v}_i^{t+1}\} - \text{Std}\{v_i^{t+1}\} \|^2$ — 防止速度预测坍缩到零

**Stage 2 — RL 策略学习**:
- 冻结 world model 的动力学特征 $f_{\text{dy}}$ 作为策略输入条件
- Actor-Critic + 本体感知 + 任务目标
- **课程学习**: 策略 rollout 数据反过来精炼 world model → 迭代 3 轮，成功率从 61.3% → 71.8%

### 2.2 Clutter6D Benchmark

- 3 密度等级: Sparse (4 objects), Moderate (8), Dense (12)
- 6D 物体重排任务（平移+旋转）

## 3. 实验结果

**仿真 (Clutter6D Sparse track)**:

| 方法 | Sparse SR | Moderate SR | Dense SR |
|------|:---------:|:-----------:|:--------:|
| **DAPL (Ours)** | **71.88%** | **51.04%** | **44.56%** |
| CORN | 46.63% | 45.83% | 22.22% |
| UniCORN | 20.61% | 11.67% | 5.81% |
| Teleoperation | 50.0% | 40.0% | 20.0% |
| GraspGen+CuRobo | 26.6% | 15.6% | 3.13% |

**真实世界** (10 scenes, zero-shot sim-to-real):
- DAPL: 48% SR, 平均执行时间 42.6s
- Human Teleoperation: 52% SR, 平均 55.9s
- DAPL 更高效但成功率略低于人类

**消融**: 去除速度/质量物理属性 → SR 从 71.88% 降至 42.00%；用 object-level 位姿预测替代 point-level → SR 降至 16.88%

## 4. 核心洞见 (Insights)

1. **动力学 > 几何**: 在接触丰富的杂乱场景中，物体"如何响应接触"比"长什么样"更关键 → 与 [[ContactMechanics]] 的核心论点一致
2. **自适应行为涌现**: 相同几何布局、不同质量分配 → 策略自动切换接触对象（利用重物作锚点 vs 回避轻物），表明 dynamics representation 成功编码了物理属性
3. **点级预测 >> 物体级预测**: 粗粒度 6DoF 位姿监督不足以捕获接触传播的精细物理 → 密集表示的优势
4. **训练效率优势**: 动力学先验使策略在 ~10⁴ 迭代即达 70% SR，而几何方法需 3-4× 更多迭代 → 与 [[ReinforcementLearning#5.1 Domain Randomization 与 Sim-to-Real|DR]] 中 "好的表征减少采样需求" 的原理一致
5. **Zero-shot sim-to-real**: 通过 student-teacher distillation + 观测噪声注入实现 → 与 [[Dynamics#Sim-to-Real 与动力学迁移|System ID]] 互补的迁移方案

## 5. 与知识体系的联系

### 与 [[Dynamics]] 的联系
- World model 本质是学习场景级多体动力学的代理 — 不同于 analytical dynamics，此处用点级 Transformer 作为动力学近似器
- 质量+速度作为物理属性直接进入表征 → 与 [[Dynamics#刚体动力学#Newton-Euler|Newton-Euler]] 中的质量/惯量平行

### 与 [[ContactMechanics]] 的联系
- Extrinsic dexterity 的核心是选择性利用接触力传递 → 接触链的合理"借力"
- Variance-aware regularization 处理的是接触稀疏性问题 — 大部分点静止，仅少数点上有接触力

### 与 [[RepresentationLearning]] 的联系
- 动力学表征 vs 几何表征 的核心对比 → 任务相关性决定表征质量
- Patch-based Transformer 上的 point cloud 表征学习

### 与 [[ReinforcementLearning]] 的联系
- 世界模型 → RL 条件化的两阶段范式 → 类似 model-based RL 但仅用表征而非直接做 planning
- 课程式迭代精炼 → 与 [[Curriculum Learning]] 理念一致

## 6. 局限与未来方向

- 6DoF pushing 仍局限于单目标 + 周围场景的设定，多目标联合重排更复杂
- 仅用 Franka 单臂 + 平行夹爪 → 与灵巧手的 extrinsic dexterity 尚未结合
- 真实世界依赖 FoundationPose + SAM2 追踪 → 感知失败会级联影响策略
- 质量由 VLM 粗估 → 物理属性精度有天花板
