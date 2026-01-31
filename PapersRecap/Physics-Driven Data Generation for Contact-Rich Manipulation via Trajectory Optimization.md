---
tags:
  - paper
  - trajectory-optimization
  - data-generation
  - contact-rich
  - cross-embodiment
aliases:
  - PhysicsGen
  - Physics-Driven Data Generation
paper-year: 2025
read-date: 2026-02-01
related:
  - "[[Optimization]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[ReinforcementLearning]]"
---

# Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization

> [!abstract] 核心概要
> 利用轨迹优化将少量人类演示自动扩增为大规模、物理一致的接触丰富轨迹数据集，支持跨具身迁移和域随机化，实现零样本硬件部署。

> [!tip] 与理论基础的关联
> - [[Optimization#轨迹优化]] - 接触隐式轨迹优化 (CITO)
> - [[Dynamics#接触动力学]] - 物理一致的轨迹生成
> - [[ContactMechanics#多接触规划]] - 复杂多接触交互
> - [[ReinforcementLearning#Diffusion Policy]] - Diffusion Policy 训练
>
> **核心技术**: VR Demo Collection, Kinematic Retargeting, Demonstration-Guided Trajectory Optimization

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
人类演示提供全局引导（何时何处接触），轨迹优化提供局部优化（物理可行性），两者结合高效生成大规模接触丰富数据。

### 直观隐喻
就像有经验的木匠先粗略画出榫卯位置（人类演示），然后用精密工具精确加工（轨迹优化）——粗略的全局指导 + 精确的局部优化。

### 领域定位
```
MimicGen: 运动学重放（无物理）
    ↓
RL + Demo: 需要大量采样
    ↓
PhysicsGen: 演示引导 + 轨迹优化 → 物理一致数据 ← 本文
```

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人工作 | 限制 | PhysicsGen 突破 |
|---------|------|----------------|
| MimicGen | 运动学重放，接触任务失败 | **轨迹优化保证物理可行** |
| RL + Demo | 采样效率低 | **直接优化** |
| CITO | 需要好的初始猜测 | **演示提供全局引导** |
| 单具身数据 | 每个机器人需单独收集 | **跨具身迁移** |

### 关键贡献点
1. **VR 演示接口**: 具身无关的人手演示，Apple Vision Pro 实时可视化
2. **运动学重定向**: 将人手演示映射到不同机器人具身
3. **演示引导轨迹优化**: 用演示初始化 + 局部优化得到物理可行轨迹
4. **跨具身数据复用**: 同一演示适配 Allegro Hand / Kuka / Panda

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 数据生成流程

```
Human Demo (VR)
    ↓ Kinematic Retargeting
Robot Trajectory (kinematically feasible)
    ↓ Trajectory Optimization
Dynamically Feasible Trajectory
    ↓ Parameter Randomization
Large-Scale Dataset
    ↓ Diffusion Policy Training
Robust Policy
```

### 3.2 运动学重定向

给定演示 $x^{demo}_{0:T}$，求解机器人配置 $q^{retarget}_{0:T}$：

$$
q_t^{retarget*} = \arg\min_{q} \sum_{i=0}^{N} w_i \|\psi_i(q) - \tilde{\psi}_i(x^{demo}_t)\|^2
$$

约束：
- 非穿透: $\phi_j(q) \geq 0$
- 关节限位: $q_{min} \leq q \leq q_{max}$

其中 $\psi_i$ 和 $\tilde{\psi}_i$ 是机器人和演示的对应点映射。

### 3.3 演示引导轨迹优化

**关键洞察**: 运动学重定向的轨迹提供了：
- 接触时机
- 接触位置
- 全局运动模式

轨迹优化只需在此基础上**局部细化**：

$$
\min_{x_{0:T}, u_{0:T}} \sum_{t=0}^{T} \ell(x_t, u_t, x^{retarget}_t) + \ell_T(x_T)
$$

约束：
- 动力学: $x_{t+1} = f(x_t, u_t, \theta)$
- 接触: complementarity constraints

### 3.4 域随机化数据生成

```
Algorithm 1: Automated Data Generation
Input: 概率分布 ρ, 增强数量 N, 演示轨迹
Output: N 条动力学一致轨迹

for i = 1 to N:
    θ ~ ρ  # 采样物理参数
    x_init ~ P_init  # 采样初始条件
    
    # 以重定向轨迹为初始猜测
    x_opt = TrajOpt(x_retarget, θ, x_init)
    
    if x_opt is feasible:
        Dataset.add(x_opt)
```

### 3.5 具身配置

| 具身 | DoF | 任务 |
|-----|-----|-----|
| Floating Allegro Hand | 22 | Cube manipulation |
| Bimanual Kuka iiwa | 14 | Box manipulation |
| Bimanual Panda | 14 | Box manipulation |

**跨具身泛化**: 同一套人手演示适配所有三种具身！

## 4. 实验与验证 (Experiments)

### 数据效率
- **输入**: 24 条人类演示（约 7 分钟收集）
- **输出**: 数千条物理一致轨迹

### 零样本硬件部署
- 平台: Bimanual Kuka iiwa
- 任务: Box reorientation
- 成功率: **高**（无需真实数据微调）

### 与 MimicGen 对比
| 方法 | 接触任务成功率 |
|-----|---------------|
| MimicGen | 低（运动学重放失败） |
| **PhysicsGen** | **高** |

## 5. 批判性分析 (Critical Analysis)

### 优势
- **物理一致**: 轨迹优化保证动力学可行
- **跨具身**: 演示可复用到不同机器人
- **低成本**: VR 演示无需真实硬件
- **接触丰富**: 专门针对多接触任务设计

### 局限性
- 需要高质量物理仿真器
- 轨迹优化计算成本
- 复杂任务可能需要更多演示

### 未来方向
- 更复杂的灵巧操作任务
- 实时轨迹优化
- 与学习方法结合

## 6. 对灵巧操作的启发 (Implications)

1. **人类演示 = 全局引导**: 不需要精确，只需指明大方向
2. **轨迹优化 = 局部细化**: 处理物理细节和接触
3. **跨具身潜力**: 未来可能实现"一次演示，多机器人部署"
4. **接触丰富任务**: MimicGen 失效的场景

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── MimicGen (2023): 运动学演示扩增
├── CITO: 接触隐式轨迹优化
└── Sampling-based Planning: 高熵轨迹问题

本论文: PhysicsGen (2025)
├── VR 演示 + 运动学重定向
├── 演示引导轨迹优化
├── 跨具身数据生成
└── 零样本硬件部署

后续影响:
├── 大规模物理一致数据集
├── 通用机器人基础模型
└── 接触丰富任务的数据引擎
```

## 8. 与相关方法的对比

| 方面 | MimicGen | CyberDemo | PhysicsGen |
|-----|----------|-----------|------------|
| 演示来源 | 真实/仿真 | 仿真 | VR |
| 数据扩增 | 运动学 | 视觉+物理 | 轨迹优化 |
| 接触任务 | 受限 | 需仿真 | **专门设计** |
| 跨具身 | ❌ | ❌ | **✅** |
| 物理一致性 | ❌ | 部分 | **✅** |
