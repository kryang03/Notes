---
tags:
  - sim-to-real
  - dexterous-hand
  - mechanical-design
  - reinforcement-learning
aliases:
  - Sim-to-Real Gap 分析
  - sim2real gap
  - 仿真到真机迁移
related:
  - "[[传动]]"
  - "[[电机]]"
  - "[[减速器]]"
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
---

# 灵巧手机械结构的 Sim-to-Real Gap 分析

> [!abstract] 核心论点
> 在基于强化学习的灵巧操作中，仿真器（IsaacGym / MuJoCo / Isaac Lab）将力矩直接施加在理想化的关节上，但真机中电机输出的扭矩需经过减速器、传动机构才能到达关节——**这条力传递链路中的每一个非理想环节都是 Sim-to-Real Gap 的来源**。本文系统分析不同[[电机]]、[[减速器]]和[[传动]]方案对仿真建模与真机部署之间差异的影响，为选型和 Domain Randomization 策略提供依据。

---

## 1. 仿真器的理想化假设

### 1.1 IsaacGym / MuJoCo 的关节力矩模型

在主流物理仿真器中，RL 策略输出的 action 通常被解释为**关节力矩** $\tau$ 或**关节目标位置** $q^*$（通过 PD 控制器转换为力矩），直接施加于刚体关节：

$$
M(q)\ddot{q} + C(q,\dot{q})\dot{q} + g(q) = \tau_{sim}
$$

这一模型隐含了以下**理想化假设**：

| 假设 | 仿真中的处理 | 真机现实 |
|-----|-----------|---------|
| 力矩瞬时施加 | $\tau$ 在每个仿真步直接生效 | 电机有电气/机械时间常数 |
| 零背隙 | 关节力矩-角度为单值映射 | 减速器存在背隙死区 |
| 零摩擦或简单摩擦 | 无摩擦或仅粘滞摩擦 | Stribeck 非线性摩擦 |
| 刚性关节 | 关节无弹性变形 | 谐波减速器柔轮有弹性 |
| 完美力矩传递 | $\tau_{joint} = \tau_{sim}$ | $\tau_{joint} = \eta \cdot i \cdot \tau_{motor} - \tau_{friction}$ |
| 独立关节 | 各关节独立驱动 | 欠驱动耦合、腱绳交叉耦合 |
| 无热效应 | 力矩上限恒定 | 连续运行后热降额 |

### 1.2 力矩传递链路的完整模型

真实的关节力矩输出应为：

$$
\tau_{joint} = \eta(T, \dot{q}) \cdot i \cdot K_t \cdot I - \tau_{friction}(\dot{q}, T) - k(\theta_{twist}) \cdot \theta_{twist}
$$

其中：
- $\eta(T, \dot{q})$ — 减速器效率（温度和速度相关）
- $i$ — 减速比
- $K_t$ — 电机力矩常数
- $I$ — 电流
- $\tau_{friction}$ — Stribeck 摩擦力矩
- $k(\theta_{twist})$ — 减速器扭转刚度（非线性）
- $\theta_{twist}$ — 减速器扭转变形角

仿真器直接跳过了这整条链路，将 $\tau_{sim}$ 等效为 $\tau_{joint}$。

---

## 2. 电机选型对 Sim-to-Real 的影响

### 2.1 各电机类型的 Gap 来源

