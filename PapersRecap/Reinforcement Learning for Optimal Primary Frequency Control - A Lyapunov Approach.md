---
tags:
  - paper
  - reinforcement-learning
  - lyapunov-stability
  - frequency-control
  - neural-network-structure
  - power-systems
aliases:
  - Lyapunov RL
  - Stable Frequency Control
read-date: 2026-02-01
venue: IEEE Trans. Power Systems (arXiv 2009.05654)
paper-year: 2021
authors:
  - Wenqi Cui
  - Yan Jiang
  - Baosen Zhang
institution: University of Washington
paper-pdf: "[[Papers/Reinforcement Learning for Optimal Primary Frequency Control: A Lyapunov Approach.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[Optimization]]"
---

# Reinforcement Learning for Optimal Primary Frequency Control: A Lyapunov Approach

> [!note] Foundation 关联
> - **[[ReinforcementLearning]]**: RL 训练框架
> - **[[ControlTheory]]**: Lyapunov 稳定性嵌入网络结构
> - **[[Optimization]]**: 单调性约束的凸优化

> [!abstract] 核心贡献
> 将 **Lyapunov 稳定性**直接嵌入神经网络控制器的**结构设计**中。证明若控制器是**单调递增函数**（过原点），则系统具有唯一平衡点且局部指数稳定。用 Stacked-ReLU 网络实现单调性，并设计 RNN 框架高效训练。

## 1. 问题背景

### 1.1 电力系统频率控制挑战

**传统方案**：线性 droop 控制 $u_i = k_i \omega_i$
- 来自同步发电机的机械特性
- **非最优**：对于频率偏差和控制成本

**逆变器优势**：
- 可实现**任意控制律**
- 不限于线性 droop

### 1.2 RL 应用的核心挑战

> [!warning] 稳定性必须是**硬约束**
> 
> 现有方法：软惩罚（状态越界加高 cost）
> - 不能保证稳定性
> - 训练样本有限 vs 需要全状态空间稳定

---

## 2. 核心理论

### 2.1 摇摆方程（Swing Equation）

$$M_i \dot{\omega}_i = p_{m,i} - D_i \omega_i - u_i(\omega_i) - \sum_{j=1}^n B_{ij} \sin(\theta_i - \theta_j)$$

其中：
- $\omega_i$：频率偏差
- $u_i(\omega_i)$：局部反馈控制器
- $B_{ij}$：电纳矩阵

### 2.2 Lyapunov 稳定性条件

> [!theorem] 稳定控制器的结构性质
> 若 $u_i(\omega_i)$ 满足：
> 1. **单调递增**
> 2. **过原点**：$u_i(0) = 0$
> 
> 则系统存在**唯一平衡点**，且是**局部指数稳定**的。

**证明思路**：构造 Lyapunov 函数

$$V = \frac{1}{2} \sum_i M_i \omega_i^2 + \sum_{(i,j) \in E} B_{ij}(1 - \cos(\delta_i - \delta_j))$$

沿系统轨迹的导数：

$$\dot{V} = -\sum_i \omega_i (D_i \omega_i + u_i(\omega_i))$$

若 $u_i$ 单调且过原点 → $\omega_i u_i(\omega_i) \geq 0$ → $\dot{V} \leq 0$

---

## 3. 神经网络结构设计

### 3.1 单调性实现：Stacked-ReLU

普通 ReLU 网络不保证单调性。**Stacked-ReLU** 结构：

$$u_i(\omega_i) = \sum_{k=1}^K \alpha_k \cdot \text{ReLU}(\omega_i - \beta_k)$$

其中：
- $\alpha_k > 0$（正权重）
- $\beta_k$ 是可学习的偏置

> [!tip] 为什么单调？
> - 每个 $\text{ReLU}(\omega - \beta)$ 是单调非递减的
> - 正系数 $\alpha_k$ 的加权和仍单调
> - $\beta_k$ 的选择确保过原点

### 3.2 结构约束的实现

