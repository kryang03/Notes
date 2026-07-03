---
tags:
  - paper
  - model-based-rl
  - dexterous-manipulation
  - world-model
  - mpc
  - uncertainty
aliases:
  - PDDM
  - Deep Dynamics Models
  - Online Planning with Deep Dynamics Models
paper-year: 2019
read-date: 2026-06-25
venue: CoRL 2019
paper-pdf: "[[Papers/Deep Dynamics Models for Learning Dexterous Manipulation.pdf]]"
related:
  - "[[Dynamics]]"
  - "[[Optimization]]"
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
---

# Deep Dynamics Models for Learning Dexterous Manipulation

> [!abstract] 核心贡献
> PDDM 把 bootstrap ensemble dynamics、reward-weighted MPC/MPPI 和 temporally filtered action sampling 拼成一个能在 24-DoF Shadow Hand 上用约 4 小时真实数据学习 Baoding balls 的 model-based RL 系统；它的价值不在“神经网络学动力学”这句泛泛表述，而在证明高维接触灵巧操作可以通过**短 horizon 模型预测 + 每步重规划 + 不确定性降风险**获得样本效率。

> [!tip] 与理论基础的关联
> - [[Dynamics]] — 学的是 residual/forward transition model：$s_{t+1}\approx s_t+f_\theta(s_t,a_t)$，用数据替代显式接触方程。
> - [[Optimization]] — reward-weighted refinement 是熵正则轨迹分布优化/MPPI 的采样近似；CEM 是其 hard elite 特例。
> - [[ReinforcementLearning]] — model-based RL 把 sparse return 优化拆成 dense transition supervision + online planning。
> - [[StochasticProcess]] — bootstrap ensemble 近似 $p(\theta\mid\mathcal{D})$，disagreement 是 epistemic uncertainty proxy，而不是完整 aleatoric contact noise。
>
> **核心技术**: Bootstrap Ensemble Dynamics, PDDM-MPC, Reward-Weighted Refinement, Beta-Filtered Action Noise, Receding-Horizon Planning

## 0. 阅读定位与范本价值

这篇论文在你的知识库里有两个位置。

第一，它是 **dexterous world model / learned dynamics** 的早期硬证据：不是在低维 MuJoCo benchmark 上说 model-based RL 样本效率高，而是把 deep dynamics model 推到 24-DoF Shadow Hand、free-floating Baoding balls、handwriting 这种接触切换密集任务。它给 WMTS 的启发非常直接：world model 的首要用途未必是端到端生成动作，而是做短 horizon 评估、失败边界发现、uncertainty-aware task sampling。

第二，它也是一个反面边界：PDDM 没有 amortized policy、没有视觉/触觉统一 latent、没有显式安全约束、没有长 horizon sparse-reward abstraction。它能学 90°/180° Baoding balls，但方式是昂贵在线 MPC；对 LinkerHand L25 的转笔，不能照搬成部署控制器，只能借它的 ensemble uncertainty、short-horizon evaluator、planner-as-teacher 思想。

| 四支柱 | 本文需要回答的硬问题 | 本 recap 落点 |
|---|---|---|
| 逻辑与价值 | 为什么 2019 年还要在灵巧手上做 model-based RL？ | §1：model-free 样本贵、解析接触模型不可扩、高维随机射击失效 |
| 原理与理论 | PDDM 从 MDP、MLE、Bayesian ensemble、MPPI 怎样一步步来？ | §2：变量表、MLE→MSE、posterior ensemble、CEM→reward weighting、AR(1) filter |
| 实验与验证 | 哪些数字/趋势证明“组合是 critical”？ | §3：task/reward/hyperparameter 表、Fig.4 因果消融、Fig.5-9 主结果 |
| 未来与结合 | 它对 WMTS/DNPM 是组件、教师还是反例？ | §5-§7：ensemble-LCB、planner teacher、tactile/contact gap、与 DexNDM/FOWM/MoDem-V2 的演进 |

## 1. 问题设定与动机

### 1.1 一句话核心

PDDM 的一句话核心是：**把“学习灵巧操作策略”改写成“学习局部接触动力学，然后每个真实时间步重新规划一小段动作序列”**，从而用 dense transition supervision 获得样本效率，用 MPC 的闭环重规划抵消 learned model 的长期误差。

这里的关键不是 model-based RL 这个标签，而是这个改写把难题从：

$$
\max_\pi \mathbb{E}_\pi\left[\sum_t r(s_t,a_t)\right]
$$

变成两个较可控的问题：

1. 用每条真实 transition 训练 $\hat{p}_\theta(s_{t+1}\mid s_t,a_t)$；
2. 在当前 $s_t$ 上只规划 $H$ 步，执行第一步后立刻重算。

对接触任务来说，这个拆分非常重要：接触模式切换导致长期 open-loop prediction 快速发散，但短 horizon 内的局部 transition 仍可学。

### 1.2 直观隐喻

PDDM 像一个“每一步都重画 7 步小地图的盲人探路器”：

- dynamics model 是短距离地图，不保证远方准确；
- ensemble disagreement 是地图上“我不确定这里有没有坑”的阴影；
- reward-weighted MPC 是在阴影地图上试很多条小路；
- beta-filtered noise 让小路像手部动作而不是白噪声抖动；
- receding horizon 让它走一步看一步，避免把 1000 步未来一次性押在错误地图上。

