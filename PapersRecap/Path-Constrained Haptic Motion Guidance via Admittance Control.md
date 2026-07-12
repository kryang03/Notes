---
tags:
  - paper
  - haptic-guidance
  - admittance-control
  - human-robot-interaction
  - impedance-compliance
aliases:
  - Phase-Based Admittance Control
  - Path-Constrained Haptic Guidance
paper-year: 2025
read-date: 2026-02-02
venue: IEEE TRO 2025
paper-pdf: "[[Papers/Path-Constrained_Haptic_Motion_Guidance_via_Adaptive_Phase-Based_Admittance_Control.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[Dynamics]]"
  - "[[Optimization]]"
---

# Path-Constrained Haptic Motion Guidance via Adaptive Phase-Based Admittance Control

> [!abstract] 核心贡献
> 本文把传统导纳控制从 Cartesian 空间搬到**路径相位空间**：人施加 wrench 决定相位 $\phi(t)$ 的进退，机器人只执行 $x_d(\phi)$，因此 desired motion 天然落在预定义几何路径上；再用 human manipulability 调节导纳质量 $m_a$，并用 virtual energy tank 限制自适应带来的 passivity violation。

> [!tip] 与理论基础的关联
> - [[ControlTheory]] — 导纳控制、阻抗控制、passivity 与 energy tank：本文的核心是把外力 $\to$ 运动的导纳关系投影到相位变量。
> - [[Dynamics]] — Cartesian operational-space dynamics 与 impedance tracking：机器人本体仍靠 $M_C,C_C,K_C,D_C$ 闭环跟踪 $x_d(\phi)$。
> - [[Optimization]] — 预定义路径/虚拟约束可视为几何可行集，本文用 phase parametrization 替代在线约束优化。
>
> **核心技术**: phase-based admittance, path-constrained haptic guidance, manipulability-aware adaptation, passivity, virtual energy tank

## 0. 阅读定位与范本价值

这篇不是一篇“又一个可变导纳控制”的论文。它真正有价值的地方在于：把 HRI 中“人想控制速度/时机”和“机器人必须满足几何约束”这两个目标做了结构解耦。

传统 virtual fixture / virtual guide 往往用法向虚拟力把机器人推回路径，或用 virtual mechanism 把 setpoint 当作沿路径滑动的 massless particle。这些方法的问题是：phase 轨迹常常依赖机器人真实位姿和 motion controller 的跟踪误差，路径约束与运动响应被耦合在一起。本文的核心结构是：

$$
f_h \rightarrow f_s \rightarrow \phi(t) \rightarrow x_d(\phi) \rightarrow \text{impedance-controlled robot}
$$

也就是说，人并不直接决定 Cartesian 目标，而是只决定路径参数 $\phi$。只要 $x_d(\phi)$ 编码正确，desired trajectory 就不会离开路径；路径跟踪误差再由底层 impedance controller 处理。

这对知识库有两个价值：

1. 它补齐 impedance/compliance 簇的 HRI/虚拟约束分支：VICES/FACET 关注 robot learning 的柔顺动作空间，MCC/Data-Driven VIC 关注力/阻抗参数来源，本文关注**几何约束下的人机控制权分配**。
2. 它把 $m(s)$ 元控制家族从“刚度 $K(s)$”扩展到“导纳质量/响应性 $m_a(s)$”：不是只问当前该多软硬，还问当前人推一下应该让系统走多快。

## 1. 问题设定与动机

### 1.1 一句话核心

**机器人保证走哪条路径，人类通过力决定沿路径怎么走。**

### 1.2 直观隐喻

这像把工具装在一条“虚拟导轨”上。导轨决定几何路径，操作者的力只决定沿导轨前进、后退、快慢和停顿。区别是，这条导轨不是物理硬件，而是由 $x_d(\phi)$ 和 phase-domain admittance 生成的。

### 1.3 现有方法的局限

