---
tags: [insight, WMTS, task-definition, rl-theory, rationale]
aliases: [Planner-Follower Rationale, 为什么 goal-conditioning 会 mode collapse]
created: 2026-06-16
status: rationale
related:
  - "[[Final_WMTS]]"
  - "[[auto_taskgen]]"
  - "[[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation]]"
  - "[[ReinforcementLearning]]"
---

# Planner-Follower 任务定义：为什么 goal-conditioned RL 必致 Mode Collapse

> [!abstract] 核心论证（这是 WMTS 任务生成设计背后"缺失的 why"）
> **把手内重定向单纯定义为"到达某个绝对目标 $g$"、并交给标准 PPO 端到端求解，必然导致 mode collapse——不是因为算法弱，而是任务定义本身让 RL 有"偷懒"的数学激励。解药不是换算法（不是 SAC 最大熵），而是改任务定义：把长目标拆成 receding-horizon 航点，让 PPO 退化为 follower/tracker，规划交给上层。**
> 本 note 把这条论证从临时对话（`insight-chat-tmp.md` Turn 2-3）萃取为永久 rationale，给 [[auto_taskgen]] 已有的 atomic-stitching / Receding Horizon 设计补上严格的 RL 理论依据。

> [!tip] 与已有设计的衔接
> - [[auto_taskgen]] 已记录 **Start-to-Goal 的"过拟合/机械记忆"症状** 与 **原子短切片 + Receding Horizon** 的解；本 note 补的是**为什么**（三条 RL 理论机制）+ **Planner-Follower 抽象** + **POMDP→Teacher-Student 必然性**。
> - 遵循 WMTS 默认：**PPO 为唯一 Oracle 主干**（用户已在 Turn 3 显式否决 SAC），多峰由下游 Diffusion/Flow generalist 承担，不靠最大熵 RL。

## 1. 痛点：goal-conditioning 给了 RL "偷懒"的数学激励

当前重定向常定义为 $P(\text{success}\mid g)$——给定绝对目标姿态 $g$ 求成功率。这有两个结构缺陷：

1. **忽略初始流形 (Initial Manifold Ignorance)**：旋转难度不只取决于 $\Delta x = $ 起止位姿差，而**强依赖手当前构型 $q$**。五指张开转 90° 容易，处于奇异/死锁构型时同样 90° 可能物理不可达。只条件化物体状态 $x$、不条件化手状态 $q$ 的任务定义，本身就丢了难度的一半来源。
2. **缺乏多样性驱动**：只以"到达目标"为奖励，PPO 必然坍缩到一条**方差最小、最确定**的轨迹。它不需要学"滑脱了怎么补救"，因为训练时只走那条不滑脱的完美路径。

## 2. 为什么是 PPO 的本质问题（三条 RL 理论机制）

> [!warning] 不要笼统说"mode collapse"——指明优化/数据机制（见 research-insight-critic skill 红线）

| 机制 | RL 理论表述 | 后果 |
|------|-------------|------|
| **贪婪轨迹优化 (Path of Least Resistance)** | PPO 最大化 $J(\pi)=\mathbb{E}_{\tau\sim\pi}[\sum\gamma^t r_t]$；一旦偶然发现某条"凑巧到达 $g$"的指法，策略梯度疯狂放大其概率 | 收敛到单一轨迹，放弃探索其它解 |
| **虚假相关 / 背板 (Spurious Correlation)** | 学到的是"state=A,goal=B → 固定输出动作序列 X 拿 reward"，而非摩擦/重心/接触面的泛化物理律 | 微扰或需新指法时彻底崩溃 |
| **信用分配失效 (Credit Assignment)** | 长视野只给终点奖励 → 无法归因失败发生在哪一步 → 收敛到次优局部解 | 长程规划必然"偷懒" |

**结论（用户 Turn 3 的核心 claim）**：**RL 应作为 Follower（执行器），不能自主承担 Planner（规划器）的决策，否则一定偷懒。** 这把 ViserDex Turn-1 的观察（"绕轴连续旋转不需精确物理；goal-reorientation 才需要"）推进一步：goal-reorientation + 端到端 PPO = mode collapse 的温床。

## 3. 解药：Planner-Follower + Receding-Horizon 轨迹追踪（非 SAC）

> [!danger] 纠正一条岔路
> 中间对话曾建议用 **SAC 最大熵** 打破轨迹固化。**用户已否决**：(1) PPO 鲁棒性更高、当前实验基建都基于 PPO；(2) 熵正则也**无法**根治 goal-conditioning 导致的 mode collapse（它鼓励动作分布发散，但不改变"单目标→单轨迹"的激励结构）。真正的解是**改任务定义**，不是改算法。

**Receding Horizon Trajectory Tracking**：把大目标 $g_{final}$ 从 PPO 观测中剥离，引入上层 Planner 动态生成未来 $H$ 步物理可行航点 $\mathcal{W}_t=\{g_{t+1},\dots,g_{t+H}\}$。PPO 降级为底层 tracker：

$$
s_t^{follower}=(q_t,\dot q_t,x_t,\mathcal{W}_t),\qquad
r_t=-\lambda_1\lVert x_t-g_{t+1}\rVert_{SE(3)}-\lambda_2\,\text{Penalty}_{energy}
$$

