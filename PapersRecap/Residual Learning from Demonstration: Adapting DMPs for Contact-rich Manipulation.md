---
tags:
  - paper
  - learning-from-demonstration
  - dmp
  - residual-learning
  - contact-manipulation
  - insertion
aliases:
  - rLfD
  - Residual DMP
  - Residual Learning from Demonstration
paper-year: 2022
read-date: 2026-06-25
venue: IEEE RA-L / ICRA 2022
paper-pdf: "[[Papers/Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
---

# Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation

> [!abstract] 核心贡献
> rLfD 把单次示范学到的 DMP 作为 100 Hz base policy，再叠加一个 10 Hz task-space residual RL policy，并由 500 Hz impedance controller 执行；核心结论是：对 contact-rich insertion，残差应该直接加在 task-space full pose 上，而不是加在 DMP forcing parameters 或 phase coupling 上。物理实验中 full-pose PPO/PPO rLfD 在 peg/gear/RJ-45 平均 86.9% 成功率，而无残差 DMP 平均 31.4%。

> [!tip] 与理论基础的关联
> - [[ControlTheory]] — DMP 是稳定二阶 attractor + forcing term；rLfD 保留其轨迹先验，再用残差调 setpoint/twist。
> - [[ReinforcementLearning]] — residual policy 只学“何时偏离示范”，显著降低探索维度；SAC/PPO 用 sparse reward 即可工作。
> - [[ContactMechanics]] — 插入任务的难点来自 jamming、friction、微小 pose error 引起的接触状态突变；task-space jiggling 是接触搜索策略。
> - [[Dynamics]] — full-pose correction 需要在 $SE(3)$ 上组合平移和四元数姿态，不能把欧拉角/四元数当普通向量相加。
>
> **核心技术**: Dynamic Movement Primitives, Residual Reinforcement Learning, Task-space Exploration, Quaternion Residual Correction, Full-pose Insertion, Real-time Impedance Control

## 0. 阅读定位与范本价值

这篇论文对你的知识库价值很高，因为它把一个非常常见的机器人学习问题讲清楚了：**示范轨迹可以把机器人带到“差不多对”的区域，但 contact-rich insertion 的最后 1-3 cm / 10-40° 误差，需要在线接触搜索来解决**。

它不是单纯“DMP + RL”这么简单。真正的问题是：残差应该加在哪里？

- 加在 DMP forcing weights $\omega$ 上？太全局，局部接触搜索不够。
- 加在 phase-modulated coupling $C_t$ 上？仍跟 DMP phase 绑定，不够局部。
- 完全不用 DMP，纯 SAC/PPO？可以高分，但训练长、reward dense、真机风险大。
- 直接加在 task-space twist / full pose 上？本文结论：最适合 contact-rich insertion。

这对 WMTS/DNPM 也有启发：对高风险真机 RL，不一定要从零学动作；可以让强先验轨迹/技能先把系统带进可学习区域，再让低频 residual policy 学局部修正。关键是残差作用空间必须和失败机制对齐。

| 四支柱 | 本文必须回答的问题 | 本 recap 落点 |
|---|---|---|
| 逻辑与价值 | 为什么 DMP 需要 residual，为什么 residual 要在 task space？ | §1：示范解决全局路线，接触误差需要局部 jiggling |
| 原理与理论 | DMP、MDP、task-space residual、quaternion correction 如何从零连起来？ | §2：DMP 二阶系统、残差叠加、$SO(3)$ composition |
| 实验与验证 | 哪些表格证明 task-space/full-pose residual 是核心？ | §3：Table I-VI 逐表因果链 |
| 未来与结合 | 如何迁移到 LinkerHand/WMTS，哪里不该外推？ | §5-§7：residual PPO、action-space adapter、触觉/力限制 |

## 1. 问题设定与动机

### 1.1 一句话核心

rLfD 的一句话核心是：**用 DMP 保留示范给出的稳定全局轨迹，用 RL 残差只学习接触阶段的局部 task-space 修正，从而把真机 insertion 从“全任务探索”变成“示范附近的安全 jiggling 搜索”。**

### 1.2 直观隐喻

这就像插网线：

- 你先靠视觉和记忆把插头移动到接口附近，这是 DMP；
- 接近后，你不会按原轨迹硬推，而会轻微晃动、调整角度、感受卡住的位置，这是 residual policy；
- 如果完全靠随机 RL 学插网线，它可能先撞坏塑料卡扣；如果完全靠 DMP，初始姿态稍偏就卡住。

