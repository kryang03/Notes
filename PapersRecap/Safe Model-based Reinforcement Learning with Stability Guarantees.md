---
tags:
  - paper-recap
  - safe-RL
  - lyapunov-stability
  - gaussian-process
  - model-based-RL
  - region-of-attraction
aliases:
  - Safe Model-based RL
  - Lyapunov RL
  - SafeOpt-RL
created: 2026-01-31
venue: NeurIPS 2017
year: 2017
authors:
  - Felix Berkenkamp
  - Matteo Turchetta
  - Angela P. Schoellig
  - Andreas Krause
institution: ETH Zurich, University of Toronto
---

# Safe Model-based Reinforcement Learning with Stability Guarantees

> [!abstract] 核心贡献
> 首次提出具有**可证明稳定性保证**的安全 RL 算法。利用 **Lyapunov 函数** 定义安全区域，结合 **Gaussian Process** 建模动力学不确定性，实现在不离开吸引域的前提下安全学习和策略优化。

## 1. 问题设定

### 1.1 安全的定义

**核心观点**：RL 中的安全 = 控制理论中的**稳定性**

**吸引域 (Region of Attraction, RoA)**：
- 状态空间的一个子集 $\mathcal{V}(c)$
- 前向不变：$x_0 \in \mathcal{V}(c) \Rightarrow x_t \in \mathcal{V}(c), \forall t > 0$
- 渐近收敛：$\lim_{t \to \infty} x_t = 0$

**安全约束**：
1. 适应策略时不得**缩小**吸引域
2. 探索动作不得**离开**吸引域

### 1.2 系统模型

$$x_{t+1} = f(x_t, u_t) = \underbrace{h(x_t, u_t)}_{\text{已知先验模型}} + \underbrace{g(x_t, u_t)}_{\text{未知模型误差}}$$

**假设**：
- **Lipschitz 连续性**：$h$, $g$ 和策略 $\pi$ 都是 Lipschitz 连续的
- **统计模型**：使用 GP 建模 $g$，提供校准的不确定性估计

---

## 2. 理论框架

### 2.1 Lyapunov 稳定性验证

**Lyapunov 函数** $v: \mathcal{X} \to \mathbb{R}_{\geq 0}$：
- $v(0) = 0$, $v(x) > 0$ for $x \neq 0$
- 连续可微

> [!theorem] Theorem 1 (Lyapunov 稳定性)
> 若对所有 $x \in \mathcal{V}(c)$ 有 $v(f(x, \pi(x))) < v(x)$，则 $\mathcal{V}(c)$ 是吸引域。

**关键洞见**：将复杂的收敛性验证转化为**单步下降条件**

### 2.2 基于统计模型的安全验证

**不确定性量化**：
$$Q_n(x,u) := [v(\mu_{n-1}(x,u)) \pm L_v \beta_n \sigma_{n-1}(x,u)]$$

其中：
- $\mu_n$, $\sigma_n$：GP 后验均值和标准差
- $\beta_n$：置信区间缩放因子
- $L_v$：Lyapunov 函数的 Lipschitz 常数

> [!theorem] Theorem 2 (离散化验证)
> 在 Lipschitz 假设下，只需在离散网格 $\mathcal{X}_\tau$ 上验证下降条件：
> $$u_n(x, u) < v(x) - L_{\Delta v} \tau$$
> 即可保证连续状态空间的稳定性。

### 2.3 策略优化

**安全策略空间**：
$$\mathcal{D}_n = \{(x, u) \in \mathcal{X}_\tau \times \mathcal{U} \mid u_n(x, u) - v(x) < -L_{\Delta v} \tau\}$$

**优化目标**：
$$\pi_n, c_n = \argmax_{\pi \in \Pi_L, c > 0} c \quad \text{s.t.} \quad \forall x \in \mathcal{V}(c) \cap \mathcal{X}_\tau: (x, \pi(x)) \in \mathcal{D}_n$$

**含义**：寻找使吸引域最大的策略，同时保证安全约束

### 2.4 安全探索

**安全探索集**：
$$\mathcal{S}_n = \{z' \in \mathcal{V}(c_n) \cap \mathcal{X}_\tau \times \mathcal{U}_\tau \mid u_n(z) + L_v L_f \|z - z'\|_1 \leq c_n\}$$