**为什么这能根治 mode collapse**：PPO 不再思考"怎么翻最省事"，而是被强制在**各种难度、各种姿态的短程轨迹**上拟合控制量——若想抄近道就因偏离 $g_{t+1}$ 被罚。于是它被迫学"在这个接触面下把物体挪 1cm"的**通用物理微操**，而非死记一条长轨迹。这正是 [[auto_taskgen]] **原子短切片 (0.5s/1s stitching)** 设计的理论根据：每个切片是"物理上绝对可行的局部运动流形"。

## 4. 副产物：难度估计器 = 可行性/可达性估计器

任务空间里**大量任务物理不可完成**。引入难度判别器 $\mathcal{D}_\phi(s_t,g)\to[0,1]$（可达性函数）：$\mathcal{D}_\phi=0$ 表示当前构型 $q$ + 物体位姿 $x$ 下目标 $g$ 物理不可达（运动学极限/严重碰撞），$\mathcal{D}_\phi=1$ 表示极易。

- **不可达屏蔽**：随机采样相对目标 $g_{rand}$，若 $\mathcal{D}_\phi<\epsilon$ 直接拒绝 → 解决"大量任务不可能完成"。
- **自动课程 (ACL)**：生成 $\mathcal{D}_\phi\approx0.5$ 的"最近发展区"任务；策略变强 → $\mathcal{D}_\phi$ 更新 → 自动加难。
- 与 [[auto_taskgen]] 已有的 **CMA-ES fitness 物理可行性惩罚项 $\lambda_{pen}$**（一碰就爆的任务 Fitness 降至最低）是同一思想的两种实现：CMA-ES 在任务生成端惩罚不可行，$\mathcal{D}_\phi$ 在采样端屏蔽不可行。
- **状态条件难度**必须同时含**手状态 $q$ + 物体状态 $x$ + horizon + contact mode**（research-insight-critic skill WMTS 默认），而非仅物体状态——这正回应 §1 的 Initial Manifold Ignorance。

## 5. 为什么必须 Teacher-Student（POMDP 必然性）

把目标定为"追踪"后有一个隐患：若策略**执行中看不到物体实时位姿 $x_t$**（手指遮挡 / 视觉推理跟不上），只能靠初始误差 + 关节角 $q_t$ 盲推 → 单帧观测 $o_t$ 无法完整描述真实状态 $s_t$ → **马尔可夫性崩溃**，问题从 MDP 退化为恶劣 POMDP。

$$
\mathbb{P}(s_{t+1}\mid o_t,a_t)\neq\mathbb{P}(s_{t+1}\mid s_t,a_t)\quad\text{(单帧观测不充分)}
$$

**Teacher-Student 是结构性解药，不是工程选项**：
- **Teacher**（仿真，特权态：真实 6D 位姿/接触力/摩擦系数）面对**完美 MDP**，PPO 高效学操控。
- **Student**（真机，遮挡 RGB/本体）处于 POMDP，须用 RNN 把历史观测流压成**信念态 $b_t$**；蒸馏本质是逼 $b_t\to s_t$（教师真实物理态）。
- 拆成 receding-horizon 航点后，tracker 要精准追 $g_{t+1}$ → **更**需要对物体微观状态的敏锐 belief → Teacher-Student **更必要**。
- 这条与 [[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation#2.5 机制级补充（自深度精读萃取）|ViserDex 的 belief-state RNN + 重构监督]] 完全同构（ViserDex 借鉴 Miki et al. 四足 perceptive locomotion 的 belief encoder-decoder）。

## 6. 对 WMTS 的净启发

1. **任务定义层**：坚持 receding-horizon 航点追踪 + 原子短切片（已在 [[auto_taskgen]]），并把"为什么"写清——这是抵御审稿人"你这不就是 goal-conditioned RL 换皮"质疑的论证。
2. **角色分工**：上层 Planner（CMA-ES/CVAE 任务生成 + WM lookahead）负责"去哪"，PPO Oracle 只负责"怎么跟"——明确 RL = follower。
3. **可行性优先**：$\mathcal{D}_\phi$ 可达性估计器 + CMA-ES $\lambda_{pen}$ 双端排除不可行任务。
4. **感知诚实**：遮挡 → POMDP → Teacher-Student + belief 是必然，不是可选；touch-centric（[[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation|ViserDex]] 自陈 RGB 在快速遮挡失守）进一步强化 belief 须含触觉。

## 7. 待解开放问题（承接对话未尽处）

- **冷启动**：$\mathcal{D}_\phi$ 早期只输出噪声 → 任务生成器下发离谱目标。预填充策略：用基础开环轨迹（手指乱拨）填充 $\mathcal{D}_\phi$ 数据，还是初期把目标严格限制在当前姿态极小邻域？（用户对话中留作开放）
- **难度估计器训练**：HER + TD-error 联合训练——失败轨迹实际到达的 $g'$ 作为 $\mathcal{D}_\phi(s_t,g')=1$ 的真值；多次探索仍不可达的区域 $\mathcal{D}_\phi\to0$。
- **无限序列表示**：CVAE 需定长输入 vs 任务连续无限长——见 [[auto_taskgen]] 开放问题。

## References
- 萃取自：`insight-chat-tmp.md`（ViserDex 深度对话 Turn 2-3，用户本人 formulation，2026-06-14）
- 设计落点：[[auto_taskgen]]（原子切片 / Receding Horizon / CMA-ES 可行性惩罚）、[[Final_WMTS]]（五模块）
- 同构机制：[[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation|ViserDex]]（belief-state RNN 蒸馏、POMDP）
- 理论默认：research-insight-critic skill（PPO-only、receding horizon、state-conditioned difficulty）
- 领域根：[[ReinforcementLearning]]（信用分配、策略梯度、POMDP）