| 方法 | 基本思想 | 卡点 |
|------|----------|------|
| 普通 admittance control | $f_h \rightarrow x_d$，人推哪里机器人去哪 | 无法保证 $x_d$ 落在路径上 |
| virtual fixture | 对偏离路径方向施加虚拟力 | 路径保持依赖法向刚度，刚度低会偏，高会不舒服 |
| virtual mechanism | setpoint 是路径上的 massless particle，通过 spring-damper 与机器人耦合 | phase dynamics 与机器人位姿/跟踪误差耦合，无法独立调“人推一下走多快” |
| DMP + admittance | 用相位生成轨迹，再调速度 | 通常不是从 phase domain 推导 admittance，路径约束保证弱 |
| **本文** | wrench 投影到 path tangent，直接驱动 $\phi$ 的非线性导纳 | 依赖正确测量 guiding wrench，且路径必须预定义 |

### 1.4 Delta 分析

本文的 Delta 不是“用了 manipulability”或“用了 energy tank”，而是：

$$
\text{Cartesian admittance} \quad M\ddot{x}+D\dot{x}=f
\quad \Longrightarrow \quad
\text{phase admittance} \quad m_\phi\ddot{\phi}+d_\phi\dot{\phi}+c_\phi\dot{\phi}^2=f_s
$$

其中 $c_\phi\dot{\phi}^2$ 不是装饰项，而是为了让 phase-space law 在切向对齐时精确等价于熟悉的 Cartesian mass-damper relation：

$$
m_a\ddot{x}_d+d_a\dot{x}_d=f_h.
$$

这使参数调节仍然是物理可解释的 $m_a,d_a$，而不是难以理解的 $m_\phi,d_\phi,c_\phi$。

## 2. 核心方法与理论

### 2.1 变量来源追踪

枢纽：**路径约束由 $x_d(\phi)$ 保证，运动响应由 $\phi$ 的导纳动力学调节，稳定性由 $E_t$ 限制自适应注入能量。**

| 变量 | 类型/空间 | 来源阶段 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|----------------|----------|
| $q,\dot q$ | $\mathbb{R}^n$ | 机器人传感 | 关节状态 | 论文把主要推导放在 Cartesian 空间 |
| $x,\dot x,\ddot x$ | $\mathbb{R}^m$ | forward kinematics / dynamics | end-effector pose/velocity/acceleration | $m$ 可含平移+旋转，单位混合需权重 |
| $M_C(q),C_C(q,\dot q),f_g(q)$ | Cartesian dynamics | 模型计算 | operational-space inertia / Coriolis / gravity | 不是关节空间 $M(q)$；跟踪稳定性依赖底层 controller |
| $f_h$ | wrench | robot wrench sensing | 人/环境施加的交互力 | 最大陷阱：算法无法自动区分“人想推”与“环境碰撞” |
| $x_d(\phi)$ | path map | 预定义/示教/GP 编码 | phase 到路径 setpoint 的映射 | 路径必须已知；branching path 不自然 |
| $\phi\in[0,1]$ | scalar | phase generator 状态 | 路径进度 | 可 reset/saturate；不是时间，也不一定匀速 |
| $f_s=f_h^T\frac{dx_d}{d\phi}$ | scalar | wrench 投影 | 沿路径切向的 steering force | path tangent 尺度影响 $f_s$，所以需要 generalized admittance |
| $m_\phi,d_\phi,c_\phi$ | scalar/functions | 由 $m_a,d_a,x_d(\phi)$ 推出 | phase-space admittance 参数 | $c_\phi$ 来自曲率/非均匀编码，不是经验摩擦项 |
| $m_a,d_a$ | mass/damping | preset 或自适应 | 人可理解的导纳质量/阻尼 | $m_a$ 越小，同样力下相位走得越快 |
| $J_h(q_h),\Lambda(q_h)$ | human Jacobian / ellipsoid core | RealSense + OpenPose + arm model | 人体 manipulability 估计 | 实验只用肩/肘/腕三点，人体模型是简化的 |
| $l$ | scalar | manipulability projection | 当前路径方向上人体运动/施力可行性 | $l$ 大小的解释依赖 motion vs force ellipsoid 对偶 |
| $E_t,\mu$ | scalar | virtual tank | 限制 $m_a$ 变化率，防止注入无界能量 | tank 初值是设计问题，论文未给通用最优解 |

