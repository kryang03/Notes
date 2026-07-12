---
tags:
  - PaperRecap
  - paper
  - SignalProcessing
  - PWM
  - sampling-theory
  - actuator-encoding
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

> [!abstract] 核心贡献
> 本文证明了一个 PWM 版本的采样定理：任意带宽为 $B$ 且峰值满足 $|x(t)|\le 2/\pi\approx0.637$ 的基带带限信号，都可以用频率 $2B$、单位幅值、变脉宽的 PWM 波形无失真表示；低通滤波可精确恢复原信号，且脉冲数等于 Nyquist samples 数。

> [!tip] 与理论基础的关联
> - [[SignalProcessing#1.1 采样与混叠：离散化不是无损记录|SignalProcessing §1.1]] — 经典 Nyquist-Shannon 用”等间隔、变幅值”样本表示带限信号；本文改成”等幅值、变宽度”脉冲，并用 sinc side-lobes / ISI 分析其可逆性。恢复端的”理想低通”正是 [[SignalProcessing#1.4 数字滤波器：去噪、延迟与可控性的三角权衡|SignalProcessing §1.4]] 讨论的滤波器。
> - [[ControlTheory#1.3 频率响应：Bode、相位裕度与带宽|ControlTheory §1.3]] — PWM 是功率 DAC / 电机驱动常用表示；它和 ZOH/PAM 都是在讨论连续控制信号如何被离散硬件承载，而”能承载到多高频”由电流环/机械惯性的**带宽与相位裕度**决定。
> - [[Actuation#5.2 电流环带宽、交叉耦合与量化延迟|Actuation §5.2]] — **电流≠关节力矩暗线的信号层根**：本文的 PWM 波形正是 [[Actuation#11.3 差分抗噪与位时序带宽|Actuation §11.3]] 里 MCU 输出、经内部驱动器隐藏的那一层；策略输出的”动作”要穿过 PWM→电流环→减速器才变成关节力矩。
> - [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks|EvoControl]] — 该文引用 PWM 采样定理类比”高频控制可用脉冲宽度承载连续动作信息”。
>
> **核心技术**: PWM Sampling Theorem, Worst-ISI Bound, Sequential Local Error Minimization, Matrix-Based Iterative Pulsewidth Solver

## 0. 阅读定位与范本价值

这是一篇纯信号处理/电路系统理论论文，不是机器人学习论文。它在你的知识库里不应被强行拔高成“灵巧操作方法”，但它提供了一个非常有用的底层抽象：**连续信号不一定只能用样本幅值表示，也可以用固定幅值脉冲的时间宽度表示。**

这对 control frequency / actuator dynamics 簇的意义是：机器人策略输出的“动作”最终一定要被硬件编码。PPO/DP/WMTS 关心的是上层决策频率，PFQI 关心的是 action repeat/ZOH，而本文关心更低一层：功率电子/开关放大器如何用开关时间宽度重建连续模拟信号。

最低标准映射：

| 四支柱 | 本文 recap 的落点 | 必须抓住的判断 |
|---|---|---|
| 逻辑与价值 | §1, §4 | 它不是说“普通 PWM 低通就天然无失真”，而是证明存在一类可求解的 PWM 脉宽，使低通恢复精确 |
| 原理与理论 | §2 | 从 Nyquist/PAM 到 PWM 波形定义，再到 sinc convolution、ISI、$2/\pi$ 峰值界和迭代求解 |
| 实验与验证 | §3 | 论文用理论命题 + 数值例子验证：峰值界是 universal sufficient/tight but not necessary |
| 未来与结合 | §5-§7 | 对灵巧手只应作为执行器编码/频率抽象参考，不应直接把 policy action 设计成 PWM |

## 1. 问题设定与动机

### 1.1 一句话核心

经典采样定理用“样本高度”编码带限信号；本文证明在峰值受限时，也可以用“单位幅值脉冲宽度”编码同样的信息。

### 1.2 直观隐喻

Nyquist/PAM 像用不同高度的柱子表示信号：每个采样点的数值直接变成脉冲高度。PWM 像用同样高度的柱子，但改变柱子的宽窄：柱子越宽，低通滤波后的面积贡献越大。问题是，宽柱子的 sinc side lobes 会影响邻居，所以脉宽不能只按本点样本独立决定，必须把所有脉冲之间的 intersymbol interference 一起解掉。

这个隐喻的关键是“面积”只是第一层直觉；真正的数学难点是 sinc 旁瓣导致非局部耦合。

### 1.3 现有方法的局限

| 方法 | 注入了什么先验 | 关键局限 |
|---|---|---|
| Nyquist/PAM | 带限信号由等间隔样本幅值决定 | 需要可精确产生模拟幅值；功率放大场景中线性幅值 DAC 效率低 |
| Conventional PWM | 固定幅值、调节占空比，硬件高效 | PWM conversion 非线性；传统 uniform/natural PWM 低通后通常有 distortion |
| Optimal PWM / harmonic elimination | 优化周期信号谐波 | 多针对周期信号，不给一般带限基带信号的精确表示定理 |
| Click modulation / time encoding | 用 binary/transition time 表示带限信号 | 条件复杂、频率可能不固定；本文选择规则脉冲中心，给出简单峰值约束 |
| Sigma-Delta / PDM | 过采样 + 噪声整形/密度编码 | 通过高采样率转移量化噪声；本文强调 Nyquist 数量级脉冲数即可 |

### 1.4 Delta 分析

本文的 Delta 是把 PWM 从“高效但有失真”的工程调制方式，提升为一个采样定理：

1. **表示层 Delta**：不是变幅 impulse，而是单位幅值、中心固定、宽度可变 pulse。
2. **理论层 Delta**：用 worst-ISI 上界证明 universal sufficient peak constraint $2/\pi$。
3. **构造层 Delta**：给出 sequential local error minimization 和 matrix-based iterative solver，证明/实现从样本到脉宽的逆映射。
4. **边界层 Delta**：$2/\pi$ 是 universal sufficient condition，对这个充分条件是 tight，但不是 individual signal 的必要条件。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 符号/对象 | 空间/类型 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $x(t)$ | bandlimited baseband signal | 输入信号 | 否 | 要被 PWM 表示并低通恢复的连续信号 | 需满足 bandwidth $B$；峰值界是对 $x(t)$ 而非 PWM pulse |
| $B$ | bandwidth | 信号假设 | 否 | 基带带宽 | PWM switching frequency 取 $2B$，不是任意高频 |
| $T$ | sampling/PWM period | 采样设计 | 否 | $1/T=2B$ | 同时是采样周期和 PWM period |
| $u(t)$ | Heaviside step | 数学定义 | 否 | 构造矩形脉冲的边沿 | 与控制输入 $u$ 不同，别混成 control action |
| $w_n$ | normalized pulse width | 待求解变量 | 否 | 第 $n$ 个 pulse 的归一化宽度，实际宽度 $w_nT$ | three-level: $[-1,1]$；two-level: $[0,1]$ |
| $pwm(t)$ | switching waveform | 由 $\{w_n\}$ 构造 | 否 | 单位幅值、变宽度脉冲序列 | 普通 PWM 初值不等于最终无失真 PWM |
| $s(t)$ | transformed signal | 由 $x(t)$ 变换 | 否 | 统一 two-level/three-level 记号 | two-level 用 $(x+1)/2$，three-level 直接用 $x$ |
| $f_n(w)$ | sinc convolution contribution | 低通滤波推导 | 否 | 宽度为 $w$ 的 pulse 对第 $n$ 个采样点的贡献 | $f_0$ 是主瓣；$n\ne0$ 是旁瓣 |
| $ISI_t$ | scalar interference | 由其他 pulse side lobes 叠加 | 否 | 其他脉冲对第 $t$ 个样本的干扰 | 本文核心困难：PWM 逆映射非局部 |
| $ISI^m$ | worst-ISI upper bound | Proposition 3.1 | 否 | 任意单个 pulse 可遭遇的最大旁瓣干扰 | 数值 $0.236$；不是信号峰值 |
| $2/\pi$ | amplitude bound | worst square wave / sinc 分析 | 否 | universal peak constraint | 充分条件；对 universal bound tight，但非必要 |
| $E=\sum_n |e_n|$ | total absolute error | 迭代算法 | 否 | filtered PWM samples 与目标 samples 的误差 | convergence proof 用 $E$ 单调下降 |
| $A$ | Toeplitz matrix | matrix solver | 否 | 线性化后的全局脉宽更新近似 | 预计算 $A^{-1}$；不是神经网络矩阵 |

### 2.2 从 Nyquist/PAM 到 PWM

经典 Nyquist-Shannon 定理说：若 $x(t)$ 带宽不超过 $B$，以 $T=1/(2B)$ 采样，则可由样本 $x(nT)$ 精确重建：

$$
x(t)
=
\sum_{n=-\infty}^{\infty}
x(nT)\,\mathrm{sinc}\left(\frac{t-nT}{T}\right).
$$

这里的表示是 PAM-like：位置固定，幅值变。

本文换成 PWM-like：幅值固定为 1，中心固定在 $nT$，宽度 $w_nT$ 可变。三电平 PWM 波形写成：

$$
pwm(t)=
\sum_{n=-\infty}^{\infty}
\left[
u\left(t-nT+\frac{w_nT}{2}\right)
-
u\left(t-nT-\frac{w_nT}{2}\right)
\right].
$$

其中：

- $w_n\in[-1,1]$ 时，负宽度可理解为负脉冲，对应 three-level $\{-1,0,+1\}$；
- $w_n\in[0,1]$ 时先得到 $\{0,1\}$ PWM，再通过 $2pwm(t)-1$ 得到 two-level $\{-1,+1\}$。

为了统一 two-level/three-level，论文定义

$$
s(t)=
\begin{cases}
\dfrac{x(t)+1}{2}, & \text{two-level},\\
x(t), & \text{three-level}.
\end{cases}
$$

符号陷阱：two-level 不是直接把 $x(t)$ 当作 pulse width；它先平移/缩放到正区间，再由 $2pwm-1$ 回到 $\pm1$ 电平。

### 2.3 为什么 PWM 逆映射不等于“宽度 = 样本值”

脉冲通过理想低通滤波器后，其输出是与 sinc 的卷积。定义 $f_n(w)$ 为一个单位幅值、宽度 $w$ 的 pulse 对距离 $n$ 个采样周期处的贡献：

$$
f_n(w)=
\int_{n-w/2}^{n+w/2}
\frac{\sin \pi t}{\pi t}\,dt,\qquad n=0,1,2,\dots
$$

$f_0$ 是主瓣贡献，$f_n,n\ne0$ 是旁瓣贡献。第 $t$ 个输出样本不是只由第 $t$ 个 pulse 决定，而是

$$
\hat s_t=f_0(w_t)+ISI_t,
$$

其中

$$
ISI_t=
\sum_{\substack{n=-\infty\\n\ne t}}^{\infty}
f_{t-n}(w_n).
$$

这一步是理解本文的关键：PWM 的非线性和失真不来自“低通滤波不够好”这么粗糙的说法，而来自所有 pulse 的 sinc side lobes 互相干扰。要无失真，必须求一个全局一致的 $\{w_n\}$，使每个 $\hat s_t$ 都等于目标样本 $s_t$。

### 2.4 Worst ISI 与 $2/\pi$ 峰值约束

Proposition 3.1 证明：对任意单个 pulse，所有其他 pulse 能造成的 ISI 幅值有 universal upper bound：

$$
ISI^m=
2\sum_{n=1}^{\infty}
\left(
\int_{n-1/2}^{n}
\left|\frac{\sin \pi t}{\pi t}\right|dt
-
\int_{n}^{n+1/2}
\left|\frac{\sin \pi t}{\pi t}\right|dt
\right),
$$

且数值为：

$$
ISI^m=0.236.
$$

这个 worst case 由 periodic ideal square waveform 达到。方波的 Fourier series：

$$
sq(t)=
\frac{4}{\pi}
\sum_{k=1}^{\infty}
\frac{\sin((2k-1)\pi t)}{2k-1}.
$$

低通只保留基波，得到

$$
\frac{2}{\pi}\sin(\pi t).
$$

因此：

$$
f_0(1)-ISI^m=\frac{2}{\pi}=0.637.
$$

旧稿把 0.637 粗略说成 “Gibbs/sinc 交叉”是不够准确的。更精确地说：它来自 worst-ISI analysis；方波产生最大旁瓣干扰，而方波低通后的基波幅值是 $2/\pi$。

### 2.5 三电平与二电平 PWM 采样定理

Theorem 3.7（三电平）：

若 $x(t)$ 带宽为 $B$ 且

$$
|x(t)|\le \frac{2}{\pi}=0.637,
$$

则 $x(t)$ 可以由频率 $2B$、电平为 $0,\pm1$ 的 three-level PWM waveform 表示；理想低通滤波可精确恢复 $x(t)$。

Theorem 3.8（二电平）：

同样条件下，$x(t)$ 也可以由频率 $2B$、电平为 $\pm1$ 的 two-level PWM waveform 表示；理想低通滤波可精确恢复 $x(t)$。

两个定理有三个容易忽略的含义：

1. **脉冲数不增加**：PWM pulse 数 = Nyquist sample 数，不靠过采样逃避问题。
2. **two-level/three-level 峰值界相同**：$2/\pi$ 与电平类型无关。
3. **这是存在性 + 构造性定理**：论文不仅说存在，还给了迭代求脉宽的方法。

### 2.6 Sequential local error minimization

给定 $N$ 个 Nyquist samples $\mathbf{s}$，目标是找到 $N$ 个 widths $\mathbf{w}$。论文先用 conventional PWM 初始化：

$$
\mathbf{w}^{(1)}=\frac{1}{P}\mathbf{s},
$$

其中 $P$ 可取 samples 的最大绝对幅值。

然后用数字域闭环迭代：

1. 由当前 $\mathbf{w}$ 生成 PWM；
2. 低通并在 pulse center 采样，得到 $\hat{\mathbf{s}}$；
3. 计算误差

$$
\mathbf e=\mathbf s-\hat{\mathbf s};
$$

4. 逐个 pulse 调整 $w_t$，使对应 $\hat s_t=s_t$；
5. 重复直到总误差

$$
E=\sum_{n=1}^{N}|e_n|
$$

收敛到 0。

Proposition 3.6 的关键是：每一次非零宽度调整都会让 $E$ 严格下降。Theorem 3.10 更进一步说：只要 exact PWM representation 存在，sequential local error minimization 总会收敛到正确答案；若收敛后还有误差，则误差只可能卡在 saturated pulses 上，而这与 exact representation 存在矛盾。

### 2.7 Matrix-based iterative solver

Sequential 方法适合证明，但实际计算慢。论文进一步给出矩阵迭代：

$$
\hat s_t^{(i)}
=
f_0(w_t^{(i)})
+
\sum_{\substack{n=1\\n\ne t}}^{N}
f_{t-n}(w_n^{(i)}),
$$

$$
\mathbf e^{(i)}=\mathbf s-\hat{\mathbf s}^{(i)},
$$

$$
\mathbf w^{(i+1)}
=
\mathbf w^{(i)}
+
\mathbf e^{(i)}A^{-1}.
$$

$A$ 是一个 symmetric Toeplitz matrix，来自对 $f_n(\cdot)$ 的线性化。选择常数矩阵的原因很工程：$A^{-1}$ 可预先计算并复用，不必每次迭代重新求逆。

论文还把峰值约束推广为最大允许脉宽 $\tilde w$ 的函数：

$$
P(\tilde w)=f_0(\tilde w)-ISI^m(\tilde w).
$$

这说明若你不允许 pulse 用满宽度，而是限制 $|w|\le\tilde w<1$，可表示信号峰值会下降，但矩阵迭代的收敛速度会显著提高。它是一个很典型的“动态范围 vs 数值收敛/硬件裕度”交换。

## 3. 实验、数值验证与证据链

### 3.1 理论结果的关键数值

| 结论 | 数值/条件 | 证明或验证来源 | 支持的故事 |
|---|---:|---|---|
| PWM switching frequency | $2B$ | Theorem 3.7/3.8 | 与 Nyquist sample rate 同阶，不需要额外 pulse 数 |
| universal peak constraint | $2/\pi=0.637$ | worst-ISI + square-wave low-pass | 峰值界来自最坏旁瓣干扰，而不是经验调参 |
| worst ISI | $ISI^m=0.236$ | Proposition 3.1 | 所有 pulse 对单点的最大旁瓣干扰可被统一上界 |
| three-level voltage | $0,\pm1$ | Theorem 3.7 | 允许正负 pulse 和 zero state |
| two-level voltage | $\pm1$ | Theorem 3.8 | 通过 $s=(x+1)/2$ 与 $2pwm-1$ 转换 |
| lower-than-PWM sinusoid | frequency ratio $<0.33$ 时 two-/three-level 约束重合 | Fig. 10 | $2/\pi$ 不是 individual signal 必要条件 |

因果解释：这些数字证明的不是“PWM 方便”，而是“PWM 可以在 Nyquist 数量级 pulse 下成为无失真表示”。其中 $2/\pi$ 与 $ISI^m$ 把非线性 PWM 的旁瓣干扰压进一个可验证的充分条件。

### 3.2 为什么 $2/\pi$ 是 tight but not necessary

论文对 $2/\pi$ 的定位很细：

- **tight for the sufficient condition**：若允许任意带限信号，超过 $2/\pi$ 后可以构造不可精确表示的信号；例如 fundamental frequency 为 PWM switching frequency 一半的 sinusoid，若振幅超过 $2/\pi$，two-level/three-level PWM 都不能精确表示。
- **not necessary for individual signals**：很多具体信号峰值超过 $2/\pi$ 仍可精确表示；例如 DC signal 和更低频 sinusoid。

这非常像控制里的 robust bound：universal guarantee 往往保守，但保守不是错误，而是为了覆盖最坏情况。

### 3.3 随机信号与 clipping probability

Section V.A 分析 bandlimited white Gaussian signals。工程系统通常 peak-limited，因此随机信号要 clipping。论文比较 Nyquist samples 与 PWM representation 在相同 clipping probability 下可承载的信号功率。

关键机制：

- Nyquist sample clipping 只看样本幅值是否超过幅值约束；
- PWM clipping 还取决于每个样本与其他样本通过 ISI 形成的有效余量；
- 因为 $ISI_t$ 与样本本身相关，论文用窗口近似给出 clipping probability 的上界。

这组结果的意义不是给机器人直接用的数值表，而是证明 $2/\pi$ 只是 universal bound；在具体随机分布下，实际可表示空间可以比最坏情况更宽。

### 3.4 低于 PWM 频率的 sinusoid

Section V.B 研究

$$
x(t)=A\sin(2\pi f t)
$$

且 $f$ 低于 PWM frequency 的 sinusoid。Fig. 10 显示：

- 当 $f/f_{\mathrm{PWM}}<0.33$ 左右时，two-level 与 three-level 的可表示振幅约束基本重合；
- 当 $0.33<f/f_{\mathrm{PWM}}<1$ 时，three-level PWM 可支持更高振幅；
- half-PWM-frequency sinusoid 是最坏情况之一，对应 $2/\pi$ tightness。

这组数值验证了论文的边界叙事：频率越接近 PWM switching frequency，side-lobe / interference 约束越紧；低频信号更容易由 PWM 精确表示。

### 3.5 Ablation 式因果链

| 改变/条件 | 观察 | 因果机制 | 含义 |
|---|---|---|---|
| PAM → PWM | 仍可无失真表示，但需要求解脉宽 | PWM 的固定幅值牺牲线性幅值自由度，换来时间宽度自由度 | 表示能力不只来自 amplitude，也来自 timing |
| 忽略 ISI，直接按样本设宽度 | 低通后有 distortion | sinc side lobes 让每个 pulse 影响多个 sample | 无失真 PWM 必须做全局/迭代求解 |
| 信号峰值满足 $2/\pi$ | sequential solver 保证收敛 | worst-ISI 下仍能为每个样本找到合法 width | universal guarantee 成立 |
| 限制 $|w|\le\tilde w<1$ | 峰值可表示范围下降，收敛变快 | 留出饱和裕度，线性化更稳定 | 硬件中不要长期贴近 0/100% duty |
| 频率低于 PWM switching | 可表示振幅可超过 $2/\pi$ | 信号结构远离 worst square-wave case | 不要把 sufficient bound 误当实际极限 |

## 4. 核心洞见

### 4.1 真正的 insight：采样自由度可以从幅值转移到时间

Nyquist 定理的常见读法是“带限信号 = 一串幅值样本”。本文提醒：采样定理的本质不是“幅值必须可变”，而是“有足够自由度确定带限函数”。如果幅值固定，时间宽度也可以承载自由度。

对应关系：

| 维度 | PAM / Nyquist | PWM theorem |
|---|---|---|
| 自由度 | sample amplitude $x(nT)$ | pulse width $w_n$ |
| 硬件形态 | linear DAC / variable amplitude | switching amplifier / fixed amplitude |
| 数学困难 | sinc interpolation 线性 | sinc side-lobe coupling 非线性 |
| 重建 | ideal LPF | ideal LPF |
| 约束 | bandlimited | bandlimited + peak constrained |

### 4.2 为什么这个设计有效

它有效是因为带限信号的自由度密度有限：每 $T=1/(2B)$ 秒一个自由度足够。PWM 没有减少自由度数量，只是把每个自由度从“高度”换成“宽度”。困难在于这个换元不是线性的，旁瓣干扰使每个 $w_n$ 影响多个 sample。论文通过 worst-ISI bound 证明在峰值足够小的区域，这个非线性逆问题有解且可收敛求解。

### 4.3 什么时候会失效

| 失效条件 | 原因 |
|---|---|
| 信号非带限 | Nyquist 根基失效，LPF 不可能恢复全部高频 |
| 峰值超过 universal bound 且接近 worst-case 结构 | pulse width 饱和，无法抵消 ISI |
| 硬件 pulse timing 分辨率不足 | 定理假设可精确设置 width；时钟 jitter 会转成幅值噪声 |
| LPF 非理想 | 理想低通是定理前提，实际滤波器相位/幅值误差会带来 distortion |
| 机器人接触控制直接套用 | 接触力不是单纯 bandlimited baseband signal；闭环动力学会放大 delay/jitter |

## 5. 替代方案与理论局限

### 5.1 理论维度

本文是信号表示定理，不是闭环控制稳定性定理。它没有讨论：

- PWM 经过真实电机、电感、电流环后的 torque dynamics；
- dead-time、switching loss、MOSFET 非理想；
- quantized clock 下 width resolution；
- 闭环控制里 delay 对稳定裕度的影响。

所以它只能作为 actuator encoding / sampling representation 的理论根，不能替代 [[ControlTheory]] 里的离散控制、稳定性和执行器建模。

### 5.2 算法维度

| 方法 | 表示方式 | 优点 | 局限 |
|---|---|---|---|
| PAM / DAC | 等宽变幅 | 数学线性，Nyquist 插值直接 | 需要线性幅值硬件，功率效率低 |
| PWM | 等幅变宽 | 开关放大高效，适合电机/音频功放 | 非线性，需要补偿/求解脉宽 |
| Sigma-Delta | 过采样 + 噪声整形 | 1-bit 硬件友好，噪声推高频 | 依赖高过采样率与滤波 |
| PDM | 等幅等宽变密 | 简单数字脉冲密度表示 | 对高频和滤波要求高 |
| Time encoding | 不规则 transition times | 表示能力强 | switching frequency 可能不稳定 |

### 5.3 工程维度

- 定理里的 ideal LPF 在电机系统里对应电感、电流环、机械惯性等综合低通，不是一个完美数学滤波器。
- 单位幅值 pulse 在功率电子里意味着开关器件只在饱和/关断状态工作，效率高；但真实器件有 dead time 和 rise/fall time。
- 若 duty 长期接近 0 或 1，硬件裕度、热、纹波、饱和都会恶化；这对应 §2.7 的 $\tilde w<1$ 收敛/裕度思想。
- 对智能舵机/LinkerHand 这类封装执行器，上层通常不能直接控制 PWM；能控制的是 position/current/velocity command，PWM 已被内部驱动器隐藏。

## 6. 对用户研究的启发

### 6.1 对 LinkerHand / WMTS 的谨慎迁移

这篇论文对你的项目最有价值的不是“把策略输出 PWM”，而是提供一个底层问题意识：**动作表示最终要被硬件编码，编码方式会改变可实现带宽、延迟、噪声与饱和。**

| 层级 | 论文概念 | 对 LinkerHand / WMTS 的对应 |
|---|---|---|
| 信号层 | bandlimited $x(t)$ | 期望电流/力矩/位置目标的时间序列 |
| 编码层 | PWM width $w_n$ | 内部驱动器 duty cycle，通常不可直接访问 |
| 控制层 | LPF reconstruction | 电机电感、电流环、机械惯性形成的低通 |
| 策略层 | sample rate $2B$ | PPO/DP/WMTS action update rate |
| 风险层 | width saturation / timing jitter | actuator saturation、通讯延迟、量化误差 |

如果要用于 WMTS，正确做法是把它变成 actuator-aware abstraction：

$$
\text{policy action}
\to
\text{low-level command}
\to
\text{hidden PWM/current loop}
\to
\text{joint torque/position response}.
$$

WMTS 的 world model 应建模最后这个 response，而不是假设 action 立即等于物理力矩。

### 6.2 与 PFQI / control frequency 簇的关系

PFQI 讨论的是 action repeat：

$$
a_t=a_{t+1}=\cdots=a_{t+k-1}.
$$

这更像 zero-order hold / PAM 的时间保持。本文讨论 PWM：

$$
\text{固定幅值}+\text{可变宽度}.
$$

二者共同点是都在问：连续控制信号如何被离散时间硬件承载？

| 问题 | PFQI | 本文 |
|---|---|---|
| 自由度 | 每 $k$ 个 base step 改一次 action | 每个 Nyquist period 改一次 pulse width |
| 主要 trade-off | 策略空间 vs 样本复杂度 | 幅值线性度 vs 开关效率/ISI |
| 失真来源 | 动作保持过久导致状态过期 | sinc side-lobes / pulse interaction |
| WMTS 启发 | 学状态依赖 $k(s)$ | 建 actuator encoding/带宽/饱和模型 |

### 6.3 与触觉/量化表征的联系

本文也能和 Touch Dexterity 类二值触觉形成抽象联系：两者都说明“低精度/二值硬件不必等于低信息量”，关键在于是否用时间/空间/频率上的冗余承载信息。

| 编码方式 | 信号处理含义 | 机器人对应 |
|---|---|---|
| PWM | 固定幅值，时间宽度承载幅值 | 电机驱动、功率放大 |
| Sigma-Delta | 1-bit + 过采样 + 噪声整形 | 二值触觉/事件触觉可通过时空密度恢复接触结构 |
| ZOH/PAM | 固定时间格点，幅值承载动作 | policy action repeat / low-level command hold |
| PDM | 脉冲密度承载幅值 | spike/event-based sensing 的类比 |

这给你的知识库一个 meta-insight：**硬件约束不是只会损失信息；它也会迫使信息换一个载体。** 对灵巧手，触觉二值化、action chunk、PWM duty、CAN quantization 都应放进同一个“信息载体转换”框架里分析。

### 6.4 可验证实验建议

不建议直接实现论文的 PWM solver 到机器人策略里。更务实的实验是：

| 实验 | 目的 | 观测指标 |
|---|---|---|
| actuator response identification | 测真实 command → joint response 是否近似带限/低通 | step response、frequency response、phase lag |
| command bandwidth sweep | 测 action update frequency 超过某阈值后是否只变成噪声/热 | tracking error、temperature、current ripple、success rate |
| saturation-aware policy regularization | 惩罚长期贴近 action limit / duty-like saturation | torque saturation count、slip/drop rate |
| world model 加 actuator latent | 让 WM 预测 hidden actuator lag / low-pass effect | one-step prediction error、real rollout error |

这才是本文对 WMTS 的可落地价值：把“执行器是低通/饱和/量化系统”变成 world model 或 policy regularization 的一部分。

### 6.5 不应过度外推的点

- 不要说 $0.637$ 就是电机 duty cycle 的通用安全范围；它是归一化带限信号峰值的 sufficient bound。
- 不要把 ideal LPF 等同于真实电机；真实 motor driver 有闭环电流控制、反电动势、死区和饱和。
- 不要把 PWM switching frequency 和 RL control frequency 混为一谈；前者可达 kHz-MHz，后者通常是 tens-hundreds Hz。
- 不要把“PWM 可无失真表示信号”理解成“普通 PWM 不用补偿就无失真”；论文的关键是求解特定 pulse widths。

## 7. 与知识体系的联系

### 7.1 与 [[SignalProcessing]] 的联系

本文是 Nyquist 采样定理的一个非线性表示变体：

$$
\text{bandlimited signal}
\xrightarrow{\text{PAM}}
\{x(nT)\}
\quad\text{vs}\quad
\text{bandlimited signal}
\xrightarrow{\text{PWM}}
\{w_n\}.
$$

它补充了采样理论中的一个重要方向：采样自由度可以在 amplitude、width、density、transition time 之间转移；不同硬件选择不同自由度。

### 7.2 与 [[ControlTheory]] 的联系

控制系统中的 actuator 不是理想连续输入端。数字控制链路常常是：

$$
\text{discrete controller}
\to
\text{DAC/PWM/current loop}
\to
\text{plant}.
$$

本文帮助理解中间的 PWM/current-loop 表示层，但闭环稳定性仍要回到 sampling period、delay、phase margin、actuator saturation 等控制理论问题。

### 7.3 与 control frequency 簇的联系

| 知识库节点 | 共同问题 | 区别 |
|---|---|---|
| [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning|PFQI]] | 离散时间如何承载连续控制 | PFQI 改决策频率；本文改硬件编码方式 |
| [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks|EvoControl]] | 高频控制可表达复杂连续动作 | EvoControl 用进化/高频策略；本文给 PWM 类比的采样理论 |
| [[Elastic Time Step Reinforcement Learning, VTS-RL|VTS-RL]] | 时间粒度可变 | VTS 学 $\Delta t(s)$；本文固定 $T=1/(2B)$ 求 $w_n$ |
| [[TARC - Time-Adaptive Robotic Control|TARC]] | 可变时间粒度的正确折扣 | TARC 学 $\Delta t(s)$ 并按物理时间 $e^{-c\Delta t}$ 折扣；本文固定周期、把自由度放进脉宽 $w_n$ 而非时间间隔 |
| [[Reinforcement Learning for Control with Multiple Frequencies|AP-AC]] | 多路信号各自的采样率 | AP-AC 让每个动作变量按 $c^k$ 采样（多速率）；本文是单信号内幅值↔宽度的自由度转移 |
| [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch|Touch Dexterity]] | 低比特硬件仍可承载结构信息 | Touch 用二值触觉/空间过采样；本文用 pulse width |

## 8. 应主动追问的颗粒度

| 用户式追问 | recap 应主动补充 |
|---|---|
| “PWM 为什么也能算采样定理？” | 解释 PAM 的样本幅值自由度如何换成 PWM 的脉宽自由度 |
| “0.637 哪里来的？” | 从 worst-ISI bound、periodic square wave、$2/\pi$ 基波幅值推导 |
| “普通 PWM 不是有失真吗？” | 区分 conventional PWM 与本文求解出的 distortion-free pulse widths |
| “two-level 和 three-level 有何不同？” | 写清 $s=(x+1)/2$、$2pwm-1$、$w_n$ 范围 |
| “和机器人有什么关系？” | 限定在 actuator encoding / bandwidth / saturation，不把它误当策略学习方法 |

## References

- Huang, J., Padmanabhan, K., & Collins, O. M. **The Sampling Theorem With Constant Amplitude Variable Width Pulses**. IEEE Transactions on Circuits and Systems I, 2011.
- [[SignalProcessing]]
- [[ControlTheory]]
- [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning]]
- [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks]]
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]]
