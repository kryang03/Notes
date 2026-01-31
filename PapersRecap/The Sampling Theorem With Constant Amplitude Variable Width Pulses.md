---
tags:
  - PaperRecap
  - SignalProcessing
  - PWM
  - LowRelevance
date: 2026-02-01
related:
  - "[[SignalProcessing]]"
---

# The Sampling Theorem With Constant Amplitude Variable Width Pulses

> [!note] Foundation 关联
> - **[[SignalProcessing]]**: 采样定理与 PWM 信号处理

## 元信息
- **作者**: Jing Huang, Krishnan Padmanabhan, Oliver M. Collins
- **机构**: University of Notre Dame
- **年份**: 2011 (IEEE TCAS-I)
- **领域**: 信号处理、电路系统

> [!warning] 领域相关性
> 本文是**纯信号处理理论**论文，与灵巧操作/强化学习**无直接关系**。
> 它可能因为与 [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks|EvoControl]] 论文的引用关系而被收集。

---

## 核心内容

### PWM 采样定理

**定理**：任何带宽限制在 $B$ 内且峰值 $\leq 0.637$ 的基带信号，都可以用单位幅度的 PWM 波形精确表示。

$$x(t) \xleftrightarrow{\text{PWM}} \sum_n p_n(t) \quad \text{where } p_n \text{ has variable width}$$

### 关键约束
- 脉冲数 = Nyquist 采样数
- 峰值约束 0.637 是充分条件（非必要）
- 低通滤波可精确恢复原信号

---

## 与机器人控制的间接联系

### EvoControl 中的引用

[[EvoControl - Evolved High Frequency Control for Continuous Control Tasks]] 论文的 **Proposition 2.1** 指出：
> "某些 MDP 需要动作频率趋近无穷才能达到最优"

作者将此类比为 PWM 采样定理——可变脉宽能从离散样本重建连续信号。

### 潜在应用方向
1. **高频力控制**：力矩输出可以用 PWM 方式实现
2. **电机驱动**：机器人执行器通常使用 PWM 驱动
3. **信号重建**：从离散控制信号重建连续轨迹

---

## 建议

> [!tip] 保留建议
> 虽然本文与核心研究领域关联较弱，但作为**PWM 理论参考**保留。
> 当需要理解高频控制中的采样理论时可参考。

---

## 关联笔记

- [[SignalProcessing]] - 采样理论
- [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks]] - 引用了 PWM 采样定理类比