这个隐喻的可证伪点是：如果残差不在 task space 做局部 jiggling，而是在 DMP 参数空间做平滑全局形变，应当更难解决接触卡滞。Table I 正好证明 task-space translation rLfD 平均 74.9%，PoWER/FDG/eNAC 只有 23.3/19.9/5.3%。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 在 contact-rich insertion 中的局限 |
|---|---|---|
| Pure DMP / behavior cloning | 示范轨迹 + stable attractor | 只能泛化小扰动；论文称单 demo 在 start 偏差 3 mm 内可 100% 成功，但更大偏差失败 |
| DMP forcing-term adaptation | 改 $\omega$，全局改变轨迹形状 | 探索在参数空间，局部接触 jiggling 不直接 |
| Phase coupling adaptation | 改 $C_t$，随 phase 调制 | 对 wiping/hitting 等 phase feedback 有用，但 insertion 的局部卡滞需要 task-space 搜索 |
| Pure model-free RL | 不需要示范，表达力强 | 真机训练样本多、dense reward 难调、动作幅度大，硬件磨损/损坏风险高 |
| Hybrid switching DMP/RL | 在 base policy 和 RL policy 间切换 | 切换不是叠加，丢掉“示范轨迹 + 小修正”的连续结构 |
| Translation-only residual | 学 $\Delta x$ | peg 可用，但 gear/RJ-45 需要姿态对齐，translation-only 不够 |

### 1.4 Delta 分析

rLfD 的 delta 是三层合取：

1. **Residual location**：残差直接作用在 task-space，不在 DMP 内部参数空间。
2. **Residual type**：残差是 nonlinear RL policy，而不是线性/RLS/random noise。
3. **Residual scope**：从 translation residual 扩展到 full pose residual，用 quaternion composition 避免姿态相加的奇异性。

论文故事讲得好的地方是它逐层排除替代方案：先在仿真中比较 residual 加在哪里，再比较 linear/random/SAC/PPO，再到物理系统比较 translation-only vs full-pose，最后做 speed 和 transfer。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $\pi_b$ | base policy | 单次示范拟合 DMP | 固定，无 RL 梯度 | 提供稳定名义轨迹 | DMP 不是神经 policy；运行 100 Hz |
| $\hat{\pi}_b$ | translational DMP | DMP position/velocity | 固定 | base Cartesian translation/twist | hat 表示 translation 分量 |
| $\tilde{\pi}_b$ | orientation DMP | quaternion/angular velocity DMP | 固定 | base orientation policy | tilde 表示 orientation 分量 |
| $\pi_\theta$ | residual policy | SAC/PPO 学习 | RL 中带梯度 | 学 task-space correction | 运行 10 Hz，不是 500 Hz controller |
| $\hat{\pi}_\theta$ | $\mathbb{R}^3$ translation residual | actor output | 带梯度 | 局部平移 jiggling | 加在 task-space，不加在 DMP weights |
| $\tilde{\pi}_\theta$ | angle-axis / quaternion residual | actor output | 带梯度 | 姿态 correction | 不能直接加四元数；需 $Q_\Delta\circ Q_b$ |
| $Q_b$ | unit quaternion | orientation DMP | 固定 | base end-effector orientation | $Q$ 与 $-Q$ 表同一姿态，需注意符号连续 |
| $Q_\Delta$ | unit quaternion | residual from angle-axis | 带梯度经 actor 输出 | residual rotation | $\alpha\in[-\pi,\pi]$，用 $\cos,\sin$ 映射 |
| $Q_f$ | unit quaternion | composition | controller input | final orientation | 先残差再 base：$Q_f=Q_\Delta\circ Q_b$ |
| $\pi_f$ | full twist policy | base + residual | 执行层 | final motor command before controller | $\pi_f=[\hat{\pi}_f,\tilde{\pi}_f]^T$ |
| controller | 500 Hz impedance | real-time control | 不通过 RL 反传 | 追踪 setpoint / twist | DMP/RL 给 setpoint，真正力交互由 impedance 执行 |
| reward | sparse success mostly | environment | RL signal | insertion success | pure SAC baseline 使用 engineered dense reward，不能与 rLfD sparse reward混淆 |

### 2.2 从 DMP 零基础开始：示范如何变成稳定轨迹先验

标准 point-to-point DMP 可以从二阶弹簧-阻尼系统理解：

