---
tags:
  - paper
  - reinforcement-learning
  - control-frequency
  - action-persistence
  - batch-RL
  - FQI
aliases:
  - PFQI
  - Persistent FQI
  - Action Persistence
read-date: 2026-01-31
venue: ICML 2020
paper-year: 2020
authors:
  - Alberto Maria Metelli
  - Flavio Mazzolini
  - Lorenzo Bisi
  - Luca Sabbioni
  - Marcello Restelli
institution: Politecnico di Milano
paper-pdf: "[[Papers/Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[SignalProcessing]]"
---

# Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning

> [!abstract] 核心贡献
> 本文把“控制频率”从一个通常手调的环境超参，形式化为 **action persistence**：同一个动作连续执行 $k$ 个基础决策步；由此构造 $k$-persistent MDP、证明 persistent Bellman operator 的 $\gamma^k$ 收缩性与性能损失界，并提出 PFQI 在同一批离线数据上估计不同 $k$ 的最优值函数，从而离线选择合适控制频率。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#2.3 估计价值的三种范式：DP → MC → TD（偏差-方差谱）|ReinforcementLearning §2.3]] — 本文的数学根是 Bellman operator、Fitted Q-Iteration、approximate value iteration error propagation；action persistence 不是额外 policy trick，而是改写 Bellman 备份的时间结构（把 $T^*$ 改成 $(T^\delta)^{k-1}T^*$）。
> - [[ControlTheory#1.3 频率响应：Bode、相位裕度与带宽|ControlTheory §1.3]] — $k$-persistent MDP 对应 zero-order hold：控制器每 $k\Delta t_0$ 更新一次，中间保持上一控制量；持续越久等效带宽越低。
> - [[SignalProcessing#1.1 采样与混叠：离散化不是无损记录|SignalProcessing §1.1]] — 动作保持等价于对 action signal 做低通/降采样；它抑制高频噪声，也会丢失快速接触事件（混叠/滞后）。
>
> **核心技术**: Action Persistence, $k$-Persistent MDP, Persistent Bellman Operator, PFQI, Offline Control-Frequency Selection

## 0. 阅读定位与范本价值

这篇论文不是“frame skip 有时有用”的经验论文。它真正的价值是把一个长期藏在实现里的选择写成可分析对象：

$$
\Delta t = k\Delta t_0,\qquad k\in\mathbb{N}_{\ge 1}.
$$

如果 $k=1$，agent 高频决策，策略空间最大，但单个动作对下一状态的影响可能太小，离线 FQI 难以从噪声里学出 action-value 差异；如果 $k$ 很大，动作效果清晰、样本复杂度下降，但策略被强行变成“长时间不改主意”，快速系统会失控。PFQI 的 insight 是：**控制频率不是纯工程 knob，而是 policy space 与 learning difficulty 的结构性 trade-off。**

最低标准映射：

| 四支柱 | 本文 recap 的落点 | 必须抓住的判断 |
|---|---|---|
| 逻辑与价值 | §1, §4 | 高频不是永远好；低频不是只是省算力；$k$ 改变的是 MDP 与 Bellman 备份 |
| 原理与理论 | §2 | 从连续时间/ZOH 到 base MDP，再到 $P^\delta$、$M_k$、$(T^\delta)^{k-1}T^*$，不能跳过算子顺序 |
| 实验与验证 | §3 | Table 1 的“中等/较高 persistence 常胜，过高 collapse”正好印证 policy-space vs sample-complexity |
| 未来与结合 | §5-§7 | 固定全局 $k$ 对灵巧手接触不够；WMTS 更该学状态依赖 $k(s)$ 或调度粒度 |

对你的 WMTS / LinkerHand 研究而言，这篇文章的地位像一个理论锚点：它不能直接解决高维连续动作和接触非光滑，但它给出了“任务调度粒度”如何进入 MDP、Bellman operator 和性能界的最干净版本。

## 1. 问题设定与动机

### 1.1 一句话核心

Action persistence 用一个整数 $k$ 控制“多久重新决策一次”：$k$ 越大，单个动作的效果越容易被离线 RL 看见，但可表达策略越少。

### 1.2 直观隐喻

把控制器想成给机器人发“方向盘指令”。高频控制像每一毫米都重新打方向盘：理论上最灵活，但每次动作的效果太小，离线数据里很难判断哪个动作更好。低频控制像打一把方向盘后保持一段时间：车身响应更明显，学习更容易；但如果前面突然有急弯，保持太久就冲出道路。

这个隐喻可证伪：若系统变化慢、动作效果被噪声淹没，则中等 $k$ 应优于 $k=1$；若系统需要快速纠错，则过大 $k$ 应崩掉。Table 1 正是这个形状。

### 1.3 现有路线的局限

| 方法/习惯 | 注入了什么先验 | 关键局限 |
|---|---|---|
| 固定环境 timestep | 认为 benchmark 给定频率就是合理频率 | 把控制频率当常量，无法解释为什么同一算法在不同 frame skip 下表现差异巨大 |
| 最高可用频率控制 | “更多控制机会一定更好” | 策略空间更大，但离线/值函数学习要区分 infinitesimal action effects，样本复杂度上升 |
| 手工 frame skip | 经验性重复动作 $k$ 帧 | 只给 heuristic，不说明它对应哪个 MDP、哪个 Bellman operator、何时会损失最优性 |
| Options / temporal abstraction | 用 temporally extended actions 表达技能 | 更一般，但语义通常是 subgoal/option；本文只研究“控制频率改变”这个窄问题，因此能给出更干净的理论 |
| Continuous-time RL / HJB | 从连续时间最优控制出发 | 理论强但通常需要模型或特殊离散化；PFQI 关注 batch RL 中如何用已有离散数据选频率 |

### 1.4 Delta 分析

本文的 Delta 不是“提出一个新的低通滤波器”，而是三层同时打通：

1. **理论层**：把重复动作写成 $P^\delta$ 与 $M_k=(S,A,P_k,R_k,\gamma^k)$，使 action persistence 成为一个新的 MDP，而不是 rollout trick。
2. **算子层**：证明 $T_k^\pi=(T^\delta)^{k-1}T^\pi$ 与 $T_k^*=(T^\delta)^{k-1}T^*$，保留收缩性。
3. **算法层**：PFQI 用同一批 persistence-1 数据估计多个 $k$ 的值函数，并用 estimated return 减 Bellman residual 惩罚来选 $k$。

它讲故事的方式很清楚：先承认高频控制的最优性优势，再指出学习算法面对有限数据时不一定吃得下这个策略空间，最后把“降频”从经验补丁升级为有 Bellman 语义的配置参数。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 符号/对象 | 空间/类型 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $\Delta t_0$ | positive time step | 环境离散化 | 否 | base MDP 的基础控制周期 | 不是论文要学的量；论文只在整数倍上搜索 |
| $k$ | $\mathbb{N}_{\ge 1}$ | 可配置超参 | 否 | action persistence，重复动作的步数 | 全局固定，不是状态依赖 $k(s)$ |
| $M=(S,A,P,R,\gamma)$ | MDP | base environment | 否 | persistence 1 的离散 MDP | $P$ 输出 next state；$P^\pi/P^\delta$ 输出 state-action |
| $\pi$ | Markov stationary policy | 学习/评估对象 | 可由值函数 greedy 得到 | 每到决策点选择 action | $k$-persistent policy 本身非 Markov、非 stationary |
| $P^\pi$ | kernel on $S\times A$ | 由 $P$ 与 $\pi$ 构造 | 否 | 下一状态后按 $\pi$ 重选动作 | 与 $P^\delta$ 只差“下一动作怎么来” |
| $P^\delta$ | kernel on $S\times A$ | 由 $P$ 与 Dirac action 构造 | 否 | 下一状态后保持同一动作 | $\delta$ 不是 discount，而是 Dirac/keep-action |
| $M_k$ | $(S,A,P_k,R_k,\gamma^k)$ | 推导构造 | 否 | 用普通 Markov policy 表示 persistence-$k$ 行为 | discount 必须是 $\gamma^k$ |
| $T^\delta$ | Bellman-like operator | 由 $P^\delta$ 构造 | 否 | 一步“保持动作”的备份 | 不做 max，不查询 policy |
| $T_k^\pi,T_k^*$ | operators | Theorem 3.1 | 否 | $k$-persistent Bellman expectation/optimal operator | 复合顺序是 $(T^\delta)^{k-1}T^\pi$，旧稿常写反 |
| $Q_k^*$ | bounded function on $S\times A$ | $T_k^*$ fixed point | PFQI 估计时可由函数逼近器表示 | $M_k$ 的最优 action-value | 不能直接与 $Q^*$ 混同；它在受限策略空间内最优 |
| $\hat T^*,\hat T^\delta$ | empirical operators | dataset $D$ | 否 | PFQI 中从样本估计 Bellman target | $\hat T^\delta$ target 是 $R_i+\gamma f(S_i',A_i)$，保持旧动作 |
| $B_k$ | scalar index | persistence selection heuristic | 否 | 估计回报 - Bellman residual penalty | 不是单纯选 $\hat J_k^\rho$ 最大；要惩罚值函数不可信 |

### 2.2 从连续时间控制到 base MDP

真实控制系统更自然地写成连续时间：

$$
\dot x(t)=f(x(t),u(t)).
$$

数字控制器无法每个实数时刻都改 $u(t)$，通常在采样时刻发指令，并在两个采样时刻之间保持该指令。这就是 zero-order hold：

$$
u(t)=a_n,\qquad t\in[n\Delta t,(n+1)\Delta t).
$$

若选择一个基础周期 $\Delta t_0$，就得到 base MDP $M_{\Delta t_0}$。一次 transition 表示：在 $[t,t+\Delta t_0)$ 内保持动作 $a$，系统演化到下一个状态。

本文的问题不是从所有连续 $\Delta t>0$ 里优化，而是限制在整数倍：

$$
\Delta t=k\Delta t_0.
$$

这样每个候选 $k$ 都可看作从同一个 base MDP 诱导出的新 MDP。这个限制很务实：硬件有最低通讯/控制周期，离线数据也通常按某个基础频率采集。

### 2.3 Policy view：为什么 persistence policy 不是普通 Markov policy

执行 $\pi$ with persistence $k$：

1. $t=0$ 时采样 $A_0\sim\pi(\cdot|S_0)$；
2. $A_1,\dots,A_{k-1}$ 都强制等于 $A_0$；
3. $t=k$ 时再查询 $\pi(\cdot|S_k)$。

所以诱导的 policy 是：

$$
\pi_{t,k}(B|H_t)=
\begin{cases}
\pi(B|S_t), & t\bmod k=0,\\
\delta_{A_{t-1}}(B), & \text{otherwise}.
\end{cases}
$$

这暴露了第一个关键点：如果站在原 MDP $M$ 里看，$\pi_{t,k}$ 需要记住上一动作 $A_{t-1}$，还需要知道当前 $t\bmod k$，因此它一般不是 Markov stationary policy。直接在标准 MDP 理论里处理它会很别扭。

### 2.4 Environment view：把 persistence 吸收到 MDP

为了恢复 Markov stationary policy 的分析便利，论文改从 environment view 看。

普通策略诱导的 state-action transition kernel 是：

$$
(P^\pi)(B|s,a)
=
\int_S P(ds'|s,a)\int_A\pi(da'|s')\delta_{(s',a')}(B).
$$

它表示：先按环境转移到 $s'$，再按策略重新采样 $a'$。

Persistent kernel 则是：

$$
(P^\delta)(B|s,a)
=
\int_S P(ds'|s,a)\delta_{(s',a)}(B).
$$

唯一差别是下一步 action 不是从 $\pi$ 来，而是 Dirac 到旧动作 $a$。这个小差别就是全篇理论的杠杆点。

由此定义 $k$-persistent MDP：

$$
M_k=(S,A,P_k,R_k,\gamma^k),
$$

其中

$$
P_k(B|s,a)=(P^\delta)^{k-1}P(B|s,a),
$$

$$
R_k(C|s,a)=
\sum_{i=0}^{k-1}\gamma^i\big((P^\delta)^iR\big)(C|s,a),
$$

对应的期望奖励为

$$
r_k(s,a)=
\sum_{i=0}^{k-1}\gamma^i\big((P^\delta)^ir\big)(s,a).
$$

无跳步解释：

- 第 0 步执行当前动作 $a$，得到 $r(s,a)$；
- 第 1 步仍执行 $a$，所以用 $P^\delta$ 推进 state-action，并得到 $\gamma(P^\delta r)(s,a)$；
- 一直累积到第 $k-1$ 步；
- $k$ 个 base step 后才允许下一次真正决策，因此 discount 从 $\gamma$ 变成 $\gamma^k$。

对偶性：

$$
\text{在 }M\text{ 中执行 }k\text{-persistent }\pi
\quad\Longleftrightarrow\quad
\text{在 }M_k\text{ 中普通执行 }\pi.
$$

### 2.5 Persistent Bellman operator：顺序是全篇最容易写错的地方

标准 Bellman operators：

$$
(T^\pi f)(s,a)=r(s,a)+\gamma(P^\pi f)(s,a),
$$

$$
(T^*f)(s,a)=r(s,a)+\gamma\int_S P(ds'|s,a)\max_{a'}f(s',a').
$$

Persistent operator：

$$
(T^\delta f)(s,a)=r(s,a)+\gamma(P^\delta f)(s,a).
$$

Theorem 3.1 给出：

$$
T_k^\pi=(T^\delta)^{k-1}T^\pi,\qquad
T_k^*=(T^\delta)^{k-1}T^*.
$$

这个顺序必须认真读：

| 视角 | 应如何读 |
|---|---|
| 执行时间 | 当前动作先保持 $k-1$ 个 transition，最后到下一个 decision boundary 才按 $\pi$ 或 $\max$ 决策 |
| 函数组合 | 右边的 $T^\pi/T^*$ 是最内层，表示 decision boundary 的 bootstrap；外层 $(T^\delta)^{k-1}$ 把这个 bootstrap 往当前状态动作对回传 |
| PFQI 计算 | 算法每 $k$ 次迭代先做一次 $\hat T^*$，再做 $k-1$ 次 $\hat T^\delta$，逐层构造 $(T^\delta)^{k-1}T^*$ |

旧稿里的 $T^\pi(T^\delta)^{k-1}$ 是错误顺序。它会把“先保持再决策”误读成“先决策再保持”，从而破坏 $M_k$ 与 PFQI 算法的对应关系。

因为 $M_k$ 的 discount 是 $\gamma^k$，所以 $T_k^\pi$ 和 $T_k^*$ 都是在 $L_\infty$ 范数下的 $\gamma^k$ contraction。这一点是 PFQI 能继承 value iteration 稳定性的理论根基。

### 2.6 性能损失界：低频为什么会伤最优性

由于 $k$-persistent policy 是受限策略类，最优性能不会超过 unrestricted policy：

$$
Q^*(s,a)\ge Q_k^*(s,a).
$$

论文先固定一个 policy $\pi$，分析 $Q^\pi$ 与 $Q_k^\pi$ 的差。Theorem 4.1：

$$
\|Q^\pi-Q_k^\pi\|_{p,\rho}
\le
\frac{\gamma(1-\gamma^{k-1})}{(1-\gamma)(1-\gamma^k)}
\left\|d^\pi_{\mathcal Q_k}\right\|_{p,\eta_k^{\rho,\pi}}.
$$

其中 $d^\pi_{\mathcal Q_k}$ 是 $P^\pi$ 与 $P^\delta$ 的 integral probability metric：

$$
d^\pi_{\mathcal Q_k}(s,a)
=
\sup_{f\in\mathcal Q_k}
\left|
\int_{S\times A} f(s',a')\big(P^\pi-P^\delta\big)(ds',da'|s,a)
\right|.
$$

直觉拆开：

- $P^\pi$ 表示到下个状态后重新选动作；
- $P^\delta$ 表示到下个状态后还拿旧动作；
- 如果“旧动作在近邻状态里仍然差不多好”，则二者差小；
- 如果系统快速变化或 policy 在相近状态下动作变化很大，则旧动作会迅速过期。

为了把这个抽象 discrepancy 变成可解释条件，论文引入 Time-Lipschitz Continuity：

$$
W_1(P(\cdot|s,a),\delta_s)\le L_T.
$$

它说的是：一个 base timestep 内，下一状态分布不能离当前状态太远。再结合 Lipschitz MDP 与 Lipschitz policy，可得到 Theorem 4.2 的结构：

$$
\left\|d^\pi_{\mathcal Q_k}\right\|_{p,\eta_k^{\rho,\pi}}
\le
L_{\mathcal Q_k}\big[(L_\pi+1)L_T+\sigma_p\big].
$$

四个因子分别对应：

| 因子 | 含义 | 对 persistence 的意义 |
|---|---|---|
| $L_{\mathcal Q_k}$ | value 函数族的 Lipschitz 上界 | 值函数越陡，旧动作造成的 value 差越大 |
| $L_\pi$ | policy 对 state 的敏感度 | 相近状态动作差很多，则保持旧动作危险 |
| $L_T$ | 环境每步演化速度 | 系统变化越快，降频损失越大 |
| $\sigma_p$ | 同一状态下 policy action dispersion | 随机 policy 的动作方差越大，保持某个 sampled action 越可能偏离平均策略 |

这也是本文对灵巧手接触任务最大的限制：接触发生/脱离时，状态转移不是平滑小变化；摩擦锥切换、碰撞冲量、stick-slip 都会破坏 TLC/Lipschitz 假设。

### 2.7 PFQI：用同一批离线数据估计不同 $k$

PFQI 的输入是 base MDP $M$ 中收集的数据：

$$
D=\{(S_i,A_i,S_i',R_i)\}_{i=1}^n,
$$

目标是在不重新采样的情况下，估计不同 $k$ 的 $Q_k^*$。

经验 Bellman operators：

$$
(\hat T^* f)(S_i,A_i)
=
R_i+\gamma\max_{a'}f(S_i',a'),
$$

$$
(\hat T^\delta f)(S_i,A_i)
=
R_i+\gamma f(S_i',A_i).
$$

PFQI(k) 的迭代机制：

| 迭代条件 | target | 含义 |
|---|---|---|
| $j\bmod k=0$ | $Y_i^{(j)}=(\hat T^*Q^{(j)})(S_i,A_i)$ | 到 decision boundary，允许对下一动作做 $\max$ |
| otherwise | $Y_i^{(j)}=(\hat T^\delta Q^{(j)})(S_i,A_i)$ | persistence 内部，下一动作强制仍是 $A_i$ |
| 每步之后 | $Q^{(j+1)}\in\arg\min_{f\in\mathcal F}\|f-Y^{(j)}\|_{2,D}^2$ | 投影回函数空间，FQI 风格回归 |

它不是旧稿里那种“把同一个 reward 重复加 $k$ 次”的简化 target。真正的 PFQI 通过交替 $\hat T^*$ 与 $\hat T^\delta$，用单步 transition 数据逐层逼近 $(T^\delta)^{k-1}T^*$。

计算复杂度的 insight：

$$
O\left(Jn\left(1+\frac{|A|-1}{k}\right)\right).
$$

原因是 $\hat T^*$ 需要对所有 action 做 max，$\hat T^\delta$ 只评估旧动作。$k$ 越大，昂贵的 max 发生得越少，所以 PFQI 的计算复杂度随 persistence 增大而下降。

误差传播上，论文把最终差距拆成两项：

$$
\|Q^*-Q_{\pi^{(J)}}^{(J)}\|_{p,\rho}
\le
\underbrace{\|Q^*-Q_k^*\|_{p,\rho}}_{\text{persistence 限制带来的最优性损失}}
+
\underbrace{\|Q_k^*-Q_{\pi^{(J)}}^{(J)}\|_{p,\rho}}_{\text{PFQI 学习误差}}.
$$

第一项随 $k$ 增大倾向变差；第二项在有限数据/有限迭代下可能随 $k$ 增大变好。这就是论文理论版的 trade-off。

### 2.8 Persistence selection：为什么不能只看 estimated return

如果已为每个 $k\in\mathcal K$ 训练出 $Q_k$，最想做的是选：

$$
k^*=\arg\max_{k\in\mathcal K}J_k^{\rho,\pi_k}.
$$

但 batch setting 不允许真实执行 $\pi_k$。直接用

$$
\hat J_k^\rho=\frac{1}{m}\sum_{i=1}^m V_k(S_0^i),\qquad
V_k(s)=\max_a Q_k(s,a)
$$

会受到 Q overestimation 的污染。Lemma 6.1 给出一个下界结构：

$$
J_k^{\rho,\pi}
\ge
J^\rho-\frac{1}{1-\gamma^k}\|T_k^*Q-Q\|_{1,\eta^{\rho,\pi}}.
$$

论文把不可计算项替换成数据上的 Bellman residual 估计，得到 practical index：

$$
B_k
=
\hat J_k^\rho
-
\frac{1}{1-\gamma^k}
\|\widetilde Q_k-Q_k\|_{1,D},
$$

其中 $\widetilde Q_k$ 通过把 PFQI(k) 再跑 $k$ 个额外 iteration 得到，近似 $T_k^*Q_k$。所以 $B_k$ 的意义是：**值函数说自己好，还必须通过一次 persistent Bellman consistency 检查。**

## 3. 训练、数据与实验

### 3.1 实验设置

论文用 ExtraTreesRegressor 作为主要回归器，参数为 `n_estimators=100, min_samples_split=5, min_samples_leaf=2`；每个环境从 base MDP 的数据出发，候选 persistence 为 $k\in\{1,2,4,8,16,32,64\}$。

| Environment | Action space | Sampling persistence | Original timestep | factor $m=\Delta t_{\text{original}}/\Delta t_0$ | Batch size $n$ | Iterations $J$ |
|---|---:|---:|---:|---:|---:|---:|
| Cartpole | $\{-1,1\}$ | 1 | 0.02 | 4 | 400 | 512 |
| Mountain Car | $\{-1,0,1\}$ | 8 | 1 | 2 | 20 | 256 |
| Lunar Lander | {Nop, left, main, right} | 1 | 0.02 | 1 | 100 | 256 |
| Pendulum | $\{-2,0,2\}$ | 1 | 0.05 | 1 | 100 | 64 |
| Acrobot | $\{-1,0,1\}$ | 4 | 0.2 | 4 | 200 | 512 |
| Swimmer | $\{-1,0,1\}^2$ | 1 | 2 frame-skip | 2 | 100 | 128 |
| Hopper | $\{-1,0,1\}^3$ | 1 | 1 frame-skip | 2 | 100 | 128 |
| Walker 2D | $\{-1,0,1\}^9$ | 1 | 1 frame-skip | 2 | 100 | 128 |

两个细节很重要：

- Mountain Car / Acrobot 的 sample collection 也用了较高 sampling persistence，说明 persistence 不只影响 evaluation，也影响 exploration distribution。
- 当原始 timestep 被缩小 $m$ 倍时，horizon 被放大 $m$ 倍，discount 按 $\gamma=(\gamma_{\text{original}})^{1/m}$ 调整，以保持相近 effective horizon。

### 3.2 主结果：中等 persistence 常胜，过高 persistence 崩溃

Table 1 核心结果如下，数值为最终 policy 在对应 $M_k$ 中的 estimated return，20 runs mean $\pm$ std。

| Environment | $k=1$ | $k=2$ | $k=4$ | $k=8$ | $k=16$ | $k=32$ | $k=64$ | selection loss $\delta$ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Cartpole | 169.9±5.8 | 176.5±5.0 | **239.5±4.4** | 10.0±0.0 | 9.8±0.0 | 9.8±0.0 | 9.8±0.0 | 0.0±0.0 |
| MountainCar | -111.1±1.5 | -103.6±1.6 | -97.2±2.0 | -93.6±2.1 | -94.4±1.8 | **-92.4±1.5** | -136.7±0.9 | 1.88±0.85 |
| LunarLander | -165.8±50.4 | -12.8±4.7 | **1.2±3.6** | **2.0±3.4** | -44.1±6.9 | -122.8±10.5 | -121.2±8.6 | 2.12±4.21 |
| Pendulum | **-116.7±16.7** | **-113.1±16.3** | -153.8±23.0 | -283.1±18.0 | -338.9±16.3 | -364.3±22.1 | -377.2±21.7 | 3.52±0.0 |
| Acrobot | -89.2±1.1 | **-82.5±1.7** | **-83.4±1.3** | -122.8±1.3 | -266.2±1.9 | -287.3±0.3 | -286.7±0.6 | 0.80±0.27 |
| Swimmer | 21.3±1.1 | **25.2±0.8** | **25.0±0.5** | 24.0±0.3 | 22.4±0.3 | 12.8±1.2 | 14.0±0.2 | 2.69±1.71 |
| Hopper | 58.6±4.8 | 61.9±4.2 | 62.2±1.7 | 59.7±3.1 | 60.8±1.0 | 66.7±2.7 | **73.4±1.2** | 5.33±2.32 |
| Walker 2D | 61.6±5.5 | 37.6±4.0 | 62.7±18.2 | 80.8±6.6 | **102.1±19.3** | 91.5±13.0 | **97.2±17.6** | 5.10±3.74 |

因果解释：

- **Cartpole**：$k=4$ 从 169.9 提到 239.5，但 $k\ge 8$ 直接跌到约 10，说明该任务有明确“甜点”：适度保持让动作效果明显，过度保持则无法及时扶杆。
- **LunarLander / Acrobot / Swimmer**：$k=1$ 很少是最好；中等 persistence 改善学习，符合“低频降低样本复杂度”的叙事。
- **Pendulum**：$k=1,2$ 接近，之后快速变差；这是系统需要连续稳定调节的例子，过大 $k$ 让控制太粗。
- **Hopper / Walker2D**：复杂 MuJoCo-like 任务反而偏好较高 $k$，说明在离散动作、有限 batch 的设置下，高频的策略空间优势未必能被 FQI 利用。
- **selection loss** 普遍远小于 return 尺度，说明 $B_k$ heuristic 通常能选到可用 persistence；但 Hopper/Walker2D 的 $\delta\approx5$ 也提醒：它不是严格模型选择定理。

### 3.3 Cartpole 曲线解释：为什么要惩罚 Bellman residual

Figure 2 拆开了 $B_k$ 的三个部分：

| 曲线 | 观察 | 机制 |
|---|---|---|
| true estimated return $\hat J_k^{\rho,\pi_k}$ | $k=4$ 是最优 | 适度 persistence 让动作效果可学习，又没丢掉扶杆所需反应速度 |
| value-estimated return $\hat J_k^\rho$ | $k=1,2$ 倾向 overestimate，$k=4$ 略 under-estimate | 小 $k$ 需要更频繁应用 $\hat T^*$，max over actions 带来 overestimation bias |
| residual $\|\widetilde Q_k-Q_k\|_{1,D}$ | 用来压低不自洽的 Q 估计 | 只看 $\hat J_k^\rho$ 会偏向乐观但不可靠的值函数 |
| index $B_k$ | 正确 rank $k=4,8$，但相对 $k=1$ 会高估 $k=8,16$ | heuristic 有效但不完美；它依赖 dataset distribution 与 Bellman residual 估计质量 |

这张图证明了论文的算法故事：PFQI 不是“哪个 Q 估得高就选哪个 $k$”，而是把“高 estimated value”与“Bellman consistency”放在同一个选择指标里。

### 3.4 Batch size 实验：为什么有限数据时 persistence 更有价值

Trading 环境中，状态包含过去 60 分钟价格差、上一 portfolio position 和剩余时间比例；动作是 long/short/flat，reward 为

$$
R_t=a_t(p_t-p_{t-1})-f|a_t-a_{t-1}|,
\qquad f=4\times10^{-5}.
$$

主文 Figure 3 改变 sampled trajectories 数量（如 $n=10,30,50,100,200,400$），观察到：

- 小 batch（$10,30,50$）时，$k=2,4,8$ 往往优于 $k=1$；
- batch 变大后，$k=1$ 重新变强；
- 因为市场数据噪声很大，低频 action persistence 像一种 temporal aggregation，让单个动作的收益信号更稳定。

这补上了 Table 1 之外的关键证据：persistence 的价值不是“物理上总该低频”，而是与数据量强相关。数据越少，降低策略空间/增强动作效果越有帮助；数据足够时，高频策略空间的上限重新显现。

### 3.5 Ablation 式因果链

论文没有传统 module ablation，但它的实验结构本身可读成机制验证：

| 改变 | 观察 | 因果链 | 对使用者的含义 |
|---|---|---|---|
| $k=1\to$ 中等 $k$ | 多数环境性能上升 | 动作连续执行后，单个 action 的 state/reward effect 更可辨认，FQI target 噪声相对降低 | 离线数据少或执行延迟大时，应把控制频率纳入搜索 |
| 中等 $k\to$ 过大 $k$ | Cartpole / Pendulum / Acrobot 崩溃 | 策略空间被限制成“长时间不能纠错”，快速 dynamics 无法补偿 | 接触瞬间、平衡任务不能盲目 action chunking |
| 只看 estimated value | 小 $k$ overestimate | 高频需要更多 $\hat T^*$ max，max bias 累积 | 选 $k$ 时要做 consistency check，不然会偏向乐观 Q |
| 减小 batch size | persistence 更有利 | 数据少时估计误差大，降低频率相当于降低有效决策复杂度 | WMTS 早期少量真机数据阶段可先低频，再逐步升频 |

## 4. 核心洞见

### 4.1 论文真正的 insight

Action persistence 的本质不是“让动作平滑”，而是：

$$
\text{control frequency}
\quad\Longrightarrow\quad
\text{MDP transition/reward/discount}
\quad\Longrightarrow\quad
\text{Bellman operator}
\quad\Longrightarrow\quad
\text{learnability}.
$$

很多论文只在第一步停住，把 frame skip 当 engineering trick；PFQI 把它一路推到 Bellman operator，因此能讨论 contraction、performance loss、error propagation 和 offline selection。

### 4.2 为什么这个设计有效

它有效依赖两个前提：

1. **局部时间平滑**：短时间内状态不会远离当前 state，旧动作在近邻 state 仍大致合理；
2. **有限数据学习受限**：高频策略空间虽然包含更优策略，但 FQI/函数逼近器未必能从 batch 中学出来。

如果这两个前提成立，降低频率是一种结构化正则：它牺牲一部分 policy class，换更低的估计难度。

### 4.3 什么时候会失效

| 失效条件 | 为什么破坏 PFQI 叙事 |
|---|---|
| 接触/碰撞非光滑 | $L_T$ 与 Lipschitz transition 假设失效，旧动作可能从“合理”瞬间变成“灾难” |
| 任务需要快速反馈 | 大 $k$ 强制 open-loop 片段，无法在关键状态纠错 |
| 高维连续动作未离散化 | PFQI 的 $\max_{a'}$ 与复杂度分析基于 finite action；连续 dexterous hand 不能直接套算法 |
| dataset coverage 不足 | 用 persistence-1 数据估计 $(P^\delta)^{k-1}$ 会累积 extrapolation error |
| policy 本身强随机 | $\sigma_p$ 大，保持一次 sampled action 与 policy 平均行为差异大 |

## 5. 替代方案与理论局限

### 5.1 理论维度

本文性能界依赖 Lipschitz MDP、Lipschitz policy 和 Time-Lipschitz Continuity。对灵巧手转笔，最危险的是接触切换：

$$
M(q)\ddot q+C(q,\dot q)\dot q+g(q)=\tau+J_c(q)^T\lambda,
$$

其中 $J_c,\lambda$ 会随接触模式突变。接触模式一变，$P(\cdot|s,a)$ 不再只是当前分布附近的小 Wasserstein 移动；这时 $O(k\Delta t_0)$ 型直觉可能低估风险。

### 5.2 算法维度

| 替代/后续路线 | 优点 | 相对 PFQI 的代价 |
|---|---|---|
| [[Elastic Time Step Reinforcement Learning, VTS-RL|VTS-RL]] | 状态依赖时间步 $\Delta t(s)$，比全局 $k$ 灵活 | 理论保证弱，不像 PFQI 有 clean contraction/selection 分析 |
| [[TARC - Time-Adaptive Robotic Control|TARC]] | 学习 time-adaptive controller，贴近机器人部署 | 需要处理可变时间折扣与稳定性 |
| [[Reinforcement Learning for Control with Multiple Frequencies]] | 不同 action dimension 可用不同频率 | 更适合多关节系统，但仍多为固定分配 |
| Options / SMDP | temporal abstraction 更一般 | 容易混入语义技能，失去“控制频率”这个窄变量的清晰分析 |
| PPO / SAC + action repeat sweep | 工程上容易 | 没有离线 Bellman selection 指标，常变成 expensive hyperparameter search |

PFQI 的局限不是它“不够深”，而是它为了理论干净牺牲了三个东西：连续动作、状态依赖频率、接触非光滑。

### 5.3 工程/实验维度

- 实验动作空间被离散化为 $\{-1,0,1\}^d$ 等集合；LinkerHand 16+5 DoF 连续命令不能直接离散成这种规模。
- $k$ 是全局固定，真实 manipulation 明显有 phase：接近、接触建立、滚动/转动、释放，每段最佳频率不同。
- 论文评估主要是仿真/benchmark，没有真实通讯延迟、CAN 总线拥塞、低层控制器 saturate 等硬件因素。
- PFQI 依赖 batch 数据覆盖；若 persistence 改变后访问到 dataset 稀疏区域，Bellman residual 可能无法完全识别 extrapolation。

## 6. 对用户研究的启发

### 6.1 对 LinkerHand / WMTS 的直接迁移

对 LinkerHand，action persistence 不应只理解成“策略输出每 $k$ 步 repeat”。它对应至少三层硬件/算法事实：

| 层级 | $k$ 对应什么 | 对 WMTS 的意义 |
|---|---|---|
| 通讯层 | CAN 1Mbps 与多电机通讯造成的最小有效更新周期 | sim 中不能假设无限高频可执行；应显式建模 $k_{\min}$ 或 latency |
| 控制层 | PD target / position command 的 zero-order hold | action chunk length 是低层控制接口的一部分 |
| 策略层 | PPO / Diffusion / WMTS 多久重新规划动作 | 调度粒度本身是 task scheduler 的输出，不只是 actor 的固定超参 |
| world-model 层 | rollout 使用的 temporal abstraction | ensemble WM 可预测“保持当前 action $k$ 步”的风险/收益 |

因此 PFQI 给 WMTS 的真正启发是：把 $k$ 作为 **scheduler decision variable**，而不是在训练脚本里固定。

### 6.2 状态依赖 $k(s)$：PFQI 固定 $k$ 到 WMTS 的升级

转笔/灵巧手接触过程天然需要不同频率：

| Phase / state cue | 建议 $k(s)$ | 原因 |
|---|---:|---|
| 手指远离物体、空中接近 | 4-8 | 接触风险低，低频减少探索复杂度与动作抖动 |
| 即将接触、触觉激活前后 | 1-2 | 接触模式即将切换，TLC 假设最脆弱，需要高频纠错 |
| 稳定滚动/持续施力 | 2-4 | 保持动作有利于形成连续力，避免高频策略 jitter |
| 物体滑移/掉落风险升高 | 1 | 安全优先，立刻恢复高频闭环 |
| 释放/抛接类高速相位 | 1 或模型预测触发 | 开环保持可能可用，但必须由 world model 预测风险 |

这就是 PFQI 的局限反过来形成 WMTS 的 project insight：**PFQI 提供全局固定 $k$ 的理论下界；WMTS 应贡献状态依赖 $k(s)$ 的可学习调度，并尽量恢复部分保证。**

### 6.3 可验证实验建议

一个不浮夸、可直接做的实验：

| 实验项 | 设计 |
|---|---|
| 数据 | Isaac Gym / real replay 中按最高可执行频率采集 $(s_t,a_t,r_t,s_{t+1})$ |
| 固定 baselines | PPO/DP with $k\in\{1,2,4,8,16\}$ action repeat |
| 自适应 baseline | phase-conditioned 或 tactile-triggered $k(s)$ |
| 指标 | success rate、掉笔率、contact slip count、action jerk、torque/temperature、real latency violation |
| falsifier | 如果 $k=1$ 在少数据和真机延迟下仍全面最优，则“降频改善 learnability/robustness”在该硬件上不成立 |
| WMTS 增强 | ensemble WM 预测每个 candidate $k$ 的 return 与 uncertainty，选 LCB 最优的 $k$ |

这比“把 PFQI 直接搬到灵巧手”更合理。PFQI 的 finite-action FQI 不适合直接套进 21-DoF 连续控制，但它的 **operator view + selection view** 可以迁移到 PPO Oracle、Diffusion action chunk 和 world-model scheduler。

### 6.4 与 LaST0 / fast-slow control 的关系

LaST0 类 fast-slow latent reasoning 可以理解为在 representation / reasoning 层面引入不同时间尺度；PFQI 则在 action execution 层面给出最小理论模型。

二者结合时要避免一个坑：不要只让 VLA/VLM 慢思考，而底层动作仍以固定 chunk 粗暴执行。更好的结构是：

$$
\text{latent slow plan}
\to
\text{WM predicts candidate }k
\to
\text{fast controller executes with contact-triggered override}.
$$

也就是说，fast-slow 不只是 token/latent 的层级，还应该落到控制频率与安全 override 上。

### 6.5 不应过度外推的点

- 不要把 $k=4$ 当通用答案；Cartpole 的 $k=4$ 是该环境/数据/算法组合下的结果。
- 不要把 action persistence 当作真实 actuator dynamics model；它只能表达 zero-order hold，不能表达 backlash、dead zone、temperature drift、current saturation。
- 不要认为低频一定更 sim-to-real；低频能减少高频噪声，但也会错过触觉瞬变。
- 不要用旧稿那种简化 target 实现 PFQI；真正的关键是 $\hat T^*$ 与 $\hat T^\delta$ 的交替备份。

## 7. 与知识体系的联系

### 7.1 与 [[ReinforcementLearning]] 的联系

本文是 value-based RL 中“时间粒度改变 Bellman operator”的范例：

$$
T^*
\quad\longrightarrow\quad
T_k^*=(T^\delta)^{k-1}T^*.
$$

它提醒所有 offline RL / FQI / FQE 系统：环境 wrapper 的 frame skip 不是中性改动，会改变 transition、reward accumulation、discount 和 error propagation。对 WMTS，任何 action chunking 都必须在 value estimation 里同步体现。

### 7.2 与 [[ControlTheory]] 的联系

Control theory 里，zero-order hold 是数字控制器的基础：

$$
u(t)=a_n,\quad t\in[nk\Delta t_0,(n+1)k\Delta t_0).
$$

PFQI 相当于把 ZOH 的 sampling period 从控制器实现细节提升为 MDP 参数。这个视角非常适合真实机器人：控制频率不是纯算法选择，还受通讯、执行器、低层控制器和传感器刷新率共同约束。

### 7.3 与 [[SignalProcessing]] 的联系

Action persistence 对动作序列有低通效果。若 base action sequence 是 $a_t$，执行后实际 action 是 piecewise constant 的 staircase signal。它会：

- 抑制策略高频抖动；
- 降低 action bandwidth；
- 在接触瞬变时产生 aliasing/滞后。

因此它与 sampling theorem 的关系不是“$f_c=f_s/2k$ 这么简单”，而是一个控制闭环问题：被低通的是 action，受影响的是 state trajectory 与 reward，不是离线信号重建。

### 7.4 Control frequency / time-step 簇定位

| 论文 | 频率机制 | 固定/自适应 | 理论保证 | 在簇中的角色 |
|---|---|---|---|---|
| 本文 PFQI | action persistence $k$ | 全局固定，离线选择 | 强：contraction + loss bound + error propagation | 理论锚点 |
| [[Elastic Time Step Reinforcement Learning, VTS-RL|VTS-RL]] | 可变时间步 $\Delta t(s)$ | 状态依赖 | 弱 | 灵活性端点 |
| [[TARC - Time-Adaptive Robotic Control|TARC]] | time-adaptive robotic controller | 状态依赖 | 弱 | 机器人部署端点 |
| [[Reinforcement Learning for Control with Multiple Frequencies]] | 不同 action component 多频率 | 多变量固定/半固定 | 中 | 高维系统分解 |
| [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks|EvoControl]] | 高频底层 + 低频进化/上层 | 分层 | 弱 | 绕过梯度信用分配 |

簇级 insight：PFQI 是“全局固定 + 强保证”，后续方法多走向“状态依赖 + 弱保证”。WMTS 的潜在贡献点就是补上缺角：

$$
\text{state-dependent control frequency}
+
\text{world-model uncertainty}
+
\text{some form of performance/safety guarantee}.
$$

## 8. 应主动追问的颗粒度

| 用户式追问 | recap 应主动补充 |
|---|---|
| “为什么重复动作能写成一个 MDP？” | 从 $\pi_{t,k}$ 非 Markov 出发，引入 $P^\delta$，再构造 $M_k$ |
| “$T_k^*$ 的顺序到底是什么？” | 明确 $T_k^*=(T^\delta)^{k-1}T^*$，说明函数组合与执行时间的读法 |
| “为什么低频会帮助学习？” | 用 $\|Q^*-Q_k^*\|+\|Q_k^*-Q_{\pi^{(J)}}\|$ 的 trade-off 解释 |
| “实验如何证明故事？” | 指出中等 $k$ 常优、过大 $k$ collapse、小 batch 更偏好 persistence |
| “怎么用于我的灵巧手？” | 不直接套 PFQI；把 $k$ 变成 WMTS scheduler 的状态依赖动作，并用 tactile/contact 触发高频 override |

## References

- Metelli, A. M., Mazzolini, F., Bisi, L., Sabbioni, L., & Restelli, M. **Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning**. ICML 2020.
- [[ReinforcementLearning]]
- [[ControlTheory]]
- [[SignalProcessing]]
- [[Elastic Time Step Reinforcement Learning, VTS-RL]]
- [[TARC - Time-Adaptive Robotic Control]]
- [[Reinforcement Learning for Control with Multiple Frequencies]]
- [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks]]
