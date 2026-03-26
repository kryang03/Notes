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

### 核心洞察（直观隐喻）

**用“建筑结构”而非“安全绳”保证安全**——传统 RL 用惩罚项（安全绳）约束策略，但绳可断；本文将稳定性嵌入网络拓扑（承重结构），使策略在数学上不可能输出不稳定控制。如同拱桥的稳定性来自其几何形状，而非外部支撑。

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

### 3.4 核心代码逻辑 (PyTorch)

```python
import torch
import torch.nn as nn

class StackedReLUController(nn.Module):
    """单调递增 + 过原点的 Lyapunov 稳定控制器"""
    def __init__(self, K=20):
        super().__init__()
        self.raw_alpha = nn.Parameter(torch.randn(K))  # softplus 保证正
        self.beta = nn.Parameter(torch.linspace(-2, 2, K))  # 可学习偏置

    def forward(self, omega: torch.Tensor) -> torch.Tensor:
        alpha = torch.nn.functional.softplus(self.raw_alpha)  # α_k > 0
        basis = torch.relu(omega - self.beta)  # [batch, K]
        u = (alpha * basis).sum(dim=-1, keepdim=True)
        # 减去 u(0) 确保过原点
        u_zero = (alpha * torch.relu(-self.beta)).sum()
        return u - u_zero

class SwingEquationRNN(nn.Module):
    """将摇摆方程展开为 RNN cell 进行端到端训练"""
    def __init__(self, n_buses, dt=0.01):
        super().__init__()
        self.controllers = nn.ModuleList(
            [StackedReLUController() for _ in range(n_buses)]
        )
        self.dt = dt

    def rnn_step(self, theta, omega, M, D, B, p_m):
        u = torch.stack(
            [c(omega[:, i:i+1]) for i, c in enumerate(self.controllers)], dim=1
        ).squeeze(-1)
        coupling = (B * torch.sin(
            theta.unsqueeze(-1) - theta.unsqueeze(-2)
        )).sum(dim=-1)
        omega_dot = (p_m - D * omega - u - coupling) / M
        return theta + self.dt * omega, omega + self.dt * omega_dot
```

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

### 5.3 训练细节

| 维度 | 设定 |
|------|------|
| **训练框架** | RNN 展开 T=100 步 |
| **优化器** | Adam, lr=1e-3 |
| **网络规模** | K=20 个 ReLU 基函数/控制器 |
| **测试系统** | IEEE 39-bus 新英格兰系统 |
| **扰动场景** | 负荷阶跃变化 10–30% |
| **训练收敛** | ~500 episodes |
| **部署推理** | 单控制器 < 0.1ms |

### 5.4 Ablation 分析

| 消融项 | 效果 | 因果机制 |
|--------|------|----------|
| 去掉单调性约束 | 部分场景不稳定 | 违反 Lyapunov 条件 → $\dot{V}$ 可能为正 |
| 线性 Droop 替代 | 性能 ↓25% | 线性无法捕捉最优非线性控制律的曲率 |
| 减少 K (K<10) | 性能下降 | 分段线性逼近精度不足 → 欠拟合 |
| 去掉 RNN 展开 | 训练效率 ↓ | 无法利用动力学时间耦合计算梯度 |

### 5.5 工程实践要点 (Engineering Tricks)

1. **Softplus 代替 clip 保正性**: `softplus(raw_alpha)` 而非 `clamp(alpha, min=0)` ——后者梯度在边界处为零导致参数卡死
2. **偏置初始化**: $\beta_k$ 均匀分布在频率偏差典型范围内，确保 ReLU 基函数覆盖工作区间
3. **过原点校正**: 训练后显式减去 $u(0)$，保证部署时精确满足 $u(0)=0$
4. **RNN 展开长度**: T<50 无法捕捉低频振荡模态；T>200 梯度消失。T=100 为经验最优

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

## 8. 局限性深度分析

### 理论层面
- **局部稳定性**: Lyapunov 分析仅保证局部指数稳定，大扰动可能超出吸引域
- **单调性的保守性**: 充分条件但未讨论其与必要条件的差距——可能排除了部分安全但更优的非单调控制器
- **替代方案**: [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective|Stability-Certified RL]] 使用 ROA 估计处理更一般的 Lyapunov 函数

### 算法层面
- **表达能力**: Stacked-ReLU 是分段线性的，无法精确表示光滑最优控制律（如 $u^* \propto \omega^3$）
- **纯分散式**: 无法利用邻居信息，分布式 consensus-based 方案可能更优
- **替代方案**: Input-Convex Neural Networks (ICNN) 可保证单调性同时具有更强非线性表达力

### 工程层面
- 未报告与无约束 RL 的训练效率对比
- 逆变器控制频率 kHz 级，ReLU 网络推理可行，但更复杂约束网络可能受限

## 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **结构约束借鉴**: 将安全/稳定性嵌入网络结构而非奖励函数——转笔中可将关节限位、力矩约束编码为网络输出层结构（如 tanh 饱和 + 缩放）
2. **单调性 → 无源性**: 类比灵巧手中“施力方向与位移方向一致”的无源性条件 ([[ControlTheory]])，可构造满足接触稳定性的策略结构
3. **Stacked-ReLU 启发**: 分段线性基函数在低维控制中高效，转笔中的 per-joint 控制器可借鉴此架构

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
