---
tags: [Dexterous_Manipulation, Actuator_Dynamics, Sim-to-Real, L25_Hand, WMTS, Cascade_Control, CAN_Bus, Latency]
aliases: [Actuator2Rigid Gap, L25 硬件分析, 指令到电机轴, L25 延迟预算]
date: 2026-04-15
updated: 2026-09-02
related:
  - "[[Actuation]]"
  - "[[FOC_Control]]"
  - "[[Transmission2JointDynamics_gap]]"
  - "[[LinkerSysId]]"
  - "[[sim2real]]"
  - "[[Final_WMTS]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
---

# Actuator-to-Rigid Dynamics Gap：L25 灵巧手 指令 → 电机轴力矩

> [!abstract] 本篇在链路中的位置
> 整条链路是 `电能 → 电磁力矩 → FOC 电流环 → 减速/丝杠/连杆 → 关节力矩 → 刚体+接触`。**本篇只管从"策略给出一个数"到"电机轴上出现一个力矩"这一段**：串级三环（位置→速度→电流）、CAN 串行通信、传输/规划延迟、8-bit 量化、热漂移。上一篇是 [[FOC_Control]]（电流环内部怎么把电流变成力矩），下一篇是 [[Transmission2JointDynamics_gap]]（电机轴力矩怎么经丝杠+连杆变成关节力矩，含换向死区实验）；折算惯量的 worked example 在 [[LinkerSysId]]；整条链路的 gap 总图在 [[sim2real]]。

> [!tip] 读完你应该能回答
> 1. 策略在 20 Hz 发一个位置目标，到 `thumb_mcp` 电机轴真正出力，中间经过哪几级、每级各吃掉多少毫秒？哪一级是大头（提示：不是 CAN）？
> 2. 为什么固件电流环要跑到 kHz、速度环百 Hz、位置环几十 Hz——"内环快 5–10 倍"这个数字从相位裕度上怎么推出来？
> 3. §2.3 那个 $i_{cmd}=\frac{1}{K_tN}(K_pe+K_d\dot e+\tau_{ff})$ 和固件的三环之间是什么关系？它漏了什么？
> 4. SDK 的 `torque=100`、`speed=100`、反馈角度 0–255 分别是什么物理量？把它们当 N·m / rad·s⁻¹ / rad 拟合会出什么事？
> 5. 真机 RL 的观测里，哪些信号能当预测目标、哪些只能当输入特征？为什么电流推算的力矩排最后？

---

## 〇、边界：这份文档管什么

