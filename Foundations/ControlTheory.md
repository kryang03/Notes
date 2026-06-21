---
tags:
    - foundation
    - control-theory
    - dexterous-manipulation
aliases:
    - 控制理论
    - Control
    - 控制系统
    - 传递函数
    - Transfer Function
    - 状态空间
    - State Space
    - Bode Plot
    - 阻抗控制
    - Impedance Control
created: 2026-01-31
related:
    - "[[Dynamics]]"
    - "[[Optimization]]"
    - "[[ContactMechanics]]"
    - "[[SignalProcessing]]"
    - "[[ReinforcementLearning]]"
    - "[[EmbodiedAI]]"
---

# 灵巧操作控制理论：从负反馈到接触安全闭环

# Control Theory for Dexterous Manipulation: From Negative Feedback to Contact-Safe Closed Loops

> [!tip] 相关领域
> - [[Dynamics]] — 动力学方程是控制律的设计对象；操作空间动力学共用一套 $\Lambda/\bar J$
> - [[ContactMechanics]] — 接触力学定义了力控的约束（摩擦锥、力闭合）；Montana 决定滚动
> - [[Optimization]] — MPC/轨迹优化是现代控制的核心工具；LQR↔iLQR↔QP
> - [[SignalProcessing]] — 状态估计（KF/EKF/PF）与频域分析是控制的感知前端
> - [[ReinforcementLearning]] — 数据驱动控制是 RL 的"控制论镜像"：价值即 Lyapunov、PE 即探索充分性
> - [[EmbodiedAI]] — 分层 VLA 中低层控制器的设计
>
> **贯穿母题**：**把一根销轴插进孔里 (peg-in-hole insertion)**。这一个接触丰富控制的"果蝇"任务，把控制理论六层大厦逐层点亮：硬插会卡死/崩坏→刚度悖论与柔顺；沿孔轴找正→力/位混合；销头在倒角上滚→Montana；摩擦未知→鲁棒/自适应；接近-触碰-滑入-到底→接触状态机；要不要插得更激进→接触隐式 MPC 与 CBF 安全滤波；凭什么保证不发散→Lyapunov 统一证书。

## 0. 母题与理论大厦构建路线：从负反馈到接触安全闭环

> [!abstract] 为什么用"插销入孔"做母题？
> Peg-in-hole 是接触丰富控制的经典基准，因为它把"自由空间运动"与"受约束接触"挤进同一个任务：
> - 销轴还没碰到孔时是自由运动（位置控制就够）；一旦销头蹭到孔口倒角，高刚度位置控制会把微小对不准放大成巨大侧向力→**卡死或崩坏**（刚度悖论）；
> - 正确做法是**插入方向软、找正方向跟踪**（力/位混合 + 阻抗）；
> - 销头在倒角上**滚动/滑动**触发 Montana 几何与摩擦锥；
> - 孔的位置、摩擦、间隙都**未知**→鲁棒/自适应/数据驱动；
> - 整个过程是 free→contact→stick→slide→inserted 的**模式切换**，每次切换都不能有力的跳变（bumpless）；
> - 凭什么保证这个接触闭环不振荡、不发散？**Lyapunov/被动性证书**。
>
> 全讲每引入一个控制范式，都回到这根销轴：**"这一步该跟位置还是跟力？这个控制器在接触刚性孔壁时会不会自激振荡？"**

控制理论在灵巧操作中的主线，是把"希望系统去哪里"转成"在扰动、延迟、接触非线性下仍能稳定到达"的闭环机制。六层大厦，每层回答一个更尖锐的问题：

| 层级 | 关键问题 | 理论工具 | 插销母题的映射 | 讲稿位置 |
|:--|:--|:--|:--|:--|
| **系统描述层** | 输入/状态/输出如何作用？ | 传递函数、状态空间、可控/可观 | 电机→关节→接触→物体状态的接口 | §1–§2 |
| **稳定性层** | 闭环会发散或振荡吗？ | 极点、Lyapunov、passivity、ISS | 防接触高刚度自激振荡 | §10 |
| **频域层** | 带宽、相位裕度、延迟的影响？ | Bode、Nyquist、root locus | CAN/SDK/MCU 延迟吃掉相位裕度 | §1 |
| **柔顺层** | 接触时跟位置还是跟力？ | 阻抗、导纳、力/位混合 | 在推/找正/滑入间切换因果性 | §3–§5 |
| **优化层** | 多目标多约束如何实时处理？ | LQR、MPC、OSF、QP、CBF | 同时管任务/零空间/限位/接触力/安全 | §4,§8,§9,§11 |
| **数据层** | 模型不准时如何仍给证书？ | Willems 引理、informativity、自适应 | 用短真机轨迹建稳定性/可控性证据 | §12–§13 |

> [!important] Foundation 级判断标准
> 任何控制方法都必须说明三件事：**误差如何被测量、输入如何被限制、闭环稳定性或安全性由什么机制保证。**

> [!note] 本讲在知识图谱中的位置
> ```
> [[Dynamics]] ──动力学方程/Λ,J̄──> 【控制对象】       【柔顺层】──阻抗/熵──> [[ReinforcementLearning|SAC]]
> [[ContactMechanics]] ──摩擦锥/力闭合──> 【力控约束】     【稳定性层 Lyapunov】──价值即 Lyapunov──> [[ReinforcementLearning|Safe RL]]
> [[SignalProcessing]] ──KF/EKF/相位裕度──> 【感知前端】     【优化层 MPC/LQR】──iLQR/QP──> [[Optimization]]
>                                                          【数据层 Willems/PE】──informativity──> [[ReinforcementLearning|数据驱动 RL]]
> ```

---

## 1. 古典控制最小语法：后续一切的前置语言

