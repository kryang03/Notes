---
tags:
  - paper-recap
  - reinforcement-learning
  - control-frequency
  - action-persistence
  - batch-RL
  - FQI
aliases:
  - PFQI
  - Persistent FQI
  - Action Persistence
created: 2026-01-31
venue: ICML 2020
year: 2020
authors:
  - Alberto Maria Metelli
  - Flavio Mazzolini
  - Lorenzo Bisi
  - Luca Sabbioni
  - Marcello Restelli
institution: Politecnico di Milano
---

# Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning

> [!abstract] 核心贡献
> 提出 **Action Persistence**（动作持续）的形式化框架：在 $k$ 个决策步内重复同一动作，等价于修改控制频率。证明了持续算子的收缩性质，导出最优性能损失界，并提出 **PFQI** (Persistent Fitted Q-Iteration) 算法。

## 1. 问题背景

### 1.1 控制频率的权衡

**高频控制**：
- ✅ 策略空间更大，理论上能达到更优性能
- ❌ 单个动作效果微弱，难以从噪声中区分
- ❌ 样本复杂度高

**低频控制**：
- ✅ 动作效果明显，易于学习
- ✅ 样本复杂度低
- ❌ 策略空间受限
- ✅ 有助于克服部分可观测性（如执行延迟）

> [!question] 核心问题
> **什么是最优控制频率？**
> 答案取决于：(1) 任务特性；(2) 学习算法

---

## 2. 数学框架

### 2.1 Action Persistence 定义

**执行策略 $\pi$ at persistence $k$**：
- 在 $t = 0$ 选择 $A_0 \sim \pi(\cdot|S_0)$
- 保持 $A_0$ 固定 $k-1$ 步：$A_1 = \cdots = A_{k-1} = A_0$
- 在 $t = k$ 重新查询策略：$A_k \sim \pi(\cdot|S_k)$
- 循环...

### 2.2 两种等价视角

#### Policy View（策略视角）

**$k$-persistent policy**：非马尔可夫非平稳策略

$$\pi_{t,k}(B|H_t) = \begin{cases} \pi(B|S_t) & \text{if } t \mod k = 0 \\ \delta_{A_{t-1}}(B) & \text{otherwise} \end{cases}$$

#### Environment View（环境视角）

**$k$-persistent MDP** $M_k = (S, A, P_k, R_k, \gamma^k)$

- **转移核**：$P_k(B|s,a) = (P^\delta)^{k-1} P(B|s,a)$
- **奖励**：$R_k = \sum_{i=0}^{k-1} \gamma^i (P^\delta)^i R$
- **折扣因子**：$\gamma^k$（有效视野缩短）

> [!important] 对偶性
> 在 $M$ 中以 persistence $k$ 执行 $\pi$ ⟺ 在 $M_k$ 中以 persistence 1 执行 $\pi$

### 2.3 Persistent Bellman Operators

**$k$-persistent Bellman 期望算子**：
$$T_k^\pi f = T^\pi (T^\delta)^{k-1} f$$

**$k$-persistent Bellman 最优算子**：
$$T_k^* f = T^* (T^\delta)^{k-1} f$$

其中 $T^\delta$ 是动作不变的转移算子。

> [!theorem] 收缩性
> $T_k^\pi$ 和 $T_k^*$ 在 $L_\infty$ 范数下是 $\gamma^k$-收缩的，因此存在唯一不动点。

---

## 3. 性能损失分析

### 3.1 Lipschitz 条件下的界

设 MDP 是 $(L_P, L_r)$-Lipschitz 连续的：

$$\|Q_1^* - Q_k^*\|_\infty \leq C \cdot k \cdot \Delta t_0$$

其中 $C$ 取决于：
- 动力学的 Lipschitz 常数 $L_P$
- 奖励的 Lipschitz 常数 $L_r$
- 折扣因子 $\gamma$

> [!tip] 物理直觉
> 性能损失与**环境演化速度**成正比。对于"缓慢演化"的系统，增加 persistence 的代价更小。

---

## 4. Persistent Fitted Q-Iteration (PFQI)

### 4.1 算法思想

给定基础 MDP $M$ 中收集的数据集 $D = \{(s_i, a_i, r_i, s'_i)\}$：

1. 选择目标 persistence $k$
2. 使用 $k$-persistent Bellman 算子进行值迭代
3. 无需重新采集数据！

**关键观察**：可以用 persistence 1 的数据估计 persistence $k$ 的值函数

### 4.2 算法框架

```
输入: 数据集 D（persistence 1 采集），目标 persistence k
初始化: Q^(0) = 0
for j = 0, 1, 2, ... do
    Q^(j+1) = FQI_step(Q^(j), D, k)  // 使用 k-persistent Bellman 目标
return π_k = greedy(Q^*)
```

### 4.3 Persistence 选择启发式

**目标**：从候选集 $\mathcal{K} = \{1, 2, 4, 8, ...\}$ 中选择最优 $k^*$

**方法**：
1. 对每个 $k \in \mathcal{K}$ 运行 PFQI(k)
2. 使用价值函数估计比较性能
3. 无需额外环境交互

---

## 5. 实验结果

### 5.1 Cartpole

| Persistence $k$ | Expected Return |
|-----------------|-----------------|
| 1 | 172.0 ± 6.8 |
| 2 | 178.4 ± 6.7 |
| **4** | **276.2 ± 3.8** |
| 8 | 284.3 ± 1.6 |
| 16 | 285.9 ± 1.1 |

**最优 persistence**：$k = 4 \sim 16$

### 5.2 关键发现

1. **过低的 persistence**（$k=1,2$）：动作效果不明显，学习困难
2. **过高的 persistence**（$k>32$）：策略空间过度受限
3. **最优点存在**：任务相关的"甜蜜点"

---

## 6. 与相关概念的联系

### 6.1 与 Frame Skipping 的关系

深度 RL 中的 frame skipping（如 Atari 每 4 帧决策一次）本质上就是 action persistence

### 6.2 与 [[Elastic Time Step Reinforcement Learning, VTS-RL]] 的联系

- **VTS-RL**：动态调整时间步长
- **Action Persistence**：统一的理论框架
- 两者都关注**控制频率适配**问题

### 6.3 与 [[ReinforcementLearning]] 的联系

- **折扣因子调整**：persistence $k$ 等价于 $\gamma \to \gamma^k$
- **有效视野缩短**：$\frac{1}{1-\gamma^k} < \frac{1}{1-\gamma}$
- **样本效率**：低频 → 高样本效率，但受限策略空间

---

## 7. 核心洞见

> [!quote] Insight 1: 动作持续是可配置的环境参数
> $k$ 可以视为 Configurable MDP 的超参数，外部调节以优化学习

> [!quote] Insight 2: 性能-样本复杂度权衡
> 存在最优 persistence，平衡策略空间大小和学习难度

> [!quote] Insight 3: 可重用数据
> 用 persistence 1 收集的数据可用于估计任意 persistence $k$ 的值函数

---

## 8. 局限与扩展

1. **仅限 Batch RL**：需要扩展到 Online RL
2. **固定 persistence**：可考虑状态依赖的 $k(s)$
3. **探索影响**：persistence 改变采样分布的熵

---

## References

- [[Elastic Time Step Reinforcement Learning, VTS-RL]] — 动态时间步长
- [[Reinforcement Learning for Control with Multiple Frequencies]] — 多频率控制
- [[ReinforcementLearning]] — 基础知识
