---
tags:
  - PaperRecap
  - paper
  - SignalProcessing
  - PWM
  - LowRelevance
  - sampling-theory
aliases:
  - PWM Sampling Theorem
  - Constant Amplitude Variable Width Pulses
paper-year: 2011
date: 2026-02-01
read-date: 2026-03-16
venue: IEEE TCAS-I
paper-pdf: "[[Papers/The Sampling Theorem With Constant Amplitude Variable Width Pulses.pdf]]"
related:
  - "[[SignalProcessing]]"
  - "[[ControlTheory]]"
---

# The Sampling Theorem With Constant Amplitude Variable Width Pulses

> [!tip] 与理论基础的关联
> - [[SignalProcessing]] — Nyquist-Shannon 采样定理；PWM (等幅变宽) vs PAM (等宽变幅) vs Sigma-Delta 编码
> - [[ControlTheory]] — 离散控制 ZOH 假设本质是 PAM；PWM 是另一种 DAC 范式；电机驱动占空比上限
>
> **核心技术**: PWM Sampling Theorem, 0.637 (2/π) 峰值约束, 变宽脉冲编码
> **定位**: LowRelevance 信号处理参考——经 [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks|EvoControl]] 引用接入 control frequency 簇，作采样/编码理论根（不强套灵巧操作四支柱）。

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

### 核心符号溯源

| 符号 | 定义/来源 | 意义 | 陷阱 |
|------|----------|------|------|
| $x(t)$ | 带限信号 | 待编码基带信号 | **峰值须 ≤0.637** |
| $B$ | 带宽 | 信号带宽 | Nyquist $T_s=1/2B$ |
| $\delta_n=\frac{1}{2B}(1+x(nT_s))$ | 脉冲宽度 | 由信号值决定 | **等幅变宽**（PWM 本质） |
| $0.637=2/\pi$ | 峰值约束 | sinc 峰值交叉条件 | **充分非必要**；源自 Gibbs |
| 脉冲数 | = Nyquist 采样数 | 信息容量 | 不增不减 |

### 核心洞察（直观隐喻）
如同莫尔斯电码用"长短脉冲"编码字母 — PWM 用"宽窄脉冲"编码连续信号。关键约束是信号幅值不能太大（≤ 0.637），否则脉冲之间会"挤到重叠"，信息编码就崩溃了。这一约束与机器人 PWM 电机驱动中的占空比上限直接对应。

> [!tip] Delta 分析
> 经典 Nyquist 采样定理使用等间隔、等宽度的脉冲（PAM），本文证明了**等幅值、变宽度**（PWM）的采样同样可以完美重建信号 — 这是对采样理论的重要推广。

### PWM 采样定理

**定理**：任何带宽限制在 $B$ 内且峰值 $\leq 0.637$ 的基带信号，都可以用单位幅度的 PWM 波形精确表示。

$$x(t) \xleftrightarrow{\text{PWM}} \sum_n p_n(t) \quad \text{where } p_n \text{ has variable width}$$

### 关键约束
- 脉冲数 = Nyquist 采样数
- 峰值约束 0.637 是充分条件（非必要）
- 低通滤波可精确恢复原信号

### 数学推导核心

标准 Nyquist-Shannon 采样定理（PAM）：
$$x(t) = \sum_{n=-\infty}^{\infty} x(nT_s) \cdot \text{sinc}\left(\frac{t - nT_s}{T_s}\right), \quad T_s = \frac{1}{2B}$$

PWM 扩展：每个脉冲 $p_n(t)$ 的宽度 $\delta_n$ 由信号值决定：
$$\delta_n = \frac{1}{2B}(1 + x(nT_s)), \quad |x(nT_s)| \le 0.637$$

恢复方程（低通滤波）：
$$\hat{x}(t) = \text{LPF}\left\{\sum_n \text{rect}\left(\frac{t - nT_s}{\delta_n}\right)\right\} = x(t)$$

幅值约束 0.637 的来源：$\frac{2}{\pi} \approx 0.637$，源自傅里叶分析中 sinc 函数的峰值交叉条件 — 与 [[SignalProcessing]] 中 Gibbs 现象相关。

---

### 概念边界与符号陷阱