这个隐喻的可证伪点是：如果任务需要 long-horizon sparse reasoning、离散模式选择或高维视觉语义，单靠 7 步短地图就不够；PDDM 会变成局部贪心或被模型 hallucination 诱骗。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 在本文任务上的关键局限 |
|---|---|---|
| 解析接触规划 / motion cones | 显式几何、摩擦锥、接触模式枚举 | 接触组合随手指数指数增长；Baoding balls 两个自由物体互相碰撞，模式枚举不可扩 |
| Model-free RL: NPG/SAC/MBPO | 直接学 $\pi(a\mid s,g)$ 或 value，不需要模型 | 样本效率低；多目标 handwriting / 8-goal reorientation 容易陷入 task-specific local optimum |
| Demonstration-based dexterity | 人类/专家轨迹提供 policy scaffold | 需要演示；PDDM 的目标是无演示、纯交互学习 |
| 早期 NN dynamics + random shooting MPC | 学 $f_\theta$，用随机 action sequence 做 MPC | $H\times d_a$ 搜索空间太大；高维手部动作独立采样导致抖动轨迹，几乎不产生协调接触 |
| CEM / hard elite MPC | 用 top-$J$ elite 更新动作分布 | hard top-k 丢弃排序信息；容易过早收缩到局部动作模式 |
| PETS / ensemble model-based RL | 不确定性传播 + ensemble dynamics | 在本文 dexterous task suite 上仍不够；缺少 PDDM 对高维动作序列的 filtered sampling + soft reward weighting 组合 |

### 1.4 Delta 分析

PDDM 的 delta 不是“用了 ensemble”或“用了 MPC”这样孤立的模块增量，而是三个约束同时成立：

1. **高容量 dynamics model 必须配 epistemic uncertainty**：2x500 MLP 足够拟合复杂接触，但小数据时会自信外推；ensemble 是允许高容量模型被早期使用的保护层。
2. **高维动作搜索必须配 temporal prior**：24-DoF hand、$H=7$ 时独立随机序列维度是 $168$；beta filter 把动作序列从逐步白噪声改成低通过程。
3. **planner update 必须避免 hard elite 早熟**：reward-weighted update 利用所有 sample 的相对排序，比 random shooting 和 CEM 更适合窄成功流形。

因此，论文故事讲得好的地方在于：它没有宣称某个单一技巧神奇有效，而是通过 Fig.4 把 model capacity、ensemble、horizon、controller、reward-weighting 一排拆开，证明“组合 critical”。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $s_t$ | task-dependent state；Valve 21, Reorientation 46, Handwriting 48, Baoding 40 | 真实系统/仿真观测 | rollout 中 detached | 手、物体、目标相关状态 | 本文不是 pixel dynamics；真机 Baoding 用视觉 tracker 给 3D ball position |
| $a_t$ | task-dependent action；Valve 9, others 24 | MPC 输出后执行 | 对执行而言无梯度 | hand command，归一化到 $[-1,1]$ | planner 10 Hz，底层 position controller 1 kHz zero-order hold |
| $s_{t+1}$ | next state | 真实 rollout label | detached | dynamics supervision label | 每条 transition 都是监督信号，区别于 policy-gradient 的 episode-level credit assignment |
| $f_{\theta_i}(s,a)$ | state delta / next-state mean | 第 $i$ 个 dynamics network | 训练 dynamics 时带梯度 | learned local transition | 文中写 $\hat{s}_{t+1}=f_\theta(\hat{s}_t,a_t)+\hat{s}_t$，即常见 residual dynamics |
| $\Sigma$ | covariance | 模型参数/固定超参 | 可学习但论文称非必要 | conditional Gaussian uncertainty | 不等于 ensemble disagreement；一个是 output noise，一个是 weight posterior proxy |
| $\mathcal{D}$ | replay dataset of transitions | 所有已执行轨迹 | detached | model training data | off-policy data 全可用，这是样本效率来源 |
| $\theta_i$ | ensemble model weights | 随机初始化 + 不同 mini-batch | dynamics training 中带梯度 | 近似后验样本 | bootstrap resampling 在 deep nets 中被论文认为非必要；这是近似，不是严格 Bayesian posterior |
| $A^{(k)}=(a_0^{(k)},...,a_{H-1}^{(k)})$ | $H\times d_a$ action sequence | MPC 采样 | 无梯度采样变量 | 候选未来动作序列 | time index 是 planner horizon，不是真实 episode 的全局时间 |
| $R_k$ | scalar predicted return | ensemble rollout + reward | 无梯度用于采样权重 | 候选序列分数 | 论文用 ensemble mean reward；不是显式 LCB/pessimism |
| $\mu_t$ | action distribution mean at horizon index $t$ | reward-weighted update | 无梯度 | 下一轮采样中心 | $\mu_t$ 是 horizon slot 的均值，不是 policy network mean |
| $\gamma$ | reward-weighting factor | controller hyperparameter | 无梯度 | softmax inverse temperature | 与 RL 折扣 $\gamma$ 不同；本文 $\gamma=20$ for Baoding |
| $\beta$ | filter coefficient | controller hyperparameter | 无梯度 | temporal smoothing / AR(1) noise strength | $\beta=1$ 近似独立白噪声；$\beta$ 太小会丢控制权 |
| $H,N,M,E$ | horizon, sample count, refinement iters, model epochs | controller/training hyperparameters | 无梯度 | planning/training budget | 本文 $H=7,M=3,E=40$；$E$ 也可指 ensemble size in prose，需看上下文 |

### 2.2 从 MDP 到 model-based RL：为什么 transition supervision 更省数据

从标准 MDP 开始：

$$
\mathcal{M}=(\mathcal{S},\mathcal{A},p,r,\rho_0),\quad s_{t+1}\sim p(\cdot\mid s_t,a_t)
$$

目标是最大化期望回报：

$$
J(\pi)=\mathbb{E}_{s_0\sim\rho_0,a_t\sim\pi,s_{t+1}\sim p}
\left[\sum_{t=0}^{T-1} r(s_t,a_t)\right].
$$