$$
\tau \dot{v}
=
\alpha_v(\beta_v(g-x)-v)
+f_\omega(s)
+C_t,
$$

$$
\tau \dot{x}=v.
$$

其中：

- $x$ 是当前位姿/位置；
- $g$ 是目标；
- $\alpha_v,\beta_v$ 让系统像稳定弹簧-阻尼器一样收敛；
- $f_\omega(s)$ 是从示范拟合出来的 forcing term，负责把简单直线 attractor 变成示范形状；
- $C_t$ 是 coupling term，可用于在线调制；
- $s$ 是 canonical phase variable。

没有 forcing term 时：

$$
\tau \dot{v}=\alpha_v(\beta_v(g-x)-v)
$$

只是一个稳定收敛到 $g$ 的轨迹。DMP 的强处是：它把“到目标的稳定性”和“示范轨迹形状”分开。对 insertion，这意味着 base trajectory 不会完全随机探索，而是从一开始就朝接口移动。

但 DMP 的弱点也来自这里：它是示范附近的 attractor。接触任务只要孔位、摩擦、物体姿态、桌面斜率稍有变化，示范轨迹就可能卡住。

### 2.3 残差到底加在哪里：Eq.(1) 的四种解释

论文把探索噪声/残差 $\eta$ 放在不同位置比较：

$$
\dot{y}
=
\frac{1}{\tau^2}
\left(\alpha_v(\beta_v(g-x)-\tau y)+f_{\omega+\eta}+C_t(\eta)\right)
+\eta.
$$

这条式子的重点不是符号细节，而是四种 residual location：

| 类型 | 加在哪里 | 直觉 | 论文结果 |
|---|---|---|---|
| A | 不加 residual | DMP 原样执行 | 平均 16.0% |
| B | phase-modulated coupling $C_t(\eta)$ | 随 phase 平滑调制 | eNAC 平均 5.3% |
| C | forcing term parameters $\omega+\eta$ | 改示范轨迹形状 | FDG 19.9%, PoWER 23.3% |
| D | task space outside DMP | 直接局部 jiggling | rLfD 74.9% |

为什么 task-space 最好？因为 insertion 的失败通常是局部接触卡滞：孔边、齿轮角、RJ-45 塑料头。解决方式常常是小幅平移/旋转搜索，而不是把整条 DMP 轨迹的 forcing weights 改掉。

### 2.4 Translation residual：从 base policy 到 final policy

平移部分很直接：

$$
\hat{\pi}_f
=
\hat{\pi}_b+\hat{\pi}_\theta.
$$

其中 $\hat{\pi}_b$ 来自 DMP，$\hat{\pi}_\theta$ 来自 RL residual policy。

这个式子有一个重要含义：RL 不需要学完整动作，只需要学“偏离 base 多少”。如果 base DMP 已经把 end-effector 带到接口附近，那么 residual 的探索空间比 pure RL 小很多。这解释了为什么 rLfD SAC 只需要 700 episodes，而 pure SAC baseline 需要 12.5K episodes 且使用 dense reward。

### 2.5 Orientation residual：为什么不能把四元数当向量加

平移可以加：

$$
x_f=x_b+\Delta x.
$$

姿态不能直接加：

$$
Q_f\neq Q_b+\Delta Q.
$$

因为 unit quaternion 必须满足：

$$
\|Q\|=1,
$$

且 $SO(3)$ 是非欧式流形。直接加会破坏归一化，欧拉角还会有 gimbal lock。

论文用 angle-axis 输出 residual：

- 旋转轴 $r\in\mathbb{R}^3$；
- 角度 $\alpha\in[-\pi,\pi]$。

转成 residual quaternion：

$$
Q_\Delta
=
\left[
\cos\left(\frac{\alpha}{2}\right),
\frac{r}{\|r\|}\sin\left(\frac{\alpha}{2}\right)
\right].
$$

再用 quaternion multiplication 组合：

$$
Q_f=Q_\Delta\circ Q_b.
$$

最后 $Q_f$ 通过 log transform 转成 angular velocity 给控制器。

这段是本文对 full pose residual 的理论核心：它不是“多输出三个角度”，而是在 $SO(3)$ 上正确组合 residual rotation。

### 2.6 Full pose policy

最终 twist policy 写成：

$$
\pi_f=[\hat{\pi}_f,\tilde{\pi}_f]^T.
$$

其中：

$$
\hat{\pi}_f=\hat{\pi}_b+\hat{\pi}_\theta,
\quad
\tilde{\pi}_f: Q_f=Q_\Delta\circ Q_b.
$$

