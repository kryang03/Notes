---
tags: [Dexterous_Manipulation, Motor_Control, Field_Oriented_Control, State_Estimation, Sim-to-Real]
source: Unified FOC & PMSM Modeling Lectures
date: 2026-04-15
---

# 永磁同步电机(PMSM)与无感矢量控制(Sensorless FOC)第一性原理推导

## 一、 核心思想与领域定位 (Executive Summary)

在底层硬件驱动体系中，磁场定向控制（Field Oriented Control, FOC）通过空间坐标变换，将严重非线性、强耦合的三相交流电机动力学降维解耦为线性独立的类直流控制模型。基于内部电气模型的 Luenberger Observer 则打破了对高成本物理编码器的依赖，实现了无感（Sensorless）的转子状态估计。

在灵巧操作（Dexterous Manipulation）与强化学习（RL）的交叉语境中，理解这一底层控制逻辑至关重要。高层 Policy 网络（如 PPO）输出的通常是理想的关节力矩（Desired Torque）。然而，底层驱动的非线性、电气延时（PWM 滤波）、反电动势（Back-EMF）以及观测器在极低速下的崩溃边界，是产生 Sim-to-Real Gap 的核心根源。彻底打穿从基尔霍夫定律到力矩输出的物理链路，是构建高保真 Actuator 动力学模型的前提。

---

## 二、 物理本源：定子方程与坐标系降维

为了实现类似直流电机的解耦控制，必须剥离三相交流系统的时变与耦合特性。我们将从最基础的电磁学物理定律出发构建系统动态方程。

### 1. 静止坐标系下的三相电气方程
在定子三相静止坐标系 (a, b, c) 下，根据基尔霍夫电压定律 (KVL)，施加在电感线圈上的电压 $V$ 被消耗在三个部分：电阻压降发热、电感抵抗电流变化的感应电压、以及转子永磁体旋转切割磁感线产生的反电动势（Back-EMF，用 $e$ 表示）。

假设电机无中性点接地，满足 $I_a + I_b + I_c = 0$。为了消除冗余自由度，引入 **Clarke Transform**，将三维静止坐标系投影到正交的二维静止坐标系 $(\alpha, \beta)$ 中：
$$\begin{bmatrix} I_\alpha \\ I_\beta \end{bmatrix} = \frac{2}{3} \begin{bmatrix} 1 & -\frac{1}{2} & -\frac{1}{2} \\ 0 & \frac{\sqrt{3}}{2} & -\frac{\sqrt{3}}{2} \end{bmatrix} \begin{bmatrix} I_a \\ I_b \\ I_c \end{bmatrix}$$
由此，我们得到电机在 $(\alpha, \beta)$ 坐标系下的电气动态方程：
$$\begin{bmatrix} V_\alpha \\ V_\beta \end{bmatrix} = R_s \begin{bmatrix} I_\alpha \\ I_\beta \end{bmatrix} + L \frac{d}{dt} \begin{bmatrix} I_\alpha \\ I_\beta \end{bmatrix} + \begin{bmatrix} e_\alpha \\ e_\beta \end{bmatrix}$$

### 2. 旋转坐标系与转矩生成
静止坐标系下的电流仍是随时间交变的。引入转子电角度 $\theta_e$，利用 **Park Transform** 将 $(\alpha, \beta)$ 旋转对齐到转子磁极上，得到直轴 (d-axis) 与交轴 (q-axis)：
$$\begin{bmatrix} I_d \\ I_q \end{bmatrix} = \begin{bmatrix} \cos\theta_e & \sin\theta_e \\ -\sin\theta_e & \cos\theta_e \end{bmatrix} \begin{bmatrix} I_\alpha \\ I_\beta \end{bmatrix}$$

此时，d-q 轴的动态方程（考虑交叉耦合）展开为：
$$\begin{cases} V_d = R_s I_d + L_d \frac{d I_d}{dt} - \omega_e L_q I_q \\ V_q = R_s I_q + L_q \frac{d I_q}{dt} + \omega_e L_d I_d + \omega_e \psi_m \end{cases}$$
* $R_s$: 定子电阻。
* $L_d, L_q$: 直轴与交轴电感。
* $\omega_e \psi_m$: 永磁体切割定子产生的反电动势（$\psi_m$ 为磁链）。

