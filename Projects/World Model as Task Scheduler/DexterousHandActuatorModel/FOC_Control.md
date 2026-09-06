---
tags: [Dexterous_Manipulation, Motor_Control, Field_Oriented_Control, State_Estimation, Sim-to-Real]
source: Unified FOC & PMSM Modeling Lectures
date: 2026-04-15
updated: 2026-09-02
related:
  - "[[Actuation]]"
  - "[[Actuator2RigidDynamicsModel_gap]]"
  - "[[ControlTheory]]"
  - "[[Final_WMTS]]"
  - "[[电机]]"
  - "[[Transmission2JointDynamics_gap]]"
---

# 永磁同步电机(PMSM)与无感矢量控制(Sensorless FOC)第一性原理推导

> [!abstract] 本篇在链路中的位置
> 灵巧手链路是 `电能 → 电机电磁力矩 → FOC 电流环 → 减速器/丝杠/连杆 → 关节力矩 → 刚体+接触`。本篇管**第二段：驱动层**——三相绕组里的电压电流如何被 FOC 降维成"一个旋钮控力矩"的直流模型 $\tau = K_t I_q$，这个旋钮在无传感器、高温、高速下分别在哪里失灵，以及这些失灵怎样变成 Actuator Model 必须学的残差。**上一篇**是电机层 [[电机]]（各类电机的物理与 $K_t = K_e$ 直流模型），**下一篇**是指令层 [[Actuator2RigidDynamicsModel_gap]]（串级环、CAN、延迟、8-bit 量化），机械侧折算见 [[Transmission2JointDynamics_gap]] 与 [[LinkerSysId]]。Foundation 级的提炼版在 [[Actuation#2. 驱动层：FOC 磁场定向控制——把三相交流当直流控|Actuation §2]]–[[Actuation#6. 热漂移层：为什么跑久了力矩变小|§6]]，本篇是它的"不跳步展开版"。

> [!tip] 读完你应该能回答
> 1. 数据手册上的 $K_e$（V/krpm 或 V·s/rad）、$K_t$（N·m/A）与 FOC 力矩公式里的 $\frac32 p\psi_m$ 是怎么对上账的？为什么直流电机是 $K_t = K_e$、PMSM 却多出一个 $\frac32$？
> 2. 为什么 L25 这类灵巧手**不能**靠无感 FOC 省掉关节位置传感器？无感方案在什么转速以下失效、启动时靠什么？
> 3. 一个 20–50 Hz 的位置指令，要经过哪几层闭环才变成相电流？为什么内环带宽必须比外环高 5–10 倍？
> 4. 真机跑 20 s 后力矩为什么变小？$R_s$、$\psi_m$、$L$ 各漂多少、漂向哪里，哪一个会把无感角度估计带偏？
> 5. 仿真里 `τ = Kp(q_des − q) + Kd(...)` 这行公式与真机三级级联之间的错位，具体在哪五处？由此 WMTS 的 Actuator Model 应该学什么、不该学什么？

---

## 一、 核心思想与领域定位 (Executive Summary)

> **为什么现在讲这个**：上一篇 [[电机]] 把各类电机最终都收敛到 $\tau = K_t I$ 这一个直流模型；但灵巧手关节里的空心杯 BLDC / PMSM 有三相绕组，"$I$" 究竟是哪一个电流？本节先给出答案的形状——FOC 把三相降维成一个 $I_q$——后面各节再逐步把这句话推出来。

在底层硬件驱动体系中，磁场定向控制（Field Oriented Control, FOC）通过空间坐标变换，将严重非线性、强耦合的三相交流电机动力学降维解耦为线性独立的类直流控制模型。基于内部电气模型的 Luenberger Observer 则打破了对高成本物理编码器的依赖，实现了无感（Sensorless）的转子状态估计。

在灵巧操作（Dexterous Manipulation）与强化学习（RL）的交叉语境中，理解这一底层控制逻辑至关重要。高层 Policy 网络（如 PPO）输出的通常是理想的关节力矩（Desired Torque）或位置目标。然而，底层驱动的非线性、电气延时（PWM 滤波）、反电动势（Back-EMF）以及观测器在极低速下的崩溃边界，是产生 Sim-to-Real Gap 的核心根源。彻底打穿从基尔霍夫定律到力矩输出的物理链路，是构建高保真 Actuator 动力学模型的前提。

本篇的阅读顺序与链路一致：**§二** 把三相方程降维到 d-q 并推出 $\tau = K_t I_q$（含与直流电机 $K_t = K_e$ 的对账、$I_d = 0$ 何时才是最优、电流环之上的串级三环）；**§三** 讲没有编码器时怎样从电流里"看见"转子角度、以及它在低速时为什么必然失效；**§四** 讲温度让"常数"不再是常数；**§五** 讲高速 reorientation 下的电气极限；**§六** 把以上全部折算成 WMTS Actuator Model 的输入/输出设计。

---

## 二、 物理本源：定子方程与坐标系降维

> **为什么现在讲这个**：要把"三相交流"变成"直流旋钮"，只有两步坐标变换——Clarke（3→2，静止）和 Park（静止→随转子旋转）。这两步是后面一切（力矩公式、观测器、弱磁、温漂分析）的语言，所以必须在这里一次讲透，而且每一个系数（$\frac23$、$\frac32$、$\sqrt3$）都要有来历。

为了实现类似直流电机的解耦控制，必须剥离三相交流系统的时变与耦合特性。我们将从最基础的电磁学物理定律出发构建系统动态方程。

### 2.1 静止坐标系下的三相电气方程与 Clarke 变换

在定子三相静止坐标系 $(a, b, c)$ 下，根据基尔霍夫电压定律 (KVL)，施加在每相绕组上的电压 $V_x$（V）被消耗在三个部分：电阻压降 $R_s I_x$（发热）、电感抵抗电流变化的感应电压 $L\,\frac{dI_x}{dt}$、以及转子永磁体旋转切割定子绕组产生的反电动势 $e_x$（Back-EMF）：

$$V_x = R_s I_x + L\frac{dI_x}{dt} + e_x,\qquad x\in\{a,b,c\}$$

- $R_s$：定子每相电阻（Ω）；$L$：每相等效电感（H，表贴式/空心杯电机三相对称且不随转子位置变化）；$I_x$：相电流（A）；$e_x$：相反电动势（V）。

三相绕组 Y 接、无中性点引出时，三相电流之和恒为零：$I_a + I_b + I_c = 0$。这意味着三个电流只有**两个**自由度——第三个由前两个决定。**Clarke Transform** 正是把这个冗余的三维投影到正交的二维静止坐标系 $(\alpha, \beta)$（$\alpha$ 轴与 $a$ 相轴重合）：

$$\begin{bmatrix} I_\alpha \\ I_\beta \end{bmatrix} = \frac{2}{3} \begin{bmatrix} 1 & -\frac{1}{2} & -\frac{1}{2} \\ 0 & \frac{\sqrt{3}}{2} & -\frac{\sqrt{3}}{2} \end{bmatrix} \begin{bmatrix} I_a \\ I_b \\ I_c \end{bmatrix}$$

矩阵里的几何意义：三相轴线在空间上互差 $120°$，$b$ 相轴在 $\alpha\beta$ 平面的投影是 $(\cos120°, \sin120°) = (-\tfrac12, \tfrac{\sqrt3}{2})$，$c$ 相是 $(-\tfrac12, -\tfrac{\sqrt3}{2})$——矩阵的两行就是把三个相轴的贡献分别投到 $\alpha$、$\beta$ 轴上再相加。

> [!important] 前面的 $\frac23$ 是一个**约定**，不是物理定律：幅值不变 vs 功率不变
> 设三相平衡电流 $I_a = I_m\cos\omega t$、$I_b = I_m\cos(\omega t - \tfrac{2\pi}{3})$、$I_c = I_m\cos(\omega t + \tfrac{2\pi}{3})$（$I_m$ 为相电流**峰值**，A）。代入 $\alpha$ 行：
> $$I_\alpha = \tfrac23\Big[I_m\cos\omega t - \tfrac12 I_m\cos(\omega t - \tfrac{2\pi}{3}) - \tfrac12 I_m\cos(\omega t + \tfrac{2\pi}{3})\Big]$$
> 用和差化积 $\cos(\omega t - \tfrac{2\pi}{3}) + \cos(\omega t + \tfrac{2\pi}{3}) = 2\cos\omega t\cos\tfrac{2\pi}{3} = -\cos\omega t$，得
> $$I_\alpha = \tfrac23\Big[I_m\cos\omega t + \tfrac12 I_m\cos\omega t\Big] = I_m\cos\omega t .$$
> 所以取 $\frac23$ 时 **$I_\alpha$ 的幅值 = 相电流峰值**，称为**幅值不变 (amplitude-invariant)** 约定，好处是 $I_q$ 直接等于"相电流峰值"，工程上直观，电机驱动固件（SimpleFOC、TI InstaSPIN、ST MC-SDK 等）几乎都用它。**代价**是功率不再"不变"：三相瞬时功率 $P = V_aI_a + V_bI_b + V_cI_c$ 变换后等于 $\frac32(V_\alpha I_\alpha + V_\beta I_\beta)$——那个 $\frac32$ 会一路跟到力矩公式里（§2.4）。
> 另一种约定取系数 $\sqrt{\tfrac23}$，称为**功率不变 (power-invariant)**：此时 $P = V_\alpha I_\alpha + V_\beta I_\beta$ 无需系数，但 $I_\alpha$ 幅值变成 $\sqrt{\tfrac32}\,I_m$，力矩公式里的 $\frac32$ 也随之变成 $1$（磁链同样被缩放）。**读任何 FOC 文献/固件先确认它用哪个约定，否则 $K_t$ 会差 $\frac32$ 倍**——这是对账 §2.4 时最常见的坑。本篇全篇采用幅值不变约定（与 [[Actuation#2.1 坐标降维：Clarke 与 Park 变换|Actuation §2.1]] 一致）。

对三相 KVL 逐相施加同一个 Clarke 变换（变换是线性的，对 $V$、$I$、$\frac{dI}{dt}$、$e$ 同时作用），得到 $(\alpha, \beta)$ 坐标系下的电气动态方程：
$$\begin{bmatrix} V_\alpha \\ V_\beta \end{bmatrix} = R_s \begin{bmatrix} I_\alpha \\ I_\beta \end{bmatrix} + L \frac{d}{dt} \begin{bmatrix} I_\alpha \\ I_\beta \end{bmatrix} + \begin{bmatrix} e_\alpha \\ e_\beta \end{bmatrix}$$

形式上与单相 KVL 一模一样，只是变量从三个变成了两个正交分量。但注意：**电流仍然是交变的**——转子转一圈电周期，$I_\alpha, I_\beta$ 就是一对正弦/余弦。要变成"直流"，还差第二步。

### 2.2 电角度 $\theta_e = p\,\theta_m$ 与 Park 变换

Park 变换要"把坐标系固定在转子磁极上"，因此先要说清"转子磁极的角度"是什么——它**不是**转子机械角度。

永磁转子有 $p$ 对磁极（pole pairs，无量纲）。定子绕组看到的磁场每经过一对 N–S 极就完成一个电周期，所以转子机械转过 $\theta_m$（rad）时，磁场（电气量）转过：

$$\theta_e = p\,\theta_m,\qquad \omega_e = \frac{d\theta_e}{dt} = p\,\omega_m$$

- $\theta_m,\ \omega_m$：转子机械角度（rad）与机械角速度（rad/s）——编码器/减速器/关节看到的量；
- $\theta_e,\ \omega_e$：电角度（rad）与电角速度（rad/s）——FOC、反电动势、观测器、PLL 看到的量。

两点后果贯穿全篇：**(i)** 同一个机械转速下，极对数越多，$\omega_e$ 越高，电流环要跟踪的正弦频率越高（12N14P 外转子电机 $p = 7$，机械 3000 rpm 对应电频率 $7\times50 = 350$ Hz；微型空心杯无刷电机极对数常为 1–2，具体型号待核实）；**(ii)** 反电动势幅值正比于 $\omega_e$（§3.1），故极对数也参与决定 $K_e$（§2.4）。

引入转子电角度 $\theta_e$，利用 **Park Transform** 将 $(\alpha, \beta)$ 旋转对齐到转子磁极上，得到直轴 (d-axis，沿永磁体 N 极磁链方向) 与交轴 (q-axis，超前 d 轴 $90°$ 电角度)：
$$\begin{bmatrix} I_d \\ I_q \end{bmatrix} = \underbrace{\begin{bmatrix} \cos\theta_e & \sin\theta_e \\ -\sin\theta_e & \cos\theta_e \end{bmatrix}}_{T(\theta_e)} \begin{bmatrix} I_\alpha \\ I_\beta \end{bmatrix}$$

![[Park Transform.png]]

直觉：$(\alpha,\beta)$ 里的电流矢量在"跟着转子一起转"，观察者若也坐到转子上，就看到一个不转的矢量——它在 d、q 轴上的两个投影 $I_d, I_q$ 在稳态下是**常数**（直流）。这就是"把三相交流当直流控"的全部秘密。

### 2.3 d-q 坐标系下的动态方程：交叉耦合项从哪里来

> 这是最常被"跳步"的一段：教材直接抛出带 $\omega_e L I$ 的方程。下面把它推出来，因为交叉耦合项正是 §5.2 高速下电流环带宽被拉低的物理根源。

记 $\mathbf{I}_{\alpha\beta} = [I_\alpha, I_\beta]^\top$，$\mathbf{I}_{dq} = T(\theta_e)\mathbf{I}_{\alpha\beta}$，因此 $\mathbf{I}_{\alpha\beta} = T^{-1}(\theta_e)\mathbf{I}_{dq}$（$T$ 是旋转矩阵，$T^{-1} = T^\top$）。对 §2.1 的 $\alpha\beta$ 方程左乘 $T(\theta_e)$。前两项直接得到 $\mathbf{V}_{dq}$ 与 $R_s\mathbf{I}_{dq}$；关键在电感项，因为 $T$ 本身随时间变化（$\theta_e$ 在转）：

$$\frac{d\mathbf{I}_{\alpha\beta}}{dt} = \frac{d}{dt}\big[T^{-1}\mathbf{I}_{dq}\big] = T^{-1}\frac{d\mathbf{I}_{dq}}{dt} + \frac{dT^{-1}}{d\theta_e}\,\omega_e\,\mathbf{I}_{dq}$$

左乘 $T$：

$$T\frac{d\mathbf{I}_{\alpha\beta}}{dt} = \frac{d\mathbf{I}_{dq}}{dt} + \omega_e\,\underbrace{T\frac{dT^{-1}}{d\theta_e}}_{=\begin{bmatrix}0&-1\\1&0\end{bmatrix}}\mathbf{I}_{dq} = \frac{d\mathbf{I}_{dq}}{dt} + \omega_e\begin{bmatrix}-I_q\\ I_d\end{bmatrix}$$

（中间那个矩阵可以直接算：$T^{-1} = \begin{bmatrix}\cos&-\sin\\ \sin&\cos\end{bmatrix}$，对 $\theta_e$ 求导得 $\begin{bmatrix}-\sin&-\cos\\ \cos&-\sin\end{bmatrix}$，再左乘 $T$ 即得 $\begin{bmatrix}0&-1\\1&0\end{bmatrix}$——一个 $90°$ 旋转算子。）

反电动势项：由 §3.1 将证明 $e_\alpha = -\psi_m\omega_e\sin\theta_e,\ e_\beta = \psi_m\omega_e\cos\theta_e$，做 Park 变换：$e_d = \cos\theta_e e_\alpha + \sin\theta_e e_\beta = 0$，$e_q = -\sin\theta_e e_\alpha + \cos\theta_e e_\beta = \psi_m\omega_e(\sin^2\theta_e + \cos^2\theta_e) = \psi_m\omega_e$。即**反电动势在转子坐标系里只落在 q 轴上、且是常数**——这正是选 d 轴对齐磁链的回报。

把三部分合起来，并允许 d、q 轴电感不同（内嵌式电机 $L_d \ne L_q$；表贴式/空心杯 $L_d = L_q = L$），得到 d-q 轴动态方程：
$$\begin{cases} V_d = R_s I_d + L_d \dfrac{d I_d}{dt} - \omega_e L_q I_q \\[4pt] V_q = R_s I_q + L_q \dfrac{d I_q}{dt} + \omega_e L_d I_d + \omega_e \psi_m \end{cases}$$
* $R_s$：定子电阻（Ω）。
* $L_d, L_q$：直轴与交轴电感（H）。
* $\psi_m$：永磁体在定子绕组中产生的磁链幅值（Wb = V·s）；$\omega_e \psi_m$ 即 q 轴反电动势（V）。
* $-\omega_e L_q I_q$、$+\omega_e L_d I_d$：**交叉耦合项**（V）——它们不是"新物理"，只是电感压降在旋转坐标系下的投影；转速越高，这两项越大，d、q 两个"直流回路"互相干扰越强，电流环必须用前馈把它们减掉（§5.2）。

### 2.4 转矩方程：$T_e = \frac32 p\,\psi_m I_q$ 与直流电机 $K_t = K_e$ 的对账

**推导**（功率平衡，不跳步）：在幅值不变约定下，电机吸收的三相瞬时电功率为 $P_{in} = \frac32(V_dI_d + V_qI_q)$。把 §2.3 方程代入并展开：

$$P_{in} = \underbrace{\tfrac32 R_s(I_d^2 + I_q^2)}_{\text{铜损}} + \underbrace{\tfrac32\Big(L_dI_d\tfrac{dI_d}{dt} + L_qI_q\tfrac{dI_q}{dt}\Big)}_{\text{磁场储能变化率}} + \underbrace{\tfrac32\omega_e\Big[\psi_mI_q + (L_d - L_q)I_dI_q\Big]}_{P_{em}\text{：转化为机械功率的部分}}$$

（交叉耦合项的贡献：$V_d$ 里的 $-\omega_eL_qI_q$ 乘 $I_d$、$V_q$ 里的 $+\omega_eL_dI_d$ 乘 $I_q$，两者相加得 $\omega_e(L_d - L_q)I_dI_q$——若 $L_d = L_q$ 则相互抵消，耦合项**不做功**，只是"转移"能量。）

机械功率 $P_{em} = T_e\,\omega_m$，而 $\omega_m = \omega_e/p$（§2.2）。两边除以 $\omega_m$：

$$T_e = \frac{P_{em}}{\omega_m} = \frac{3}{2} p \left[ \psi_m I_q + (L_d - L_q)I_d I_q \right]$$

- 第一项 $\psi_m I_q$：**永磁转矩**（永磁体磁场与 q 轴电流相互作用）；第二项 $(L_d - L_q)I_dI_q$：**磁阻转矩**（转子磁路不对称时才有）。
- 单位核对：$p$ 无量纲，$\psi_m$ 为 V·s，$I_q$ 为 A，V·s·A = J = N·m ✓。

对表贴式电机（SPM）与空心杯电机（无铁芯，磁路各向同性），$L_d = L_q$，磁阻项消失；再取 $I_d = 0$（§2.5 证明这是最优），力矩公式坍缩为：
$$T_e = \left( \frac{3}{2} p \psi_m \right) I_q = K_t I_q,\qquad K_t \equiv \tfrac32 p\,\psi_m\ (\text{N·m/A})$$
**结论：** FOC 的本质是将观察系转移到转子上，使得控制 $I_q$ 即等效于控制直流电机的力矩。

> [!important] 对账：直流电机 $K_t = K_e$，PMSM 为什么是 $K_t = \frac32 K_e$？
> **直流电机**（[[电机]] §0 的统一模型）只有一个电枢回路：电功率 $e\cdot I = K_e\omega_m I$ 全部变成机械功率 $\tau\omega_m = K_tI\omega_m$，两边约掉 $I\omega_m$ 立刻得 $K_t = K_e$（SI 单位下数值相等：N·m/A 与 V·s/rad 量纲相同）。
> **PMSM**：定义每相反电动势常数 $K_e$ 为"每单位**机械**角速度产生的相反电动势峰值"：$|e| = \psi_m\omega_e = \psi_m p\,\omega_m \Rightarrow K_e = p\,\psi_m$（V·s/rad）。于是 $K_t = \frac32 p\psi_m = \frac32 K_e$。多出来的 $\frac32$ **正是 Clarke 幅值不变约定带来的功率系数**：三相各自贡献 $e_xI_x$，三个 $\cos^2$ 的时间平均各为 $\frac12$，$3\times\frac12 = \frac32$。物理上仍然是"电功率 = 机械功率"，一点没变；只是 $I_q$ 是"单相峰值"而不是"总电流"。
> **与数据手册对账**：厂家常给线电压有效值 $K_{e,LL,rms}$（V/(rad/s)）和 $K_t$（N·m/A$_{rms}$）。相峰值与线有效值的关系为 $K_e = \sqrt{\tfrac23}\,K_{e,LL,rms}$，相峰值电流与相有效值的关系为 $I_q = \sqrt2\,I_{rms}$，代入 $T_e = \tfrac32K_eI_q$ 得 $T_e = \tfrac32\cdot\sqrt{\tfrac23}\cdot\sqrt2\,K_{e,LL,rms}I_{rms} = \sqrt3\,K_{e,LL,rms}\,I_{rms}$，即数据手册上熟悉的 **$K_t = \sqrt3\,K_{e,LL,rms}$**。三个式子（$K_t = K_e$、$K_t = \frac32K_e$、$K_t = \sqrt3K_e$）说的是同一件事，差别只在"$K_e$ 和 $I$ 各按哪种约定量"。

> [!tip] 这个 $K_t$ 就是后文所有"力矩反馈"的根
> L25 SDK `torque.py` 读回的力矩是 $\tau = K_t^{nominal}I_q^{measured}$（§6.3）。它有多可信，取决于 $K_t = \frac32p\psi_m(T)$ 里的 $\psi_m$ 随温度漂了多少（§4.2）。

### 2.5 为什么 $I_d = 0$ 只对表贴式电机是 MTPA

"最大转矩电流比 (Maximum Torque Per Ampere, MTPA)" 的问题是：给定电流幅值 $|I| = \sqrt{I_d^2 + I_q^2}$（受铜损/驱动器限制），怎样分配 $I_d, I_q$ 使 $T_e$ 最大？令 $I_d = -|I|\sin\beta,\ I_q = |I|\cos\beta$（$\beta$ 为电流矢量超前 q 轴的角度，rad），代入 §2.4 的完整转矩公式并用 $\sin\beta\cos\beta = \frac12\sin2\beta$：

$$T_e(\beta) = \tfrac32p\Big[\psi_m|I|\cos\beta + \tfrac12(L_q - L_d)|I|^2\sin2\beta\Big]$$

对 $\beta$ 求导置零：$-\psi_m|I|\sin\beta + (L_q - L_d)|I|^2\cos2\beta = 0$。

- **表贴式 / 空心杯（$L_d = L_q$）**：第二项恒为零，方程退化为 $\sin\beta = 0 \Rightarrow \beta = 0 \Rightarrow I_d = 0$。此时 $I_d$ 只会白白增加铜损、既不产生力矩也（在基速以下）没有必要退磁，所以"$I_d = 0$"**恰好**就是 MTPA。空心杯电机无铁芯、磁路完全各向同性，这一结论对它是**精确**成立的——这是灵巧手空心杯关节 FOC 固件普遍用 $I_d = 0$ 而不做 MTPA 查表的物理理由。
- **内嵌式 (IPM，$L_q > L_d$)**：$\cos2\beta$ 项不为零，最优 $\beta > 0$，即需要**负** $I_d$ 来"顺便"利用磁阻转矩，$I_d = 0$ 只是次优。工业伺服/车用 IPM 电机的 MTPA 曲线就是解这个方程得到的。

> [!warning] 修正（原文表述）
> 原文写"在 MTPA 策略下我们强制令 $I_d = 0$"，读起来像是 MTPA 的定义就是 $I_d = 0$。准确说法是：**$I_d = 0$ 是 MTPA 在 $L_d = L_q$ 时的特解**；对凸极电机它不是最优。对本项目的空心杯电机结论不变，但推导来源必须写对。基速以上另有弱磁需求（§5.1），那时 $I_d < 0$ 不是为了力矩最优，而是为了电压可行。

### 2.6 从电流环到串级三环：谁给 $I_q$ 下指令，为什么带宽要分离 5–10 倍

> **为什么现在讲这个**：到此为止我们有了一个"旋钮" $I_q$；但 RL 策略给 L25 的是 20–50 Hz 的**位置**指令。位置怎么变成 $I_q$？答案是三级级联，而它能工作的唯一前提就是带宽分离——这个前提在 §5.2、§6.5 里会一再被真机打破。

真机固件的标准结构（由内向外）：

$$\underbrace{q_{des}\ \xrightarrow{\ \text{位置环 (P/PD)}\ }\ \dot q_{ref}}_{\text{外环：}\sim 10\text{–}100\ \text{Hz}}\ \xrightarrow{\ \text{速度环 (PI)}\ }\ \underbrace{I_{q,ref}}_{\text{中环：}\sim 100\text{–}500\ \text{Hz}}\ \xrightarrow{\ \text{电流环 (PI) + FOC + PWM}\ }\ \underbrace{I_q \to \tau}_{\text{内环：}\sim 1\text{–}5\ \text{kHz}}$$

- **位置环**：输入位置误差 $q_{des} - q$（rad），输出速度参考 $\dot q_{ref}$（rad/s）；
- **速度环**：输入速度误差，输出电流参考 $I_{q,ref}$（A）——它的输出就是 §2.4 的力矩指令 $\tau_{ref} = K_tI_{q,ref}$；
- **电流环**：输入电流误差，输出 $V_q$ 指令（V），经逆 Park、SVPWM 变成三相占空比。

**为什么内环必须远快于外环（推导而非口诀）**：外环设计时把内环当作"理想的、瞬时达到参考值的单位增益"。实际上内环闭环是一个一阶低通 $G_{in}(s) \approx \frac{1}{1 + s/\omega_{in}}$（$\omega_{in}$ 为内环带宽，rad/s）。它在外环穿越频率 $\omega_{out}$ 处引入的**相位滞后**为 $\phi = \arctan(\omega_{out}/\omega_{in})$：
- $\omega_{in}/\omega_{out} = 5 \Rightarrow \phi \approx 11.3°$；$=10 \Rightarrow \phi \approx 5.7°$；$=2 \Rightarrow \phi \approx 26.6°$。

外环通常只有 45–60° 的相位裕度预算（[[ControlTheory#1.3 频率响应：Bode、相位裕度与带宽|ControlTheory §1.3]]），被内环白白吃掉 26° 就已接近振荡边缘；5–10 倍分离把这个"税"压到 10° 以内，于是"内环视为理想"的近似成立，三环可以逐级独立整定。这也正是 [[ControlTheory#7.4 反步法 (Backstepping)：为串级系统"逐级建 Lyapunov"|反步法]]里"上一级已收敛、可作虚拟控制量"假设的工程充分条件（详见 [[Actuation#4. 串级控制：电流环 → 速度环 → 位置环|Actuation §4]]）。

**落到 L25**：电流环由 MCU 上的 FOC 在 kHz 级闭合（对策略透明，§4.5）；位置指令 20–50 Hz 到达——按 Nyquist，指令本身最多只能激励 10–25 Hz 的运动，位置环带宽再高也没用；速度环则夹在中间。策略从 RL 侧看到的"执行器"其实是这三层加起来的一个低通 + 饱和 + 延迟系统，这就是 §6.5 与 [[Actuator2RigidDynamicsModel_gap]] 要建模的对象。

---

## 三、 无感观测：Luenberger 观测器与 PLL

> **为什么现在讲这个**：Park 变换需要 $\theta_e$。有编码器时直接读；没有时（成本、体积——微型空心杯电机常常连霍尔都塞不下）只能从电流里"反推"。本节推出这条反推链，更重要的是推出它**在什么条件下必然失效**——这个失效边界直接回答了"灵巧手为什么仍要关节位置传感器"。

### 3.1 反电动势的几何学解释
永磁转子磁链在 $(\alpha, \beta)$ 轴上的投影随转子角度旋转：$\psi_\alpha = \psi_m \cos\theta_e$，$\psi_\beta = \psi_m \sin\theta_e$（$\psi_m$ 为磁链幅值，Wb）。法拉第定律说感应电动势等于磁链变化率、方向由楞次定律决定（阻碍电流变化）。§2.1 的 KVL 已把它写成右侧的一项**压降** $+e$（$V = R_sI + L\frac{dI}{dt} + e$），楞次的负号已经被这个写法吸收，所以在该约定下 $e = +\frac{d\psi}{dt}$。求导并代入链式法则 $\frac{d\theta_e}{dt} = \omega_e$：
$$\begin{cases} e_\alpha = \dfrac{d}{dt}\big(\psi_m\cos\theta_e\big) = -\psi_m\,\omega_e\sin\theta_e \\[4pt] e_\beta = \dfrac{d}{dt}\big(\psi_m\sin\theta_e\big) = \psi_m\,\omega_e\cos\theta_e \end{cases}$$

这就是本篇统一采用的写法（也是工程固件里最常见的）：
$$\boxed{e_\alpha = -\psi_m\omega_e\sin\theta_e,\qquad e_\beta = \psi_m\omega_e\cos\theta_e}$$
即反电动势矢量幅值为 $|e| = \psi_m|\omega_e|$（V），方向**超前**磁链方向 $90°$ 电角度（磁链在 $\theta_e$，反电动势在 $\theta_e + 90°$）。用 §2.4 的 $K_e = p\psi_m$ 也可写成 $|e| = K_e|\omega_m|$——两种写法差一个极对数 $p$，§四 中的 "$K_e\omega_e$" 应按 $|e|$ 理解。

反电动势 $e_{\alpha\beta}$ 完美编码了角度信息 $\theta_e$：只要拿到 $(e_\alpha, e_\beta)$，$\theta_e = \operatorname{atan2}(-e_\alpha, e_\beta)$。但它同时也编码了一个坏消息：**幅值正比于 $\omega_e$，转速趋零时信号趋零**——§3.6 会回到这一点。

### 3.2 为什么不能直接代数求解？
由 KVL 理论上可直接算得：$e = V - R_sI - L \frac{dI}{dt}$。
但在工程实现中：电流 $I$ 由 ADC 采样得到，包含高频白噪声（量化噪声 + 开关噪声）。对其求导 $\frac{di}{dt}$ 会导致噪声被微分算子按频率成比例放大（对白噪声，微分器增益 $\propto\omega$，高频分量被放大成百上千倍），完全淹没真实信号。同时，发热引起的 $R_s$ 漂移（§4.1）会让代数方程直接失效：$R_s$ 差 20% 就意味着 $R_sI$ 项的误差直接原封不动地进了 $e$。

### 3.3 Luenberger Observer 的闭环逻辑
我们在软件中构建一个"虚拟电机"，输入同样的电压 $V$（这是 FOC 自己算出来的指令，已知），让它用**估计的**反电动势 $\hat e$ 跑：
$$L \frac{d\hat{I}}{dt} = V - \hat{R}_s\hat{I} - \hat{e}$$
真实电机是 $L\frac{dI}{dt} = V - R_sI - e$。定义电流误差 $\tilde{I} = I - \hat{I}$，两式相减（暂设 $\hat R_s = R_s$）：
$$L\frac{d\tilde I}{dt} = -R_s\tilde I - (e - \hat e)$$
这告诉我们：**只要 $\hat e \ne e$，虚拟电流就会偏离真实电流**——电流误差是反电动势误差的"探针"。于是用 PI 反馈，把 $\hat e$ 定义为作用在 $\tilde I$ 上的 PI 输出（符号取负，使误差为正时压低 $\hat I$ 的驱动、抬高 $\hat e$）：
$$\hat e \;\equiv\; -\Big[K_p\tilde I + K_i\!\int\!\tilde I\,dt\Big]$$
- $K_p$（Ω）、$K_i$（Ω/s）：观测器增益，量纲使 $\hat e$ 为 V。

把它代回虚拟电机，就是常见的合并写法 $L\frac{d\hat I}{dt} = V - \hat R_s\hat I + K_p\tilde I + K_i\!\int\!\tilde I\,dt$。误差动态变为
$$L\frac{d\tilde I}{dt} = -(R_s + K_p)\tilde I - K_i\!\int\!\tilde I\,dt - e ,$$
一个以 $e$ 为"扰动输入"的二阶稳定系统。稳态时 $\tilde I \to 0$、$\frac{d\tilde I}{dt} \to 0$，于是
$$\hat{e} \;\to\; e = - K_i \int \tilde{I}\, dt .$$
**原理本质：** 通过强迫两套系统的状态对齐，我们用极度稳定的积分操作，替代了极度不稳定的微分操作，把未知的扰动（真实的 $e$）"挤压"到了 PI 积分器的输出中。

> [!warning] 修正（原文方程）
> 原文把观测器写成 $L\frac{d\hat I}{dt} = V - \hat R\hat I - \hat e + K_p\tilde I + K_i\int\tilde I\,dt$，同时含 $-\hat e$ 与 PI 项，等于把同一个量记了两次（$\hat e$ 本身就是 PI 的输出）。正确的是上面两种等价写法之一：要么写 $-\hat e$ 并另行定义 $\hat e$ 为 PI 输出，要么直接写 PI 项而不再出现 $\hat e$。结论 $\hat e \to -K_i\int\tilde I\,dt$ 不变。§4.1 引用该方程时按此理解。

> [!note] 这是通用 Luenberger 观测器的特例
> 状态 $x = [I, e]^\top$，输出 $y = I$，能把 $e$ 当状态估计的前提是 $e$ 相对电流是慢变量（一个电流环周期内 $\dot e \approx 0$）。分离原理允许观测器极点独立于电流环极点配置——见 [[ControlTheory#1.5 通用状态观测器 (Luenberger) 与分离原理|ControlTheory §1.5]] 与 [[Actuation#3.2 Luenberger 观测器：用积分替代微分|Actuation §3.2]]。

### 3.4 角度提取：锁相环 (PLL)
不推荐直接使用 $\theta_e = \arctan(-\hat{e}_\alpha / \hat{e}_\beta)$，因为除法运算对过零点极度敏感（$\hat e_\beta \to 0$ 时任何噪声都被放大成角度跳变），且 $\arctan$ 输出不连续。

工程上构造一个"内部也在转的角度" $\hat\theta_e$，并用它去"测"真实反电动势的相位差。把 §3.1 的 $\hat e_\alpha = -|e|\sin\theta_e$、$\hat e_\beta = |e|\cos\theta_e$ 代入下式（**不是**和差化积，而是正弦差角公式 $\sin(A - B) = \sin A\cos B - \cos A\sin B$）：
$$\epsilon = -\hat{e}_\alpha \cos\hat{\theta}_e - \hat{e}_\beta \sin\hat{\theta}_e = |e|\big(\sin\theta_e\cos\hat\theta_e - \cos\theta_e\sin\hat\theta_e\big) = |e|\sin(\theta_e - \hat{\theta}_e)$$
其中 $|e| = \psi_m\omega_e$。当误差极小时，$\sin(\theta_e - \hat{\theta}_e) \approx \theta_e - \hat{\theta}_e$，$\epsilon$ 就是一个线性的相位误差信号。将 $\epsilon$ 送入 PI 控制器得到转速估计 $\hat{\omega}_e$，再对其积分获得极其平滑的角度 $\hat{\theta}_e$：
$$\hat\omega_e = K_{p,pll}\,\epsilon + K_{i,pll}\!\int\!\epsilon\,dt,\qquad \hat\theta_e = \int\hat\omega_e\,dt$$
这是一个二阶闭环（PI + 积分器），对恒速输入无稳态误差。

**两个不能省的工程细节**：
1. **归一化**：环路增益含 $|e| = \psi_m\omega_e$，随转速变化——高速时 PLL 太"冲"、低速时太"软"。固件通常用 $\epsilon/\sqrt{\hat e_\alpha^2 + \hat e_\beta^2}$ 归一化，使带宽与转速无关。
2. **反转**：$\omega_e < 0$ 时 $|e|$ 变号，反馈符号反转、PLL 失稳。需按 $\operatorname{sign}(\hat\omega_e)$ 翻转误差符号——换向瞬间（§5.4 的过零点）正是它最脆弱的时刻。

### 3.5 线性模型的两个失效边界

上面的观测器/PLL 全部建立在 $L$、$R_s$ 是常数的线性模型上。真机里有两条边界会把它推翻：

- **磁饱和与恒定电感的灾难性假设**
  动力学方程中预设了 $L_q$ 为常数。但在灵巧操作需输出瞬态峰值力矩时，电机电流往往被推向极限（Overdrive），导致定子铁芯进入深度磁饱和，$L_q$ 会呈严重非线性下降。基于线性假设的 FOC 计算出的 $I_q$ 指令将无法产生期望的物理力矩，这种非线性是 Reality Gap 的重要组成部分。空心杯电机（Coreless Motor）无铁芯：**$L$ 不受磁饱和影响**（代价见 §4.3：$L$ 极小、电流纹波大）。

- **热漂移的脆弱性**
  定子电阻 $R_s$ 会随连续高负载作业发热而产生高达 50% 的漂移。如果在观测器中固化 $\hat{R}_s$，电压前馈补偿的偏差将不可逆地转化为角度估算误差，并最终表现为扭矩追踪精度的稳态下降。定量分析见 §4.1。

### 3.6 低速崩溃边界：为什么灵巧手关节仍然要位置传感器

> 这是本节对"定开发方向"最有用的结论。

**失效机理（三步）**：
1. 信号幅值 $|e| = \psi_m\omega_e$ 随转速线性下降；
2. 噪声不下降：ADC 量化噪声、PWM 开关噪声、$R_s$ 漂移带来的 $\Delta R_s\cdot I$ 偏置（§4.1）都与转速无关；
3. 因而信噪比 $\propto\omega_e$。经验上，基于反电动势的无感方案在**约 5–10% 额定转速以下**角度估计失效，零速时完全不可观（$e = 0$，任何角度都与观测一致）。

**为什么这对灵巧手是致命的而对风扇/云台不是**：灵巧手关节的工作点恰恰集中在低速与零速——保持抓握、接触切换 (grasp-regrasp)、指尖微调，都是"转速接近零、却最需要精确力矩和位置"的工况。此外：
- 无感估计的是**电机轴电角度** $\theta_e$，而 RL 策略需要的是**关节角度** $q$。两者之间隔着丝杠（$N_{eq}\approx108$，拇指 ≈1424/1800）、连杆与背隙——即便电机侧角度完美，关节侧仍是未知量。
- 所以 L25 在**关节侧**装了位置传感器（8-bit，0–255 反馈，[[Actuator2RigidDynamicsModel_gap]]）；电机侧 FOC 若无编码器，则只能靠下面的启动策略。

**零速/低速时怎么启动（两条工程路线）**：
- **I/F 启动 (current–frequency open-loop)**：不管转子在哪，强制施加一个幅值固定、角度按预设频率线性增长的电流矢量，转子像步进电机一样被"拖"着跟随；转到观测器可用的转速后再切换到闭环。代价：启动阶段力矩方向不可控，可能先反抖一下——对负载已接触的手指来说是不可接受的扰动。
- **高频注入 (HFI, High-Frequency Injection)**：在 d 轴叠加一个几 kHz 的小电压，利用 $L_d \ne L_q$（凸极性）使响应电流的幅值随注入方向与真实 d 轴的夹角变化，从而在**零速**下解出角度。但 §2.5 已说明表贴式/空心杯电机 $L_d = L_q$——**没有凸极性，HFI 几乎无信号**。结论：空心杯关节要么装传感器（编码器/霍尔/电位计），要么接受无感只在中高速可用。

> [!tip] 对开发的直接含义
> 不要试图靠"更好的观测器"去掉 L25 的关节传感器；相反，该考虑的是关节传感器 8-bit 分辨率（量程/255）够不够（[[Transmission2JointDynamics_gap]] 的死区分析），以及电机侧是否有可读的相电流/$I_q$（§6.1）以补足力矩信息。

---

## 四、 温度对电机模型参数的系统性影响

> **为什么现在讲这个**：§二、§三 的每一个公式都把 $R_s, \psi_m, L$ 当常数。真机跑几十秒就把它们全部变了；这一节按"漂多少 → 打到哪一个方程 → 最终力矩差多少"逐个追踪，是 Actuator Model 要不要把温度当输入的定量依据。

> [!warning] 核心洞察
> 灵巧手执行快速 in-hand reorientation 时，空心杯电机在数十秒内即可从室温升至 60-80°C，导致电机模型中 **几乎所有"常数"都不再是常数**。这是 Sim-to-Real Gap 中最隐蔽的来源之一。
> 传统仿真器（如 IsaacGym/MuJoCo）将电机模型简化为 $\tau = K_t \cdot I_q$（恒定 $K_t$），完全忽略了温度引起的级联漂移。

### 4.1 定子电阻 $R_s(T)$：最大漂移源

铜绕组电阻对温度的依赖遵循线性模型：

$$R_s(T) = R_s(T_0)\left[1 + \alpha_{Cu}(T - T_0)\right]$$

其中 $\alpha_{Cu} \approx 0.00393\,/°C$ 为铜的电阻温度系数，$T_0$ 为标定温度（通常 25°C）。

| 温升 $\Delta T$ | $R_s$ 增幅 | 对系统的影响 |
|:-:|:-:|:--|
| +30°C（轻载持续） | +12% | Luenberger Observer 前馈补偿产生偏差，角度估计开始漂移 |
| +55°C（中度连续操作） | +22% | 相同 PWM 占空比下实际电流降低，力矩输出显著不足 |
| +80°C（高速 reorientation 极限） | +31% | 电流环 PI 控制器严重失调，力矩带宽骤降 |

**对 Luenberger Observer 的致命影响**：观测器模型中使用固定 $\hat{R}_s = R_s(T_0)$，而真实 $R_s$ 持续增大。由 §3.3 的观测器方程（式中 $\hat e$ 即 PI 输出，见 §3.3 修正说明）：

$$L\frac{d\hat{I}}{dt} = V - \hat{R}_s \hat{I} - \hat{e} + K_p(I - \hat{I}) + K_i\int(I - \hat{I})dt$$

当 $\hat{R}_s < R_s^{real}$ 时，观测器对 $RI$ 项的补偿不足，缺失的电压降 $\Delta R \cdot I$ 被 PI 积分器错误地吸收进 $\hat{e}$ 中，导致反电动势估计产生等效的偏置误差 $\delta e \approx \Delta R_s \cdot I$。经由 PLL 提取角度时，该偏置引入稳态角度误差：

$$\delta \theta_e \approx \frac{\Delta R_s \cdot I_q}{K_e \omega_e}$$

（推导：偏置 $\delta e$ 与真实 $|e|$ 正交分量之比即为小角度误差，$|e| = \psi_m\omega_e$；此处分母 $K_e\omega_e$ 按 §3.1 的 $|e|$ 理解。）

**关键特征**：此误差在低速时被 $\omega_e$ 在分母放大——恰好是灵巧手在接触切换（grasp-regrasp）时最需要精确力矩控制的时刻。这与 §3.6 的信噪比论证是同一件事的两面。

### 4.2 永磁体磁链 $\psi_m(T)$：力矩常数的根源性衰减

NdFeB（钕铁硼）永磁体的剩余磁通密度具有负温度系数：

$$\psi_m(T) = \psi_m(T_0)\left[1 + \beta_{NdFeB}(T - T_0)\right], \quad \beta_{NdFeB} \approx -0.0012\,/°C$$

$$K_t(T) = \frac{3}{2}p\,\psi_m(T), \quad K_e(T) = p\,\psi_m(T)$$

| 温升 $\Delta T$ | $\psi_m$ 衰减 | $K_t$ 衰减 | $K_e$ 衰减 |
|:-:|:-:|:-:|:-:|
| +30°C | -3.6% | -3.6% | -3.6% |
| +55°C | -6.6% | -6.6% | -6.6% |
| +80°C | -9.6% | -9.6% | -9.6% |

**级联效应**：
1. **力矩直接衰减**：$T_e = K_t(T) \cdot I_q$。在同一 $I_q$ 下，力矩下降近 10%。对于快速 reorientation 中需要的峰值加速力矩，这意味着动态响应变慢。
2. **反电动势减弱**：$K_e$ 下降导致 Luenberger Observer 估算的 $\hat{e}$ 幅值偏大（因为观测器内部仍用 $K_e(T_0)$ 解算），PLL 输出转速 $\hat{\omega}_e$ 产生正偏差。
3. **$R_s$ 上升 + $K_t$ 下降的叠加**：真机中两者同向恶化——需要更大电流才能维持同等力矩，但更大电流又加剧发热，形成**正反馈热失控环路**。

> [!warning] 修正（第 2 条的机理）
> 观测器本身并不使用 $K_e$（§3.3 的 $\hat e$ 是直接从电流误差里积分出来的，与 $K_e$ 无关），PLL 又是带积分器的闭环，稳态转速估计 $\hat\omega_e$ 对环路增益不敏感——所以 $K_e$ 漂移**不会**直接给 $\hat\omega_e$ 引入稳态偏差。它真正造成的是：(a) 若固件未做 §3.4 的归一化，PLL 环路增益随 $|e|$ 下降而变软、跟踪带宽降低；(b) 若固件用开环换算 $\hat\omega = |\hat e|/K_e(T_0)$ 来估速（部分低成本方案如此），则 $|\hat e|$ 变小反而给出**负**偏差。原文"正偏差"的说法保留以示修改痕迹，但机理按此理解。对 §6 的结论（力矩反馈不可靠、温度应作 Actuator Model 输入）没有影响。

### 4.3 电感 $L_d, L_q$：非线性磁饱和

电感主要由线圈几何形状和铁芯磁导率决定。温度对电感的**直接**影响较小（铜导体几何不随温度显著变化）。但存在**间接**强耦合：

$$L_q(I_q) = L_{q,0} \cdot f_{sat}(I_q), \quad f_{sat}(I_q) = \frac{1}{1 + (I_q / I_{sat})^n}$$

- 当温度升高 → $K_t$ 下降 → 维持同一力矩需要更大 $I_q$ → 铁芯更深磁饱和 → $L_q$ 进一步塌陷
- $L_q$ 塌陷导致电流环有效增益变化（电流环传递函数为 $G(s) = 1/(Ls + R)$），PI 参数失配
- 空心杯电机（Coreless Motor）无铁芯：**$L$ 不受磁饱和影响**，这是空心杯电机在灵巧手中被广泛采用的物理优势之一。但是空心杯电机的 $L$ 极小（微亨级），导致电气时间常数 $\tau_e = L/R$ 极短（<100μs），使得电流纹波对 PWM 频率极度敏感

### 4.4 综合温度模型：各参数耦合下的力矩输出偏差

定义温度相关的**有效力矩传递函数**（从 $I_q$ 指令到实际关节力矩）：

$$\tau_{actual}(T) = K_t(T) \cdot I_q^{actual}(T) \cdot \eta_{mech}(T)$$

其中：
- $I_q^{actual}(T) = \frac{V_{dc} - K_e(T)\omega_e}{R_s(T)} \bigg|_{steady-state}$ （稳态最大可达电流随温度下降）
- $\eta_{mech}(T)$：机械传动效率，润滑脂粘度随温度变化。低温时粘度增大，高温时降低但磨损加剧。

**Sim-to-Real 的核心矛盾**：仿真中 $K_t, R_s, K_e$ 均为标定时的常数。真机中这些参数每分钟都在漂移。如果 World Model 的 Actuator Model 不捕捉这种漂移，World Model 的预测将在长 horizon rollout 中产生累积偏差。Foundation 级总结见 [[Actuation#6.1 两个漂移源与热失控环路|Actuation §6.1]]。

### 4.5 温度漂移的时间尺度与 RL 交互的耦合

| 物理过程 | 时间尺度 | RL 影响 |
|:--|:-:|:--|
| 电气时间常数 $\tau_e = L/R$ | ~10-100 μs | 远快于策略频率，对 RL 透明 |
| 机械时间常数 $\tau_m = J\omega/\tau$ | ~1-10 ms | 与 RL 控制频率（50-200Hz）同阶，**必须建模** |
| 热时间常数 $\tau_{th}$ | ~10-60 s | 跨 episode 缓慢漂移，同一 episode 内近似恒定 |
| 磨损/老化 | ~天-周 | 长期漂移，需要在线 adaptation |

**对 Actuator Model 设计的启示**：
- $\tau_e$ 级别的快动态被 FOC 电流环在 MCU 上闭合处理，策略无需关心
- $\tau_m$ 级别的动态需要 Actuator Model 通过历史窗口隐式捕捉
- $\tau_{th}$ 级别的温度漂移可以通过**将温度传感器读数 $T_{motor}$ 作为 Actuator Model 的显式输入**来处理
- 磨损级别的长期漂移需要 online adaptation（如在线微调 Actuator Model）

---

## 五、 高速 In-Hand Reorientation 下的电机动力学特性

> **为什么现在讲这个**：§四 讲的是"跑久了"的漂移，本节讲"跑快了"的极限。两者叠加（高速任务同时也是高电流、高温任务）决定了真机力矩包络的真实形状——它不是仿真里的矩形 action clip。

> [!abstract] 核心场景
> 灵巧手执行快速转笔（pen spinning）或高速 in-hand reorientation 时，电机转速可达数千 RPM，产生一系列在低速任务中不显著但在高速下主导系统行为的物理效应。

### 5.1 反电动势电压天花板与弱磁区域

由 §2.3 的 d-q 轴方程，稳态下（$\frac{dI}{dt} = 0$）q 轴电压方程为：

$$V_q = R_s I_q + \omega_e L_d I_d + \omega_e \psi_m$$

电机可用的总电压受 DC 母线电压 $V_{dc}$ 约束（$\sqrt3$ 来自 SVPWM 六边形的内切圆半径，推导见 [[Actuation#2.2 力矩生成与 MTPA|Actuation §2.2 的 SVPWM 注]]）：

$$V_d^2 + V_q^2 \leq \left(\frac{V_{dc}}{\sqrt{3}}\right)^2$$

当 $\omega_e$ 升高，反电动势项 $\omega_e \psi_m$ 线性增长。定义**基速**（Base Speed）为 $I_d = 0$ 时电压恰好饱和的转速（把 $I_d = 0$、$V_q = V_{dc}/\sqrt3$ 代入上式解出 $\omega_e$）：

$$\omega_{base} = \frac{V_{dc}/\sqrt{3} - R_s I_{q,rated}}{{\psi_m}}$$

**超过基速后**：
- $\omega_e \psi_m > V_{dc}/\sqrt{3}$，此时即使 $I_q = 0$ 也无法满足电压约束
- FOC 被迫注入**负** $I_d$（弱磁电流），人为削弱永磁体的等效磁通以降低反电动势（在 $V_q$ 方程里，$\omega_eL_dI_d$ 项为负，抵消一部分 $\omega_e\psi_m$）
- 代价：(1) $I_d$ 占用了电流矢量的一部分幅值空间，$I_q$（力矩电流）的上限被压缩；(2) 磁链被人为削弱进一步降低 $K_t$
- **结论**：在高速 reorientation 中，电机的**力矩能力随转速上升而非线性下降**。这是一个经典的转矩-转速包络（Torque-Speed Envelope）约束：

$$\text{恒转矩区 } (\omega < \omega_{base}): \quad T_{max} = K_t I_{q,max}$$
$$\text{恒功率区 } (\omega > \omega_{base}): \quad T_{max}(\omega) \approx \frac{P_{max}}{\omega} = \frac{K_t I_{q,max} \omega_{base}}{\omega}$$

> [!tip] 对 RL 策略的启示
> 当策略尝试在高速旋转中施加大力矩（如急停或方向急变），真机的力矩响应将远低于仿真预期。这种**速度相关的力矩饱和**是 Sim-to-Real 最大的未建模动力学之一。在仿真中 action clipping 是一个硬矩形约束，而真机的约束是一个**椭圆形的速度-力矩包络**。Foundation 级归纳见 [[Actuation#5.1 反电动势天花板与力矩-转速包络|Actuation §5.1]]。

### 5.2 电流环带宽与力矩追踪延迟

FOC 电流环的闭环带宽决定了 $I_q$ 能以多快的速度跟踪指令变化。被控对象是 $G(s) = \frac{1}{Ls + R_s}$；PI 控制器把零点放在 $-R_s/L$ 抵消对象极点后，闭环成为一阶低通 $\frac{1}{1 + sL/K_{p,i}}$，故典型 PI 电流控制器的闭环带宽为：

$$f_{bw} \approx \frac{1}{2\pi} \cdot \frac{K_{p,i}}{L}$$

- $K_{p,i}$：电流环比例增益（V/A = Ω）；$L$：相电感（H）。

对于空心杯电机（$L \sim 10\text{-}100\,\mu H$），电流环带宽可达 1-5 kHz。但在高速 reorientation 场景下：

- **交叉耦合项 $\omega_e L_q I_q$ 和 $\omega_e L_d I_d$ 急剧增大**：这些项（§2.3 推出）是 d-q 轴之间的扰动，必须由前馈解耦补偿。如果补偿不完美（如 $L$ 和 $\omega_e$ 存在估计误差），电流环有效带宽被拉低
- **采样延迟的相对影响增大**：MCU 的 ADC 采样和 PWM 更新引入固有 1-1.5 个 PWM 周期的延迟。在 20kHz PWM 下约 50-75μs。当力矩指令在 1ms 内剧烈变化（200Hz control → 5ms period），延迟占比尚可接受；但如果策略频率提升到 1kHz（如某些高频力控应用），延迟占比达 5-7.5%，足以引起力矩振荡
- **数字量化效应**：PWM 分辨率有限（如 12-bit timer at 20kHz → 一个 PWM 周期 $50\,\mu$s 被分成 $2^{12} = 4096$ 档，每档 $1/(20\,\text{kHz}\times4096)\approx 12$ ns，即**约 10 ns 量级**），在需要极精细力矩调节时（如 sub-Newton 级指尖力），量化噪声不可忽略

> [!warning] 修正
> 原文写"12-bit timer at 20kHz → ~50ns 分辨率"，数字错了：$1/(20\,\text{kHz}\times4096)\approx12$ ns，应为"约 10 ns 量级"。结论（量化噪声在精细力控时不可忽略）不变，只是量化步长比原文小 4 倍——占空比分辨率 $1/4096 \approx 0.024\%$。

### 5.3 多指协同高速操作的科里奥利/离心力耦合

在 in-hand reorientation 中，物体被多指协作驱动高速旋转。此时系统（手指 + 物体）的动力学方程中，科里奥利矩阵 $C(q, \dot{q})\dot{q}$ 和离心力项变得不可忽略：

$$M(q)\ddot{q} + C(q, \dot{q})\dot{q} + g(q) = \tau_{link} + J_c^T f_c$$

在低速操作中 $C(q, \dot{q})\dot{q} \approx 0$，力矩需求主要来自重力补偿 $g(q)$ 和惯性 $M(q)\ddot{q}$。但在高速 reorientation 中：

- $C(q, \dot{q})\dot{q}$ 与 $\dot{q}^2$ 成正比，**与速度二次方增长**
- 快速换指（finger gaiting）时，某根手指从高速滑动突然建立新接触，$\dot{q}$ 在接触瞬间发生跃变级的变化，$C \dot{q}$ 产生巨大的瞬态力矩需求
- 如果电机的力矩带宽不足以追踪这些瞬态需求（受限于 §5.2 的电流环带宽和 §5.1 的转矩-速度包络），物体将偏离目标轨迹甚至掉落

**对 World Model 的启示**：Rigid Dynamic Model 必须精确建模 $C(q, \dot{q})$，而 Actuator Model 必须准确预测在给定速度和温度下，电机实际能"兑现"多少力矩。两个模型在**力矩接口**上的耦合精度决定了高速任务的预测可靠性。

### 5.4 斯特里贝克摩擦与快速换向

当手指在高速 reorientation 中频繁换向（速度过零点）时，传动系统（丝杠/连杆）的摩擦力经历复杂的非线性转变：

$$\tau_{fric}(\dot{\phi}) = \left[F_c + (F_s - F_c)e^{-|\dot{\phi}/v_s|^{\delta_s}}\right]\text{sign}(\dot{\phi}) + B_v \dot{\phi}$$

其中：
- $F_s$：静摩擦力矩（Stiction），$F_c$：库仑摩擦力矩，$F_s > F_c$
- $v_s$：Stribeck 速度（过渡区宽度），$\delta_s$：Stribeck 指数（通常取 2）
- $B_v$：粘性摩擦系数

**过零点动力学的灾难**：
1. 手指从正转减速 → 经过 $\dot{\phi} = 0$ → 反转加速
2. 在 $\dot{\phi} \to 0$ 的瞬间，摩擦力从 $F_c$ 突然跳升至 $F_s$（可达 $F_c$ 的 2-5 倍）
3. 电机力矩如果不足以克服 $F_s$，手指将**卡死**在当前位置，直到力矩累积足够才突然弹射
4. 这种 "stick-slip" 行为导致力矩-位移关系出现**迟滞环（Hysteresis）**

**对 Actuator Model 的要求**：必须通过历史窗口 $[\dot{\phi}_{t-H:t}]$ 隐式学习当前处于 Stribeck 曲线的哪个区域。单一时刻的 $(\phi_t, \dot{\phi}_t)$ 无法区分"即将突破静摩擦"和"处于平稳滑动摩擦"。丝杠/连杆侧的摩擦折算（按 $N^1$）与实测死区见 [[Transmission2JointDynamics_gap]]。

### 5.5 空心杯电机的热容极限

空心杯电机（Coreless Motor）由于没有铁芯作为散热体，其热容远低于传统铁芯电机：

$$T_{coil}(t) = T_{amb} + \frac{I_{rms}^2 R_s(T)}{h A_{surface}} \left(1 - e^{-t/\tau_{th}}\right)$$

- 空心杯电机的热时间常数 $\tau_{th}$ 通常仅为 **5-30 秒**
- 在连续高速 reorientation（如持续转笔）中，RMS 电流极高，线圈温度可在 10-20 秒内逼近热极限
- 典型空心杯电机热极限约 120-150°C，超过此温度永磁体可能发生**不可逆退磁**

**对 RL 训练的影响**：
- 在仿真中训练的策略可以无限期输出高力矩动作，不会遇到热限制
- 真机部署时，如果策略依赖持续的高力矩（如快速连续换向），电机在一个 episode（通常 10-30s）内即可触发热保护
- **World Model 的 Actuator Model 必须包含温度状态变量**，使策略在 dream rollout 中"体验"到热约束

---

## 六、 从 FOC 物理到 Actuator Model 的建模启示

> **为什么现在讲这个**：前五节把"指令 → 力矩"之间的每一处非理想都摆在了桌面上。本节回答工程问题：哪些交给 MCU、哪些交给 Actuator Model 学、哪些信号可信到可以进 RL 观测与 WM 损失。

> [!abstract] 设计原则
> Actuator Model 不需要精确复现 FOC 的内部电气动态（那是 MCU 的事），但需要精确捕捉 **从力矩指令 $\tau_{cmd}$ 到关节实际输出力矩 $\tau_{link}$ 的端到端黑箱映射**，包括其对速度、温度、历史状态的所有依赖。

### 6.1 不可观测的中间变量

在 FOC + 机械传动的全链路中，以下关键变量对策略**不可观测**但对物理输出有决定性影响：

| 变量 | 物理含义 | 是否可测 | 对输出的影响 |
|:--|:--|:-:|:--|
| $I_q^{actual}$ | 实际 q 轴电流 | ✅ MCU 内部可读 | 直接决定电磁力矩 |
| $\theta_e$ (PLL 输出) | 电角度估计 | ✅ MCU 内部 | 估计误差直接转化为力矩方向误差 |
| $T_{coil}$ | 线圈实际温度 | ⚠️ 部分可读 | 决定 $R_s, K_t$ 漂移幅度 |
| $\tau_{fric}$ | 传动系统摩擦力矩 | ❌ | 吞掉电机力矩的"黑洞" |
| $\kappa_{stiffness}$ | 传动系统接触刚度 | ❌ | 决定弹性形变与振动模态 |
| FOC 电流环 PI 积分状态 | 控制器内部状态 | ❌ | 决定过渡态力矩响应 |

### 6.2 Actuator Model 的最小充分输入集

基于以上分析，Actuator Model 的输入应为：

$$\mathbf{x}_{act,t} = \Big[\underbrace{a_{t-H:t}}_{\text{指令历史}},\; \underbrace{\phi_{t-H:t}}_{\text{角度历史}},\; \underbrace{\dot{\phi}_{t-H:t}}_{\text{速度历史}},\; \underbrace{\tau_{fb,t-H:t}}_{\text{反馈力矩历史}},\; \underbrace{T_{motor,t}}_{\text{温度读数}}\Big]$$

- **历史窗口 $H$**：至少覆盖 2-3 个机械时间常数（$H \geq 2\tau_m / \Delta t \approx 10\text{-}30$ 步 at 200Hz）
- **温度 $T_{motor,t}$**：标量缓慢变化量，每 episode 采样一次即可
- **反馈力矩 $\tau_{fb}$**：虽然不精确（§4.1 讨论的 $K_t$ 漂移），但它提供了**电流环输出**的间接观测，帮助网络推断 FOC 内部状态

### 6.3 输出定义与可靠性分析

Actuator Model 的输出 $\hat{\tau}_{link}$ 表示**关节端实际力矩**，而非电机输出力矩 $\tau_{motor}$。两者差异来自传动系统：

$$\tau_{link} = \eta \cdot n \cdot \tau_{motor} - \tau_{fric}(\dot{\phi}, \phi) - \kappa \cdot \delta\phi_{elastic}$$

其中 $\eta$ 为传动效率，$n$ 为减速比（L25 四指 $N_{eq}\approx108$，且随构型变化，见 [[LinkerSysId]]），$\tau_{fric}$ 为 §5.4 的 Stribeck 摩擦，$\delta\phi_{elastic}$ 为弹性形变。

> [!warning] 力矩反馈的不可靠性
> SDK 通过 `torque.py` 读回的 $\tau_{measured} = K_t^{nominal} \cdot I_q^{measured}$：
> 1. $K_t^{nominal}$ 是出厂标定值，不随温度更新 → 系统性偏差（§4.2：+80°C 时 $-9.6\%$）
> 2. $I_q^{measured}$ 是 MCU ADC 采样的相电流经 Clarke/Park 变换（§2.1–2.2）得到 → 含量化噪声
> 3. 这是**电机轴**力矩，不是**关节端**力矩 → 缺失了全部传动损耗
> 
> **因此 $\tau_{measured}$ 不适合作为 RL 奖励信号或 World Model 的预测目标，但适合作为 Actuator Model 的输入特征**（提供电流环状态的间接观测）。Foundation 级论证见 [[Actuation#10.2 力矩反馈为何"能当输入、不能当目标"|Actuation §10.2]]。

### 6.4 可靠的真机 RL 观测信号选择

| 信号 | 来源 | 可靠性 | 延迟 | 推荐用途 |
|:--|:--|:-:|:-:|:--|
| 关节角度 $\phi_t$ | 编码器 (`angle.py`) | ⭐⭐⭐⭐ | ~15-20ms | **RL 核心观测 + WM 预测目标** |
| 关节角速度 $\dot{\phi}_t$ | 差分 (`speed.py`) | ⭐⭐⭐ | ~15-20ms + 噪声放大 | RL 观测（需滤波），WM 预测目标需谨慎 |
| 指尖触觉矩阵 $(12 \times 6)_{\times 5}$ | 薄膜阵列 (`force_sensor.py`) | ⭐⭐⭐⭐ | ~12.5ms (全手) | **RL 核心观测 + 接触状态判断** |
| 反馈力矩 $\tau_{fb}$ | 电流估算 (`torque.py`) | ⭐⭐ | ~15-20ms | Actuator Model 输入特征（**不推荐作为 RL reward 或 WM 预测目标**） |
| 电机温度 $T_{motor}$ | 温度传感器 (`temperature.py`) | ⭐⭐⭐⭐ | ~100ms | Actuator Model 显式输入，episode 级 context |
| 物体位姿 (真机) | 外部视觉/IMU | ⭐⭐-⭐⭐⭐ | ~30-100ms | 奖励计算（如果用视觉）|

**核心结论**：
- **RL 核心观测**应基于 $\phi_t$（关节角度）和触觉矩阵——这两者具有最高的物理可靠性（关节角度是关节侧传感器直接量，不经过 §3.6 的无感估计链）
- **World Model 预测目标**应为 $\hat{\phi}_{t+1}$（下一步关节角度），而非力矩——因为关节角度是直接可测量的 ground truth
- **力矩**仅作为 Actuator Model 的内部特征，不暴露给上层 RL 或 World Model 的损失函数
- **触觉传感器**提供指尖接触状态的高保真信号，对判断物体是否即将掉落至关重要（5 指各一个 12×6 taxel array，共 360 维原始触觉信号）

### 6.5 仿真 PD 与真机级联环的错位

主流仿真器把位置控制抽象成一个完美关节弹簧：

$$
τ_{sim}=K_p(q_{des}-q)+K_d(\dot q_{des}-\dot q).
$$

这个公式在 Isaac Gym / MuJoCo 中既便宜又稳定，因为仿真器假设算出的力矩会零延迟、无饱和地作用到刚体关节。真机则是 §2.6 的级联闭环：位置环输出速度参考，速度环输出电流参考，电流环/FOC 再通过 PWM 逆变器建立相电流。于是 $q_{des}\to\tau_{actual}$ 之间至少包含五类非理想性：

| 非理想性 | 真机表现 | 对仿真策略的破坏 | 本篇出处 |
|:--|:--|:--|:--|
| 电流建立延迟 | 指令到 $I_q$ 有带宽限制 | 高频 action 被低通滤掉 | §2.6、§5.2 |
| 反电动势 | 高速时电压余量不足 | 最大力矩随速度下降 | §5.1 |
| 温度漂移 | $R_s$ 上升、$K_t$ 下降 | 同一指令跨 episode 输出不同 | §四 |
| 丝杠/连杆摩擦 | stick-slip 与迟滞环 | 小力矩被死区吞噬，突破后跳变 | §5.4 |
| CAN 串行通信 | 多指指令先后到达 | 16 DOF "同步动作"变成扫描式动作 | [[Actuator2RigidDynamicsModel_gap]] |

这解释了为什么端到端 RL 在真实高减速比/丝杠灵巧手上通常仍选择输出位置目标或 action delta：底层位置伺服虽然黑箱，但能吸收一部分高频硬件非线性。相反，直接输出力矩会把搜索空间暴露给全部执行器细节，Sim-to-Real 风险急剧上升。

> [!tip] Actuator Model 设计结论
> 对 [[Final_WMTS#4.A Actuator Model：指令 → 关节力矩|WMTS Actuator Model]] 而言，目标不是替代 MCU 的 FOC，而是学习"仿真 PD 公式没有覆盖的那一段"端到端残差（即 [[Actuation#10.1 Actuator Net：学"仿真 PD 没覆盖的那段残差"|Actuator Net]] 路线）：
> $$
> \hat\tau_{link}=f_{act}(a_{t-H:t}, q_{t-H:t}, \dot q_{t-H:t}, \tau_{fb,t-H:t}, T_t, z_{\delta,t}).
> $$
> 其中 $z_{\delta,t}$ 编码 CAN 延迟/指间相位差，$T_t$ 编码热漂移，历史窗口编码摩擦迟滞与控制器内部状态。

---

## 回扣与承接

> [!example] 用 L25 的一根手指把本篇串一遍
> 策略在 $t$ 时刻给食指 `pip` 关节发一个位置目标（20–50 Hz，8-bit 归一化）。它经 CAN 到达指内 MCU 后走 §2.6 的三级级联：位置环算出速度参考，速度环算出 $I_{q,ref}$；电流环把它变成 $V_q$ 指令，经逆 Park、SVPWM 变成空心杯电机三相绕组上的 PWM（§2.1–2.3）。绕组里建立的相电流经 Clarke/Park 回到 d-q 系，产生 $\tau_{motor} = \frac32p\psi_mI_q = K_tI_q$（§2.4；空心杯 $L_d = L_q$，$I_d = 0$ 恰是 MTPA，§2.5）。若电机侧无编码器，$\theta_e$ 由 §三 的观测器 + PLL 估计——但手指在保持抓握时几乎零速，无感估计失效（§3.6），所以位置反馈来自**关节侧**传感器而非电机侧。这个 $\tau_{motor}$ 再经丝杠（导程 0.7 mm，$N_{eq}\approx108$；拇指多一级 17:1 折返减速箱、导程 0.6 mm，$N_{eq}\approx1424/1800$）与连杆折算到关节（[[LinkerSysId]]、[[Transmission2JointDynamics_gap]]），途中被 Stribeck 摩擦（§5.4）与弹性吃掉一部分。跑 20 s 后线圈到 60–80°C：$R_s$ 升 20–30%、$\psi_m$ 降 6–10%（§四），同一指令的关节力矩变小；若此时做高速 reorientation，还会撞上基速以上的转矩-转速包络（§5.1）与电流环带宽极限（§5.2）。SDK `torque.py` 读回的是 $K_t^{nominal}I_q$——电机轴、常温标定、不含传动损耗（§6.3），所以 WMTS 的 Actuator Model 把它当输入、把关节角度当目标，用历史窗口 + 温度学出这整段残差（§6.5）。

**下一篇去哪**：
- 指令怎样经 SDK 队列、CAN 帧、MCU 平滑到达电流环，延迟预算与 8-bit 量化 → [[Actuator2RigidDynamicsModel_gap]]
- 电机轴力矩怎样折算成关节力矩（惯量按 $N^2$、摩擦按 $N^1$、$N_{eq}(\theta)$ 随构型变）→ [[Transmission2JointDynamics_gap]]、[[LinkerSysId]]
- 折算结果落到仿真器参数（armature、frictionloss、solref）→ [[MuJoCo_Sim2Real_Params]]
- 回到电机物理本身（$K_t = K_e$、气隙剪应力律、空心杯电缸）→ [[电机]]；减速/丝杠自锁与反驱 → [[减速器]]

## 对开发与科研的启示

1. **不要把"去传感器化"当研究方向**。§3.6 的信噪比论证 + 空心杯零凸极性意味着 L25 这类手在零速工况下无感 FOC 原理上不可行；**这意味着下一步可以做**：量化 8-bit 关节反馈的死区对 RL 观测的影响（配合 [[Transmission2JointDynamics_gap]]），并评估是否需要从 SDK 读出 $I_q$ 作为附加观测。
2. **温度是 Actuator Model 的一等公民输入**。§四 给出的数字（$R_s$ +31%、$K_t$ −9.6% @ +80°C）远大于典型 domain randomization 的范围，且在 episode 内近似恒定——**这意味着下一步可以做**：用 `temperature.py` 采集 episode 级 $T_{motor}$，验证 Actuator Model 加/不加温度输入的 rollout 误差差异，作为 WMTS 世界模型"物理因果律约束"的一个具体实例。
3. **真机力矩包络是椭圆、不是矩形**。§5.1 的转矩-转速包络 + §5.2 的带宽限制**意味着下一步可以做**：在仿真里用 $\tau_{max}(\omega)$ 替换常数 action clip 做一次消融，看高速 reorientation 策略的 sim2real 成功率变化——这是几乎零成本的 gap 缩减实验。
4. **动作空间选位置/delta 不是妥协，而是利用了三级级联的低通特性**（§2.6、§6.5）。**这意味着下一步可以做**：把 Actuator Net（[[Actuation#10.1 Actuator Net：学"仿真 PD 没覆盖的那段残差"|Actuation §10.1]]）作为 WMTS Actuator Model 的基线实现，输入用 §6.2 的最小充分集，输出用关节角度而非力矩，在 L25 上跑一轮系统辨识数据采集。