### 2.2 前置理论从零推导

#### 2.2.1 底层机器人仍是 impedance tracking

机器人 Cartesian dynamics 写作：

$$
M_C(q)\ddot{x}+C_C(q,\dot q)\dot{x}+f_g(q)=f_{in}+f_h.
$$

底层用带重力补偿的 impedance controller：

$$
f_{in}=K_C\tilde{x}+D_C\dot{\tilde{x}}+M_C(q)\ddot{x}_d+C_C(q,\dot q)\dot{x}_d+f_g(q),
$$

其中 $\tilde{x}=x_d-x$。代回可得闭环误差系统：

$$
M_C(q)\ddot{\tilde{x}}+C_C(q,\dot q)\dot{\tilde{x}}+D_C\dot{\tilde{x}}+K_C\tilde{x}+f_h=0.
$$

这说明本文并没有发明新的底层力控器；它的创新发生在上层 motion generator：如何产生 $x_d(t)$。

#### 2.2.2 路径约束来自 phase encoding

预定义路径被编码为：

$$
x_d=x_d(\phi), \qquad \phi\in[0,1].
$$

因此只要 $\phi$ 在合法区间内，desired setpoint 就在路径上。这个结构比“机器人偏了再拉回来”更干净：它从生成目标的一刻就不允许目标离开几何路径。

#### 2.2.3 人类力只取路径切向分量

人施加的 wrench $f_h$ 被投影到路径切向：

$$
f_s=f_h^T\frac{dx_d(\phi)}{d\phi}.
$$

若 $f_h$ 与路径切向同向，$f_s>0$，相位前进；反向则相位后退；法向分量不直接推进 phase。这就是“人决定路径进度，而不是改写路径几何”。

### 2.3 论文核心机制无跳步推导

#### 2.3.1 Phase-domain admittance

本文定义：

$$
m_\phi\ddot{\phi}+d_\phi\dot{\phi}+c_\phi\dot{\phi}^2=f_s.
$$

乍看像任意非线性二阶系统，但它来自一个明确目标：当人力沿路径切向时，希望 setpoint 运动满足普通 mass-damper admittance：

$$
m_a\ddot{x}_d+d_a\dot{x}_d=f_h.
$$

由 chain rule：

$$
\dot{x}_d=\frac{dx_d}{d\phi}\dot{\phi},
$$

$$
\ddot{x}_d=\frac{d^2x_d}{d\phi^2}\dot{\phi}^2+\frac{dx_d}{d\phi}\ddot{\phi}.
$$

将它们代入 $m_a\ddot{x}_d+d_a\dot{x}_d=f_h$，并两边右乘/投影到 $\frac{dx_d}{d\phi}$，得到：

$$
\left(m_a\frac{dx_d^T}{d\phi}\frac{dx_d}{d\phi}\right)\ddot{\phi}
+
\left(d_a\frac{dx_d^T}{d\phi}\frac{dx_d}{d\phi}\right)\dot{\phi}
+
\left(m_a\frac{d^2x_d^T}{d\phi^2}\frac{dx_d}{d\phi}\right)\dot{\phi}^2
=
f_h^T\frac{dx_d}{d\phi}.
$$

于是：

$$
m_\phi=m_a\frac{dx_d^T}{d\phi}\frac{dx_d}{d\phi},
$$

$$
d_\phi=d_a\frac{dx_d^T}{d\phi}\frac{dx_d}{d\phi},
$$

$$
c_\phi=m_a\frac{d^2x_d^T}{d\phi^2}\frac{dx_d}{d\phi}.
$$

这解释了 $c_\phi\dot{\phi}^2$ 的来源：它补偿 path encoding 的曲率和非均匀参数化，使 $m_a,d_a$ 仍然有“质量/阻尼”的直觉。

#### 2.3.2 Manipulability-aware adaptation

人体 arm Jacobian $J_h(q_h)$ 构造 manipulability ellipsoid：

$$
\Lambda(q_h)=J_h(q_h)\Upsilon J_h^T(q_h).
$$