Model-free RL 直接优化 $\pi$ 或 $Q^\pi$，一条轨迹主要通过 return/advantage 反向给动作分配信用。PDDM 改走 model-based route：

$$
p(s_{t+1}\mid s_t,a_t)\quad \text{unknown}
\quad\Rightarrow\quad
\hat{p}_\theta(s_{t+1}\mid s_t,a_t)\quad \text{learned from data}.
$$

每次真实执行得到三元组：

$$
(s_t,a_t,s_{t+1})\in\mathcal{D}.
$$

这条 transition 本身就是监督学习样本，不需要等 episode 成功或失败。因此 PDDM 的样本效率来自一个非常朴素的统计事实：**每个真实时间步都提供一个 dense dynamics label**。

### 2.3 Gaussian dynamics MLE：从 log-likelihood 到 MSE

论文把 dynamics 写成条件高斯：

$$
\hat{p}_{\theta_i}(s'\mid s,a)=
\mathcal{N}\left(s';\,s+f_{\theta_i}(s,a),\,\Sigma_i\right).
$$

这里把 $s+f_{\theta_i}(s,a)$ 写出来，是为了强调它常按 residual dynamics 预测 state delta，而不是从零预测完整状态。对一个样本 $(s,a,s')$，负对数似然为：

$$
-\log \hat{p}_{\theta_i}(s'\mid s,a)
=
\frac{1}{2}(s'-s-f_{\theta_i}(s,a))^\top\Sigma_i^{-1}(s'-s-f_{\theta_i}(s,a))
+\frac{1}{2}\log|\Sigma_i|
+C.
$$

如果 $\Sigma_i=\sigma^2 I$ 固定：

$$
-\log \hat{p}_{\theta_i}(s'\mid s,a)
=
\frac{1}{2\sigma^2}\|s'-s-f_{\theta_i}(s,a)\|_2^2+C',
$$

所以最大似然等价于最小化 MSE。附录也确认证文实现使用 standard MSE supervised loss，而不是复杂 probabilistic loss；这点很关键，因为 PDDM 的主要不确定性不是靠 learned $\Sigma$，而是靠 ensemble。

### 2.4 Ensemble posterior：为什么它是 epistemic proxy，不是完整不确定性

理想 Bayesian dynamics prediction 是：

$$
p(s'\mid s,a,\mathcal{D})
=
\int p(s'\mid s,a,\theta)p(\theta\mid\mathcal{D})d\theta.
$$

这个积分不可直接算。Bootstrap ensemble 用 $E$ 个模型近似：

$$
p(s'\mid s,a,\mathcal{D})
\approx
\frac{1}{E}\sum_{i=1}^{E}
\mathcal{N}\left(s';\,s+f_{\theta_i}(s,a),\,\Sigma_i\right).
$$

如果 $f_{\theta_i}$ 在某个 $(s,a)$ 附近预测分歧大，说明训练数据没有充分约束那里；这就是 epistemic uncertainty。它的价值是早期小数据阶段防止 planner 被单个高容量模型的自信外推骗走。

但这里有两个边界：

1. 论文没有做严格 bootstrap resampling，而是用不同随机初始化和不同 mini-batch 近似后验样本；
2. ensemble disagreement 不等于全部风险，它不能直接表达 camera tracker noise、接触随机性、摩擦时变、执行延迟等 aleatoric uncertainty。

这正是 WMTS 后续必须从 PDDM 走向 explicit ensemble-LCB / uncertainty decomposition 的原因。

### 2.5 从 random shooting 到 CEM：高维动作序列为什么难

在当前真实状态 $s_t$，MPC 需要解：

$$
A^\star
=
\arg\max_{A=(a_0,\ldots,a_{H-1})}
\sum_{\tau=0}^{H-1}r(\hat{s}_{t+\tau},a_\tau),
\quad
\hat{s}_{t+\tau+1}=\hat{s}_{t+\tau}+f_\theta(\hat{s}_{t+\tau},a_\tau).
$$

Random shooting 从某个 proposal 分布直接采样 $N$ 条序列：

$$
A^{(k)}\sim q(A),\quad
k=1,\ldots,N,
$$

然后选最大 $R_k$。问题是动作序列空间维度是：

$$
\dim(A)=H\cdot d_a.
$$

Baoding balls 中 $H=7,d_a=24$，所以一个候选序列在 168 维空间里。独立白噪声采样在这种空间里几乎不会自然形成“连续推球、换指、接住”的协调动作。

CEM 改进为多轮 refinement。第 $m$ 轮采样：

$$
a_t^{(k)}\sim\mathcal{N}(\mu_t^m,\Sigma_t^m),
$$

选 top-$J$ elite 后更新：

$$
\mu_t^{m+1}=\alpha\cdot \mathrm{mean}(A_{\mathrm{elite},t})+(1-\alpha)\mu_t^m,
$$

$$
\Sigma_t^{m+1}=\alpha\cdot \mathrm{var}(A_{\mathrm{elite},t})+(1-\alpha)\Sigma_t^m.
$$

CEM 比 random shooting 好，但 hard elite 有一个结构性缺陷：第 $J+1$ 名和最后一名都被同样丢弃，排序信息被截断；在窄成功流形和嘈杂 model rollout 下，过早 elite 收缩会把 planner 锁进局部动作模式。

### 2.6 Reward-weighted refinement：MPPI 视角的无跳步推导

PDDM 使用更 soft 的 update。可以从熵正则轨迹分布优化理解它。

设当前 proposal 是 $q_0(A)$，希望找一个新的轨迹分布 $q(A)$，既偏向高 reward，又不要离原 proposal 太远：

$$
\max_q
\mathbb{E}_{A\sim q}[R(A)]
-
\frac{1}{\gamma}
\mathrm{KL}(q(A)\|q_0(A)).
$$

写出泛函拉格朗日量并加入归一化约束：

$$
\mathcal{L}(q)
=
\int q(A)R(A)dA
-
\frac{1}{\gamma}
\int q(A)\log\frac{q(A)}{q_0(A)}dA
+\lambda\left(\int q(A)dA-1\right).
$$

对 $q(A)$ 求变分导数并令零：

$$
R(A)
-
\frac{1}{\gamma}\left(\log\frac{q(A)}{q_0(A)}+1\right)
+\lambda
=0.
$$

移项：

$$
\log\frac{q(A)}{q_0(A)}
=
\gamma R(A)+\gamma\lambda-1.
$$

指数化：

$$
q^\star(A)
\propto
q_0(A)\exp(\gamma R(A)).
$$

用从 $q_0$ 采样的 $N$ 条序列做 Monte Carlo，新的 action mean 是加权均值：

$$
\mu_t
=
\mathbb{E}_{q^\star}[a_t]
\approx
\frac{\sum_{k=1}^{N}\exp(\gamma R_k)a_t^{(k)}}
{\sum_{j=1}^{N}\exp(\gamma R_j)}.
$$

这就是论文 Eq.(2)。这里 $\gamma$ 是 reward-weighting factor / inverse temperature，不是 RL 折扣因子。

两个极限帮助理解：

- $\gamma\to 0$：$\exp(\gamma R_k)\approx 1$，所有 sample 差不多等权，动作均值趋向“平均噪声”，容易不动；
- $\gamma\to\infty$：权重集中到最高 reward sample，退化为 hard elite / argmax，容易 aggressive 并掉球。

论文 Fig.4 的 $\gamma$ 消融正是在验证这个温度权衡：medium values 最稳，Baoding 采用 $\gamma=20$。

### 2.7 Beta-filtered action noise：低通先验如何降低有效维度

PDDM 不直接独立采样每个时间步动作噪声，而是先采样：

$$
u_t^{(k)}\sim\mathcal{N}(0,\Sigma),
$$

再递推：

$$
n_t^{(k)}
=
\beta u_t^{(k)}+(1-\beta)n_{t-1}^{(k)},\quad n_{t<0}=0,
$$

最后：

$$
a_t^{(k)}=\mu_t+n_t^{(k)}.
$$

把递推展开：

$$
n_t^{(k)}
=
\beta u_t^{(k)}
+\beta(1-\beta)u_{t-1}^{(k)}
+\beta(1-\beta)^2u_{t-2}^{(k)}
+\cdots
+\beta(1-\beta)^t u_0^{(k)}.
$$

所以 $n_t$ 不是独立白噪声，而是一个 AR(1)-like low-pass process。相邻动作噪声共享历史项，导致：

$$
\mathrm{Cov}(n_t,n_{t-1})\neq 0.
$$

直觉上，这个 filter 把“每 0.1 秒都可以任意跳变的 24 维动作”改成“相邻动作连续变化”的手部运动先验。它不是为了让轨迹好看，而是在高维 planner 里减少无效搜索维度，避免 sampled sequence 被高频抖动浪费。

边界也很清楚：

- $\beta=1$：$n_t=u_t$，回到独立噪声；
- $\beta$ 太小：噪声几乎沿用过去，探索/控制 authority 不足；
- filter 只表达 temporal smoothness，不表达接触模式、手指协同、摩擦锥等物理结构。

### 2.8 Ensemble reward aggregation 与隐式保守性

论文描述中，每条候选 action sequence 的 reward $R_k$ 是所有 ensemble models 的 mean predicted reward：

$$
R_k
=
\frac{1}{E}\sum_{i=1}^{E}
\sum_{\tau=0}^{H-1}
r(\hat{s}_{t+\tau}^{(k,i)},a_\tau^{(k)}).
$$

这会让 model disagreement “影响动作选择”：如果某条序列在部分模型里掉球或 reward 很差，均值会被拉低。

但这不是严格 pessimism。严格 conservative planning 更像：

$$
R_k^{LCB}=\bar{R}_k-\lambda\cdot \mathrm{Std}_i(R_k^{(i)}).
$$

PDDM 只用 mean，所以当所有模型共同乐观或 ensemble 未覆盖真实失败模式时，planner 仍会被 model exploitation 欺骗。这个差别是 PDDM 到后续 MoDem-V2/FOWM/WMTS ensemble-LCB 的关键演进。

### 2.9 信息流：PDDM 是 planner，不是 policy

PDDM 的迭代闭环是：

| 阶段 | 输入 | 计算 | 输出 | 关键风险 |
|---|---|---|---|---|
| 真实执行 | 当前 $s_t$ | PDDM-MPC 采样和模型 rollout | 执行 $a_t^\star$ | online planning latency |
| 数据收集 | $(s_t,a_t,s_{t+1})$ | append to $\mathcal{D}$ | transition dataset | 掉球/失败样本也应保留 |
| 模型训练 | $\mathcal{D}$ | 每个 model 训练 $E$ epochs | ensemble dynamics | 过拟合、小数据外推 |
| 下一步重规划 | 新 $s_{t+1}$ | horizon-$H$ optimization | 新动作 | 长 horizon 误差由 receding horizon 缓解 |

注意：PDDM 没有学习一个可直接部署的 $\pi_\phi(a\mid s)$。它每一步都调用 planner。这个性质对真机很实际：样本效率高，但部署算力和延迟压力大；也解释了为什么它更适合作为 WMTS 的 world-model evaluator / teacher，而不是最终 generalist policy。

## 3. 训练、数据与实验

### 3.1 实验设置

附录给出的统一模型与优化设置：

| 项 | 数值/设计 | 解释 |
|---|---|---|
| dynamics model | 2 hidden layers, each 500 units, ReLU | Fig.4 证明 2x64 容量不足，2x250/2x500 更合理 |
| loss | standard MSE supervised loss | 对应固定 covariance Gaussian MLE |
| optimizer | Adam, learning rate 0.001 | dynamics model 训练 |
| batch size | 500 transitions | 每个 epoch 对 dataset 单 pass |
| action normalization | $[-1,1]$ | 让不同任务动作尺度统一 |
| model training epochs per iteration | 40 | Algorithm 1 的 $E$ |
| MPC refinement iterations | 3 | Table 1 的 $M$ |
| horizon | 7 for all tasks | Fig.4 说明太短 greedy，太长 compounding error |

任务超参：

| 任务 | $R$ rollouts | $T$ steps | $H$ | $N$ samples | $\gamma$ | $\beta$ | $M$ | epochs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Valve Turning | 20 | 200 | 7 | 200 | 10 | 0.6 | 3 | 40 |
| In-hand Reorientation | 30 | 100 | 7 | 700 | 50 | 0.7 | 3 | 40 |
| Handwriting | 40 | 100 | 7 | 700 | 0.5 | 0.5 | 3 | 40 |
| Baoding Balls | 30 | 100 | 7 | 700 | 20 | 0.7 | 3 | 40 |

任务状态/action/reward：

| 任务 | $dt$ | $\dim(s)$ | $\dim(a)$ | reward 结构 |
|---|---:|---:|---:|---|
| Valve Turning | 0.15 | 21 | 9 | $-10|\theta_{valve}-\theta_{target}| + 1(|\cdot|<0.25)+10(|\cdot|<0.1)$ |
| In-hand Reorientation | 0.1 | 46 | 24 | $-7\|cube_{rpy}-target_{rpy}\|-1000\,1(isdrop)$ |
| Handwriting | 0.1 | 48 | 24 | $-100\|tip_{xy}-target_{xy}\|-20\|tip_z\|-10\,1(forwardtipping>0)$ |
| Baoding Balls | 0.1 | 40 | 24 | $-5\|objects_{xyz}-targets_{xyz}\|-500\,1(isdrop)$ |

因果解释：这些 reward 都不是 sparse success-only；PDDM 需要 dense reward 来给短 horizon planner 排序。论文 discussion 也承认 future work 应研究 sparse-reward / long-horizon abstraction。

### 3.2 Ablation：Fig.4 证明“组合 critical”

Fig.4 是 Baoding balls 上的 normalized task reward 曲线，论文没有给每条曲线的精确终点表；因此这里只记录可由图和文字确认的趋势。

| 设计因素 | 论文观察 | 因果解释 | 对使用者的判断 |
|---|---|---|---|
| Model architecture | 2x64 明显不足；2x250/2x500 好得多 | 接触丰富系统需要足够容量表达局部非线性 | 模型太小不是“更稳”，而是欠拟合接触模式 |
| Ensemble size | ensemble 对早期训练尤其有帮助 | 非 ensemble 高容量模型早期小数据过拟合且过度自信 | ensemble 是允许大模型上线探索的前提 |
| Warmstart vs random reset | 差异不大 | 数据集逐步增长时，重新训练/继续训练都能拟合 transition | 关键不是 warmstart，而是 model+planner 结构 |
| Horizon | 太短 greedy，太长 compounding error；$H=7$ 表现好 | contact dynamics 下 prediction error 随 horizon 复合 | WMTS world model 也应默认短 horizon evaluator |
| Controller type | Filtering + reward weighting 明显优于 CEM 和 random shooting | soft update 保留排序信息，filter 降低高维动作噪声 | PDDM 的 planner 贡献不是可替换小技巧 |
| Reward-weighting $\gamma$ | medium values 最稳；过软不动，过硬 aggressive 掉球 | $\gamma$ 是 entropy-vs-argmax 温度 | 这是 control authority 与 safety 的旋钮 |

这组消融是本文最有价值的证据：它没有只证明“PDDM 比 baseline 高”，而是证明 PDDM 的成功来自三个结构约束的合取：capacity + uncertainty + temporally structured optimization。

### 3.3 与 baseline 比较：哪些任务真正证明了 story

论文比较对象包括：Nagabandi et al. deterministic NN dynamics + random shooting MPC、PETS、NPG、SAC、MBPO。

| 任务 | 结果摘要 | 它证明了什么 |
|---|---|---|
| Valve Turning | 多数方法都能学会，PDDM 学得最快；NPG 需要大得多的数据量（Fig.5 为 log-scale datapoints） | 简单接触任务上，PDDM 的优势主要是样本效率，而非唯一能成功 |
| In-hand Reorientation, 2 goals | PDDM 与 SAC 都能达到较好表现，SAC final reward 甚至可相当/更高 | 单一或少量目标下，model-free policy 仍可竞争；PDDM 不是万能优于 SAC |
| In-hand Reorientation, 8 goals | PDDM 仍成功，model-free / policy learning 方法陷入 local optima | 证明 PDDM 学的是 reusable interaction model，而不是某个 goal-specific policy |
| Handwriting fixed trajectory | PDDM、SAC、NPG 可解决；早期 model-based baseline 不足 | 固定轨迹不完全体现 flexibility |
| Handwriting arbitrary trajectories | only PDDM succeeds；model-free 方法面对 arbitrary trajectories stuck | 这是 PDDM story 的强证据：learned dynamics 可换 reward/goal，而 policy 容易任务特化 |
| Baoding Balls simulation | 其它 model-based/model-free 方法未能成功；PDDM 用 100,000 datapoints / 2.7 hours data solve | 高维多物体接触切换中，filtered reward-weighted ensemble MPC 才显出必要性 |

这里的 critical reading 是：最能支撑论文价值的不是 valve 或 2-goal reorientation，而是 arbitrary handwriting 与 Baoding balls。前者证明模型可复用到 user-specified goals，后者证明高维接触交互中 planner 结构足以超过 baseline。

### 3.4 真机 Baoding balls：硬数字与边界

真机设置：

| 项 | 论文设置 |
|---|---|
| Robot | 24-DoF Shadow Hand |
| Objects | two free-floating Baoding balls |
| State estimation | camera tracker estimates 3D ball positions |
| Tracker input | 280x180 RGB stereo pair, 12 cm baseline |
| Tracker training | sim + real fine-tune；约 100 hand-labeled images in 25 videos → >10,000 training images |
| Tracker quality | average tracking error 5 mm, latency 20 ms |
| Planner frequency | 10 Hz |
| Low-level controller | position controller at 1 kHz, zero-order hold |
| Episode horizon | 10 s or until either ball drops |
| Reset | ramp + 7-DoF Franka-Emika arm reset |

真机结果：

| 任务 | 数据量/训练时间 | 成功率 | 解释 |
|---|---:|---:|---|
| 90° Baoding rotation | under 2 hours real-world training | about 100% | 短 horizon model + MPC 足以学稳定双球旋转 |
| 180° Baoding rotation | up to about 4 hours real-world training | about 54% | 更长模式转换需要 pinky-to-thumb control transfer，局部模型仍受限 |

因果解释：90° 的成功说明 PDDM 确实能从纯真实数据学到可执行接触技能；180° 只有 54% 则暴露了它的边界：当任务需要更长程的接触模式接力时，短 horizon planner 的局部性和 model error 会成为瓶颈。

### 3.5 实验故事的严谨读法

本文的实验不是在证明“神经世界模型已经解决灵巧操作”，而是在证明：

1. **model-based RL 的样本效率优势在高维灵巧手上仍能成立**，前提是 planner 不是 naive random shooting；
2. **learned dynamics 比 task-specific policy 更适合 goal/reward 切换**，handwriting arbitrary trajectories 是关键证据；
3. **ensemble 是早期真机学习的安全带，但不是完整安全机制**，因为 mean reward aggregation 不等于 risk-sensitive planning；
4. **短 horizon replan 是成功条件也是能力边界**，它能抑制 model error，却处理不了需要抽象技能层级的 sparse long-horizon task。

## 4. 核心洞见

### 4.1 论文真正的 insight

PDDM 的真正 insight 是：**在接触-rich dexterous manipulation 里，世界模型不需要先成为一个长期精确 simulator；它只需要在当前数据分布附近足够支持短 horizon ranking，就能通过 receding horizon 控制产生长程行为。**

这句话比“learn a dynamics model”更准确。PDDM 不要求模型能 open-loop 预测 1000 steps Baoding trajectory；它只要求模型在 $H=7$ 内把“这条动作会掉球”和“这条动作会推进目标”排得相对正确。每步重新观测真实状态后，长程行为由短程 ranking 拼出来。

### 4.2 为什么这个设计有效

它有效是因为三个偏差刚好对齐任务结构：

1. **Dense transition bias**：接触任务虽然 reward 难，transition label 密；每个 $s,a,s'$ 都能训练模型。
2. **Short-horizon bias**：接触模型长期不准，但短期局部可学；MPC 正好只用短期。
3. **Smooth-action bias**：手部动作必须连续协调；beta filter 把搜索空间从白噪声动作降到更像真实控制的低通序列。

这些 bias 不是通用 magic。它们适合 Baoding/handwriting 这类 dense reward、连续控制、局部接触可观测任务；换成语言条件长程任务或视觉遮挡严重任务，PDDM 的 bias 就不够。

### 4.3 什么时候会失效

PDDM 的失败边界可以从公式直接看出来：

- 若 reward 只在很长 horizon 后出现，$R_k=\sum_{\tau=0}^{H-1}r(\hat{s}_{t+\tau},a_\tau)$ 在 $H=7$ 内没有区分度，planner 无法排序；
- 若 state 缺失关键接触变量，$\hat{p}(s'\mid s,a)$ 学到的是 partial-observation aliasing，不是动力学；
- 若 model ensemble 全体在同一区域乐观，mean reward 反而会稳定地选错；
- 若实时预算无法支持 $N=700$ samples × ensemble rollouts × $M=3$ refinements，PDDM 不能直接部署；
- 若动作空间是高层技能/离散接触模式，而不是连续 hand command，beta-filtered Gaussian noise 不是合适 proposal。

## 5. 替代方案与理论局限

### 5.1 理论维度

| 局限 | 为什么是理论问题 | 对 WMTS 的含义 |
|---|---|---|
| learned forward dynamics 不显式建模接触互补约束 | 真实接触满足非穿透、摩擦锥、冲量等约束；PDDM 只通过数据近似局部转移 | 需要 tactile/contact latent 或结构化 residual，不应只靠 MLP 吞状态 |
| ensemble 只近似 epistemic uncertainty | 无法分离观测噪声、执行延迟、摩擦随机性 | WMTS ensemble 应配 aleatoric head / calibrated uncertainty / LCB |
| reward mean 不是 robust objective | $\bar{R}$ 可能被共同乐观 bias 诱导 | task scheduler 需要 Solve/Probe/Reject 或 LCB/variance penalty |
| short-horizon ranking 不能解决 sparse long-horizon abstraction | $H=7$ 内无 reward 差异时采样优化失去信号 | WMTS 的 latent task generation 必须提供中间目标/课程 |

### 5.2 算法维度

| 替代方案 | 优点 | 相对 PDDM 的问题 |
|---|---|---|
| SAC/NPG model-free policy | 部署快、amortized、无需模型 rollout | 真机样本贵；arbitrary goal flexibility 差 |
| PETS | ensemble/probabilistic MBRL 更系统 | 本文实验显示在 dexterous suite 上不够，缺少 PDDM planner 结构 |
| CEM-MPC | 简单强基线 | hard elite 早熟，排序信息利用差 |
| Differentiable MPC / analytic gradients | 可用梯度优化动作 | 接触 discontinuity 和 learned model artifacts 会让梯度不可靠 |
| Diffusion Policy / Flow policy | 学可部署多模态 action distribution | 需要数据；PDDM 可作为 data collector / planner teacher，而非替代 |
| DexNDM joint-wise dynamics | 更适合关节级 reality gap compensation | 需要真实 joint-level actuator/dynamics data；不直接解决 online task replanning |

### 5.3 工程/实验维度

- 真机状态依赖 camera tracker；论文没有直接处理 tactile 或 raw vision dynamics。
- 自动 reset 系统是成功条件之一；没有 reset，纯真机 exploration 的 wall-clock 和安全代价会高很多。
- 10 Hz planner + 1 kHz low-level position control 隐含了底层控制器稳定性；LinkerHand CAN/actuator latency 下不能直接假设同等可行。
- 实验主要是 dense reward continuous tasks；sparse reward long-horizon 技能仍是 future work。
- Fig.5-8 多为曲线图而非数值表，不能把图中趋势夸大成精确 benchmark ranking。

## 6. 对用户研究的启发

### 6.1 对 WMTS 的迁移：PDDM 应变成 evaluator / teacher，而不是最终 policy

WMTS 管线是 latent task generation → PPO Oracle → Diffusion/Flow generalist → Ensemble World Model → real-robot fine-tuning。PDDM 可以插入三个位置：

| PDDM 组件 | 在 WMTS 中应变成什么 | 具体用法 | 不应照搬的点 |
|---|---|---|---|
| Bootstrap ensemble dynamics | Ensemble World Model | 对 candidate task / rollout 做 short-horizon feasibility scoring | 不能只用 mean reward；应加 LCB/uncertainty decomposition |
| MPC trajectory sampler | Oracle/teacher data generator | 对新 latent task 生成高价值局部解或失败边界 | 不作为最终高频部署 controller |
| Reward-weighted refinement | Task-conditioned local planner | 用于筛选 diffusion policy action chunks / flow samples | 不能在 168 维以上无限采样，需 learned proposal |
| Beta-filtered noise | Smooth action prior | 作为 LinkerHand action chunk 的 low-pass prior / actuator-safe proposal | 不能替代 actuator dynamics model |
| Receding horizon | Safety checker | 每步评估未来 $H$ 步掉落风险、接触丢失风险 | 不能解决全局 task decomposition |

最具体的 WMTS 改造是：

$$
Score(\tau,g)
=
\mathbb{E}_{i}[R_i(\tau,g)]
-\lambda\mathrm{Std}_{i}[R_i(\tau,g)]
-\eta\,Cost_{contact/actuator}(\tau),
$$

其中 $\tau$ 可以来自 PPO Oracle、Diffusion/Flow generalist 或 task generator。PDDM 给了 $\mathbb{E}_i[R_i]$ 的早期形式；WMTS 应补上 $\mathrm{Std}_i$ 和 contact/actuator cost。

### 6.2 对 DNPM/转笔的具体设计

转笔比 Baoding balls 更难直接套 PDDM，因为 pen spinning 有更强的离手/再接触、角动量相位、接触点不可观测问题。但 PDDM 仍能给出一个可做的实验：

| 转笔变量 | PDDM 对应 | 需要改造 |
|---|---|---|
| hand proprioception $q,\dot{q}$ | $s_t$ | 保留为 model input |
| pen pose/velocity | Baoding ball 3D position | 必须加入视觉/marker 或 estimator；只有 proprioception 不够 |
| tactile contact bits / shear | PDDM 未用 | 应加入 dynamics state，避免 partial observation |
| action chunk $a_{t:t+H}$ | PDDM candidate sequence | 用 beta filter 或 diffusion proposal 保持 smooth |
| phase/contact mode | PDDM 无显式 mode | 需要 latent mode 或 hybrid dynamics head |
| drop / unsafe contact | reward penalty | 应变成 explicit cost critic / safety head |

一个低风险实验：

1. 先在 Isaac/Genesis 中收集转笔短片段 transition；
2. 训练 ensemble dynamics 预测 $(pen\ pose, pen\ velocity, contact\ mode)$ 的短 horizon；
3. 对同一批 candidate action chunks 比较三种 scoring：mean reward、LCB reward、LCB + contact cost；
4. 如果 LCB 能更早拒绝掉落/滑飞片段，说明 PDDM-style ensemble 对 WMTS task scheduler 有真实价值；
5. 如果 ensemble disagreement 与真实失败无关，则说明 observation/latent 不足，不能继续堆 planner。

### 6.3 与 DexNDM / DexTrack / Diffusion Policy 的组合

PDDM 到后续工作形成一条清晰演进线：

| 论文/方法 | 学什么 | 用法 | 对 PDDM 的修正 |
|---|---|---|---|
| PDDM | 整体 $f(s,a)$ | online MPC | 样本效率高，但 planner 昂贵 |
| [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]] | joint-wise neural dynamics | residual policy / sim-to-real correction | 把整体高维 dynamics 分解到关节，降低 reality gap |
| [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] | reference tracking controller | human reference → robot tracking | 从 online planning 转向可部署 tracking policy |
| [[Diffusion Policy: Visuomotor Policy]] | multimodal action distribution | amortized action generation | 可把 PDDM planner 的成功 chunks 蒸馏成 generalist |
| [[Finetuning Offline World Models in the Real World|Finetuning Offline World Models in the Real World (FOWM)]] | offline-to-online world model | uncertainty-aware real fine-tune | 把 PDDM 的 ensemble intuition 推到 offline/online setting |

对 WMTS 最自然的组合是：PDDM-style ensemble 先做局部 feasibility oracle，筛出高价值 action chunks；Diffusion/Flow generalist 学这些 chunks 的条件分布；真机阶段再用 ensemble disagreement 做 Probe/Reject。

### 6.4 不应过度外推的点

- 不要把“4 小时真机 Baoding balls”外推成“任意灵巧手任务 4 小时解决”；它依赖 dense reward、可追踪球位置、自动 reset、低层 position control。
- 不要把 ensemble disagreement 当安全证书；它只是数据覆盖不足的 proxy。
- 不要把 PDDM 当作可部署实时策略；它每步要采样规划。
- 不要忽略 reward engineering：本文任务 reward 都足够 shaped，PDDM 没解决 sparse success-only dexterity。
- 不要假设 LinkerHand 与 Shadow Hand 的 actuator/latency/friction gap 可以被同一 dynamics MLP 吞掉；需要 actuator-aware state 或 residual model。

## 7. 与知识体系的联系

### 7.1 与 [[Dynamics]] 的联系

PDDM 是“从解析动力学到数据驱动局部动力学”的节点。传统刚体/接触动力学会写成：

$$
M(q)\ddot{q}+C(q,\dot{q})\dot{q}+g(q)
=
\tau+J(q)^\top\lambda,
$$

并加互补条件、摩擦锥、接触切换。PDDM 不显式求这些量，而是学习：

$$
s_{t+1}-s_t=f_\theta(s_t,a_t)+\epsilon.
$$

这牺牲了可解释物理结构，换来对复杂接触的经验拟合和在线适应。对你的知识库而言，它应被放在“learned dynamics / neural world model”而非“严格物理 simulator”一侧。

### 7.2 与 [[Optimization]] 的联系

PDDM 的 controller 是 sampling-based trajectory optimization。Random shooting、CEM、MPPI/reward weighting 是一条连续谱：

| 方法 | 更新方式 | 信息利用 | 失败模式 |
|---|---|---|---|
| Random shooting | 取 best sequence | 只用 argmax | 高维空间极低效 |
| CEM | top-$J$ elite mean/variance | 用 elite 子集 | hard cutoff 早熟 |
| PDDM reward weighting | $\exp(\gamma R_k)$ soft weights | 用所有 sample 排序 | $\gamma$ 太大退化 hard，太小无控制权 |

这条谱对 WMTS 很重要：以后 task generator / action chunk optimizer 如果用采样优化，应明确 proposal、temperature、elite/soft update 与 uncertainty penalty，而不是只说“用 CEM 选最优”。

### 7.3 与 [[ReinforcementLearning]] 的联系

PDDM 是 model-based RL 的典型“policy-free planning”分支。它没有学 actor，而是用：

$$
\mathcal{D}\rightarrow \hat{p}_\theta \rightarrow \arg\max_A \hat{R}(A)
$$

替代：

$$
\mathcal{D}\rightarrow \pi_\phi(a\mid s).
$$

这解释了它在 arbitrary goals 上强：reward/goal 可在 run-time 换，因为模型不绑定某个目标策略。但这也解释了它部署慢：每个动作都要重新优化。

### 7.4 与 [[StochasticProcess]] 的联系

PDDM 里的随机性有两类，不能混淆：

1. ensemble over $\theta_i$：近似 dynamics posterior，表达 epistemic uncertainty；
2. filtered action noise $n_t$：AR(1)-like sampling process，表达 temporally correlated exploration/proposal。

前者回答“模型知不知道”；后者回答“planner 该如何试动作”。把二者混起来会导致错误设计，例如用更大 action noise 试图解决 model uncertainty，或用 ensemble variance 替代 action smoothness。

## 8. 应复刻的提问颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “PDDM 相比 PETS 到底多了什么？” | PETS 有 ensemble/probabilistic model；PDDM 的关键增量是 high-dimensional dexterous setting 下 reward-weighted refinement + beta-filtered action sequence + receding horizon 组合 |
| “为什么 ensemble 有用，不就是多个网络平均？” | 从 $p(s'\mid s,a,\mathcal{D})=\int p(s'\mid s,a,\theta)p(\theta\mid D)d\theta$ 推到 finite ensemble；说明它是 epistemic proxy，不是安全证书 |
| “公式里的 $\gamma$ 是 RL discount 吗？” | 不是；它是 reward-weighting inverse temperature，控制 soft update 到 hard elite 的程度 |
| “beta filter 到底降低了什么维度？” | 展开 $n_t=\beta\sum_j(1-\beta)^{t-j}u_j$，说明相邻动作相关，减少 $H d_a$ 白噪声搜索 |
| “4 小时真机数据能不能支撑我的 LinkerHand 转笔？” | 不能直接外推；要检查 state observability、reset、reward density、actuator latency、tactile/contact sensing |
| “PDDM 对 WMTS 最重要的迁移是什么？” | ensemble short-horizon evaluator + planner teacher + uncertainty-driven Probe/Reject，不是最终 online MPC policy |
| “实验数字如何支撑故事？” | arbitrary handwriting 证明 goal flexibility；Baoding 100k datapoints/2.7h 证明高维接触组合；真机 90°≈100%/180°≈54% 同时证明能力和长程边界 |

## References

- [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]]
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]]
- [[Diffusion Policy: Visuomotor Policy]]
- [[Finetuning Offline World Models in the Real World|Finetuning Offline World Models in the Real World (FOWM)]]
- [[Model-Based Lookahead Reinforcement Learning for in-hand manipulation]]
- [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation]]