> [!tip] 本节四拍
> **直觉**（控制的最小定义：选输入使未来状态趋向期望）→ **推导**（三视角→阶次→极点→频域→PID→状态空间→离散延迟）→ **对比**（开环 vs 闭环、传递函数 vs 状态空间）→ **联系**（这是 §3 阻抗、§10 稳定性、§11 LQR 的共同语言，与 [[SignalProcessing#1. 从波形到状态：信号处理的系统骨架|信号处理基础]]对接）。

> [!note] 入门直觉
> 控制系统的最小定义：**选择输入，使系统未来状态趋向期望状态。** 同一件事出现在开关电源调压、机械隔振、机器人 PID、飞机颤振抑制中。**开环**：输入不依赖输出（固定油门），环境变化直接造成漂移；**闭环（负反馈）**：传感器测输出、与参考比较得误差、控制器调输入——这正是 [[SignalProcessing|状态估计]]、[[Dynamics|动力学]]、[[Optimization|控制优化]]汇合的接口。**阻尼直觉**：手指按住振动的酒杯让声响更快消失，因为你改变了能量耗散路径——阻抗控制本质上就是在设计"该吸收/反弹多少能量"。

### 1.1 三种等价视角与系统阶次

| 视角 | 形式 | 擅长回答 |
|:--|:--|:--|
| 微分方程 | $a_n y^{(n)}+\cdots+a_0y=b_mu^{(m)}+\cdots+b_0u$ | 真实动力学如何演化 |
| 传递函数 | $G(s)=Y(s)/U(s)$ | 输入某频率/阶跃后输出如何变 |
| 状态空间 | $\dot x=Ax+Bu,\ y=Cx+Du$ | 内部状态、可控/可观、MIMO |

约去公因子后，分母阶数 $n$ 是**系统阶次**＝最小状态维度（直觉：阶次越高，要记住的内部变量越多）。

| 阶次 | 形式 | 插销/灵巧操作例子 |
|:--|:--|:--|
| 1 阶 | $G=\frac{K}{\tau s+1}$，$y_{step}=K(1-e^{-t/\tau})$ | 电流环、热漂移、低通滤波 |
| 2 阶 | $G=\frac{\omega_n^2}{s^2+2\zeta\omega_ns+\omega_n^2}$ | 关节伺服、弹簧-阻尼、**阻抗控制** |

二阶系统的阻尼比 $\zeta$：$0<\zeta<1$ 欠阻尼（快但接触易反弹）、$\zeta=1$ 临界（不振荡最快）、$\zeta>1$ 过阻尼（稳但慢）。质量-弹簧-阻尼 $M\ddot x+D\dot x+Kx=F\Rightarrow\frac{X}{F}=\frac{1}{Ms^2+Ds+K}$——**这正是 §3.2 阻抗控制的数学原型：调 $M,D,K$ 就是在调闭环二阶系统的自然频率与阻尼。**

### 1.2 极点、零点与稳定性

$G(s)=K\frac{\prod(s-z_i)}{\prod(s-p_j)}$：极点（分母根）决定自然响应，零点（分子根）塑形输入。连续 LTI 稳定 ⟺ 所有极点在左半平面 $\mathrm{Re}(p_j)<0$；离散系统 ⟺ 所有极点在单位圆内 $|z_j|<1$。

> [!warning] 插销母题里的危险极点
> 高刚度 PD + 刚性孔壁接触，会把闭环极点推向高频。若执行器/传动柔性/采样延迟未建模，真实系统会出现未预测的振荡——销轴在孔口"嗡嗡"自激。这就是 §3.1 刚度悖论的古典控制解释。

### 1.3 频率响应：Bode、相位裕度与带宽

$G(j\omega)=|G(j\omega)|e^{j\phi(\omega)}$。**Bode 图**画幅频/相频随频率变化，回答两个关键问题：

| 指标 | 含义 | 对机器人的影响 |
|:--|:--|:--|
| 增益裕度 | 增益还能放大多少才失稳 | $K_p$ 调到何处会振荡 |
| 相位裕度 | 还能承受多少额外延迟 | 传感/通信/滤波延迟是否危险 |
| 带宽 | 能响应多快的扰动 | 高频滑移能否被闭环抑制 |

这与 [[SignalProcessing#1. 从波形到状态：信号处理的系统骨架|傅里叶变换]]是同一套数学：信号处理关心"频率成分是什么"，控制理论关心"系统对这些频率成分做什么"。

### 1.4 PID、灵敏度与状态空间

PID $C(s)=K_p+\frac{K_i}{s}+K_ds$（微分项常加低通防噪声放大）。单位负反馈闭环：互补灵敏度 $T=\frac{CG}{1+CG}$（参考→输出）、灵敏度 $S=\frac{1}{1+CG}$（扰动/模型误差→输出），$S+T=1$ 是控制的基本权衡。

| PID 项 | 作用 | 风险 |
|:--|:--|:--|
| $K_p$ | 提刚度、减误差 | 过大→超调/接触冲击 |
| $K_i$ | 消稳态误差 | 积分饱和、接触蓄能 |
| $K_d$ | 增阻尼 | 放大噪声，需滤波 |

**状态空间**（MIMO/高阶/内部状态重要时更合适）：可控性 $\mathrm{rank}[B\ AB\ \cdots\ A^{n-1}B]=n$（输入能否移动所有状态）；可观性 $\mathrm{rank}[C;CA;\cdots;CA^{n-1}]=n$（传感器能否恢复所有状态）。LQR 依赖可镇定、Kalman 依赖可检测，二者经**分离原理**合成 LQG——这也是 [[SignalProcessing#5.2 演进脉络：KF → EKF → UKF → PF → 因子图|KF/EKF/PF]]必须进 SignalProcessing 的原因。

> [!warning] 离散化与延迟：相位裕度预算
> 数字控制器经零阶保持采样 $A_d=e^{AT_s}$；单位延迟 $z^{-1}$ 在频域是相位滞后 $e^{-j\omega T_d}$——**频率越高，同样延迟吃掉越多相位裕度**。低频看似稳定的控制器，在高频接触切换或通信延迟下可能失稳。CAN 延迟、触觉帧率、动作保持时间，都应理解为闭环相位裕度预算的一部分。

> [!tip] DNPM 解释
> [[Dynamic Non-Prehensile Manipulation|DNPM]] 中策略输出 $q_{target}$ 后由固定 $K_p,K_d$ 的 PD 转力矩——策略无法改变闭环极点，故难以同时满足 snap 相的高带宽与 contact 相的顺应性。这正是相位自适应阻抗的控制理论动机（§3.4）。

---

## 2. 运动学与静力学对偶：灵巧操作的两个核心矩阵

> [!tip] 本节四拍
> **直觉**（多指协调要同时管"怎么动"与"怎么使力"）→ **推导**（虚功原理→对偶性）→ **对比**（手雅可比 $J_h$ vs 抓取矩阵 $G$）→ **联系**（与 [[ContactMechanics#2.3 接触雅可比与对偶性：连接关节空间|接触雅可比]]、[[Dynamics#8.1 腱网络运动学：耦合矩阵 $P$|腱耦合矩阵 P]]同构）。

### 2.1 虚功原理与对偶性

机器人力学最深刻的洞察之一：**力空间与运动空间对偶**。源于虚功原理（静平衡时虚功之和为零）。数学表现为雅可比转置关系：**若 $A$ 把速度从空间 $X$ 映到 $Y$（$v_y=Av_x$），则 $A^T$ 必把力从 $Y$ 映回 $X$（$f_x=A^Tf_y$）。** 这一句是理解 $J_h$ 与 $G$ 的钥匙。

### 2.2 手雅可比 $J_h$：从关节到接触

$J_h$ 把关节速度映到指尖接触速度 $v_c=J_h\dot q$；其转置把接触力映回关节力矩 $\tau=J_h^Tf_c$。$J_h$ 奇异（秩亏）意味着某方向上失去施力或运动能力，故规划常最大化可操作度 $\sqrt{\det(J_hJ_h^T)}$ 远离奇异（与 [[Dynamics#8.3 冗余、自运动与可操作度|可操作度椭球]]同源）。

### 2.3 抓取矩阵 $G$：从接触到物体

$G$ 把接触力合成为物体 wrench $F_o=Gf_c$；其转置描述约束一致性 $v_c=G^Tv_o$。

> [!important] 一张表记住两个矩阵的对偶
> | 矩阵 | 正向映射 | 转置映射 | 物理本质 |
> |:--|:--|:--|:--|
> | **手雅可比 $J_h$** | 关节速度→接触速度 | 接触力→关节力矩 | 机构传动特性 |
> | **抓取矩阵 $G$** | 接触力→物体力 | 物体速度→接触速度 | 物体几何约束 |
>
> $v_c=G^Tv_o$ 的物理含义常被忽视——它定义了**约束一致性**：物体动起来，接触点必须有 $G^Tv_o$ 的速度，否则就发生滑移或形变。$G$ 的严格定义、力闭合、内力见 [[ContactMechanics#3. 接触静力学：能否夹稳这颗弹珠|ContactMechanics §3]]。

```cpp
// 空间抓取矩阵构建（硬指：传 3 力、0 力矩）。Eigen。
MatrixXd partialGraspMatrix(const Vector3d& contact, const Vector3d& com) {
    Vector3d r = contact - com;               // COM→接触点
    MatrixXd Gi(6, 3);
    Gi.block<3,3>(0,0) = Matrix3d::Identity(); // 力部分：直接平移
    Gi.block<3,3>(3,0) = skew(r);              // 力矩部分：r × F
    return Gi;
}
// 两指对置时检查 rank(G)：< 6 即无法抵抗所有扰动（非力闭合）
```

---

## 3. 柔顺层：从刚性位置控制到顺应交互

> [!tip] 本节四拍
> **直觉**（硬插销轴会卡死/崩坏——位置控制在接触中致命）→ **推导**（刚度悖论→计算力矩→阻抗/导纳因果性）→ **对比**（阻抗 vs 导纳 vs 学习型变阻抗）→ **联系**（阻抗↔[[Dynamics#7.3 操作空间动力学 (Khatib)：在任务空间直接设计|操作空间]]、↔[[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|SAC 熵即柔顺]]）。

### 3.1 刚度悖论与计算力矩控制的诱惑

经典 PID 位置控制 $\tau=K_pe+K_d\dot e+\tau_g$ 为了高精度跟踪会把 $K_p$ 设得极高。自由空间有效，但接触时引发**刚度悖论**：

> [!warning] 刚度悖论（插销母题的核心失败模式）
> 环境位置模型永远有误差 $\delta x$。当销轴试图移动到一个被孔壁占据的位置，高增益控制器把它当位置误差，输出巨力 $F=K_p\delta x$ 试图消除——力迅速饱和，卡死或崩坏。更糟：环境刚度 $K_e$ 使闭环总刚度 $K_{total}\approx K_p+K_e$ 极大，自然频率升高，激发未建模高频动力学（齿轮箱柔性），引发**接触不稳定（self-excited 振荡）**。

**计算力矩控制 (CTC)** 是一个改进：用全状态反馈精确消去非线性，$\tau=M(q)[\ddot q_d-K_v\dot e-K_pe]+C\dot q+N$，代入后误差动力学化为纯线性 $\ddot e+K_v\dot e+K_pe=0$（Murray Prop 4.8，对称正定 $K_p,K_v$ 保证指数跟踪）。但 CTC 仍不适合灵巧操作：

1. **模型依赖**：需精确 $M,C,N$，接触切换使模型误差严重；
2. **消除而非调节交互**：CTC 把 $F_{ext}$ 当扰动消除，但灵巧操作里接触力是任务核心，要**调节**而非消除；
3. **PD 的本质局限**：Murray 明言"PD 永远无法精确跟踪非平凡轨迹"——固定 $K_p,K_d$ 无法表达动态任务所需的**时变刚度**。

> [!warning] 实证：$K_p$ 对成功率的极端敏感（DNPM Exp2, 2026-02）
> TP 任务的 $K_p$ 网格搜索显示**最优区间仅 3.5–8.5**（~2.4× 范围），区间外急剧衰退：过低力矩不足、过高接触相无法顺从致笔弹飞。这窄区间证实了刚度悖论的严重性——固定 $K_p$ 无法同时满足运动相与接触相，正是相位自适应阻抗（§3.4）的动机。

**演进逻辑**：PID 接触失稳 → CTC 消非线性但忽略交互 → 需要能**主动调节机器人-环境交互动态关系**的范式 → **阻抗控制**。

---

### 3.2 阻抗控制：调节力与运动的动态关系

Hogan 的阻抗控制不直接控力或位置，而是控制二者的**动态关系**——把机器人"伪装"成一个质量-弹簧-阻尼系统：

$$M_d(\ddot x-\ddot x_d)+B_d(\dot x-\dot x_d)+K_d(x-x_d)=F_{ext}.$$

> [!important] 因果性洞察：为什么阻抗适合刚性环境
> **阻抗因果性**：输入位移（环境推机器人）、输出力（机器人回弹），$F=Z(x)$。刚性环境本身表现为**导纳**（输入力、输出位移）。两个系统耦合应当是"阻抗 + 导纳"，而非"阻抗 + 阻抗"——这就是阻抗控制与刚性孔壁交互稳定的根本原因。插销母题里：让销轴在插入方向表现为低刚度阻抗，孔壁的几何约束（导纳）与之匹配，不会硬碰硬。

> [!note] 被动性稳定证明（阻抗为何天然稳定）
> 取能量储存函数 $V=\frac12\tilde x^TK_d\tilde x+\frac12\dot{\tilde x}^TM_d\dot{\tilde x}$（$\tilde x=x-x_d$）。求导并代入目标动力学：
> $$\dot V=\dot{\tilde x}^T(F_{ext}-B_d\dot{\tilde x})=\dot{\tilde x}^TF_{ext}-\dot{\tilde x}^TB_d\dot{\tilde x}.$$
> 无外力时 $\dot V=-\dot{\tilde x}^TB_d\dot{\tilde x}\le0$（负半定），由 LaSalle（§10.2）渐近稳定到 $\tilde x=0$。**阻尼 $B_d$ 耗散能量**——系统像漏气气球必回平衡。这是阻抗在接触任务中天然稳定的数学保证，也是 §10 被动性理论的具体实例。

### 3.3 导纳控制与阻抗/导纳因果性校准

**导纳控制**反过来：输入力（力传感器测）、输出位移，$x=Y(F)$。先按测得的力算出"应处的位置" $x_{ref}$（$M_d\ddot x_{ref}+B_d\dot x_{ref}+K_dx_{ref}=F_{meas}$），再交给底层刚性位置环执行。

> [!important] 阻抗 vs 导纳：选型取决于底层硬件
> | 特性 | 阻抗 | 导纳 |
> |:--|:--|:--|
> | 底层环 | 力矩控制 | 位置/速度控制 |
> | 硬件 | 直驱/准直驱、低摩擦（Franka, iiwa） | 通用工业臂、高减速比（UR, Fanuc） |
> | 适应环境 | 刚性环境 | 自由空间/柔性环境 |
> | 风险 | 自由空间精度受摩擦影响 | **接触刚性表面易"锤击"失稳** |
>
> 导纳的最大风险：环境很硬时极小位移→巨大力变化，若 $M_d,B_d$ 不当，力突变使 $x_{ref}$ 剧烈波动，刚性位置环忠实执行→像锤子反复敲击。

> [!tip] 把"学习型阻抗"看清楚：很多其实是导纳
> 高减速比/丝杠/商用伺服更易稳定执行位置目标而非透明力矩，故许多"学习型阻抗"工程上实为**导纳架构**：上层据力生成退让轨迹、下层 PD 跟踪。两个例子：
> - **Unified Policy**：$x^{target}=x^{cmd}+\frac{F^{ext}+(F^{cmd}-F^{react})}{K}$——本质是基于显式力估计器的**准静态导纳**（导纳方程令 $M,D\to0$）。
> - **[[FACET - Force-Adaptive Control via Impedance Reference Tracking|FACET]]**：参考模型 $m\ddot x_{ref}=K_p(x_{des}-x_{ref})+K_d(\dot x_{des}-\dot x_{ref})+f_{ext}$ 等价于**动态导纳**；创新在于让 RL 跟踪虚拟质量-弹簧-阻尼积分出的 $x_{ref}(t)$。
>
> **对灵巧手的启发**：若硬件是空心杯电机+丝杠+连杆耦合，直接做纯力矩阻抗会暴露全部 Actuator-to-Rigid gap；更稳健的是导纳式分层（上层学力/触觉→参考运动，下层保留位置伺服），再用 actuator model 补延迟/温漂/摩擦/背隙。

### 3.4 学习型变阻抗：RL × 阻抗的桥

固定阻抗参数无法适应任务变化。三条学习路线：

| 方法 | RL 输出 | 关键思想 |
|:--|:--|:--|
| **[[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks\|VICES]]** | $(\Delta x, K_{diag})$ 直接作阻抗参数 | 任务学习与底层动力学补偿**解耦**；低刚度自然限制接触力；"软/硬"语义可跨机器人迁移 |
| **[[FACET - Force-Adaptive Control via Impedance Reference Tracking\|FACET]]** | $(x_{des},K_p,K_d)$ 作参考模型输入 | 跟踪**动态参考轨迹**而非静态平衡点；通过参考模型主动响应 $f_{ext}$；碰撞冲击降 80% |
| **数据驱动阻抗辨识（[[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking\|Prosthesis VI]]）** | — | 固定平衡角时力矩对 $K,B$ **线性**→两步凸优化全局最优 |

> [!tip] 插销母题的相位自适应阻抗
> peg-in-hole 的理想阻抗随相位变化：**接近相**高刚度（精确定位孔口）→**触碰/找正相**插入方向低刚度（顺应倒角）→**滑入相**侧向低、轴向中→**到底相**全向中高刚度（确认就位）。这正是"为每个手指/相位定义独立阻抗参考模型"的用武之地，也呼应 [[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|SAC 的熵即虚拟柔顺]]——**熵正则在数学上扮演阻抗的角色**。

> [!tip] 多速率控制（[[Reinforcement Learning for Control with Multiple Frequencies|AP-AC]]）
> 不同变量有不同自然时间尺度：关节力矩 ~1kHz、抓手开合 ~10Hz、运动规划 ~1Hz。标准 RL 假设单一频率→强制高频→轨迹过长→探索低效。AP-AC 用周期性非平稳策略 $\pi(a\mid s,t)=\prod_j\pi_j(a^j\mid s,t\bmod T_j)$ 让每个变量按自己节奏更新。插销母题：末端位置中频、手指高频、抓握力低频。

### 3.5 统一阻抗-导纳架构

引入占空比 $\alpha\in[0,1]$ 在两种因果性间连续插值：接触刚性环境倾向阻抗（$\alpha\to1$，用力矩控制的自然顺应）；自由/柔性环境倾向导纳（$\alpha\to0$，用位置控制的高精度）。关键在切换瞬间保证状态连续（通过状态映射矩阵防控制量跳变）——这预告了 §7 接触状态机的 **bumpless transfer**。

---

## 4. 操作空间公式化 (OSF)：在任务空间直接设计控制

> [!tip] 本节四拍
> **直觉**（任务定义在销轴尖的笛卡尔空间，不在关节空间）→ **推导**（把动力学投影到任务空间）→ **对比**（动力学一致逆 $\bar J$ vs Moore-Penrose 伪逆）→ **联系**（与 [[Dynamics#7.3 操作空间动力学 (Khatib)：在任务空间直接设计|Dynamics §7.3]] 是同一 $\Lambda/\bar J$，此处看控制律设计）。

Khatib 的 OSF 是分水岭：不仅把运动学、更把**动力学**投影到任务空间，实现真正的动态解耦。任务空间动力学 $\Lambda(q)\ddot x+\mu\dot x+p=F_{op}$，其中：

- **操作空间惯量** $\Lambda(q)=(JM^{-1}J^T)^{-1}$——末端在各方向感受到的"等效质量"，奇异附近趋于无穷（无法在奇异方向产生加速度，回扣 [[Dynamics#7.1 拓扑突变与有效惯量|有效惯量]]）；
- 控制律 $\tau=J^TF_{op}+N^T\tau_{null}$。

> [!important] 动力学一致逆 $\bar J=M^{-1}J^T\Lambda$ 的深刻之处
> $\bar J$ 含 $M^{-1}$，分配任务时**自动惩罚大惯量关节**——想让销轴尖快速移动，算法倾向驱动轻量的手指/手腕而非沉重的肩部。零空间投影 $N=I-\bar JJ$ 保证 $\tau_{null}$ 产生的关节加速度映射回任务空间为零（**动态不干扰**，比运动学零空间的"速度为零"更强，$JM^{-1}N^T=0$）。任务优先级嵌套：
> ```
> 主任务（销轴尖轨迹）→零空间→次任务（避障/奇异回避/姿态优化）
> ```

```cpp
// OSF 核心：Λ, J̄, 零空间投影 N
MatrixXd Minv = M.inverse();
MatrixXd Lambda = (J * Minv * J.transpose()
                   + 1e-4 * MatrixXd::Identity(J.rows(), J.rows())).inverse(); // 奇异附近加阻尼
MatrixXd Jbar = Minv * J.transpose() * Lambda;        // 动力学一致逆
MatrixXd N = MatrixXd::Identity(n, n) - Jbar * J;     // 零空间投影；验证 ||J*N|| ≈ 0
```

---

## 5. 力/位混合控制：正交分解任务空间

> [!tip] 本节四拍
> **直觉**（插销时：插入方向控力、找正方向控位置）→ **推导**（选择矩阵正交分解）→ **对比**（理论优雅 vs 几何不一致的工程陷阱）→ **联系**（约束方向↔[[ContactMechanics#3. 接触静力学：能否夹稳这颗弹珠|力闭合]]、↔§6 Montana）。

任何任务可分解为正交的**位置控制子空间**与**力控制子空间**，由对角**选择矩阵** $S=\mathrm{diag}(s_1,\dots,s_6)$（$s_i\in\{0,1\}$）实现：$s_i=1$ 该方向被环境约束、控力；$s_i=0$ 自由运动、控位置。控制律 $\tau=J^T(Su_{force}+(I-S)u_{pos})$。

**插销母题**：孔轴 $Z$ 方向被约束→控插入力（$s_z=1$）；$X,Y$ 找正→控位置（$s_x=s_y=0$）。

> [!warning] 几何不一致：混合控制的工程陷阱
> Mason–Raibert 理论优雅，但若人为定义的 $S$ 坐标系与真实几何约束不对齐（孔倾斜 5°、法线估计有误），则：位置控制器在实际受限方向尝试运动→巨大冲突力；力控制器在实际自由方向施力→机器人意外飞出 (runaway)。现代解法：**自适应混合控制 / 并行力位控制 / 从演示学 $S$**——这把混合控制推向了 §12 自适应与 [[ReinforcementLearning|学习]]。

---

## 6. 接触非线性：Montana 接触运动学

> [!tip] 本节四拍
> **直觉**（销头在孔口倒角上滚动，接触点在两曲面上爬行）→ **推导**（接触方程的相对曲率）→ **对比**（纯滚动 vs 自旋奇异）→ **联系**（与 [[ContactMechanics#2.2 Montana 接触运动学方程|ContactMechanics §2.2]] 同一方程，此处看控制含义）。

接触状态 $q=(u_1,v_1,u_2,v_2,\psi)$（两曲面高斯坐标 + 接触角）。Montana 方程把**接触点演化速度**与**相对刚体速度**用一阶微分关系联系，核心是相对曲率 $(K_1+R_\psi K_2R_\psi^T)$：

$$\dot U\propto(K_{rel})^{-1}\omega_{rel}.$$

- 曲率差大（销头按在平面上）→滚动稳定、接触点移动适中；
- 曲率接近（球在同半径球窝里）→相对曲率趋零→接触点速度趋无穷，**自旋 (spinning)** 奇异，控制上极难，需规划层规避。

> [!important] 非完整约束的控制含义
> 纯滚动是经典**非完整约束**：接触点位置不能由滚动速度代数求得，依赖路径积分。后果——让销头从倒角点 A 滚到 B 而不滑，不能直线移动，需执行类似平行泊车的 **Lie bracket 机动**。这使基于 Montana 的灵巧操作规划成为极具挑战的非线性控制问题（与 [[Dynamics#4.1 Pfaffian 约束与完整/非完整之分|非完整 Pfaffian 约束]]同源）。

---

## 7. 鲁棒控制与接触状态机：对抗不确定、管理模式切换

> [!tip] 本节四拍
> **直觉**（孔的摩擦未知、接触在 free/stick/slide 间跳变）→ **推导**（滑模面强制收敛 + 状态机切换）→ **对比**（理想 SMC 抖振 vs 边界层平滑）→ **联系**（滑移检测↔[[SignalProcessing#4.1 早期滑移 (Incipient Slip) 检测|SignalProcessing]]、模式↔[[ReinforcementLearning#1.3 非光滑性的两副面孔：接触流形与混合动力学|RL 混合动力学]]）。

### 7.1 滑模控制 (SMC) 与抖振

CTC 一旦模型有误差 $\Delta M$ 性能迅速退化。SMC 把状态强行约束到**滑模面** $s=\dot e+\lambda e=0$（$\lambda>0$）上——一旦保持在 $s=0$，误差以指数 $\dot e=-\lambda e$ 收敛，**与具体动力学参数无关**。控制律 $u=u_{eq}+u_{dis}$：等效控制维持 $s=0$，切换控制 $u_{dis}=-k\,\mathrm{sgn}(s)$ 处理不确定性（只要 $k>$ 不确定性上界即稳）。

> [!warning] 抖振与边界层平滑
> 理想 SMC 需无限高频切换 $\mathrm{sgn}(s)$；实际数字系统中导致 $s=0$ 附近剧烈震荡（**抖振**），引起电机过热、齿轮磨损、激发高频共振。解法：在滑模面附近引入厚度 $\phi$ 的**边界层**，用连续饱和函数 $\mathrm{sat}(s/\phi)$ 替代硬切换。代价：边界层内变成高增益 PD，牺牲完美滑模不变性，误差收敛到 $\phi$ 界的小区域（工程可接受的妥协）。

### 7.2 接触状态机：混合系统视角

灵巧操作是典型**混合动力系统**，动力学在离散接触模式间切换：

| 状态 | 物理条件 | 动力学 |
|:--|:--|:--|
| Free（游离） | $\phi(q)>0$ | 自由运动、无接触力 |
| Contact（接触） | $\phi=0,\dot\phi=0$ | 法向约束激活 |
| Sticking（粘滞） | $\|f_t\|<\mu f_n$ | 摩擦锥内、静摩擦 |
| Sliding（滑移） | $\|f_t\|=\mu f_n$ | 切向力达摩擦锥边界 |
| Rolling（滚动） | $v_{contact}=0,\omega\ne0$ | 纯滚动无滑移 |

**插销状态机**：`Free →(接近)→ Contact →(增切向力)→ Sticking →(达摩擦极限)→ Sliding`，配合控制律切换（Free 用位置控制快速接近、Contact 用阻抗顺应、Sliding 用力控维持法向力）。

> [!warning] Bumpless Transfer（无扰切换）
> 模式切换瞬间必须保证控制量连续，否则产生冲击力致物体掉落或硬件损坏——这正是 §3.5 统一架构要解决的状态连续性问题。切换时刻的力跳变是灵巧操作真机事故的常见原因。

### 7.3 滑移检测与闭环防滑

> [!tip] 灵巧操作的核心安全约束
> 稳定夹持的本质是保持接触力始终在**摩擦锥内部**；滑移意味着接触约束即将失效。

**摩擦锥余量** $\gamma=\mu f_n-\|f_t\|$ 是滑移风险指标：$\gamma>0$ 安全、$\gamma\approx0$ 临界、$\gamma<0$ 已滑移。滑移概率 $P_{slip}=\sigma((\gamma_{th}-\gamma)/\tau)$。检测手段：视触觉（DIGIT/GelSight 标记点位移/光流）、6D 力矩（摩擦锥余量）、压阻/电容阵列（接触面积变化率）——这些信号处理细节见 [[SignalProcessing#4.1 早期滑移 (Incipient Slip) 检测|SignalProcessing §4.1]]。

**分层防滑架构**（三个时间尺度）：

```
高层 (RL/MPC, 10-50Hz): 接触状态机管理、操作相位规划、损失加接触保持项
  ↓ 目标力/位姿
低层 (阻抗/力控, 100-1000Hz): 维持 f_n ≥ f_n,min、限切向速度/加速度防冲击
  ↓ γ < γ_th 触发
反射 (Reflex, <1ms): 立即增法向力 Δf_n、短时提摩擦裕度、触发再抓
```

法向力自适应律 $\dot f_n^{ref}=K_{adapt}\max(0,\gamma_{th}-\gamma)$——检测到滑移风险上升即自适应增夹持力。不同材质（橡胶 $\mu\sim0.8$–1.2、硅胶-金属 $\mu\sim0.2$–0.4）需在线估计或查表设 $\gamma_{th}$。

---

## 8. 接触隐式模型预测控制 (Contact-Implicit MPC)

> [!tip] 本节四拍
> **直觉**（别预设"先食指后拇指"的接触序列，让优化器自己发现）→ **推导**（互补约束的非光滑性如何被平滑化）→ **对比**（预设接触序列 vs 接触隐式）→ **联系**（与 [[Optimization#5.3 阶段三：接触隐式轨迹优化 CITO（求解器自己发现）|Optimization CITO]]、[[ContactMechanics#5.1 互补条件与 LCP 的构建|LCP]]同源）。

接触动力学本质是**互补约束** $0\le\lambda\perp\phi(q)\ge0$（分离则无力、受力则贴合）。这非凸、非光滑——梯度在接触瞬间未定义或为零，使 iLQR/DDP 难以直接应用。

> [!important] Sigmoid 松弛：让优化器"感觉到"即将到来的接触
> 把严格互补 $\lambda\phi=0$ 松弛为 $\lambda\phi\le\epsilon$，或用 Sigmoid 构造连续可导接触力 $F_{contact}\approx\frac{F_{max}}{1+e^{-k\phi(q)}}$。这让优化器能计算**穿过接触事件的梯度**，自动规划最佳接触序列、无需人工指定何时接触——机器人能自主发现利用环境重定姿的策略（extrinsic dexterity）。这与 [[ContactMechanics#6.2 实现可微的三条路径|可微接触的零阶平滑]]、[[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|平滑化范式]]是同一思想。

**分层架构**（平衡长时程规划与高频响应）：高层 (10–50Hz) 跑接触隐式 MPC，基于简化模型规划未来几秒的接触序列；底层 (1kHz) 跑全身控制/阻抗，接收参考轨迹与接触力指令，用高频力反馈稳定当前接触、补偿高层忽略的高频动态。**这种"优化智能决策 + 反馈物理鲁棒"的分层，是当前灵巧操作控制的最高水平。**

---

## 9. 安全滤波：Control Barrier Function 与可达性

> [!tip] 本节四拍
> **直觉**（插销时绝不能用力过猛崩坏孔/销——要在不违反安全的前提下尽量激进）→ **推导**（CBF 把安全写成不变集约束）→ **对比**（CBF 保守可行集 vs 可达性最大可行集）→ **联系**（CBF↔§10 Lyapunov 对偶、↔[[ReinforcementLearning|Safe RL]]）。

> [!important] CBF = Lyapunov 在安全约束上的对偶
> 安全集 $\mathcal C=\{x:h(x)\ge0\}$。对控制仿射系统 $\dot x=f(x)+g(x)u$，$h$ 是 **CBF** 当 $\sup_u[L_fh+L_gh\cdot u]\ge-\alpha(h(x))$。给定名义控制器 $u^{nom}$，**CBF-QP 安全滤波**实时求解
> $$u^*=\arg\min_u\|u-u^{nom}\|^2\quad\text{s.t.}\quad L_fh+L_gh\cdot u\ge-\alpha(h(x)),$$
> 这是个可实时求解的 QP。
>
> | | Lyapunov (CLF) | Barrier (CBF) |
> |:--|:--|:--|
> | 保证 | 收敛到目标 | 永不进入危险 |
> | 不变集 | 吸引域 | 安全集 $\mathcal C$ |
> | 约束 | $\dot V\le-\alpha(V)$ | $\dot h\ge-\alpha(h)$ |
> **稳定性与安全性，是同一套不变集数学的两面**（§10 详述 Lyapunov）。

> [!abstract] 可达性：最大可行集（[[Reachability Constrained Reinforcement Learning|RCRL]]）
> 传统约束 RL 用期望累积代价 $\mathbb E[\sum\gamma^tc]\le\epsilon$，可能"期望安全但单步违约"。可达性视角定义**安全价值** $V_c^{\max}(s)=\max_\pi\mathbb E[\max_{t\ge0}\gamma^tc(s_t)]$（最坏情况最大代价），**最大可行集** $\mathcal F=\{s:V_c^{\max}(s)\le d\}$——理论上最大的可控不变集。对比 CBF：CBF 需手工设计 $h(x)$、可行集保守；RCRL 学 $V_c^{\max}$、得最大理论可行集。**插销启示**：高速 in-hand 操作中，"最大可行集"允许更激进的动作，只要保证"最终能稳住"。

> [!tip] 难以解析表达的安全约束怎么办（[[How to Train Your Latent Control Barrier Function - Smooth Safety Filtering Under Hard-to-Model Constraints|LatentCBF]]）
> "不掉落物体"难以解析写成 $h(x)$。LatentCBF 在 world model 的**潜空间**学 CBF，无需显式状态表示。关键洞察：值函数光滑性线性依赖 margin function 光滑性——分类器作 margin 会梯度饱和，WGAN 梯度惩罚可学光滑 margin。这把 CBF 接到了 [[ReinforcementLearning#6.1 Model-Based RL：在想象中转笔|世界模型]]。

---

## 10. 稳定性理论的统一基石

> [!important] 章节定位：所有控制器共享的底层骨架
> §3–§9 介绍了阻抗、OSF、混合、SMC、CIMPC、CBF 等设计范式。本节回到它们**共享的数学骨架**——Lyapunov 稳定性。它统一了 §3.2 阻抗的被动性、§4 OSF 零空间收敛、§9 CBF 对偶、§11 LQR 代价收敛、§12 自适应参数收敛，以及与 [[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|RL]] 的桥梁。**它是评判任何控制器（古典/RL/Diffusion）是否"真正可靠"的唯一通用尺度。**

> [!tip] 本节四拍
> **直觉**（找一个"能量函数"沿轨迹单调下降，就能断言收敛，无需解 ODE）→ **推导**（Lyapunov→LaSalle→ISS→被动性）→ **对比**（渐近 vs 指数 vs 输入-状态稳定）→ **联系**（价值函数即 Lyapunov 函数——RL 与控制的最深握手）。

### 10.1 Lyapunov 直接法

考虑 $\dot x=f(x)$，$f(0)=0$。**Lyapunov 函数候选** $V$：$V(0)=0$、$V(x)>0$（正定）。沿轨迹 $\dot V=\nabla V^Tf(x)$。

> [!theorem] Lyapunov 直接法
> 1. $\dot V\le0$ → **Lyapunov 稳定**（轨迹有界）；
> 2. $\dot V<0$（$x\ne0$）→ **渐近稳定**（$x\to0$）；
> 3. $\dot V\le-\alpha V$ → **指数稳定**（$\|x(t)\|\le Ce^{-\alpha t/2}\|x(0)\|$）。

灵巧操作应用：PD+重力补偿用 $V=\frac12\dot q^TM\dot q+\frac12\tilde q^TK_p\tilde q$；阻抗用 §3.2 的 $V$；OSF 用 $\Lambda$-加权 $V$；CBF 用 $h(x)$ 作对偶 barrier。

### 10.2 LaSalle 不变集原理

> [!theorem] LaSalle 不变集原理
> 紧致正不变集 $\Omega$ 上 $\dot V\le0$，令 $E=\{x:\dot V=0\}$、$M$ 为 $E$ 内最大不变集，则轨迹 $\to M$。

**为何重要**：许多机械系统 $\dot V$ **半负定**（如 $\dot V=-\dot q^TD\dot q$ 仅在 $\dot q=0$ 处为零），Lyapunov 只给稳定、不给渐近稳定。LaSalle 弥补：分析"$\dot V=0$ 的最大不变集"是否仅含平衡点。例：PD+重力补偿下 $\dot V=-\dot q^TK_d\dot q\le0$，$\dot V=0\Leftrightarrow\dot q=0$，代入闭环得 $\dot q\equiv0\Rightarrow\tilde q=0$，故全局渐近稳定。

### 10.3 输入-状态稳定性 (ISS)

> [!theorem] ISS-Lyapunov 函数
> 系统 ISS ⟺ 存在 $V$ 与 $\mathcal K_\infty$ 函数使 $\|x\|\ge\chi(\|u\|)\Rightarrow\dot V\le-\alpha_3(\|x\|)$。
> **物理含义**：状态范数大于扰动幅值的某非线性增益时能量严格下降——对所有有界扰动给出有界响应。

灵巧操作应用：把未建模动力学（摩擦、迟滞、电缆张力）当输入扰动，ISS 保证策略不因小扰动发散；把 **sim-to-real gap 视为有界外部输入**，ISS-Lyapunov 给出"仿真控制器在真机仍稳定"的充分条件——这是 frozen-rigid 适配的理论根据（呼应 [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|sim-to-real]]）。

### 10.4 被动性与"价值即 Lyapunov"

> [!important] 被动性的统一表述 + RL 桥梁
> 系统 $\Sigma:u\to y$ **被动**：存在储能 $H\ge0$ 使 $\dot H\le u^Ty$。关键性质：两个被动系统反馈互联仍被动（被动性定理）；严格输出被动 + 零状态可观 ⇒ 渐近稳定。
>
> **与 RL 的统一（[[Safe Model-based Reinforcement Learning with Stability Guarantees|价值即 Lyapunov]]）**：对严格正定代价 $r(x,u)>0$，价值函数 $V^\pi(x)=r+V^\pi(f(x,\pi(x)))$ 重排得 $V^\pi(f(x,\pi(x)))=V^\pi(x)-r<V^\pi(x)$——**恰好是 Lyapunov 下降条件！** 故价值函数定义系统吸引域、策略优化等价于扩大吸引域。这给 [[ReinforcementLearning|Safe RL]] 提供控制论根基。另一路线（结构约束而非软惩罚）：用单调 + 过原点的 Stacked-ReLU 网络 $u(\omega)=\sum\alpha_k\mathrm{ReLU}(\omega-\beta_k)$（$\alpha_k>0$）把无源性条件 $\omega u(\omega)\ge0$ 直接编码进架构。

---

## 11. 线性二次最优控制 (LQR)

> [!tip] 本节四拍
> **直觉**（插销接近相用 LQR 当 baseline，免手调 PD）→ **推导**（HJB→ARE / Riccati 递推）→ **对比**（LQR / iLQR / 数据驱动 LQR / RL）→ **联系**（LQR=能解析求解的 RL，§10 Lyapunov、[[Dynamics#3.5 Hamiltonian 形式与三种等价视角|Hamiltonian]]、[[Optimization#6.1 iLQR/DDP：动态规划结构上的 Gauss-Newton|iLQR]]）。

> [!theorem] 连续 ARE 与最优反馈
> $\dot x=Ax+Bu$、$J=\int_0^\infty(x^TQx+u^TRu)dt$（$Q\succeq0,R\succ0$）。若 $(A,B)$ 可镇定、$(A,Q^{1/2})$ 可观，则代数 Riccati 方程 $A^TP+PA-PBR^{-1}B^TP+Q=0$ 有唯一正定解 $P^*$，最优反馈 $u^*=-Kx$，$K=R^{-1}B^TP^*$，闭环 $A-BK$ Hurwitz，最优代价 $J^*=x_0^TP^*x_0$。
> **证明骨架**：对 $V=x^TPx$ 应用 HJB $\min_u\{x^TQx+u^TRu+\nabla V\cdot(Ax+Bu)\}=0$，对 $u$ 求导得 $u^*=-R^{-1}B^TPx$，回代即 ARE。

离散有限时域是 **Riccati 后向递推** $P_k=Q+A^TP_{k+1}A-A^TP_{k+1}B(R+B^TP_{k+1}B)^{-1}B^TP_{k+1}A$——这正是 [[Optimization#6.1 iLQR/DDP：动态规划结构上的 Gauss-Newton|iLQR]] 后向 pass 的线性化原型。

> [!important] LQR 是连接四个领域的枢纽
> | 方法 | 模型来源 | 解法 |
> |:--|:--|:--|
> | **LQR** | 已知 LTI | ARE 一次求解 |
> | **iLQR/DDP** | 非线性+线性化 | 后向 Riccati + 前向滚动 |
> | **数据驱动 LQR**（§13） | Hankel/PE 数据 | LMI/SDP |
> | **DDPG/SAC** | 神经网络拟合 $Q_\phi$ | 随机梯度 |
>
> **LQR = 能解析求解的 RL**（回扣 [[ReinforcementLearning#2.2 值函数与 Bellman 方程|Bellman↔HJB↔LQR]]）。插销母题：接近相 $A,B$ 由刚体动力学线性化、LQR 给最优增益免手调 PD，进入接触段切换到 §3.2 阻抗或 §5 hybrid——"分段线性 + 模式切换"是工业级灵巧操作的实用骨架。

---

## 12. 自适应控制与确定性等价

> [!tip] 本节四拍
> **直觉**（孔的摩擦、销的质量未知但恒定，边干边辨识）→ **推导**（MRAC + 参数误差进能量函数）→ **对比**（鲁棒控制 vs 自适应控制）→ **联系**（参数线性性↔[[Dynamics#3.4 惯量参数线性性：通往自适应控制的桥|Dynamics §3.4]]、自适应≈Meta-RL）。

被控对象 $\dot x=f(x,u,\theta)$，$\theta$ 未知但常值（负载惯量、摩擦、电缆刚度）。目标：同时**辨识 $\theta$** 与**控制 $x$**。

**MRAC**：参考模型 $\dot x_m=A_mx_m+B_mr$ 给期望响应，控制律 $u=\theta_x^Tx+\theta_r^Tr$ 由可调 $\hat\theta(t)$ 实现，误差 $e=x-x_m$，梯度自适应律 $\dot{\hat\theta}=-\Gamma e^TPB\phi$。

> [!theorem] MRAC 稳定性
> 匹配条件下取 $V=e^TPe+\tilde\theta^T\Gamma^{-1}\tilde\theta$，则 $\dot V=-e^TQe\le0$，LaSalle 给 $e\to0$。
> **关键**：$V$ 含**参数误差** $\tilde\theta=\hat\theta-\theta^*$——参数误差进入能量函数，这是自适应与固定增益控制最本质的区别。

**确定性等价**：用当前估计 $\hat\theta$ 替真实 $\theta$，$u_{CE}=\pi^*(x;\hat\theta)$。可证收敛的条件：辨识误差 $\tilde\theta\to0$ 足够快（**持续激励 PE**）且 $\pi^*$ 对 $\theta$ 连续。

> [!theorem] PE → 参数收敛
> 若回归向量 $\phi$ 满足 $\alpha I\preceq\int_t^{t+T}\phi\phi^Td\tau$（$\forall t$），则 $\hat\theta\to\theta^*$ 指数收敛。**物理含义**：仅当输入"足够丰富"（在 $T$ 内激发所有模式），辨识才能区分真实参数与等价参数。PE 正是 §13 Hankel 满秩条件的连续时间对偶。

> [!important] 自适应控制 ≈ Meta-RL（现代视角）
> RMA、Latent Adapter、FiLM Conditioning 本质都是**学习版的确定性等价控制器**：神经网络替代解析 $\pi^*(x;\theta)$，隐变量 $z$ 替代经典 $\hat\theta$（见 [[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|RMA]]）。Lyapunov 自适应律的 PE→收敛保证，解释了这些深度自适应方法"为何能在小数据下工作"。其力学根基是 [[Dynamics#3.4 惯量参数线性性：通往自适应控制的桥|操作器方程对惯量参数线性]] + $\dot M-2C$ 反对称。
>
> **鲁棒 vs 自适应**：鲁棒控制（SMC/$H_\infty$）应对范数有界的最坏情况、保守、无需在线辨识；自适应应对参数化慢时变、需 PE。现代趋势：鲁棒+CBF→安全 RL；自适应+Meta-RL→Latent Adapter。

---

## 13. 数据驱动控制：模型不准时如何仍给稳定性证书

> [!tip] 本节四拍
> **直觉**（孔/执行器模型难辨识，能否直接从轨迹数据设计控制器？）→ **推导**（Willems 引理：数据=系统行为的非参数表示）→ **对比**（先辨识再控制 vs 直接数据驱动）→ **联系**（PE↔§12、informativity↔[[ReinforcementLearning|数据驱动 RL]]）。

> [!important] Willems 基本引理（数据驱动控制的基石）
> 对可控 LTI 系统，若输入 $u_{[0,T-1]}$ 是 $(N+L)$ 阶**持续激励**（其深度 $L$ 的 Hankel 矩阵行满秩，需 $T\ge(m+1)(N+L)-1$），则 $(\bar u,\bar y)$ 是系统合法轨迹 **当且仅当** 存在 $g$ 使
> $$\begin{pmatrix}\bar u\\\bar y\end{pmatrix}=\begin{pmatrix}\mathcal H_L(u)\\\mathcal H_L(y)\end{pmatrix}g.$$
> **核心洞察**：Hankel 矩阵的列空间**精确等于**所有长度 $L$ 的合法轨迹空间——**数据本身就是系统行为的非参数化表示**，无需先辨识 $(A,B,C,D)$。

**数据信息性框架**：数据 $D$ 对性质 $P$ **信息充分** ⟺ 数据一致集 $\Sigma_D\subseteq\Sigma_P$（所有能生成该数据的系统都具性质 $P$）。对控制：存在**单一控制器** $K$ 镇定所有一致系统。无噪声情形，若 $[X_-;U_-]$ 行满秩，镇定控制器可经 LMI 求解 $K=U_-GP^{-1}$（$\begin{bmatrix}P&X_+G\\G^TX_+^T&P\end{bmatrix}\succ0$）。

> [!note] 带噪声数据：S-lemma 把无穷多模型收成一个 LMI
> 噪声使 $\Sigma_D$ 含无穷多系统，鲁棒镇定要一个控制器同时覆盖全部。把噪声先验写成**二次矩阵不等式 (QMI)**、Lyapunov 条件也写成 QMI，再用 **Matrix S-lemma/Finsler 引理** 把"QMI 蕴含 QMI"转成有限维 LMI（$M-\alpha N\succ0$）——无穷多约束坍缩成一个可解的 SDP。这是 data-based control 的关键技巧。

> [!important] 灵巧操作应用：短真机轨迹 → 稳定性证书
> 对 L25 执行器 gap，局部状态 $x_t=[\phi_t,\dot\phi_t,T_t,z_{\delta,t}]$（$z_\delta$ 编码 CAN latency），用 5–10 分钟 scripted 真机激励轨迹给出 $(U_-,X_-,X_+)$，噪声项吸收 CAN 抖动/温漂/触觉误差/未建模摩擦。流程：① 检查 $[X_-;U_-]$ 是否满秩（PE）；② 设噪声 QMI；③ 求解 LMI；④ 若可行，$P$ 是覆盖所有一致 actuator 模型的**共同 Lyapunov 证书**。这给 [[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|"5 分钟真机适配"]]增加了古典控制判据：不只看 validation MSE，而是检查所有与短数据一致的局部模型是否共享同一稳定性证书。

**DeePC**（Data-Enabled Predictive Control）把 Willems 引理嵌入 MPC：用数据 Hankel 矩阵替代显式模型，$\min_{g,\sigma}\sum\|\bar y-y_{ref}\|_Q^2+\|\bar u\|_R^2+\lambda\|\sigma\|^2$（松弛项 $\sigma$ 处理测量噪声）。

> [!warning] 局限与扩展
> 数据驱动控制主要针对 **LTI**。灵巧操作的非线性/混合动力学需扩展：**Koopman 算子**提升到无限维线性空间、**分段线性**（不同接触模式分别应用）、**与 RL 结合**（数据驱动给初始策略、RL 在线精调）。这正是数据驱动控制与 [[ReinforcementLearning|RL]]的交汇带。

---

## 14. 知识回扣与记忆图：一根销轴串起控制理论六层

> [!abstract] 用一根销轴把全讲复述一遍（刻意复述，为记忆）
> 我们要把销轴插进孔。**(§1)** 先用古典语言描述电机-关节闭环——极点决定会不会振荡，相位裕度决定 CAN 延迟是否危险。**(§2)** 多指协调靠 $J_h$（关节↔接触）与 $G$（接触↔物体）的虚功对偶。**(§3)** 硬插会因刚度悖论卡死，于是用阻抗（插入方向软）；硬件是高减速比时其实用导纳；RL 可学时变阻抗让接近相硬、滑入相软。**(§4)** 在销轴尖的任务空间直接设计控制，用 $\bar J$ 把次任务藏进零空间。**(§5)** 插入方向控力、找正方向控位置——力位混合，但当心几何不一致致 runaway。**(§6)** 销头在倒角上滚是非完整约束，规划要做平行泊车式机动。**(§7)** 摩擦未知用 SMC，接触在 free/stick/slide 间切换要 bumpless，靠摩擦锥余量 $\gamma$ 闭环防滑。**(§8)** 让接触隐式 MPC 自己发现接触序列（Sigmoid 松弛穿过接触梯度）。**(§9)** 用 CBF-QP 安全滤波保证绝不崩坏孔。**(§10)** 凭什么这些都稳？Lyapunov——而且价值函数就是 Lyapunov 函数。**(§11)** 接近相用 LQR 当 baseline。**(§12)** 孔的摩擦未知就自适应辨识（PE 条件下收敛）。**(§13)** 连模型都不要，直接用短真机轨迹的 Hankel 矩阵 + S-lemma 给出稳定性证书。**一根销轴，插穿了控制理论六层大厦。**

> [!important] 一张表记住全篇
> | 层 | 核心问题 | 关键工具 | 销轴的哪一环 |
> |:--|:--|:--|:--|
> | §1 系统描述 | 闭环会振荡吗 | 极点、相位裕度 | 延迟会否自激 |
> | §2 运动学/静力学 | 怎么动/怎么使力 | $J_h$/$G$ 对偶 | 多指协调 |
> | §3 柔顺 | 跟位置还是跟力 | 阻抗/导纳/变阻抗 | 插入方向软 |
> | §4 OSF | 任务空间设计 | $\Lambda$、$\bar J$、零空间 | 销轴尖任务阻抗 |
> | §5 力位混合 | 正交分解 | 选择矩阵 $S$ | 轴向控力/横向控位 |
> | §6 接触非线性 | 滚动几何 | Montana、非完整 | 倒角上滚动 |
> | §7 鲁棒/状态机 | 摩擦未知、模式切换 | SMC、状态机、防滑 | bumpless、防滑 |
> | §8 接触隐式 MPC | 自发现接触序列 | LCP、Sigmoid 松弛 | 自动规划插入 |
> | §9 安全 | 绝不崩坏 | CBF-QP、可达性 | 力上限滤波 |
> | §10 稳定性 | 凭什么稳 | Lyapunov/LaSalle/ISS/被动性 | 接触闭环证书 |
> | §11 LQR | 最优反馈 | ARE/Riccati | 接近相 baseline |
> | §12 自适应 | 未知参数 | MRAC、PE、确定性等价 | 在线辨识摩擦 |
> | §13 数据驱动 | 无模型证书 | Willems、informativity、S-lemma | 短轨迹给证书 |

> [!tip] 六条贯穿全讲的"暗线"
> 1. **对偶性 $J_h/G$**：运动映射与力映射经虚功对偶（§2），外连 [[Dynamics]]/[[ContactMechanics]] 的 $J/G/P$ 大家族。
> 2. **阻抗/导纳因果性**：选哪个取决于底层硬件能否透明输出力矩（§3）——这是工程落地的命门。
> 3. **Lyapunov 统一一切**：稳定性（§10）=安全性（§9 CBF 对偶）=最优代价（§11）=自适应能量（§12 含参数误差）——一个 $\dot V\le0$，统摄全部。
> 4. **接触状态机 + bumpless**：混合系统的模式切换（§7）贯穿统一架构（§3.5）、CIMPC（§8）、与 [[ReinforcementLearning#1.3 非光滑性的两副面孔：接触流形与混合动力学|RL 混合动力学]]。
> 5. **PE 主线**：持续激励既是自适应参数收敛的条件（§12）、又是数据驱动 Hankel 满秩的条件（§13）——同一个"输入要足够丰富"。
> 6. **价值即 Lyapunov**：RL 的价值函数天然是 Lyapunov 函数（§10.4）——这是控制论与 [[ReinforcementLearning|RL]] 最深的握手，也是 Safe RL 的根基。

> [!note] 跨领域链接（双向、点对点）
> - **↔ [[Dynamics]]**：操作器方程是控制对象；OSF 共用 $\Lambda/\bar J$（§4↔Dyn §7）；线性参数化↔自适应（§12↔Dyn §3.4）；Hamiltonian↔LQR（§11）。
> - **↔ [[ContactMechanics]]**：摩擦锥/力闭合定义力控约束（§5,§7）；Montana 滚动（§6）；LCP↔接触隐式 MPC（§8）。
> - **↔ [[Optimization]]**：LQR↔iLQR↔QP（§11）；CIMPC↔CITO（§8）；CBF-QP（§9）。
> - **↔ [[SignalProcessing]]**：相位裕度/Bode（§1）；KF/EKF 状态估计（§1.4）；滑移检测（§7.3）。
> - **↔ [[ReinforcementLearning]]**：价值即 Lyapunov（§10.4）；SAC 熵即柔顺（§3）；数据驱动↔RL（§13）；RMA↔自适应（§12）。
> - **↔ [[EmbodiedAI]]**：分层 VLA 的低层控制器。

---

## 15. 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文涉及控制理论的核心主题。

### 阻抗控制与变刚度
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks|VICES]] — 阻抗控制作为 RL 动作空间
- [[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking|Prosthesis VI]] — 数据驱动阻抗辨识（两步凸优化）
- [[FACET - Force-Adaptive Control via Impedance Reference Tracking|FACET]] — 阻抗参考模型跟踪，RL 跟踪虚拟弹簧-质量-阻尼轨迹
- [[Path-Constrained Haptic Motion Guidance via Admittance Control]] — 路径约束导纳控制

### Safe RL 与稳定性
- [[Safe Model-based Reinforcement Learning with Stability Guarantees]] — 价值即 Lyapunov、吸引域
- [[Reachability Constrained Reinforcement Learning]] — 可达性约束、最大可行集
- [[How to Train Your Latent Control Barrier Function - Smooth Safety Filtering Under Hard-to-Model Constraints]] — 潜空间 CBF
- [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] — 偏导数界 SDP 稳定性证书
- [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] — Lipschitz 约束网络
- [[On Robust Reinforcement Learning with Lipschitz-Bounded Policy Networks]] — 鲁棒 RL
- [[Reinforcement Learning for Optimal Primary Frequency Control - A Lyapunov Approach]] — 结构约束网络保证稳定性

### 控制频率与时间步
- [[TARC - Time-Adaptive Robotic Control]] — 策略输出动作+持续时间
- [[Elastic Time Step Reinforcement Learning, VTS-RL]] — 弹性时间步
- [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks]] — 高频控制进化
- [[Reinforcement Learning for Control with Multiple Frequencies]] — 多速率采样
- [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning]] — 动作持续性

### 轨迹跟踪与模仿
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] — 神经跟踪控制
- [[DeepMimic - Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills]] — 物理角色动画
- [[Learning Agile and Dynamic Motor Skills for Legged Robots]] — action-to-torque Actuator Network 近似低层闭环
- [[Learning Quadrupedal Locomotion over Challenging Terrain]] — proprioceptive student 调制底层运动 primitive

### Actuation-Aware 建模与高动态控制
- [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control|OmniXtreme]] — torque-speed envelope 建模执行器物理极限，actuation-aware 残差 RL

### 顺应控制与硬件
- [[Minimalist Compliance Control|MCC]] — 方向相关效率 + 系列弹性元件的最小模型力控
- [[sim2real|硬件 Sim-to-Real Gap 分析]] — 电机/减速器/传动方案对控制迁移的系统影响

### Sim-to-Real 与视触觉控制
- [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding|CGP]] — 力-触觉反馈闭环的 sim-to-real 对齐

### 项目级真机控制 Idea（WMTS）
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-002-Latency-Aware-Actuator|LAAA]] — CAN 延迟与温漂 conditioned actuator FiLM
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-013-Stick-Slip-Mode-Switching|SSMS]] — stick-slip 模态识别的双子策略切换控制

---

## 16. 结论

从高增益位置控制，到引入顺应性的阻抗/导纳（§3），到处理冗余的 OSF（§4），控制理论的演进主线是**对物理交互本质的尊重**——不再强行命令机器人违反物理约束，而是用数学工具（对偶性、动态解耦、接触松弛）去建模和利用约束。非线性控制与接触隐式 MPC（§8）更把这一理念推向极致：**接触不再是干扰，而是可优化利用的资源**。而把这一切缝在一起的，是 Lyapunov 这把统一尺度（§10）——它让稳定性、安全性、最优性、自适应、乃至 RL 的价值函数说同一种语言。三大记忆支柱：**对偶性、动态解耦、接触松弛**；一条终极暗线：**价值即 Lyapunov**——它通向 [[ReinforcementLearning|强化学习]]的安全未来。