令其特征向量/特征值为 $\nu_i,\lambda_i$，半径：

$$
r_i=\sqrt{\lambda_i}.
$$

路径方向单位向量：

$$
\nu(\phi)=\frac{dx_d(\phi)/d\phi}{\|dx_d(\phi)/d\phi\|}.
$$

将 ellipsoid 主轴投影到路径方向：

$$
l_i=|r_i\nu_i^T\nu(\phi)|,\qquad l=\sqrt{\sum_i l_i^2}.
$$

然后用 $l$ 线性调节导纳质量：

$$
m_a=
\begin{cases}
m_{a,\max}, & l\le r_{\min}\\
m_{a,\min}+(r_{\max}-l)\frac{\Delta m_a}{\Delta r}, & r_{\min}<l<r_{\max}\\
m_{a,\min}, & r_{\max}\le l.
\end{cases}
$$

直觉：当人体当前姿态沿该路径方向容易运动/施力时，减小 $m_a$，同样的力让 phase 走得更快；当姿态不适合快速运动时，增大 $m_a$，系统变“重”，避免把人拉进不舒服的状态。

#### 2.3.3 Passivity 与 energy tank

系统存储函数：

$$
S_{sys}=\frac12\dot{\tilde{x}}^T M_C(q)\dot{\tilde{x}}+\frac12\tilde{x}^TK_C\tilde{x}+\frac12m_\phi\dot{\phi}^2.
$$

推导后得到关键不等式：

$$
\dot{S}_{sys}\le \dot{x}^Tf_h+\frac12\dot{m}_a\dot{x}_d^T\dot{x}_d.
$$

第一项 $\dot{x}^Tf_h$ 对应人类输入能量，可假设人/被动环境的总能量有限。第二项才是本文必须处理的新问题：当 $m_a$ 自适应变化时，系统可能凭空注入能量，破坏 passivity。

引入 tank energy：

$$
\dot{E}_t=-\frac12\dot{m}_a^*\dot{x}_d^T\dot{x}_d.
$$

并限制：

$$
|\dot{m}_a^*|\le \mu.
$$

当 tank 能量不足时，$\mu\rightarrow 0$，自适应停止，$m_a$ 不再快速变化。总存储函数：

$$
S_{all}=S_{sys}+E_h+E_t\ge 0
$$

满足：

$$
\dot{S}_{all}\le 0.
$$

所以 energy tank 不是简单安全开关，而是把“自适应产生的额外能量”会计化：有预算时允许调参，没预算时冻结调参。

### 2.4 概念边界与符号陷阱

- **desired path vs actual path**：$x_d(\phi)$ 保证 desired setpoint 在路径上；真实机器人 $x$ 仍会有跟踪误差，取决于底层 impedance controller。
- **phase 不是时间**：$\phi$ 可快可慢、可停、可反向；非均匀编码会改变 $\frac{dx_d}{d\phi}$，必须用 $m_\phi,d_\phi,c_\phi$ 补偿。
- **$c_\phi\dot{\phi}^2$ 不是经验阻尼**：它来自 chain rule 中的 $\frac{d^2x_d}{d\phi^2}\dot{\phi}^2$。
- **wrench source ambiguity**：系统只看到 $f_h$，但无法知道它来自人、重力、摩擦还是碰撞。Experiment 3 的 pendulum 就会被当成“指导力”。
- **manipulability 是简化估计**：实验用 RealSense + OpenPose，只识别肩/肘/腕三点，对人体真实肌肉力容量只是近似。
- **tank initial energy 是超参**：论文展示 18 J vs 3 J 的差异，但没有给出普适初始化策略。
- **path must be predefined**：本文不是在线规划器。若任务需要实时决定路径拓扑，应接 MPC/planner，而不是只调 $\phi$。

### 2.5 信息流/算法机制（无代码）