| 电机类型 | 力矩线性度 | 响应延迟 | 齿槽干扰 | 热漂移 | Sim-to-Real 友好度 |
|---------|----------|---------|---------|-------|-----------------|
| [[电机#1. 有刷直流电机 (Brushed DC Motor)|有刷直流电机]] | 高（$\tau = K_t I$） | 中（电感+机械） | 无 | 中（电刷磨损） | ⭐⭐⭐ |
| [[电机#2. 无刷直流电机 (BLDC Motor)|BLDC (FOC)]] | **极高** | **极低**（FOC 带宽 > 1kHz） | 有（可通过 FOC 补偿） | 低 | ⭐⭐⭐⭐ |
| [[电机#3. 无框力矩电机 (Frameless Torque Motor)|无框力矩电机]] | **极高** | **极低** | 低 | 中（散热依赖结构） | ⭐⭐⭐⭐⭐ |
| [[电机#4. 空心杯电机 (Coreless Motor)|空心杯电机]] | **极高** | **极低**（惯量最小） | **零** | 差（无铁芯散热差） | ⭐⭐⭐⭐ |
| [[电机#5. 伺服电机系统 (Servo Motor System)|RC 舵机]] | 低（齿轮组非线性） | 高（多级齿轮惯量） | 有 | 中 | ⭐ |

### 2.2 关键 Gap 分析

#### 2.2.1 电气时间常数 vs 仿真时间步

电机的电气时间常数 $\tau_e = L/R$ 决定了电流上升速度（即力矩响应速度）：
- 空心杯电机 $\tau_e \approx 0.1 \text{ ms}$（电感极低）
- BLDC $\tau_e \approx 0.5–2 \text{ ms}$
- 有刷电机 $\tau_e \approx 1–5 \text{ ms}$

IsaacGym 的仿真步长通常为 $dt = 1/60 \text{ s} \approx 16.7 \text{ ms}$（控制频率 60 Hz）或 $dt = 1/120 \text{ s} \approx 8.3 \text{ ms}$。对于空心杯和 BLDC+FOC，电气响应远快于控制周期，力矩可视为"瞬时施加"——**仿真假设基本成立**。但若使用高惯量有刷电机或 RC 舵机，响应延迟不可忽略。

> [!tip] 实践建议
> 选择 BLDC+FOC 或空心杯电机的灵巧手，电机响应延迟对 Sim-to-Real 的影响可忽略。仿真中可不建模电气动态。

#### 2.2.2 齿槽效应 (Cogging Torque)

有铁芯 BLDC 电机在低速旋转时，转子永磁体与定子齿槽之间的磁力会产生周期性的力矩脉动（齿槽转矩）。仿真中完全不存在此效应。

**影响**：低速精密力控时，齿槽效应导致实际输出力矩在电流对应力矩附近波动，引起手指微颤或位置精度下降。

**缓解方案**：
- 选择**空心杯电机**（零齿槽）
- 使用 FOC 驱动时加入**齿槽补偿表** (Cogging Map)
- 仿真中通过 Domain Randomization 对力矩添加周期性扰动

#### 2.2.3 热降额 (Thermal Derating)

电机连续运行时绕组温度上升，导致铜电阻增大（$R = R_0(1 + \alpha \Delta T)$），同一电流下力矩不变但电压需求增加，最终达到驱动器电压上限后强制限流——等效为**力矩上限随时间下降**。

仿真中力矩上限是恒定的（`effort_limit`），不随时间变化。在需要**持续高力矩输出**的任务（如抓持重物长时间搬运）中，这一差异会导致 Sim-to-Real Gap。

---

## 3. 减速器选型对 Sim-to-Real 的影响

### 3.1 各减速器类型的 Gap 来源

| 减速器类型 | 背隙 | 摩擦非线性 | 扭转弹性 | 反驱动性 | Sim-to-Real 友好度 |
|-----------|------|----------|---------|---------|-----------------|
| [[减速器#2.1 行星齿轮箱 (Planetary Gearbox)|行星齿轮箱]] | ⚠️ 中（8–15 arcmin） | 中 | 低 | 良好 | ⭐⭐⭐ |
| [[减速器#2.3 蜗轮蜗杆减速器 (Worm Gearbox)|蜗轮蜗杆]] | 低 | **极高**（自锁） | 低 | **不可** | ⭐ |
| [[减速器#2.4 谐波减速器 (Harmonic Drive)|谐波减速器]] | ✅ 零 | 中偏高 | **高（非线性）** | 中偏差 | ⭐⭐⭐ |
| [[减速器#2.5 摆线针轮减速器 (Cycloidal Gearbox)|摆线针轮]] | 低 | 中 | 低 | 中 | ⭐⭐⭐ |
| 无减速器（直驱） | ✅ 零 | **极低** | **零** | **最佳** | ⭐⭐⭐⭐⭐ |
| 低比减速（QDD） | 低 | 低 | 极低 | 良好 | ⭐⭐⭐⭐ |

### 3.2 关键 Gap 分析

#### 3.2.1 背隙 (Backlash)

**现象**：当关节力矩方向反转时（如手指从抓取切换到释放），减速器齿轮间的间隙导致一小段"空行程"，在此期间输出端几乎没有力矩响应。

**仿真影响**：
- 仿真中关节为**零间隙**理想铰链，力矩方向切换瞬时生效
- 真机中存在背隙死区 $\Delta\theta \approx 0.02°–0.25°$（对应 1–15 arcmin）
- 在精细操作中（如旋转笔、翻转物体），频繁的力矩方向切换使背隙效应累积

**Domain Randomization 策略**：
```python
# 在仿真中近似背隙效应
backlash_angle = uniform(0, 0.004)  # rad, ~0.25°
if sign(tau_t) != sign(tau_t_prev):
    tau_effective = 0  # 死区
```

> [!warning] 谐波减速器的零背隙优势
> [[减速器#2.4 谐波减速器 (Harmonic Drive)|谐波减速器]]的弹性预载使其实现零背隙——这是其在灵巧手中被广泛采用的核心原因之一。从 Sim-to-Real 角度，零背隙显著降低了仿真与真机之间的力矩传递差异。

#### 3.2.2 非线性摩擦

**现象**：减速器内部摩擦遵循 Stribeck 模型（详见 [[减速器#1. 减速器核心参数]]），从静止到运动的转变过程中摩擦力矩先从静摩擦 $F_s$ 下降到库仑摩擦 $F_c$，然后随速度增大线性增加（粘滞项）。

**仿真影响**：
- IsaacGym 中 `joint_friction` 参数仅建模粘滞摩擦 $b\dot{q}$，忽略了：
  - 静→动摩擦的 Stribeck 过渡
  - 摩擦的温度依赖性
  - 预滑动微位移 (Pre-sliding displacement)
- MuJoCo 提供了更精细的摩擦模型（`frictionloss` 参数对应库仑摩擦），但仍未建模 Stribeck 效应

**影响程度**：
- 高减速比方案（谐波/RV）：摩擦损耗 10–35%，影响大
- 低减速比方案（QDD）：摩擦损耗 3–10%，影响小
- 直驱：仅轴承摩擦，< 2%，几乎可忽略

#### 3.2.3 扭转弹性 (Torsional Compliance)

**现象**：[[减速器#2.4 谐波减速器 (Harmonic Drive)|谐波减速器]]的柔轮在传递力矩时发生弹性变形，关节实际角度 $q_{actual}$ 与电机编码器测量角度 $q_{encoder}$ 之间存在偏差：

$$
q_{actual} = q_{encoder}/i - \tau_{load}/k(\tau_{load})
$$

其中 $k$ 为非线性扭转刚度。

**仿真影响**：
- 仿真中关节为刚性，$q_{actual} = q_{encoder}/i$，无弹性偏差
- 真机中高载荷下弹性偏差可达 $0.1°–0.5°$
- 弹性关节还引入了**二阶动力学响应**（弹簧-质量系统），产生振荡，仿真中不存在

**缓解方案**：
- 使用 MuJoCo 的弹性关节模型（设置关节 `stiffness` 和 `damping`）
- 对弹性刚度进行 Domain Randomization

#### 3.2.4 效率损耗与力矩缩放

仿真中 RL 策略输出的 $\tau_{sim}$ 在真机中需经过效率缩放：

$$
\tau_{real} = \eta \cdot \tau_{sim} \quad (\eta < 1)
$$

| 减速器 | 正向效率 $\eta_{fwd}$ | 反向效率 $\eta_{rev}$ | 力矩缩减 |
|-------|---------------------|---------------------|---------|
| 行星齿轮 | 95–97% | 90–95% | 3–10% |
| 谐波 | 65–90% | 40–70% | 10–60% |
| 蜗轮蜗杆 | 30–90% | **~0%** | **完全丧失** |
| 摆线针轮 | 85–95% | 75–90% | 5–25% |

> [!warning] 正向与反向效率不对称
> 减速器的正向效率（电机→关节）与反向效率（关节→电机）通常不相等。谐波减速器的反向效率仅为正向的 60–80%，这意味着**外力推动关节时的力矩反馈远小于仿真预期**——对力感知和阻抗控制策略影响显著。

---

## 4. 传动方案对 Sim-to-Real 的影响

### 4.1 欠驱动耦合 (Underactuation Coupling)

> [!warning] 欠驱动是 Sim-to-Real 的核心挑战之一
> 许多灵巧手（尤其是腱绳和连杆传动）采用欠驱动设计，例如 **PIP-DIP 耦合**：一个电机同时驱动指中关节（PIP）和指尖关节（DIP），两者之间通过连杆或差分腱绳以固定比例联动。

**仿真中的处理**：
- IsaacGym/MuJoCo 中可以定义耦合关节（`mimic joint` 或通过 URDF 的 `transmission` 标签）
- 但仿真中的耦合是**运动学层面的理想耦合**：$q_{DIP} = k \cdot q_{PIP}$
- 真机中的耦合是**力学层面的非理想耦合**：受摩擦、弹性、间隙影响

**具体差异**：
1. **负载可变耦合比**：当 DIP 接触物体受到外力时，连杆/腱绳的弹性变形使耦合比偏离理想值
2. **单向耦合约束**：腱绳只能拉不能推，DIP 可能在某些构型下"松脱"而非跟随 PIP
3. **差分机构的力分配**：差分滑轮向两个指节分配力矩的比例取决于各指节的阻力，仿真中难以精确建模

**实际影响**：
- RL 策略在仿真中学到的 PIP 控制策略在真机上可能导致 DIP 行为不一致
- 接触状态切换时（如从自由运动到与物体接触），耦合行为发生突变

### 4.2 腱绳传动的特殊挑战

腱绳传动系统引入了仿真中最难建模的一组非线性效应：

| 效应 | 仿真建模难度 | 对 Gap 的贡献 |
|-----|-----------|-------------|
| **Capstan 摩擦** | 极高（路径相关） | 力矩传递效率不确定 |
| **腱绳弹性** | 高（蠕变+迟滞） | 位置/力矩响应滞后 |
| **预紧力衰减** | 中（需时变模型） | 长时间运行后性能退化 |
| **耦合矩阵非线性** | 极高 | 关节间力矩交叉耦合 |
| **腱绳松弛检测** | 高 | 松弛腱绳瞬间无力控能力 |

> [!note] 腱绳传动的仿真策略
> 当前主流 RL 工作（如 Shadow Hand in-hand rotation）通常**不直接建模腱绳**，而是：
> 1. 将 RL action 解释为关节力矩/位置（假设腱绳-关节映射为理想）
> 2. 依靠 **Domain Randomization** 覆盖腱绳非线性带来的不确定性
> 3. 结合系统辨识（System Identification）离线标定腱绳参数
>
> 这种做法在一定程度上有效，但对于**高动态非预抓取操作**（如抛接、旋转笔），腱绳非线性的影响更加显著。

### 4.3 直驱：最小 Sim-to-Real Gap

[[传动#3. 直驱 (Direct Drive)|直驱方案]]消除了所有传动中间环节，力矩传递链路简化为：

$$
\tau_{joint} = K_t \cdot I - b\omega
$$

**Gap 来源仅剩**：
- 轴承摩擦（极小，< 2% 额定扭矩）
- 电机齿槽效应（空心杯/无框力矩电机可消除）
- 热降额（长时间运行）

这使得直驱方案的仿真与真机之间差异最小化，是对 **Sim-to-Real 最友好的选择**。

### 4.4 准直驱 (QDD)：平衡 Gap 与性能

[[传动#4. 准直驱 (Quasi-Direct Drive, QDD)|QDD]] 在低减速比（$i \leq 10$）下引入的 Gap 远小于高减速比方案：
- 背隙与级数成正比——单级行星减速背隙可控
- 摩擦损耗按 $(1-\eta)$ 缩放——95% 效率仅损失 5%
- Reflected inertia = $i^2 J_{motor}$——较直驱增大但远小于谐波方案

---

## 5. 综合方案选型矩阵

### 5.1 Sim-to-Real 友好度排名

| 排名 | 传动+电机+减速器组合 | Sim-to-Real Gap 等级 | 典型灵巧手 |
|-----|-------------------|-------------------|----------|
| 1 | 直驱 + 无框力矩/空心杯 + 无减速 | **最小** | Allegro v4 |
| 2 | QDD + BLDC(FOC) + 低比行星 | 小 | MIT-style hands |
| 3 | 连杆 + BLDC + 谐波减速 | 中 | DLR Hand |
| 4 | 连杆 + BLDC + 行星减速 | 中偏大 | Schunk SDH |
| 5 | 腱绳 + BLDC + 行星减速 | 大 | LEAP Hand |
| 6 | 腱绳 + 气动 | **最大** | Shadow Hand (pneumatic) |

### 5.2 Domain Randomization 参数建议

根据不同传动方案，建议在仿真训练中随机化以下参数：

| 参数 | 直驱 | QDD | 齿轮传动 | 腱绳传动 |
|-----|------|-----|---------|---------|
| **关节摩擦** $b$ | ±20% | ±30% | ±50% | ±80% |
| **关节阻尼** $d$ | ±15% | ±25% | ±40% | ±60% |
| **力矩缩放** (效率) | ±5% | ±10% | ±20% | ±30% |
| **关节刚度** $k$ | N/A | ±10% | ±30% | ±50% |
| **背隙角度** | N/A | ±0.002 rad | ±0.005 rad | N/A |
| **力矩延迟** (steps) | 0 | 0–1 | 0–2 | 0–3 |
| **耦合比偏差** | N/A | N/A | ±5% | ±15% |

> [!tip] Action Space 设计建议
> - **直驱/QDD**：可直接使用 **torque control**（action = 关节力矩），因为电机电流-力矩线性关系直接映射
> - **高减速比传动**：建议使用 **position control**（action = 目标关节角度 + PD 控制器），让底层 PD 控制器吸收减速器非线性
> - **腱绳传动**：建议使用 **position control** + **力矩限幅**，避免 RL 策略直接操作力矩空间中难以建模的非线性区域

---

## 6. 仿真建模实践指南

### 6.1 IsaacGym 中的关键配置

```python
# 关节属性配置 — 考虑机械结构非理想性
asset_options = gymapi.AssetOptions()
asset_options.fix_base_link = True
asset_options.default_dof_drive_mode = gymapi.DOF_MODE_EFFORT  # 直驱: torque mode

# 每个关节的属性
dof_props = gym.get_asset_dof_properties(asset)
for i in range(num_dofs):
    dof_props['friction'][i] = 0.05     # 粘滞摩擦近似
    dof_props['damping'][i] = 0.01      # 关节阻尼
    dof_props['effort'][i] = max_torque  # 力矩上限 (不含热降额)
```

### 6.2 欠驱动关节的 URDF 建模

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
> URDF 的 `mimic` 标签实现的是**纯运动学耦合**（$q_{dip} = 0.67 \cdot q_{pip}$），不建模力学耦合。在真机中，当 DIP 接触物体时 PIP 的受力会改变——仿真中不会体现这一效应。对于接触丰富的灵巧操作，建议在仿真中将耦合关节改为独立关节 + 弹簧约束以近似力学耦合。

### 6.3 总结

> [!abstract] 核心结论
> 1. **直驱和 QDD 是 Sim-to-Real 最友好的方案**——Gap 最小，Domain Randomization 幅度最小
> 2. **谐波减速器的零背隙优势在 Sim-to-Real 中至关重要**——但要注意其非线性刚度和效率损耗
> 3. **腱绳传动的 Sim-to-Real Gap 最大**——需要最激进的 Domain Randomization 或系统辨识
> 4. **欠驱动耦合在仿真中通常被过度理想化**——接触状态变化时真机行为可能显著偏离仿真
> 5. **Action Space 的选择应匹配传动方案**——直驱用力矩，有减速器用位置
> 6. **机械结构选型决定了 RL 技术路线的上限**——硬件设计与算法设计应协同考虑

---

## 7. 相关研究与知识图谱关联

### 7.1 Sim-to-Real 方法论

本文档的硬件级分析构成了 Sim-to-Real Gap 的**底层物理来源**，与以下 RL 层面的迁移方法形成互补：

- [[ReinforcementLearning#5. Bridging the Gap: Sim-to-Real & Offline RL|RL Sim-to-Real 方法综述]] — Domain Randomization、System ID、Online Adaptation 理论框架
- [[A Survey of Sim-to-Real Methods in RL]] — MDP 四要素分类法：本文档侧重 Action 和 Transition 层面的 Gap
- [[Reinforcement Learning in Robotic Systems - A Review on Sim-to-Real Transfer]] — 执行器级建模视角，与本文 §2-§4 直接对应
- [[Grounded Action Transformation]] — 学习 $a_{real} = h(s, a_{sim})$ 映射修正仿真中的执行器非理想性
- [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction]] — 在线修正策略，补偿本文分析的硬件非线性

### 7.2 神经动力学补偿

针对本文 §1.2 力矩传递链路模型中难以精确辨识的参数（$\eta$, $\tau_{friction}$, $k$），以下工作用数据驱动方法直接学习残差：

- [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]] — 关节级神经动力学模型，直接学习 $\Delta\tau = f_{NN}(q, \dot{q}, \tau_{cmd})$
- [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]] — 环境编码器从历史序列推断隐式物理参数 $z_t$，实现在线自适应
- [[Minimalist Compliance Control]] — 方向相关效率模型，以最小参数辨识代价实现谐波减速器力控

### 7.3 对 DNPM 项目的直接影响

> [!tip] 与 DNPM 实验设计的关联
> 本分析直接影响以下 Idea 的实验设计：
> - [[Idea-001-Phase-Adaptive Impedance]] — 时变阻抗参数的 DR 范围应参考 §5.2 建议
> - [[Idea-005-Test-Time Contact Adaptation]] — 在线辨识的参数集应覆盖 §1.2 力矩链路中的 $\eta$, $\tau_{friction}$, $k$
> - [[Idea-007-Dual Orthogonal Curriculum]] — 物理轴课程的 α-scaling 可结合硬件特性选择参数化方向
