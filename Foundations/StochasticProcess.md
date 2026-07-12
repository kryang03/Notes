---
tags:
  - foundation
  - stochastic-process
  - uncertainty
  - belief-space
aliases:
  - 随机过程
  - SDE
  - 维纳过程
  - MPPI
  - 高斯过程
created: 2026-01-31
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[Optimization]]"
  - "[[SignalProcessing]]"
  - "[[InformationTheory]]"
  - "[[Dynamics]]"
  - "[[WorldModels]]"
---

# 灵巧操作中的随机过程：从随机扰动到信念空间控制

# Stochastic Processes for Dexterous Manipulation: From Random Disturbance to Belief-Space Control

> [!tip] 相关领域
> - [[ControlTheory]] — 随机最优控制、鲁棒控制；HJB 加噪即随机 HJB
> - [[ReinforcementLearning]] — MDP=可控马尔可夫链；扩散策略=学出来的 SDE；MPPI↔策略改进
> - [[Optimization]] — MPPI 是采样式优化；随机平滑修复不可微梯度
> - [[SignalProcessing]] — 贝叶斯滤波 (KF/EKF/UKF/PF) 是状态估计的共同语言
> - [[InformationTheory]] — 信念空间规划的目标=最大化信息增益（降熵）
> - [[Dynamics]] — GP 残差补偿刚体动力学模型误差
>
> **贯穿母题（本讲的"主角"）**：**在未知摩擦的桌面上把冰球推到目标点 (push a puck to a target under unknown friction)**。一个平面推动任务，却把随机过程每一层都逼了出来——我们让它贯穿全篇。

## 0. 母题与理论大厦构建路线：从随机扰动到信念空间控制

> [!abstract] 为什么用"推冰球"做贯穿母题？
> 随机过程不是"给模型加点噪声"的附属品，而是描述真实操作如何在**不可观测、不可精确预测**的接触界面上演化的基础语言。**在未知摩擦桌面上推冰球**这一个任务，恰好把每一层都点亮：
> - 冰球忽走忽停的 **stick-slip** → 噪声是**状态相关**的（SDE 的扩散项）；
> - 桌面摩擦系数 $\mu$ **事先不知道、且随位置变化** → 参数 + 结构不确定性、非马尔可夫；
> - 手挡住冰球、看不清它滑了多远 → **感知不确定性**、多峰后验；
> - "要不要先轻推一下试试摩擦" → **为感知而行动**（信念空间规划）；
> - 该用多大力推才既不滑过头又能动 → **随机最优控制 (MPPI)**、风险敏感。
>
> 全讲每引入一个概念，我们都回到这枚冰球："**它对应推冰球的哪一难？这一难为什么让确定性方法失效？**"

随机过程的主线，是把"不确定性"从模糊的工程直觉，提升为可计算的数学对象。整座大厦分六层，每层落到"推冰球"的一难：

| 层级 | 关键问题 | 理论对象 | 推冰球母题的映射 | 讲稿位置 |
|:--|:--|:--|:--|:--|
| **随机动力学层** | 状态为何不是单条轨迹？ | SDE、drift/diffusion、Itō calculus | stick-slip 使噪声随速度而变 | §2 |
| **马尔可夫层** | 当前观测是否足够？ | Markov property、POMDP、状态增广 | 单帧看不见 $\mu$、滑移史、隐藏接触模式 | §2 |
| **信念更新层** | 如何融合新观测？ | Bayes filter、EKF/UKF/PF、RBPF | "滑了没"常是多峰后验 | §4 |
| **非参数建模层** | 未知动力学如何学？ | 高斯过程、ensemble、epistemic 不确定性 | 摩擦残差需要带置信度地学 | §5 |
| **随机控制层** | 不确定下如何选动作？ | MPPI、path integral、risk-sensitive | 采样多条推法、按代价指数加权 | §6 |
| **接触随机层** | 互补约束本身不确定怎么办？ | stochastic complementarity、robust sampling | 摩擦阈值、接触间隙本身是随机变量 | §8 |

> [!important] Foundation 级判断标准（任何随机方法进入本库都要回答四问）
> 1. **不确定性属于哪一类**（参数 / 结构 / 感知）？这决定了治法。
> 2. **是 aleatoric 还是 epistemic**（世界本身的随机，还是我无知）？混淆二者会让安全/探索追逐噪声而非知识缺口。
> 3. **在哪个空间决策**（物理状态空间，还是信念空间 $b_t=p(x_t\mid z_{1:t})$）？
> 4. **如何对不可微/随机的接触求可用梯度或策略**（平滑 / 采样）？

> [!note] 本讲在知识图谱中的位置（依赖 / 被依赖）
> ```
>   [[Dynamics]] ─名义模型─┐                       ┌── belief/uncertainty ──> [[ReinforcementLearning]]
> [[ContactMechanics]] ─随机接触─┤                      │
>   [[SignalProcessing]] ─贝叶斯滤波─┼──> 【StochasticProcess】 ──MPPI──> [[Optimization]]/[[ControlTheory]]
>                              │                      │
>                信息增益目标 <──[[InformationTheory]]┘    └── 风险敏感安全 ──> Safe Control
> ```
> 读法：左侧给随机过程"喂"名义模型、随机接触结构、滤波语言；右侧消费它的产出（belief 进 RL、MPPI 进优化/控制、信息增益目标接信息论）。每个推导拐点都会用 `[[链接]]` 回扣。

------

## 1. 为什么必须拥抱随机性：从确定性的幻象说起

> [!tip] 本节四拍
> **直觉**（推冰球时，同样的力两次推出两条不同轨迹——确定性模型错在哪）→ **推导**（写出接触界面的微观随机来源）→ **对比**（确定性 LQG vs 随机视角）→ **落点**（随机性是特性而非缺陷，要拥抱而非消除）。

经典控制建立在"精确模型"的幻象上：刚体完美、摩擦遵守简单库伦律、传感器如实反映世界。这在工业臂重复轨迹时大获成功。但当多指手在非结构化环境里推冰球、转笔、盲抓时，幻象破灭。

> [!important] 一句话立论
> **灵巧操作的本质是管理接触 (managing contact)，而接触的本质是不确定性 (uncertainty)。** 指尖与物体的交互发生在一个充满微观随机性的界面上：表面粗糙度引起的摩擦波动、软指尖的非线性迟滞、接触点位置的不可观测——宏观上就表现为显著随机。于是：微分方程不再是确定轨道，而是**概率分布的流动**；状态估计不再是追踪一个点，而是**信念 (belief) 的贝叶斯更新**。

推一次冰球，它可能多滑 2cm，也可能因为一粒灰尘卡住——同样的输入、不同的结局。把这种"同输入异结局"当噪声压制（高增益反馈）不仅徒劳，还危险（高增益会把接触瞬间放大成刚性碰撞、损坏硬件）。本讲的纲领是：**把随机性当作可利用的特性**——用噪声去探索（§6）、用方差去感知风险（§7）、用采样去覆盖未知（§8）。

------

## 2. 随机动力学的语言：SDE、Itō 与马尔可夫

