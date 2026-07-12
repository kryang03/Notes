---
tags: [Dexterous_Manipulation, Actuator_Dynamics, Sim-to-Real, L25_Hand, WMTS]
aliases: [Actuator2Rigid Gap, L25 硬件分析]
date: 2026-04-15
related:
  - "[[Actuation]]"
  - "[[FOC_Control]]"
  - "[[Final_WMTS]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
---

# Actuator-to-Rigid Dynamics Gap：L25 灵巧手硬件深度分析

> [!abstract] 核心命题
> 在高动态灵巧操作中，**电流 ≠ 关节力矩**。从力矩指令到指尖输出力之间隔着电磁非线性、传动摩擦和连杆耦合三级鸿沟。本文档系统分析 L25 灵巧手的硬件特性，推导 Actuator Model 与 Rigid Dynamic Model 之间的信息流重构方案。

---

## 一、 串级控制结构与物理方程

L25 灵巧手底层采用标准的串级控制（Cascaded Control）：位置环 → 速度环 → 电流环。

### 1.1 电学方程（电流环被控对象）

$$U = L \frac{di}{dt} + R i + K_e \omega_m$$

> [!warning] 高速场景的电压饱和
> 在灵巧手快速伸展手指时，$K_e \omega_m$ 占据大部分电压余量，导致电流爬升率 $di/dt$ 受限。RL 策略在高速状态下输出的高频力矩指令会被底层硬件物理极限无情滤除——表现为"软弱无力"。

### 1.2 电磁力矩方程

空心杯电机在正常工作区间内，电磁力矩与电流严格线性：$\tau_e = K_t i$

### 1.3 机械动力学方程

$$J\dot{\omega} = \tau - c\omega - \tau_d$$

$J$：转子惯量，$c\omega$：粘性摩擦力矩，$\tau_d$：负载力矩——**连接电机系统与刚体动力学系统的核心桥梁**。

---

## 二、 电机参数到刚体动力学的完整映射

孤立地将电流等同于关节输出力矩，在静态抓取时勉强可用，但在高动态操作中会导致巨大误差。

### 2.1 运动学映射

电机角度/速度通过减速器（减速比 $N$）严格映射到关节空间：

$$\theta_{joint} = \frac{\theta_m}{N}, \quad \dot{\theta}_{joint} = \frac{\omega_m}{N}$$

### 2.2 动力学映射（力矩传递损耗与畸变）

$$\tau_{joint} = \left( K_t \cdot i - J_m \ddot{\theta}_m - C_m \dot{\theta}_m - \tau_{fric}(\dot{\theta}_m) \right) \cdot N \cdot \eta$$

- $J_m \ddot{\theta}_m$：**转子惯量力矩**——高动态灵巧操作中（急停/反转），等效到关节端的转子惯量被放大 $N^2$ 倍（$J_{eq} = N^2 J_m$），可能比外部负载还大
- $\tau_{fric}$：静摩擦与库仑摩擦
- $\eta$：传动效率（行星滚柱丝杠效率波动）

### 2.3 控制架构

**位置控制（PD + 动力学前馈）**：

$$i_{cmd} = \frac{1}{K_t \cdot N} \left( K_p(\theta_{jd} - \theta_j) + K_d(\dot{\theta}_{jd} - \dot{\theta}_j) + \tau_{ff} \right)$$

**力矩控制**：
- **方案 A（无传感器）**：$i_d = \frac{\tau_{target}}{K_t N \eta}$（缺陷：摩擦力无法准确建模）
- **方案 B（力矩传感器闭环）**：在减速器输出端安装 JTS，实现真正的"透明化"刚体动力学控制

---

## 三、 L25 灵巧手 CAN 协议与可读取量分析

L25 灵巧手通过 **CAN 总线**（1Mbps）通信，16 DOF 分布在五根手指上。