频率分离：

| 模块 | 频率 | 作用 |
|---|---:|---|
| DMP base policy $\pi_b$ | 100 Hz | 生成平滑示范轨迹 |
| residual RL policy $\pi_\theta$ | 10 Hz | 低频局部修正 |
| impedance controller | 500 Hz | 实时追踪并处理接触 |

这个频率设计很 pragmatic：RL residual 不需要高频直接控制接触力；高频稳定性交给 impedance controller，示范轨迹连续性由 DMP 保持。

### 2.7 实现细节与训练边界

PDF 中确认的关键实现：

| 项 | 设置 |
|---|---|
| Demonstration | single demonstration to build base policy |
| DMP basis functions | 40 for translational $\hat{\pi}_b$, 70 for orientation $\tilde{\pi}_b$ |
| DMP alone near-demo performance | start within 3 mm from demo start 时 100% successful insertions |
| SAC | recurrent policy, cell state 40, actor 400/300 ReLU, critic 300, 32 policy updates per iteration |
| PPO | clipped objective; physical experiments use curriculum over start configuration |
| PPO curriculum | task complexity increased until 1.5 cm away from demo start |
| Action projection | tanh normal projection for continuous actions |
| Simulation | MuJoCo + Robosuite |
| Real robot | 7-DoF Franka Emika Panda |
| Real control | Jacobian-transpose Cartesian impedance control |
| Episode | physical insertion max 10 s |
| Physical residual start | use $\pi_\theta$ after 3.9 s of executing base policy |

注意：论文分析 generalized force，但不要误读为 residual policy 一定使用 force/torque as input。可以说它比较了不同策略的 forcefulness；不能凭旧稿把 force observation 写成方法核心。

## 3. 训练、数据与实验

### 3.1 仿真实验任务

仿真中使用 peg insertion easy/hard 两个任务。难度由 hole size 决定；机器人起点在 demonstration 初始位置沿各轴 $\pm 12$ cm 内采样。hard task 更紧，friction/jamming 更明显。

任务完成条件：peg fully inserted。

### 3.2 Table I：残差加在 DMP 哪里

| Type | Exploration type | Model | Easy | Hard | Average | Efficiency | Reward |
|---|---|---|---:|---:|---:|---:|---|
| A | No corrections | DMP | 24.0% ±2.5 | 8.0% ±1.4 | 16.0% ±2.0 | n/a | n/a |
| B | phase-modulated coupling | eNAC | 7.2% ±1.9 | 3.4% ±2.2 | 5.3% ±2.1 | 8K | $\exp\{-L_1\}$ |
| C | forcing-term parameters | FDG | 23.6% ±4.3 | 16.2% ±1.9 | 19.9% ±3.1 | 8K | $\exp\{-L_1\}$ |
| C | forcing-term parameters | PoWER | 32.2% ±2.8 | 14.4% ±2.7 | 23.3% ±2.8 | 8K | $\exp\{-L_1\}$ |
| D | task-space translation | rLfD | **94.8% ±1.3** | **55.0% ±2.7** | **74.9% ±2.0** | **700** | $1[L_2\le\kappa]$ |

因果解释：task-space residual 不仅成功率最高，而且使用 sparse success reward 和 700 episodes。参数空间方法用 8K episodes 和 shaped reward 仍远低。这直接证明“残差作用空间”是论文核心，而不是 RL 算法本身。

### 3.3 Table II：task-space residual 需要 nonlinear policy 吗

| Type | Corrections | Adaptive policy | Easy | Hard | Average | Eff. | Reward |
|---|---|---|---:|---:|---:|---:|---|
| A | translation | Random | 25.8% ±4.3 | 9.0% ±1.8 | 17.4% ±3.1 | n/a | n/a |
| A | translation | Linear | 25.4% ±3.6 | 8.0% ±2.6 | 16.7% ±3.1 | n/a | n/a |
| D | translation | SAC | 94.8% ±1.3 | 55.0% ±2.7 | 74.9% ±2.0 | 700 | $1[L_2\le\kappa]$ |
| D | translation | PPO | 87.6% ±1.5 | **69.0% ±4.6** | **78.3% ±3.1** | 25.5K | $1[L_2\le\kappa]$ |

因果解释：linear/random residual 几乎没有解决 contact nonlinearities；SAC 和 PPO 都有效。PPO hard-task 更强但需要 25.5K episodes；SAC 在 700 episodes 达到相近平均，更符合真机样本约束。这里的取舍是：PPO 稳定 vs SAC 样本效率。

