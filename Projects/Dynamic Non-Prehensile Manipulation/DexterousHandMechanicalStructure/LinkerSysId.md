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