> [!tip] 本节四拍
> **直觉**（确定性 ODE 描述平均行为，SDE 还描述围绕平均的涨落）→ **推导**（Itō 形式的 SDE；Itō 引理与"噪声改变能量漂移"）→ **对比**（常数噪声 vs 状态相关噪声）→ **联系**（马尔可夫性如何在推冰球里被破坏 → POMDP/belief，接 §4、[[ReinforcementLearning#2.1 MDP 与 POMDP：把"试错"写成数学|RL POMDP]]）。

### 2.1 SDE：漂移 + 扩散，且扩散是状态相关的

经典力学 $\dot x=f(x,u)$ 只给平均行为。把微观未建模动力学（表面微凸体碰撞、电机齿槽转矩、软指高频振动）统称噪声，得 Itō 形式 SDE：

$$
dx_t=\underbrace{f(x_t,u_t)\,dt}_{\text{drift 漂移}}+\underbrace{G(x_t)\,dW_t}_{\text{diffusion 扩散}},
$$

$W_t$ 是维纳过程（布朗运动）。drift 是"期望发生的"（牛顿-欧拉刚体运动），diffusion 是"随时间发散的趋势"。

> [!important] 关键洞见：扩散项 $G(x_t)$ 是状态相关的（别当常数）
> 把 $G$ 简化成常数矩阵 $\Sigma$，是 LQG 等线性高斯控制器在复杂操作中失效的重要原因。推冰球里：
> - **摩擦的随机性随速度变**：低速时 Stribeck 效应与 stick-slip 显著、摩擦力剧烈波动，$G$ 很大；进入稳定滑动后摩擦平滑、随机性降低。**冰球忽走忽停那一刻，正是 $G(x_t)$ 飙升的时刻。**
> - **几何诱导的随机性**：冰球推到桌面边缘或曲率突变处，微小位置误差被放大为巨大法向方向误差→动力学分叉，$G$ 与接触构型高度相关。

> [!note] 补严：为什么 $dW\sim\sqrt{dt}$——维纳过程的二次变差 (quadratic variation)
> §2.2 的推导反复用到"$dW_t\sim\sqrt{dt}$、$(dW)^2\sim dt$"，这不是记号约定，而是维纳过程 $W_t$ 的**定义性质**，必须讲实，否则 Itō 二阶项就成了空中楼阁。维纳过程由三条公理定义（$W_t$=布朗运动位置 [无量纲或状态量]、$t$=时间 [s]）：① $W_0=0$；② 增量独立；③ 增量高斯 $W_{t+\Delta}-W_t\sim\mathcal N(0,\Delta)$——**方差等于时间间隔 $\Delta$**（这是关键，方差正比于 $\Delta$ 而非 $\Delta^2$）。
> 由③直接得单个增量的两个矩：$\mathbb E[(W_{t+\Delta}-W_t)^2]=\Delta$（均方 $\sim\Delta$）、$\mathrm{Var}[(W_{t+\Delta}-W_t)^2]=2\Delta^2$（高斯四阶矩公式 $\mathbb E[X^4]=3\sigma^4$ 减 $\sigma^4$ 得 $2\sigma^4=2\Delta^2$）。故增量的标准差 $\sim\sqrt{\Delta}$——**这就是"$dW\sim\sqrt{dt}$"的字面来历**。
> 把它累加起来就是**二次变差**：把 $[0,t]$ 均分成 $n$ 段（$\Delta=t/n$），平方增量之和的期望 $\sum_{k}\mathbb E[(\Delta W_k)^2]=n\cdot\Delta=t$，而其方差 $\sum_k 2\Delta^2=2t^2/n\to0$。于是当 $n\to\infty$，随机和在均方意义下**收敛到确定值**：
> $$[W]_t\;:=\;\lim_{n\to\infty}\sum_{k=1}^{n}(W_{t_k}-W_{t_{k-1}})^2\;=\;t\quad(\text{均方收敛}).$$
> 对比光滑函数 $g(t)$：其平方增量 $\sim(g'\Delta)^2\sim\Delta^2$，求和 $\sim n\Delta^2=t^2/n\to0$，二次变差为**零**。**布朗轨迹二次变差非零（$=t$）正是它处处连续却处处不可微、"无限抖动"的量化刻画**——也是它必须用 Itō 微积分而非牛顿微积分的根本原因：$(dW)^2$ 这个在光滑世界里该被丢掉的二阶量，在这里**均方退化成确定的 $dt$**（即 §2.2 用的 Itō 乘法表 $dW_i\,dW_j=\delta_{ij}dt$），撑起了 §2.2 那个多出来的能量漂移项，也定标了 §6.4 扩散 SDE 里 $g(t)\,dW$ 的噪声量纲 [$\cdot/\sqrt{\mathrm s}$]。这与 [[Optimization#3.2 非凸景观：鞍点、虚假极小与"好景观"的判据|优化中扰动逃离鞍点]]是同一件事的两副面孔：非零二次变差=噪声在弯曲景观上被整流出的确定性效应。

### 2.2 Itō 引理：噪声不止增加方差，还改变能量的漂移方向

处理 SDE 不能用普通链式法则，须用 **Itō 引理**（随机版链式法则）。对状态的标量函数 $V(x_t)$（Lyapunov/能量/价值函数）：

$$
dV=\Big(\partial_t V+\nabla V^Tf+\tfrac12\,\mathrm{Tr}(G^T\nabla^2V\,G)\Big)dt+\nabla V^TG\,dW.
$$

> [!note] 逐步推导：那个二阶项从哪来（普通链式法则为什么不够）
> 关键只有一句：**维纳增量 $dW$ 不是"高阶小量"**。确定性微积分里 $dx\sim dt$，二阶项 $(dx)^2\sim(dt)^2$ 可丢；但布朗运动的增量 $dW_t\sim\sqrt{dt}$（其标准差随 $\sqrt{dt}$ 缩，见 §2.1），于是 $(dW)^2\sim dt$ **和一阶项同量级、不能丢**。把 $V(x_t)$ 做二阶 Taylor 展开（$V$=能量/价值函数 [代价单位]）：
> $$dV=\partial_t V\,dt+\nabla V^{T}dx+\tfrac12\,dx^{T}\nabla^2V\,dx+o(dt).$$
> 代入 $dx=f\,dt+G\,dW$ 并逐项定阶（$dt$=时间步 [s]、$dW$=维纳增量 [$\sim\sqrt{\mathrm s}$]、$f$=漂移 [状态量/s]、$G$=扩散矩阵）：
> - $\nabla V^{T}dx=\nabla V^{T}f\,dt+\nabla V^{T}G\,dW$ —— 一阶漂移 + 一阶噪声，保留；
> - $dx^{T}\nabla^2V\,dx$ 里：$(f\,dt)^2\sim(dt)^2\to0$、交叉项 $f\,dt\cdot G\,dW\sim dt^{3/2}\to0$，**只剩** $(G\,dW)^{T}\nabla^2V(G\,dW)$ 这一项 $\sim dt$。
>
> 最后用 **Itō 乘法表** $dW_i\,dW_j=\delta_{ij}\,dt$（$\delta_{ij}$=克罗内克符号；直觉：$\mathbb E[(dW)^2]=dt$ 且其方差 $\sim(dt)^2$ 可忽略，故 $(dW)^2$ 在均方意义下**退化成确定量 $dt$**）把随机的 $(dW)^2$ 换成确定的 $dt$：
> $$(G\,dW)^{T}\nabla^2V(G\,dW)=\sum_{i,j}(\nabla^2V)_{ij}(G\,dW)_i(G\,dW)_j\ \longrightarrow\ \mathrm{Tr}(G^{T}\nabla^2V\,G)\,dt.$$
> 乘上前面的 $\tfrac12$，正是那个多出来的二阶漂移项。**这一项是随机微积分区别于牛顿微积分的全部秘密**——它不是近似误差，而是噪声在弯曲的 $V$ 上被"整流 (rectify)"出的真实确定性漂移。

> [!important] 那个二阶项 $\tfrac12\mathrm{Tr}(G^T\nabla^2V\,G)$ 的物理意义
> 它是**随机性引入的额外漂移**：噪声不仅加大方差，还**改变系统能量（代价）的期望演化方向**。确定性系统只需沿 $-\nabla V$ 下降；随机系统里若曲率 $\nabla^2V$ 大，噪声会产生一个额外的"力"推系统偏离确定性轨迹。这正是 MPPI（§6）能用噪声"探索"的数学根：**噪声修正了最优控制的梯度方向**。这条与 [[Optimization#3.2 非凸景观：鞍点、虚假极小与"好景观"的判据|优化的鞍点逃逸]]（扰动帮助逃离鞍点）是同一现象的两种语言。

### 2.3 马尔可夫性：它如何在推冰球里被破坏，又如何被"信念"救回

马尔可夫性断言 $p(x_{t+1}\mid x_t,u_t,\text{history})=p(x_{t+1}\mid x_t,u_t)$——"当前状态已概括预测未来所需的一切"。但推冰球在物理上常是**非马尔可夫**的：

1. **迟滞 (hysteresis)**：软指尖形变力不仅取决于当前压缩量，还取决于在加载还是卸载——这是记忆效应（见 [[SignalProcessing]] 的 Prandtl–Ishlinskii 模型）。
2. **隐变量**：摩擦系数随接触时间老化、随滑动产热而变；这些不在标准状态 $x=[q,\dot q]$ 里。

> [!important] 两条救法（决定你要不要上 RNN / 要不要 belief）
> - **状态增广**：把"滑动积分项""迟滞内部变量"塞进状态向量，恢复马尔可夫性。
> - **转入 POMDP / 信念空间**：承认状态不可知，改在 **belief** $b_t=p(x_t\mid z_{1:t},u_{1:t})$ 上规划。**深刻之处**：物理状态可能非马尔可夫，但**信念状态的演化在数学上是马尔可夫的**——我们放弃追踪物理状态，转而追踪"关于状态的知识"的演化。这与 [[ReinforcementLearning#2.1 MDP 与 POMDP：把"试错"写成数学|RL 的 POMDP→belief]] 是同一视角转换，§7 会把它做成规划目标。

------

## 3. 不确定性的分类：参数、结构、感知（治法各不相同）

> [!tip] 本节四拍
> **直觉**（"承认有不确定性"不够，要分清是哪一种）→ **推导**（三类的数学特征）→ **对比**（aleatoric vs epistemic：世界的随机 vs 我的无知）→ **落点**（分类决定治法：DR / GP / 粒子滤波）。

### 3.1 三类不确定性

**参数不确定性 (Parametric)**：模型结构已知、参数未知。最易处理。推冰球里就是**摩擦系数 $\mu$、冰球质量/质心未知**。建模为随机变量 $\theta\sim p(\theta)$（如 $\mu\sim\mathcal N_{trunc}(\bar\mu,\sigma^2,0,\infty)$ 保非负）。治法：**域随机化 (DR)**——每次仿真采一组参数，逼策略学会对参数不敏感，或隐式辨识（[[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|RL §9.2]]）。

**结构不确定性 (Structural)**：更危险——**方程 $f(x,u)$ 本身错或不全**。推冰球里就是**桌面纹理不均、冰球底部不规则**这种无法参数化的偏差；缆驱手的腱迟滞、软体形变（无限维）亦属此类。治法：**非参数残差** $\dot x=f_{nominal}(x,u;\theta)+g_{residual}(x,u)$，保留物理先验、用 GP/NN 学残差（§5）。

**感知不确定性 (Sensing)**：观测非理想。推冰球里就是**手挡住冰球→位置观测丢失**（遮挡是灵巧操作的致命伤）。观测方程 $z_t=h(x_t)+v_t,\ v_t\sim\mathcal N(0,R(x_t))$，且 $R$ 状态相关（遮挡时方差→∞）→ 非高斯多峰，催生粒子滤波（§4）。

| 类型 | 来源示例 | 数学特征 | 典型治法 |
|:--|:--|:--|:--|
| **参数** | $\mu$、质量未知 | $\theta\sim p(\theta)$ | DR、自适应控制、在线 SysID |
| **结构** | 桌面纹理、腱迟滞、软体 | $f(\cdot)$ 形式未知 | GP 回归、残差物理网络 |
| **感知** | 遮挡、传感噪声 | $h(\cdot)$ 非高斯/多峰 | 粒子滤波、信念空间、主动感知 |

### 3.2 一个必须刻进脑子的区分：Aleatoric vs Epistemic

> [!important] 偶然 vs 认知——决定"该探索还是该保守"
> - **Aleatoric（偶然）**：世界本身的随机（冰球底下那粒灰尘）。再多数据也消不掉，只能建模。
> - **Epistemic（认知）**：我的模型无知（从没推过这片桌面区域）。**多采数据就能消**。
>
> 为什么生死攸关：① 安全控制要在 **epistemic 高**处保守/减速（我不懂这里），而非在 aleatoric 高处瞎保守；② 主动探索（§7）应奔向 **epistemic 高**的区域（那里学得到东西），而非 aleatoric 高（那里只有噪声）。**GP（§5）的预测方差能区分二者，这正是它压过普通神经网络的关键**；输出分布的熵只能抓 aleatoric（见 [[ReinforcementLearning#6.1 Model-Based RL：在想象中转笔|RL ensemble 抓 epistemic]]、[[InformationTheory]] 的信息增益）。
>
> **把 epistemic 算子化成信息增益（BALD 的桥）**：上面说"奔向 epistemic 高处探索"，但"高多少、该采哪个观测"需要一个可优化的标量。[[InformationTheory#2.2 互信息：观测的"切割能力"|互信息]] 给出算子化答案——BALD (Bayesian Active Learning by Disagreement) 把一次观测能消掉的 epistemic 写成参数 $\theta$ 与观测 $z$ 的互信息（$\theta$=未知动力学参数如 $\mu$、$z$=候选观测如"轻推后的位移"、$\mathcal D$=已有数据）：
> $$\mathbb I(\theta;z\mid\mathcal D)=\underbrace{\mathbb H[z\mid\mathcal D]}_{\text{总预测熵（含 aleatoric）}}-\underbrace{\mathbb E_{\theta\sim p(\theta\mid\mathcal D)}\,\mathbb H[z\mid\theta,\mathcal D]}_{\text{给定参数后的平均熵（纯 aleatoric）}}.$$
> **两项相减把 aleatoric 精确抵消，余下的差额恰是 epistemic**：直觉上"总的不确定"里，"就算我完全知道 $\theta$ 也还剩的那部分"（第二项）是世界的随机、消不掉；减掉它，剩的就是"只因我不知 $\theta$ 而多出的不确定"——这正是这次观测能带来的信息增益。于是 §7 的"奔向 epistemic 高处"严格等价于"挑 $\mathbb I(\theta;z)$ 最大的观测"，而 ensemble/GP 成员间的**分歧**正是这个互信息的采样近似（挂在 §1 **认知不确定性三用**暗线：ensemble 分歧 = epistemic = 信息增益）。

------

## 4. 信念更新：从 EKF 失效到粒子滤波

> [!tip] 本节四拍
> **直觉**（盲推冰球：看不见它，只能靠手腕受力反推"它在哪、滑了没"）→ **推导**（贝叶斯滤波；EKF 的线性高斯假设为何在接触处崩）→ **对比**（EKF 单峰 vs 粒子滤波多峰）→ **落点**（CPF/MPF：把粒子约束在机器人表面流形上做接触定位）。

**核心问题**：不靠触觉皮肤、只凭本体感知（关节角、关节力矩），如何估计外部接触状态？这是"盲操作"的关键。

### 4.0 贝叶斯滤波的骨架：预测-更新递推（KF→EKF→UKF→PF 一张阶梯）

所有滤波器（KF/EKF/UKF/PF）都是**同一个贝叶斯递推的不同近似**，只在"用什么表示后验、怎么算两个积分"上分家。设状态 $x_t$、控制 $u_t$、观测 $z_t$，目标是维护后验 $p(x_t\mid z_{1:t})$。递推分两拍：

**① 预测（时间更新，用动力学把信念往前推）**——Chapman–Kolmogorov 方程：
$$p(x_t\mid z_{1:t-1})=\int \underbrace{p(x_t\mid x_{t-1},u_t)}_{\text{运动模型}}\,\underbrace{p(x_{t-1}\mid z_{1:t-1})}_{\text{上一步后验}}\,dx_{t-1}.$$
物理意义：把"上一刻关于状态的信念"沿动力学正向卷积，信念**变宽**（不确定性因过程噪声增长）。

**② 更新（观测更新，用新测量把信念收窄）**——Bayes 定理：
$$p(x_t\mid z_{1:t})=\frac{\overbrace{p(z_t\mid x_t)}^{\text{似然}}\,p(x_t\mid z_{1:t-1})}{\int p(z_t\mid x_t)\,p(x_t\mid z_{1:t-1})\,dx_t}\ \propto\ p(z_t\mid x_t)\,p(x_t\mid z_{1:t-1}).$$
物理意义：先验 × 似然 → 后验，信念**变窄**（观测消去了一部分不确定）。

难点在这两个积分一般**没有解析解**。四个滤波器就是四种"怎么算这两个积分"的妥协，构成一条**从便宜到通用**的阶梯：

| 滤波器 | 后验表示 | 两个积分怎么算 | 何时够用 / 何时崩 |
|:--|:--|:--|:--|
| **KF** | 单峰高斯 $(\mu,\Sigma)$ | $f,h$ **线性** + 高斯噪声 → 积分**闭式**、后验严格保持高斯 | 线性系统精确；接触/几何非线性下失效 |
| **EKF** | 单峰高斯 | 把 $f,h$ 在当前 $\mu$ 处**一阶 Taylor 线性化**（Jacobian $F,H$），再套 KF 公式 | 弱非线性够用；接触处**线性化误差爆炸**（§4.1） |
| **UKF** | 单峰高斯 | 不求导：撒 $2n{+}1$ 个 **sigma 点**过**真实**非线性 $f/h$，再由样本反推均值/协方差（捕捉到二阶矩） | 强非线性优于 EKF，但**仍假设单峰**，多峰后验照样崩 |
| **PF** | 一组加权粒子（任意形状） | 蒙特卡洛：预测=粒子过动力学 + 采噪，更新=按似然重赋权 + 重采样 | **多峰/非高斯通吃**（§4.2 的出路）；代价是粒子数随维度爆炸 |

以 KF 为例把"闭式"写实（每个符号标物理意义）——预测拍 $\hat\mu_t^-=F\hat\mu_{t-1}+Bu_t$、$\Sigma_t^-=F\Sigma_{t-1}F^{T}+Q$（$F$=状态转移矩阵、$Q$=过程噪声协方差 [状态量²]，让信念变宽）；更新拍先算**卡尔曼增益** $K_t=\Sigma_t^-H^{T}(H\Sigma_t^-H^{T}+R)^{-1}$（$H$=观测矩阵、$R$=观测噪声协方差 [观测量²]），再 $\hat\mu_t=\hat\mu_t^-+K_t(z_t-H\hat\mu_t^-)$、$\Sigma_t=(I-K_tH)\Sigma_t^-$。$K_t$ 的物理意义是**信任分配**：观测越准（$R$ 小）$K_t$ 越大、越信新测量；先验越准（$\Sigma_t^-$ 小）$K_t$ 越小、越信预测。EKF 只是把这里的常数 $F,H$ 换成在 $\mu$ 处**现算的 Jacobian**——**这也埋下 §4.1 的雷：接触瞬间力从 0 跳到 $F_N$，Jacobian 无定义，整套公式失去依据**。

> [!note] 跨模块联系（POMDP → belief → latent 暗线）
> 这条 KF→EKF→UKF→PF 阶梯与 [[SignalProcessing#5.2 演进脉络：KF → EKF → UKF → PF → 因子图|信号处理的状态估计演进]] 是**同一条阶梯的两处出口**：信号处理用它从触觉波形估状态、随机过程用它做接触定位。再往上一层，"维护 belief 的这套预测-更新递推"正是 [[WorldModels#2.1 演进脉络：从 Dyna 到 RSSM 到 Transformer 世界模型|RSSM]] 用神经网络学的东西——RSSM 的 recurrent 隐状态就是一个**学出来的、隐空间里的贝叶斯滤波器**，把这里手写的两拍换成可学习的门控更新（承接 §2.3 的 POMDP→belief→latent）。

### 4.1 EKF 为何在接触处失效

EKF 依赖动力学线性化（Jacobian $F_k=\partial f/\partial x$）与高斯噪声假设。但接触动力学本质**非光滑 + 多峰**：

- **不连续**：从"未接触"到"接触"，力从 0 瞬跳到 $F_N$；线性化误差极大，Jacobian 在接触瞬间甚至无定义。
- **多峰**：推冰球时"推到了/没推到"对应后验 $p(x\mid z)$ 的**双峰**。EKF 强行用单峰高斯拟合，估计均值落在两峰之间（"半接触"），物理上荒谬、方差被错误放大。

**出路：粒子滤波 (Particle Filter, SMC)**——用一组加权样本近似任意形状后验。它能**同时持有"推到了"和"没推到"两个假设**，直到新观测（力反馈）消去其一；不需可微性，天然适配接触的硬非线性。

### 4.2 Contact Particle Filter (CPF) 与 Manifold Particle Filter (MPF)

> [!tip] 物理直觉：黑屋里用手杖探路
> 你不知道手杖碰到了哪一点（接触位置 $r$），但碰到时手腕能感到反作用力矩（残差 $\gamma$）。CPF 的核心是**基于残差的假设检验**：若在假设接触点 $r^{[i]}$ 施加一个合物理（在摩擦锥内）的力，能完美解释观测到的关节力矩残差 $\gamma$，该假设权重就高。

三个关键组件：

1. **残差观测器**：从电机电流分离出外部接触力矩 $\gamma=\tau_{meas}-(\hat M\ddot q+\hat C\dot q+\hat g)\approx J^Tf_{ext}$（依赖 [[Dynamics#5.2 RNEA：$O(N)$ 逆动力学（控制的基石）|逆动力学]]）。
2. **观测模型（精髓）**：给定假设点 $r^{[i]}$，解一个 QP——"该点是否存在摩擦锥内的力 $f$，使 $J(r^{[i]})^Tf$ 最接近 $\gamma$？" 似然 $p(\gamma\mid r^{[i]})\propto\exp(-\lambda\cdot\mathrm{error}^{[i]})$。
3. **流形投影 (MPF)**：标准 PF 运动更新加噪后粒子会飞离机器人表面；MPF 在加噪后**立即投影回最近表面**，保证物理一致性，避免在"虚空"里找接触点。

```python
import numpy as np
# Contact Particle Filter 核心更新逻辑（去防御代码，聚焦数学）
class ContactParticleFilter:
    def __init__(self, num_particles, robot_model, friction_coeff=0.5):
        self.N, self.robot, self.mu = num_particles, robot_model, friction_coeff
        self.particles = self.robot.sample_surface_uniform(self.N)   # 粒子=机器人表面上的假设接触点
        self.weights = np.ones(self.N) / self.N

    def update(self, torque_residual, joint_angles):
        # 1) 运动更新（流形上的扩散）：加噪后投影回表面
        self.particles += np.random.normal(0, 0.01, self.particles.shape)
        self.particles = self.robot.project_to_surface(self.particles)     # ★ MPF 的关键
        # 2) 观测更新：每个假设点解最小二乘力 + 摩擦锥检验
        for i in range(self.N):
            pt = self.particles[i]
            J_pt = self.robot.get_jacobian(joint_angles, pt)              # 接触力→关节力矩
            f_opt, residual, *_ = np.linalg.lstsq(J_pt.T, torque_residual, rcond=None)
            n = self.robot.get_normal(pt); f_n = f_opt @ n               # 法向分量
            f_t = f_opt - f_n * n                                        # 切向分量
            if f_n < 0:                                                  # 拉力→接触不可能
                like = 1e-10
            elif np.linalg.norm(f_t) > self.mu * f_n:                    # 出摩擦锥→不太可能静接触
                like = np.exp(-10.0 * residual) * 0.1
            else:                                                        # 解释得好
                like = np.exp(-10.0 * residual)
            self.weights[i] = like
        self.weights /= (self.weights.sum() + 1e-8)
        # 3) 系统重采样 + 返回加权均值（估计接触点）
        self.particles = self.particles[self._systematic_resample(self.weights)]
        est = np.average(self.particles, axis=0, weights=self.weights)
        self.weights = np.ones(self.N) / self.N
        return est
```

> [!note] 跨原理联系
> CPF 的"解 QP 求解释力"与 [[ContactMechanics#3.1 抓取矩阵的严格定义与内力|抓取矩阵]]、[[Optimization#2.3 KKT 条件：约束最优的"语法"|力分配 QP]] 同源；其"多峰后验"正是 [[SignalProcessing|状态估计从 KF 到 PF]] 的演进动机。**同一个贝叶斯滤波框架，信号处理用它融合触觉、随机过程用它做接触定位、RL 用它当 belief 编码器。**

> [!important] 补严：RBPF——用 Rao-Blackwell 定理把粒子数从"指数爆炸"拉回可用
> §4.0 阶梯的末端说"PF 通吃多峰，代价是粒子数随维度爆炸"。**Rao-Blackwellized Particle Filter (RBPF)** 是这句代价的正面解药，也是把 §4 的粒子滤波真正用上高维接触状态的关键一步。思想只有一句：**能解析积分的维度，就别用采样去糊弄它**。
> 把状态劈成两块 $x=(x^n,x^l)$：$x^n$=**非线性/离散**子状态（如接触模式"推到了/没推到"、接触点落在哪个面片——正是逼出多峰的那部分），$x^l$=**条件线性高斯**子状态（如给定接触模式后的物体位姿，其动力学/观测对 $x^l$ 是线性高斯的）。后验按链式法则**精确因式分解**（无任何近似，纯概率恒等式）：
> $$p(x^n_{1:t},x^l_t\mid z_{1:t})=\underbrace{p(x^n_{1:t}\mid z_{1:t})}_{\text{粒子采样（低维、多峰）}}\;\cdot\;\underbrace{p(x^l_t\mid x^n_{1:t},z_{1:t})}_{\text{解析 KF（每个粒子挂一台 KF）}}.$$
> 第二个因子在给定粒子的模式轨迹 $x^n_{1:t}$ 后**严格是高斯**，于是用一台卡尔曼滤波器闭式求出（每个粒子携带自己的 $(\mu^l,\Sigma^l)$），**只有低维的 $x^n$ 需要撒粒子**。
> **为什么粒子数骤减（Rao-Blackwell 定理的严格保证）**：定理说"对一个无偏估计量，把它对充分统计量取条件期望（=解析积分掉一部分随机性），所得估计量方差**不增**（一般严格减）"。这里"解析积分掉 $x^l$"正是对 $x^l$ 做了条件期望，故 RBPF 估计量方差严格低于对全 $x$ 盲采的普通 PF——**同样精度所需粒子数按被解析掉的维度指数级下降**，直接缓解 §4.0 表里"粒子数随维度爆炸"的诅咒。
> 挂 §1 **POMDP → belief → latent** 暗线：RBPF 是"belief 的结构化分解"——把 belief 拆成"必须采样的难部分 + 可闭式的易部分"，与 [[WorldModels#2.1 演进脉络：从 Dyna 到 RSSM 到 Transformer 世界模型|RSSM]] 把 latent 拆成 stochastic + deterministic 两支是**同一记账思想**（该随机的随机、该确定的确定）。信息论侧的同一对象见 [[InformationTheory#4.1 粒子滤波与 RBPF：表达多峰信念|InformationTheory §4.1 的 RBPF]]——那里从信息增益角度用它，这里从状态估计角度用它，是一枚硬币两面。

------

## 5. 学习未知动力学：高斯过程与残差学习

> [!tip] 本节四拍
> **直觉**（解析摩擦模型不准，能不能用数据学这片桌面的"脾气"？）→ **推导**（残差学习 = 物理先验 + 数据修补）→ **对比**（GP vs 神经网络：样本效率 + 不确定性量化）→ **落点**（核函数选择编码"动力学有多光滑"；Local GP 保实时）。

### 5.1 从系统辨识到残差回归

**系统辨识**假设结构已知（$F=ma+\mu N+C\dot q$），最小二乘求参数——处理不了**结构不确定性**（若摩擦还非线性依赖温度/磨损就欠拟合）。**现代共识：不抛弃物理模型，而是修补它**：

$$f_{real}(x,u)=\underbrace{f_{nominal}(x,u;\theta)}_{\text{刚体主体（强外推）}}+\underbrace{g_{residual}(x,u)}_{\text{数据学的未建模项}}.$$

推冰球里，$f_{nominal}$ 给"匀减速滑行"的主体，$g_{residual}$ 捕捉这片桌面特有的纹理摩擦。

### 5.2 为什么用高斯过程 (GP) 而非神经网络

> [!important] GP 的两个决定性优势（在机器人上压过 NN）
> 1. **样本效率**：真机实验极贵；NN 常需数万条数据，GP 基于贝叶斯推断，几百到几千点就表现优异。
> 2. **不确定性量化**：GP 输出**均值 $\mu(x)$ + 方差 $\Sigma(x)$**。方差量化 **epistemic 不确定性**（§3.2）——没去过的桌面区域，GP 在那儿输出大方差。控制器据此在不确定区降增益/减速，或主动去探索降不确定（**主动学习**，接 §7）。**这正是 §3.2 "区分 aleatoric/epistemic" 的算法兑现。**

> [!note] 逐步推导：后验均值/方差从哪来（§5.3 代码里的 `mean`/`var` 就是这么来的）
> GP 的定义：函数在任意有限组输入上的取值**联合高斯**。给定训练输入 $X=\{x_i\}$、带噪观测 $y_i=f(x_i)+\varepsilon_i,\ \varepsilon_i\sim\mathcal N(0,\sigma_n^2)$，和一个查询点 $x_*$，则"训练值 $y$ + 查询值 $f_*$"服从联合高斯（取零均值先验）：
> $$\begin{bmatrix}y\\ f_*\end{bmatrix}\sim\mathcal N\!\left(0,\ \begin{bmatrix}K+\sigma_n^2 I & k_*\\ k_*^{T} & k_{**}\end{bmatrix}\right),$$
> 其中 $K_{ij}=k(x_i,x_j)$（训练点两两协方差 [残差量²]）、$k_*=[k(x_i,x_*)]_i$（查询点与各训练点的协方差向量）、$k_{**}=k(x_*,x_*)$（查询点先验方差）、$\sigma_n^2$=观测噪声方差（**aleatoric**）。
>
> 对联合高斯用**条件公式**（"已知 $y$ 求 $f_*$"，标准高斯条件化，无需任何额外假设）直接得后验 $p(f_*\mid y)=\mathcal N(\mu_*,\sigma_*^2)$：
> $$\mu_*=k_*^{T}(K+\sigma_n^2 I)^{-1}y,\qquad \sigma_*^2=\underbrace{k_{**}-k_*^{T}(K+\sigma_n^2 I)^{-1}k_*}_{\text{epistemic：模型无知}}+\underbrace{\sigma_n^2}_{\text{aleatoric：世界噪声}}.$$
> 对照 §5.3 代码：`alpha`$=(K+\sigma_n^2I)^{-1}y$（Cholesky 解出，数值稳定）、`mean`$=k_*^{T}\alpha$、`var`$=k_{**}-\lVert v\rVert^2+\sigma_n^2$（其中 $v=L^{-1}k_*$，故 $\lVert v\rVert^2=k_*^{T}(K+\sigma_n^2I)^{-1}k_*$）——逐项一一对应。
>
> **决定性观察（这才是 §3.2 的严格兑现）**：方差 $\sigma_*^2$ **只依赖输入位置 $X,x_*$，完全不含 $y$ 的取值**。查询点离训练数据近 → $k_*$ 大 → 减掉一大块 → $\sigma_*^2$ 小（我懂这里）；远离数据 → $k_*\to0$ → $\sigma_*^2\to k_{**}$ 回到先验方差（我不懂这里）。**这就是"GP 方差 = epistemic 不确定性"的严格来历**：它度量"数据覆盖到没覆盖到"，而非标签噪声。据此，控制器在 $\sigma_*^2$ 大处减速/降增益、探索器奔 $\sigma_*^2$ 大处采数据（§7）。这与 [[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性|PETS 用 bootstrap ensemble 分歧抓 epistemic]] 殊途同归（GP 用核方差、PETS 用集成方差，量化的是同一个"认知不确定性"，是 §1 **认知不确定性三用**暗线的两种实现）；两者的方差都可直接当 [[InformationTheory#4.2 信息增益目标与粒子近似|信息增益]] 的代理去驱动主动探索。

**核函数 (kernel) 编码"动力学有多光滑"**：$k(x,x')=\mathrm{Cov}(f(x),f(x'))$。

- **平方指数 (SE)** $k=\sigma^2\exp(-r^2/2l^2)$：假设无限可微（极平滑）。
- **Matérn**：物理动力学常**不是无限光滑**的（加速度连续，但 jerk 会因接触碰撞而跳变）。Matérn $\nu=3/2$ 或 $5/2$ 只要求一/二次可微，更贴合真实接触动力学——**核选择即物理先验**。

### 5.3 Local GP：把 $O(N^3)$ 压到实时

全量 GP 推理需对协方差矩阵求逆，$O(N^3)$，撑不住 1kHz 控制。**Local/Sparse GP** 只用查询点附近 $K$ 个最近邻，复杂度降到 $O(K^3)$：

```python
import numpy as np
from scipy.spatial.distance import cdist
# Local Gaussian Process：实时动力学学习（只用 k 近邻，复杂度与总数据量无关）
class LocalGaussianProcess:
    def __init__(self, length_scale=1.0, sigma_f=1.0, sigma_n=0.01, max_buffer=2000):
        self.X, self.Y = [], []                          # 状态库 / 残差库（滚动缓冲）
        self.l, self.sf, self.sn = length_scale, sigma_f, sigma_n
        self.max_buffer = max_buffer

    def matern_kernel_32(self, x1, x2):                   # k(r)=sf²(1+√3 r/l)exp(-√3 r/l)
        r = np.sqrt(3) * cdist(x1, x2, 'euclidean') / self.l
        return (self.sf**2) * (1 + r) * np.exp(-r)

    def add_data(self, x_new, y_new):
        if len(self.X) >= self.max_buffer: self.X.pop(0); self.Y.pop(0)
        self.X.append(x_new); self.Y.append(y_new)

    def predict(self, x_query, k_nearest=50):
        X, Y = np.array(self.X), np.array(self.Y)
        idx = np.argsort(np.sum((X - x_query)**2, axis=1))[:k_nearest]   # 1) 找 k 近邻
        Xl, Yl = X[idx], Y[idx]
        K = self.matern_kernel_32(Xl, Xl) + np.eye(len(Xl)) * self.sn**2 # 2) 协方差 + 噪声正则
        k_m = self.matern_kernel_32(Xl, x_query.reshape(1, -1))          # 3) 交叉协方差
        L = np.linalg.cholesky(K)                                        # 4) Cholesky 解，数值稳定
        alpha = np.linalg.solve(L.T, np.linalg.solve(L, Yl))
        mean = k_m.T @ alpha                                             # 预测均值
        v = np.linalg.solve(L, k_m)
        var = self.sf**2 - v.T @ v + self.sn**2                          # 预测方差 = epistemic + aleatoric
        return mean.flatten(), var.flatten()
```

> [!note] 跨原理联系
> GP 残差学习是 [[Dynamics#9. 适配层：可微物理与神经动力学|Dynamics 的神经动力学]]、[[ReinforcementLearning#6.1 Model-Based RL：在想象中转笔|MBRL 世界模型]] 的贝叶斯版本；其 epistemic 方差正是 [[ControlTheory#12. 自适应控制与确定性等价|自适应控制]] 里"参数还没辨识准"的概率刻画，也是 §7 主动感知与 [[InformationTheory|信息增益]]的驱动量。

------

## 6. 随机最优控制：MPPI（用采样代替梯度）

> [!tip] 本节四拍
> **直觉**（推冰球的接触动力学不可微，iLQR 的梯度会指错方向——能不能不用梯度？）→ **推导**（路径积分 / 自由能 / 重要性采样）→ **对比**（基于梯度 iLQR vs 无梯度 MPPI）→ **联系**（温度 $\lambda$ ↔ [[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|SAC 熵温度]]、[[Optimization#7.3 基于采样：MPPI（用并行换梯度）|Optimization MPPI]]）。

### 6.1 为什么 MPPI 适合灵巧操作

iLQR/DDP（[[Optimization#6. 核心算法实现：iLQR/DDP 与"让梯度穿过接触"的三方案|见 Optimization §6]]）依赖动力学可微、要算 $\nabla_uf$。但推冰球的接触充满不连续：接触边缘梯度不连续、甚至数值上指向错误方向；接触流形多局部极小。**MPPI 的范式转移：基于采样的无梯度优化**——不求导，用高斯噪声"轰炸"系统、并行模拟上千条轨迹、按代价概率加权更新。天然适配不可微接触。

### 6.2 物理根：自由能最小化与重要性采样

MPPI 的数学根是**信息论对偶 / 路径积分**。随机最优控制可转化为路径积分估计：找一个控制分布使系统**自由能**最小。由 Feynman–Kac 定理，最优控制序列的概率与轨迹代价指数成正比：

$$
F=-\lambda\log\mathbb E_{\mathbb Q}\big[\exp(-S(\xi)/\lambda)\big].
$$

低代价轨迹 $\xi_i$ 获得极高权重。**温度 $\lambda$**（类比统计力学温度）：$\lambda\to0$ 只认代价最低的单条（贪婪）；$\lambda\to\infty$ 一视同仁（随机游走）；适中则平衡探索-利用。

> [!note] 逐步推导：从"自由能最小"到 $\omega_k=\mathrm{softmax}(-S/\lambda)$（那步权重不是拍脑袋）
> 上式只给了自由能，还没告诉你该怎么挪控制。补上中间三步：
> 1. **变分最优分布是 Gibbs 分布**。在所有轨迹分布 $q$ 中，最小化"期望代价 $+\lambda\,\mathrm{KL}(q\,\Vert\,p)$"这个自由能泛函（$p$=无控制的被动动力学轨迹分布），其最优解有闭式（KL 正则变分问题的标准结论，用 $\delta/\delta q$ 加归一化约束一解即得）：
> $$q^*(\xi)=\frac1Z\,p(\xi)\,\exp\!\big(-S(\xi)/\lambda\big),\quad Z=\int p(\xi)\,e^{-S(\xi)/\lambda}\,d\xi.$$
> $q^*$=最优轨迹分布、$p(\xi)$=被动（零控制）轨迹先验、$S(\xi)$=轨迹总代价 [代价单位]、$\lambda$=温度、$Z$=配分函数。**代价越低的轨迹，$q^*$ 给的概率指数级越高**——这就是"低代价获高权重"的严格来历。
> 2. **$q^*$ 采不了（$Z$ 是高维积分），改用重要性采样**。我们能采的是"标称控制 $U$ + 高斯噪声 $\epsilon$"这个**提议分布** $q_U$。任意期望满足 $\mathbb E_{q^*}[\,\cdot\,]=\mathbb E_{q_U}[\tfrac{q^*}{q_U}\cdot]$，重要性权重 $w(\xi)\propto q^*(\xi)/q_U(\xi)$。把高斯提议 $q_U$ 与被动先验 $p$ 的密度比代入（控制仿射 + 同一噪声协方差时，$p/q_U$ 恰好贡献二次型控制代价，可并入 $S$），指数里只剩轨迹代价：$w_k\propto\exp(-S(\xi_k)/\lambda)$，归一化即 $\omega_k=\mathrm{softmax}(-S(\xi_k)/\lambda)$。
> 3. **最优控制 = 在 $q^*$ 下取期望动作**，用样本近似就是 $u_t\leftarrow\sum_k\omega_k(U_t+\epsilon_t^k)$——§6.3 第⑤步的"加权平均扰动"正是这个期望的蒙特卡洛估计，一步不多、一步不少。
>
> **跨模块联系（采样+加权 暗线）**：这套"采一批 → 按代价/回报指数加权 → 把分布挪向好样本"与 [[Optimization#4.4 零阶与进化优化：当梯度根本求不出来（CMA-ES）|CMA-ES]]（在**参数空间**采、按 fitness 加权挪均值/协方差）、[[ReinforcementLearning#4.1 策略梯度定理：log-derivative 技巧|策略梯度]]（在**动作空间**采、按 advantage 加权挪策略）是**同一台机器的三种投影**——MPPI 在**控制序列空间**做它。认出这点，三个算法的"更新公式"其实是一个。

> [!important] 一把旋钮，四处现身
> MPPI 的 $\lambda$、内点法的 barrier $\mu$（[[Optimization#4.3 内点法：沿"中心路径"把约束问题变成一串 Newton|Optimization §4.3]]）、SAC 的熵温度 $\alpha$（[[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|RL §5.2.3]]）、同伦的 $\lambda$——**都是"从软/探索连续过渡到硬/利用"的同一把温度旋钮**。认出这一点，四个领域的"超参数玄学"就统一了。

### 6.3 算法与实现

五步循环（GPU 上 50–100Hz 并行 4096+ 条）：① **探索**：在标称控制序列 $U$ 上叠高斯噪声 $\epsilon\sim\mathcal N(0,\Sigma)$；② **Rollout**：并行模拟 $x_{t+1}=f(x_t,u_t+\epsilon_t)$；③ **评估**：算每条代价 $S(\tau_k)$；④ **重加权** $\omega_k=\mathrm{softmax}(-S(\tau_k)/\lambda)$；⑤ **更新** $u_t\leftarrow u_t+\sum_k\omega_k\epsilon_t^k$（对所有扰动加权平均，而非只选最优一条——这给控制律做了平滑）。

```cpp
// MPPI 核心逻辑（概念性 CUDA kernel + host 更新）
__global__ void mppi_rollout(float* costs, const float* U, const float* E, const float* x0) {
    int k = blockIdx.x * blockDim.x + threadIdx.x;        // 轨迹索引
    if (k >= NUM_SAMPLES) return;
    State x = load_state(x0);  float cost = 0.f;
    for (int t = 0; t < HORIZON; t++) {
        float u[M];
        for (int m = 0; m < M; m++) {
            u[m] = U[t*M+m] + E[(k*HORIZON+t)*M+m];      // 标称 + 噪声
            u[m] = fminf(fmaxf(u[m], U_MIN), U_MAX);      // 执行器限幅
        }
        step_dynamics(x, u);                              // 黑盒物理：不同噪声样本自动探索不同接触模式
        cost += compute_cost(x, u);
        if (t == HORIZON-1) cost += terminal_cost(x);
    }
    costs[k] = cost;                                       // 危险轨迹(穿透/速度爆炸)应置 +inf → 权重归零
}
void mppi_update(float* U, const float* E, const float* costs) {
    float cmin = find_min(costs), Z = 0.f; std::vector<float> w(NUM_SAMPLES);
    for (int k = 0; k < NUM_SAMPLES; k++) { w[k] = expf(-(costs[k]-cmin)/LAMBDA); Z += w[k]; } // softmax 防下溢
    for (int k = 0; k < NUM_SAMPLES; k++) w[k] /= Z;
    for (int t = 0; t < HORIZON; t++)                      // 路径积分更新 = 加权平均扰动
        for (int m = 0; m < M; m++) {
            float dn = 0.f;
            for (int k = 0; k < NUM_SAMPLES; k++) dn += w[k] * E[(k*HORIZON+t)*M+m];
            U[t*M+m] += dn;
        }
    shift_control_sequence(U);                             // receding horizon：左移一格
}
```

> [!tip] 两个工程要点 + 两条跨域伏笔
> - **防御性采样**：穿透物体/关节速度爆炸的轨迹代价设 $\infty$、权重归零，防危险动作污染控制序列。
> - **Robust/Tube-MPPI**：在初始状态 $x_0$ 也叠感知噪声，提高对状态估计误差的鲁棒（接 §8）。
> - **AR 探索噪声**（[[Autoregressive Policies for Continuous Control Deep Reinforcement Learning|ARP]]）：把白噪声 $\epsilon_t$ 换成 AR-p 过程 $\epsilon_t=\sum_i\phi_i\epsilon_{t-i}+\eta_t$，**边缘分布不变但时间相关**——避免高频抖动、生成更合物理的探索路径（与 [[ReinforcementLearning#5.4.1 时间一致探索：从白噪声到自回归过程|RL 时间一致探索]]同源）。
> - **连续时间熵正则**（[[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach|Exploration vs Exploitation]]）：MPPI 的 $\lambda$ 在连续极限下正是随机 HJB 里的熵正则系数——**MPPI 不是经验主义算法，而是熵正则随机控制的蒙特卡洛近似**。这把 MPPI 与 [[ControlTheory#11. 线性二次最优控制 (LQR)|最优控制]]、RL 的最大熵彻底打通。

### 6.4 扩散策略 = 学出来的逆向 SDE：把 §2 的 SDE 倒过来跑

全篇多处说"扩散策略 = 学出来的 SDE"，这里把它讲实——它就是把 §2 的 SDE **倒着跑**。

**前向 SDE（加噪，把数据揉成高斯）**：对动作/轨迹 $x_0\sim p_{data}$，定义一条随时间 $t:0\to T$ 逐步注入噪声的 SDE
$$dx=f(x,t)\,dt+g(t)\,dW,$$
$f(x,t)$=漂移（如 VP-SDE 的 $-\tfrac12\beta(t)x$，把数据往原点收）、$g(t)$=噪声强度 [$\cdot/\sqrt{\mathrm s}$]、$dW$=维纳增量。跑到 $t=T$ 时 $x_T$ 已是**纯高斯噪声**——数据结构被完全抹平。这正是 §1"Continuation/平滑化"暗线里"从平滑近凸的高斯出发"的那一端。

**逆向 SDE（去噪，把高斯长回数据）**：Anderson (1982) 时间反演定理给出——上式对应一条**逆时** SDE（$t:T\to0$）：
$$dx=\big[f(x,t)-g(t)^2\,\underbrace{\nabla_x\log p_t(x)}_{\text{score 分数}}\big]dt+g(t)\,d\bar W,$$
$p_t(x)$=时刻 $t$ 的边缘密度、$d\bar W$=逆时维纳增量。唯一新东西是那个多出来的漂移 $-g^2\nabla_x\log p_t(x)$：**score function** $\nabla_x\log p_t(x)$=对数概率密度的梯度，指向"数据更密"的方向，物理上是一把把噪声样本推回数据流形的力。

> [!important] "学出来的 SDE"到底学什么
> 逆向 SDE 里 $f,g$ 都是已知设计量，**唯一未知的是 score** $\nabla_x\log p_t(x)$。扩散模型用网络 $s_\theta(x,t)\approx\nabla_x\log p_t(x)$（denoising score matching / $\epsilon$-prediction 训练）把它**学出来**——学到 score，逆向 SDE 就完全确定，于是**采样 = 数值积分这条逆向 SDE = 迭代去噪**。这就是"扩散 = 学出来的逆向 SDE"的字面含义。
>
> 两个回扣：① 那个 score 漂移项与 §2.2 Itō 引理里"噪声诱导的额外漂移"**是同一类物体**——都是噪声在概率景观上被整流出的确定性方向修正；② 把 score 条件化到观测 $o$（$s_\theta(a,t\mid o)$ 的分数条件在图像/触觉上）、在**动作空间**跑逆向 SDE，就是 [[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器|扩散策略]]——它天生输出**多峰**动作分布，正好解 §4 反复出现的"多峰后验"顽疾。这是 §1"扩散 ↔ 表征学习"暗线的落点。

------

## 7. 信念空间规划：为感知而行动

> [!tip] 本节四拍
> **直觉**（"要不要先轻推一下试试摩擦"——这动作不为移动，只为获取信息）→ **推导**（在 belief $(\mu,\Sigma)$ 上规划，动力学变成滤波更新）→ **对比**（物理状态空间 vs 信念空间）→ **落点**（信息增益目标自动产生主动感知行为）。

MPPI 解"如何行动"，信念空间规划 (BSP) 解**感知与行动的耦合**。推冰球里：**静止不动则 $\mu$ 不可观测；只有施力试推、观察滑或不滑，才提供关于 $\mu$ 的信息**。这种"为感知而行动"在纯物理状态空间里看似浪费（耗能却没把球推到位），在信念空间里却最优——它极大压缩了不确定性 $\Sigma$。

**高斯信念空间**：POMDP 难解，故设 belief $b_t$ 为高斯、由 $(\mu_t,\Sigma_t)$ 参数化。扩增状态 $x_{belief}=(\mu_t,\Sigma_t)$，其"动力学"是 EKF 更新方程 $(\mu_{t+1},\Sigma_{t+1})=\mathrm{EKF}(\mu_t,\Sigma_t,u_t,z_{t+1})$——**注意它不仅依赖物理，还依赖观测模型 $H_t$**。

**信息增益目标**：在代价里加不确定性惩罚

$$
J=\sum_t\Big[(\mu_t-x_{goal})^TQ(\mu_t-x_{goal})+u_t^TRu_t+\alpha\,\mathrm{Tr}(\Sigma_t)\Big].
$$

$\mathrm{Tr}(\Sigma_t)$ 项**逼规划器选信息丰富的路径**，自动产生"轻推试探""指尖滑动触摸"等主动感知行为（这正是 [[InformationTheory|信息论的主动感知]] 的控制版）。

> [!note] MLO 假设：把随机规划"确定性化"
> 规划时刻不知道未来观测 $z_{t+1}$（它是随机变量），对所有 $z$ 积分会爆炸。**最大似然观测 (MLO)** 假设未来观测正好等于预测值 $z_{t+1}^{exp}=h(f(\mu_t,u_t))$，于是可用标准 iLQR/MPPI 在信念空间规划。虽忽略了观测随机性，实践中已证明能产生高效鲁棒的主动感知策略。

> [!important] 从"惩罚方差"到风险敏感控制：$\exp$ 效用把 §6.2 自由能、§2.2 Itō 方差、§7 的 $\mathrm{Tr}(\Sigma)$ 拧成一根
> §7 的目标用 $\alpha\,\mathrm{Tr}(\Sigma_t)$ **手工**加了个不确定性惩罚项——但"该罚多少方差"其实有一个从最优控制内生长出来的答案：**风险敏感控制**。它不最小化期望代价 $\mathbb E[S]$，而是最小化**指数效用 (exponential utility)**（$S$=轨迹总代价 [代价单位]、$\gamma$=风险敏感系数 [1/代价单位]，使 $\gamma S$ 无量纲）：
> $$J_\gamma=\frac1\gamma\log\mathbb E\big[\exp(\gamma S)\big].$$
> **为什么这一个式子就等价于"均值 + 方差惩罚"**：把 $\log\mathbb E[e^{\gamma S}]$ 按 $\gamma$ 做小量展开——它正是 $S$ 的**累积量生成函数**，前两阶累积量就是均值与方差（$\mu_S=\mathbb E[S]$、$\sigma_S^2=\mathrm{Var}[S]$）：
> $$J_\gamma=\frac1\gamma\Big(\gamma\mu_S+\tfrac{\gamma^2}{2}\sigma_S^2+O(\gamma^3)\Big)=\underbrace{\mathbb E[S]}_{\text{名义代价}}+\underbrace{\tfrac{\gamma}{2}\mathrm{Var}[S]}_{\text{方差惩罚（自动出现）}}+O(\gamma^2).$$
> 于是 §7 里那个人手加的 $\alpha\,\mathrm{Tr}(\Sigma)$ **不再是拍脑袋的正则**——它是指数效用的二阶展开，系数 $\alpha$ 的物理身份就是风险敏感度 $\gamma/2$。**$\gamma>0$ 风险规避**（怕高代价的坏尾巴，抓玻璃时保守减力、躲 epistemic 高处——接 §3.2）；**$\gamma<0$ 风险偏好**（奖励方差、主动往不确定里钻去探索）；$\gamma\to0$ 退回风险中性 $\mathbb E[S]$。
> **决定性回扣（一根拧三处）**：① 与 §6.2 **自由能** $F=-\lambda\log\mathbb E[\exp(-S/\lambda)]$ 逐字对照，令 $\gamma=-1/\lambda$ 二者**完全相等**——**MPPI 的温度 $\lambda$ 本质就是一个风险敏感系数**（且 $\gamma=-1/\lambda<0$ 天然风险偏好，这正解释了 §6.3 那个 softmax 为何"乐观地"给低代价样本指数级高权，是内建的探索倾向）；② 展开式里 $\gamma$ 乘的 $\mathrm{Var}[S]$ 与 §2.2 Itō 引理中噪声整流出的二阶项 $\tfrac12\mathrm{Tr}(G^T\nabla^2V\,G)$ 是同一个"方差改变期望代价"的机制——风险敏感 HJB 里这一项正由 $\gamma$ 定标；③ 因此 §1 的**一把温度旋钮**（MPPI $\lambda$ / 内点 barrier / SAC 熵 $\alpha$）与"风险敏感度"是同一把旋钮的两种叫法，也与"采样+加权"暗线相通——[[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|SAC 的熵温度]]、[[ControlTheory#11. 线性二次最优控制 (LQR)|最优控制的确定性等价]]（$\gamma\to0$ 极限即 LQG 的 certainty-equivalence，方差项消失、规划退化成对均值规划）在这里被同一个 $\gamma$ 收编。

------

## 8. 随机互补：当接触本身是随机的

> [!tip] 本节四拍
> **直觉**（推冰球的摩擦阈值、接触间隙本身就是随机变量——LCP 的硬约束怎么办）→ **推导**（随机互补问题 SCP）→ **对比**（平滑化 vs Robust MPPI）→ **落点**（在仿真注入随机软接触 = 注入物理先验，利于 sim-to-real）。

回到一切算法的基石——物理引擎。标准刚体接触建模为 **LCP**：$0\le\lambda\perp\phi(q)\ge0$（要么距离 0 有力、要么距离正无力，详见 [[ContactMechanics#5.1 互补条件与 LCP 的构建|ContactMechanics §5.1]]）。其非光滑导致**梯度消失/爆炸 + 接触-分离间高频震荡 (Zeno)**。

**随机互补问题 (SCP)** 是 LCP 在不确定下的推广：当接触参数（$\mu$、刚度 $k$）本身随机 $\omega\in\Omega$ 时，

$$
M(\omega)\dot v=f_{ext}+J_n^T(\omega)\lambda_n+J_t^T(\omega)\lambda_t,\quad 0\le\lambda_n\perp\phi(q;\omega)\ge0,\quad \lambda_t\in\mathcal K(\mu(\omega),\lambda_n).
$$

难点：互补 $\perp$ 的满足依赖 $\omega$ 的实现，而决策时不知 $\omega$。**物理意义就是风险敏感抓取**：抓未知物体，$\mu$ 可能是玻璃 0.1 或橡胶 0.8——抓力 $\lambda_n$ 要在低 $\mu$ 时不滑落、高 $\mu$ 时不压坏。

**两条治法**：

| 路线 | 做法 | 优点 | 代价 |
|:--|:--|:--|:--|
| **平滑化（软接触）** | 互补条件换平滑函数 $\lambda\approx\frac1\epsilon\ln(1+e^{-\epsilon\phi})$ | 处处可微（可微物理）、更合微观事实 | 引入微小穿透 |
| **采样（Robust MPPI）** | 每条轨迹起始从 $p(\mu)$ 采一个摩擦系数、解该条 LCP、按指数权重聚合 | 保 LCP 精确、覆盖参数不确定 | 计算量大 |

> [!important] Sim-to-Real 洞见：随机软接触 = 注入物理先验
> 用随机/软 LCP 训练的策略 sim-to-real 更好——因为真实接触（软指肉、传感噪声）本就是"软"的。在仿真里注入这种随机平滑，等于在训练中注入物理先验，**防止策略过拟合到理想刚体模型**。这与 [[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|RL 的域随机化]]、[[ContactMechanics#6.2 实现可微的三条路径|可微接触]] 是同一思想的三处显形。

------

## 9. 知识回扣与记忆图：一枚冰球串起随机过程六层

> [!abstract] 用一条故事线把全讲复述一遍（刻意复述，为了记忆）
> 我们要把冰球推到目标，但桌面摩擦未知。**(§1)** 同样的力两次推出不同轨迹——确定性幻象破灭，我们决定拥抱随机性。**(§2)** 用 SDE 描述它：drift 是匀减速主体、diffusion 是 stick-slip 涨落且随速度而变；Itō 引理告诉我们噪声还会改变能量的漂移方向（这是后面用噪声探索的根）；而摩擦的迟滞与隐变量破坏了马尔可夫性，逼我们转向 belief。**(§3)** 把不确定性分成参数（$\mu$ 未知）、结构（桌面纹理）、感知（手挡住球），并分清 aleatoric（世界的随机）与 epistemic（我的无知）。**(§4)** 看不见球就用粒子滤波从手腕受力反推接触点（CPF/MPF），它能同时持有"推到了/没推到"两个假设。**(§5)** 用高斯过程学这片桌面的摩擦残差，它的方差恰好量化 epistemic 无知。**(§6)** 不可微就别求梯度——MPPI 撒上千条推法、按代价指数加权，温度 $\lambda$ 就是探索-利用旋钮。**(§7)** 干脆先轻推一下试摩擦——信念空间规划用 $\mathrm{Tr}(\Sigma)$ 把"为感知而行动"写进目标。**(§8)** 最后承认连接触阈值本身都是随机的（SCP），用软接触或 Robust MPPI 兜底。**一枚冰球，推完了整座随机过程大厦。**

> [!important] 一张表记住全篇（层 → 问题 → 工具 → 推冰球角色）
> | 层 | 核心问题 | 关键工具 | 冰球的哪一难 |
> |:--|:--|:--|:--|
> | §2 随机动力学 | 状态为何非单轨 | SDE、Itō、状态相关扩散 | stick-slip 噪声随速度变 |
> | §2 马尔可夫 | 单帧够不够 | POMDP、belief、状态增广 | 看不见 $\mu$/滑移史 |
> | §3 不确定性分类 | 是哪种不确定 | 参数/结构/感知、aleatoric/epistemic | 该探索还是该保守 |
> | §4 信念更新 | 多峰后验怎么估 | EKF→粒子滤波、CPF/MPF | "推到了没"双峰 |
> | §5 非参数学习 | 未知动力学怎么学 | 高斯过程、Matérn 核、Local GP | 学桌面摩擦残差 |
> | §6 随机控制 | 不可微怎么优化 | MPPI、路径积分、温度 $\lambda$ | 撒千条推法加权 |
> | §7 信念规划 | 感知-行动耦合 | 信息增益 $\mathrm{Tr}(\Sigma)$、MLO | 轻推试摩擦 |
> | §8 随机互补 | 接触本身随机 | SCP、软接触/Robust MPPI | 摩擦阈值随机 |

> [!tip] 四条贯穿全讲的"暗线"（抓住它们，细节自来）
> 1. **状态相关噪声是灵魂**：从 §2 的 $G(x_t)$ 到 §3 的 $R(x_t)$ 到 §8 的 $\mu(\omega)$——把噪声当常数，是一切线性高斯方法失效之源。
> 2. **一把温度旋钮**：MPPI 的 $\lambda$ = 内点 barrier $\mu$ = SAC 熵 $\alpha$ = 同伦 $\lambda$（§6.2）——软/探索 ↔ 硬/利用的连续过渡。
> 3. **贝叶斯滤波一以贯之**：CPF（§4）、GP（§5）、信念规划（§7）都是"先验 × 似然 → 后验"；信号处理用它融合触觉、RL 用它当 belief 编码器。
> 4. **aleatoric vs epistemic 决定一切下游**：安全要躲 epistemic（§3.2），探索要奔 epistemic（§7），DR 覆盖参数不确定（§3.1）——分错类就会追逐噪声。

> [!note] 跨领域链接（双向、点对点）
> - **↔ [[SignalProcessing]]**：贝叶斯滤波 KF/EKF/UKF/PF 是状态估计共同语言（§4）；触觉迟滞=非马尔可夫源（§2.3）。
> - **↔ [[ReinforcementLearning]]**：MDP=可控马尔可夫链；POMDP→belief（§2.3）；扩散策略=学出来的 SDE（§6）；DR（§3.1、§8）；AR 探索（§6.3）。
> - **↔ [[Optimization]]**：MPPI 是采样式优化（§6）；随机平滑修复不可微梯度（§8）；Itō 二阶项↔鞍点逃逸（§2.2）。
> - **↔ [[ControlTheory]]**：随机 HJB（§6.3）；信念空间=输出反馈的概率版；GP 方差↔自适应控制的参数不确定（§5）。
> - **↔ [[ContactMechanics]]**：随机互补 SCP（§8）；CPF 解力分配 QP（§4）。
> - **↔ [[Dynamics]]**：名义模型 + GP 残差（§5）；CPF 用逆动力学算残差（§4）。
> - **↔ [[InformationTheory]]**：信念空间的信息增益目标（§7）；epistemic 不确定=信息缺口（§3.2）。

------

## 10. 结论与领域洞察

1. **随机性是特性，而非缺陷 (Stochasticity is a Feature, not a Bug)**：试图用高增益反馈消除所有不确定性是徒劳且危险的（会致刚性碰撞损坏硬件）。最先进的方法（MPPI、信念空间规划）都在**拥抱不确定性**——用噪声探索（§6）、用方差感知风险（§7、§3.2）。
2. **从几何到物理，再到信息**：灵巧操作发展三代——几何（RRT/PRM，假设世界确定）→ 物理（阻抗/LCP，处理接触但假设模型已知）→ **信息**（信念空间/主动感知，核心是把**触觉信息流**实时转化为对物体物理属性的信念更新）。本讲是第三代的数学底座。
3. **计算换鲁棒性**：MPPI 的大规模并行采样、DR 的海量仿真，都在用算力换对不确定性的鲁棒。算法演进方向是更高效地用算力（全量 GP→Sparse GP、LCP→可微物理）。

> [!important] 一句话钥匙
> 随机过程教会灵巧操作的，是从"追踪一个状态"转向"追踪关于状态的信念"，并把噪声从敌人变成工具。叠上"贝叶斯滤波一以贯之"与"一把温度旋钮串起 MPPI/内点/SAC"两座桥，随机过程、信号处理、优化、控制、RL 在你眼里就连成一张图。

------

## 11. 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文涉及本 Foundation 的随机过程理论。

### 扩散模型与生成式策略
- [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation|GLIDE]]：规划引导扩散策略，score-based SDE
- [[Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization|Physics-Driven Data]]：基于物理的随机采样数据生成
- [[Dynamic Reinforcement Learning for Actors|Dynamic RL for Actors]]：动态随机策略学习
- [[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]]：Denoising Sub-MDP，扩散策略 RL 微调 + consistency distillation
- [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control|OmniXtreme]]：Flow Matching 预训练，条件速度场 $v_\theta(x_t,t\mid c)$
- [[WMPO - World Model-based Policy Optimization for VLA|WMPO]]：像素空间视频世界模型的随机轨迹生成 + GRPO

### MPPI 与采样轨迹优化
- [[Autoregressive Policies for Continuous Control Deep Reinforcement Learning|Autoregressive Policies]]：AR 时间一致探索噪声（§6.3）
- [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration|DemoSpeedup]]：熵引导采样加速
- [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach|Exploration vs Exploitation]]：随机控制视角的探索-利用，MPPI 的熵正则解释（§6.3）

### 安全约束与不确定性量化
- [[How to Train Your Latent Control Barrier Function - Smooth Safety Filtering Under Hard-to-Model Constraints|Latent CBF]]：潜空间随机安全边界
- [[Safe Model-based Reinforcement Learning with Stability Guarantees|Safe MBRL]]：模型不确定性传播
- [[Learning Visuotactile Skills with Two Multifingered Hands (HATO)|HATO]]：双手协调中的随机性建模

### 项目级真机不确定性 Idea（WMTS）
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-010-EBM-Mode-Mismatch|EBM Mode-Mismatch]]：能量模型 / Langevin 采样刻画 sim 分布，检测真机模态漂移
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-004-WM-Guided-Diffusion|WGDR]]：扩散逆过程 test-time score modification，按 WM 不确定性自适应保守度