### 3.4 Table III：rLfD vs pure SAC vs hybrid switching

| Type | Corrections | Policy type | Easy | Hard | Average | Eff. | Reward |
|---|---|---|---:|---:|---:|---:|---|
| A | None | DMP | 24.0% ±2.5 | 8.0% ±1.4 | 16.0% ±2.0 | n/a | n/a |
| D | translation pure | SAC | 94.4% ±1.2 | 41.8% ±7.2 | 68.1% ±4.2 | 12.5K | $-(\alpha L_1+L_2\beta-\epsilon)$ |
| D | translation hybrid | SAC | 57.2% ±2.5 | 45.6% ±2.7 | 46.4% ±2.6 | 8K | $1[L_2\le\kappa]$ |
| D | translation rLfD | SAC | **94.8% ±1.3** | **55.0% ±2.7** | **74.9% ±2.0** | **700** | $1[L_2\le\kappa]$ |

因果解释：

- Pure SAC 可接近 rLfD easy performance，但要 12.5K episodes 和 dense reward；
- Hybrid switching 不如 additive residual，说明“何时切换 base/RL”不如“base + 小 residual”自然；
- rLfD 在 hard task 上比 pure SAC 更好，说明 DMP prior 不只是加速训练，也约束探索到更合理的接触搜索空间。

### 3.5 Fig.4：gentle insertion 的证据

Fig.4 比较 generalized force。论文文字结论：

- rLfD 成功时的 generalized force 与 DMP 相当；
- rLfD 失败时在 easy/hard task 上甚至更小；
- pure SAC / hybrid 更 forceful，可能因为缺少 base policy，需要更大动作幅度补偿；
- DMP 有时会失败于持续向下硬推。

这很重要：rLfD 的价值不是只把成功率拉高，而是在不显著增加接触力的情况下提高成功率。对真机来说，这比“高成功但用大力乱撞”更有价值。

### 3.6 物理实验任务

物理实验用 Franka Panda 做三类插入：

| Task | 难点 | 设置 |
|---|---|---|
| Peg | friction-heavy insertion | peg 28 x 28 x 77 mm，hole clearance 0.4 mm；500 starting points，up to ±3 cm |
| Gear | square hole alignment | gear 79.2 x 79.85 x 10.79 mm，hole 23 x 23 x 10 mm |
| RJ-45 / LAN cable | fragile connector + position/orientation | standard RJ-45；160 unit-vector samples, 8 bins x 20, up to 40° and ±1 cm |

每个 episode 最多 10 s；residual policy 在 base policy 执行 3.9 s 后启用。

### 3.7 Table IV：full-pose correction 是物理任务关键

| Type | Corrections | Adaptive policy | Peg | Gear | RJ-45 | Average |
|---|---|---|---:|---:|---:|---:|
| A | No corrections | None / None | 52.6% ±0.7 | 41.5% ±1.5 | 0.0% ±0.0 | 31.4% ±0.7 |
| A | translation | Linear / None | 80.7% ±4.0 | 58.7% ±1.1 | 14.6% ±1.6 | 51.3% ±2.2 |
| D | translation | PPO / None | 94.2% ±0.9 | 50.0% ±0.4 | 57.2% ±2.1 | 67.4% ±1.1 |
| A | full pose | Linear / Random | 60.3% ±2.9 | 76.2% ±2.6 | 57.3% ±2.5 | 64.6% ±2.7 |
| A | full pose | Random / Random | 91.0% ±1.9 | 86.9% ±1.7 | 64.8% ±1.2 | 80.9% ±1.6 |
| D | full pose | PPO / PPO | **97.9% ±1.2** | **92.2% ±2.6** | **70.6% ±1.4** | **86.9% ±1.7** |

因果解释：

- Peg 主要靠 translation correction，PPO/None 已达 94.2%；
- Gear/RJ-45 需要 orientation，translation-only 平均掉到 67.4，RJ-45 只有 57.2；
- Full-pose PPO/PPO 在三任务都最高，说明姿态 residual 是任务复杂化后的关键；
- Random/Random 也很强但论文指出动作幅度较大，可能损伤 fragile RJ-45 tip，因此不能只看成功率。

### 3.8 Table V：速度不是牺牲项