**探索策略**（最大化信息增益）：
$$(x_n, u_n) = \argmax_{(x,u) \in \mathcal{S}_n} u_n(x, u) - l_n(x, u)$$

选择**不确定性最大**的安全状态-动作对

---

## 3. 理论保证

> [!theorem] Theorem 4 (安全与探索保证)
> 在 GP 模型假设下，对任意 $\delta \in (0,1)$，以至少 $(1-\delta)$ 的概率：
> 
> (i) $\mathcal{V}(c_n) \subseteq \mathcal{R}_{\pi_n}$ — 估计的吸引域包含于真实吸引域
> 
> (ii) $f(x,u) \in \mathcal{R}_{\pi_n}, \forall (x,u) \in \mathcal{S}_n$ — 所有探索点都在吸引域内
> 
> (iii) 经过有限次探索后，达到最优探索性能

**核心含义**：可以**安全地学习**系统动力学，同时**扩大吸引域**

---

## 4. 实践算法

### 4.1 Algorithm 1: Safe Lyapunov Learning

```
输入: 初始安全策略 π₀, GP 动力学模型
for n = 1, 2, ... do
    1. 通过 SGD 优化策略 πₙ
    2. 计算最大安全等值线 cₙ
    3. 更新安全探索集 Sₙ
    4. 选择 (xₙ, uₙ) ∈ Sₙ 并收集数据
    5. 用新数据更新 GP 模型
```

### 4.2 实现细节

**策略表示**：神经网络（2 隐藏层，32 神经元，ReLU）

**Lyapunov 函数来源**：
- 物理能量（机械系统的动能+势能）
- **价值函数**！对于正定代价 $r(x,u)$，$V^\pi$ 天然是 Lyapunov 函数

**置信区间简化**：$\beta_n = 2$（实践中比理论值更激进）

---

## 5. 实验结果

### 5.1 倒立摆稳定

| 阶段 | 吸引域大小 | 控制性能 |
|------|-----------|---------|
| 初始策略 | 小（仅局部稳定） | 差 |
| 50 数据点后 | 显著扩大 | 大幅改善 |

**关键结果**：摆从未倒下——整个学习过程都是安全的

---

## 6. 核心洞见

> [!tip] Insight 1: Lyapunov 函数 = 安全证书
> Lyapunov 函数将"长期稳定性"转化为"单步可验证条件"，使安全约束可计算

> [!tip] Insight 2: GP 提供"诚实"的不确定性
> 校准的置信区间允许保守但有效的安全验证

> [!tip] Insight 3: 价值函数天然是 Lyapunov 函数
> 对于正定代价，RL 的价值函数可直接用作稳定性分析工具

> [!tip] Insight 4: 安全与探索可以兼得
> 在吸引域内探索不会破坏安全性，同时可以扩大吸引域

---

## 7. 与知识体系的联系

### 与 [[ControlTheory]] 的联系

- **Lyapunov 稳定性理论** 是本文的核心工具
- **吸引域 (RoA)** 概念来自非线性控制
- 将控制理论的安全保证引入 RL

### 与 [[ReinforcementLearning]] 的联系

- **Model-Based RL** + GP 动力学模型
- **Safe Exploration** 的形式化定义
- 价值函数与 Lyapunov 函数的对偶关系

### 与 [[Optimization]] 的联系

- **约束优化** 形式的策略更新
- Lipschitz 连续性假设的利用
- 信息论驱动的探索策略

---

## 8. 局限与后续

**局限**：
1. 需要 Lyapunov 函数（不总是容易获得）
2. 离散化带来计算开销
3. GP 在高维状态空间扩展性有限
4. 假设完全可观测状态

**后续工作**：
- [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] — 更一般的框架
- [[Reachability Constrained Reinforcement Learning]] — 可达性约束
- [[How to Train Your Latent Control Barrier Function - Smooth Safety Filtering Under Hard-to-Model Constraints]] — 隐空间安全过滤

---

## References

- [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] — Lipschitz 网络设计
- [[ControlTheory]] — Lyapunov 稳定性理论基础