**为什么先讲这个**：本文档与 [[Transmission2JointDynamics_gap#〇、边界：这份文档管什么|Transmission gap §〇]] 是一对，两篇各管半条链，边界必须写在同一处公式上，否则读者会在两篇里看到同一现象的两种解释。

$$\tau_{joint} = \underbrace{\left( K_t i - J_m\ddot\theta_m - C_m\dot\theta_m \right)}_{\text{本文档：指令} \to \text{电机轴力矩}} \cdot \underbrace{N\eta - \tau_{fric}}_{\text{Transmission 文档：电机轴} \to \text{关节}}$$

| 符号 | 物理意义 | 单位 |
|:--|:--|:--|
| $i$ | 交轴电流 $I_q$（FOC 之后等效为直流电机电流） | A |
| $K_t$ | 力矩常数（随温度漂移，§4.3） | N·m/A |
| $J_m$, $C_m$ | 转子惯量、转子侧粘性系数 | kg·m², N·m·s/rad |
| $N$, $\eta$ | 电机轴→关节的等效减速比与传动效率 | –, – |
| $\tau_{fric}$ | 关节端折算的丝杠/减速箱摩擦（Stribeck） | N·m |

**遇到一个现象先判归属**（与 Transmission 文档同一张表，方向相反）：

| 现象 | 归属 | 判据 |
|---|---|---|
| **高速无力、长时间出力下降、指令高频成分被滤掉、命令与首动之间有固定延迟** | **本文** | 与速度 / 温度 / 通信时序相关，与运动方向无关 |
| 换向卡顿、阶梯响应、反驱不对称、单向自锁 | [[Transmission2JointDynamics_gap]] | 与 $\mathrm{sgn}(\dot q)$ 或外力方向绑定 |
| 起步后过冲 | 待判 | 随粘住时长增长 → 本文内环积分；否则 → Transmission §4.4 |

因此本篇 §五、§六 里原来的机械内容（DIP 耦合、丝杠推力、传动雅可比）**压缩为指路**，只保留边界上必须共用的公式。

---

## 一、 串级控制结构与物理方程

**为什么先讲这个**：固件把策略的位置目标变成电流，靠的是三个嵌套闭环。不把每一环的输入/输出写清楚，后面"延迟预算""为什么 RL 该输出位置而不是力矩"都没法说。这一节按被控对象 → 每一环 → 带宽分离 → 折叠成 §2.3 的公式，一步不跳。

### 1.1 电学方程（电流环被控对象）

从定子电压平衡出发（FOC 变换后 q 轴等效为一台直流电机，推导见 [[FOC_Control#二、 物理本源：定子方程与坐标系降维|FOC §二]]）：

$$U = L \frac{di}{dt} + R i + K_e \omega_m$$

$U$：驱动器施加的（q 轴）电压 [V]；$L$：绕组电感 [H]；$R$：绕组电阻 [Ω]；$K_e$：反电动势常数 [V·s/rad]，SI 单位下 $K_e = K_t$；$\omega_m$：电机轴角速度 [rad/s]。

> [!warning] 高速场景的电压饱和
> 手指快速伸展时 $K_e\omega_m$ 占掉大部分电压余量，剩给 $L\,di/dt$ 的电压变小，电流爬升率受限。RL 策略在高速状态下输出的高频力矩指令会被这个物理极限滤掉——表现为"软弱无力"。定量包络见 §4.4。

### 1.2 电磁力矩方程

空心杯/无槽电机在额定电流内磁路不饱和，电磁力矩与电流严格线性：

$$\tau_e = K_t\, i$$

### 1.3 机械动力学方程（速度环被控对象）

对转子做力矩平衡：

$$J_m\dot{\omega}_m = \tau_e - C_m\omega_m - \tau_d$$

$J_m$：转子惯量 [kg·m²]（L25 四指 $1.425\times10^{-7}$，拇指 $1.4\times10^{-10}$，来自 [[LinkerSysId]]）；$C_m\omega_m$：转子侧粘性摩擦 [N·m]；$\tau_d$：折算到电机轴的负载力矩 [N·m]——**这一项就是 §〇 公式里交给 Transmission 文档的那半边**，它把电机世界和刚体世界连起来。

### 1.4 三环串级：每一环的输入、输出、被控对象

固件的结构是标准串级（Cascaded Control）。**外环的输出是内环的参考值**，从外往里写：

**(a) 位置环**（输入：关节目标 $\theta_d$ 与反馈 $\theta$；输出：速度参考 $\omega_{ref}$）

$$e_\theta = \theta_d - \theta,\qquad \omega_{ref} = K_{p\theta}\, e_\theta + \dot\theta_d$$

$K_{p\theta}$ 单位 [1/s]；$\dot\theta_d$ 是目标的导数，作为速度前馈（很多固件省略它，只剩比例项）。位置环通常是纯 P：因为它的被控对象是"速度环 + 一个积分器（$\theta=\int\omega$）"，积分器已经自带一个零稳态误差的极点，再加 I 反而伤相位。

**(b) 速度环**（输入：$\omega_{ref}$ 与反馈 $\omega$；输出：电流参考 $i_{ref}$）

$$e_\omega = \omega_{ref} - \omega,\qquad i_{ref} = K_{p\omega}\, e_\omega + K_{i\omega}\!\int e_\omega\, dt$$

$K_{p\omega}$ 单位 [A·s/rad]。这里需要 I 项：由 §1.3，恒定负载 $\tau_d$ 要靠一个恒定电流 $i = \tau_d/K_t$ 顶住，纯 P 会留下 $e_\omega = \tau_d/(K_tK_{p\omega})$ 的稳态差，I 项把它积掉。

**(c) 电流环**（输入：$i_{ref}$ 与反馈 $i$；输出：电压 $U$）

$$e_i = i_{ref} - i,\qquad U = K_{pi}\, e_i + K_{ii}\!\int e_i\, dt \;(+\, K_e\omega_m \text{ 前馈})$$

$K_{pi}$ 单位 [V/A = Ω]。代回 §1.1：

$$L\frac{di}{dt} = K_{pi}(i_{ref}-i) + K_{ii}\!\int e_i - Ri - K_e\omega_m + (\text{前馈})$$

若固件做了反电动势前馈，$K_e\omega_m$ 被抵消；只看比例项时闭环是一阶系统：

$$\frac{i}{i_{ref}}(s) \approx \frac{K_{pi}}{Ls + (R + K_{pi})} \;\Rightarrow\; \omega_{bw,i} \approx \frac{R+K_{pi}}{L} \approx \frac{K_{pi}}{L}\quad (K_{pi}\gg R)$$

$\omega_{bw,i}$ 是电流环带宽 [rad/s]。空心杯电机 $L$ 极小（无铁芯），所以同样的 $K_{pi}$ 能换来 1–5 kHz 的电流环带宽——这是 [[Actuation#5.2 电流环带宽、交叉耦合与量化延迟|Actuation §5.2]] 里那句"空心杯电流环可达 kHz"的来源。

把三环串起来就是 [[Actuation#4. 串级控制：电流环 → 速度环 → 位置环|Actuation §4]] 的那条链：

$$\theta_d \xrightarrow{\text{位置环 P}} \omega_{ref} \xrightarrow{\text{速度环 PI}} i_{ref} \xrightarrow{\text{电流环 PI / FOC}} i \xrightarrow{K_t} \tau_e$$

### 1.5 为什么内环必须比外环快 5–10 倍

**直觉**：外环设计时把内环当成"我要多少它就立刻给多少"的理想环节。这个假设成立的条件是：在外环关心的频率上，内环的相位滞后可以忽略。

**推导**：把内环近似成一阶低通 $G_{in}(s)=\frac{1}{1+s/\omega_{in}}$（$\omega_{in}$ 是内环带宽）。它在频率 $\omega$ 处贡献的相位滞后是

$$\varphi_{in}(\omega) = -\arctan\!\left(\frac{\omega}{\omega_{in}}\right)$$

外环的穿越频率（crossover）记 $\omega_{c}$。外环的相位裕度（phase margin，定义见 [[ControlTheory#1.3 频率响应：Bode、相位裕度与带宽|ControlTheory §1.3]]）会被 $\varphi_{in}(\omega_c)$ 直接吃掉。代几个数：

| $\omega_{in}/\omega_c$ | 内环在 $\omega_c$ 处的相位滞后 | 含义 |
|:-:|:-:|:--|
| 1 | 45° | 相位裕度几乎被吃光，外环必振 |
| 3 | 18.4° | 勉强，参数稍漂就出问题 |
| **5** | **11.3°** | 工程下限：牺牲约 10° 裕度换"内环≈理想" |
| **10** | **5.7°** | 舒适区，外环可完全按理想内环设计 |

所以"5–10 倍"不是经验口诀，是"我愿意为内环付出 5–11° 相位裕度"的数值翻译。这一条同时也是 [[ControlTheory#7.4 反步法 (Backstepping)：为串级系统"逐级建 Lyapunov"|反步法]]里"上一级已收敛、可视为理想"假设的工程充分条件。

**对 L25 的量级**：电流环 kHz 级 → 速度环最多百 Hz 级 → 位置环最多几十 Hz 级。再往外一层是策略（20–50 Hz）：**策略的下发率已经和固件位置环带宽同一量级**，所以策略不能再指望位置环"瞬时跟上"——这就是 §4.2 延迟预算里 $T_f$ 那一项的根源。

> [!important] 仿真 PD 与真机三环的错位
> 仿真器把位控抽象成一个零延迟、无饱和的关节弹簧 $\tau = K_p(q_d-q)+K_d(\dot q_d-\dot q)$。真机里同一个 $q_d$ 要经过三个带宽各异的环、一个采样保持、一个规划平滑、一条串行总线才变成力矩。**这是本文档存在的原因。** 讲法上的对照见 [[FOC_Control#6.5 仿真 PD 与真机级联环的错位|FOC §6.5]] 与 [[Actuation#4. 串级控制：电流环 → 速度环 → 位置环|Actuation §4]] 的 important 框。

---

## 二、 电机参数到刚体动力学的完整映射

**为什么现在讲这个**：§一讲了电机轴上怎么产生力矩。策略与仿真器关心的却是**关节**力矩。这一节只把"电机轴 ↔ 关节"的两条映射写出来作为接口，细节全部交给 Transmission 文档。

### 2.1 运动学映射

电机角度/速度通过等效减速比 $N$（丝杠手上 $N=N_{eq}(\theta)$ 随构型变，推导见 [[LinkerSysId]]）映射到关节空间：

$$\theta_{joint} = \frac{\theta_m}{N}, \qquad \dot{\theta}_{joint} = \frac{\omega_m}{N}$$

### 2.2 动力学映射（力矩传递损耗与畸变）

$$\tau_{joint} = \left( K_t\, i - J_m \ddot{\theta}_m - C_m \dot{\theta}_m \right) N \eta - \tau_{fric}(\dot{\theta}_{joint})$$

- $J_m\ddot\theta_m$：转子惯量力矩。折算到关节端放大 $N^2$ 倍（$J_{eq}=N^2J_m$），四指 $N_{eq}\approx108$ 时 $J_{eq}\approx1.65\times10^{-3}$ kg·m²，急停/反转时可能比外部负载还大 → [[Actuation#7.2 Reflected Inertia：为什么减速比是把双刃剑|Actuation §7.2]]、[[LinkerSysId]]。
- $\tau_{fric}$：Stribeck 摩擦，按 $N^1$ 折算（不是 $N^2$）→ §5.2 与 [[Transmission2JointDynamics_gap#2.1 两个不同的幂次|Transmission §2.1]]。
- $\eta$：传动效率——丝杠（滚动体型式待核实：滚珠 / 滚柱）的效率随载荷与速度波动 → [[Actuation#8.2 三大非理想性——机械侧 gap 的主体|Actuation §8.2]]。

> [!warning] 修正
> 原文此处写作"$(\cdots-\tau_{fric})\cdot N\eta$"并称 $\eta$ 为"行星滚柱丝杠效率波动"。摩擦项放在括号里意味着它随 $N\eta$ 一起缩放，与 [[Transmission2JointDynamics_gap#2.1 两个不同的幂次|Transmission §2.1]] 实测的 $N^1$ 折算矛盾；现改为写在括号外、以关节端量表示，与 §〇 的边界公式一致。丝杠型式三处文档说法不一（滚珠/滚柱/行星滚柱），统一改为"待核实"。

### 2.3 控制架构：把 §1.4 的三环折叠成一个式子

**位置控制（PD + 动力学前馈）**：

$$i_{cmd} = \frac{1}{K_t \cdot N} \left( K_p(\theta_{jd} - \theta_j) + K_d(\dot{\theta}_{jd} - \dot{\theta}_j) + \tau_{ff} \right)$$

**它从哪来**：假设电流环远快于速度环、速度环远快于位置环（§1.5），则 $i\approx i_{ref}$，速度环的 I 项暂时忽略，把 §1.4(a) 代入 (b)：

$$i_{ref} = K_{p\omega}\big(\underbrace{K_{p\theta}e_\theta + \dot\theta_d}_{\omega_{ref}} - \omega\big) = K_{p\omega}K_{p\theta}\, e_\theta + K_{p\omega}(\dot\theta_d - \omega)$$

这正是一个 PD：$K_p^{(m)} \equiv K_{p\omega}K_{p\theta}$、$K_d^{(m)}\equiv K_{p\omega}$，量纲在**电机侧**、以电流为输出。要写成**关节侧、以力矩为量纲**的形式，用 §2.1 把误差换到关节角（$e_\theta^{(m)}=N e_\theta^{(j)}$），再把电流乘 $K_t$ 变力矩、乘 $N$ 变关节力矩：

$$K_p = K_tN^2K_{p\omega}K_{p\theta},\qquad K_d = K_tN^2K_{p\omega}$$

除回 $K_tN$ 就得到上面的 $i_{cmd}$ 公式。**三点提醒**：
1. 公式里的 $K_p, K_d$ 是"关节侧等效增益"，[[Transmission2JointDynamics_gap#4.3 拟合结果|Transmission §4.3]] 拟出来的 $k_p, k_d$ 就是它们，**不是**固件里真实的 $K_{p\theta},K_{p\omega}$；
2. 它把 $\eta$ 和 $\tau_{fric}$ 都当 1 和 0，所以它给的电流在真机上会差一个摩擦补偿量——正是 [[Transmission2JointDynamics_gap#1.1 三阶段换向|换向死区 $d_C=F_C/k_p$]] 的来源；
3. 它省掉了速度环的 I 项。粘住期间误差持续积分、释放后的过冲（Transmission §4.4 "待判"那一条）若存在，就来自这个被省掉的项。

**力矩控制**：
- **方案 A（无传感器）**：$i_d = \dfrac{\tau_{target}}{K_t N \eta}$——缺陷：$\eta$ 与 $\tau_{fric}$ 无法准确建模，且 $K_t$ 随温度漂移（§4.3）。
- **方案 B（力矩传感器闭环）**：在减速器输出端装 JTS，闭环消掉传动损耗，实现"透明化"刚体动力学控制 → [[Actuation#10.3 力矩传感器闭环 (JTS) 与数据驱动鲁棒证书|Actuation §10.3]]。L25 没有 JTS，所以本文档 §七 的结论是"电流推算力矩只能当输入特征"。

---

## 三、 L25 灵巧手 CAN 协议与可读取量分析

**为什么现在讲这个**：§一、§二假设"指令瞬时到达固件"。真机上指令要先排队、再上总线、再被 MCU 解析。这一节列出 SDK 层能读写什么、它们各自经过什么路径，是 §四延迟预算的素材。

L25 灵巧手通过 **CAN 总线**（1 Mbps）通信；本篇所述 **16 主动 DoF** 是用户手上这台 **L25NS** 的配置，分布在五根手指上（命名对照见 §3.5）。

| **类别** | **变量** | **读/写** | **单位/范围** | **关节数** | **实现机制** |
|:--|:--|:-:|:--|:-:|:--|
| 运动控制 | 关节角度 | R/W | 0-100 归一化 | 16 | 磁编码器/电位计绝对位置 |
| 运动控制 | 关节速度 | R/W | 0-100 归一化 | 16 | 固件内部速度环 PID |
| 运动控制 | 关节力矩 | R/W | 0-100 归一化 | 16 | 电流环近似模拟（$K_t \cdot I_q$） |
| 感知 | 触觉传感器 | R | uint8 矩阵 | 5×12×6 | 分帧传输，高密度薄膜阵列 |
| 感知 | 电机温度 | R | °C | 16 | NTC 热敏电阻 |
| 状态 | 故障代码 | R/W | 位掩码 | 16 | 堵转/过流/过温/通信异常 |

### 3.1 SDK 到硬件的时序链路

L25 的上位机控制并不是"策略输出后同时作用于 16 个关节"，而是一条串行通信链：

$$
\pi_\theta(o_t) \to a_t \to \text{SDK Manager} \to \text{CANMessageDispatcher} \to \text{CAN bus} \to \text{finger MCU} \to \text{FOC current loop}.
$$

- **宿主机阶段**：PC/4090 上的策略产生 $a_t$ 或 $\tau_{cmd}$ 后，SDK 将其写入 `_send_queue`；后台发送线程按 `SEND_INTERVAL_S = 0.0003s` 串行发送 CAN 帧。
- **总线阶段**：运动指令按手指分组封装，角度帧约为 `0x41-0x45`，速度帧约为 `0x49-0x4D`，力矩帧约为 `0x51-0x55`。CAN 1 Mbps 总线通过非破坏性仲裁保证高优先级帧不被低优先级帧破坏，但代价是多帧指令存在先后到达的相位差。
- **MCU 阶段**：手指内部 MCU 收到帧后，将归一化指令转为位置/速度/电流环参考值（§1.4 的 $\theta_d$ 入口），FOC 电流环在更高频率上闭合，具体电流到力矩链路见 [[FOC_Control#二、 物理本源：定子方程与坐标系降维|FOC 物理本源]]。

> [!important] 对 World Model 的含义
> 16 DoF 的控制写入在软件 API 上看似同步，真实硬件上却是按 CAN 帧串行落地。因此 [[Idea-002-Latency-Aware-Actuator|Latency-Aware Actuator]] 不应只建模一个全局 latency，而应至少保留"手指级/关节级执行时间戳"或其低维编码 $z_{\delta,t}$。

### 3.2 归一化指令不是物理量

SDK 的角度、速度、力矩接口都暴露为 $[0,100]$ 的归一化数值，并在 CAN 层线性映射为单字节原始值：

$$
u_{raw}=\operatorname{round}\left(255\cdot \frac{u_{sdk}}{100}\right),\qquad u_{sdk}=100\cdot \frac{u_{raw}}{255}.
$$

这意味着：

- `torque=100` 只是固件允许的最大电流/力矩百分比，不等价于固定的 N·m；它会随温度、转速、反电动势、丝杠摩擦和安全限流改变。
- `speed=100` 只是固件速度环的最大参考比例，不等价于固定 rad/s；高速区会被反电动势电压天花板截断。
- 任何把 SDK 百分比直接当作物理单位拟合的模型，都会把固件策略、硬件热状态和机械传动损耗混成一个不可解释黑箱。

Foundation 层的同一论断见 [[Actuation#11.2 归一化指令不是物理量|Actuation §11.2]]。

### 3.3 读取模式与观测可信度

SDK 提供三层读取模式：

| 模式 | 机制 | 适合用途 | 风险 |
|:--|:--|:--|:--|
| Polling | 后台线程按固定频率发送查询帧 | 长时间记录、低侵入数据采集 | 查询本身占用 CAN 带宽 |
| Blocking | 清空缓存后发送请求，等待对应回调唤醒 | 标定和单步诊断 | 阻塞时间包含总线排队与 MCU 响应 |
| Snapshot | 读取 `DataRelay` 中最近一次成功解析值 | RL 高频观测 | 可能混合不同手指的不同时刻数据 |

力觉数据最容易产生相位差：每指 72 字节触觉需要 12 个 CAN 帧拼接，且 `ForceSensorManager` 对不同手指请求加入约 2.5 ms 间隔。对真机 RL 而言，全手触觉矩阵不是同一物理时刻的严格同步快照，而是一个带时间戳结构的异步观测。

### 3.4 嵌入式概念闭环：MCU、STM32 与 CAN

MCU 是"把 CPU、存储器和外设集成在单芯片上"的实时控制计算机；STM32 是基于 ARM Cortex-M 的具体 MCU 产品族；CAN 是多个 MCU/驱动节点之间共享的抗干扰通信总线。三者在灵巧手中的角色是：STM32/同类 MCU 运行手指局部闭环（§1.4 的三环全部跑在这里），CAN 在上位机与各指节点之间传递命令和观测。Foundation 层概述见 [[Actuation#11. 接口层：嵌入式实现——MCU / STM32 / CAN|Actuation §11]]。

CAN 的可靠性来自差分信号：

$$
V_{diff}=V_{CAN\_H}-V_{CAN\_L}.
$$

若外部电磁噪声以共模形式叠加到两根线，$(V_{CAN\_H}+\Delta V)-(V_{CAN\_L}+\Delta V)=V_{diff}$，差分电压不变。CAN 的实时性则受位时序限制：

$$
BaudRate=\frac{1}{(1+t_{PROP}+t_{PHASE1}+t_{PHASE2})T_q}.
$$

因此，CAN 很可靠，但不是无限带宽、无限同步的"理想总线"。L25 的执行器模型必须同时接受"差分通信抗噪声强"和"多指高频观测/控制存在排队相位差"这两个事实。

**一帧要多久**：标准 CAN 2.0A 帧，8 字节数据时帧长 ≈ 108 bit（不含位填充）～最多约 130 bit（含填充）。1 Mbps 下**一帧 ≈ 0.11–0.13 ms**。这个数字在 §4.2 会反复用到——它说明 CAN 本身不是延迟大头。

### 3.5 关节命名对照：SDK 名 ↔ 本库论文/实验名

**为什么需要这张表**：SDK 与固件按手指分组、用 `abd / yaw / root1 / tip` 这类"位置名"；[[Transmission2JointDynamics_gap]]、[[LinkerSysId]]、[[MuJoCo_Sim2Real_Params]] 用的是解剖学名（`thumb_cmc_pitch`、`thumb_mcp`、`*_pip` …）。两套名字混用是本库现在最容易出错的地方。

| 手指 | SDK/固件名 | 解剖学名（本库实验文档用） | 驱动 | 备注 |
|:--|:--|:--|:--|:--|
| Thumb | `abd` | `thumb_cmc_yaw`（侧摆/外展） | 主动 | **以 SDK 为准，待核实**：`abd` 与 `yaw` 哪个对应 CMC 的掌侧外展、哪个对应侧摆，需上电逐关节验证 |
| Thumb | `yaw` | `thumb_cmc_pitch`（CMC 屈伸） | 主动，**丝杠后多一级 17:1 折返减速箱** | 同上，待核实 |
| Thumb | `root1` | `thumb_mcp` | 主动，**17:1 折返减速箱** | 换向死区实验对象（Transmission 文档） |
| Thumb | `tip` | `thumb_ip` | 主动 | 待核实是否主动 |
| Index/Middle/Ring/Pinky | `abd` | `*_mcp_abd`（侧摆） | 主动 | — |
| Index/Middle/Ring/Pinky | `root1` | `*_mcp`（MCP 屈伸） | 主动，四指电缸 $N_{eq}\approx108$ | — |
| Index/Middle/Ring/Pinky | `tip` | `*_pip` | 主动，四指电缸 | LinkerSysId 折算例 |
| Index/Middle/Ring/Pinky | （无） | `*_dip` | **被动**，连杆与 PIP 耦合 | 仿真中设 holonomic 约束（§5.1） |

- 主动 DoF 计数：拇指 4 + 四指 3×4 = **16**，与 SDK 帧 `0x41-0x45`（每指一帧）一致。被动 5 个的具体归属（4 个 DIP + 1 个拇指关节？）**待核实**——原文档写"5 个 DIP 关节为被动自由度"，但拇指没有 DIP，原样保留并标注。
- **实操规则**：凡在脚本、拟合表、MJCF 里出现的关节名，以 SDK 返回的顺序与命名为唯一真值；解剖学名只用于叙述。

### 3.6 8-bit 量化：命令与反馈共用一张栅格

§3.2 的映射意味着**角度命令和角度反馈都只有 255 级**：

$$q_{LSB} = \frac{\text{量程}}{255}$$

后果有三条，每条都会直接出现在 sim2real 里：
1. **比 1 LSB 小的命令增量到不了手**。策略网络输出的连续 action 在 SDK 里被 `round` 掉，等效于一个死区宽 $q_{LSB}$ 的量化器串在位置环前面。
2. **反馈里 ±0.5 LSB 的量化噪声被差分放大**。以 20 Hz 差分求速度，噪声幅值 $\approx q_{LSB}\times 20 = 20\,q_{LSB}$ rad/s——这是 §7.1 建议用 KF 或序列模型而非直接差分的量化根据。
3. **换向死区用 LSB 来衡量才有意义**。[[Transmission2JointDynamics_gap]] 实测 `thumb_mcp` 死区总宽 24.1 mrad = 4.92 LSB，反推该关节 $q_{LSB}\approx4.9$ mrad（量程 ≈ 1.25 rad，待核实）；死区若小于 1 LSB 就根本观测不到，这决定了激励轨迹必须在字节域上整数步进（Transmission §7.3）。

采样与量化的一般理论见 [[SignalProcessing#1.1 采样与混叠：离散化不是无损记录|SignalProcessing §1.1]]。

---

## 四、 电气与传感特征的带宽瓶颈

**为什么现在讲这个**：有了 §一的环路结构和 §三的通信结构，可以把"一条指令从策略到电机轴要多久"逐项列出来。这张表是 [[Idea-002-Latency-Aware-Actuator]] 和 Transmission 文档 $T_d$、$T_f$ 两个参数的物理出处。

### 4.1 高频感知的总线瓶颈

- 全手力觉数据 360 字节/次，CAN 1 Mbps 下占据显著总线带宽：360 字节 = 5 指 × 12 帧 = 60 帧 ≈ 60 × 0.12 ms ≈ **7 ms 纯总线时间**，再叠加下一条的指间间隔。
- `ForceSensorManager` 强制 2.5 ms 指间请求延迟（MCU 处理上限），力觉反馈存在"指间相位差"：第 5 指比第 1 指晚 4 × 2.5 = **10 ms**，一轮全手触觉 ≥ 12.5 ms。

### 4.2 延迟预算表：从策略到电机轴

把 §三的各级按发生顺序排开，每级给出量级与出处。**$T_d$ = 首动延迟（纯传输）**，**$T_f$ = 相位滞后（预滤波）**，二者在 [[Transmission2JointDynamics_gap#4.2 一个必须补上的自由度：$T_f$|Transmission §4.2]] 里必须分列，这里给出它们各自由哪几行相加而来。

| # | 环节 | 机制 | 量级 | 归入 | 出处 |
|:-:|:--|:--|:--|:-:|:--|
| 1 | 策略下发采样保持 | 位置命令 20–50 Hz 零阶保持，平均等待半个周期 | 10–25 ms（均值），0–50 ms（最坏） | 相位 | 部署口径 20 Hz / 50 Hz |
| 2 | SDK 发送队列 | `_send_queue` 串行，`SEND_INTERVAL_S = 0.3 ms`/帧 × 帧数 | 5 帧角度 = **1.5 ms**；若同周期再发速度/力矩帧，× 2–3 | $T_d$ | §3.1 |
| 3 | CAN 帧传输 | 1 Mbps，8 字节帧 ≈ 108–130 bit | **0.11–0.13 ms/帧**，5 帧 ≈ 0.6 ms | $T_d$ | §3.4 |
| 4 | CAN 仲裁抖动 | 高优先级帧插队、触觉帧占线 | 0 – 数 ms（随总线负载） | $T_d$（随机） | §3.1、§4.1 |
| 5 | MCU 解析 + 位置环采样 | 位置环几十 Hz 级采样 | ≲ 数 ms | $T_d$ | §1.5 |
| 6 | **MCU 规划平滑（S 曲线 / 低通）** | 固件对目标做插值/滤波，**首动不推迟，相位大量滞后** | **可达 ~150 ms；chirp 实测 $T_f\approx120$ ms** | **$T_f$** | [[LinkerSysId]] 警告、Transmission §4.2 |
| 7 | 速度环 + 电流环建立 | 百 Hz / kHz 带宽的一阶滞后 | 1–3 ms / < 0.5 ms | 相位 | §1.4–1.5 |
| 8 | 反馈读回 | 查询帧 + MCU 响应 + 解析 | **~15–20 ms** | 观测延迟 | SDK 实测 |
| 9 | 触觉读回 | 12 帧/指 + 2.5 ms 指间间隔 | 全手 ≥ 12.5 ms，指间相位差 10 ms | 观测延迟 | §4.1 |

**读表的方法**：
- 把 #2–#5 相加得到**首动延迟** $T_d\approx 2\text{–}5$ ms，与 Transmission 文档阶跃直测的 $T_d\lesssim10$ ms 一致，**四指与拇指同量级**（[[Transmission2JointDynamics_gap#六、被推翻的猜想|被推翻的猜想 #4]]：拇指 45 ms 是把死区的常数相位误当成了传输延迟）。
- **大头是 #6**：$T_f\approx120$ ms 比整条通信链大两个数量级。仿真里若只加一个"延迟 N 步"的纯传输延迟而不加一阶预滤波，高频幅值比会差 2.5 倍（Transmission §4.3 的 2.584 → 0.940）。
- #1 与 #8 决定了策略看到的是"20–40 ms 前的手"，这是 [[ReinforcementLearning#2.1 MDP 与 POMDP：把"试错"写成数学|POMDP]] 意义下的观测延迟，靠 §7.1 的历史序列输入吸收。
- #4 是唯一**随机**项，也是 [[Idea-002-Latency-Aware-Actuator]] 要用 $z_{\delta,t}$ 编码的对象。

> [!important] 对仿真的直接指令
> 在 mjlab / Isaac Gym 里复现 L25 位控，至少要串三样东西：**零阶保持（20–50 Hz）→ 一阶低通 $T_f\approx120$ ms → 纯延迟 $T_d\approx10$ ms → PD**。缺第二样，阶梯响应做不出来；具体配方见 [[Transmission2JointDynamics_gap#5.1 配方|Transmission §5.1]] 与 [[MuJoCo_Sim2Real_Params]]。

### 4.3 热漂移与 $K_t$ 不稳定性

空心杯电机无铁芯、转子热容极小。温度升高时绕组电阻增大（$R_s$ @80°C 约 +31%），永磁体磁链下降（$K_t$ @80°C 约 −9.6%），相同电流指令产生的物理力矩因 $K_t(T)$ 衰减而漂移，且 $R_s\uparrow$ → 同力矩需更大电流 → 铜损 $I^2R$ 更大 → 温度更高，构成正反馈热失控环路。详见 [[FOC_Control#四、 温度对电机模型参数的系统性影响|FOC §四]] 与 [[Actuation#6.1 两个漂移源与热失控环路|Actuation §6.1]]。时间尺度：热时间常数分钟级，远慢于 RL 的控制周期，所以温度是"缓变的隐参数"而非"状态"——这是 §7.3 把 $T_{motor}$ 当显式输入的理由。

### 4.4 反电动势与速度-力矩包络

由 §1.1，稳态下 $U_{max}\ge Ri + K_e\omega_m$，可用电流上限 $i_{max}(\omega_m) = (U_{max}-K_e\omega_m)/R$，于是可用力矩随转速线性下降：

$$\tau_{max}(\omega_m) = K_t\,\frac{U_{max}-K_e\omega_m}{R}$$

高速拨动时 Back-EMF 抵消驱动电压，形成非线性的转矩-转速饱和区。详见 [[FOC_Control#5.1 反电动势电压天花板与弱磁区域|FOC §5.1]]。

---

## 五、 机械传动与耦合非线性（指路）

**为什么只指路**：按 §〇 的边界，这一节的内容属于电机轴之后的世界。这里只保留两处入站锚点与其它文档共用的最小公式，细节去 [[Transmission2JointDynamics_gap]] 与 [[LinkerSysId]]。

### 5.1 16 主动 + 5 被动 DOF 的耦合结构

- Thumb：4 主动 DoF（`abd, yaw, root1, tip`）；其余四指：各 3 主动 DoF（`abd, root1, tip`）——命名对照见 §3.5。
- **DIP 耦合**：DIP 关节为被动自由度，通过连杆与 PIP 机械耦合（$\theta_{DIP} = f(\theta_{PIP})$），在 Rigid Dynamic Model 中必须设为 holonomic constraint（完整/非完整之分见 [[Dynamics#4.1 Pfaffian 约束与完整/非完整之分|Dynamics §4.1]]）。"5 个被动"的具体归属待核实（§3.5）。

### 5.2 丝杠传动的 Stribeck 摩擦

丝杠（滚动体型式待核实：滚珠 / 滚柱）在速度过零点时存在明显静摩擦（stiction）。低力矩指令被静摩擦吞噬导致手指不动，突破后突然滑动——产生 stick-slip 跳变。关节端折算的摩擦模型：

$$\tau_{fric}(\dot{\phi}) = \left[F_c + (F_s - F_c)e^{-|\dot{\phi}/v_s|^{\delta_s}}\right]\text{sign}(\dot{\phi}) + B_v \dot{\phi}$$

$F_c$：库仑摩擦 [N·m]；$F_s$：静摩擦 [N·m]；$v_s$：Stribeck 速度 [rad/s]；$\delta_s$：形状指数；$B_v$：粘性系数 [N·m·s/rad]。

> [!warning] 修正
> 原文此处断言"行星滚柱丝杠 … 巨大静摩擦"。L25 丝杠的滚动体型式在本库三份文档里说法不一，未经核实；且 [[Transmission2JointDynamics_gap#1.3 主要矛盾：阶梯的主体是死区**总宽**，不是 $F_S/F_C$ **比值**|Transmission §1.3]] 实测表明 $F_s/F_c\le1.5$，"巨大"并不成立——**阶梯响应的主体是 $N_{eq}$ 把死区总宽放大，不是 $F_s$ 本身大**。自锁/反驱结论依赖滚动体型式（滑动 $\mu\approx0.15$ 自锁，滚动 $\mu\approx0.005$ 可反驱），见 [[Transmission2JointDynamics_gap#2.4 自锁：为什么拇指掰不动|Transmission §2.4]]。

**去哪深挖**：三阶段换向与 $d_C=F_C/k_p$ → Transmission §1.1；$F_s$ 只需两个参数 → Transmission §三；仿真只有库仑型 `frictionloss`、没有 Stribeck → Transmission §5.2 与 [[sim2real]]。

---

## 六、 World Model 信息流重构（指路 + 本篇负责的畸变）

**为什么现在讲这个**：WMTS 的 Actuator Model（[[Final_WMTS#4.A Actuator Model：指令 → 关节力矩|WMTS §4.A]]）需要知道"指令到关节力矩"有几级非线性、每级由哪篇文档负责建模。

### 6.1 电磁力矩 → 直线推力（丝杠级）

$$F_{linear} = \frac{2\pi \eta}{l} \tau_m - F_{friction}(\dot{x}, T)$$

$l$：丝杠导程 [m]（四指 0.7 mm、拇指 0.6 mm）。这是 [[LinkerSysId]] 旋转→直线折算的出发点，本篇不展开。

### 6.2 直线推力 → 关节力矩（连杆耦合）

$$\tau_{joint} = J^T(x) \cdot F_{linear}$$

传动雅可比 $J(x)$ 随构型时变（$N_{eq}(\theta)=2\pi r(\theta)/l$），DIP-PIP 耦合使外力通过连杆逆向改变等效惯量和摩擦分布 → [[LinkerSysId]]、[[Transmission2JointDynamics_gap]]。

### 6.3 高动态操控的关键畸变

1. **Back-EMF 硬截断**（本篇 §4.4）：$U_{max} \ge L(T) \frac{di_q}{dt} + R(T) i_q + K_e \omega_m$ → 高速下电流爬升受限。
2. **$K_t(T)$ 热衰减**（本篇 §4.3）：$R_s$ @80°C +31%、$K_t$ @80°C −9.6% → 正反馈热失控环路。
3. **通信与规划滞后**（本篇 §4.2）：$T_d\approx10$ ms 纯延迟 + $T_f\approx120$ ms 预滤波 + 20–50 Hz 采样保持。
4. **传动比角度依赖**（Transmission 文档）：丝杠和 PIP/DIP 强耦合连杆的 Jacobian 与静摩擦高度依赖当前手指弯曲角度。

> [!warning] 修正
> 原文 §6.3 只列了 1、2、4 三条，把通信/规划延迟完全漏掉；而 Transmission 文档的拟合表明 $T_f$ 是高频幅值比误差的**全部来源**。现补为第 3 条。

---

## 七、 RL State Space 设计法则

**为什么现在讲这个**：前六节列出了从指令到力矩的全部污染源。这一节回答"哪些信号污染少到可以当观测/预测目标"。

> [!tip] 核心原则
> **绝对不要将底层电流推算的力矩作为高权重或可信的观测状态**。因为该力矩在传递到指尖之前已被热漂移 $K_t(T)$、丝杠静摩擦、非线性 Jacobian 和连杆弹性形变严重"污染"。Foundation 层论证见 [[Actuation#10.2 力矩反馈为何"能当输入、不能当目标"|Actuation §10.2]]。

### 7.1 刚性状态：关节角度与速度

- **$\theta_{meas}$ (16D)**：编码器位置——唯一的运动学 Ground Truth（⭐⭐⭐⭐）。注意它是 8-bit（§3.6），分辨率 $q_{LSB}$。
- **$\dot{\theta}_{meas}$ (16D)**：差分求速度噪声大（§3.6 第 2 条：$\approx20\,q_{LSB}$ rad/s），建议引入 KF（[[SignalProcessing#1.4 数字滤波器：去噪、延迟与可控性的三角权衡|SignalProcessing §1.4]]）或将历史角度序列 $[\theta_{t-k}, \ldots, \theta_t]$ 输入 RNN/Transformer（⭐⭐⭐）。历史序列同时吸收 §4.2 的观测延迟。

### 7.2 接触状态：高维触觉传感

- **$F_{tactile}$ (5×12×6)**：摒弃基于电流的接触力估算；直接使用高密度触觉阵列数据——提供接触法向量、物体局部曲率和滑动趋势（⭐⭐⭐⭐）。但要记住它是异步快照（§3.3、§4.1），指间相位差 10 ms。理论定位见 [[ReinforcementLearning#8.1 状态表征：触觉是灵巧操作的"暗感官"|RL §8.1]]。

### 7.3 隐式动力学状态：温度与时序

- **$T_{motor}$ (16D)**：温度是系统时变动力学参数的隐变量。网络通过 $T$ 隐式学习当前电机的阻力和出力上限，实现自适应控制（⭐⭐⭐⭐）。
- **$z_{\delta,t}$**：最近若干帧的执行时间戳 / 指间相位差低维编码（§3.1、§4.2 #4），喂给 Actuator Net（[[Actuation#10.1 Actuator Net：学"仿真 PD 没覆盖的那段残差"|Actuation §10.1]]）。

| 信号 | 可靠性 | 推荐用途 |
|:--|:-:|:--|
| 关节角度 $\phi_t$ | ⭐⭐⭐⭐ | **RL 核心观测 + WM 预测目标** |
| 触觉矩阵 $(12\times 6)_{\times 5}$ | ⭐⭐⭐⭐ | **RL 核心观测 + 接触判断** |
| 角速度 $\dot{\phi}_t$ | ⭐⭐⭐ | RL 观测（需滤波） |
| 反馈力矩 $\tau_{fb}$ | ⭐⭐ | Actuator Model 输入特征（**非** reward/预测目标） |
| 温度 $T_{motor}$ | ⭐⭐⭐⭐ | Actuator Model 显式输入 |
| 执行时间戳编码 $z_{\delta,t}$ | ⭐⭐⭐ | Actuator Model 显式输入 |

---

## 八、 （进阶可选）数据驱动鲁棒控制视角：从短真机轨迹到安全证书

> [!note] 这一节买到什么，先用一句大白话说
> 前七节教你怎么**拟合**一个 actuator model；但拟合得再好，也只能说"在采过的数据上误差小"，说不了"没采到的工况下策略会不会把手指撞坏"。本节的工具（数据一致集 + LMI）回答的是后一个问题：**用 5–10 分钟真机数据，能不能证明"所有与这些数据一致的执行器模型"都被同一个局部控制器镇定**。能 → 得到一张安全证书；不能 → 告诉你缺哪类数据。它不改变前七节的建模，只在其上多加一道验收。第一次读可以跳过，做真机适配实验前再回来。
>
> 教科书参考：[[ControlTheory#13. 数据驱动控制：模型不准时如何仍给稳定性证书|ControlTheory §13]]，源自 [[Books/Data-based linear systems and control theory.pdf]] Chapter 3.6-3.7 的数据一致集与 LMI 证书思想。

执行器模型的难点不是"能不能拟合一条轨迹"，而是：**在 CAN 抖动、温度漂移、丝杠摩擦和触觉噪声都存在时，短真机数据能否证明一个局部控制器对所有可能真实模型都安全**。

对 L25 手，可以在每个局部工况下定义近似线性状态：

$$
x_t=[\phi_t,\dot\phi_t,T_t,z_{\delta,t}],\quad u_t=a_t,
$$

其中 $z_{\delta,t}$ 是最近若干帧 CAN latency / 指间相位差的低维编码（§7.3）。短真机轨迹形成输入-状态数据矩阵：

$$
X_+ = A X_- + B U_- + W_-.
$$

这里 $W_-$ 不是"坏掉的数据"，而是把未建模物理显式纳入证书的噪声集合——**每一项都能在前面的章节里找到出处**：

- **通信噪声**（§3.1、§4.2 #4）：CAN 仲裁与分帧触觉造成的相位不一致
- **电气漂移**（§4.3）：$K_t(T)$ 与 $R_s(T)$ 的温度依赖
- **传动非线性**（§5.2 → Transmission 文档）：Stribeck 静摩擦、丝杠效率波动、连杆柔性
- **估计误差**（§3.6、§7.1）：差分速度与触觉接触定位的噪声

若噪声集合满足 $W_-W_-^\top\preceq T\epsilon I$ 或更精细的各向异性 QMI，则可用 Matrix S-lemma 把"无穷多一致模型都满足 Lyapunov 条件"收成一个有限维 LMI，检查是否存在共同 Lyapunov 矩阵 $P\succ0$（推导见 [[ControlTheory#13. 数据驱动控制：模型不准时如何仍给稳定性证书|ControlTheory §13]]）。这使 [[Idea-002-Latency-Aware-Actuator|Latency-Aware Actuator]] 的 "5 min real adaptation" 多了一层硬判据：

> [!important] 实验判据
> 适配后的 Actuator Model 不只报告预测 MSE，还应报告数据驱动 LMI 是否可行。若不可行，说明 scripted motion 没有充分激发执行器模式，或噪声界设得过窄；此时应优先补采高/低速、升温、过零 stick-slip 三类轨迹（与 [[Transmission2JointDynamics_gap#7.3 还缺什么：不是缺激励，是缺一维|Transmission §7.3]] 的"缺一维"结论互为印证），而不是盲目加大网络容量。

---

## 回扣与承接

用 L25 的**一根手指**把本篇走一遍：空心杯电机 → 丝杠电缸 → 连杆 → 关节；拇指的 `thumb_mcp` 在丝杠前多一级 17:1 折返减速箱。

1. **策略下发**（§4.2 #1）：20 Hz 给 `thumb_mcp` 一个位置目标 0–100，SDK 先 `round` 成 0–255 的一个字节（§3.2、§3.6）——比 4.9 mrad 小的增量在这里就消失了。
2. **排队上线**（§3.1、§4.2 #2–#4）：进 `_send_queue`，每 0.3 ms 出一帧，拇指帧 `0x41` 先走；总线上一帧 0.12 ms；若此时 `ForceSensorManager` 正在拉 60 帧触觉，等待时间不定——这就是 $z_{\delta,t}$ 要编码的抖动。
3. **MCU 平滑**（§4.2 #6）：手指 MCU 把新目标塞进 S 曲线/低通，**首动 ≲10 ms 就开始，但相位要拖 ~120 ms**——阶梯响应的高频幅值比全靠这一项。
4. **三环落地**（§1.4）：平滑后的 $\theta_d$ 进位置环出 $\omega_{ref}$，速度环出 $i_{ref}$，kHz 电流环把 $i$ 压到 $i_{ref}$，转子上出现 $\tau_e=K_ti$。电流环快过速度环快过位置环各 5–10 倍（§1.5），所以外面看到的就是 §2.3 那个等效 PD。
5. **本篇到此为止**：转子力矩减去 $J_m\ddot\theta_m$、$C_m\dot\theta_m$ 之后交出去（§〇）。若手指跑久了变软——回 §4.3 看温度；若高速伸展无力——回 §4.4 看反电动势。
6. **下一篇接手**：$\tau_e$ 经 17:1 减速箱、丝杠、连杆到关节，摩擦按 $N^1$、惯量按 $N^2$ 折算，$N_{eq}\approx1400\sim1800$ 把 $F_C+F_S$ 撑成 24 mrad 死区 → [[Transmission2JointDynamics_gap]]；数字怎么算 → [[LinkerSysId]]；进 MJCF 怎么写 → [[MuJoCo_Sim2Real_Params]]；整条链的 gap 地图 → [[sim2real]]。

---

## 对开发与科研的启示

1. **仿真位控必须补 $T_f$**：延迟预算表说明规划平滑（~120 ms）比整条通信链大两个数量级。这意味着下一步可以在 mjlab 的 actuator 配方里把"零阶保持 → 一阶低通 → 纯延迟 → PD"做成标准模块，并用 chirp 频响做验收，而不是只比阶跃首动时刻。
2. **策略输出位置而非力矩，是有定量理由的**：三环带宽分离让位置伺服吸收了 kHz–百 Hz 段的硬件非线性；策略只需面对 $T_f$ 与死区。这意味着 WMTS 的 Actuator Model 应把"位置目标 → 关节角"作为主映射，把力矩接口留给 §八的鲁棒验收。
3. **$z_{\delta,t}$ 是可以直接采的**：SDK 层能拿到每帧的发送/回调时间戳，CAN 仲裁抖动是预算表里唯一随机项。这意味着 [[Idea-002-Latency-Aware-Actuator]] 的第一版不需要学一个 latency 分布，先把时间戳当特征喂给 Actuator Net 做消融即可。
4. **关节命名要在代码里冻结**：§3.5 那张表有多处"待核实"。这意味着下一次上电的第一件事是逐关节单步、把 SDK 索引 ↔ 解剖学名 ↔ MJCF 名写进一个唯一的映射文件，所有脚本从它读。
