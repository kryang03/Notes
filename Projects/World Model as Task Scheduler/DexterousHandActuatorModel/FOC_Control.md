---
tags: [Dexterous_Manipulation, Motor_Control, Field_Oriented_Control, State_Estimation, Sim-to-Real]
source: Unified FOC & PMSM Modeling Lectures
date: 2026-04-15
related:
  - "[[Actuation]]"
  - "[[Actuator2RigidDynamicsModel_gap]]"
  - "[[ControlTheory]]"
  - "[[Final_WMTS]]"
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

![[Park Transform.png]]
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
    
    动力学方程中预设了 $L_q$ 为常数。但在灵巧操作需输出瞬态峰值力矩时，电机电流往往被推向极限（Overdrive），导致定子铁芯进入深度磁饱和，$L_q$ 会呈严重非线性下降。基于线性假设的 FOC 计算出的 $I_q$ 指令将无法产生期望的物理力矩，这种非线性是 Reality Gap 的重要组成部分。空心杯电机（Coreless Motor）无铁芯：**$L$ 不受磁饱和影响
    
- **热漂移的脆弱性**
    
    定子电阻 $R_s$ 会随连续高负载作业发热而产生高达 50% 的漂移。如果在观测器中固化 $\hat{R}$，电压前馈补偿的偏差将不可逆地转化为角度估算误差，并最终表现为扭矩追踪精度的稳态下降。

---

## 四、 温度对电机模型参数的系统性影响

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

**对 Luenberger Observer 的致命影响**：观测器模型中使用固定 $\hat{R}_s = R_s(T_0)$，而真实 $R_s$ 持续增大。由 §三.3 的观测器方程：

$$L\frac{d\hat{I}}{dt} = V - \hat{R}_s \hat{I} - \hat{e} + K_p(I - \hat{I}) + K_i\int(I - \hat{I})dt$$

当 $\hat{R}_s < R_s^{real}$ 时，观测器对 $RI$ 项的补偿不足，缺失的电压降 $\Delta R \cdot I$ 被 PI 积分器错误地吸收进 $\hat{e}$ 中，导致反电动势估计产生等效的偏置误差 $\delta e \approx \Delta R_s \cdot I$。经由 PLL 提取角度时，该偏置引入稳态角度误差：

$$\delta \theta_e \approx \frac{\Delta R_s \cdot I_q}{K_e \omega_e}$$

**关键特征**：此误差在低速时被 $\omega_e$ 在分母放大——恰好是灵巧手在接触切换（grasp-regrasp）时最需要精确力矩控制的时刻。

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

**Sim-to-Real 的核心矛盾**：仿真中 $K_t, R_s, K_e$ 均为标定时的常数。真机中这些参数每分钟都在漂移。如果 World Model 的 Actuator Model 不捕捉这种漂移，World Model 的预测将在长 horizon rollout 中产生累积偏差。

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

> [!abstract] 核心场景
> 灵巧手执行快速转笔（pen spinning）或高速 in-hand reorientation 时，电机转速可达数千 RPM，产生一系列在低速任务中不显著但在高速下主导系统行为的物理效应。

### 5.1 反电动势电压天花板与弱磁区域

由 §二.2 的 d-q 轴方程，稳态下 q 轴电压方程为：

$$V_q = R_s I_q + \omega_e L_d I_d + \omega_e \psi_m$$

电机可用的总电压受 DC 母线电压 $V_{dc}$ 约束：

$$V_d^2 + V_q^2 \leq \left(\frac{V_{dc}}{\sqrt{3}}\right)^2$$

当 $\omega_e$ 升高，反电动势项 $\omega_e \psi_m$ 线性增长。定义**基速**（Base Speed）为 $I_d = 0$ 时电压恰好饱和的转速：

$$\omega_{base} = \frac{V_{dc}/\sqrt{3} - R_s I_{q,rated}}{{\psi_m}}$$

**超过基速后**：
- $\omega_e \psi_m > V_{dc}/\sqrt{3}$，此时即使 $I_q = 0$ 也无法满足电压约束
- FOC 被迫注入**负** $I_d$（弱磁电流），人为削弱永磁体的等效磁通以降低反电动势
- 代价：(1) $I_d$ 占用了电流矢量的一部分幅值空间，$I_q$（力矩电流）的上限被压缩；(2) 磁链被人为削弱进一步降低 $K_t$
- **结论**：在高速 reorientation 中，电机的**力矩能力随转速上升而非线性下降**。这是一个经典的转矩-转速包络（Torque-Speed Envelope）约束：

$$\text{恒转矩区 } (\omega < \omega_{base}): \quad T_{max} = K_t I_{q,max}$$
$$\text{恒功率区 } (\omega > \omega_{base}): \quad T_{max}(\omega) \approx \frac{P_{max}}{\omega} = \frac{K_t I_{q,max} \omega_{base}}{\omega}$$

> [!tip] 对 RL 策略的启示
> 当策略尝试在高速旋转中施加大力矩（如急停或方向急变），真机的力矩响应将远低于仿真预期。这种**速度相关的力矩饱和**是 Sim-to-Real 最大的未建模动力学之一。在仿真中 action clipping 是一个硬矩形约束，而真机的约束是一个**椭圆形的速度-力矩包络**。

### 5.2 电流环带宽与力矩追踪延迟

FOC 电流环的闭环带宽决定了 $I_q$ 能以多快的速度跟踪指令变化。典型的 PI 电流控制器的闭环带宽为：

$$f_{bw} \approx \frac{1}{2\pi} \cdot \frac{K_{p,i}}{L}$$

对于空心杯电机（$L \sim 10\text{-}100\,\mu H$），电流环带宽可达 1-5 kHz。但在高速 reorientation 场景下：

