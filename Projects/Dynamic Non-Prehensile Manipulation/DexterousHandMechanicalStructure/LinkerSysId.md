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
related:
  - "[[Actuation]]"
  - "[[减速器]]"
  - "[[电机]]"
  - "[[传动]]"
  - "[[Dynamics]]"
  - "[[sim2real]]"
  - "[[Actuator2RigidDynamicsModel_gap]]"
---

# LinkerHand 电缸系统辨识：转子惯量 → 等效直线质量 → Isaac Gym `armature`

> [!abstract] 这是 [[Actuation#7.2 Reflected Inertia：为什么减速比是把双刃剑|Actuation §7.2 reflected inertia]] 在**丝杠直线驱动**下的具体落地
> 通用 reflected inertia 律 $J_{reflected}=i^2J_{motor}$ 说的是"减速比平方放大转子惯量"。这里把它用到 LinkerHand L25 的**旋转→直线电缸**上：旋转减速比换成**导程增益** $2\pi/l$，最终要交给仿真的量是 Isaac Gym 关节的 `armature`。下面每一步都能扣回 §7.2 的能量等效推导——目的是消除"仿真漏掉转子折算惯量、导致力控增益迁到真机就振荡"的 Sim-to-Real gap（[[Actuator2RigidDynamicsModel_gap|执行器↔刚体 gap]]）。

电缸将电机的旋转运动转化为了推杆的直线运动。虽然电机的转子惯量看起来极小（$0.1425 \text{ kg}\cdot\text{mm}^2$），但由于丝杆导程（Lead）只有 0.7 毫米，这意味着电机要疯狂转动一整圈（$360^\circ$），推杆才前进仅仅 0.7 毫米。

根据能量守恒和运动学折算，我们可以计算出这个微小转子等效到推杆上的**直线惯性质量（Equivalent Linear Mass, $M_{eq}$）**。

- **物理推导：**

  设丝杆导程为 $l = 0.7 \text{ mm} = 0.0007 \text{ m}$。

  转子惯量为 $J_{rotor} = 0.1425 \text{ kg}\cdot\text{mm}^2 = 1.425 \times 10^{-7} \text{ kg}\cdot\text{m}^2$。

  当推杆以速度 $v$ 直线运动时，电机的角速度 $\omega = v \cdot \frac{2\pi}{l}$。

  根据动能等效法则：

  $$\frac{1}{2} M_{eq} v^2 = \frac{1}{2} J_{rotor} \omega^2$$

  代入 $\omega$ 得出终极折算公式：

  $$M_{eq} = J_{rotor} \left( \frac{2\pi}{l} \right)^2$$

- **带入数据计算：**

  $$M_{eq} = 1.425 \times 10^{-7} \times \left( \frac{2\pi}{0.0007} \right)^2 \approx \mathbf{11.48 \text{ kg}}$$

要将刚才算出的直线质量（11.48 kg）最终转化为 Isaac Gym 关节所需的 `armature`（旋转关节的等效转动惯量，$kg\cdot m^2$），以及将推力转化为关节力矩，你必须知道机械连杆的**力臂（Lever Arm/Moment Arm, $R$）**。

- **关节有效力臂 ($R$)：** 丝杆推杆的直线作用力点到手指关节旋转轴心的垂直距离（约为 12 mm，会随构型改变而有轻微变化）。

  - **计算 `armature`：** 一旦拿到力臂 $R$，关节的真实 `armature` 就是：

    $$J_{armature} = M_{eq} \cdot R^2 = 11.48 \times (0.015)^2 \approx 0.00258 \text{ kg}\cdot\text{m}^2$$
    
  - **计算等效减速比**
  
    - 假设手指关节转动了微小角度 $\Delta \theta_{joint}$ (弧度)。
    - 对应的丝杠直线位移为 $\Delta x \approx R \cdot \Delta \theta_{joint}$ （其中 $R$ 为推杆作用点到关节旋转轴心的垂直力臂距离，）。
    - 丝杠移动 $\Delta x$ 距离，要求电机转过的角度为 $\Delta \theta_{motor} = \frac{\Delta x}{l} \cdot 2\pi$。
    - 将 2 代入 3，得到等效减速比的严谨公式：
    
    $$N_{eq} = \frac{\Delta \theta_{motor}}{\Delta \theta_{joint}} = \frac{2\pi \cdot R}{l}$$
    
    **粗略估计L25NS的减速比：**
    
    $$N_{eq} = \frac{2 \times 3.1415 \times 12}{0.7} \approx \mathbf{107.7}$$

---

> [!important] 一句话说透：这就是 $J_{reflected}=i^2J_{motor}$ 的丝杠版本
> 把三步串起来消掉中间量 $M_{eq},R$：
> $$J_{armature}=M_{eq}R^2=J_{rotor}\Big(\tfrac{2\pi}{l}\Big)^2R^2=J_{rotor}\Big(\tfrac{2\pi R}{l}\Big)^2=N_{eq}^2\,J_{rotor}.$$
> 于是**关节侧 `armature` = 等效减速比的平方 × 转子惯量**，与通用律 $J_{reflected}=i^2J_{motor}$ **完全同构**（$i\to N_{eq}=2\pi R/l$）——那个"平方"仍旧来自动能里的速度平方（见 [[Actuation#7.2 Reflected Inertia：为什么减速比是把双刃剑|§7.2 能量等效推导]]）。旋转-旋转传动的减速比 $i$，在旋转-直线电缸里换成了导程增益与力臂的乘积 $2\pi R/l$，物理内核不变。
>
> - **为什么必须填进仿真**：Isaac Gym 关节默认 `armature=0`，会**整项漏掉转子折算惯量**。对 L25 这类高 $N_{eq}$（≈108）传动，漏掉的 $N_{eq}^2J_{rotor}\approx2.6\times10^{-3}\ \text{kg·m}^2$ 与连杆本体惯量同量级，Sim 关节因此"过轻过灵"，在 Sim 里整好的阻抗/力控增益一迁到真机就振荡——这正是 [[Actuator2RigidDynamicsModel_gap|执行器↔刚体动力学 gap]] 的一个可量化来源。
> - **反驱动性对账**：$N_{eq}\approx108$ 看似"高减速比理应难反驱"，但滚珠丝杠 $\eta>90\%$（螺旋角 > 摩擦角、滚动替代滑动，见 [[减速器]] 与 [[Actuation#8.1 核心参数与类型谱系|§8.1 自锁判据]]），故灵心巧手上电后**仍可反驱、无明显自锁**——**低损耗传动把"高 $N_{eq}$"与"可反驱"解耦**了，这也是它相对蜗轮蜗杆自锁方案的接触友好优势。