| Type | Corrections | Adaptive policy | Peg | Gear | RJ-45 | Average |
|---|---|---|---:|---:|---:|---:|
| A | No corrections | None / None | 7.0s ±0.1 | 8.1s ±0.2 | 10.0s ±0.0 | 8.6s ±0.1 |
| A | full pose | Linear / Random | 7.1s ±0.2 | 6.6s ±0.1 | 8.7s ±0.1 | 7.5s ±0.1 |
| A | full pose | Random / Random | 6.3s ±0.1 | 6.2s ±0.1 | 8.6s ±0.1 | 7.0s ±0.1 |
| D | full pose | PPO / PPO | **5.1s ±0.1** | **5.9s ±0.1** | **8.4s ±0.0** | **6.5s ±0.1** |

成功率提升没有靠“更慢更保守”换来；full-pose PPO/PPO 也是最快。解释是 residual policy 更早找到正确微调方向，减少卡住/反复试探时间。

### 3.9 Table VI：跨任务 transfer

| Type | Corrections | Adaptive policy | Gear | RJ-45 | Average | Eff. |
|---|---|---|---:|---:|---:|---:|
| D | full pose, full training | $\pi_{targ}$ | 92.2% ±2.6 | 70.6% ±1.4 | 81.4% ±2.0 | 500 |
| D | full pose, full training | $\pi_{src}$ | 85.4% ±1.4 | 54.5% ±3.2 | 69.9% ±2.3 | 500 |
| D | full pose, 3-shot | $\pi_{targ}$ | 70.3% ±4.0 | 59.1% ±3.1 | 64.7% ±3.6 | 60 |
| D | full pose, 3-shot | $\pi_{src\rightarrow targ}$ | **92.0% ±2.1** | **70.6% ±1.7** | **81.3% ±1.9** | **60** |

因果解释：把 source residual policy 迁移到 target，再用 3 update steps / 60 episodes，几乎恢复 full training target performance。论文称这约等于 15 分钟训练，而 full budget 500 episodes 约 2 小时。这个结果说明 residual policy 学到的不只是单个孔位，而是可迁移的接触搜索策略。

## 4. 核心洞见

### 4.1 论文真正的 insight

rLfD 的真正 insight 是：**contact-rich insertion 的学习对象不是完整技能，而是示范轨迹附近的局部误差补偿场**。

用公式说：

$$
\pi_{full}
\neq
\pi_\theta \ \text{from scratch},
$$

而是：

$$
\pi_{full}
=
\pi_{demo-prior}
+
\pi_{local-correction}.
$$

这使 RL 的探索集中在 DMP 已经带来的接触邻域里。对插入任务，成功往往不是“找到一条全新路径”，而是“在孔边卡住时怎样晃、怎样转、怎样少用力地进入”。

### 4.2 为什么 task-space residual 比 DMP parameter residual 有效

DMP parameter residual 改的是整条轨迹的形状；task-space residual 改的是当前执行点的局部动作。接触卡滞是局部事件：

$$
\text{small pose error}
\rightarrow
\text{contact normal/friction changes}
\rightarrow
\text{jam or slide-in}.
$$

因此 residual 的作用空间必须能直接表达“小幅局部平移/旋转”。Table I 的 D vs B/C 正是机制验证。

### 4.3 为什么 full-pose residual 是物理系统关键

Peg 可近似 translation insertion；gear/RJ-45 不是。Gear 的 square hole 和 RJ-45 的 fragile asymmetric connector 都要求姿态精度。若只学 $\Delta x$，会出现“位置到了但角度错”的接触卡滞。

Table IV 中 RJ-45：

- None/None: 0.0%
- Linear/None: 14.6%
- PPO/None: 57.2%
- PPO/PPO: 70.6%

这条链说明姿态 residual 不是锦上添花，而是任务从圆孔 peg 走向真实连接器时的必要条件。

### 4.4 什么时候会失效

- DMP base 太差：如果示范不能把系统带到接触邻域，residual 要学完整任务，优势消失。
- 接触状态不可观测：没有视觉/触觉/力信息时，residual 可能只能盲目 jiggling。
- 任务需要离散重规划：比如完全错孔、遮挡、需要换 grasp，局部残差不够。
- 高速动态任务：10 Hz residual + 100 Hz DMP + 500 Hz impedance 适合准静态插入，不适合快速抛接/空中转笔。
- 姿态 residual 参数化不当：若直接加欧拉角/四元数，可能引入奇异或不连续。

## 5. 替代方案与理论局限

### 5.1 理论维度