1. 预先编码路径 $x_d(\phi)$。
2. 机器人测得交互 wrench $f_h$。
3. 将 $f_h$ 投影到路径切向，得到 $f_s$。
4. 根据当前路径导数和 generalized parameters $m_a,d_a$ 计算 $m_\phi,d_\phi,c_\phi$。
5. 用 phase-domain admittance 积分 $\phi$。
6. 由 $x_d(\phi)$ 生成 Cartesian setpoint。
7. 底层 impedance controller 跟踪 setpoint。
8. 若启用 adaptation，用人体 manipulability 更新 $m_a$；若 energy tank 快耗尽，则限制 $\dot{m}_a$。

## 3. 训练、数据与实验

### 3.1 实验设置

本文不是学习论文，没有 neural policy / RL training。实验用 7-DoF Franka robot，wrench 来源随实验不同：

| 实验 | 目的 | 关键设置 |
|------|------|----------|
| Exp. 1 | 验证 phase-based admittance 与 path encoding | 2.6 kg load 产生近似恒定力；70 cm vertical/arc path |
| Exp. 2 | 验证 manipulability-aware adaptation | RealSense D435 + OpenPose BODY-25；只用 shoulder/elbow/wrist 建 arm Jacobian；10 cm path |
| Exp. 3 | 验证 virtual energy tank | 人推机器人，路径上 $\phi=0.8$ 处碰撞 5 kg pendulum；比较 18 J vs 3 J initial tank |
| Exp. 4 | 对比 virtual mechanism | 20 cm horizontal path；5 N constant guiding wrench；比较 virtual mechanism 与 phase admittance |
| Exp. 5 | usability study | pyrography 木板烙画；20 participants，10 male/10 female，age 22-61，avg 31.3 |

底层 impedance controller 的典型参数：

$$
K_C=\mathrm{diag}(1000,1000,1000,50,50,50)
$$

阻尼取 critical damping。

### 3.2 关键结果

| 证据 | 观察 | 机制解释 |
|------|------|----------|
| Exp. 1.1 vs 1.3 | 非均匀 phase encoding 会让初期 $f_s$ 大、后期 $f_s$ 小，运动先快后慢 | $f_s=f_h^Tdx_d/d\phi$ 直接受 path derivative 尺度影响 |
| Exp. 1.4 | 用 $m_a=40$ kg, $d_a=160$ Ns/m 通过 (6)-(8) 推出 phase 参数后，非均匀编码也能得到接近 Exp. 1.1 的 desired motion | generalized admittance 消除了 phase distribution 对物理响应的污染 |
| Exp. 2.1 | $l\approx26$ cm，$m_a\approx50$ kg，平均路径方向力约 -5 N | 中等 manipulability -> 中等导纳质量 |
| Exp. 2.2 | near singular extended arm，$l\approx4$ cm，$m_a\approx76$ kg，10 cm path 约 1.8 s，平均力约 -7 N | 人体姿态不适合快速 motion，系统变重 |
| Exp. 2.3 | 相似手臂姿态但路径方向沿 ellipsoid 长轴，$l\approx67$ cm，$m_a\approx4$ kg，$\phi=1$ at $t\approx0.55$ s，平均力约 -1 N | 改变路径方向即可大幅改变 human capability |
| Exp. 3.1 | tank 初值 18 J，$m_a$ 可自由上升，collision 时 $E_{ka}=5.5$ J，pendulum 无法阻止 phase 到 1 | 高导纳质量积累虚拟动能，碰撞被系统“推过去” |
| Exp. 3.2 | tank 初值 3 J，$m_a^*$ 被限制，$E_{ka}=1.5$ J，collision 在 $\phi=0.9$ 处阻止/反转运动 | tank 限制自适应注能，保守但更安全 |
| Exp. 4 | virtual mechanism 降低 stiffness/damping 会产生 z 偏移；phase admittance 用 $m_a,d_a$ 降低到 10 kg/10 Ns/m 可加快路径运动且几何偏差仍小 | 本文把 guidance dynamics 与 motion tracking stiffness 解耦 |
| Exp. 5 | Mode 1 多数主观指标最高；低 crafts 经验组 comfort: mode1 4.7 vs mode3 3.4 vs mode2 2.7；低 robot experience 组 control: mode1 4.8 vs mode2 3.6 vs mode3 3.9；mode1 对 14/20 participants 最快 | path constraint + human speed control 同时降低难度和提高效率 |