| **类别** | **变量** | **读/写** | **单位/范围** | **关节数** | **实现机制** |
|:--|:--|:-:|:--|:-:|:--|
| 运动控制 | 关节角度 | R/W | 0-100 归一化 | 16 | 磁编码器/电位计绝对位置 |
| 运动控制 | 关节速度 | R/W | 0-100 归一化 | 16 | 固件内部速度环 PID |
| 运动控制 | 关节力矩 | R/W | 0-100 归一化 | 16 | 电流环近似模拟（$K_t \cdot I_q$） |
| 感知 | 触觉传感器 | R | uint8 矩阵 | 5×12×6 | 分帧传输，高密度薄膜阵列 |
| 感知 | 电机温度 | R | °C | 16 | NTC 热敏电阻 |
| 状态 | 故障代码 | R/W | 位掩码 | 16 | 堵转/过流/过温/通信异常 |

### 3.1 SDK 到硬件的时序链路

L25 的上位机控制并不是“策略输出后同时作用于 16 个关节”，而是一条串行通信链：

$$
\pi_\theta(o_t) \to a_t \to \text{SDK Manager} \to \text{CANMessageDispatcher} \to \text{CAN bus} \to \text{finger MCU} \to \text{FOC current loop}.
$$

- **宿主机阶段**：PC/4090 上的策略产生 $a_t$ 或 $\tau_{cmd}$ 后，SDK 将其写入 `_send_queue`；后台发送线程按 `SEND_INTERVAL_S = 0.0003s` 串行发送 CAN 帧。
- **总线阶段**：运动指令按手指分组封装，角度帧约为 `0x41-0x45`，速度帧约为 `0x49-0x4D`，力矩帧约为 `0x51-0x55`。CAN 1Mbps 总线通过非破坏性仲裁保证高优先级帧不被低优先级帧破坏，但代价是多帧指令存在先后到达的相位差。
- **MCU 阶段**：手指内部 MCU 收到帧后，将归一化指令转为位置/速度/电流环参考值；FOC 电流环在更高频率上闭合，具体电流到力矩链路见 [[FOC_Control#二、 物理本源：定子方程与坐标系降维|FOC 物理本源]]。

> [!important] 对 World Model 的含义
> 16 DOF 的控制写入在软件 API 上看似同步，真实硬件上却是按 CAN 帧串行落地。因此 [[Idea-002-Latency-Aware-Actuator|Latency-Aware Actuator]] 不应只建模一个全局 latency，而应至少保留“手指级/关节级执行时间戳”或其低维编码 $z_{\delta,t}$。

### 3.2 归一化指令不是物理量

SDK 的角度、速度、力矩接口都暴露为 $[0,100]$ 的归一化数值，并在 CAN 层线性映射为单字节原始值：

$$
u_{raw}=\operatorname{round}\left(255\cdot \frac{u_{sdk}}{100}\right),\qquad u_{sdk}=100\cdot \frac{u_{raw}}{255}.
$$

这意味着：

- `torque=100` 只是固件允许的最大电流/力矩百分比，不等价于固定的 N·m；它会随温度、转速、反电动势、丝杠摩擦和安全限流改变。
- `speed=100` 只是固件速度环的最大参考比例，不等价于固定 rad/s；高速区会被反电动势电压天花板截断。
- 任何把 SDK 百分比直接当作物理单位拟合的模型，都会把固件策略、硬件热状态和机械传动损耗混成一个不可解释黑箱。

### 3.3 读取模式与观测可信度

SDK 提供三层读取模式：

| 模式 | 机制 | 适合用途 | 风险 |
|:--|:--|:--|:--|
| Polling | 后台线程按固定频率发送查询帧 | 长时间记录、低侵入数据采集 | 查询本身占用 CAN 带宽 |
| Blocking | 清空缓存后发送请求，等待对应回调唤醒 | 标定和单步诊断 | 阻塞时间包含总线排队与 MCU 响应 |
| Snapshot | 读取 `DataRelay` 中最近一次成功解析值 | RL 高频观测 | 可能混合不同手指的不同时刻数据 |

力觉数据最容易产生相位差：每指 72 字节触觉需要 12 个 CAN 帧拼接，且 `ForceSensorManager` 对不同手指请求加入约 2.5ms 间隔。对真机 RL 而言，全手触觉矩阵不是同一物理时刻的严格同步快照，而是一个带时间戳结构的异步观测。

### 3.4 嵌入式概念闭环：MCU、STM32 与 CAN

MCU 是“把 CPU、存储器和外设集成在单芯片上”的实时控制计算机；STM32 是基于 ARM Cortex-M 的具体 MCU 产品族；CAN 是多个 MCU/驱动节点之间共享的抗干扰通信总线。三者在灵巧手中的角色是：STM32/同类 MCU 运行手指局部闭环，CAN 在上位机与各指节点之间传递命令和观测。

CAN 的可靠性来自差分信号：

$$
V_{diff}=V_{CAN\_H}-V_{CAN\_L}.
$$

若外部电磁噪声以共模形式叠加到两根线，$(V_{CAN\_H}+\Delta V)-(V_{CAN\_L}+\Delta V)=V_{diff}$，差分电压不变。CAN 的实时性则受位时序限制：

$$
BaudRate=\frac{1}{(1+t_{PROP}+t_{PHASE1}+t_{PHASE2})T_q}.
$$

因此，CAN 很可靠，但不是无限带宽、无限同步的“理想总线”。L25 的执行器模型必须同时接受“差分通信抗噪声强”和“多指高频观测/控制存在排队相位差”这两个事实。

---

## 四、 电气与传感特征的带宽瓶颈

### 4.1 高频感知的总线瓶颈

- 全手力觉数据 360 字节/次，CAN 1Mbps 下占据显著总线带宽
- `ForceSensorManager` 强制 2.5ms 指间请求延迟（MCU 处理上限），力觉反馈存在"指间相位差"

### 4.2 热漂移与 $K_t$ 不稳定性

空心杯电机无铁芯、转子热容极小。温度升高时绕组电阻增大，相同电流指令产生的物理力矩因 $K_t(T)$ 衰减而漂移。详见 [[FOC_Control#四、 温度对电机模型参数的系统性影响|FOC §四]]。

### 4.3 反电动势与速度-力矩包络

高速拨动时 Back-EMF 抵消驱动电压，形成非线性的转矩-转速饱和区。详见 [[FOC_Control#5.1 反电动势电压天花板与弱磁区域|FOC §5.1]]。

---

## 五、 机械传动与耦合非线性

### 5.1 16 主动 + 5 被动 DOF 的耦合结构

- Thumb：4 主动 DOF（abd, yaw, root1, tip）
- 其余四指：各 3 主动 DOF（abd, root1, tip）
- **DIP 耦合**：5 个 DIP 关节为被动自由度，通过连杆与 PIP 机械耦合（$\theta_{DIP} = f(\theta_{PIP})$），在 Rigid Dynamic Model 中必须设为 Holonomic Constraint

### 5.2 丝杠传动的 Stribeck 摩擦

行星滚柱丝杠在速度过零点时存在巨大静摩擦（Stiction）。低力矩指令被静摩擦力吞噬导致手指不动，突破后突然滑动——产生"stick-slip"跳变。

$$\tau_{fric}(\dot{\phi}) = \left[F_c + (F_s - F_c)e^{-|\dot{\phi}/v_s|^{\delta_s}}\right]\text{sign}(\dot{\phi}) + B_v \dot{\phi}$$

---

## 六、 World Model 信息流重构：三级非线性映射

### 6.1 电磁力矩 → 直线推力（丝杠级）

$$F_{linear} = \frac{2\pi \eta}{p} \tau_m - F_{friction}(\dot{x}, T)$$

### 6.2 直线推力 → 关节力矩（连杆耦合）

$$\tau_{joint} = J^T(x) \cdot F_{linear}$$

传动雅可比 $J(x)$ 时变，DIP-PIP 耦合使外力通过连杆逆向改变等效惯量和摩擦分布。

### 6.3 高动态操控的关键畸变

1. **Back-EMF 硬截断**：$U_{max} \ge L(T) \frac{di_q}{dt} + R(T) i_q + K_e \omega_m$ → 高速下电流爬升受限
2. **$K_t(T)$ 热衰减**：$R_s$ @80°C +31%、$K_t$ @80°C -9.6% → 正反馈热失控环路
3. **传动比角度依赖**：丝杠和 PIP/DIP 强耦合连杆的 Jacobian 和静摩擦力**高度依赖当前手指弯曲角度**

---

## 七、 RL State Space 设计法则

> [!tip] 核心原则
> **绝对不要将底层电流推算的力矩作为高权重或可信的观测状态**。因为该力矩在传递到指尖之前已被热漂移 $K_t(T)$、丝杠静摩擦、非线性 Jacobian 和连杆弹性形变严重"污染"。

### 7.1 刚性状态：关节角度与速度

- **$\theta_{meas}$ (16D)**：编码器位置——唯一的运动学 Ground Truth（⭐⭐⭐⭐）
- **$\dot{\theta}_{meas}$ (16D)**：差分求速度噪声大，建议引入 KF 或将历史角度序列 $[\theta_{t-k}, \ldots, \theta_t]$ 输入 RNN/Transformer（⭐⭐⭐）

### 7.2 接触状态：高维触觉传感

- **$F_{tactile}$ (5×12×6)**：摒弃基于电流的接触力估算；直接使用高密度触觉阵列数据——提供接触法向量、物体局部曲率和滑动趋势（⭐⭐⭐⭐）

### 7.3 隐式动力学状态：温度与时序

- **$T_{motor}$ (16D)**：温度是系统时变动力学参数的隐变量。网络通过 $T$ 隐式学习当前电机的阻力和出力上限，实现自适应控制（⭐⭐⭐⭐）

| 信号 | 可靠性 | 推荐用途 |
|:--|:-:|:--|
| 关节角度 $\phi_t$ | ⭐⭐⭐⭐ | **RL 核心观测 + WM 预测目标** |
| 触觉矩阵 $(12\times 6)_{\times 5}$ | ⭐⭐⭐⭐ | **RL 核心观测 + 接触判断** |
| 角速度 $\dot{\phi}_t$ | ⭐⭐⭐ | RL 观测（需滤波） |
| 反馈力矩 $\tau_{fb}$ | ⭐⭐ | Actuator Model 输入特征（**非** reward/预测目标） |
| 温度 $T_{motor}$ | ⭐⭐⭐⭐ | Actuator Model 显式输入 |

---

## 八、 数据驱动鲁棒控制视角：从短真机轨迹到安全证书

> [!note] 教科书参考
> 本节连接 [[ControlTheory|带噪声数据的鲁棒镇定]]，基于 [[Books/Data-based linear systems and control theory.pdf]] Chapter 3.6-3.7 的数据一致集与 LMI 证书思想。

执行器模型的难点不是“能不能拟合一条轨迹”，而是：**在 CAN 抖动、温度漂移、丝杠摩擦和触觉噪声都存在时，短真机数据能否证明一个局部控制器对所有可能真实模型都安全**。

对 L25 手，可以在每个局部工况下定义近似线性状态：

$$
x_t=[\phi_t,\dot\phi_t,T_t,z_{\delta,t}],\quad u_t=a_t,
$$

其中 $z_{\delta,t}$ 是最近若干帧 CAN latency / 指间相位差的低维编码。短真机轨迹形成输入-状态数据矩阵：

$$
X_+ = A X_- + B U_- + W_-.
$$

这里 $W_-$ 不是“坏掉的数据”，而是把未建模物理显式纳入证书的噪声集合：

- **通信噪声**：CAN 仲裁与分帧触觉造成的相位不一致
- **电气漂移**：$K_t(T)$ 与 $R_s(T)$ 的温度依赖
- **传动非线性**：Stribeck 静摩擦、丝杠效率波动、连杆柔性
- **估计误差**：差分速度与触觉接触定位的噪声

若噪声集合满足 $W_-W_-^\top\preceq T\epsilon I$ 或更精细的各向异性 QMI，则可用 [[ControlTheory|Matrix S-lemma LMI]] 检查是否存在共同 Lyapunov 矩阵 $P\succ0$。这使 [[Idea-002-Latency-Aware-Actuator|Latency-Aware Actuator]] 的 “5 min real adaptation” 多了一层硬判据：

> [!important] 实验判据
> 适配后的 Actuator Model 不只报告预测 MSE，还应报告数据驱动 LMI 是否可行。若不可行，说明 scripted motion 没有充分激发执行器模式，或噪声界设得过窄；此时应优先补采高/低速、升温、过零 stick-slip 三类轨迹，而不是盲目加大网络容量。