| 局限 | 为什么重要 | 对用户研究的含义 |
|---|---|---|
| DMP 是单一示范 attractor | 多模态接触策略无法表达 | 转笔如果有多种 gait/contact mode，需要 mixture/Diffusion residual |
| residual 是局部补偿 | 无法做全局任务重规划 | WMTS 需 task scheduler 决定何时换子任务，而不是只加残差 |
| full pose 在 $SE(3)$ 上仍简化 | 没有显式摩擦锥/接触模式 | 接触安全应配 tactile/contact classifier |
| sparse reward 依赖已有 base policy | 如果 base policy 不接近成功，sparse reward 学不到 | PPO Oracle 需要 curriculum / demo reset / privileged teacher |

### 5.2 算法维度

| 替代方案 | 优点 | 相对 rLfD 的问题 |
|---|---|---|
| Pure PPO/SAC | 表达力强，可学完整策略 | 样本多、dense reward、真机风险高 |
| Hybrid switching | 简单，不需设计 additive structure | 表现 46.4% 平均，不如 residual 74.9；切换不如叠加平滑 |
| Parameter-space DMP RL | 保持轨迹平滑 | 缺少局部接触 jiggling |
| Random residual | 可增强探索 | 可能用力大、损伤 RJ-45，且不可学习 |
| Diffusion residual policy | 可表达多模态局部修正 | 需要更多数据；可作为 rLfD 后续而非本文内容 |

### 5.3 工程/实验维度

- 物理任务仍是结构化 insertion，不是开放场景 manipulation。
- 使用 Franka Panda 和 impedance controller；没有验证多指手或复杂触觉。
- 纯 RL 在物理任务未能成功抽取可用策略，说明比较边界不完全对称。
- generalized force 是分析指标，不等于 residual policy 的显式输入。
- Future work 明确提到 contact sequence difficulty、减少 insertion force、视觉输入、更跨技能泛化。

## 6. 对用户研究的启发

### 6.1 对 WMTS 的迁移

rLfD 可以转成 WMTS 里的“先验技能 + residual specialist”模块：

| rLfD 组件 | WMTS 对应 | 具体用法 |
|---|---|---|
| DMP base $\pi_b$ | Diffusion/Flow generalist 或 scripted/demo prior | 生成接近成功区域的 action chunk |
| residual $\pi_\theta$ | PPO Oracle specialist | 只学局部 contact correction |
| task-space residual | end-effector / object-centric correction head | 比 joint-space 从零探索更安全 |
| full-pose quaternion correction | $SE(3)$ action adapter | 避免姿态残差的欧拉角奇异 |
| sparse reward $1[L_2\le\kappa]$ | success / contact-mode completion reward | 在强 base prior 下 sparse reward 可行 |
| transfer $\pi_{src\rightarrow targ}$ | cross-task residual reuse | 同类插入/接触子任务间快速 few-shot adaptation |

对 WMTS 的直接实验建议：

1. 用 Diffusion Policy / demonstration replay 生成 base action chunk；
2. 训练 PPO residual head 输出低幅度 $\Delta a$；
3. 比较 residual 作用空间：joint residual、task-space residual、contact-frame residual；
4. 指标不只 success，还看 contact force、drop rate、actuator saturation、training episodes；
5. 对同类任务做 3-shot transfer，检验 residual 是否学到可迁移接触搜索。

### 6.2 对 LinkerHand / 转笔的启发

转笔不是插孔，但有同构结构：一个 base gait/trajectory 负责把笔带到相位附近，局部 residual 负责防掉、补相位、修接触。

| rLfD 概念 | 转笔对应 |
|---|---|
| DMP base | human/demo/open-loop pen-spin phase trajectory |
| task-space residual | fingertip/contact-frame residual force/position command |
| full pose residual | pen axis + spin phase correction |
| sparse success | phase advanced without drop / contact mode reached |
| forcefulness metric | tactile pressure / tendon current / actuator temperature |
| transfer | 从一种笔/速度迁移到另一种笔/速度 |

关键改造：转笔 residual 不应只在 end-effector Cartesian space；更合理的是在 contact frame：

$$
\Delta a
=
[\Delta f_n,\Delta f_t,\Delta \tau_{spin},\Delta q_{local}]
$$

或者让 policy 输出对 base action 的 bounded residual：

$$
a_t=a_t^{base}+\mathrm{clip}(\Delta a_t,[-\epsilon,\epsilon]).
$$

这能把探索限制在安全局部区域，类似 rLfD 避免 pure RL 大力乱撞。

