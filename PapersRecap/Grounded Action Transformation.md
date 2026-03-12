---
tags:
  - paper
  - sim-to-real
  - grounded-simulation
  - transfer-learning
aliases:
  - GAT
  - Grounded Action Transformation
paper-year: 2017
read-date: 2026-03-13
venue: AAAI 2017
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
---

# Grounded Action Transformation

> [!abstract] 核心贡献
> 提出 **Grounded Action Transformation (GAT)**，一种在 Grounded Simulation Learning (GSL) 框架下的新算法：通过学习仿真与真实世界之间的**动作映射函数** $f_\alpha: a_{sim} \to a_{real}$，修正仿真器中动作效果的偏差，使仿真优化的策略直接迁移到物理系统。在 NAO 双足行走任务上提升行走速度 43.27%。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — GSL 框架，策略优化，sim-to-real 经典方法
> - [[Dynamics]] — 仿真器动力学校准，动作效果差异建模
>
> **历史地位**: Sim-to-real 领域奠基性工作之一，开创了"修正仿真器（而非修正策略）"的范式

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
与其让策略适应不完美的仿真，不如修正仿真器使其匹配真实世界——GAT 通过学习动作映射来 ground 仿真器。

### 领域定位
- **Sim-to-real 经典三范式**:
  1. Domain Randomization — 增大仿真多样性以覆盖真实
  2. System Identification — 调参使仿真逼近真实
  3. **Grounded Simulation** — 用真实数据修正仿真器 ← GAT 属于此类
- **核心假设**: 仿真与真实的主要差异在于**动作效果**（关节指令到实际运动的映射不同）

### 关键创新
1. **动作变换函数** — 学习 $f_\alpha(s,a_{sim}) \to a_{grounded}$, 使 grounded simulator 中执行变换后的动作产生与真实世界相同的状态转移
2. **迭代 grounding** — 策略更新后重新收集真实数据再次 ground，处理分布偏移
3. **全自动化** — 去除前作 GUIDED GSL 中需要人工选择可变参数的限制

## 2. 方法细节

### GSL 框架
$$\phi^* = \arg\min_\phi \sum_{\tau \in \mathcal{D}} d\left(Pr(\tau|\theta), Pr_{sim}(\tau|\theta, \phi)\right)$$
其中 $d$ 为轨迹分布的相似度度量。

### GAT 核心
将仿真器 ground 问题分解为逐步状态转移匹配：
$$\phi^* = \arg\min_\phi \sum_{i=1}^{L} d\left(P(s_{t+1}^i | s_t^i, a_t^i),\; P_\phi(s_{t+1}^i | s_t^i, a_t^i)\right)$$

动作变换通过前向模型逆推：
1. 学习仿真器前向模型 $\hat{s}_{t+1} = g(s_t, a_t)$
2. 求解 $a^* = \arg\min_a \|g(s_t, a) - s_{t+1}^{real}\|^2$
3. 在仿真训练时用 $a^*$ 替代原始动作

## 3. 演进脉络定位 (Evolution Context)

```
Farchy et al. (2013): GUIDED GSL (需人工指导)
    ↓
本论文: GAT (全自动动作变换, AAAI 2017)
    ↓
GARAT (2021): + 随机化增强 grounding 鲁棒性
    ↓
[[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction|TRANSIC]] (2024): 在线修正 + residual RL
    ↓
现代 sim-to-real: Domain Randomization 主导, 但 GAT 思想融入 system identification
```

## 4. 对灵巧操作的启发 (Implications)

> [!note] DNPM 项目相关性
> - GAT 的"动作效果差异"问题在灵巧操作中更为严重——高减速比伺服的实际关节角响应与指令存在显著延迟和非线性
> - [[Minimalist Compliance Control]] 中的"方向相关效率模型"本质上处理类似问题——补偿理论动作与实际效果的差异
> - 现代 sim-to-real 方法（如 [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots|DemoStart]]）通常用 Domain Randomization 替代 system identification，但 GAT 的思想在 residual policy 中重现