### 3.3 Ablation 因果链

| 改动 | 结果 | 因果链 |
|------|------|--------|
| 不用 generalized parameters，只固定 $m_\phi,d_\phi,c_\phi$ | path encoding 改变时 desired motion profile 也改变 | $\frac{dx_d}{d\phi}$ 的尺度进入 $f_s$ 和 phase dynamics，非均匀编码污染物理响应 |
| virtual mechanism 降低 $K_{vm},D_{vm}$ | 路径 z 方向偏移 | virtual mechanism 的 guidance 与 tracking stiffness 绑定；降低“易推性”同时降低路径约束强度 |
| phase admittance 降低 $m_a,d_a$ | 同样 5 N 下路径 traversing 更快，偏差仍小 | 易推性由 phase dynamics 决定，路径保持仍由 $x_d(\phi)$ + motion controller 保证 |
| tank 初值 18 J -> 3 J | $m_a$ 自适应被限制，collision 能阻止 phase | tank 把 $m_a$ 变化率绑定到能量预算，降低虚拟动能 |
| 不区分 human/environment wrench | pendulum collision 被当作 guiding wrench | 系统只读 $f_h$，没有意图识别或环境动力学模型 |

### 3.4 工程约束与实验边界

- 该方法适合已有清晰路径的任务：切割、焊接、烙画、康复轨迹、teleoperation leader/follower constraint。
- 底层 controller 必须足够可靠，否则 desired path 在路径上不代表实际 robot pose 在路径上。
- 若接触环境会施加显著外力，必须加入 human wrench sensing、object dynamics 或 intent classifier，否则环境接触会污染 phase。
- Pyrography 用户研究主要是 usability 证据，不是严格的算法 benchmark；作者也指出未来可加入 curve accuracy / interaction power 等定量指标。

## 4. 核心洞见

### 4.1 论文真正的 insight

本文真正的 insight 是：

> **把几何约束写进 motion generator 的坐标选择里，而不是靠反馈力把偏差修回来。**

一旦 motion generator 的状态是 $\phi$ 而不是 $x$，路径约束就从控制目标变成表示结构。控制器不再问“如何让自由 Cartesian 目标不离开路径”，而是问“人希望路径参数怎么演化”。

### 4.2 为什么这个设计有效

它有效是因为把三个原本耦合的对象拆开了：

1. **几何**：$x_d(\phi)$ 决定路径。
2. **交互响应**：$m_a,d_a$ 决定人推一下 phase 走多快。
3. **稳定性预算**：$E_t$ 决定自适应能不能继续注入动能。

virtual mechanism 把 1 和 2 绑定在 spring-damper stiffness 上，所以“更容易推”和“更严格贴路径”会互相冲突。本文让 phase dynamics 管易推性，让底层 impedance 管路径 tracking，这就是解耦的价值。

### 4.3 什么时候会失效

- 路径不是单连通曲线、有分叉或需要在线拓扑选择时，单标量 $\phi$ 不够。
- 高速灵巧操作中，contact events 的外力可能远大于人机交互场景；若误当 guiding wrench，会让 phase 错误跳变。
- 若 $x_d(\phi)$ 的曲率很高且底层 bandwidth 不够，desired path 合法但 robot tracking 会滞后。
- 如果人体姿态估计 noisy，$m_a$ adaptation 会抖动；tank 只能限制能量，不能让错误的人体模型变正确。

## 5. 替代方案与理论局限

### 5.1 理论维度

| 方案 | 优点 | 局限 |
|------|------|------|
| 本文 phase admittance | 路径 setpoint 结构保证；响应参数物理可解释；可做 passivity proof | 依赖预定义一维路径；wrench source ambiguity |
| MPC/path-constrained optimization | 可处理约束、代价、障碍与在线重规划 | 计算更重；HRI 力反馈直觉弱 |
| CBF/path safety filter | 可把路径偏差作为 safety constraint | 更像部署过滤器，不直接解决人如何调 motion profile |
| DMP + admittance | 容易接示教轨迹 | 若 admittance 不在 phase domain，路径约束不天然保证 |

