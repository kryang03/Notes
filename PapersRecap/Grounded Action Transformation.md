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

### 一句话核心与直观隐喻

与其修改仿真器使其"更像真实"，不如学一个"翻译器"将仿真动作转换为真实等效动作。

> 就像在弹钢琴上练习后到另一架质感不同的钢琴上演奏——不需要改造新钢琴，而是学会调整触键力度。GAT 不修改仿真器本身，而是学习在动作层面"调力度"，使仿真策略在真机上产生相同状态转移。

### 现有方法的局限

| 方法 | 局限 |
|------|------|
| 直接迁移 | 动力学差异导致策略失效 |
| System ID | 仅能匹配参数化的差异，无法处理结构性建模误差 |
| Domain Randomization | 保守策略，牺牲性能换取鲁棒性 |

- **Sim-to-Real Gap 的根源**：仿真器无法完美模拟真实动力学 → 仿真训练策略直接部署性能退化
- **GSL 框架**：修改仿真器使其匹配真实世界 → 仿真中训练 → 真机评估 → 收集数据进一步修改仿真器

## 2. 核心方法

### Delta 分析

| 维度 | System ID | Domain Randomization | GAT |
|-----|-----------|---------------------|-----|
| 修正层面 | 仿真器参数 | ​训练分布 | **动作空间** |
| 真机数据需求 | 中 (轨迹) | 无 | **低 (转移)** |
| 刹车结构性建模误差 | 不能 | 不能 | **可以** |
| 计算成本 | 低 | 中 | 中 (动作搜索) |
| 迭代改进 | 支持 | 不支持 | **支持 (GSL 循环)** |

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

> [!tip] 与 [[ReinforcementLearning#5.0 系统辨识与在线参数学习 (System Identification & Online Adaptation)|System ID]] 的联系
> GAT 与 System ID 互补：System ID 减小 $\mathbb{E}[\|T_{sim} - T_{real}\|]$，GAT 在动作层面修正残差。在灵巧手场景中，GAT 可用于补偿执行器非线性（齿隙、摩擦）导致的动作空间偏移。

## 2.1 核心 PyTorch 逻辑

```python
import torch
import torch.nn as nn

class GroundedActionTransform(nn.Module):
    """GAT: 学习动作残差映射 a' = a + f_theta(s, a)"""
    def __init__(self, state_dim: int, action_dim: int, hidden: int = 256):
        super().__init__()
        self.residual_net = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, action_dim),
        )

    def forward(self, state: torch.Tensor, action_sim: torch.Tensor) -> torch.Tensor:
        """
        state: (B, D_s) — 当前状态
        action_sim: (B, D_a) — 仿真中的最优动作
        return: (B, D_a) — 真实世界等效动作
        """
        x = torch.cat([state, action_sim], dim=-1)
        residual = self.residual_net(x)  # 学习动作偏差
        return action_sim + residual     # a_real = a_sim + f_theta(s, a_sim)

def gat_grounding_step(
    real_transitions: list,  # [(s, a_policy, s'_real), ...]
    sim_env,                 # 仿真环境
    n_search: int = 100,     # 动作搜索采样数
):
    """为每个真实转移，在仿真中搜索使 s_sim' ≈ s'_real 的动作"""
    pairs = []
    for s, a_policy, s_next_real in real_transitions:
        # 在仿真中采样多个动作，找到产生最相似 s' 的
        best_a_sim, best_dist = None, float('inf')
        for _ in range(n_search):
            a_candidate = sim_env.action_space.sample()
            s_next_sim = sim_env.step_from(s, a_candidate)
            dist = torch.norm(s_next_sim - s_next_real)
            if dist < best_dist:
                best_dist = dist
                best_a_sim = a_candidate
        pairs.append((s, a_policy, best_a_sim))  # (s, a_real, a_sim)
    return pairs  # 用于训练 GAT 映射
```

> [!note] 数学本质
> GAT 的动作搜索本质是求解逆动力学 $a_{sim} = T_{sim}^{-1}(s, s'_{real})$，用采样近似代替解析求逆。这与 [[Dynamics]] 中逆动力学求解思想一致。

## 3. 实验结果

### 训练设定详情

| 参数 | 值 |
|------|------|
| 平台 | SoftBank NAO 机器人 |
| 任务 | 双足行走 |
| 动作空间 | 12 关节角度 (6 每腿) |
| 状态空间 | 关节角/角速度 + IMU |
| 仿真器 | 高保真 NAO 仿真器 (代理真实世界) |
| RL 算法 | CMA-ES (进化策略) |
| GSL 迭代次数 | 3 轮 |
| 动作搜索采样数 | ~100 per transition |
| GAT 模型 | 2 层 MLP (256 hidden) |

- **结果**: 步行速度提升 **43.27%**（vs 最先进手工策略）
- 验证使用高保真仿真器作为真实世界代理

### 工程关键细节 (Engineering Tricks)

| 技巧 | 作用 |
|------|------|
| 采样搜索代替解析求逆 | 避免需要可微仿真器，但计算量大 |
| 残差建模 $f_\theta(s,a)$ | 比直接学习映射更稳定，初始值接近恒等 |
| GSL 迭代循环 | 每轮用新策略采集真机数据，渐进改进 |
| CMA-ES 进化策略 | 适用于低维参数空间的无梯度优化 |

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

### 局限性（理论/算法/工程三维度）

| 维度 | 局限 | 根因 | 替代方案 |
|-----|------|------|--------|
| **理论** | 动作变换仍假设相同状态在两域可达 | 若仿真器状态空间与真实不对齐，动作映射无意义 | 状态+动作联合变换（后续 GARAT） |
| **理论** | 映射假设为全局函数 | 真实动力学差异可能是状态依赖的 | 局部自适应策略 ([[ControlTheory]]) |
| **算法** | 动作搜索计算量 $O(N \times K)$ | 每个真实转移需采样 K 次 | 可微仿真器解析求逆 ([[Optimization]]) |
| **算法** | 仅验证于低维动作 (12-DoF) | 高维搜索效率急剧下降 | 分层/分关节变换 |
| **工程** | 需要真机数据收集 (非 zero-shot) | GSL 每轮都需真机交互 | 减少每轮所需数据量，或用在线学习 |

### 跨方法对比

| 方法 | 年份 | 修正层面 | 真机数据 | Zero-shot | 高维适用 |
|------|------|----------|---------|-----------|----------|
| GAT | 2017 | 动作空间 | 需要 | 否 | 未验证 |
| Domain Randomization | 2017 | 训练分布 | 不需要 | **是** | 是 |
| [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction\|TRANSIC]] | 2024 | 可组合模块 | 在线 | 否 | 是 |
| [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model\|DexNDM]] | 2024 | 神经动力学 | 少量 | 否 | **是 (16-DoF)** |
| [[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation\|RialTo]] | 2024 | 数字孜生 + RL | 少量 | 否 | 中 |

## 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **Grounding 作为 Sim-to-Real 校正**: GAT 系列的「用真机数据修正仿真动作」思想可应用于转笔——在仿真中训练基策略，用真机数据学习动作变换函数
2. **低数据量要求**: GAT 仅需真机上的少量数据学习映射，适合灵巧手转笔的缺乏真机训练场景
3. **局限**: 高维动作空间（24-DoF）下的 Grounding 质量未验证，可能需要将动作变换分解到关节级别
