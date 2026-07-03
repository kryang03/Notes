---
tags:
  - paper
  - sim-to-real
  - reinforcement-learning
  - dynamics
aliases:
  - GAT
  - Grounded Action Transformation
paper-year: 2017
read-date: 2026-06-25
venue: AAAI 2017
paper-pdf: "[[Papers/Grounded Action Transformation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
  - "[[The CMA Evolution Strategy: A Tutorial]]"
---

# Grounded Action Transformation

> [!abstract] 核心贡献
> GAT 是 Grounded Simulation Learning 的一个动作层 grounding 算法：它不直接调仿真器物理参数，而是学习真实 forward dynamics $f(s,a)$ 与仿真 inverse dynamics $f^{-1}_{sim}(s,s')$，在仿真器内部用 $g(s,a)=\alpha f^{-1}_{sim}(s,f(s,a))+(1-\alpha)a$ 替换 policy action，使仿真中执行同一个 policy action 的效果更接近真机；在 NAO 双足行走中把 state-of-the-art hand-coded walk 从 19.52 cm/s 提升到 27.97 cm/s，提升 43.27%。

> [!tip] 与理论基础的关联
> - [[Dynamics]] — GAT 的核心是 forward model 与 inverse dynamics model 的组合：先预测真实动作效果，再求仿真中产生同等效果的动作。
> - [[ReinforcementLearning]] — 属于 sim-to-real / grounded simulation learning：policy improvement 仍在 grounded simulator 中做，真机主要用于 grounding 数据和候选 policy evaluation。
> - [[The CMA Evolution Strategy: A Tutorial]] — 论文用 CMA-ES 优化 NAO walk engine 的 15 个参数，体现老式 policy search 与 grounding 的结合。
> - [[ControlTheory]] — 对执行器延迟、关节响应差异的补偿发生在动作层；这与 actuator model / latency-aware residual control 同源。
>
> **核心技术**: Grounded Simulation Learning, Action Transformation, Forward Dynamics Model, Simulator Inverse Dynamics, CMA-ES, Sim-to-Real Locomotion

## 0. 阅读定位与范本价值

这是一篇 2017 年的老 sim-to-real 论文，但对 WMTS 仍有价值，因为它把一个常被混淆的问题讲清楚：**sim-to-real gap 不一定只能通过改物理参数或 domain randomization 解决，也可以通过“动作进入仿真器前的变换”解决。**

最容易误解的一点是方向：GAT 不是学 $a_{\mathrm{real}}=h(s,a_{\mathrm{sim}})$ 然后部署时把仿真动作翻译到真机。它是在仿真器里包一层 transformation：

$$
a \xrightarrow{g(s,a)} \hat a_{\mathrm{sim}},
$$

使得在仿真中执行 $\hat a_{\mathrm{sim}}$ 的下一状态，尽量等同于真实机器人执行原始 action $a$ 的下一状态。然后 policy optimization 在这个 grounded simulator 中进行；学到的 policy action $a$ 最终直接给真机。

最低标准对齐：

| 四支柱 | 本文必须回答的问题 |
|--------|--------------------|
| 逻辑与价值 | 为什么不调仿真器参数，而是在动作层修正？它相对 System ID / noise envelope 的 insight 是什么？ |
| 原理与理论 | GSL 的 trajectory distribution matching 如何变成 one-step dynamics matching？$f$ 和 $f^{-1}_{sim}$ 如何组成 $g$？$\alpha$ 为什么必要？ |
| 实验与验证 | SimSpark→Gazebo 与 SimSpark/Gazebo→NAO 的数字是否证明 action grounding 有效？真机样本量和仿真样本量分别是多少？ |
| 未来与结合 | 对 LinkerHand/WMTS，动作 grounding 可用于 actuator/latency compensation，但为什么 contact-rich dexterity 会突破 GAT 假设？ |

## 1. 问题设定与动机

### 1.1 一句话核心

GAT 用少量真实机器人转移数据学习“真实动作效果”和“仿真逆动作”之间的映射，把仿真器改造成一个 action-grounded simulator，使得在仿真中优化出来的 policy 更可能在真机上改善。

### 1.2 直观隐喻

如果仿真器是一架键感过轻的钢琴，真实机器人是一架键感滞后的钢琴，System ID 试图重新调琴，Domain Randomization 让你在各种琴上练，GAT 则是在练习室里给每次按键加一个变换器：你在练习室按“这个力度”，变换器会让练习室钢琴产生真实钢琴上同样的琴键响应。你练出来的手法仍是原手法，只是练习环境被改得更像现实。

这个隐喻的可证伪点是：如果真实转移无法由任何仿真动作复现，例如接触外力、摩擦卡滞、不可建模碰撞，那么动作变换器就无解。

### 1.3 现有方法的局限

| 方法 | 修正位置 | 注入的假设 | 局限 |
|------|----------|------------|------|
| Direct sim policy transfer | 无 | simulator 已足够准 | 真实动力学不同，policy 可能退化 |
| System Identification | 仿真器物理参数 | gap 可由少量参数解释 | 结构性误差、执行器延迟、接触模型错误可能不在参数化范围内 |
| Domain Randomization / noise envelope | 训练分布 | 学鲁棒 policy 比学准确 simulator 更容易 | 常得到保守策略，性能可能低于专门校准 |
| GUIDED GSL | grounding + 人工限制优化参数 | actions instantaneously achieve desired effect；人选哪些参数可变 | 需要专家干预，且关节响应假设太强 |
| GAT | action entering simulator | 对真实转移存在仿真等效动作 | 高维/接触下逆动作难学；状态分布 shift |

GAT 的 Delta：**不要求找到正确物理参数，而是要求对 policy 会访问的状态分布，仿真中存在一个替代动作能产生真实动作效果。** 这是更局部、更任务相关的 grounding。

### 1.4 论文贡献

1. 将 GSL 的 simulator grounding 实例化为 action transformation。
2. 用真实 forward model $f$ 和仿真 inverse model $f^{-1}_{sim}$ 构造可学习的 simulator modification。
3. 去掉 GUIDED GSL 中“动作即时达到目标角度”和“人类选择可优化参数”的限制。
4. 在 SimSpark→Gazebo 控制实验中证明 GAT 比 no grounding 和 noise envelope 更稳。
5. 在 SoftBank NAO 真机行走中，相对 UNSW hand-coded walk 提升 43.27%。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $E$ | real environment | 真实 NAO 或高保真 Gazebo surrogate | 否 | 目标物理世界 | SimSpark→Gazebo 实验中 Gazebo 被当作“real” |
| $E_{sim}$ | simulator | SimSpark/Gazebo | 否 | 学习发生的仿真环境 | GAT 修改的是进入 $E_{sim}$ 的 action，不是 $E$ |
| $P,P_{sim}$ | transition distributions | real/sim dynamics | 否 | 真实/仿真转移 | GSL 想让 trajectory distribution 更接近 |
| $\theta$ | 15 walk-engine parameters | CMA-ES policy search | 是，CMA-ES 分布更新 | NAO walk policy 参数 | policy 不是神经网络，而是 hand-coded walk engine 参数 |
| $s_t$ | full state | 理论定义 | 否 | $\langle x_t,\dot x_t,\ddot x_t,\omega_t,\psi_t\rangle$ | 真实观测不含全部速度/加速度，实际是 POMDP |
| $x_t$ | joint configuration | robot/sim sensors | 否 | 当前关节角 | 网络用历史 $x_t,\dots,x_{t-4}$ 估计隐藏动态 |
| $\omega_t$ | high-level intention | walk command | 否 | 例如 forward velocity request | 对 policy 来说是 state feature |
| $\psi_t$ | IMU + foot sensors | robot sensors | 否 | 稳定性/接触反馈 | GAT 模型主要针对 joint transition |
| $a_t$ | desired joint angles / changes | policy output | 否 | 原始 policy action | 最终真机执行的是 $a_t$，仿真中执行的是 $g(s_t,a_t)$ |
| $f(s_t,a_t)$ | predicted next configuration/effect | real forward model | supervised model | 预测真实执行 $a_t$ 后的效果 | 实现中预测 joint acceleration，再积分到下一状态 |
| $f^{-1}_{sim}(s_t,s_{t+1})$ | simulated inverse dynamics | supervised model from sim data | supervised model | 找到仿真中产生目标 next state 的动作 | 不是解析逆动力学，是神经网络近似 |
| $g(s_t,a_t)$ | transformed sim action | action transformation | 由两个模型组合 | grounded simulator 中真正执行的动作 | 方向是 real-effect → sim-equivalent action |
| $\alpha$ | smoothing coefficient | 手动选取 | 否 | 平衡 transformation 与原动作 | 设得尽可能高但保持 walk stable |
| $D_{robot},D_{sim}$ | trajectory transition datasets | rollouts | 否 | 训练 $f$ 和 $f^{-1}_{sim}$ | state distribution 来自当前 policy，换 policy 后会 shift |

### 2.2 GSL 从 trajectory matching 开始

GSL 假设有可修改 simulator：

$$
E_{sim}=\langle S,A,P_{sim},c\rangle,\qquad
P_\phi(\cdot\mid s,a)=P_{sim}(\cdot\mid s,a;\phi).
$$

理想 grounding 是找参数 $\phi$，让真实轨迹分布与仿真轨迹分布接近：

$$
\phi^*
=
\arg\min_{\phi}
\sum_{\tau\in D}
d\left(
P_r(\tau\mid\theta),
P_{sim}(\tau\mid\theta,\phi)
\right).
$$

这很难，因为 trajectory distribution 的误差会跨时间累积，而且物理 simulator 参数多、不可微、未必能表达真实 gap。

GAT 用 one-step dynamics surrogate 替代：

$$
\phi^*
=
\arg\min_\phi
\sum_{\tau_i\in D}\sum_{t=0}^{L}
d\left(
P(s^i_{t+1}\mid s^i_t,a^i_t),
P_\phi(s^i_{t+1}\mid s^i_t,a^i_t)
\right).
$$

直觉：先让每一步转移像真实，再希望 rollout trajectory 更像真实。这个 surrogate 不完美，但可用真实 transition data 监督学习。

### 2.3 GAT 如何构造动作变换

GAT 不把 $\phi$ 设为摩擦、质量、关节阻尼等物理参数，而是设为 action transformation function：

$$
g_\phi:S\times A\to A.
$$

它由两个模型组成：

1. 真实 forward model：

$$
f(s_t,a_t)\approx \arg\max_{x_{t+1}}P(x_{t+1}\mid s_t,a_t).
$$

2. 仿真 inverse model：

$$
f^{-1}_{sim}(s_t,x_{t+1})\approx
\arg\max_{a}
P_{sim}(x_{t+1}\mid s_t,a).
$$

组合后：

$$
g(s_t,a_t)
=
\alpha f^{-1}_{sim}(s_t,f(s_t,a_t))
+(1-\alpha)a_t.
$$

解释：

- $f(s_t,a_t)$：真实机器人执行原动作 $a_t$ 后预计会到哪里。
- $f^{-1}_{sim}$：在仿真中，要到同样的下一状态应该执行什么动作。
- $\alpha$：如果模型不准，完全替换动作会让 walk 不稳；平滑保留一部分原动作。

这就是 action-grounded simulator：policy 在仿真中仍输出 $a_t$，但 simulator 实际接收 $g(s_t,a_t)$。

### 2.4 实现细节

| 组件 | PDF 细节 | 为什么重要 |
|------|----------|------------|
| $f$ 和 $f^{-1}_{sim}$ 网络 | 3-layer NN，hidden sizes 200 和 180 | 当年足够表达 NAO joint response |
| $f$ 输入 | $s_t,a_t$ | 预测真实动作效果 |
| $f^{-1}_{sim}$ 输入 | $s_t,f(s_t,a_t)$ | 预测仿真替代动作 |
| action encoding | desired change in $x_t$，而非绝对 joint angle | 提高 prediction quality |
| forward target | joint acceleration | 比直接预测 $s_{t+1}$ 更稳定 |
| sine/cosine target + arctan output | 对 target angular acceleration 编码 | 保证输出合法角度范围 |
| state estimate | $x_t,\dots,x_{t-4},a_{t-1},\dots,a_{t-4}$ | 用历史隐式捕获 $\dot x_t,\ddot x_t$ 等不可观测变量 |
| optimizer | CMA-ES | 优化 15 个 walk engine 参数，无需梯度 |
| fall penalty | 轨迹中摔倒加 cost 15 | 避免只追速度导致不稳定 |

### 2.5 概念边界

GAT 与常见“动作残差部署器”不同。它不是部署时执行：

$$
a_{\mathrm{real}}=a+f_\theta(s,a).
$$

而是训练时修改 simulator：

$$
s_{t+1}^{sim}
\sim
P_{sim}\left(\cdot\mid s_t,g(s_t,a_t)\right)
\approx
P_{real}\left(\cdot\mid s_t,a_t\right).
$$

因此最终 policy $\theta$ 学到的是适合真实机器人执行的原始 action $a_t$。这个方向对 WMTS 很关键：如果我们要用 GAT 思想校准仿真训练环境，应把 transformation 放在 simulator/world model 内部，而不是默认部署时再包一个动作修正器。

## 3. 训练、数据与实验

### 3.1 平台与任务

| 项目 | 设置 |
|------|------|
| Robot | SoftBank NAO，25 DoF |
| Task | bipedal forward walking |
| Base walk | UNSW open-source ZMP/inverted-pendulum walk engine |
| Learnable policy | walk engine 的 15 个参数 |
| Action | desired joint angle/change |
| State features | joint config, high-level intention, IMU, foot sensors；实际 POMDP |
| Cost | negative average forward velocity；falls 加 penalty |
| Simulators | SimSpark (fast/lower fidelity), Gazebo (higher fidelity) |
| Optimize | CMA-ES |

### 3.2 SimSpark → Gazebo controlled experiment

这个实验用 Gazebo 作为“真实世界 surrogate”，比较三种方法：

| Method | Avg % Improve | Failures | Best generation |
|--------|---------------|----------|-----------------|
| No Ground | 11.094 | 7/10 | 1.33 |
| Noise-Envelope | 18.93 | 5/10 | 6.6 |
| GAT | 22.48 | 1/10 | 2.67 |

设置：

- 每个方法 10 trials。
- GAT 用 50 条 Gazebo trajectories 训练 $f$，50 条 SimSpark trajectories 训练 $f^{-1}_{sim}$。
- 每 trial 优化 10 generations。
- 每 generation 采样 150 policies，每个 policy 用 20 simulated trajectories 估计 $J_{sim}$。
- 每 trial 总计 30,000 simulated trajectories。

因果解释：

- No Ground 失败 7/10，说明在未 grounded 的 SimSpark 中优化很快 overfit 到 SimSpark dynamics。
- Noise-Envelope 比 No Ground 好，说明加噪可鼓励鲁棒 policy，但平均改进仍低于 GAT。
- GAT 失败仅 1/10，平均提升 22.48%，说明 action transformation 学到的不是随机鲁棒性，而是更贴近目标 dynamics 的局部修正。

### 3.3 Simulator → physical NAO

| Method | Velocity | Improvement |
|--------|----------|-------------|
| $\theta_0$ | 19.52 cm/s | 0.0 |
| GAT SimSpark $\theta_1$ | 26.27 cm/s | 34.58% |
| GAT SimSpark $\theta_2$ | 27.97 cm/s | 43.27% |
| GAT Gazebo $\theta_1$ | 26.89 cm/s | 37.76% |

设置：

- 初始真实数据 $D$：用 $\theta_0$ 在 physical NAO 上收集 15 trajectories。
- 每轮 CMA-ES 优化 10 generations。
- 每 generation 的 best policy 用 5 trajectories 在真机评估。
- 若 5 条中任一摔倒，则 policy 被视为 unstable。
- simulator 50Hz，physical NAO 100Hz；通过跳过每隔一个 measurement 得到等效 50Hz trace。
- 第一轮真机 trajectory 数约 65：15 条 grounding data + 10 generations × 5 evaluations。
- 第二轮用 $\theta_1$ 收集新的 15 trajectories reground，再优化，得到 $\theta_2$。

因果解释：

- 从 19.52 到 27.97 cm/s 的提升说明 GAT 不只是从弱 baseline 上优化；base 是 RoboCup SPL 中强 open-source walk。
- SimSpark 和 Gazebo 都能提升，说明方法不依赖单一 simulator。
- 第二轮 reground 从 34.58% 提升到 43.27%，直接验证 GSL 的迭代必要性：policy 改变后 state distribution 变了，需要重新 grounding。

## 4. 核心洞见

### 4.1 论文真正的 insight

GAT 的 insight 是：**sim-to-real gap 可以在“动作导致状态转移的接口”处被局部补偿，而不必先恢复全局真实物理参数。**

System ID 问“真实摩擦/阻尼/质量是多少？”  
GAT 问“在当前 policy 会访问的状态附近，真实执行这个 action 的效果，在仿真中要用什么 action 才能复现？”

后者更局部，因此样本需求可以低；也更任务相关，因此可能在某个 skill 上超过通用物理校准。

### 4.2 为什么有效

NAO 行走的主要 reality gap 包含关节响应延迟和执行器动态差异。SimSpark 中 action 几乎瞬时达到 desired command angle，真实 NAO 有 delay；Gazebo 介于两者之间。GAT 正好修的是 action → joint configuration transition，因此切中 bottleneck。

也就是说，GAT 成功不是因为动作层永远最好，而是因为 NAO walking 的主要 gap 恰好在 actuator/joint-response 层。

### 4.3 什么时候会失效

1. **不存在仿真等效动作**：真实接触被外力、摩擦卡滞、物体变形支配时，仿真中可能没有任何 $\hat a$ 能产生同样 $s'$。
2. **高维动作逆问题**：NAO walk engine 参数低维；对 16+5 DoF hand 或更高维 action chunk，$f^{-1}_{sim}$ 难度暴涨。
3. **状态分布 shift**：$f$ 和 $f^{-1}_{sim}$ 用旧 policy 数据训练；policy 优化后会访问新状态，模型可能失效。
4. **观测不完整**：真实状态含 $\dot x,\ddot x$，但机器人只观测部分；历史堆叠只是近似 belief，不保证充分。
5. **sensor gap 未修**：GAT 只修 action effect，不修真实传感器观测与仿真状态之间的差异。

## 5. 替代方案与理论局限

### 5.1 理论维度

GAT 的核心假设可以写成：

$$
\forall(s,a,s')\sim P_{real},\quad
\exists \hat a\in A
\quad
P_{sim}(s'\mid s,\hat a)\ \text{large}.
$$

也就是真实转移必须落在仿真 action-reachable set 内。对 actuator delay 这类 gap，这通常成立；对复杂接触、形变、摩擦粘滑、触觉不可见状态，这可能不成立。

### 5.2 算法维度

| 方法 | 优势 | 风险 |
|------|------|------|
| GAT | 少量真实数据，局部修 action-effect gap，不需改物理参数 | 依赖 inverse dynamics 可学；policy shift 后要 reground |
| System ID | 物理可解释，适合参数 gap | 无法表达结构性模型误差 |
| Domain Randomization | zero-shot，适合大规模 sim | 保守，性能可能牺牲 |
| Residual policy on real robot | 直接修部署动作 | 真机在线风险高，可能破坏稳定策略 |
| Neural dynamics model / actuator model | 可处理复杂状态依赖 | 训练成本高，需要更多数据和 uncertainty |

### 5.3 工程与实验维度

1. 真机任务只有 NAO walking，且 policy 是 15 维 walk-engine 参数，不是通用高维 neural control。
2. SimSpark→Gazebo 部分是 surrogate real-world 实验，不是真实机器人。
3. 真机评估每个候选 policy 只有 5 trajectories，虽然稳定 policy 方差小，但统计量有限。
4. $\alpha$ 需要调到“尽可能高但稳定”，仍有经验成分。
5. GAT 没有处理 sensor modification；作者自己提出这是 future work。

## 6. 对用户研究的启发

### 6.1 对 WMTS / LinkerHand 的迁移

GAT 对 WMTS 的价值是 actuator/dynamics grounding 的思想，而不是直接照搬 NAO action transform。

| GAT 概念 | WMTS 可替换版本 | 目的 |
|----------|----------------|------|
| $f(s,a)$ real forward model | LinkerHand real actuator/contact response model | 预测真实 command 后的关节/触觉/物体变化 |
| $f^{-1}_{sim}(s,s')$ sim inverse model | 仿真/世界模型中实现目标 transition 的 command inverse | 让 sim/world model 中的 action effect 更像真机 |
| $g(s,a)$ simulator action transform | grounded sim action wrapper / actuator correction layer | 在仿真训练时校正 action-effect gap |
| history $x_{t:t-4},a_{t-1:t-4}$ | tactile/proprio/action latency history | 捕获 actuator delay、摩擦、控制滞后 |
| $\alpha$ smoothing | residual gain / safety interpolation | 避免模型误差导致 unstable hand motion |

关键方向：对 LinkerHand，不应只学全局 $g(s,a)$。更合理是 joint-wise 或 contact-mode-conditioned grounding：

$$
g_i(h_t,a_i)
=
a_i+\Delta a_i(h_t,a_i,m_t),
$$

其中 $h_t$ 包含 joint history、tactile history、上一步 action、温度/电流/延迟估计，$m_t$ 是 contact mode 或 task phase。

### 6.2 可验证实验建议

1. **Actuator response grounding**  
   收集小幅随机 command，在真机和仿真中比较 $q_{t+1},\dot q_{t+1}$。训练 $f_{real}$ 和 $f^{-1}_{sim}$，验证 one-step transition error 是否下降。

2. **History length ablation**  
   比较只用 $(q_t,a_t)$、加入 4 步历史、加入 tactile/CAN latency belief。若历史显著降低误差，说明 gap 来自未观测动态。

3. **Contact-mode split**  
   分别在 free motion、light contact、firm contact、slip 中训练/评估 GAT。若 contact 中误差仍高，说明 action-only grounding 不足，需要 contact dynamics model。

4. **Policy transfer test**  
   在 grounded sim 中训练 PPO Oracle 或 diffusion policy，再部署真机，比较 no-grounding / domain randomization / actuator grounding。

5. **Distribution-shift audit**  
   学到新 policy 后重新收集 transitions，测试旧 $g$ 的 one-step error 是否上升。如果上升，必须做 DAgger-style reground。

### 6.3 不应过度外推的点

- GAT 的 43.27% 提升来自双足行走速度，不代表高维 dexterous manipulation 会同样样本高效。
- 它修的是 action-effect gap，不修 perception/tactile gap。
- 它假设仿真里存在等效 action；转笔中的滑移、碰撞、摩擦非线性可能违反这个假设。
- 它没有 uncertainty；对 WMTS 应与 ensemble world model 或 conservative gate 结合。

## 7. 与知识体系的联系

### 7.1 与 [[Dynamics]] 的联系

GAT 的数学链是：

$$
(s,a)\xrightarrow{f_{real}}s'_{real}
\xrightarrow{f^{-1}_{sim}}\hat a_{sim}
\xrightarrow{P_{sim}}s'_{sim}\approx s'_{real}.
$$

这其实是把动力学误差从 transition model 参数转移到 action preprocessor。对 actuator dynamics 和 latency，这是非常自然的分解。

### 7.2 与 [[ReinforcementLearning]] 的联系

GAT 仍然是 policy search/RL，只是优化环境被 grounded：

$$
\theta^*
=
\arg\min_\theta J_{sim,g}(\theta).
$$

它依赖仿真中的大量 policy evaluation：每 trial 30,000 simulated trajectories，而真机只用于少量 grounding/evaluation。这个样本分配模式与现代 world-model RL 的精神一致：把昂贵真实交互变成少量校准信号，把大规模优化放在模型中。

### 7.3 与 WMTS 的关系

WMTS 的 ensemble world model 线可以吸收 GAT 的一部分思想：不是只学 $P_{real}(s'\mid s,a)$，也可以学一个 action-grounding layer 让仿真/world model 的 action interface 更接近真机。

一个合理组合：

`real hand transitions → actuator/action grounding → grounded simulator/world model → PPO Oracle / Diffusion generalist training → ensemble uncertainty gate → real fine-tuning`

这会把 GAT 的局部动作修正，与 Part A 的 ensemble uncertainty、RL-100 的 real fine-tuning 连接起来。

## References

- Hanna and Stone, 2017. *Grounded Action Transformation for Robot Learning in Simulation*.
- Farchy et al., 2013. *Humanoid Robots Learning to Walk Faster: From the Real World to Simulation and Back*.
- Hansen, 2006. *The CMA Evolution Strategy*.
- Ross and Bagnell, 2012. *Agnostic System Identification for Model-Based Reinforcement Learning*.