### 5.2 算法维度

本文的 adaptation policy 只是示例：用 manipulability 调 $m_a$。更一般地，$m_a$ 可以由 fatigue、confidence、vision quality、contact risk、task phase 等决定。关键不是具体的 $m_a(l)$，而是任何自适应都要重新检查 passivity-violating power。

### 5.3 工程/实验维度

实验已经覆盖机制验证和用户研究，但还缺：

- 多分支/复杂曲线路径下的在线 path selection。
- 强环境接触任务中 human wrench 与 environment wrench 的分离。
- 高速动态任务的 tracking lag 与 phase stability。
- 与 MPC/CBF/learning-based guide 的严格定量对比。

## 6. 对用户研究的启发

### 6.1 对灵巧手/转笔/PPO/DP/Sim-to-Real 的迁移

**转笔中的 phase variable**：snap -> rotate -> catch 可以被写成操作相位 $\phi_{manip}$。与其让 PPO/DP 在全状态空间自由探索，不如把一部分策略输出变成：

$$
\pi(o)\rightarrow (\dot{\phi}, m_a, K_{finger}, \Delta x_{finger})
$$

其中 $\phi$ 管任务进度，$K_{finger}$ 管柔顺度，$m_a$ 管“相位推进响应性”。这与 VICES 的 $K(s)$、FACET 的 $K_p(s)$、Data-Driven VIC 的 $K(\phi,v,\alpha)$ 是同一个 $m(s)$ 家族的不同维度。

**用于 imitation/RL bootstrapping**：如果有专家转笔轨迹，可以先拟合 contact schedule / object orientation path 为 $x_d(\phi)$ 或 $R_d(\phi)$，再让 RL 只学 phase correction 与局部 residual。这会把“生成完整动作”降维成“沿已知 manipulation manifold 调速和修正”。

**用于遥操作/数据采集**：人通过 haptic 或 GUI 控制 $\phi$，机器人/仿真系统保证接触几何路径，适合收集高质量 demonstration。比直接遥操作所有 DOF 更接近“人给任务语义，机器保低层约束”。

### 6.2 可验证实验建议

1. **phase-constrained PPO**：把转笔分为 snap/rotation/catch 的 one-dimensional phase，比较普通 PPO vs phase-conditioned PPO 的 sample efficiency 与 failure mode。
2. **wrench ambiguity diagnostic**：在仿真中注入非人类来源的 contact impulse，测试 phase generator 是否误推进；验证是否需要 intent classifier。
3. **tank budget sweep**：把 $E_t(0)$ 当成 safety/performance knob，扫其对 catch success、drop rate、contact force peak 的影响。
4. **manipulability to hand dexterity**：把 human manipulability 替换为 hand-object grasp manipulability，用 $l$ 调节 finger impedance 或 phase speed。

### 6.3 不应过度外推的点

- 本文不是学习方法，不能替代 world model 或 policy learning。
- 它处理的是“给定路径下如何人机引导”，不是“路径怎么产生”。
- HRI 低速任务的 passivity 分析不能直接保证高速转笔稳定；转笔中物体飞行动力学和间歇接触会引入更强 hybrid dynamics。

## 7. 与知识体系的联系

### 与 [[ControlTheory]] 的联系

本文是导纳控制的一个结构化变体：普通导纳把 $f_h$ 映射到 Cartesian motion，本文把 $f_h$ 映射到 phase motion。passivity 分析和 energy tank 则把 adaptive admittance 的稳定性问题具体化：凡是在线改 $m_a,K,D$ 的方法，都要回答“参数变化是否注入能量”。

### 与 [[Dynamics]] 的联系

底层闭环依赖 operational-space dynamics：

$$
M_C(q)\ddot{\tilde{x}}+C_C(q,\dot q)\dot{\tilde{x}}+D_C\dot{\tilde{x}}+K_C\tilde{x}+f_h=0.
$$