系统最终输出的机械转矩 $T_e$ 为：
$$T_e = \frac{3}{2} p \left[ \psi_m I_q + (L_d - L_q)I_d I_q \right]$$
*(p 为极对数)*。在最大转矩电流比 (MTPA) 策略下，我们强制令 $I_d = 0$（不产生退磁或助磁）。此时对于表贴式电机 ($L_d = L_q$)，力矩公式极度坍缩：
$$T_e = \left( \frac{3}{2} p \psi_m \right) I_q = K_t I_q$$
**结论：** FOC 的本质是将观察系转移到转子上，使得控制 $I_q$ 即等效于控制直流电机的力矩。

---

## 三、 转子密码：反电动势与 Luenberger 观测器

在无感 (Sensorless) 控制中，获取电角度 $\theta_e$ 是执行 Park 变换的前提。

### 1. 反电动势的几何学解释
根据法拉第电磁感应定律 $e = -\frac{d\psi}{dt}$，假设转子磁链在 $(\alpha, \beta)$ 轴上的投影为 $\psi_\alpha = \psi_f \cos\theta_e$ 和 $\psi_\beta = \psi_f \sin\theta_e$。对其求导并代入链式法则 $\frac{d\theta_e}{dt} = \omega_e$：
$$\begin{cases} e_\alpha = -K_e \omega_e \sin\theta_e \\ e_\beta = K_e \omega_e \cos\theta_e \end{cases}$$
反电动势 $e_{\alpha\beta}$ 完美编码了角度信息 $\theta_e$。

### 2. 为什么不能直接代数求解？
由 KVL 理论上可直接算得：$e = V - RI - L \frac{di}{dt}$。
但在工程实现中：电流 $I$ 包含高频白噪声。对其求导 $\frac{di}{dt}$ 会导致噪声被微分算子成百上千倍放大，完全淹没真实信号。同时，发热引起的 $R$ 漂移会让代数方程直接失效。

### 3. Luenberger Observer 的闭环逻辑
我们在软件中构建一个“虚拟电机”，输入同样的电压 $V$，并使用 PI 反馈补偿来强迫虚拟电流 $\hat{I}$ 逼近真实电流 $I$：
$$L \frac{d\hat{I}}{dt} = V - \hat{R}\hat{I} - \hat{e} + K_p(I - \hat{I}) + K_i \int (I - \hat{I}) dt$$
定义误差 $\tilde{I} = I - \hat{I}$，当 PI 控制器促使 $\tilde{I} \to 0$ 且微分项为 0 时：
$$\hat{e} \to e = - K_i \int \tilde{I} dt$$
**原理本质：** 通过强迫两套系统的状态对齐，我们用极度稳定的积分操作，替代了极度不稳定的微分操作，把未知的扰动（真实的 $e$）“挤压”到了 PI 积分器的输出中。

### 4. 角度提取：锁相环 (PLL)
不推荐直接使用 $\theta_e = \arctan(-\hat{e}_\alpha / \hat{e}_\beta)$，因为除法运算对过零点极度敏感。
工程上利用和差化积公式构建二阶 PLL：
$$\epsilon = -\hat{e}_\alpha \cos\hat{\theta}_e - \hat{e}_\beta \sin\hat{\theta}_e = K_e \omega_e \sin(\theta_e - \hat{\theta}_e)$$
当误差极小时，$\sin(\theta_e - \hat{\theta}_e) \approx \theta_e - \hat{\theta}_e$。将 $\epsilon$ 送入 PI 控制器得到转速 $\hat{\omega}_e$，再对其积分获得极其平滑的角度 $\hat{\theta}_e$。

---
- **磁饱和与恒定电感的灾难性假设**
    
    动力学方程中预设了 $L_q$ 为常数。但在灵巧操作需输出瞬态峰值力矩时，电机电流往往被推向极限（Overdrive），导致定子铁芯进入深度磁饱和，$L_q$ 会呈严重非线性下降。基于线性假设的 FOC 计算出的 $I_q$ 指令将无法产生期望的物理力矩，这种非线性是 Reality Gap 的重要组成部分。
    
- **热漂移的脆弱性**
    
    定子电阻 $R_s$ 会随连续高负载作业发热而产生高达 50% 的漂移。如果在观测器中固化 $\hat{R}$，电压前馈补偿的偏差将不可逆地转化为角度估算误差，并最终表现为扭矩追踪精度的稳态下降。