### 6.3 与当前知识库的组合

| 相关 recap | 组合方式 |
|---|---|
| [[HIL-SERL - Precise and Dexterous Robotic Manipulation via Human-in-the-Loop Reinforcement Learning]] | HIL-SERL 采 failure-boundary intervention；rLfD 给 base+residual 结构，可减少 intervention 负担 |
| [[Learning Long-Horizon Robot Manipulation Skills via Privileged Action]] | privileged action 可作为 base policy，residual policy 学真实可执行修正 |
| [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots]] | demo reset/curriculum 把策略放到接触邻域，rLfD 在邻域内学 residual |
| [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding]] | CGP 生成 contact-consistent target，rLfD residual 执行局部修正 |
| [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] | rLfD 输出 pose residual；VICES/FACET 类方法可输出 impedance residual，二者可组合 |

### 6.4 不应过度外推的点

- rLfD 不等于“RL 一定安全”；安全来自 DMP prior、bounded residual、impedance controller 和 sparse局部任务。
- 它没有解决感知问题；任务状态和接口位置仍需要足够准确。
- 10 Hz residual 适合准静态插入，不适合高动态转笔直接控制。
- 单 DMP base 不适合多模态策略，可能需要 mixture of primitives 或 diffusion base。
- 物理实验没有证明可扩展到高维灵巧手，仅证明 7-DoF arm insertion。

## 7. 与知识体系的联系

### 7.1 与 [[ControlTheory]] 的联系

rLfD 的控制结构是分层闭环：

$$
\text{DMP prior} \rightarrow \text{residual correction} \rightarrow \text{impedance controller}.
$$

DMP 提供稳定参考，residual 修正参考，impedance controller 吸收接触误差。它不是用 RL 直接替代控制器，而是把 RL 放在低频 setpoint 修正层。

### 7.2 与 [[ReinforcementLearning]] 的联系

Residual RL 的样本效率来自 action decomposition：

$$
a=a_{base}+a_{res}.
$$

这把 policy search 从完整动作空间缩小到示范附近的 correction space。Table III 的 700 vs 12.5K episodes 是这条理论的实验版本。

### 7.3 与 [[ContactMechanics]] 的联系

插入失败常来自接触法向和摩擦锥的局部变化。task-space jiggling 能改变接触点、法向和微小姿态，使系统从 jammed contact mode 进入 sliding/insertion mode。rLfD 没有显式建模摩擦锥，但通过 residual policy 学了这种局部 contact mode search。

### 7.4 与 [[Dynamics]] 的联系

姿态 correction 必须尊重 $SO(3)$ 几何。论文从 angle-axis 到 quaternion：

$$
Q_\Delta
=
[\cos(\alpha/2),\frac{r}{\|r\|}\sin(\alpha/2)]
$$

再组合：

$$
Q_f=Q_\Delta\circ Q_b.
$$

这是 robotics dynamics/kinematics 中典型的 Lie group 思维：姿态残差属于群作用，不是普通向量加法。

## 8. 应复刻的提问颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “rLfD 相比普通 residual RL 多了什么？” | 它系统比较 residual 加在 DMP 的 phase/forcing/task-space 哪个位置，并证明 task-space 最有效 |
| “为什么 full pose correction 重要？” | Gear/RJ-45 需要姿态对齐；Table IV 中 PPO/PPO 86.9 平均，PPO/None 67.4 |
| “为什么不是 pure SAC？” | Pure SAC 68.1 平均、12.5K episodes、dense reward；rLfD 74.9、700 episodes、sparse reward |
| “四元数残差怎么写才对？” | 输出 angle-axis，构造 $Q_\Delta$，用 $Q_f=Q_\Delta\circ Q_b$，不能直接加 quaternion |
| “对真机安全有什么证据？” | Fig.4 generalized force：rLfD force comparable to DMP and less forceful than pure/hybrid SAC |
| “对 WMTS 怎么用？” | 让 Diffusion/demo prior 产生 base chunk，PPO residual 只学 bounded contact correction |
| “对转笔能直接用吗？” | 不能直接用 DMP 插入框架；应改成 phase/contact-frame residual，并加入 tactile/actuator safety |

## References

- [[HIL-SERL - Precise and Dexterous Robotic Manipulation via Human-in-the-Loop Reinforcement Learning]]
- [[Learning Long-Horizon Robot Manipulation Skills via Privileged Action]]
- [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots]]
- [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding]]
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]]