这说明 phase generator 只是产生 $x_d$；实际是否贴路径仍取决于 robot dynamics compensation、Cartesian stiffness/damping、wrench sensing 和 bandwidth。

### 与 [[Optimization]] 的联系

本文用 path parametrization 避免在线求解 constrained optimization。若路径固定且一维，$\phi$ 是极其便宜的约束坐标；若路径需要在线选择、避障或多目标权衡，就应升级到 MPC/trajectory optimization/CBF 类方法。

### impedance/compliance 簇综述：几何约束导纳 + $m_a(s)$ 元控制

> [!note] impedance 簇收官定位
> 本文补齐 impedance/compliance 簇的**HRI 几何约束**分支。簇内现在可按两条谱理解：
>
> **学习程度谱**：零学习物理模型（[[Minimalist Compliance Control|MCC]]）→ 凸优化辨识（[[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking|Data-Driven VIC]]）→ RL 学阻抗/参考（[[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks|VICES]] / [[FACET - Force-Adaptive Control via Impedance Reference Tracking|FACET]]）→ HRI 在线调导纳质量（本文）。
>
> **阻抗/导纳进入系统的位置谱**：action space（VICES）→ reference model（FACET）→ physical estimator（MCC）→ phase generator（本文）→ demonstration residual（[[Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation|Residual LfD]]）。
>
> **新 insight**：阻抗簇不只是在问“刚度 $K$ 怎么来”，还在问“交互响应性 $m_a$ 怎么来”。VICES/FACET/Data-Driven VIC 的核心元控制量是 $K(s)$ 或 $K(\phi)$，本文的核心元控制量是 $m_a(s)$。二者合起来形成柔顺控制的两维旋钮：**多硬/多软** 与 **人推一下系统走多快**。这把 $m(s)$ 家族扩展为：
> 控制频率 $\Delta t(s)$ · 平滑度 $K(x)$ · 探索 $\lambda_{max}(s)$ · 安全裕度 · 阻抗刚度 $K(s)$ · **导纳质量 $m_a(s)$**。

> [!note] Foundation 精确锚点 · 簇内 Delta · 暗线（补 §7 收官 note）
> **Foundation 精确锚点**：$f_h\to\phi$ 的导纳映射 = [[ControlTheory#3.3 导纳控制与阻抗/导纳因果性校准|ControlTheory §3.3]]（导纳 = 力→运动，与阻抗因果相反）；底层机器人仍是阻抗 tracking = [[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|ControlTheory §3.2]]；统一视角 [[ControlTheory#3.5 统一阻抗-导纳架构|ControlTheory §3.5]]；energy tank / passivity 证明 = [[ControlTheory#10.4 被动性与"价值即 Lyapunov"|ControlTheory §10.4]] 的被动性理论；operational-space 闭环 = [[Dynamics#7.3 操作空间动力学 (Khatib)：在任务空间直接设计|Dynamics §7.3]]。
>
> **簇内 Delta 补链**：vs [[FACET - Force-Adaptive Control via Impedance Reference Tracking|FACET]]——两者都在上层生成参考轨迹让底层阻抗跟踪，但 FACET 的参考=虚拟阻抗模型（RL 学参数）、本文的参考=路径 $x_d(\phi)$（人力驱动相位）；FACET 管"多软硬 $K_p$"、本文管"沿路径走多快 $m_a$"。vs [[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking|Data-Driven VIC]]：两者都以相位 $\phi$ 为控制自变量，一个调阻抗、一个调 setpoint。
>
> **暗线 · 反驱动性**：导纳控制要求机器人能顺人力而动——底层需**可反驱**执行器或高质量力反馈，否则 $\tilde{x}$ tracking 会把人力当扰动硬顶（[[Actuation#10.2 力矩反馈为何"能当输入、不能当目标"|Actuation §10.2]]）。

## References

- Shahriari, E., Svarny, P., Baradaran Birjandi, S. A., Hoffmann, M., & Haddadin, S. (2025). *Path-Constrained Haptic Motion Guidance via Adaptive Phase-Based Admittance Control*. IEEE Transactions on Robotics, 41, 1039-1060.
