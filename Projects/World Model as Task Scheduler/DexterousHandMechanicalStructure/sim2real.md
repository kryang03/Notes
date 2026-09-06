---
tags:
  - sim-to-real
  - dexterous-hand
  - mechanical-design
  - reinforcement-learning
  - linkerhand-l25
aliases:
  - Sim-to-Real Gap 分析
  - sim2real gap
  - 仿真到真机迁移
  - 灵巧手 gap 总图
related:
  - "[[Actuation]]"
  - "[[传动]]"
  - "[[电机]]"
  - "[[减速器]]"
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[FOC_Control]]"
  - "[[Actuator2RigidDynamicsModel_gap]]"
  - "[[Transmission2JointDynamics_gap]]"
  - "[[MuJoCo_Sim2Real_Params]]"
  - "[[LinkerSysId]]"
---

# 灵巧手 Sim-to-Real Gap 总图：从电流到接触的四层分流

> [!abstract] 本篇在链路中的位置
> 这是三个 tutorial 文件夹的**总图**，不深挖任何一层，只做两件事：(1) 把"仿真直接给关节施加 $\tau_{sim}$"与"真机上 $\tau_{joint}$ 要穿过 电气/热 → 减速/传动 → 固件位控环+通信 → 接触 四层"之间的差异**按层列清楚**；(2) 每层结尾告诉你**深挖去哪篇**。上一篇是三份硬件基础（[[电机]]、[[减速器]]、[[传动]]），下一篇按你要深挖的层分流：驱动层去 [[FOC_Control]]，指令→电机轴去 [[Actuator2RigidDynamicsModel_gap]]，电机轴→关节去 [[Transmission2JointDynamics_gap]]（worked example 在 [[LinkerSysId]]），引擎参数落地去 [[MuJoCo_Sim2Real_Params]]。Foundation 层面的同一张图见 [[Actuation#9. 迁移层 I：执行器 Sim-to-Real gap 的完整解剖|Actuation §9]]。

> [!tip] 读完你应该能回答
> 1. 对 L25 这类"空心杯直线电缸 + 丝杠 + 连杆、8-bit 位控"的手，四层里**哪一层的 gap 最大**？为什么不是电气层？
> 2. 一条 20–50 Hz 的位置指令从 SDK 发出到关节真正动，延迟预算里哪一项占大头？这对 RL 的 action delay randomization 意味着几步？
> 3. 为什么 L25 / Ability / Inspire 这类手的 RL 策略应该输出**位置目标**而不是力矩，而 QDD 手可以输出力矩？
> 4. Isaac Gym 的 `dof_props['friction']` 和 MuJoCo 的 `frictionloss` 分别是什么摩擦？为什么它们都表达不了换向死区？
> 5. Domain Randomization、白箱系统辨识、Actuator Net 三条路线各自适合在什么时候上？

---

## 0. 总图：四层 gap 与分流表

**为什么先给总图**：后面每一层都能写成一篇独立文档，读者最容易在细节里迷路。先记住这张表，再进任何一层。

真机上一条 RL action 到关节力矩要走的链路：

```
RL action (位置目标 q*, 20–50 Hz, 8-bit)
   │  ④ 通信/延迟/量化：SDK 队列 → CAN 1 Mbps → 指节 MCU 平滑/位控环
   ▼
固件级联环：位置环 → 速度环 → 电流环 (FOC)
   │  ① 电气/热：K_t I，电感延迟，反电动势天花板，K_t(T)、R(T) 漂移
   ▼
电机轴力矩 τ_m
   │  ② 减速/传动：丝杠 N_eq、效率 η、Stribeck/死区、背隙、扭转弹性、连杆 N_eq(θ)
   ▼
关节力矩 τ_joint
   │  ③ 接触：μ、接触刚度/阻尼、接触几何、触觉延迟
   ▼
物体运动
```

| 层 | 仿真里的假设 | 真机上多出来的东西 | L25 上的严重程度 | 深挖去哪篇 |
|:--|:--|:--|:--|:--|
| ① 电气 / 热 | $\tau=K_t I$ 瞬时、$K_t$ 恒定、力矩上限恒定 | 电感时间常数、齿槽、反电动势限速、$R_s(T)\uparrow$、$\psi_m(T)\downarrow$ 热降额 | **低**（空心杯 $\tau_e\sim0.1$ ms，远快于 20–50 Hz 指令），长时间运行才显热 | [[FOC_Control]] §四、§5.1；[[Actuation#5. 电气极限层：高速时力矩为什么"软"\|Actuation §5]]、[[Actuation#6. 热漂移层：为什么跑久了力矩变小\|§6]] |
| ② 减速 / 传动 | 零背隙、零/线性摩擦、刚性、$\tau_{joint}=\tau_{sim}$ | $N_{eq}\approx108$（拇指 1424/1800）把摩擦按 $N^1$、惯量按 $N^2$ 放大；换向三阶段死区；反驱不对称/自锁 | **高**（换向阶梯是真机实测的主要矛盾） | [[Transmission2JointDynamics_gap]]、[[LinkerSysId]]、[[Actuator2RigidDynamicsModel_gap#5.2 丝杠传动的 Stribeck 摩擦\|Actuator gap §5.2]]、[[Actuation#7.2 Reflected Inertia：为什么减速比是把双刃剑\|Actuation §7.2]] |
| ④ 固件位控环 + 通信 / 延迟 / 量化 | 仿真 PD 零延迟、连续值、每步生效 | 8-bit 0–255 指令/反馈栅格、20–50 Hz 采样保持、CAN 串行、MCU 平滑 ≤150 ms、级联环黑箱 | **高**（延迟预算与量化步长都比机械背隙大一个量级，且原文档完全没写） | 本篇 §4（首次系统写出）；[[Actuator2RigidDynamicsModel_gap#三、 L25 灵巧手 CAN 协议与可读取量分析\|Actuator gap §三]]、[[FOC_Control#6.5 仿真 PD 与真机级联环的错位\|FOC §6.5]] |
| ③ 接触 | 点接触、恒定 $\mu$、刚性或单一 solref | 软指接触斑、$\mu$ 随材料/温度变、接触几何误差、触觉 12 帧拼接的异步 | **中**（与关节摩擦互相掩盖，标定顺序有讲究） | [[ContactMechanics#7. Sim-to-Real 与工程实现\|ContactMechanics §7]]、[[MuJoCo_Sim2Real_Params]] §六 |

> [!important] 一句话结论
> 对 L25 这类手，**gap 的主体不在电机而在"丝杠传动 + 固件位控环"**。原文档把注意力放在电机/减速器类型上，那是对无框力矩电机、QDD 手成立的视角；对丝杠位控手，电气层几乎可以忽略，机械死区与固件延迟/量化才是要建模、随机化或辨识的对象。

---

## 1. 仿真器的理想化假设与完整链路模型

**为什么现在讲这个**：后面四层的每一条 gap，都是对下面这张"理想化假设表"某一行的违反。先把假设列全，后面就有了对照表。

### 1.1 IsaacGym / MuJoCo 的关节力矩模型

主流物理仿真器中，RL 策略输出的 action 被解释为**关节力矩** $\tau$ 或**关节目标位置** $q^*$（由仿真 PD 转成力矩），直接施加于刚体关节：

$$
M(q)\ddot{q} + C(q,\dot{q})\dot{q} + g(q) = \tau_{sim}
$$

- $M(q)$：关节空间惯量矩阵（kg·m²）；$C(q,\dot q)\dot q$：科里奥利/离心项（N·m）；$g(q)$：重力项（N·m）；$\tau_{sim}$：仿真施加的关节力矩（N·m）。

隐含的理想化假设：

| 假设 | 仿真中的处理 | 真机现实 | 属于哪一层 |
|-----|-----------|---------|:--:|
| 力矩瞬时施加 | $\tau$ 在每个仿真步直接生效 | 电机有电气/机械时间常数 | ① |
| 力矩上限恒定 | `effort_limit` 常数 | 连续运行后热降额；高速时反电动势限流 | ① |
| 零背隙 | 关节力矩-角度为单值映射 | 减速器/连杆存在背隙死区 | ② |
| 零摩擦或简单摩擦 | 无摩擦、库仑或粘滞 | Stribeck 非线性 + 换向死区 | ② |
| 刚性关节 | 无弹性变形 | 谐波柔轮/腱绳/连杆有弹性 | ② |
| 完美力矩传递 | $\tau_{joint}=\tau_{sim}$ | $\tau_{joint}=\eta\, i\, \tau_{motor}-\tau_{friction}$ | ② |
| 独立关节 | 各关节独立驱动 | 欠驱动耦合、腱绳交叉耦合 | ② |
| 指令连续、零延迟、每步生效 | 仿真 PD 直接读浮点 $q^*$ | 8-bit 量化、20–50 Hz 采样保持、CAN 串行、MCU 平滑 | ④ |
| 接触参数已知恒定 | 单一 $\mu$、solref | $\mu$ 随材料/温度/污染变，触觉异步 | ③ |

### 1.2 力矩传递链路的完整模型

把四层串起来，真实关节力矩写成：

$$
\tau_{joint}(t) = \eta(T,\dot q)\cdot i\cdot K_t(T)\cdot I\!\left(u_q\!\left(t-\delta\right)\right) - \tau_{friction}(\dot q, T) - k(\theta_{twist})\,\theta_{twist}
$$

逐项读：
- $u_q(t-\delta)$ — 经过 8-bit 量化 $Q_{255}(\cdot)$ 与总延迟 $\delta$ 后到达固件的位置指令（层 ④）；固件级联环再把它变成电流 $I$。
- $K_t(T)$ — 力矩常数（N·m/A），随永磁体温度下降（层 ①）。
- $\eta(T,\dot q)$ — 传动效率（无量纲），温度与速度相关；$i$ — 减速比（丝杠手用 $N_{eq}$）（层 ②）。
- $\tau_{friction}(\dot q,T)$ — Stribeck 摩擦力矩（N·m），含静摩擦 $F_S$ 与库仑 $F_C$（层 ②）。
- $k(\theta_{twist})\theta_{twist}$ — 传动扭转弹性造成的力矩损失，$k$ 为非线性扭转刚度（N·m/rad）（层 ②）。

仿真器把这整条链压成 $\tau_{sim}=\tau_{joint}$。**下面四节分别拆开每一层。**

---

## 2. 第 ① 层：电气 / 热

**为什么现在讲这个**：这一层是原文档的重点，但对 L25 反而是最轻的一层。先讲它，是为了让你能自信地把它"排除"——知道为什么能忽略，比知道要忽略更重要。

### 2.1 各电机类型的 Gap 来源

| 电机类型 | 力矩线性度 | 响应延迟 | 齿槽干扰 | 热漂移 | Sim-to-Real 友好度 |
|---------|----------|---------|---------|-------|-----------------|
| [[电机#1. 有刷直流电机 (Brushed DC Motor)\|有刷直流电机]] | 高（$\tau = K_t I$） | 中（电感+机械） | 无 | 中（电刷磨损） | ⭐⭐⭐ |
| [[电机#2. 无刷直流电机 (BLDC Motor)\|BLDC (FOC)]] | **极高** | **极低**（FOC 带宽 > 1 kHz） | 有（可 FOC 补偿） | 低 | ⭐⭐⭐⭐ |
| [[电机#3. 无框力矩电机 (Frameless Torque Motor)\|无框力矩电机]] | **极高** | **极低** | 低 | 中（散热依赖结构） | ⭐⭐⭐⭐⭐ |
| [[电机#4. 空心杯电机 (Coreless Motor)\|空心杯电机]]（L25 / Ability / Inspire 的直线电缸即此类） | **极高** | **极低**（惯量最小） | **零** | 差（无铁芯散热差、热容小） | ⭐⭐⭐⭐（电机本身）|
| [[电机#5. 伺服电机系统 (Servo Motor System)\|智能舵机 / RC 舵机]]（LEAP 用 Dynamixel XC330） | 中（内置齿轮箱 + 位控固件黑箱） | 高（固件位控环 + 多级齿轮） | 有 | 中 | ⭐⭐（gap 主要来自固件，见 §4） |

> [!warning] 修正
> 原表最后一行写的是"RC 舵机"并给 ⭐。现代灵巧手用的是 **Dynamixel 类智能舵机**（LEAP Hand：16 DoF，XC330-M288 直驱，关节即舵机输出轴），它带位置/电流闭环固件与通信协议，不是 RC 舵机的 PWM 开环。它的 gap 主要来自固件位控环黑箱，归本篇 §4，而不是电机层。

### 2.2 电气时间常数 vs 指令周期

电机的电气时间常数 $\tau_e = L/R$（s）决定电流（即力矩）建立速度：
- 空心杯电机 $\tau_e \approx 0.1$ ms（电感极低）
- BLDC $\tau_e \approx 0.5$–$2$ ms
- 有刷电机 $\tau_e \approx 1$–$5$ ms

仿真步长通常 $dt=1/60\text{ s}\approx16.7$ ms 或 $1/120\text{ s}\approx8.3$ ms；L25 的位置指令周期 20–50 ms。三者相比，电气建立比指令周期快 **两个数量级**，"力矩瞬时施加"这一条假设在电气层**基本成立**。

> [!tip] 但要小心"瞬时"指的是什么
> 电气层瞬时 ≠ 关节响应瞬时。电流建立只用 0.1 ms，但从 SDK 发出 $q^*$ 到电流环拿到参考值，中间还有 §4 的 10–150 ms。**电气层可以忽略，正是因为延迟被别的层包了。**

### 2.3 齿槽效应 (Cogging Torque)

有铁芯 BLDC 低速时，转子永磁体与定子齿槽的磁力产生周期性力矩脉动，仿真完全不存在。影响：低速精密力控时输出力矩围绕 $K_tI$ 波动，手指微颤或位置精度下降。缓解：选空心杯（零齿槽）；FOC 加齿槽补偿表 (cogging map)；仿真中对力矩加周期扰动做 DR。L25 用空心杯，此项可忽略。

### 2.4 热降额 (Thermal Derating)

连续运行时绕组温度上升，铜电阻 $R = R_0(1 + \alpha \Delta T)$（$\alpha\approx0.0039$/K）增大，同一电流下所需电压增加，触及驱动器电压上限后被迫限流——等效为**力矩上限随时间下降**；同时永磁体磁链 $\psi_m(T)$ 下降使 $K_t$ 本身变小。仿真中 `effort_limit` 恒定。对需要**持续高力矩**的任务（长时间抓持）差异显著；空心杯热容小，升温更快。

> [!example] 深挖去哪篇
> 温度对 $R_s$、$\psi_m$、$L_{d,q}$ 的系统性影响与时间尺度：[[FOC_Control#四、 温度对电机模型参数的系统性影响|FOC §四]]；反电动势电压天花板、高速时力矩为什么"软"：[[FOC_Control#5.1 反电动势电压天花板与弱磁区域|FOC §5.1]]；Foundation 层：[[Actuation#6.1 两个漂移源与热失控环路|Actuation §6.1]]。

---

## 3. 第 ② 层：减速 / 传动

**为什么现在讲这个**：对 L25 这是 gap 的主体。原文档按"减速器类型"和"传动类型"两张表讲，这里保留两张表，但把它们统一到一个问题上：**减速比 $N$ 把哪些非理想性放大了多少倍。**

### 3.1 统一视角：摩擦按 $N^1$、惯量按 $N^2$ 折算

设电机轴摩擦 $\tau_{f,m}$（N·m）、转子惯量 $J_m$（kg·m²）、减速比 $N$（无量纲，丝杠+连杆手用 $N_{eq}$）。折算到关节侧：

$$
\tau_{f,joint}=N\,\tau_{f,m},\qquad J_{joint}=N^2 J_m
$$

来源：摩擦是力矩，按虚功 $\tau_{f,m}\,d\theta_m=\tau_{f,joint}\,d q$ 且 $d\theta_m=N\,dq$ 得 $N^1$；惯量是能量 $\tfrac12 J_m\dot\theta_m^2=\tfrac12 J_{joint}\dot q^2$ 且 $\dot\theta_m=N\dot q$ 得 $N^2$（完整虚功推导在 [[Transmission2JointDynamics_gap]] §二.1，数值代入在 [[LinkerSysId]]）。

L25 数值：四指 $N_{eq}\approx108$，拇指 `thumb_mcp`/`thumb_cmc_pitch` 多一级 17:1 折返减速箱后 $N_{eq}\approx1424/1800$。这意味着：
- 电机轴上一点点静摩擦，到关节侧乘 108（拇指乘 1400+）——**换向死区**由此而来。
- 转子惯量 $1.425\times10^{-7}$ kg·m² 乘 $108^2\approx1.17\times10^4$ → 关节侧 $\sim1.65\times10^{-3}$ kg·m²，与手指连杆自身惯量同量级甚至更大——这就是引擎里 `armature` 要填的值。

### 3.2 各减速器类型的 Gap 来源

| 减速器类型 | 背隙 | 摩擦非线性 | 扭转弹性 | 反驱动性 | Sim-to-Real 友好度 |
|-----------|------|----------|---------|---------|-----------------|
| [[减速器#2.1 行星齿轮箱 (Planetary Gearbox)\|行星齿轮箱]] | 中（8–15 arcmin） | 中 | 低 | 良好 | ⭐⭐⭐ |
| [[减速器#2.3 蜗轮蜗杆减速器 (Worm Gearbox)\|蜗轮蜗杆]] | 低 | **极高**（自锁） | 低 | **不可** | ⭐ |
| [[减速器#2.4 谐波减速器 (Harmonic Drive)\|谐波减速器]] | 零 | 中偏高 | **高（非线性）** | 中偏差 | ⭐⭐⭐ |
| [[减速器#2.5 摆线针轮减速器 (Cycloidal Gearbox)\|摆线针轮]] | 低 | 中 | 低 | 中 | ⭐⭐⭐ |
| [[减速器\|微型丝杠]] + 连杆（L25 / Ability / Inspire） | 低–中（丝母 + 连杆销轴累积） | **高**（$N_{eq}$ 放大后的 Stribeck；滚动体型式待核实：滚珠 / 滚柱，决定自锁与否） | 低 | 取决于升角与摩擦角：$\lambda<\rho$ 自锁 | ⭐⭐ |
| 无减速器（直驱） | 零 | **极低** | **零** | **最佳** | ⭐⭐⭐⭐⭐ |
| 低比减速（QDD） | 低 | 低 | 极低 | 良好 | ⭐⭐⭐⭐ |

### 3.3 背隙 (Backlash)

**现象**：力矩方向反转时（抓取→释放），齿轮间隙造成一小段"空行程"，期间输出端几乎无力矩响应。真机死区 $\Delta\theta \approx 0.02°$–$0.25°$（1–15 arcmin）；精细操作（转笔、翻转）频繁换向使其累积。

**DR 近似**：
```python
# 在仿真中近似背隙效应
backlash_angle = uniform(0, 0.004)  # rad, ~0.25°
if sign(tau_t) != sign(tau_t_prev):
    tau_effective = 0  # 死区
```

> [!warning] 谐波减速器的零背隙优势
> [[减速器#2.4 谐波减速器 (Harmonic Drive)|谐波减速器]]的弹性预载使其零背隙——这是其在 DLR/HIT 类手中被采用的核心原因之一。但注意零背隙 ≠ 零 lost motion：柔轮迟滞仍会造成加载-卸载曲线不重合（[[减速器]] §2.4）。

### 3.4 非线性摩擦与换向死区

**现象**：减速器/丝杠内部摩擦遵循 Stribeck 模型（[[减速器#1. 减速器核心参数|减速器 §1]]）：静止→运动时摩擦从静摩擦 $F_S$ 降到库仑 $F_C$，再随速度线性增加（粘滞项）。经 $N_{eq}$ 放大后，在 L25 上表现为真机实测的**三阶段换向阶梯**（[[Transmission2JointDynamics_gap]] §一）。

**仿真影响**：

> [!warning] 修正：Isaac Gym 的 `friction` 不是粘滞摩擦
> 原文档写"IsaacGym `joint_friction` 仅建模粘滞摩擦 $b\dot q$"。**错**。Isaac Gym（PhysX articulation）的 `dof_props['friction']` 是**干摩擦 / 库仑型**关节摩擦（单位 N·m，方向反于速度），`dof_props['damping']` 才是粘滞项 $b\dot q$。MuJoCo 的 `frictionloss` 同样是库仑型（以约束形式实现）。**两者都没有 Stribeck**——都没有 $F_S\neq F_C$ 的静→动过渡、温度依赖和预滑动微位移。要表达 $F_S>F_C$：MuJoCo 侧见 [[MuJoCo_Sim2Real_Params]] §8.1；Isaac Gym 侧在 PD 回路里显式加一段"粘着时 clip 到 $\pm F_S$、滑动时 $F_C\,\mathrm{sign}(v)$"（[[Transmission2JointDynamics_gap]] §5.4）。

**影响程度**（原文档给的量级）：高减速比方案（谐波/RV）摩擦损耗 10–35%；QDD 3–10%；直驱仅轴承摩擦 < 2%。丝杠手按 [[Transmission2JointDynamics_gap]] 实测归入"高"。

### 3.5 扭转弹性 (Torsional Compliance)

谐波柔轮传递力矩时弹性变形，关节实际角 $q_{actual}$ 与电机编码器折算角之间有偏差：

$$
q_{actual} = q_{encoder}/i - \tau_{load}/k(\tau_{load})
$$

$k$ 为非线性扭转刚度（N·m/rad）。仿真中 $q_{actual}=q_{encoder}/i$；真机高载荷下偏差 $0.1°$–$0.5°$，并引入二阶弹簧-质量振荡。缓解：MuJoCo 关节 `stiffness`/`damping` 建弹性关节，并对 $k$ 做 DR。丝杠手的弹性主要来自连杆销轴与丝母，通常小于谐波。

### 3.6 效率损耗与力矩缩放

$$
\tau_{real} = \eta \cdot \tau_{sim} \quad (\eta < 1)
$$

| 减速器 | 正向效率 $\eta_{fwd}$ | 反向效率 $\eta_{rev}$ | 力矩缩减 |
|-------|---------------------|---------------------|---------|
| 行星齿轮 | 95–97% | 90–95% | 3–10% |
| 谐波 | 65–90% | 40–70% | 10–60% |
| 蜗轮蜗杆 | 30–90% | **~0%** | **完全丧失** |
| 摆线针轮 | 85–95% | 75–90% | 5–25% |
| 微型丝杠（滑动） | 20–40%（$\lambda\approx4°$、$\mu\approx0.15$，待核实） | ~0%（自锁） | 大 |
| 微型丝杠（滚动体） | 85–95% | 70–90% | 5–30% |

> [!warning] 正向与反向效率不对称
> 反向效率（关节→电机）通常低于正向；谐波的 $\eta_{rev}$ 仅为 $\eta_{fwd}$ 的 60–80%，意味着**外力推关节时的力矩反馈远小于仿真预期**——对力感知与阻抗控制影响显著。丝杠手更极端：若 $\eta_{fwd}<50\%$ 则反向自锁（推导在 [[减速器]] §3），这就是"拇指掰不动"的原因（[[Transmission2JointDynamics_gap]] §2.4）。

### 3.7 传动方案：欠驱动、腱绳、直驱、QDD、直线电缸+连杆

**欠驱动耦合**（PIP-DIP 联动是典型）：仿真用 `mimic`/`transmission` 做**运动学理想耦合** $q_{DIP}=k\,q_{PIP}$；真机是**力学非理想耦合**：负载改变耦合比（弹性）、腱绳只拉不推可"松脱"、差分机构的力分配取决于各指节阻力。接触状态切换时耦合行为突变，仿真里学到的 PIP 策略在真机上 DIP 行为不一致。L25 有 5 个被动 DoF 属此类（[[Actuator2RigidDynamicsModel_gap]] §5.1）。

**腱绳传动**（Shadow Hand：24 关节、20 主动 DoF、前臂 40 根拮抗腱，电机版或气动肌肉版）引入最难建模的一组非线性：

| 效应 | 仿真建模难度 | 对 Gap 的贡献 |
|-----|-----------|-------------|
| Capstan 摩擦 | 极高（路径相关） | 力矩传递效率不确定 |
| 腱绳弹性 | 高（蠕变+迟滞） | 位置/力矩响应滞后 |
| 预紧力衰减 | 中（时变） | 长时间运行后性能退化 |
| 耦合矩阵非线性 | 极高 | 关节间力矩交叉耦合 |
| 腱绳松弛检测 | 高 | 松弛瞬间无力控能力 |

主流 RL 工作（Shadow Hand in-hand rotation）通常**不直接建模腱绳**：把 action 当关节位置/力矩，靠 DR 覆盖腱绳非线性，再配离线 System ID。对高动态非抓取操作（抛接、转笔）这条捷径更吃亏。腱网络的对偶性见 [[Actuation#7.3 腱网络的对偶性（承接 Dynamics §8）|Actuation §7.3]]。

**直驱**（[[传动#3. 直驱 (Direct Drive)|直驱]]）：$\tau_{joint}=K_tI-b\omega$，gap 仅剩轴承摩擦（< 2%）、齿槽、热降额——Sim-to-Real 最友好，但力矩密度太低，手指尺度几乎无人用纯直驱；"智能舵机直驱"（LEAP）是其现实变体，舵机内部仍有齿轮箱与位控固件。

**QDD**（[[传动#4. 准直驱 (Quasi-Direct Drive, QDD)|QDD]]，$i\le10$，MIT Mini Cheetah 6:1 单级行星）：背隙与级数成正比、摩擦损耗按 $(1-\eta)$ 缩放、reflected inertia $i^2J_m$ 远小于谐波。

**直线电缸 + 连杆**（L25 / Ability / Inspire / DexLink，本库主线）：空心杯电机 → 丝杠（旋转→直线）→ 连杆（直线→关节转动），$N_{eq}(\theta)=2\pi r(\theta)/l$ 随构型变（$r$ 力臂 m，$l$ 导程 m）。紧凑、力矩密度高、可自锁（省抓持功耗），代价是 §3.1 的 $N^1/N^2$ 放大、换向死区、反驱不对称、且几乎都配位控固件（引出 §4）。

> [!example] 深挖去哪篇
> 换向三阶段与死区拟合：[[Transmission2JointDynamics_gap]]；$N_{eq}$、armature 折算的 worked example：[[LinkerSysId]]；丝杠 Stribeck 与 $K_t$ 不稳定：[[Actuator2RigidDynamicsModel_gap#5.2 丝杠传动的 Stribeck 摩擦|Actuator gap §5.2]]；减速比双刃剑：[[Actuation#7.2 Reflected Inertia：为什么减速比是把双刃剑|Actuation §7.2]]、三大非理想性：[[Actuation#8.2 三大非理想性——机械侧 gap 的主体|Actuation §8.2]]；腱驱动动力学：[[Dynamics#8. 腱驱动与冗余动力学：真实灵巧手的传动|Dynamics §8]]。

---

## 4. 第 ④ 层：固件位控环 + 通信 / 延迟 / 量化

**为什么现在讲这个**：原文档完全没有这一层，而它恰恰是 L25 上仅次于机械死区的第二大 gap，且与 RL 训练配置（control decimation、action delay DR、观测历史长度）直接挂钩。这一节全部用 L25 的实测/文档参数：**8-bit 0–255 指令与反馈、位控指令 20–50 Hz、CAN 1 Mbps、MCU 规划平滑最长约 150 ms、SDK 发送间隔 0.3 ms/帧。**

### 4.1 仿真 PD vs 真机级联环

仿真把位置控制当一个完美弹簧：$\tau_{sim}=K_p(q^*-q)+K_d(\dot q^*-\dot q)$，每步零延迟生效。真机是三层级联：

$$
q^*\ \xrightarrow{\text{位置环 (十 Hz 级)}}\ \dot\theta_{ref}\ \xrightarrow{\text{速度环 (百 Hz 级)}}\ I_{q,ref}\ \xrightarrow{\text{电流环 (kHz 级)}}\ I_q\ \to\ \tau_m=K_tI_q
$$

内环必须比外环快 5–10 倍才能被外环"看成瞬时"（带宽分离，[[Actuation#4. 串级控制：电流环 → 速度环 → 位置环|Actuation §4]]）。对 RL 的含义：**固件的 $K_p, K_d$、速度/电流限幅、积分抗饱和都是黑箱**，仿真里的 PD 增益不等于真机的等效增益——这是"仿真 PD 与真机级联环错位"（[[FOC_Control#6.5 仿真 PD 与真机级联环的错位|FOC §6.5]]）。

### 4.2 8-bit 量化：指令栅格比背隙粗一个量级

SDK 的 0–100 归一化值在 CAN 层线性映射为单字节：$u_{raw}=\mathrm{round}(255\,u_{sdk}/100)$（[[Actuator2RigidDynamicsModel_gap#三、 L25 灵巧手 CAN 协议与可读取量分析|Actuator gap §三]]）。一个 LSB 对应的关节角：

$$
\Delta q_{LSB}=\frac{q_{max}-q_{min}}{255}
$$

以 $90°$ 量程为例：$\Delta q_{LSB}=90°/255\approx0.35°\approx6.2$ mrad。对比 §3.3 的机械背隙 $0.02°$–$0.25°$：**量化步长与最大背隙同量级或更粗**。三个直接后果：
1. **指令死区**：策略输出的 $q^*$ 变化小于 0.35° 时固件根本收不到变化——相当于在机械死区之外又叠了一层"数字死区"。
2. **反馈噪声地板**：反馈同样 8-bit，用差分求速度时 1 LSB 抖动在 50 Hz 下就是 $0.35°\times50=17.6°/\text{s}$ 的速度噪声——**真机上不要用差分速度做观测**（[[Actuator2RigidDynamicsModel_gap#七、 RL State Space 设计法则|Actuator gap §七]]）。
3. **辨识分辨率上限**：任何小于 1 LSB 的死区/背隙无法从"发了什么位置、读到什么位置"里辨识出来（[[Transmission2JointDynamics_gap]] §四的数据极简方案正是在这个约束下设计的）。

仿真里对应做法：对 action 和 obs 都套 $Q_{255}(\cdot)$，且量程要与真机映射一致——这比任何噪声 DR 都更"像"真机。

### 4.3 延迟预算表

把一条位置指令从策略到关节的每一段延迟列出来（L25 数值，单位 ms）：

| 段 | 机制 | 典型值 | 说明 |
|:--|:--|--:|:--|
| SDK 队列 | 后台线程 `SEND_INTERVAL_S = 0.3 ms` 逐帧发 | 1.5（5 帧角度）～4.5（角度+速度+力矩 15 帧） | 五指各一帧；帧越多末指越晚 |
| CAN 帧传输 | 1 Mbps，标准帧 8 字节 ≈ 108–135 bit（含填充） | 0.11–0.135 / 帧 | 小于 SDK 间隔，总线利用率 < 50%，不是瓶颈 |
| 位控采样保持 (ZOH) | 指令 20–50 Hz | 平均 $T_s/2$ = 10–25，最坏 20–50 | 指令周期本身就是延迟 |
| MCU 规划平滑 | 固件对新目标做轨迹平滑/限速 | **最长约 150** | 与指令跳变幅度相关，大跳变时占大头 |
| 级联环建立 | 位置环→速度环→电流环 | 数 ms 级 | 与 4.1 的固件增益有关 |
| 电气建立 | $\tau_e=L/R$ | 0.1 | §2.2，可忽略 |

结论：**延迟预算由固件平滑（≤150 ms）和指令周期（10–50 ms）主导，通信（数 ms）与电气（0.1 ms）可忽略。** 在 50 Hz 控制下 150 ms = 7.5 个控制步，20 Hz 下 = 3 步。原文档 DR 表建议"力矩延迟 0–3 steps"对 L25 偏小，应放宽到 **0–8 步（50 Hz）**，并且延迟与指令跳变幅度相关（不是常数），最好用[[Idea-002-Latency-Aware-Actuator]]那种把延迟当隐变量建模的方式。

### 4.4 异步：16 DoF 的"同步动作"是扫描式的

CAN 是串行总线，五指指令按帧先后到达，触觉每指 72 字节需 12 帧拼接、指间还有约 2.5 ms 间隔——**全手观测不是同一物理时刻的快照**（[[Actuator2RigidDynamicsModel_gap#三、 L25 灵巧手 CAN 协议与可读取量分析|Actuator gap §三]]）。仿真里所有关节同一步更新；真机是"扫描"。对高动态任务，这意味着观测里应保留时间戳或至少做统一的延迟对齐。采样/混叠的一般理论见 [[SignalProcessing#1.1 采样与混叠：离散化不是无损记录|SignalProcessing §1.1]]。

> [!example] 深挖去哪篇
> CAN 协议、可读量、三种读取模式、归一化指令不是物理量：[[Actuator2RigidDynamicsModel_gap#三、 L25 灵巧手 CAN 协议与可读取量分析|Actuator gap §三]]；哪些量能进 RL state：[[Actuator2RigidDynamicsModel_gap#七、 RL State Space 设计法则|Actuator gap §七]]；仿真 PD 与级联环的五类错位：[[FOC_Control#6.5 仿真 PD 与真机级联环的错位|FOC §6.5]]；嵌入式接口层：[[Actuation#11. 接口层：嵌入式实现——MCU / STM32 / CAN|Actuation §11]]。

---

## 5. 第 ③ 层：接触

**为什么现在讲这个**：关节力矩到了，物体动不动还取决于接触。这一层本库有独立 Foundation，这里只说它与前三层的**耦合关系**。

- **关节摩擦与接触摩擦会互相掩盖**：关节摩擦调大 → 手指更"僵" → 物体更不容易被蹭掉，看起来像接触摩擦够了。所以标定顺序必须是**先空载定关节摩擦（层 ②），再带载定接触摩擦（层 ③）**（[[MuJoCo_Sim2Real_Params]] §六）。
- **接触 DR 不能只随机 $\mu$**：还要随机接触刚度/阻尼（`solref`/`solimp`）、接触→触觉读数的延迟（层 ④ 的 12 帧拼接）、接触几何（碰撞网格扰动）——[[ContactMechanics#7. Sim-to-Real 与工程实现|ContactMechanics §7]]。
- **触觉 5×12×6 是异步观测**（§4.4），世界模型若把它当同步快照会学到假因果。

> [!example] 深挖去哪篇
> 接触模型层级与求解器：[[ContactMechanics#5. 接触动力学与求解器：如何算出下一时刻|ContactMechanics §5]]；MuJoCo `solref/solimp/impratio/cone` 与 L25NS 取值表：[[MuJoCo_Sim2Real_Params]]。

---

## 6. 综合选型：代表手排名、DR 参数、Action Space

### 6.1 Sim-to-Real 友好度排名（已修正）

> [!warning] 修正：原表有三处硬件事实错误
> - 原表把 **Allegro v4** 列为"直驱 + 无框力矩电机"。错。Allegro v4：16 DoF，**直流电机 + 齿轮减速**（有减速比），CAN 333 Hz 力矩指令；既不是直驱也不是腱绳。
> - 原表把 **LEAP Hand** 列为"腱绳 + BLDC + 行星减速"。错。LEAP（CMU, Shaw 2023）：16 DoF，**Dynamixel XC330 智能舵机直驱**（关节即舵机输出轴），无腱绳。
> - 原表把 **DLR Hand** 笼统写成"连杆 + BLDC + 谐波"。补全：DLR/HIT Hand II 每指 3 DoF 4 关节，**BLDC + 谐波 1:100 + 同步带 1:1.25**，指尖力 ~30 N。
> - 原表缺 L25 所属的"直线电缸 + 连杆"路线；Schunk SDH 一行为原文档给的例子，待核实。

| 排名 | 传动 + 电机 + 减速组合 | Gap 主要来源 | Gap 等级 | 典型灵巧手 |
|:-:|:--|:--|:--|:--|
| 1 | 直驱 + 无框力矩/空心杯 + 无减速 | 仅轴承摩擦、热 | **最小** | 研究原型（手指尺度几乎无量产直驱手） |
| 2 | QDD + BLDC(FOC) + 低比行星（≤10:1） | 少量背隙、$i^2J_m$ | 小 | MIT Mini Cheetah 式关节（6:1）、MIT-style hands |
| 3 | 智能舵机直驱（舵机内含齿轮箱 + 位控固件） | 固件位控环黑箱（层 ④）、舵机齿轮背隙 | 中 | LEAP Hand（Dynamixel XC330） |
| 4 | 连杆/同步带 + BLDC + 谐波 1:100 | 柔轮弹性、反驱效率、迟滞 | 中 | DLR/HIT Hand II |
| 5 | 齿轮 + 直流电机 + 齿轮减速，CAN 力矩指令 | 齿轮背隙、摩擦 | 中偏大 | Allegro v4（333 Hz）；Schunk SDH（待核实） |
| 6 | **直线电缸（空心杯 + 丝杠）+ 连杆，8-bit 位控固件** | $N_{eq}\approx108$–$1800$ 放大的换向死区（层 ②）+ 量化/延迟（层 ④） | 大 | **LinkerHand L25**、PSYONIC Ability Hand、Inspire |
| 7 | 腱绳 + 电机 / 气动 | Capstan 摩擦、弹性、耦合矩阵 | **最大** | Shadow Hand（20 主动 DoF，40 腱） |

排名的含义不是"谁更好"，而是**同样的 RL 训练配置搬到哪只手上需要更多 DR/辨识**。L25 排第 6 不是电机差，而是丝杠 + 位控固件把两层 gap 都占全了——但换来的是小体积、高力矩密度和自锁抓持。

### 6.2 Domain Randomization 参数建议

| 参数 | 直驱 | QDD | 齿轮传动 | 腱绳传动 | 直线电缸+连杆（L25，建议起点） |
|-----|------|-----|---------|---------|:--|
| **关节摩擦**（库仑 $F_C$） | ±20% | ±30% | ±50% | ±80% | ±50%，且 $F_S/F_C$ 另随机 1.0–1.5 |
| **关节阻尼** $d$ | ±15% | ±25% | ±40% | ±60% | ±40% |
| **力矩缩放**（效率） | ±5% | ±10% | ±20% | ±30% | ±20%，正反向分开 |
| **关节刚度** $k$ | N/A | ±10% | ±30% | ±50% | ±20%（连杆销轴） |
| **背隙角度** | N/A | ±0.002 rad | ±0.005 rad | N/A | ±0.005 rad + 8-bit 量化（确定性，不随机） |
| **指令延迟** (steps) | 0 | 0–1 | 0–2 | 0–3 | **0–8 @ 50 Hz**（§4.3，与跳变幅度相关） |
| **armature** | N/A | ±10% | ±20% | N/A | ±20%（围绕 [[LinkerSysId]] 折算值） |
| **耦合比偏差** | N/A | N/A | ±5% | ±15% | ±5%（5 个被动 DoF） |

> [!tip] DR 幅度不是越大越好
> 幅度大过真机分布只会让策略保守。L25 这一列是"起点"，正确做法是先按 §8 辨识出中心值，再围绕它做窄幅 DR（[[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|RL §9.2]]）。

### 6.3 Action Space：为什么 L25 类手用位置目标

- **直驱 / QDD**：可用 **torque control**（action = 关节力矩）——电流→力矩线性、无固件黑箱、反驱良好，力矩空间是"可见"的。
- **高减速比 / 丝杠 + 位控固件（L25、Ability、Inspire、LEAP 舵机）**：用 **position control**（action = 目标关节角 或 action delta，仿真 PD 转力矩），理由有三层：
  1. **接口只有位置**：固件暴露的 0–255 是位置/速度/力矩百分比，"力矩 = 100"不是 N·m（[[Actuator2RigidDynamicsModel_gap]] §3.2），力矩接口本身不可标定。
  2. **底层位控环吸收非线性**：换向死区、Stribeck、量化——位置伺服会自己"顶过去"，策略看到的是一个较平滑的 $q^*\to q$ 映射；输出力矩则把搜索空间暴露给全部执行器细节（[[FOC_Control#6.5 仿真 PD 与真机级联环的错位|FOC §6.5]]）。
  3. **自锁传动下力矩不可反驱**：外力推不动关节，力矩控制的"柔顺"在物理上根本实现不了；要柔顺只能靠位置层的阻抗策略（[[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|ControlTheory §3.2]]、[[Idea-001-Phase-Adaptive Impedance]]）。
- **腱绳传动**：position control + 力矩限幅，避免策略进入难建模的力矩非线性区。

---

## 7. 仿真引擎实践

### 7.1 Isaac Gym 中的关键配置（已修正语义）

```python
# 关节属性配置 — 考虑机械结构非理想性
asset_options = gymapi.AssetOptions()
asset_options.fix_base_link = True
# L25 类位控手: 用 DOF_MODE_POS 让仿真 PD 吸收非线性; 直驱/QDD 才用 DOF_MODE_EFFORT
asset_options.default_dof_drive_mode = gymapi.DOF_MODE_POS

dof_props = gym.get_asset_dof_properties(asset)
for i in range(num_dofs):
    dof_props['friction'][i] = 0.05     # 库仑/干摩擦 F_C (N·m), 不是粘滞!
    dof_props['damping'][i] = 0.01      # 粘滞阻尼 b (N·m·s/rad), 位控模式下同时是 PD 的 K_d
    dof_props['armature'][i] = 1.65e-3  # N_eq^2 J_m 折算 (四指), 见 LinkerSysId
    dof_props['effort'][i] = max_torque # 力矩上限 (不含热降额)
```

`friction` 只有一个库仑值，表达不了 $F_S>F_C$；需要静摩擦时在 PD 回路里显式实现（[[Transmission2JointDynamics_gap]] §5.4）。

### 7.2 MuJoCo / mjlab

`frictionloss`（库仑关节摩擦，约束式）、`armature`、`damping`、`solref/solimp`（约束时间尺度与阻抗）、`impratio`、`cone` 的语义、默认值陷阱（默认 `solimp` 会让 `frictionloss` 退化成弱阻尼）和 L25NS 取值表全部在 [[MuJoCo_Sim2Real_Params]]，本篇不重复。

### 7.3 欠驱动关节的 URDF 建模

```xml
<!-- PIP-DIP 耦合关节示例 -->
<joint name="finger_pip" type="revolute">
    <limit lower="0" upper="1.57" effort="2.0" velocity="5.0"/>
</joint>

<joint name="finger_dip" type="revolute">
    <limit lower="0" upper="1.57" effort="2.0" velocity="5.0"/>
    <mimic joint="finger_pip" multiplier="0.67" offset="0"/>
</joint>
```

> [!warning] `mimic` 关节的局限性
> `mimic` 是**纯运动学耦合**（$q_{dip}=0.67\,q_{pip}$），不建模力学耦合。真机上 DIP 接触物体时 PIP 受力会变，仿真不体现。接触丰富任务建议改为独立关节 + 弹簧约束近似力学耦合。

---

## 8. 从 DR 到辨识：三条闭合 gap 的路线

**为什么现在讲这个**：§6.2 的 DR 只是"增覆盖"；真机数据在手里时，应该先"减偏差"。三条路线按数据需求与可解释性排列。

| 路线 | 做什么 | 需要什么数据 | 适合闭合哪层 | L25 现状 |
|:--|:--|:--|:--|:--|
| **A. 白箱参数辨识** | 用物理公式算/拟 $N_{eq}$、armature、$F_C$、$F_S$、$T_f$ | CAD 参数 + 空载"发位置/读位置"轨迹 | ② 传动 | 已做：[[LinkerSysId]]（折算）、[[Transmission2JointDynamics_gap]] §四（死区拟合，三种测法互证到 8%） |
| **B. Actuator Net**（Hwangbo 2019） | 用 MLP 学 $\tau_{joint}=f(\text{位置误差历史},\ \text{速度历史})$，**替换仿真 PD**，把固件级联环 + 传动 + 延迟一起当黑箱学 | 真机 $(q^*, q, \dot q)$ 序列 + 关节力矩真值（或电流 × $K_t$ 近似） | ④ + ② 一起 | 未做；难点是 L25 没有可信力矩真值（8-bit 力矩百分比不是 N·m），需先用路线 A 定 $K_t N_{eq}\eta$ 标尺 |
| **C. 残差 / 神经动力学** | 保留解析模型，学 $\Delta\tau$ 或 $\Delta q_{t+1}$ 残差；或用历史序列推断隐变量 $z_t$ 在线适配 | 真机轨迹（可含接触） | ②③④ 剩余部分 | 对应 [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model\|DexNDM]]、[[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)\|HORA]]；WMTS 的 Actuator + Rigid 解耦 WM 就是把 B/C 放进世界模型 |

Actuator Net 的关键设计——为什么输入是**位置误差与速度的历史窗**而不是当前值：延迟和 Stribeck 都是"有记忆"的，当前 $(q^*-q)$ 不足以决定力矩；历史窗把 §4.3 的延迟和 §3.4 的换向阶段一起编码进去。推导与 Hwangbo 2019 的原始设置见 [[Actuation#10.1 Actuator Net：学"仿真 PD 没覆盖的那段残差"|Actuation §10.1]]；力矩反馈为何"能当输入、不能当目标"见 [[Actuation#10.2 力矩反馈为何"能当输入、不能当目标"|Actuation §10.2]]。

推荐顺序：**A → B（或 C）→ 窄幅 DR**。先用白箱把中心值定准（不然 B/C 会把固件策略、热状态、传动损耗混成不可解释黑箱），再让网络学剩余残差，最后围绕辨识值做小幅 DR 兜底。

---

## 9. 相关研究与知识图谱关联

### 9.1 Sim-to-Real 方法论

本篇的硬件级分析是 Sim-to-Real Gap 的**底层物理来源**，与以下 RL 层面方法互补：

- [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|RL §9 Sim-to-Real]] — Domain Randomization、System ID、Online Adaptation 理论框架
- [[A Survey of Sim-to-Real Methods in RL]] — MDP 四要素分类法：本篇侧重 Action 和 Transition 层面的 gap
- [[Reinforcement Learning in Robotic Systems - A Review on Sim-to-Real Transfer]] — 执行器级建模视角，与本篇 §2–§4 直接对应
- [[Grounded Action Transformation]] — 学习 $a_{real}=h(s,a_{sim})$ 修正执行器非理想性，可视为路线 B 的策略侧版本
- [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction]] — 在线修正策略，补偿本篇分析的硬件非线性

### 9.2 神经动力学补偿

针对 §1.2 链路中难以精确辨识的参数（$\eta$、$\tau_{friction}$、$k$、$\delta$），用数据驱动直接学残差：

- [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]] — 关节级神经动力学模型，学 $\Delta\tau=f_{NN}(q,\dot q,\tau_{cmd})$
- [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]] — 环境编码器从历史序列推断隐式物理参数 $z_t$，在线自适应
- [[Minimalist Compliance Control]] — 方向相关效率模型，以最小辨识代价实现谐波减速器力控（对应 §3.6 的 $\eta_{fwd}\ne\eta_{rev}$）

### 9.3 对 DNPM / WMTS 项目的直接影响

> [!tip] 与项目实验设计的关联
> - [[Idea-001-Phase-Adaptive Impedance]] — 时变阻抗参数的 DR 范围参考 §6.2；自锁传动下阻抗只能在位置层实现（§6.3）
> - [[Idea-005-Test-Time Contact Adaptation]] — 在线辨识的参数集应覆盖 §1.2 中的 $\eta$、$\tau_{friction}$、$k$，以及 §4 的 $\delta$
> - [[Idea-007-Dual Orthogonal Curriculum]] — 物理轴课程的 α-scaling 可按四层 gap 的严重程度选参数化方向
> - [[Idea-002-Latency-Aware-Actuator]] — §4.3 的延迟预算是它的输入：延迟不是常数，是"手指级/关节级 + 跳变幅度相关"的隐变量
> - [[WorldModels#5.2 WMTS 的核心结构决策：Actuator + Rigid 解耦|WorldModels §5.2]] — Actuator 子模型的边界正好是本篇的层 ①②④，Rigid 子模型是层 ③ + 刚体

---

## 回扣与承接

用 L25 的一根食指把四层走一遍——**空心杯电机 → 丝杠电缸 → 连杆 → PIP 关节**（拇指再多一级 17:1 折返减速箱）：

1. 策略在 50 Hz 输出 $q^*$，SDK 把它量化成 0–255 的一个字节（**层 ④**：0.35°/LSB 的栅格），排进 0.3 ms/帧的发送队列，经 CAN 1 Mbps 到指节 MCU；MCU 对新目标做平滑，最长 150 ms 才把参考值喂给位置环。到此为止，关节还没动，延迟已经 10–150 ms。
2. 级联环把位置误差变成 $I_q$，空心杯在 0.1 ms 内建立电流，$\tau_m=K_tI_q$（**层 ①**：只有跑久了 $K_t(T)$ 才会掉）。
3. $\tau_m$ 经丝杠（导程 0.7 mm）变成推力，经连杆（力臂 ≈12 mm）变成关节力矩，$N_{eq}\approx108$（**层 ②**）：电机轴的静摩擦被乘 108 后成为换向死区，转子惯量 $1.425\times10^{-7}$ 乘 $108^2$ 成为 $1.65\times10^{-3}$ kg·m² 的 armature。拇指 $N_{eq}\approx1424/1800$，且 $\eta_{fwd}<50\%$ 时自锁——掰不动。
4. 关节力矩通过指面接触到物体（**层 ③**）：先空载定好层 ② 的 $F_C/F_S$，再带载定 $\mu$，否则两者互相掩盖。

**下一篇去哪**：想弄清层 ① 与固件级联环 → [[FOC_Control]]；想弄清指令→电机轴（CAN、量化、延迟、热）→ [[Actuator2RigidDynamicsModel_gap]]；想弄清电机轴→关节（$N^1/N^2$、死区拟合）→ [[Transmission2JointDynamics_gap]] 与 [[LinkerSysId]]；想把这些填进引擎 → [[MuJoCo_Sim2Real_Params]]。

---

## 对开发与科研的启示

1. **先关掉电气层，把精力放到层 ②④**：对 L25，电气延迟 0.1 ms 对 20–50 ms 的指令周期完全不可见；训练配置里最该改的是 **action delay DR 放宽到 0–8 步、action/obs 加 8-bit 量化、观测里去掉差分速度**。这意味着下一步可以直接改 mjlab 环境的 obs/action wrapper，不用动模型。
2. **延迟不是常数而是隐变量**：MCU 平滑与指令跳变幅度相关，CAN 使五指扫描式到达——这正是 [[Idea-002-Latency-Aware-Actuator]] 的实验动机；下一步可以用 §4.3 的预算表设计一组"跳变幅度 × 延迟"的真机标定轨迹。
3. **Actuator Net 在 L25 上的前置条件是力矩标尺**：8-bit 力矩百分比不是 N·m，直接训 Hwangbo 式 Actuator Net 没有真值。可行路径是用 [[LinkerSysId]] 的 $K_tN_{eq}\eta$ 把电流百分比换算成关节力矩近似真值，或者改学 $q_{t+1}$ 残差（路线 C）——这是 WMTS Actuator 子模型的直接选题。
4. **硬件选型决定 RL 技术路线上限**：如果未来换手，用 §6.1 排名判断"位置 vs 力矩 action"与 DR 幅度；如果继续用 L25，接受"位置目标 + 位置层阻抗"是唯一可行的柔顺路线，把科研问题定义在**位置层阻抗如何在自锁传动上实现相位自适应**（[[Idea-001-Phase-Adaptive Impedance]]）。
