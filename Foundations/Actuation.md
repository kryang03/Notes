---
tags:
    - foundation
    - actuation
    - motor-control
    - dexterous-manipulation
    - sim-to-real
aliases:
    - 执行器
    - 执行器与驱动
    - 驱动系统
    - Actuation
    - 电机控制
    - Motor Control
    - FOC
    - Field-Oriented Control
    - 力矩传递链
    - Actuator Model
created: 2026-07-12
related:
    - "[[ControlTheory]]"
    - "[[Dynamics]]"
    - "[[ReinforcementLearning]]"
    - "[[WorldModels]]"
    - "[[ContactMechanics]]"
    - "[[SignalProcessing]]"
---

# 灵巧操作执行器与驱动系统：从电磁力矩到关节输出的 Sim-to-Real 链路

# Actuation & Drive Systems for Dexterous Manipulation: From Electromagnetic Torque to Joint Output Across the Sim-to-Real Chain

> [!tip] 相关领域
> - [[ControlTheory]] — 电流/速度/位置串级环、状态观测器 (Luenberger)、相位裕度、阻抗与反驱动性都是控制理论的直接应用；本讲是 [[ControlTheory#1. 古典控制最小语法：后续一切的前置语言|古典控制]]中"电流环=一阶系统、热漂移=时变增益"那句话的完整展开
> - [[Dynamics]] — 操作器方程 $M\ddot q+C\dot q+N=\tau$ 右端那个 $\tau$ 就是本讲的**输出**；腱耦合矩阵 $P$（[[Dynamics#8.1 腱网络运动学：耦合矩阵 $P$|§8.1]]）与本讲的传动雅可比同源；神经动力学（[[Dynamics#9. 适配层：可微物理与神经动力学|§9]]）与本讲的 actuator net 是同一残差思想
> - [[ReinforcementLearning]] — 仿真"关节虚拟力矩"假设的失效，正是 [[ReinforcementLearning#9.1 先分类，再治疗：MDP 四要素 gap 诊断|Sim-to-Real 的 Action/Transition gap]]的**物理来源**；本讲 §9 的 DR 参数直接喂给 RL 的域随机化
> - [[ContactMechanics]] — 反驱动性 (Backdrivability) 决定了被动柔顺，是力控与安全接触的物理前提
> - [[SignalProcessing]] — 编码器、电流采样、差分测速与卡尔曼滤波是执行器的感知前端；无感观测器与 [[SignalProcessing#5.2 演进脉络：KF → EKF → UKF → PF → 因子图|KF/EKF]]同源
>
> **贯穿母题**：**一次高速转笔中的一个力矩指令 (one torque command in high-speed pen-spinning)**。策略在仿真里对某关节输出一个峰值力矩、命令它急停反向；同一个指令在真机里要依次穿过 FOC 电流环、空心杯电机、行星滚柱丝杠、PIP-DIP 耦合连杆才到达指尖。这一路上：电流环带宽限制其上升率、反电动势天花板削掉高速段的顶、$K_t(T)$ 热衰减打折、Stribeck 静摩擦吞掉过零点的一段、背隙制造死区、连杆弹性让它滞后——**最终到达指尖的力矩与仿真预期差之千里。全讲每引入一个环节，都回到这个指令：这一步，真机能兑现仿真承诺的多少？**

## 0. 母题与理论大厦构建路线：从电磁力矩到关节输出

> [!abstract] 为什么用"一个力矩指令的旅程"做母题？
> 主流物理仿真器（IsaacGym / MuJoCo / Isaac Lab）里，RL 策略输出的 action 被解释为**关节力矩** $\tau_{sim}$（或经固定 PD 转成力矩），**零延迟、无饱和、无损耗地**施加在理想刚体关节上：
> $$M(q)\ddot q + C(q,\dot q)\dot q + g(q) = \tau_{sim}.$$
> 这条方程把"从电信号到关节力矩"的全部物理**一笔抹去**。真机里，同一个 $\tau$ 是一条串级闭环的终点：位置环→速度环→电流环/FOC→PWM 逆变器→相电流→电磁力矩→减速器→传动→关节。于是仿真里的一个标量 $\tau_{sim}$，在真机里对应一整套非线性、时变、带延迟、受温度和转速调制的映射。
>
> **机械差异**（背隙、Stribeck 摩擦、弹性形变、传动比误差、reflected inertia）与**电气差异**（电流环带宽、反电动势天花板、力矩饱和、热漂移、齿槽转矩）共同构成 [[sim2real|执行器级的 Sim-to-Real gap]]。本讲就是要把这条被仿真抹去的链路一节一节重建出来，并回答：**哪些环节可以忽略、哪些必须建模、哪些只能用数据补。**

执行器理论在灵巧操作中的主线，是把"策略想要的关节力矩"变成"真机在延迟、饱和、摩擦、温漂下**实际兑现**的关节力矩"。七层大厦，每层回答一个更尖锐的问题：

| 层级 | 关键问题 | 理论工具 | 转笔母题的映射 | 讲稿位置 |
|:--|:--|:--|:--|:--|
| **电机层** | 电流如何变成力矩？ | 电磁方程、$K_t/K_e/K_m$、直流统一模型 | $I_q \to \tau$ 的物理起点 | §1 |
| **驱动层** | 三相交流怎么当直流控？ | FOC、Clarke/Park、MTPA、Luenberger 观测器 | 底层 MCU 如何兑现 $\tau$ 指令 | §2–§4 |
| **电气极限层** | 高速时力矩为何"软"？ | 反电动势天花板、力矩-转速包络、弱磁、电流环带宽 | 急停指令被削顶 | §5 |
| **热漂移层** | 为何跑久了力矩变小？ | $R_s(T)/\psi_m(T)/K_t(T)$、热失控环路、时间尺度 | 连续转笔后力矩打折 | §6 |
| **机械层** | 力矩怎么从电机到关节？ | 传动方案、减速器、背隙、Stribeck、reflected inertia、扭转刚度 | $\tau$ 穿过丝杠+连杆的损耗畸变 | §7–§8 |
| **迁移层** | 仿真假设错在哪、怎么补？ | 力矩传递链模型、actuator net、DR、JTS 力矩闭环 | 关节虚拟力矩假设的失效与修复 | §9–§10 |
| **接口层** | 指令真机上怎么落地？ | MCU/STM32/CAN、归一化、延迟相位差、观测可信度 | 16 DOF 串行落地的相位差 | §11 |

> [!important] Foundation 级判断标准
> 任何执行器方案都必须说明三件事：**电流如何映射为力矩（含其线性度）、力矩上限如何随转速/温度变化、传动链吞掉了多少并引入了哪些非线性。** 一句话——**电流 ≠ 关节力矩**。

> [!note] 本讲在知识图谱中的位置
> ```
> [[ControlTheory]] ──串级环/观测器/相位裕度──> 【驱动层设计工具】     【迁移层 actuator net】──残差──> [[ReinforcementLearning|残差 RL/RMA]]
> [[Dynamics]] ──操作器方程的 τ / 腱耦合 P──> 【输出接口】            【机械层 反驱动性】──被动柔顺──> [[ContactMechanics|安全接触]]
> [[SignalProcessing]] ──编码器/电流采样/KF──> 【感知前端】            【迁移层 gap 诊断】──Action/Transition──> [[ReinforcementLearning|Sim-to-Real]]
> ```

---

## 1. 电机层：从电磁学到统一直流模型

> [!tip] 本节四拍
> **直觉**（电机把电流变成力矩，$\tau=K_tI$ 是力控的物理基础）→ **推导**（电气方程 + 机械方程 + $K_t=K_e$）→ **对比**（有刷/BLDC/无框/空心杯/舵机的 Sim-to-Real 友好度）→ **联系**（$K_t$ 的线性度决定 §9 的 gap、$K_m$ 决定选型、惯量决定 §7 的 reflected inertia）。详见项目笔记 [[电机]]。

### 1.1 直流电机统一模型：一切力控的起点

所有直流电机（有刷/无刷）的核心电气-机械耦合可用两条方程描述：

$$\underbrace{V = L\frac{dI}{dt} + RI + K_e\omega}_{\text{电气方程 (KVL)}}, \qquad \underbrace{J\dot\omega = K_tI - b\omega - \tau_{load}}_{\text{机械方程 (Newton)}}$$

| 符号 | 含义 | 单位 |
|:--|:--|:--|
| $V,I$ | 端电压、电枢电流 | V, A |
| $L,R$ | 绕组电感、电阻 | H, Ω |
| $K_e$ | 反电动势常数 (Back-EMF) | V·s/rad |
| $K_t$ | 力矩常数 (Torque constant) | Nm/A |
| $J,b$ | 转子惯量、粘滞摩擦系数 | kg·m², Nm·s/rad |

**关键恒等式**：国际单位制下理想电机 $K_t = K_e$——这意味着**电流直接对应力矩** $\tau_e = K_tI$，是"用电流控力"的物理根基。电气方程是一阶系统 $\frac{I}{V}=\frac{1/R}{\tau_e s+1}$，时间常数 $\tau_e = L/R$（[[ControlTheory#1.1 三种等价视角与系统阶次|ControlTheory §1.1]] 里"1 阶=电流环"正是此处）。

> [!tip] 电机常数 $K_m = K_t/\sqrt{R}$
> 单位 Nm/$\sqrt{W}$，衡量"单位铜损下能产生多少力矩"，是横向比较不同尺寸电机力矩效率的归一化指标。灵巧手关节空间 < 20 mm，$K_m$ 是选型的核心判据。

### 1.2 电机类型谱系与 Sim-to-Real 友好度

灵巧手对电机的要求极端苛刻：极小体积内高扭矩密度、低惯量、高带宽、精确力控。五类主流方案的**力控友好度 = 力矩线性度 × 低齿槽 × 低惯量 × 高反驱动**：

| 电机类型 | 力矩线性度 | 响应延迟 $\tau_e$ | 齿槽转矩 | 惯量 | Sim-to-Real 友好度 |
|:--|:--|:--|:--|:--|:--|
| 有刷直流 | 高 ($\tau=K_tI$) | 中 (1–5 ms) | 无 | 中 | ⭐⭐⭐ |
| **BLDC (FOC)** | 极高 | 极低 (0.5–2 ms) | 有 (可补偿) | 中 | ⭐⭐⭐⭐ |
| **无框力矩电机** | 极高 | 极低 | 低 | 低 | ⭐⭐⭐⭐⭐ |
| **空心杯电机** | 极高 | 极低 (<0.1 ms) | **零** | **极低** | ⭐⭐⭐⭐ |
| RC 舵机 | 低 (齿轮非线性) | 高 | 有 | 高 | ⭐ |

- **有刷直流**：定子永磁 + 转子绕组 + 电刷换向。控制最简（H 桥切电流方向），但电刷磨损限制寿命。
- **BLDC / PMSM**：线圈定子 + 永磁转子 + 电子换向。叠层硅钢片抑制涡流。**无框力矩电机**与**空心杯电机**都是 BLDC 的特化。12N14P 是灵巧手/无人机最常见极槽配置——分数槽集中绕组带来高绕组系数（≈0.933）与低齿槽转矩（$\mathrm{lcm}(12,14)=84$），并非为了"避免死锁"（旧说法已在 [[电机#2. 无刷直流电机 (BLDC Motor)|电机 §2.1]] 修正）。
- **空心杯电机**：彻底取消铁芯 → 零齿槽、零铁损、惯量最小、$L$ 极小（微亨级，不受磁饱和影响）。代价：热容极小（$\tau_{th}\approx5$–30 s），功率受限。
- **无框力矩电机**：省去外壳/轴承/转轴，转子即关节轴——极致紧凑、零传动背隙、高反驱动，是高端灵巧手首选（常配谐波减速器）。

> [!note] 步进电机 (Stepper) 为何不进研究级灵巧手（源自机电选型培训）
> 步进电机靠多相绕组按固定步距角逐步吸合，**开环即可定位**（无需编码器），工业自动化里因此便宜好用。但它有两个致命短板：**① 失步 (step loss)**——负载超过保持力矩时悄悄丢步且开环无从察觉；**② 力矩随频率陡降**（力矩-频率特性曲线），高速几乎无力矩。灵巧操作需要连续、可测、高带宽的力控，故用**闭环 FOC 伺服**（§2–§4）而非步进。步进 vs 伺服的本质差异，正是"开环步进 vs 闭环连续力矩"——这条界线定义了 §2 之后的全部内容。

> [!warning] 舵机为何几乎不用于研究级灵巧手
> RC 舵机是"电机+多级齿轮+电位器+PWM 位控板"的闭环黑箱，齿轮组非线性、带宽低、力矩线性度差——直接把 §9 的所有 gap 叠满。研究级灵巧手用工业 FOC 驱动 + 高分辨率编码器，或无框力矩电机直驱。

---

## 2. 驱动层：FOC 磁场定向控制——把三相交流当直流控

> [!tip] 本节四拍
> **直觉**（三相交流强耦合非线性，要像直流一样"一个旋钮控力矩"）→ **推导**（Clarke → Park → d-q 方程 → MTPA → $\tau=K_tI_q$）→ **对比**（六步方波 vs FOC 正弦）→ **联系**（$I_q$ 就是 §1 的 $I$，FOC 是把电机降维成 §1 统一模型的手段）。第一性原理推导详见 [[FOC_Control]]。

> [!note] 教科书参考
> FOC 的第一性原理与本项目电机的工程细节见项目笔记 [[FOC_Control]]；系统的学习笔记另见 [[FOC控制学习笔记.pdf|《FOC 控制学习笔记》]]（`Books/`，涵盖 Clarke/Park、电流环整定、SVPWM、无感观测的推导与实操），可与本节 §2–§5 对照。本节只提炼"为什么能把三相交流当直流控"这条主干，细节不再重复。

### 2.1 坐标降维：Clarke 与 Park 变换

三相静止坐标 $(a,b,c)$ 下，KVL 给出 $V = RI + L\frac{dI}{dt} + e$（$e$ 为反电动势）。无中性点接地时 $I_a+I_b+I_c=0$，冗余。两步变换消除耦合与时变：

**Clarke（3→2，静止正交）**：
$$\begin{bmatrix} I_\alpha \\ I_\beta \end{bmatrix} = \frac{2}{3}\begin{bmatrix} 1 & -\frac12 & -\frac12 \\ 0 & \frac{\sqrt3}{2} & -\frac{\sqrt3}{2}\end{bmatrix}\begin{bmatrix} I_a \\ I_b \\ I_c\end{bmatrix}$$

**Park（旋转对齐转子磁极，$\alpha\beta \to dq$）**：
$$\begin{bmatrix} I_d \\ I_q \end{bmatrix} = \begin{bmatrix}\cos\theta_e & \sin\theta_e \\ -\sin\theta_e & \cos\theta_e\end{bmatrix}\begin{bmatrix} I_\alpha \\ I_\beta\end{bmatrix}$$

d-q 坐标下动态方程（含交叉耦合）：
$$\begin{cases} V_d = R_sI_d + L_d\dot I_d - \omega_e L_qI_q \\ V_q = R_sI_q + L_q\dot I_q + \omega_e L_dI_d + \omega_e\psi_m \end{cases}$$

### 2.2 力矩生成与 MTPA

> [!example] 由功率平衡推出转矩方程、$K_t=\tfrac32K_e$（幅值不变约定）与直流电机 $K_t=K_e$ 的对账、以及 $I_d=0$ 只对表贴式是 MTPA 的证明，见 [[FOC_Control#2.4 转矩方程：$T_e = \frac32 p\,\psi_m I_q$ 与直流电机 $K_t = K_e$ 的对账|FOC §2.4]]。

机械转矩：
$$T_e = \frac{3}{2}p\left[\psi_mI_q + (L_d-L_q)I_dI_q\right]$$

**MTPA（最大转矩电流比）**策略令 $I_d=0$（不助磁不退磁）。对表贴式电机 $L_d=L_q$，力矩公式坍缩为：
$$\boxed{T_e = \left(\frac{3}{2}p\psi_m\right)I_q = K_tI_q}$$

**这就是 FOC 的本质**：把观察系搬到转子上，控制 $I_q$ 即等效于控制一台直流电机的力矩——§1 的统一模型由此对 BLDC 成立。相比六步方波换向，FOC 给出连续正弦电流、零速满转矩、最小铜损、极低转矩脉动，是灵巧手 BLDC 关节的标准方案。

> [!note] $I_d,I_q$ 的物理分工
> $I_d$（直轴/磁通分量）改变等效磁场强度；$I_q$（交轴/力矩分量）产生力矩。正常工况 $I_d=0$，全部电流用于产力矩；高速时注入负 $I_d$ 弱磁（§5.2）。

> [!note] SVPWM：把电压指令"合成"出来——兼谈 $V_{dc}/\sqrt3$ 的由来
> FOC 电流环（含 §5.2 解耦）算出的是 d-q 电压指令 $V_d^{cmd},V_q^{cmd}$；经**逆 Park** 变回静止系得目标电压矢量 $\vec V_{ref}=(V_\alpha,V_\beta)$。但三相逆变器只有 **8 种开关状态**（6 个非零基本矢量 $\vec V_1\!\sim\!\vec V_6$ 指向正六边形 6 个顶点 + 2 个零矢量 $\vec V_0,\vec V_7$），无法直接输出任意 $\vec V_{ref}$。**空间矢量调制 (SVPWM)** 的思路：在一个 PWM 周期 $T_s$ 内，用相邻两个基本矢量按**时间加权平均**合成目标——设 $\vec V_{ref}$ 落在 $\vec V_1,\vec V_2$ 之间，令
> $$\vec V_{ref}\,T_s = \vec V_1 t_1 + \vec V_2 t_2 + \vec V_0 t_0,\qquad t_1+t_2+t_0=T_s,$$
> 其中 $t_1,t_2$（s）是两个非零矢量的作用时间、$t_0$（s）是零矢量补足时间。解这个二维矢量方程即得占空比。**关键结论**：SVPWM 能合成的最大幅值矢量是正六边形**内切圆**半径 $=\frac{2}{\sqrt3}\cdot\frac{V_{dc}}{2}=\frac{V_{dc}}{\sqrt3}$，比正弦 PWM（内切圆 $=V_{dc}/2$）**高约 15%** 的母线利用率。**这正是 §5.1 电压约束写成 $V_d^2+V_q^2\le(V_{dc}/\sqrt3)^2$、基速里出现 $V_{dc}/\sqrt3$ 的物理来源**——那个 $\sqrt3$ 不是凑的，是 SVPWM 六边形几何的产物。母题落点：急停指令能调动的最大电压，被这个六边形硬性封顶。

---

## 3. 无感观测：Luenberger 观测器 + 锁相环

> [!tip] 本节四拍
> **直觉**（FOC 需要转子角 $\theta_e$，但物理编码器贵且占空间）→ **推导**（虚拟电机 + PI 反馈把未知反电动势"挤"进积分器 → PLL 提角）→ **对比**（代数微分求解 vs 观测器积分求解）→ **联系**（这是 [[ControlTheory#1.4 PID、灵敏度与状态空间|状态观测器/可观性]]与 [[SignalProcessing#5.2 演进脉络：KF → EKF → UKF → PF → 因子图|KF]]在电机上的落地）。

### 3.1 为什么不能代数求解反电动势

由 KVL 理论上 $e = V - RI - L\frac{dI}{dt}$。但工程上：电流 $I$ 含高频白噪声，微分算子 $\frac{dI}{dt}$ 把噪声放大成百上千倍；且发热引起 $R$ 漂移使代数方程直接失效。**微分是不稳定操作，积分是稳定操作**——这是构造观测器的动机。

### 3.2 Luenberger 观测器：用积分替代微分

软件中建"虚拟电机"，输入同样电压 $V$，用 PI 反馈强迫虚拟电流 $\hat I$ 逼近真实 $I$：
$$L\frac{d\hat I}{dt} = V - \hat R\hat I - \hat e + K_p(I-\hat I) + K_i\int(I-\hat I)dt$$

> [!note] 这是通用状态观测器在电机上的特例
> 上式正是 [[ControlTheory#1.5 通用状态观测器 (Luenberger) 与分离原理|Luenberger 观测器]]的骨架 $\dot{\hat x}=A\hat x+Bu+L(y-\hat y)$ 落到电机模型上：状态 $x=[I,\,e]^\top$（电流 A、反电动势 V），输出 $y=I$（唯一可测的电流），注入增益 $L=[K_p,\,K_i]^\top$。之所以能把 $e$ 当"状态"估计，是因为 $e$ 相对电流是慢变量（$\dot e\approx0$ 在一个电流环周期内成立），满足可观性。**分离原理**在此给出关键工程许可：观测器极点（$\hat e$ 的收敛速度）可**独立于** FOC 电流环极点单独配置——这就是为什么无感观测能"外挂"在一个已经整定好的电流环之外，而不破坏其闭环稳定性（把 $K_p,K_i$ 调快不会连累电流环带宽）。

当 $\tilde I = I-\hat I \to 0$ 时，$\hat e \to e = -K_i\int\tilde I\,dt$——未知反电动势被**挤压进 PI 积分器**。反电动势编码了角度信息：$e_\alpha = -K_e\omega_e\sin\theta_e,\ e_\beta = K_e\omega_e\cos\theta_e$。

### 3.3 锁相环 (PLL) 提取平滑角度

不直接用 $\theta_e = \arctan(-\hat e_\alpha/\hat e_\beta)$（除法在过零点极敏感）。利用正弦差角公式 $\sin(A-B)=\sin A\cos B-\cos A\sin B$ 构造二阶 PLL 误差（逐步推导与低速崩溃边界见 [[FOC_Control#3.6 低速崩溃边界：为什么灵巧手关节仍然要位置传感器|FOC §3.6]]）：
$$\epsilon = -\hat e_\alpha\cos\hat\theta_e - \hat e_\beta\sin\hat\theta_e = K_e\omega_e\sin(\theta_e-\hat\theta_e) \approx K_e\omega_e(\theta_e-\hat\theta_e)$$

$\epsilon$ 经 PI 得转速 $\hat\omega_e$，积分得极平滑角度 $\hat\theta_e$。

> [!warning] 无感观测的崩溃边界
> 反电动势幅值 $\propto\omega_e$——**低速时信号弱、零速时消失**。这正是灵巧手在接触切换 (grasp-regrasp) 时最需要精确力矩、却是无感观测最脆弱的时刻。低速需高频注入或霍尔/编码器辅助。这一崩溃边界是 §9 gap 的电气侧根源之一。

---

## 4. 串级控制：电流环 → 速度环 → 位置环

> [!example] 三环逐环推导与"内环为何须快 5–10 倍"的相位裕度计算见 [[FOC_Control#2.6 从电流环到串级三环：谁给 $I_q$ 下指令，为什么带宽要分离 5–10 倍|FOC §2.6]] 与 [[Actuator2RigidDynamicsModel_gap#1.5 为什么内环必须比外环快 5–10 倍|Actuator gap §1.5]]。

> [!tip] 本节四拍
> **直觉**（外环给内环下参考，内环带宽必须远高于外环）→ **推导**（三环级联 + 带宽分离）→ **对比**（仿真单一 PD 弹簧 vs 真机三级级联）→ **联系**（这是 [[ControlTheory#1. 古典控制最小语法：后续一切的前置语言|古典控制]]的多环设计，相位裕度预算见 [[ControlTheory#1.3 频率响应：Bode、相位裕度与带宽|§1.3]]）。

真机底层是标准串级闭环（Cascaded Control），从内到外：

$$\underbrace{\theta_{jd}\xrightarrow{\text{位置环 PD}}\dot\theta_{ref}}_{\sim\text{100s Hz}}\xrightarrow{\text{速度环 PI}}\underbrace{I_{ref}}_{}\xrightarrow{\text{电流环 PI / FOC}}\underbrace{I_q\to\tau}_{\sim\text{kHz–10kHz}}$$

**带宽分离原则**：内环带宽 ≫ 外环带宽（通常 5–10×），使外环设计时可把内环近似为理想。电流环带宽（§5.2）$f_{bw}\approx\frac{1}{2\pi}\frac{K_{p,i}}{L}$，空心杯电机可达 1–5 kHz。

> [!note] 串级 = "逐级建 Lyapunov" 的工程直觉
> 位置→速度→电流三级级联，本质是把一个高阶控制问题递归拆解："外环把内环的输出（速度、电流）当作可任意指定的**虚拟控制量**"。这正是 [[ControlTheory#7.4 反步法 (Backstepping)：为串级系统"逐级建 Lyapunov"|反步法 (Backstepping)]]所形式化的对象——每一级配一个 Lyapunov 函数、把上一级期望值作为下一级的虚拟控制参考逐级下压，从而对整条链给出稳定性证书。而带宽分离（内环快 5–10×）正是这套递归得以成立的**工程充分条件**：它让 backstepping 里"上一级已收敛、可视为理想"的假设近似为真；反过来，若内外环带宽靠得太近，这个假设失效，级联就会互相激励振荡。

**位置控制（PD + 动力学前馈）**把关节目标转成电流指令：
$$i_{cmd} = \frac{1}{K_tN}\left(K_p(\theta_{jd}-\theta_j) + K_d(\dot\theta_{jd}-\dot\theta_j) + \tau_{ff}\right)$$

> [!important] 仿真 PD 与真机级联环的错位（Sim-to-Real 的隐形裂缝）
> 仿真器把位控抽象成一个完美关节弹簧 $\tau_{sim} = K_p(q_{des}-q)+K_d(\dot q_{des}-\dot q)$，算出的力矩**零延迟、无饱和**作用到刚体。真机里 $q_{des}\to\tau_{actual}$ 至少含五类非理想：电流建立延迟（高频 action 被低通滤掉）、反电动势（高速力矩下降）、温漂（$R_s\uparrow,K_t\downarrow$）、丝杠 stick-slip（小力矩被死区吞噬）、CAN 串行通信（16 DOF "同步"变扫描式）。
> **这解释了工程惯例**：高减速比/丝杠灵巧手的端到端 RL 通常仍输出**位置目标或 action delta**，让底层位置伺服吸收一部分高频硬件非线性；直接输出力矩会把搜索空间暴露给全部执行器细节，Sim-to-Real 风险急剧上升（§9.3、[[FOC_Control#6.5 仿真 PD 与真机级联环的错位|FOC §6.5 仿真 PD vs 真机级联环]]）。

---

## 5. 电气极限层：高速时力矩为什么"软"

> [!tip] 本节四拍
> **直觉**（母题里那个急停指令，在高速转笔时真机"使不上劲"）→ **推导**（电压约束 → 基速 → 弱磁 → 力矩-转速包络）→ **对比**（仿真矩形 clip vs 真机椭圆包络）→ **联系**（这是 §9 "最大未建模动力学"，与 [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control|OmniXtreme]] 的 actuation-aware 建模同一件事）。

### 5.1 反电动势天花板与力矩-转速包络

稳态 q 轴电压 $V_q = R_sI_q + \omega_eL_dI_d + \omega_e\psi_m$，总电压受 DC 母线约束 $V_d^2+V_q^2 \le (V_{dc}/\sqrt3)^2$。反电动势项 $\omega_e\psi_m$ 随转速**线性增长**。定义**基速** $\omega_{base} = \frac{V_{dc}/\sqrt3 - R_sI_{q,rated}}{\psi_m}$：

$$\text{恒转矩区 }(\omega<\omega_{base}):\ T_{max} = K_tI_{q,max} \qquad \text{恒功率区 }(\omega>\omega_{base}):\ T_{max}(\omega)\approx\frac{K_tI_{q,max}\omega_{base}}{\omega}$$

超过基速后即使 $I_q=0$ 也无法满足电压约束，FOC 被迫注入负 $I_d$（**弱磁**）人为削弱磁通，代价是压缩 $I_q$ 上限并进一步降 $K_t$。**结论：力矩能力随转速上升而非线性下降。**

> [!warning] 仿真的矩形 vs 真机的椭圆
> 仿真里 action clipping 是硬矩形约束 $|\tau|\le\tau_{max}$；真机的约束是一个**速度-力矩椭圆包络**。当策略在高速旋转中命令大力矩急停/急转，真机力矩响应远低于仿真预期——这是 [[sim2real|Sim-to-Real]] 最大的未建模动力学之一。修复见 §10（把包络作为 actuator net 的显式约束，或 OmniXtreme 式 actuation-aware 残差）。

### 5.2 电流环带宽、交叉耦合与量化延迟

高速下 d-q 交叉耦合项 $\omega_eL_qI_q,\ \omega_eL_dI_d$ 急剧增大，需**前馈解耦**补偿；若 $L,\omega_e$ 估计有误，电流环有效带宽被拉低。

**d-q 交叉耦合前馈解耦（逐步推导，不跳步）**：回到 §2.1 的 d-q 电压方程，把耦合项显式标出：
$$V_d = R_sI_d + L_d\dot I_d - \underbrace{\omega_e L_qI_q}_{\text{来自 }q\text{ 轴}}, \qquad V_q = R_sI_q + L_q\dot I_q + \underbrace{\omega_e L_dI_d + \omega_e\psi_m}_{\text{来自 }d\text{ 轴 + 反电动势}}.$$
问题：$d$ 轴电压里混进了 $q$ 轴电流 $I_q$、$q$ 轴电压里混进了 $I_d$——两条电流环**互相耦合**，转速 $\omega_e$（电角速度，rad/s）越高耦合越强，单个 SISO PI 无法把它们当两个独立一阶系统整定。解法是**让 PI 只负责解耦后的"净"电压，把耦合项用估计参数前馈补回指令**：
$$V_d^{cmd}=V_d^{PI}-\omega_e \hat L_qI_q,\qquad V_q^{cmd}=V_q^{PI}+\omega_e \hat L_dI_d+\omega_e\hat\psi_m,$$
其中 $V_{d}^{PI},V_q^{PI}$ 是两个独立 PI 的输出（V），$\hat L_d,\hat L_q$（H）、$\hat\psi_m$（Wb）是估计参数。把 $V_d^{cmd},V_q^{cmd}$ 代回电压方程，前馈项与耦合项**逐项相消**，剩下两个**解耦的一阶方程**：
$$V_d^{PI}=R_sI_d+L_d\dot I_d,\qquad V_q^{PI}=R_sI_q+L_q\dot I_q,$$
即各自退化成 §1.1 那个 $\frac{I}{V}=\frac{1/R}{\tau_e s+1}$（$\tau_e=L/R$）的 SISO 电流环——PI 可独立整定，§1 的直流统一模型这才对高速旋转的 BLDC 重新成立。

> [!warning] 解耦精度依赖参数——又一条通向温漂的出口
> 相消只在 $\hat L\approx L,\ \hat\psi_m\approx\psi_m$ 时精确。$\psi_m$ 随温度衰减（§6，NdFeB $\beta\approx-0.0012/°C$），前馈用的 $\hat\psi_m$ 一旦过时，残余耦合 $\omega_e(\psi_m-\hat\psi_m)$ 就重新注入 $q$ 轴，且被高转速 $\omega_e$ **放大**。于是**温漂不只直接打折 $K_t$（§6.1），还通过破坏 d-q 解耦间接压低电流环有效带宽**——这与 §6.2"温漂经 $\hat R_s$ 污染无感观测角度"是同一机理的第二个出口，共同挂在"电流≠关节力矩"暗线上：$\hat\psi_m$ 越旧，$\tau_{sim}$ 与指尖 $\tau$ 的裂缝越宽。

此外，电流环还受两类离散化伤害：
- **采样延迟**：ADC 采样 + PWM 更新固有 1–1.5 个 PWM 周期延迟（20 kHz 下约 50–75 μs）。控制频率越高，延迟占相位裕度预算越大（[[ControlTheory#1.3 频率响应：Bode、相位裕度与带宽|相位裕度]]）。更根本地，电流环可闭环控制的最高频率被**采样定理**封顶在 $f_{PWM}/2$（[[SignalProcessing#1.1 采样与混叠：离散化不是无损记录|采样与混叠]]）：超过奈奎斯特频率的电流纹波不仅无从控制，还会**混叠**成低频伪信号污染 $I$ 反馈——"提高带宽"与"避免混叠"因此是一对硬权衡，采样率同时给带宽设了天花板、给相位裕度设了预算。
- **数字量化**：PWM 分辨率有限（12-bit@20kHz → ~50 ns），sub-Newton 级指尖力控时量化噪声不可忽略。

---

## 6. 热漂移层：为什么跑久了力矩变小

> [!tip] 本节四拍
> **直觉**（连续转笔十几秒，空心杯电机 60–80°C，几乎所有"常数"都不再是常数）→ **推导**（$R_s(T)\uparrow$、$\psi_m(T)\downarrow$ → $K_t\downarrow$、热失控环路）→ **对比**（仿真恒定 $K_t$ vs 真机每分钟漂移）→ **联系**（温度是 §10 actuator net 的显式输入、是 [[Actuator2RigidDynamicsModel_gap|WM]] 的隐变量）。完整推导见 [[FOC_Control#四、 温度对电机模型参数的系统性影响|FOC §四]]。

### 6.1 两个漂移源与热失控环路

**定子电阻（最大漂移源）** $R_s(T) = R_s(T_0)[1+\alpha_{Cu}(T-T_0)]$，$\alpha_{Cu}\approx0.00393/°C$：
**永磁磁链（力矩常数的根源衰减）** $\psi_m(T)=\psi_m(T_0)[1+\beta(T-T_0)]$，NdFeB $\beta\approx-0.0012/°C$，且 $K_t(T)=\frac32p\psi_m(T)$。

| 温升 $\Delta T$ | $R_s$ 增幅 | $K_t$ 衰减 |
|:-:|:-:|:-:|
| +30°C | +12% | −3.6% |
| +55°C | +22% | −6.6% |
| +80°C | **+31%** | **−9.6%** |

> [!danger] 正反馈热失控环路
> $R_s\uparrow$ 与 $K_t\downarrow$ **同向恶化**：温度升 → $K_t$ 降 → 维持同等力矩需更大电流 → 更大电流加剧发热 → 温度更升。空心杯电机热容极小（$\tau_{th}\approx5$–30 s），连续高速 reorientation 中线圈可在 10–20 s 内逼近热极限（120–150°C，超过永磁**不可逆退磁**）。

### 6.2 对无感观测的致命影响

观测器内固化 $\hat R_s=R_s(T_0)$，真实 $R_s$ 持续增大 → 缺失的电压降 $\Delta R\cdot I$ 被 PI 积分器错误吸收进 $\hat e$ → 经 PLL 引入稳态角度误差：
$$\delta\theta_e \approx \frac{\Delta R_s\cdot I_q}{K_e\omega_e}$$

**关键**：分母 $\omega_e$ 在**低速时放大此误差**——恰是接触切换时最需要精确力矩的时刻（呼应 §3.3 崩溃边界）。

### 6.3 时间尺度与 RL 交互

| 物理过程 | 时间尺度 | 对 RL 的处理 |
|:--|:-:|:--|
| 电气时间常数 $\tau_e=L/R$ | ~10–100 μs | 远快于策略频率，对 RL 透明（FOC 在 MCU 上闭合） |
| 机械时间常数 $\tau_m=J\omega/\tau$ | ~1–10 ms | 与 RL 频率 (50–200 Hz) 同阶，**必须由历史窗口隐式建模** |
| 热时间常数 $\tau_{th}$ | ~10–60 s | 跨 episode 缓慢漂移，同一 episode 内近似恒定，可作**显式温度输入** |
| 磨损/老化 | 天–周 | 需在线自适应 |

---

## 7. 机械层 I：传动方案——力矩如何从电机到关节

> [!tip] 本节四拍
> **直觉**（电机在指尖只有 <0.5 Nm，得靠传动把力矩送到关节）→ **推导**（连杆/腱绳/直驱/QDD 四路线 + Capstan + reflected inertia）→ **对比**（Sim-to-Real 友好度：直驱 > QDD > 连杆 > 腱绳）→ **联系**（腱耦合矩阵与 [[Dynamics#8.1 腱网络运动学：耦合矩阵 $P$|Dynamics §8.1 的 $P$]] 同构）。详见 [[传动]]。

### 7.1 四条传动路线

| 方案 | 刚度 | 反驱动性 | 控制精度 | Sim-to-Real 友好度 | 典型手 |
|:--|:--|:--|:--|:--|:--|
| **连杆** | 最高 | 差 (齿轮自锁) | 中 (累积间隙) | 中 | Barrett, Schunk SDH |
| **腱绳** | 最低 | 中 (取决预紧) | 最低 (非线性迟滞) | **最差** | Shadow (20 主动 DoF / 24 关节), Faive |
| **直驱** | 中 | **最佳** | **最高** ($\tau=K_tI$) | **最佳** | LEAP Hand (Dynamixel XC330 舵机直驱) |
| **准直驱 QDD** | 中偏高 | 良好 | 高 | 良好 | MIT Mini Cheetah 腿 (6:1) 及其衍生手 |
| **直线电缸 + 连杆** | 高 | 取决于丝杠型式 (滚动可反驱 / 滑动或加级自锁) | 中 (换向死区) | 中 (死区可闭式辨识) | **LinkerHand L25**, Inspire, PSYONIC Ability |

> [!warning] 修正（2026-09-02）
> 旧表把 LEAP 列为腱绳手、Allegro v4 列为直驱、BRUCE 列为 QDD 手，均不成立：LEAP 是 Dynamixel 舵机直驱；Allegro v4 是直流电机 + 齿轮减速（CAN 333 Hz 力矩指令）；BRUCE 是 UCLA 的小型人形机器人而非灵巧手。表已按 [[传动]] 的核实结果更新，并补上灵巧手里最常见的第五条路线"直线电缸 + 连杆"。

- **直驱**：$\tau_{joint}=K_tI-b\omega$，力矩链路最短，gap 仅剩轴承摩擦（<2%）+ 齿槽（空心杯为零）+ 热降额。**对 Sim-to-Real 最友好**。
- **腱绳**：仿生肌腱，电机远置降低末端惯量，但引入最难建模的一组非线性——Capstan 摩擦 $T_{out}=T_{in}e^{-\mu\sum\theta_i}$、弹性迟滞、预紧衰减、单向性（只能拉不能推，需拮抗对）。

> [!note] Capstan 方程 $T_{out}=T_{in}e^{-\mu\theta}$ 的逐步推导（不跳步）
> 取绕在半径 $r$（m）圆柱上、包角 $\theta$（rad）的腱绳一小段微元 $d\theta$，其两端张力为 $T$ 与 $T+dT$（N，沿腱切向）。对该微元做受力平衡，分解到法向与切向两个方向：
> - **法向**（指向圆心）：两端张力各在半径方向投影 $T\sin(d\theta/2)$，用小角近似 $\sin(d\theta/2)\approx d\theta/2$，两端合计的向心分量 $=2\cdot T\cdot\frac{d\theta}{2}=T\,d\theta$。它由圆柱对微元的法向支持力 $dN$（N）平衡，故 $dN=T\,d\theta$。
> - **切向**：两端张力差 $dT$ 由 Coulomb 摩擦 $dF=\mu\,dN$（$\mu$ 无量纲摩擦系数）平衡。当腱被"拉出"（output 端相对圆柱滑动），摩擦阻碍力的传递，取符号得 $dT=-\mu\,dN=-\mu T\,d\theta$。
>
> 得到可分离变量的一阶 ODE $\dfrac{dT}{T}=-\mu\,d\theta$。从 input 到 output 沿包角积分：$\displaystyle\int_{T_{in}}^{T_{out}}\frac{dT}{T}=-\mu\int_0^{\theta}d\theta\ \Rightarrow\ \ln\frac{T_{out}}{T_{in}}=-\mu\theta$，即 $\boxed{T_{out}=T_{in}e^{-\mu\theta}}$。注意结果**与半径 $r$ 无关**，只取决于包角与摩擦系数。
>
> **物理含义与失效边界**：张力沿包角**指数衰减**——多段绕行（$\sum\theta_i$ 大）的腱手（Shadow）力传递损耗最重、力控最难标定。更关键的是**方向性**：把腱"放松"时相对滑动方向反转，摩擦符号翻转为 $+\mu$，于是拉紧走上支 $e^{-\mu\theta}$、松开走下支 $e^{+\mu\theta}$，围出一个**力矩迟滞环**。**这条方向相关的非光滑性，正是"接触的非光滑性"暗线在传动侧的现身**：Capstan 本质是"分布式 [[ContactMechanics#4.2 软指模型：接触斑与扭转摩擦|摩擦锥]]沿曲面的积分"，指数即积分的产物；它和 §8.2 的 Stribeck stick-slip 一样，把本该可微的力矩映射撕成方向相关的分段函数——这也是腱手在 §9.3 需要最大 DR 幅度、且几乎从不让 RL 直接输出力矩的根因。

### 7.2 Reflected Inertia：为什么减速比是把双刃剑

传动折算到输出轴的等效惯量：
$$J_{reflected} = i^2J_{motor}$$

> [!note] $J_{reflected}=i^2J_{motor}$ 的能量推导 + 它为何给阻抗带宽设了地板
> **推导（能量等效，不跳步）**：设减速比 $i=\omega_m/\omega_j$（电机角速度 $\omega_m$ / 关节角速度 $\omega_j$，均 rad/s；$i>1$ 为减速）。转子转动动能 $E=\frac12 J_{motor}\omega_m^2$（J）。折算惯量 $J_{reflected}$ 的定义是"在关节侧转出同样动能所需的等效惯量"，即 $\frac12 J_{reflected}\omega_j^2 \overset{!}{=}\frac12 J_{motor}\omega_m^2$。两边解出 $J_{reflected}=J_{motor}(\omega_m/\omega_j)^2=i^2 J_{motor}$——**平方来自动能里的速度平方，这就是减速比被"平方放大"的物理根**。
>
> **为何是双刃剑——阻抗带宽的地板**：阻抗控制（[[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|阻抗控制]]）想让关节对外表现出一个**目标表观惯量** $M_d$，靠控制器在带宽 $\omega_c$（rad/s）内主动"抵消"真实惯量。但对**频率高于 $\omega_c$ 的外部冲击**（碰撞、突加接触），控制器来不及反应，环境直接撞上的是**未经补偿的物理惯量 $J_{reflected}$**。因此可渲染的最小表观惯量存在硬地板：$M_d \gtrsim J_{reflected}$（在 $\omega>\omega_c$ 频段）。高减速比（$i=100\Rightarrow J_{reflected}=10^4J_{motor}$）把这个地板抬得极高——关节在碰撞瞬间"又硬又重"，冲量 $\int F\,dt$ 巨大。**这条"高频段暴露原始惯量"的机理，把 reflected inertia 直接钉在"接触的非光滑性"暗线上**：接触是一个宽频事件（[[ContactMechanics|碰撞含高频分量]]），恰好落在控制带宽之外，于是 $i^2J_m$ 决定了撞击的剧烈程度、也决定了被动柔顺（反驱动性）能有多好。这正是 QDD（$i\approx6$，$J_{reflected}=36J_{motor}$）相比高减速比方案在接触丰富任务上的核心优势。

直驱 ($i=1$) 最小；QDD ($i\approx6$) 为 $36J_{motor}$；高减速比 ($i=100$) 达 $10^4J_{motor}$。高 reflected inertia **限制机器人对外力的响应带宽**，是 QDD 相比高减速比的核心优势，也直接决定 [[ContactMechanics|接触]]时的碰撞冲量与 [[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|阻抗控制]]可达的最小表观惯量。

> [!example] 丝杠灵巧手的具体折算：LinkerHand L25（完整 worked example 见 [[LinkerSysId#§3 直线→关节折算：等效直线质量变成关节 armature|LinkerSysId §3]]）
> 旋转→直线电缸把"减速比"换成**导程增益** $2\pi/l$（rad/m，$l$ 为丝杠导程）。转子惯量 $J_{rotor}$ 先折算成推杆的**等效直线质量** $M_{eq}=J_{rotor}(2\pi/l)^2$，再经关节力臂 $R$ 折回关节，得 Isaac Gym 的 `armature`：
> $$J_{armature}=M_{eq}R^2=J_{rotor}\Big(\tfrac{2\pi R}{l}\Big)^2=N_{eq}^2\,J_{rotor},\qquad N_{eq}=\tfrac{2\pi R}{l}.$$
> **这正是 $J_{reflected}=i^2J_{motor}$ 的丝杠版本**（$i\to N_{eq}$），"平方"同源于动能里的速度平方。代入 L25NS（$l=0.7$ mm、$R\approx12$ mm、$J_{rotor}=0.1425$ kg·mm²）：$M_{eq}\approx11.48$ kg、$N_{eq}\approx108$、`armature`$=M_{eq}R^2\approx11.48\times0.012^2\approx1.65\times10^{-3}$ kg·m²（旧版误用 $R=15$ mm 得 $2.6\times10^{-3}$，已修正）。**这个 `armature` 必须写进仿真关节**，否则转子折算惯量被漏掉、Sim 关节过轻，力控增益迁到真机即振荡（[[Actuator2RigidDynamicsModel_gap|执行器↔刚体 gap]]）。而 $N_{eq}\approx108$ 虽高，因丝杠为滚动体式（滚珠 / 滚柱，型式待核实）$\eta>90\%$（§8.1）故四指**仍可反驱**（拇指因多一级 17:1 折返减速箱而不可反驱，见 [[Transmission2JointDynamics_gap]]）——高减速比与可反驱在低损耗传动下并不矛盾。

> [!note] 惯量匹配 (Inertia Matching)——工程选型的黄金律
> 伺服系统要求负载惯量/电机惯量比 $J_L/J_M$ 通常 ≤ 5–10:1。比值过高则动态响应迟钝、易振荡、整定困难。灵巧手高动态操作中，快速换指使等效惯量突变——这既是选型约束（选低惯量空心杯/无框电机），也是 §5 力矩-转速包络之外又一个动态性能瓶颈。（源自机电选型工程实践）

### 7.3 腱网络的对偶性（承接 Dynamics §8）

$m$ 腱驱 $n$ 关节：$\boldsymbol\tau = R(q)\mathbf f$，$R$ 元素是力臂。这与 [[Dynamics#8.1 腱网络运动学：耦合矩阵 $P$|Dynamics 的耦合矩阵 $P$]] 完全同构，抓取分析的全部工具（力闭合、冗余、零空间）可直搬。欠驱动 $m<2n$ 时力矩空间可达集受约束——直接影响仿真力控精度。**这是"对偶性 $J/G/P$"暗线在执行器侧的又一次现身。**

---

## 8. 机械层 II：减速器——背隙、摩擦、弹性的来源

> [!tip] 本节四拍
> **直觉**（电机力矩不够，减速器放大扭矩，但引入背隙/摩擦/弹性三大 gap）→ **推导**（各类型的核心参数 + Stribeck 摩擦模型 + 谐波非线性刚度）→ **对比**（谐波零背隙 vs 蜗轮自锁不可反驱动）→ **联系**（这三大非理想性是 §9 gap 的机械侧主体）。详见 [[减速器]] 与 [[谐波减速器与RV减速器选型核心区分依据|谐波 vs RV 选型]]。

### 8.1 核心参数与类型谱系

| 减速器 | 背隙 | 效率 $\eta$ | 反驱动性 | 扭转刚度 | 灵巧手适用 |
|:--|:--|:--|:--|:--|:--|
| 行星齿轮 | 精密 ≤3′ / 经济型 8–15′ | 高 (95–97%) | 良好 | 低 | ⭐⭐⭐⭐ |
| 蜗轮蜗杆 | 低 | 低 (30–90%) | **不可 (自锁)** | 低 | ⭐ |
| **谐波** | **零** | 中偏高 (65–90%) | 中偏差 | **非线性** | ⭐⭐⭐⭐⭐ |
| 摆线针轮 | 低 (<1′) | 高 (85–95%) | 中 | 高 | ⭐⭐⭐ |
| RV | 极低 | 中 | 差 | 极高 | ⭐⭐ |
| 滚珠/滚柱丝杠 | 低 | 高 (>90%) | 可 | 高 | ⭐⭐⭐ (线性驱动) |

**反驱动性与自锁的判据**：$\eta<50\%$ 时摩擦耗散超过可传递能量 → 自锁（蜗轮蜗杆）。灵巧手力控需 $\eta>50\%$、最好 $>80\%$。**等价的几何判据**（丝杠/螺纹侧）是**螺旋角 $\lambda$ 与摩擦角 $\rho=\arctan\mu$ 的大小关系**：$\lambda<\rho$ 则无论施加多大轴向力都推不动（自锁），$\lambda>\rho$ 则可反驱。滚珠丝杠用**滚动替代滑动**把 $\mu$（进而 $\rho$）压到极低，故高效率、可反驱——这就是为什么 [[减速器|滚珠丝杠]]驱动的灵心巧手上电后无明显自锁（可反驱），而蜗轮蜗杆式传动被自锁钉死、失去被动柔顺。一个高等效减速比的丝杠灵巧手仍可反驱的完整对账见 [[LinkerSysId#§6 反驱对账：高减速比为什么不一定自锁|LinkerSysId §6]]；螺旋升角与正/反向效率的逐步推导见 [[减速器#3.0 螺旋 = 缠在圆柱上的斜面：自锁与效率的完整推导|减速器 §3.0]]。

### 8.2 三大非理想性——机械侧 gap 的主体

**① 背隙 (Backlash)**：力矩方向反转时的空行程死区 $\Delta\theta\approx0.02°$–$0.25°$。仿真为零间隙理想铰链，力矩方向切换瞬时生效；真机在精细操作（转笔、翻转）中频繁换向使背隙累积。谐波减速器的弹性预载实现**零背隙**——这是其在灵巧手中被广泛采用的核心原因。

**② 非线性摩擦 (Stribeck)**：
$$\tau_{fric}(\dot q) = \left[F_c + (F_s-F_c)e^{-(\dot q/v_s)^2}\right]\text{sgn}(\dot q) + b\dot q$$
静摩擦 $F_s>$ 库仑 $F_c$，过零点 $F_s$ 可达 $F_c$ 的 2–5 倍，产生 **stick-slip 跳变**与迟滞环。仿真通常只建粘滞项 $b\dot q$（IsaacGym `joint_friction`）或加库仑项（MuJoCo `frictionloss`），**忽略 Stribeck 过渡**——这是 gap 的重要来源。

**③ 扭转弹性（谐波柔轮）**：非线性刚度 $k(\theta)=k_0+k_1|\theta|+k_2\theta^2$，加载/卸载路径不同（迟滞）。高载下弹性偏差 $0.1°$–$0.5°$，还引入二阶振荡。仿真常简化为刚性关节。

> [!note] 非线性刚度 $k(\theta)$ 与迟滞环：为什么"渐硬"且"卸载不原路返回"
> 这里 $k(\theta)$（Nm/rad）是**切线刚度** $k(\theta)=d\tau/d\theta_{tw}$（$\theta_{tw}$ 为柔轮扭转角 rad，$\tau$ 为传递力矩 Nm），不是常数弹簧。于是实际传递力矩要对它积分：
> $$\tau(\theta_{tw})=\int_0^{\theta_{tw}}k(\theta')\,d\theta'=k_0\theta_{tw}+\tfrac{k_1}{2}\theta_{tw}|\theta_{tw}|+\tfrac{k_2}{3}\theta_{tw}^3.$$
> - $k_0$ 是小载荷线性刚度；$k_1,k_2$ 项使刚度随扭转角**渐增（渐硬弹簧, stiffening）**——柔轮齿与波发生器啮合越深，接触面越多、越硬。这解释了"小力矩软、大力矩硬"的手感，也是为何低力矩指令易被弹性"吞掉"位移、高力矩下又突然变硬引发二阶振荡。
> - **迟滞环**：加载与卸载走不同路径，因为柔轮齿面间存在**内摩擦/微滑**（每次啮合有微观 stick-slip）。加载走上支、卸载走下支，围出的**环面积 = 每循环耗散的弹性势能**（J），表现为力控中的能量损失与相位滞后。
>
> **跨模块统一工具**：这个方向相关的迟滞，与腱绳 Capstan 迟滞（§7.1）、[[SignalProcessing#2.2 迟滞：Prandtl–Ishlinskii 模型与逆补偿|电容触觉的迟滞]]是**同一数学对象**——都可用 **Prandtl–Ishlinskii 模型**（一族 backlash/play 算子的加权叠加）刻画并做**逆补偿**。换言之，SignalProcessing 为触觉迟滞开发的逆模型可**直搬**到谐波柔轮的力矩标定上。**这是"接触的非光滑性"暗线的又一现身**：谐波柔轮把"刚性关节"这一仿真理想撕成一个带记忆（path-dependent）的非光滑映射——而"带记忆"恰恰意味着当前力矩不再是当前状态的函数，需要 §10 的历史窗口才能补出（呼应 POMDP→history-window 的处理）。

> [!warning] 正向/反向效率不对称
> 谐波减速器反向效率仅为正向的 60–80%——**外力推动关节时的力矩反馈远小于仿真预期**，对力感知和阻抗控制影响显著。这直接决定了 [[Minimalist Compliance Control|MCC]] 为何要用方向相关效率模型做力控。

---

## 9. 迁移层 I：执行器 Sim-to-Real gap 的完整解剖

> [!tip] 本节四拍
> **直觉**（回到母题：仿真 $\tau_{sim}$ 直接等于关节力矩，真机要穿整条链）→ **推导**（理想化假设清单 → 完整力矩传递链模型）→ **对比**（各传动方案的 DR 幅度）→ **联系**（这是 [[ReinforcementLearning#9.1 先分类，再治疗：MDP 四要素 gap 诊断|RL Sim-to-Real 的 Action/Transition gap]]的物理来源）。系统分析见 [[sim2real]]。

### 9.1 仿真理想化假设清单

| 假设 | 仿真处理 | 真机现实 | 落点 |
|:--|:--|:--|:--|
| 力矩瞬时施加 | $\tau$ 每步直接生效 | 电气/机械时间常数 + 电流环带宽 | §4–§5 |
| 零背隙 | 力矩-角度单值映射 | 减速器背隙死区 | §8.2 |
| 简单摩擦 | 无/仅粘滞 | Stribeck 非线性 + stick-slip | §8.2 |
| 刚性关节 | 无弹性变形 | 谐波柔轮/腱绳弹性 → 二阶振荡 | §8.2 |
| 完美力矩传递 | $\tau_{joint}=\tau_{sim}$ | $\eta iK_tI-\tau_{fric}-k\theta$ | §7–§8 |
| 力矩上限恒定 | `effort_limit` 常数 | 力矩-转速包络 + 热降额 | §5–§6 |
| 独立关节 | 各关节独立 | 欠驱动耦合 / 腱交叉耦合 | §7 |

### 9.2 完整力矩传递链模型

仿真抹去的这条链，完整写出来是：
$$\tau_{joint} = \underbrace{\eta(T,\dot q)}_{\text{效率}}\cdot\underbrace{i}_{\text{减速比}}\cdot\underbrace{K_t(T)}_{\text{热漂移}}\cdot\underbrace{I}_{\text{电流环兑现}} - \underbrace{\tau_{fric}(\dot q,T)}_{\text{Stribeck}} - \underbrace{k(\theta_{tw})\theta_{tw}}_{\text{弹性}}$$

同时 $I$ 本身受 §5 电压约束与电流环带宽限制、受 §8 背隙死区延迟。**仿真把这整条链等效成 $\tau_{sim}\equiv\tau_{joint}$。**

> [!note] 这条链要兑现的"目标值"来自 RNEA
> 传递链左端那个待实现的关节力矩 $\tau_{joint}$，正是 [[Dynamics#5.2 RNEA：$O(N)$ 逆动力学（控制的基石）|RNEA]] 为跟踪期望轨迹算出的**逆动力学力矩** $\tau=M(q)\ddot q_d+C(q,\dot q)\dot q_d+g(q)$（$\ddot q_d,\dot q_d,q_d$ 为期望关节加速度/速度/位置）。换言之：**Dynamics 侧回答"关节需要多少 $\tau$"（上游需求），本讲这条链回答"电机端怎么把它兑现出来"（下游供给）**，二者恰在 $\tau_{joint}$ 处对接。这正是"电流≠关节力矩"暗线的两端——$\tau$ 作为控制律的**输出目标**（RNEA）与作为执行器链的**待实现量**（本讲）在此缝合：仿真直接令 $\tau_{sim}\equiv$ 需求 $=$ 供给，把中间整条供给链一笔抹去。

### 9.3 按传动方案的 Domain Randomization 建议

DR 的物理原则：**gap 越大的环节，随机化幅度越大**（[[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|RL §9.2 增覆盖]]）。

| 参数 | 直驱 | QDD | 齿轮 | 腱绳 |
|:--|:-:|:-:|:-:|:-:|
| 关节摩擦 $b$ | ±20% | ±30% | ±50% | ±80% |
| 力矩缩放 (效率) | ±5% | ±10% | ±20% | ±30% |
| 关节刚度 $k$ | — | ±10% | ±30% | ±50% |
| 背隙角 | — | ±0.002 rad | ±0.005 rad | — |
| 力矩延迟 (steps) | 0 | 0–1 | 0–2 | 0–3 |

> [!tip] Action Space 应匹配传动方案
> - **直驱/QDD**：可用 **torque control**（电流-力矩线性直接映射）
> - **高减速比/丝杠**：用 **position control**（action=目标角+PD），让底层 PD 吸收减速器非线性（呼应 §4 的工程惯例）
> - **腱绳**：position control + 力矩限幅，避免策略直接操作难建模的力矩非线性区

---

## 10. 迁移层 II：数据驱动执行器模型 (Actuator Model)

> [!tip] 本节四拍
> **直觉**（$\eta,\tau_{fric},k,K_t(T)$ 难精确辨识，就用数据学残差）→ **推导**（最小充分输入集 + POMDP 历史窗口 + 输出定义）→ **对比**（解析辨识 vs 神经黑箱 vs 力矩传感器闭环）→ **联系**（与 [[Dynamics#9. 适配层：可微物理与神经动力学|DexNDM 关节级神经动力学]]、残差 RL、[[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|RMA]] 同源）。

### 10.1 Actuator Net：学"仿真 PD 没覆盖的那段残差"

不复现 FOC 内部电气动态（那是 MCU 的事），而学**从力矩/位置指令到关节实际力矩的端到端黑箱映射**。经典范式 [[Learning Agile and Dynamic Motor Skills for Legged Robots|ANYmal actuator net]]：用真机采集的 $(误差历史)\to\tau$ 数据训练网络，替代解析执行器模型嵌入仿真。

**POMDP 本质**：通信延迟、减速器摩擦、反电动势、控制器内部状态使单帧 $s_t$ 无法完整描述系统 → 传入**历史窗口**让网络第一层学成非线性 FIR 滤波器。最小充分输入集：
$$\mathbf x_{act,t} = \big[\underbrace{a_{t-H:t}}_{\text{指令}},\ \underbrace{\phi_{t-H:t}}_{\text{角度}},\ \underbrace{\dot\phi_{t-H:t}}_{\text{速度}},\ \underbrace{\tau_{fb,t-H:t}}_{\text{反馈力矩}},\ \underbrace{T_{motor,t}}_{\text{温度}}\big],\quad H\ge2\tau_m/\Delta t\approx10\text{–}30$$

- **历史窗口** 覆盖 2–3 个机械时间常数，隐式捕捉 Stribeck 迟滞（判断处于摩擦曲线哪一段）与控制器过渡态
- **温度 $T$** 作显式输入编码热漂移（§6）——标量缓变量，episode 级采样
- **输出** $\hat\tau_{link}$ 是**关节端**力矩，非电机轴力矩

### 10.2 力矩反馈为何"能当输入、不能当目标"

SDK 读回的 $\tau_{measured}=K_t^{nominal}\cdot I_q^{measured}$ 有三重污染：$K_t^{nominal}$ 不随温度更新（系统偏差）、$I_q$ 含量化噪声、是电机轴力矩缺全部传动损耗。

> [!warning] 观测信号的可靠性排序（真机 RL 状态设计法则）
> | 信号 | 来源 | 可靠性 | 推荐用途 |
> |:--|:--|:-:|:--|
> | 关节角度 $\phi$ | 编码器 | ⭐⭐⭐⭐ | **RL 核心观测 + WM 预测目标** |
> | 触觉矩阵 | 薄膜阵列 | ⭐⭐⭐⭐ | **RL 核心观测 + 接触判断** |
> | 角速度 $\dot\phi$ | 差分 | ⭐⭐⭐ | RL 观测（需 KF/低通滤波） |
> | 反馈力矩 $\tau_{fb}$ | 电流估算 | ⭐⭐ | Actuator Net **输入特征**（❌ 非 reward / 非预测目标） |
> | 温度 $T$ | NTC | ⭐⭐⭐⭐ | Actuator Net 显式输入 |
>
> **核心结论**：绝不要把电流推算的力矩作为高权重观测、reward 或 WM 预测目标——它在到达指尖前已被热漂移、Stribeck、非线性 Jacobian、连杆弹性严重污染，会引发 Reward Hacking（策略学会"轻柔但无效"降低虚假力矩）。RL 核心观测应是角度 + 触觉（[[ReinforcementLearning#8.1 状态表征：触觉是灵巧操作的"暗感官"|触觉暗感官]]）。详见 [[Actuator2RigidDynamicsModel_gap#七、 RL State Space 设计法则|Actuator gap §七]]。

### 10.3 力矩传感器闭环 (JTS) 与数据驱动鲁棒证书

**方案对比**：
- **无传感器** $i_d=\tau_{target}/(K_tN\eta)$：便宜，但摩擦无法准确建模
- **JTS 闭环**：减速器输出端装力矩传感器，实现真正"透明化"刚体动力学控制，代价是成本与集成

> [!tip] 从"能拟合"到"能证明安全"（连接数据驱动控制）
> Actuator Model 的真机适配不应只看 one-step MSE。将短真机轨迹写成 $X_+=AX_-+BU_-+W_-$，其中 $W_-$ 是把 CAN 抖动、温漂、Stribeck、触觉噪声**显式纳入证书**的噪声集合。若 $W_-W_-^\top\preceq T\epsilon I$，可用 [[ControlTheory#13. 数据驱动控制：模型不准时如何仍给稳定性证书|ControlTheory §13 的 Matrix S-lemma LMI]] 检查是否存在共同 Lyapunov 矩阵 $P\succ0$。**若 LMI 不可行**，说明脚本运动没充分激发执行器模式——应补采高/低速、升温、过零 stick-slip 三类轨迹，而非盲目加大网络容量。这给 [[Actuator2RigidDynamicsModel_gap|"5 分钟真机自适应"]]一层硬判据。

---

## 11. 接口层：嵌入式实现——MCU / STM32 / CAN

> [!example] L25 真机的逐项延迟预算（SDK 队列 / CAN 帧 / MCU 规划平滑 $T_f\approx120$ ms / 反馈）见 [[Actuator2RigidDynamicsModel_gap#4.2 延迟预算表：从策略到电机轴|Actuator gap §4.2]]；整条链路的 gap 总图见 [[sim2real|灵巧手 gap 总图]]。

> [!tip] 本节四拍
> **直觉**（16 DOF 指令在 API 上看似同步，硬件上按 CAN 帧串行落地）→ **推导**（归一化指令 + 差分抗噪 + 位时序带宽）→ **对比**（软件同步假设 vs 硬件串行相位差）→ **联系**（这些延迟/相位差进入 §4 相位裕度预算、§10 actuator net 的 latency 编码）。详见 [[Actuator2RigidDynamicsModel_gap#三、 L25 灵巧手 CAN 协议与可读取量分析|L25 CAN 分析]]。

### 11.1 三者角色

**MCU** 是"CPU+存储+外设集成在单芯片"的实时控制计算机；**STM32** 是基于 ARM Cortex-M 的具体 MCU 产品族，运行手指局部串级闭环；**CAN** 是多节点共享的抗干扰总线，在上位机与各指节点间传命令/观测。典型链路：
$$\pi_\theta(o_t)\to a_t\to\text{SDK}\to\text{CAN dispatcher}\to\text{CAN bus}\to\text{finger MCU}\to\text{FOC 电流环}$$

### 11.2 归一化指令不是物理量

SDK 常把角度/速度/力矩暴露为 $[0,100]$ 归一化值，CAN 层线性映射为单字节 $u_{raw}=\text{round}(255\cdot u_{sdk}/100)$。因此 `torque=100` 只是**固件允许的最大电流百分比**，不等价固定 N·m——它随温度、转速、反电动势、丝杠摩擦、安全限流改变。**任何把 SDK 百分比当物理单位拟合的模型，都会把固件策略、热状态、传动损耗混成不可解释黑箱。**

### 11.3 差分抗噪与位时序带宽

CAN 可靠性来自差分信号 $V_{diff}=V_{CAN\_H}-V_{CAN\_L}$：共模噪声 $\Delta V$ 叠加到两线时差分电压不变。实时性受位时序限制 $\text{BaudRate}=1/[(1+t_{PROP}+t_{PHASE1}+t_{PHASE2})T_q]$。

> [!important] 对 World Model / Actuator Net 的含义
> 16 DOF 控制写入在软件 API 上看似同步，硬件上却按 CAN 帧串行落地（角度帧 `0x41-45`、速度帧 `0x49-4D`、力矩帧 `0x51-55`），存在"手指级/关节级"相位差；每指 72 字节触觉需 12 帧拼接 + ~2.5 ms 指间间隔，全手触觉不是同一物理时刻的严格快照。因此 [[Actuator2RigidDynamicsModel_gap|Latency-Aware Actuator]] 不应只建一个全局 latency，而应保留执行时间戳的低维编码 $z_{\delta,t}$，喂给 §10 的 actuator net。

---

## 12. 知识回扣与记忆图：一个力矩指令串起执行器七层

> [!abstract] 用一个转笔力矩指令把全讲复述一遍（刻意复述，为记忆）
> 策略在仿真里对某关节输出一个峰值力矩、命令它急停反向，仿真里这个 $\tau_{sim}$ **零延迟无损耗**地推动理想关节。真机里它开始一段坎坷旅程：**(§1)** 力矩的物理起点是电流，$\tau=K_tI$——但只有空心杯/无框电机能让这条线性关系干净成立。**(§2)** 电机是三相交流的，FOC 用 Clarke/Park 把它降维成直流，令 $I_d=0$ 后 $\tau=K_tI_q$，指令这才有了兑现的载体。**(§3)** 可 FOC 需要转子角，无感观测器用 Luenberger+PLL 把它从反电动势里挤出来——低速时这套会崩，恰是接触切换最要命的时刻。**(§4)** 指令穿过位置→速度→电流三级串级环，仿真的单一 PD 弹簧在这里裂成一条带延迟带饱和的级联链。**(§5)** 若此刻手指正高速旋转，反电动势顶到电压天花板，力矩-转速椭圆包络把这个急停指令**削了顶**——仿真的矩形 clip 骗了策略。**(§6)** 连续转了十几秒，空心杯电机 80°C，$K_t$ 掉 9.6%、$R_s$ 涨 31%，同一指令**打了折**还在热失控环里越陷越深。**(§7)** 力矩终于出了电机，穿过丝杠/连杆，reflected inertia $i^2J_m$ 让它变"重"，欠驱动耦合让它串味。**(§8)** 又被减速器的背隙吞掉换向的一瞬、被 Stribeck 静摩擦卡在过零点、被谐波柔轮的非线性弹性拖出滞后。**(§9)** 到达指尖时，它与仿真预期差之千里——这就是关节虚拟力矩假设的失效，机械差异 + 电气差异的合谋。**(§10)** 我们没法精确辨识每个环节，就用 actuator net 吃历史窗口 + 温度，学"仿真 PD 没覆盖的那段残差"，还用数据驱动 LMI 证明这 5 分钟数据够不够。**(§11)** 而这一切的指令，本就不是同步落地的——它们按 CAN 帧串行挤过总线，带着相位差抵达各指 MCU。**一个力矩指令，走遍了执行器七层大厦。**

> [!note] 三大记忆支柱 + 一条暗线
> **三支柱**：**电流≠关节力矩**（$K_t$ 线性度 → 传动畸变 → 到指尖已面目全非）、**力矩上限是动态的**（转速包络 × 热降额，不是矩形 clip）、**历史窗口是解药**（POMDP 本质，用时序隐式补不可观的摩擦/延迟/温漂）。**一条暗线**：**仿真把 $\tau$ 当输入，真机把 $\tau$ 当输出**——Sim-to-Real 的执行器 gap，本质是这一"输入/输出"身份错位。

---

## 13. 相关论文与项目 (PapersRecap & Projects)

> [!abstract] 知识图谱反向链接
> 以下论文/笔记在其研究中涉及执行器建模、力矩传递链或电机级 Sim-to-Real 的核心主题。

### 执行器建模与 actuation-aware 控制
- [[Learning Agile and Dynamic Motor Skills for Legged Robots]] — action-to-torque **actuator network** 近似低层闭环的开创性范式
- [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control|OmniXtreme]] — torque-speed envelope 建模执行器物理极限，actuation-aware 残差 RL（§5.1 的直接对应）
- [[Minimalist Compliance Control|MCC]] — 方向相关效率 + 系列弹性元件的最小模型力控（§8.2 效率不对称的落地）
- [[谐波减速器与RV减速器选型核心区分依据|谐波 vs RV 减速器]] — 谐波柔轮弹性对 sim-to-real gap 的影响（§8）
- [[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning|DexCtrl]] — 学习式自适应控制器直接补执行器非理想（§10 actuator net 的控制器版）

### 神经动力学与残差补偿
- [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model|DexNDM]] — 关节级神经动力学，隐式吸收摩擦/间隙/耦合（§10 同源）
- [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)|HORA]] — 环境编码器从历史推断隐式物理参数，在线自适应
- [[Grounded Action Transformation|GAT]] — 学 $a_{real}=h(s,a_{sim})$ 修正执行器非理想性

### Sim-to-Real 方法论
- [[sim2real|硬件 Sim-to-Real Gap 分析]] — 力矩传递链完整建模 $\tau_{joint}=\eta iK_tI-\tau_{fric}-k\theta$（本讲 §9 的项目级母本）
- [[A Survey of Sim-to-Real Methods in RL|Sim2Real Survey]] — MDP 四要素分类：本讲聚焦 Action 与 Transition 层的物理 gap
- [[Reinforcement Learning in Robotic Systems - A Review on Sim-to-Real Transfer|Tiwari Sim2Real]] — 执行器级建模视角
- [[DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality|DeXtreme]] — ADR 覆盖电机刚度/阻尼/延迟等执行器参数（§9.3）
- [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction|TRANSIC]] — 在线修正补偿执行器/硬件非线性（§10）
- [[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation|ViserDex]] — 视觉 sim2real in-hand，含执行器 EMA 随机化=隐式延迟 DR

### 项目级真机执行器 Idea（WMTS / DNPM）
- [[FOC_Control|PMSM 与无感 FOC 第一性原理推导]] — 本讲 §2–§6 的项目级完整推导源
- [[Actuator2RigidDynamicsModel_gap|Actuator-to-Rigid Gap：L25 硬件深度分析]] — 本讲 §10–§11 的项目级母本
- [[Final_WMTS|World Model as Task Scheduler]] — Actuator Model + Rigid Dynamic Model 解耦世界模型
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-002-Latency-Aware-Actuator|LAAA]] — CAN 延迟 + 温漂 conditioned actuator FiLM，5 min 真机自适应
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-013-Stick-Slip-Mode-Switching|SSMS]] — stick-slip 模态识别的双子策略切换

---

## 14. 结论

灵巧操作的执行器早已不是"给个力矩就完事"，而是一条被仿真器**一笔抹去、却在真机上处处设卡**的物理链路。从电磁力矩的起点（§1）、FOC 的降维解耦（§2–§4）、电气与热的动态极限（§5–§6），到机械传动与减速的损耗畸变（§7–§8），最终落到 Sim-to-Real gap 的解剖与数据驱动修复（§9–§10）、以及嵌入式接口的现实约束（§11）：**理解"电流≠关节力矩"是入门，能量化力矩-转速包络与热漂移是进阶，能用 actuator net + 数据驱动证书把这条链缝回 RL 训练闭环，则是通向可靠 Sim-to-Real 的钥匙。**

而贯穿始终的暗线，是**"仿真把 $\tau$ 当输入、真机把 $\tau$ 当输出"这一身份错位**——它把 [[ControlTheory|控制理论]]的串级环与观测器、[[Dynamics|动力学]]的操作器方程与腱耦合、[[ReinforcementLearning|强化学习]]的 Sim-to-Real 三味药，缝进同一条力矩传递链。执行器，是策略意图与物理现实之间**最后一公里的翻译官**。