```
┌─────────────────────────────────────────┐
│  ω_i  →  Stacked-ReLU  →  u_i(ω_i)      │
│                                          │
│  权重约束: α_k > 0                        │
│  初始化: 确保 u_i(0) = 0                  │
│                                          │
│  结果: 单调 + 过原点 → Lyapunov 稳定    │
└─────────────────────────────────────────┘
```

### 3.3 RNN 训练框架

**问题**：状态在长时间跨度上耦合 → 直接反向传播低效

**解决方案**：将摇摆方程视为 RNN 的 cell：

$$\begin{bmatrix} \theta^{t+1} \\ \omega^{t+1} \end{bmatrix} = f_{cell}\left(\begin{bmatrix} \theta^t \\ \omega^t \end{bmatrix}, u^t\right)$$

![[lyapunov_rnn_framework.png]]

---

## 4. 优化问题

$$\min_u \sum_{i=1}^n \left( \|\omega_i\|_\infty + \gamma \|u_i\|_2^2 \right)$$

约束：
- 动力学方程 (摇摆方程)
- 控制饱和 $\underline{u}_i \leq u_i(\omega_i) \leq \overline{u}_i$
- **稳定性**（通过结构自动满足）

---

## 5. 实验结果

### 5.1 与基线对比

| 方法 | 频率偏差 | 控制成本 | 稳定性保证 |
|------|----------|----------|-----------|
| 线性 Droop | 基准 | 基准 | ✅ |
| 标准 RL (软惩罚) | ↓30% | ↓20% | ❌ 可能不稳定 |
| **本文 (Lyapunov 结构)** | ↓35% | ↓25% | ✅ **保证稳定** |

### 5.2 关键发现

1. **非线性优于线性**：学习的非线性控制器在性能上显著优于最优线性 droop
2. **稳定性至关重要**：无稳定性约束的 RL 可能学到不稳定控制器
3. **分散式有效**：每个控制器只用本地频率信息

---

## 6. 与知识体系的联系

### 与 [[ControlTheory]] 的联系

- **Lyapunov 稳定性理论**的直接应用
- **能量函数**作为 Lyapunov 函数（物理直觉）
- **无源性 (Passivity)**：$\omega_i u_i(\omega_i) \geq 0$ 是无源性条件

### 与 [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] 的联系

| 方面 | 本文 | Stability-Certified RL |
|------|------|------------------------|
| 稳定性方法 | 结构约束 | ROA 估计 |
| 应用场景 | 电力系统 | 一般非线性系统 |
| 网络结构 | Stacked-ReLU | 一般 NN |
| 理论基础 | 能量 Lyapunov | 价值函数 ≈ Lyapunov |

**共同主题**：将 Lyapunov 稳定性融入 RL 框架

### 与 [[ReinforcementLearning]] 的联系

- **策略结构设计**：不只是训练，还要设计网络结构
- **物理先验**：利用动力学性质约束策略空间
- **RNN 用于动力学**：将时间耦合建模为循环结构

---

## 7. 核心洞见

> [!quote] Insight 1: 结构 > 惩罚
> 将稳定性约束嵌入网络**结构**比用软惩罚更可靠

> [!quote] Insight 2: 单调性 = 稳定性
> 对于 swing 方程，控制器单调性直接导出 Lyapunov 稳定性

> [!quote] Insight 3: 分散式 + 非线性 + 稳定
> 三者可以同时实现，只需正确的网络结构

---

## 8. 扩展思考

### 对灵巧操作的启发

**类比**：
- 电力系统频率 ↔ 机器人关节速度
- 摇摆方程 ↔ 关节动力学
- 频率稳定 ↔ 速度/力稳定

**潜在应用**：
- 设计单调性约束的阻抗控制器
- 用能量函数作为 Lyapunov 函数保证接触稳定

---

## References

- [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] — ROA 估计方法
- [[Safe Model-based Reinforcement Learning with Stability Guarantees]] — 模型基安全 RL
- [[ControlTheory]] — Lyapunov 稳定性基础
- [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] — 网络结构约束