- **PWM = 等幅变宽**（vs PAM 等宽变幅、Sigma-Delta 过采样噪声整形、PDM 等宽等幅变密）。
- **0.637 = 2/π 充分非必要**：源自 sinc 峰值交叉 / Gibbs 现象。
- **仅带限信号 + 峰值约束**：冲击/阶跃信号不适用。
- **电机占空比 [18%, 82%] 对称裕度**；死区时间限制可表示的动态范围。
- **PWM 谐波需滤波 → 增加延迟**。

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

## 工程关键细节 (Engineering Tricks for Robotics)

- **PWM 频率选择**: 机器人电机驱动 PWM 频率通常 10-50 kHz → 远超控制带宽（~1 kHz），满足 Nyquist 条件
- **0.637 约束的实际意义**: 电机占空比 ∈ [18%, 82%]（对称裕度），超出则谐波失真引起电流纹波 → 影响力矩精度
- **死区补偿**: 实际 H 桥驱动有死区时间 → PWM 脉冲宽度需最小值保证 → 限制了可表示信号的动态范围

## 局限与替代方案

| 维度 | PWM (本文) | PAM (经典 Nyquist) | Sigma-Delta | PDM |
|------|-----------|-------------------|-------------|-----|
| **编码方式** | 等幅变宽 | 等宽变幅 | 过采样+噪声整形 | 等宽等幅变密 |
| **幅值约束** | ≤0.637 | 无 | 无 | 无 |
| **硬件友好** | ✅ (数字开关) | ❌ (需 DAC) | ✅ | ✅ |
| **应用场景** | 电机驱动 | 通信 | 音频 | 功率放大 |

**理论局限**: 仅适用于带限信号 + 峰值约束 → 对冲击/阶跃信号不适用；实际中 PWM 谐波需滤波增加延迟。

> [!note] 采样/编码理论 → 机器人控制与传感的映射（接 control frequency 簇 + Touch Dexterity）
> 本文的 PWM/PAM/Sigma-Delta/PDM 编码谱，正好映射到知识库机器人方法的不同量化策略：
>
> | 编码 | 信号处理 | 机器人对应 |
> |------|---------|----------|
> | PAM/ZOH | 等宽变幅 | [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning\|PFQI]] 的 "persistence = ZOH 离散化" |
> | **Sigma-Delta** | 过采样 + 1-bit 噪声整形 | **[[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch\|Touch Dexterity]] 的 "1-bit 二值触觉 + 空间/时间过采样"** |
> | PWM | 等幅变宽 | 电机驱动、高频力控（[[EvoControl - Evolved High Frequency Control for Continuous Control Tasks\|EvoControl]]）|
> | Nyquist $f_s\ge2f_{max}$ | 采样下限 | control frequency 簇普遍（[[Elastic Time Step Reinforcement Learning, VTS-RL\|VTS-RL]]/[[TARC - Time-Adaptive Robotic Control\|TARC]] 的自适应 Nyquist）|
>
> **insight**：机器人"如何用有限比特/脉冲表示连续控制量/传感量"本质是采样编码问题。Touch Dexterity 的二值触觉 = Sigma-Delta 在触觉传感的实例（1-bit + 多路复用换鲁棒），PFQI 的 persistence = ZOH。**这篇纯信号理论是 control frequency 簇与 Touch Dexterity 的共同数学根**——虽 LowRelevance，却提供了"量化/采样"视角的理论统一。

## 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **高频控制与 PWM**: 灵巧手关节电机由 PWM 信号驱动 → 理解采样极限有助于确定控制频率上界
2. **力矩精度与 PWM 分辨率**: 转笔任务需要精细力矩控制（~0.01 Nm 量级）→ PWM 分辨率（占空比步进）直接决定力矩分辨率
3. **与 [[ControlTheory]] 的联系**: 离散控制器的 ZOH（零阶保持）假设本质上是 PAM → PWM 提供了另一种 DAC 范式
4. **与 [[SignalProcessing]] 的数学联系**: 连续控制信号 $u(t)$ 的离散化 $u[n]$ 需满足 $f_s \ge 2B_u$，PWM 定理将此推广到功率级执行器域

## 建议

> [!tip] 保留建议
> 虽然本文与核心研究领域关联较弱，但作为**PWM 理论参考**保留。
> 当需要理解高频控制中的采样理论时可参考。

---

## 关联笔记

- [[SignalProcessing]] - 采样理论
- [[ControlTheory]] - 离散控制与 ZOH 假设
- [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks]] - 引用了 PWM 采样定理类比
