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

### 2.2 Itō 引理：噪声不止增加方差，还改变能量的漂移方向

处理 SDE 不能用普通链式法则，须用 **Itō 引理**（随机版链式法则）。对状态的标量函数 $V(x_t)$（Lyapunov/能量/价值函数）：

$$
dV=\Big(\partial_t V+\nabla V^Tf+\tfrac12\,\mathrm{Tr}(G^T\nabla^2V\,G)\Big)dt+\nabla V^TG\,dW.
$$

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

------

## 4. 信念更新：从 EKF 失效到粒子滤波

> [!tip] 本节四拍
> **直觉**（盲推冰球：看不见它，只能靠手腕受力反推"它在哪、滑了没"）→ **推导**（贝叶斯滤波；EKF 的线性高斯假设为何在接触处崩）→ **对比**（EKF 单峰 vs 粒子滤波多峰）→ **落点**（CPF/MPF：把粒子约束在机器人表面流形上做接触定位）。

**核心问题**：不靠触觉皮肤、只凭本体感知（关节角、关节力矩），如何估计外部接触状态？这是"盲操作"的关键。

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