- **交叉耦合项 $\omega_e L_q I_q$ 和 $\omega_e L_d I_d$ 急剧增大**：这些项是 d-q 轴之间的扰动，必须由前馈解耦补偿。如果补偿不完美（如 $L$ 和 $\omega_e$ 存在估计误差），电流环有效带宽被拉低
- **采样延迟的相对影响增大**：MCU 的 ADC 采样和 PWM 更新引入固有 1-1.5 个 PWM 周期的延迟。在 20kHz PWM 下约 50-75μs。当力矩指令在 1ms 内剧烈变化（200Hz control → 5ms period），延迟占比尚可接受；但如果策略频率提升到 1kHz（如某些高频力控应用），延迟占比达 5-7.5%，足以引起力矩振荡
- **数字量化效应**：PWM 分辨率有限（如 12-bit timer at 20kHz → ~50ns 分辨率），在需要极精细力矩调节时（如 sub-Newton 级指尖力），量化噪声不可忽略

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

**对 Actuator Model 的要求**：必须通过历史窗口 $[\dot{\phi}_{t-H:t}]$ 隐式学习当前处于 Stribeck 曲线的哪个区域。单一时刻的 $(\phi_t, \dot{\phi}_t)$ 无法区分"即将突破静摩擦"和"处于平稳滑动摩擦"。

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
- **反馈力矩 $\tau_{fb}$**：虽然不精确（§四.1 讨论的 $K_t$ 漂移），但它提供了**电流环输出**的间接观测，帮助网络推断 FOC 内部状态

### 6.3 输出定义与可靠性分析

Actuator Model 的输出 $\hat{\tau}_{link}$ 表示**关节端实际力矩**，而非电机输出力矩 $\tau_{motor}$。两者差异来自传动系统：

$$\tau_{link} = \eta \cdot n \cdot \tau_{motor} - \tau_{fric}(\dot{\phi}, \phi) - \kappa \cdot \delta\phi_{elastic}$$

其中 $\eta$ 为传动效率，$n$ 为减速比，$\tau_{fric}$ 为 §5.4 的 Stribeck 摩擦，$\delta\phi_{elastic}$ 为弹性形变。

> [!warning] 力矩反馈的不可靠性
> SDK 通过 `torque.py` 读回的 $\tau_{measured} = K_t^{nominal} \cdot I_q^{measured}$：
> 1. $K_t^{nominal}$ 是出厂标定值，不随温度更新 → 系统性偏差
> 2. $I_q^{measured}$ 是 MCU ADC 采样的相电流经 Park 变换得到 → 含量化噪声
> 3. 这是**电机轴**力矩，不是**关节端**力矩 → 缺失了全部传动损耗
> 
> **因此 $\tau_{measured}$ 不适合作为 RL 奖励信号或 World Model 的预测目标，但适合作为 Actuator Model 的输入特征**（提供电流环状态的间接观测）。

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
- **RL 核心观测**应基于 $\phi_t$（关节角度）和触觉矩阵——这两者具有最高的物理可靠性
- **World Model 预测目标**应为 $\hat{\phi}_{t+1}$（下一步关节角度），而非力矩——因为关节角度是直接可测量的 ground truth
- **力矩**仅作为 Actuator Model 的内部特征，不暴露给上层 RL 或 World Model 的损失函数
- **触觉传感器**提供指尖接触状态的高保真信号，对判断物体是否即将掉落至关重要（5 指各一个 12×6 taxel array，共 360 维原始触觉信号）

### 6.5 仿真 PD 与真机级联环的错位

主流仿真器把位置控制抽象成一个完美关节弹簧：

$$
τ_{sim}=K_p(q_{des}-q)+K_d(\dot q_{des}-\dot q).
$$

这个公式在 Isaac Gym / MuJoCo 中既便宜又稳定，因为仿真器假设算出的力矩会零延迟、无饱和地作用到刚体关节。真机则是级联闭环：位置环输出速度参考，速度环输出电流参考，电流环/FOC 再通过 PWM 逆变器建立相电流。于是 $q_{des}\to\tau_{actual}$ 之间至少包含五类非理想性：

| 非理想性 | 真机表现 | 对仿真策略的破坏 |
|:--|:--|:--|
| 电流建立延迟 | 指令到 $I_q$ 有带宽限制 | 高频 action 被低通滤掉 |
| 反电动势 | 高速时电压余量不足 | 最大力矩随速度下降 |
| 温度漂移 | $R_s$ 上升、$K_t$ 下降 | 同一指令跨 episode 输出不同 |
| 丝杠/连杆摩擦 | stick-slip 与迟滞环 | 小力矩被死区吞噬，突破后跳变 |
| CAN 串行通信 | 多指指令先后到达 | 16 DOF “同步动作”变成扫描式动作 |

这解释了为什么端到端 RL 在真实高减速比/丝杠灵巧手上通常仍选择输出位置目标或 action delta：底层位置伺服虽然黑箱，但能吸收一部分高频硬件非线性。相反，直接输出力矩会把搜索空间暴露给全部执行器细节，Sim-to-Real 风险急剧上升。

> [!tip] Actuator Model 设计结论
> 对 [[Final_WMTS#4.A Actuator Model：指令 → 关节力矩|WMTS Actuator Model]] 而言，目标不是替代 MCU 的 FOC，而是学习“仿真 PD 公式没有覆盖的那一段”端到端残差：
> $$
> \hat\tau_{link}=f_{act}(a_{t-H:t}, q_{t-H:t}, \dot q_{t-H:t}, \tau_{fb,t-H:t}, T_t, z_{\delta,t}).
> $$
> 其中 $z_{\delta,t}$ 编码 CAN 延迟/指间相位差，$T_t$ 编码热漂移，历史窗口编码摩擦迟滞与控制器内部状态。