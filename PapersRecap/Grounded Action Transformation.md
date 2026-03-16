---
tags:
  - paper
  - sim-to-real
  - reinforcement-learning
aliases:
  - GAT
  - Grounded Action Transformation
paper-year: 2017
read-date: 2026-03-13
venue: AAAI 2017
paper-pdf: "[[Papers/Grounded Action Transformation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
---

# Grounded Action Transformation

> [!abstract] 核心贡献
> 提出 **Grounded Action Transformation (GAT)**——在 Grounded Simulation Learning (GSL) 框架下，通过学习动作转换函数 $a_{real} = h(s, a_{sim})$ 修正仿真-真实动力学差异，在 NAO 双足行走上实现 43.27% 速度提升。

## 1. 问题设定与动机

- **Sim-to-Real Gap 的根源**：仿真器无法完美模拟真实动力学 → 仿真训练策略直接部署性能退化
- **GSL 框架**：修改仿真器使其匹配真实世界 → 仿真中训练 → 真机评估 → 收集数据进一步修改仿真器

## 2. 核心方法

### Grounded Action Transformation (GAT)

学习映射 $a' = a + f_\theta(s, a)$，其中 $f_\theta$ 是参数化的残差模型，将仿真中的最优动作转换为真实世界中等效的动作。

**关键流程**：
1. 在真机上执行当前策略 → 收集 $(s, a, s')_{real}$ 数据
2. 对每个真实转移 $(s, a, s')_{real}$，在仿真中搜索使 $s_{sim}' \approx s'_{real}$ 的动作 $a_{sim}$
3. 学习映射 $(s, a) \mapsto a_{sim}$
4. 在修正后的仿真器中训练策略

### 与 System ID 的区别
- **System ID**：修正仿真器参数使 $T_{sim} \approx T_{real}$
- **GAT**：不修改仿真器参数，而是在动作空间中补偿差异

> [!tip] 与 [[ReinforcementLearning#5.0 系统辨识与在线参数学习|System ID]] 的联系
> GAT 与 System ID 互补：System ID 减小 $\mathbb{E}[\|T_{sim} - T_{real}\|]$，GAT 在动作层面修正残差。在灵巧手场景中，GAT 可用于补偿执行器非线性（齿隙、摩擦）导致的动作空间偏移。

## 3. 实验结果

- **平台**: SoftBank NAO 机器人双足行走
- **结果**: 步行速度提升 **43.27%**（vs 最先进手工策略）
- 验证使用高保真仿真器作为真实世界代理

## 4. 核心洞见 (Insights)

1. **动作空间修正比状态空间修正更高效**：当仿真器动力学差异主要体现在执行层面时
2. **迭代修正**：GSL 框架支持多轮 collect-ground-train 循环，逐步缩小域差异
3. **奠基性工作**：为后续 TRANSIC (在线修正) 和 DexNDM (神经动力学) 等方法提供了理论先驱

## 5. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
- Sim-to-Real 方法谱系中的"动作转换"范式——与 DR、System ID 正交
- §5.0 在线自适应方法表中的 GAT 条目

### 与 [[Dynamics]] 的联系
- 动作转换隐式补偿了动力学模型误差

## 6. 局限与未来方向

- 需要真机数据收集（非零样本）
- 动作搜索过程计算量大
- 仅验证在低维动作空间（关节角度）——高维灵巧手场景有效性待验证
