---
tags:
  - mechanical-design
  - dexterous-hand
  - system-identification
  - sim2real
aliases:
  - 灵巧手系统辨识
  - LinkerHand SysId
  - 等效直线质量
  - Equivalent Linear Mass
  - 丝杠 armature 折算
related:
  - "[[Actuation]]"
  - "[[减速器]]"
  - "[[电机]]"
  - "[[传动]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[sim2real]]"
  - "[[Actuator2RigidDynamicsModel_gap]]"
  - "[[Transmission2JointDynamics_gap]]"
  - "[[MuJoCo_Sim2Real_Params]]"
---

# LinkerHand 电缸系统辨识：转子惯量 → 等效直线质量 → 关节 `armature`（worked example）

> [!abstract] 本篇在链路中的位置
> 整条链路是 **电能 → 电机电磁力矩 → FOC 电流环 → 减速器/丝杠/连杆传动 → 关节力矩 → 刚体+接触**。本篇只管其中"**电机轴 → 关节**"这一段里最容易被仿真漏掉的一个量：**转子惯量经过丝杠和连杆折算到关节侧之后有多大**，也就是 Isaac Gym / MuJoCo 关节的 `armature`。上一篇是 [[减速器]]（丝杠是什么、自锁判据从哪来）；下一篇是 [[Transmission2JointDynamics_gap]]（同一段传动里的**摩擦**如何折算、真机换向死区怎么测），引擎落地看 [[MuJoCo_Sim2Real_Params]]。理论根在 [[Actuation#7.2 Reflected Inertia：为什么减速比是把双刃剑|Actuation §7.2 Reflected Inertia]]。

> [!tip] 读完你应该能回答
> 1. 为什么一个 $1.4\times10^{-7}\ \text{kg·m}^2$ 的转子，折到关节上会变成和连杆本体同量级的惯量？"平方"从哪来？
> 2. 四指电缸 $N_{eq}\approx108$，拇指 $N_{eq}\approx1424$，为什么拇指的 `armature` 反而**更小**？
> 3. 同一根丝杠，为什么惯量按 $N^2$ 折算、摩擦却只按 $N^1$ 折算？这两条分别是从哪个守恒律推出来的？
> 4. 四指上电后能被掰动、拇指掰不动——自锁到底来自丝杠还是来自减速箱？结论依赖哪个待核实的事实？
> 5. 算出来的数字该填进 Isaac Gym / MuJoCo 的哪个字段？填错（填 0）会在真机上表现成什么？

---

## §1 问题：为什么仿真里的 armature 不能填 0

**为什么现在讲这个**：Isaac Gym 与 MuJoCo 里关节 `armature` 的默认值都是 0。对直驱关节这没问题；对 L25 这种"空心杯电机 + 丝杠电缸 + 连杆"的高减速比关节，填 0 意味着**整项漏掉转子折算惯量**，而这项与连杆本体惯量同量级。

先把 L25 一根手指的硬件数据摆出来（用户实测 / CAD 值，原样保留）：

| 量 | 符号 | 四指电缸 | 单位 | 含义 |
|---|---|---:|---|---|
| 转子惯量 | $J_{rotor}$ | $1.425\times10^{-7}$（即 $0.1425\ \text{kg·mm}^2$） | kg·m² | 电机转子绕自身轴的转动惯量 |
| 丝杠导程 | $l$ | $0.7\times10^{-3}$ | m | 丝杠转一整圈（$2\pi$ rad），螺母/推杆前进的距离 |
| 关节力臂 | $R$ | $\approx 12\times10^{-3}$ | m | 推杆作用点到关节转轴的垂直距离，随构型轻微变化，$R=r(\theta)$ |

直觉先行：转子看起来"极轻"（$0.1425\ \text{kg·mm}^2$），但导程只有 0.7 mm——电机**转满一整圈**推杆才前进 0.7 mm。也就是说，推杆每动 1 mm，转子要转 $1/0.7\approx1.43$ 圈 $\approx9$ rad。推杆慢慢动，转子却在飞转；**动能里的角速度是平方进去的**，所以转子的动能远比"它很轻"这个印象大。这就是 `armature` 不能为 0 的物理来源。

> [!important] 为什么必须填进仿真
> Isaac Gym / MuJoCo 关节默认 `armature = 0`，会整项漏掉转子折算惯量。对 L25 四指这类高 $N_{eq}$（≈108）传动，漏掉的 $N_{eq}^2 J_{rotor}\approx1.65\times10^{-3}\ \text{kg·m}^2$ 与连杆本体惯量同量级，Sim 关节因此"过轻过灵"：在 Sim 里整好的阻抗/力控增益一迁到真机，真机关节比 Sim 重得多、响应慢得多，PD 增益相对过高 → **振荡**。这正是 [[Actuator2RigidDynamicsModel_gap|执行器↔刚体动力学 gap]] 的一个可量化来源，也是 [[Actuation#8.2 三大非理想性——机械侧 gap 的主体|Actuation §8.2 机械侧 gap]] 里"惯量项"那一栏的具体数字。

本篇的目标就是把上表三个数变成一个 `armature`，分三步：**旋转 → 直线（§2）→ 关节（§3）**，然后用拇指做第二例（§4），再把"摩擦怎么折"讲清（§5），最后对账反驱（§6）、填进引擎（§7）。

---

## §2 旋转→直线折算：转子惯量变成等效直线质量

**为什么现在讲这个**：丝杠把旋转变成直线，所以第一步要问"这个转子，如果把它当成挂在推杆上的一块直线运动的质量，等于多少公斤"。这个量叫**等效直线质量 (Equivalent Linear Mass)** $M_{eq}$。

### 2.1 运动学：推杆速度 ↔ 电机角速度

设推杆以直线速度 $v$（m/s）运动。丝杠导程 $l$ 的定义是"转一圈前进 $l$"，所以

$$\text{转一圈（}2\pi\text{ rad）} \;\leftrightarrow\; \text{前进 } l \quad\Longrightarrow\quad \frac{\theta_m}{x}=\frac{2\pi}{l}$$

其中 $\theta_m$（rad）是电机转角，$x$（m）是推杆位移。两边对时间求导，得到角速度与直线速度的关系：

$$\omega_m=\frac{2\pi}{l}\,v \qquad [\text{rad/s}]$$

$2\pi/l$ 的单位是 rad/m，可以叫"**导程增益**"。对 L25 四指：$2\pi/0.0007\approx 8976\ \text{rad/m}$，即推杆每前进 1 m 转子要转 8976 rad。

### 2.2 能量等效：为什么用动能、不用力

我们要找一个 $M_{eq}$，使得"一块质量 $M_{eq}$ 以速度 $v$ 直线运动"与"转子以对应角速度 $\omega_m$ 旋转"**储存同样多的动能**——因为惯性效应本质上就是动能的储存与释放，两者动能相同则对外表现的惯性相同。写出等式：

$$\frac12 M_{eq} v^2 = \frac12 J_{rotor}\,\omega_m^2$$

把 §2.1 的 $\omega_m=(2\pi/l)\,v$ 代入右边：

$$\frac12 M_{eq} v^2 = \frac12 J_{rotor}\left(\frac{2\pi}{l}\right)^2 v^2$$

两边同除以 $\frac12 v^2$（$v\neq0$），得到

$$\boxed{M_{eq}=J_{rotor}\left(\frac{2\pi}{l}\right)^2}\qquad[\text{kg}]$$

量纲检查：$\text{kg·m}^2\times(\text{rad/m})^2=\text{kg}$（rad 无量纲）。✓

### 2.3 代入数字

$$M_{eq}=1.425\times10^{-7}\times\left(\frac{2\pi}{0.0007}\right)^2
=1.425\times10^{-7}\times 8.06\times10^{7}\approx\mathbf{11.48\ \text{kg}}$$

一块 0.1425 kg·mm² 的转子，从推杆看过去像一块 **11.5 kg** 的铁。这个"放大 $8\times10^7$ 倍"完全来自 $(2\pi/l)^2$——导程越小，放大越狠，而且是平方。

> [!tip] 对比：如果导程是 7 mm 而不是 0.7 mm
> $M_{eq}$ 会缩到 $1/100$，只有 0.115 kg。**导程缩 10 倍，等效质量涨 100 倍**——这就是为什么微型丝杠电缸虽然紧凑、力大，但从惯量角度是"重"的。

---

## §3 直线→关节折算：等效直线质量变成关节 armature

**为什么现在讲这个**：仿真里的关节是**旋转关节**，需要的量是 kg·m²，不是 kg。推杆通过连杆推动手指绕关节转，所以还要再折一次：直线 → 旋转。

### 3.1 运动学：推杆位移 ↔ 关节转角

设手指关节转过微小角度 $\Delta\theta_j$（rad），推杆作用点到关节转轴的垂直距离（力臂）为 $R$（m）。由弧长关系，推杆需要移动

$$\Delta x \approx R\,\Delta\theta_j \quad\Longrightarrow\quad v = R\,\dot\theta_j$$

（这是小角度下的一阶近似；严格地说 $R=r(\theta)$ 随构型变化，见 §3.4。）

### 3.2 能量等效：再做一次同样的事

同 §2.2 的思路：找一个绕关节轴的等效转动惯量 $J_{armature}$，让它以 $\dot\theta_j$ 旋转时动能等于 $M_{eq}$ 以 $v$ 直线运动的动能：

$$\frac12 J_{armature}\dot\theta_j^2=\frac12 M_{eq} v^2=\frac12 M_{eq}R^2\dot\theta_j^2$$

两边同除以 $\frac12\dot\theta_j^2$：

$$\boxed{J_{armature}=M_{eq}R^2}\qquad[\text{kg·m}^2]$$

### 3.3 代入数字（修正后）

> [!warning] 修正：原文档此处力臂用错了数
> 原文正文写 $R\approx12$ mm，但代入公式时用的是 $0.015$（15 mm），算出 $0.00258\ \text{kg·m}^2$。**统一用 $R=12$ mm**：

$$J_{armature}=11.48\times(0.012)^2=11.48\times1.44\times10^{-4}\approx\mathbf{1.65\times10^{-3}\ \text{kg·m}^2}$$

这个值与 [[Transmission2JointDynamics_gap]] §2.2 表中四指 `pip` 的 `armature = 0.001653` 一致（那张表就是这样算出来的）。

### 3.4 顺手得到等效减速比 $N_{eq}$

把两步运动学串起来：关节转 $\Delta\theta_j$ → 推杆走 $\Delta x=R\Delta\theta_j$ → 电机转 $\Delta\theta_m=\dfrac{2\pi}{l}\Delta x=\dfrac{2\pi R}{l}\Delta\theta_j$。于是

$$\boxed{N_{eq}\equiv\frac{\Delta\theta_m}{\Delta\theta_j}=\frac{2\pi R}{l}}$$

代入：$N_{eq}=\dfrac{2\pi\times12}{0.7}\approx\mathbf{107.7}$（单位约掉，mm/mm）。电机转 107.7 rad，关节才转 1 rad——这就是"电缸手指等效于一个 108:1 减速器"。

**$R=r(\theta)$ 随构型变**：连杆机构的力臂在手指弯曲过程中并非常数，所以 $N_{eq}(\theta)=2\pi r(\theta)/l$ 和 $J_{armature}(\theta)$ 都随关节角变化。本篇用 12 mm 这个代表值；引擎里 `armature` 是常数，所以这是一个**结构性的近似**，其构型依赖适合在 sim2real 里做域随机化（见 [[Transmission2JointDynamics_gap]] §八第 3 条）。

> [!important] 一句话说透：这就是 $J_{reflected}=i^2J_{motor}$ 的丝杠版本
> 把三步串起来消掉中间量 $M_{eq},R$：
> $$J_{armature}=M_{eq}R^2=J_{rotor}\Big(\tfrac{2\pi}{l}\Big)^2R^2=J_{rotor}\Big(\tfrac{2\pi R}{l}\Big)^2=N_{eq}^2\,J_{rotor}.$$
> 于是**关节侧 `armature` = 等效减速比的平方 × 转子惯量**，与通用律 $J_{reflected}=i^2J_{motor}$ **完全同构**（$i\to N_{eq}=2\pi R/l$）——那个"平方"仍旧来自动能里的速度平方（见 [[Actuation#7.2 Reflected Inertia：为什么减速比是把双刃剑|Actuation §7.2 能量等效推导]]）。旋转-旋转传动的减速比 $i$，在旋转-直线电缸里换成了导程增益与力臂的乘积 $2\pi R/l$，物理内核不变。
> 验算：$N_{eq}^2 J_{rotor}=107.7^2\times1.425\times10^{-7}=11599\times1.425\times10^{-7}\approx1.65\times10^{-3}$ ✓，与 §3.3 完全一致。

---

## §4 拇指第二例：多一级 17:1 折返减速箱

**为什么现在讲这个**：拇指 `thumb_mcp` / `thumb_cmc_pitch` 的电缸和四指不是同一型号——电机更小，而且丝杠前面**多了一级 17:1 折返齿轮减速箱**。用同一套公式再算一遍，会得到一个反直觉的结果，正好检验你有没有真的懂 §3。

### 4.1 硬件数据

| 量 | 四指电缸 | 拇指折返电缸 | 单位 |
|---|---:|---:|---|
| 转子惯量 $J_{rotor}$ | $1.425\times10^{-7}$ | $1.4\times10^{-10}$ | kg·m² |
| 丝杠导程 $l$ | 0.7 | 0.6 | mm |
| 前置减速比 $N_{gear}$ | 1 | **17** | — |
| 等效减速比 $N_{eq}$（[[Transmission2JointDynamics_gap]] §2.2 表） | 107.7 | **1424.2** | — |

### 4.2 $N_{eq}$ 多一个因子

有了齿轮箱，电机转 $N_{gear}$ 圈丝杠才转 1 圈。把它接在 §3.4 的链条最前端：

$$\theta_m = N_{gear}\,\theta_{screw},\qquad \theta_{screw}=\frac{2\pi}{l}x,\qquad x=r(\theta)\,\theta_j$$

$$\Longrightarrow\quad\boxed{N_{eq}=\frac{2\pi\,r(\theta)\,N_{gear}}{l}}$$

用 [[Transmission2JointDynamics_gap]] 给的 $N_{eq}=1424.2$ 反推拇指力臂：$r=\dfrac{N_{eq}\,l}{2\pi N_{gear}}=\dfrac{1424.2\times0.6}{2\pi\times17}\approx8.0$ mm（拇指 `thumb_mcp` 的力臂比四指的 12 mm 短；`thumb_cmc_pitch` 的 $N_{eq}\approx1800$ 对应 $r\approx10$ mm。**力臂值由 $N_{eq}$ 反推，待与 CAD 核实**）。

### 4.3 代入数字

$$J_{armature}^{thumb}=N_{eq}^2J_{rotor}=1424.2^2\times1.4\times10^{-10}
=2.03\times10^{6}\times1.4\times10^{-10}\approx\mathbf{2.84\times10^{-4}\ \text{kg·m}^2}$$

与 [[Transmission2JointDynamics_gap]] §2.2 表中 `thumb_mcp` 的 `armature = 0.000284` 一致。

### 4.4 反直觉：$N_{eq}$ 大 13 倍，armature 反而小 5.8 倍

$$\frac{J^{thumb}_{armature}}{J^{pip}_{armature}}
=\underbrace{\left(\frac{1424.2}{107.7}\right)^2}_{13.22^2\approx174.8}\times
\underbrace{\frac{1.4\times10^{-10}}{1.425\times10^{-7}}}_{1/1018}
\approx\frac{174.8}{1018}\approx\frac{1}{5.8}$$

**减速比的平方把惯量放大了 175 倍，但拇指的转子本身轻了 1018 倍**——后者赢了。所以拇指关节的 `armature`（$2.84\times10^{-4}$）反而比四指（$1.65\times10^{-3}$）小。这条曾被误判成"拇指多一级减速 → 惯量被低估 14~35 倍"，据以把 armature 抬高了 37 倍，后来实测推翻（[[Transmission2JointDynamics_gap]] §六 第 1、2 条）。

> [!tip] 教训
> $J_{armature}=N_{eq}^2J_{rotor}$ 有**两个**因子，看到"减速比大"就断言"折算惯量大"，是只看了一个。凡是不同型号电机之间比较，必须两个因子一起算。

---

## §5 摩擦按 N 的一次方折算、惯量按 N 的平方折算

**为什么现在讲这个**：§3、§4 算的是惯量，用的是**动能**。但同一根丝杠上的**摩擦**折到关节侧，放大倍数不是 $N^2$ 而是 $N^1$。两个幂次不同，是因为它们来自两个不同的守恒律——不把这一点推透，就会像 §4.4 那样把拇指的大摩擦误认成大惯量。

### 5.1 力矩/摩擦：虚功（功率平衡）→ 一次方

考虑理想传动（暂不计损耗，$\eta=1$）。电机侧力矩 $\tau_m$ 以角速度 $\omega_m$ 输出功率，关节侧以 $\tau_j$、$\omega_j$ 接收；无损耗时功率相等：

$$\tau_m\,\omega_m=\tau_j\,\omega_j$$

运动学给 $\omega_m=N\omega_j$（§3.4），代入：

$$\tau_m\,N\omega_j=\tau_j\,\omega_j\quad\Longrightarrow\quad\boxed{\tau_j=N\,\tau_m}$$

这就是"杠杆比"：**力矩按 $N$ 的一次方放大**。等价的虚功表述：任一虚位移 $\delta\theta_j$ 下，$\tau_j\,\delta\theta_j=\tau_m\,\delta\theta_m=\tau_m\,N\,\delta\theta_j$。

摩擦是一种力矩，所以同样按一次方折算。设电机轴上有库仑摩擦力矩 $\tau^m_C$（与速度方向相反、大小恒定）。关节转 $\delta\theta_j$ 时电机轴转 $N\delta\theta_j$，摩擦耗散的功为 $\tau^m_C\cdot N|\delta\theta_j|$；要在关节侧用一个等效摩擦力矩 $F_C$ 表示同样的耗散，须有 $F_C|\delta\theta_j|=\tau^m_C N|\delta\theta_j|$，于是

$$\boxed{F_C=N\,\tau^m_C}$$

计入传动效率 $\eta$ 时，正向传递的有用力矩变成 $\eta N\tau_m$，摩擦这一项在 [[Transmission2JointDynamics_gap]] 里写成 $\tau^m=\tau^j/(k\,N_{eq})$，其中 $k$ 是一个约为 1 的连杆几何因子（待核实）。

### 5.2 惯量：动能 → 平方

已在 §2.2、§3.2 推过：$\frac12J_{rotor}\omega_m^2=\frac12J_{rotor}N^2\omega_j^2$，所以 $J_{armature}=N^2J_{rotor}$。也可以从力矩角度看出"两个 $N$"从哪来：

$$\tau_j=\underbrace{N}_{\text{杠杆：力矩放大}}\times\underbrace{J_{rotor}\ddot\theta_m}_{\text{电机侧惯性力矩}}
=N\,J_{rotor}\,\underbrace{N\ddot\theta_j}_{\text{运动学：}\ddot\theta_m=N\ddot\theta_j}
=N^2J_{rotor}\ddot\theta_j$$

**一个 $N$ 来自力矩放大（和摩擦一样），另一个 $N$ 来自加速度也被放大了**。摩擦力矩的大小与速度/加速度无关（库仑型），所以没有第二个 $N$。

### 5.3 用 L25 的数字对账

| | 四指 pip | 拇指 mcp | 比值 |
|---|---:|---:|---:|
| $N_{eq}$ | 107.7 | 1424.2 | 13.22 |
| 关节侧库仑摩擦 $F_C$（实测，[[Transmission2JointDynamics_gap]] §2.2） | 0.0191 N·m | 0.2412 N·m | **12.66** ≈ $N^1$ 比 |
| 关节侧 armature $J_{armature}$ | $1.65\times10^{-3}$ | $2.84\times10^{-4}$ | 1/5.8 ≈ $N^2$ 比 × 转子比 |

摩擦比值 12.66 与 $N_{eq}$ 比值 13.22 吻合到 4%——**摩擦确实按一次方折算，实测证实**；把两个关节的 $F_C$ 各除以自己的 $N_{eq}$，电机侧摩擦都落在同一个 $\sim10^{2}\ \mu$N·m 量级。所以拇指"卡"不是因为它的摩擦机制特殊，而是同一份电机侧摩擦乘了一个大 13 倍的杠杆。

> [!important] 这决定了拇指两个关节的性质
> 惯量小（$N^2\times$轻转子），摩擦大（$N^1\times$同样的摩擦）——拇指是一个**低惯量、高静摩擦**的关节，换向时会出现约 24 mrad（≈5 个 8-bit LSB）的死区。这不是标定问题，是 $N_{eq}\approx1400$ 的结构性后果；摩擦建模与实验全部在 [[Transmission2JointDynamics_gap]]。摩擦模型本身（Coulomb / 静摩擦 / Stribeck / LuGre）的接触力学根源见 [[ContactMechanics#4. 接触模型的层级：从点接触到软体|ContactMechanics §4]]。

---

## §6 反驱对账：高减速比为什么不一定自锁

**为什么现在讲这个**：$N_{eq}\approx108$ 甚至 $1424$，按"减速比高就难反驱"的直觉，手指应当掰不动。真机上四指上电后可被反驱，拇指掰不动。要用两条独立的判据把这个差别解释清楚。

### 6.1 丝杠自身的自锁判据

丝杠是一个缠在圆柱上的斜面。螺旋升角 $\lambda$ 由导程与中径 $d_m$ 决定：

$$\tan\lambda=\frac{l}{\pi d_m}$$

摩擦角 $\rho_f=\arctan\mu$。斜面上的物体在重力（这里是轴向负载）作用下会不会自己滑下来，取决于 $\lambda$ 与 $\rho_f$ 的大小：**$\lambda<\rho_f$ 则自锁**（负载推不动螺母，反驱不可能），完整推导见 [[减速器]] 与 [[Actuation#8.1 核心参数与类型谱系|Actuation §8.1 自锁判据]]。

代入 L25：取 $d_m\approx3$ mm，四指 $\tan\lambda=0.7/(\pi\times3)\approx0.074$（$\lambda\approx4.2°$）；拇指 $l=0.6$ mm、$d_m=3\sim5$ mm 给 $\lambda\approx2.2°\sim3.6°$。于是：

- 若是**滑动**丝杠（钢-钢滑动 $\mu\approx0.15$，$\rho_f\approx8.5°$）→ $\lambda<\rho_f$，**自锁**。
- 若是**滚动体式**丝杠（滚珠/滚柱，$\mu\approx0.003\sim0.01$，$\rho_f\approx0.2°\sim0.6°$）→ $\lambda>\rho_f$，**可反驱**，正反向效率都 $>90\%$。

> [!warning] 丝杠滚动体型式待核实：滚珠 / 滚柱
> 本库各文档对 L25 丝杠型式的说法不一（滚珠 / 行星滚柱 / 滚柱）。上面"可反驱"的结论**依赖它是滚动体式**这一事实。四指上电后可被掰动、无明显自锁，这一实测现象与"滚动体式"相容，与"滑动式"矛盾——是间接证据，不是 CAD 证据。

### 6.2 四指：低损耗传动把"高 $N_{eq}$"与"可反驱"解耦了

四指 $N_{eq}\approx108$，但丝杠是低摩擦滚动接触、前面没有齿轮箱，反向效率高，所以**上电后仍可反驱**。这说明减速比本身不决定自锁，**效率**才决定：$\eta_{fwd}<50\%$ 才会自锁（推导见 [[减速器]]）。这也是丝杠电缸相对蜗轮蜗杆方案的接触友好优势——高 $N_{eq}$ 带来大力与大 armature，却没有把关节锁死。

### 6.3 拇指：自锁来自 17:1 减速箱，不来自丝杠

拇指的丝杠升角虽然更小，但只要它是滚动体式，丝杠本身依然不自锁。**真正的自锁来自那级 17:1 折返齿轮箱**：反驱时，高速端（电机侧）的阻力矩 $T_h$ 被减速比 $i$ 放大后抵消负载：

$$\eta_{rev}=\left(1-\frac{T_l}{T_{load}}\right)\eta_m-\frac{T_h\,i}{T_{load}}$$

减数项 $T_h i/T_{load}$ 随 $i=17$ 线性放大，可以把 $\eta_{rev}$ 直接压到零以下 → 掰不动。注意这**与位置环 $k_p$ 无关**：手感硬来自传动自锁，不来自控制刚度（[[Transmission2JointDynamics_gap]] §2.4）。

| | 四指 | 拇指 |
|---|---|---|
| 丝杠 | 滚动体式（待核实） → 不自锁 | 同左 → 不自锁 |
| 前置减速 | 无 | 17:1 折返齿轮箱 → $\eta_{rev}<0$ |
| 上电后反驱 | **可以** | **不可以** |
| 对 RL 的含义 | 接触时能被环境"推回"，物理顺应 | 接触时像刚性位置源，接触力由 $k_p$ 与死区共同决定 |

---

## §7 填进仿真：Isaac Gym 与 MuJoCo 的 armature

**为什么现在讲这个**：算完了数，得知道往哪填、和哪些量绑定。

### 7.1 Isaac Gym

关节属性 `dof_props['armature']`（PhysX articulation），单位 kg·m²，逐 DoF 填：

| 关节 | `armature` | 来源 |
|---|---:|---|
| 四指 pip（及同型电缸关节） | $1.65\times10^{-3}$ | §3.3 |
| `thumb_mcp` | $2.84\times10^{-4}$ | §4.3 |
| `thumb_cmc_pitch` | $4.44\times10^{-4}$ | $N_{eq}\approx1800$ 同法折算（[[Transmission2JointDynamics_gap]] §六） |

PhysX 把 `armature` 直接加到关节空间质量矩阵的对角项上（$M_{jj}\leftarrow M_{jj}+J_{armature}$），与 [[Dynamics#3. 能量层：从 Hamilton 原理到操作器方程|Dynamics §3 操作器方程]] $M(q)\ddot q+C\dot q+N=\tau$ 里 $M(q)$ 的对角项对应——它不随构型变（引擎限制），而真实的 $N_{eq}(\theta)^2J_{rotor}$ 会变。

### 7.2 MuJoCo

MJCF `<joint armature="...">`，语义相同（加到 $M$ 对角、也进入隐式积分的惯性项）。**它和 `damping` 的放置方式绑定**：armature 改小之后，显式 PD 阻尼的稳定性条件 $k_dh/I_a<2$ 会被打破，阻尼必须走关节 `damping` 字段走隐式积分——这一条以及 `frictionloss` / `solimpfriction` 的配方见 [[MuJoCo_Sim2Real_Params]] 与 [[Transmission2JointDynamics_gap]] §5.2。

### 7.3 附注：MCU 命令平滑不在 armature 里

真机上关节对命令的滞后有三种来源，只有第一种与本篇有关：

| 滞后来源 | 物理量 | 归哪篇 |
|---|---|---|
| 惯量 + 阻尼 | $I_a/k_d$（拇指 ≈0.17 ms，测量带外） | 本篇（armature） |
| 固件命令预滤波（MCU 规划平滑：S 曲线 / 低通） | 时间常数 $T_f$，实测拟合 ≈120 ms；原项目文档给的量级"可达 150 ms"（**待核实**） | [[Actuator2RigidDynamicsModel_gap]]（MCU/CAN 时序链路） |
| 纯传输延迟 | $T_d\lesssim10$ ms（阶跃直测） | [[Actuator2RigidDynamicsModel_gap]] |

> [!warning] 别用 armature 或 $k_d$ 去"补"这几十毫秒相位
> $T_f$ 是命令侧的一阶预滤波，对首动时刻几乎不推迟、却贡献大量相位；它与惯量在频响上不可互换。曾经的教训：$T_d$ 从 45 ms 砍到实测 10 ms 后，优化器把 $k_d$ 推到网格上界来接管缺掉的相位，直到 $T_f$ 被单列出来（[[Transmission2JointDynamics_gap]] §4.2）。

---

## 回扣与承接

用 L25 的一根手指把本篇串一遍：**空心杯电机（$J_{rotor}=1.425\times10^{-7}$）→ 丝杠电缸（$l=0.7$ mm，导程增益 $2\pi/l\approx8976$ rad/m）→ 连杆（力臂 $r(\theta)\approx12$ mm）→ 关节**。

1. §2：转子经导程折成推杆侧 $M_{eq}=J_{rotor}(2\pi/l)^2=11.48$ kg——动能等效，速度平方。
2. §3：推杆经力臂折成关节侧 $J_{armature}=M_{eq}R^2=1.65\times10^{-3}$ kg·m²；消掉中间量就是 $N_{eq}^2J_{rotor}$，$N_{eq}=2\pi R/l=107.7$。
3. §4：拇指多一级 17:1，$N_{eq}=2\pi rN_{gear}/l=1424$，但转子轻 1018 倍，armature 反而只有 $2.84\times10^{-4}$。
4. §5：同一根链条上摩擦只按 $N^1$（功率平衡），惯量按 $N^2$（动能）——拇指因此是"低惯量、高摩擦"关节。
5. §6：四指可反驱（滚动体丝杠，待核实），拇指不可（17:1 齿轮箱把 $\eta_{rev}$ 压到零下）。
6. §7：数填进 Isaac Gym `armature` / MuJoCo `armature`，与 `damping` 的隐式放置绑定；命令平滑 $T_f$ 另算。

**下一篇去哪**：摩擦怎么测、死区怎么建 → [[Transmission2JointDynamics_gap]]；引擎字段逐条讲解 → [[MuJoCo_Sim2Real_Params]]；指令到电机轴的延迟/量化 → [[Actuator2RigidDynamicsModel_gap]]；整条链路的 gap 总图 → [[sim2real]]。

---

## 对开发与科研的启示

1. **armature 是一个可以从 CAD 直接算出、不需要辨识的量**（两个因子：$N_{eq}^2$ 与 $J_{rotor}$）。这意味着下一步 sysid 的自由度应该花在**摩擦与 $T_f$** 上，而不是再去拟 armature；[[Transmission2JointDynamics_gap]] §4 的"只用位置数据、armature 取 CAD 值"正是这条的落实。
2. **$N_{eq}(\theta)=2\pi r(\theta)/l$ 随构型变，而引擎 armature 是常数**。这意味着可以做一个小实验：把 $r(\theta)$ 从 CAD 里导出来，评估 $J_{armature}(\theta)$ 在工作区间的变化幅度；若超过 ±20%，值得在 mjlab 里逐步（per-step）改写 armature，或把它作为域随机化的一维。
3. **拇指"低惯量、高摩擦、不可反驱"是硬件性质**。这意味着策略侧对 `thumb_mcp` / `thumb_cmc_pitch` 应施加更低的动作带宽，把换向死区当作硬约束；WMTS 世界模型里对这两个关节的 actuator 子模块应显式含 set-valued 摩擦，而不是靠数据随机化抹平。
4. **反驱结论依赖丝杠滚动体型式**。这意味着下一步应从 CAD 或厂商确认 L25 丝杠是滚珠还是滚柱——它同时决定 §6 的自锁判据与 [[Transmission2JointDynamics_gap]] §2.3 里 $\mu_s/\mu_k$ 的取值区间。
