

### 零、 核心变量与空间定义

在定义各个模块之前，我们必须对所处的数学空间进行严格规范：

- **任务定义空间 $\mathcal{C}_{global}$ (Task Definition)**：
  【我希望把当前的任务空间扩充为连续：这里存在问题，in-hand reorientation其实可以定义为一个连续的任务，只要目标转速、位姿等物理特性不出现动力学不可行的跳变，但是为了统一生成隐空间的input，这里必须把目标轨迹长度对齐，这样就无法充分利用这个任务连续性的特征持续生成目标（我还是希望能把任务定义为可以无限长的，仔细分析它在作为diffusion的condition、PPO的input、CVAE的input等等身份中的不同，以及你任务应该如何选择）；同时“一段目标”还带来了急停和急开始的问题，可能会影响到训练和追踪精度的表示；同时，连续表示不能是在全局使用旋转轴 $\vec{\omega}_{axis}$ 和目标角速度 $\omega_{mag}$ 来参数化无限长的旋转任务，这样就无法表示时变的转轴和转速，也无法表示平动】
  作为diffusion的condition、PPO的input时，采用 **Receding Horizon Control**没问题，任务编码 $C_{local,t}$ 应该永远是一个滑动窗口只需要知道“在当前状态下，未来 10 步要达到什么位姿”；但在CVAE里做隐空间任务生成器时，我更倾向使用无限长的任务（这样隐空间也更良态，也自然地包含了平滑的启动和结尾），但没有找到合适的数学表示工具

  四元数存在双重覆盖问题（$q$ 和 $-q$ 表示同一旋转，破坏欧氏距离），而欧拉角有万向节死锁。 任务的定义空间中旋转一项使用 **Continuous 6D Rotation Representation** ($R_{6D} \in \mathbb{R}^6$)
  
- **状态空间 $\mathcal{S}$**：

  - 特权状态 $$O_{oracle, t} = [ P_{obj, t},\dot{P}_{obj, t},Q_{obj, t},\dot{Q}_{obj, t}, F_{contact}]$$ （仅仿真可知，如物体的精确质心坐标、确切的接触力矩阵 Fcontact、精确摩擦系数。物体位姿、速度、受力；这里没有任务相关的信息，任务是在真机上也应该知晓的观测）

  - 真机观测 $O_{real} \in \mathbb{R}^{N_{obs}}$ （真机可获取的信息，如灵巧手本体的关节角度 $q_t$、角速度$\dot{q}_t$、指尖触觉历史序列、$C_{local,t}$）

    - $C_{local,t}$ 是来源于任务的一个target look-ahead Receding Horizon$C_{local,t} = [\text{Base}_{pose} \in \mathbb{R}^2, \text{Inertia} \in \mathbb{R}^{10}, \text{Geom}_{feat} \in \mathbb{R}^{100}, \text{Target}_{P, Q, \dot{P}, \dot{Q}} \in \mathbb{R}^{H \times 13}]$

      *(注：$H$ 为 Look-ahead 窗口长度，超出部分采用 Zero-Velocity Hold (速度强制为 0，位姿复制最后一帧) 填充 Buffer，引导模型稳定停机 )*
      
      **① 物体形状描述 (Fixed Observation)**，该特征在 episode 内保持不变。
      
      $$\mathbf{o}^{\text{shape}} = \text{PointNet}(\mathcal{P}) \in \mathbb{R}^{d_s}, \quad d_s = 100$$
      
      其中 $\mathcal{P} = \{\mathbf{p}_i\}_{i=1}^{N_p} \subset \mathbb{R}^3$ 为物体表面采样的原始三维点云，经 **PointNet** 编码器（含逐点 MLP + 对称聚合函数 max-pooling）映射为固定维度 $d_s$ 的全局形状特征向量。
      
      **② 物体惯性参数 (Oracle — Static)**，该特征在 episode 内保持不变。
      
      $$\mathbf{o}^{\text{inertia}} = \Big[\, m, \;\; \mathbf{r}_{\text{com}}^\top, \;\; \text{vech}(\mathbf{I}_{\text{com}})^\top \,\Big]^\top \in \mathbb{R}^{10}$$
      
      其中：
      
      - $m \in \mathbb{R}_{>0}$：物体标量质量
      - $\mathbf{r}_{\text{com}} \in \mathbb{R}^3$：质心在物体局部坐标系 $\{O\}$ 下的位置向量
      - $\mathbf{I}_{\text{com}} \in \mathbb{S}^{3}_{++}$：在质心坐标系下计算的惯性张量（对称正定矩阵），取其六个独立分量：
        $$\text{vech}(\mathbf{I}_{\text{com}}) = \big[I_{xx},\; I_{xy},\; I_{xz},\; I_{yy},\; I_{yz},\; I_{zz}\big]^\top \in \mathbb{R}^6$$
      
      **③ 任务目标 (Pre-defined Task — Look-ahead Buffer)**
      
      策略不仅观测下一步的目标，而是接收未来 $T_{\text{la}}$ 步的目标序列，形成 look-ahead buffer：
      
      $$\mathbf{o}^{\text{task}}_t = \Big[\, \mathbf{g}_{t+1}^\top, \;\; \mathbf{g}_{t+2}^\top, \;\; \ldots, \;\; \mathbf{g}_{t+T_{\text{la}}}^\top \,\Big]^\top \in \mathbb{R}^{13 \, T_{\text{la}}}$$
      
      其中每一步的目标向量定义为：
      
      $$\mathbf{g}_{t+k} = \Big[\, {}^{W}\mathbf{p}^{*\top}_{t+k}, \;\; {}^{W}\mathbf{q}^{*\top}_{t+k}, \;\; {}^{W}\dot{\mathbf{p}}^{*\top}_{t+k}, \;\; {}^{W}\boldsymbol{\omega}^{*\top}_{t+k} \,\Big]^\top \in \mathbb{R}^{13}, \quad k = 1, \ldots, T_{\text{la}}$$
      
      所有量均定义在**手腕关节坐标系** $\{W\}$ 下（使策略对全局手腕位姿不变）：
      
      | 符号                                  | 维度           | 含义                                |
      | ------------------------------------- | -------------- | ----------------------------------- |
      | ${}^{W}\mathbf{p}^{*}_{t+k}$          | $\mathbb{R}^3$ | 第 $k$ 步物体目标位置               |
      | ${}^{W}\mathbf{q}^{*}_{t+k}$          | $\mathbb{R}^4$ | 第 $k$ 步物体目标姿态（单位四元数） |
      | ${}^{W}\dot{\mathbf{p}}^{*}_{t+k}$    | $\mathbb{R}^3$ | 第 $k$ 步物体目标线速度             |
      | ${}^{W}\boldsymbol{\omega}^{*}_{t+k}$ | $\mathbb{R}^3$ | 第 $k$ 步物体目标角速度             |
      
      **④ 手腕姿态 (Dynamic Observation — Hand Orientation)**，该特征在 episode 内保持不变。
      
      $$\mathbf{o}^{\text{hand}}_t = {}^{G}\mathbf{q}^{B}_t \in \mathbb{R}^{4}$$
      
      其中 ${}^{G}\mathbf{q}^{B}_t$ 为手部基座坐标系 $\{B\}$ (`base_link`) 相对于全局坐标系 $\{G\}$ 的姿态，以单位四元数表示。仅取姿态而不包含位置，因为：
      
      - 手腕位置已隐含在任务目标的手腕坐标系变换中，无需重复提供
      - 手腕姿态反映了重力方向相对于手掌的朝向，对判断抓取稳定性至关重要（如掌心朝上 vs 朝下时所需的抓力策略截然不同）
      
      

- **动作空间 $\mathcal{A}$**：关节的目标位置增量 $A_t \in \mathbb{R}^{N_{joints}}$，然后通过fixed PD转换为关节力矩作用在仿真环境中。

- **初始状态 $S_0$**：与任务定义 $C$ 严格解耦，作为环境 $t=0$ 时刻的物理初值。

- **单步追踪误差**：$\mathcal{E}_t = || P_t - P_{target, t} ||_2 + \lambda_R \arccos\left(\frac{\text{tr}(R_{target}^T R_t) - 1}{2}\right)$，$R \in \mathbb{R}^{3 \times 3}$

  **总追踪误差**：$\mathcal{E}_{traj} = \frac{1}{T}\sum_t \mathcal{E}_t$

  **成功率（不掉落）**：$\mathcal{R}_{succ} = \mathbb{I}(Z_{obj, 1:T} > Z_{threshold})$

------

### 一、 隐空间任务生成器 (Latent Task Generator)

该模块负责在动力学可行域内主动采样新任务，为系统提供源源不断的课程难度梯度。

- **网络架构**：Variational Autoencoder (VAE)  + CMA-ES 演化算法。

- **Input**：已知成功解算的任务集 $\mathcal{D}_{known} = \{ \xi_1, \xi_2, \dots, \xi_K \}$，其中 $\xi = [C_{global}, S_0]$。

- **Output**：新生成的测试任务候选集 $\xi_{new} = [C_{new}, S_{0, new}]$。

- **Fitness Function**：

  - World Model的认知不确定性（Curiosity）

    训练 $M$ 个独立初始化且通过不同 mini-batch 训练的模型，构成一个 Ensemble $\mathcal{F} = \{f_{\theta_m}\}_{m=1}^M$ 。 对于同一个输入 $(s_t, a_t)$，如果这 $M$ 个模型预测出的下一个状态差异极大，说明这个区域的转移规律还没被学明白（模型产生了**分歧 Disagreement**）。

    该分歧通过预测值的协方差矩阵的迹（Trace）来度量，作为探索阶段的内在奖励（Intrinsic Reward $R_I$）：

    $$R_I(s_t, a_t) = \text{tr}\left(\text{Cov}(\{\hat{s}_{t+1}^m = f_{\theta_m}(s_t, a_t) \mid m=1,\dots,M\})\right)$$

    这本质上是贝叶斯主动学习（Bayesian Active Learning）中的信息增益（Information Gain）的近似表示 。最大化分歧，就是引导系统走向能最大幅度减小整体认知不确定性的状态区域 。
    认知不确定性 (Epistemic) 是因为“没见过”而产生的不确定性，随着数据增加会降低；而偶然不确定性 (Aleatoric) 是系统本身的随机性（如传感器噪声），增加数据也无法降低。Ensemble 的方差恰好只衡量了前者。

  - 将新任务 $\xi_{new}$ 喂给通才进行 Zero-shot Rollout，获得追踪误差 $\mathcal{E}_{traj}$ 和成功标记 $\mathcal{R}_{succ}$。

    演化目标是：**寻找通才“没掉落，但跟得很吃力”的任务（舒适区边缘），或者“刚好掉落且贴近已知凸包”的任务（恐慌区边界）。**

    $$\mathcal{F}(\xi_{new}) = \alpha \cdot (\mathcal{E}_{traj} \cdot \mathcal{R}_{succ}) - \lambda_{hull} \mathcal{D}_{latent}(\xi_{new}, \text{Hull}(\mathcal{D}_{known}))$$
    【这里VAE或者CVAE（condition是什么）的隐空间映射需要细化丰富流程】

- ##### CMA-ES（Covariance Matrix Adaptation Evolution Strategy，协方差矩阵自适应进化策略）是专门用来对付这种**黑盒、非连续、多峰值函数**的

  CMA-ES 不维护单一的最佳解，而是维护一个**多维正态分布** $\mathcal{N}(m, C)$。其中 $m$ 是均值向量，$C$ 是协方差矩阵。

  它的核心过程可以浓缩为四个严谨的步骤：

  1. **采样 (Sampling)**：

     算法首先在一个多维空间中生成 $\lambda$ 个候选解（Offspring）。其基础采样方程为：

     $$x_k^{(g+1)} \sim m^{(g)} + \sigma^{(g)}\mathcal{N}(0, C^{(g)})$$

     对于 $k = 1, \dots, \lambda$ 。 在这里，$m^{(g)}$ 是分布均值，$\sigma^{(g)}$ 是整体步长（Step-size），$C^{(g)}$ 是协方差矩阵 。

  2. **评估与排序 (Evaluation & Sorting)**：

     把这 $\lambda$ 个任务喂给通才进行 Rollout。根据我们设定的 Fitness Function（例如：刚好掉落且贴近已知凸包，即 $\mathcal{F}(z_i)$ 分数最高）对这 $\lambda$ 个任务进行排名。

  3. **均值更新 (Mean Update - 找准大方向)**：

     采用截断选择（Truncation Selection），仅利用排名前 $\mu$ 的个体来更新下一代的均值 ：

     $$m^{(g+1)} = \sum_{i=1}^\mu w_i x_{i:\lambda}^{(g+1)}$$

     其中 $w_i$ 是递减的重组权重（$w_1 \ge \dots \ge w_\mu > 0$ 且 $\sum w_i = 1$） 。这里引入了一个关键的理论指标——方差有效选择质量（Variance Effective Selection Mass）：$\mu_{eff} = 1 / \sum_{i=1}^\mu w_i^2$ 。它量化了实际利用的信息量，并在后续的参数自适应中起到基准作用 。

  4. **协方差矩阵自适应 (Covariance Matrix Adaptation - 核心精髓)**：

     结合了两种不同视角的信息来更新 $C^{(g+1)}$：

     - **Rank-$\mu$-Update（秩 $\mu$ 更新）：** 利用当前代种群中优秀个体的方差信息 。这在种群规模较大时极为有效 。

       使用的是**旧均值 $m^{(g)}$** 作为参考点：

       $$C_\mu^{(g+1)} = \sum_{i=1}^\mu w_i (x_{i:\lambda}^{(g+1)} - m^{(g)})(x_{i:\lambda}^{(g+1)} - m^{(g)})^T$$

       这里估计的不再是“选中个体的分布”，而是“**成功变异步长（Selected Steps）的分布**” 。 从几何意义上讲，当种群沿着目标函数的梯度方向移动时，使用旧均值计算出的协方差矩阵，会在**梯度方向上几何级数地拉长期望方差**，从而引导下一代沿着该方向进行更大胆的搜索 。
       【利用单代种群内部的海量变异样本。

       在大种群下能极其高效地、同时在多个正交维度上重塑协方差矩阵的形状 。

       当种群极小（如 $\lambda \le 10$）时，单代的方差估计极不可靠，必须依赖历史累积 。】

     - **Rank-One-Update（秩一更新）与 Cumulation（累积）：**引入了**进化路径（Evolution Path，$p_c$）**。它不只看当前步，而是累积历史连续步的方向 。这极大地利用了连续世代之间的相关性信息，它对连续步的“方向相关性”产生了非线性的**放大与缩小效应** 。 

       进化路径 $p_c$ 并非单纯的步长相加，而是算法在历史世代中所走过的连续步的指数平滑加权和 。为了消除每代全局整体步长尺度变化带来的干扰，构造时会严格剔除当前步长 $\sigma^{(g)}$ 的影响 。

       其核心递推公式如下 ：

       $$p_c^{(g+1)} = (1-c_c)p_c^{(g)} + \sqrt{c_c(2-c_c)\mu_{eff}} \frac{m^{(g+1)} - m^{(g)}}{c_m \sigma^{(g)}}$$

       其中 $c_c \le 1$ 是路径的时间衰减常数，决定了向后追溯的时间视野

       捕捉了连续代际相关信息的进化路径 $p_c$，最终会被送入协方差矩阵的秩一更新（Rank-One-Update）公式 ：

       $$C^{(g+1)} = (1-c_1)C^{(g)} + c_1 p_c^{(g+1)} (p_c^{(g+1)})^T$$
       【利用代际间的进化路径（均值的连续漂移）。

       利用连续代际的相关性，极大加速病态地形（如长条形山谷）中单一主轴的适应速度 。

       在大种群中显得信息利用率不足，因为每一代只提取了一个均值漂移方向。】

  5. **Step-Size Control（步长控制 / CSA）**

     基于共轭进化路径的全局尺度调节协方差矩阵 $C^{(g)}$ 确实能够极其完美地拟合目标函数的等高线形状，但它在控制“全局步长尺度”（Overall Step Length）时存在两个致命的数学缺陷：

     1. **缩放速度过慢**：协方差矩阵的学习率 $c_1$ 和 $c_\mu$ 非常保守（通常在 $\mathcal{O}(1/n^2)$ 级别）。如果在像球面函数这样的简单地形上，要想达到最优的步长收缩速率，单靠矩阵更新会慢得令人发指 。
     2. **与选择质量 $\mu_{eff}$ 脱节**：理论上的最优步长与方差有效选择质量 $\mu_{eff}$ 成正比，但矩阵更新公式（Rank-1 和 Rank-$\mu$）从根本上无法实现这种代数关系的缩放 。

     为了打破这个瓶颈，CMA-ES 引入了**累积步长自适应（Cumulative Step-Size Adaptation, CSA）**。它的核心哲学是：**通过比较实际进化路径的长度，与纯随机游走（Random Walk）在各向同性空间下的期望长度，来决定步长的增减** 。 算法构建了另一条消除方向偏置的共轭进化路径 $p_\sigma$ ，并将其长度 $||p_\sigma||$ 与随机选择下的期望长度 $E||\mathcal{N}(0, I)||$ 进行比较 

     1. 如果路径过短（步相互抵消/反相关），则减小 $\sigma$ 。
     2. 如果路径过长（步同向/正相关），说明可以用更少的长步长到达，因此增大 $\sigma$ 。

  我们将已知可行任务通过 CVAE 映射到隐空间 $Z$。在这个相对平滑的低维空间里，CMA-ES 的协方差矩阵可以非常高效地顺着“可行且困难”的流形（Manifold）边缘滑动。它既能利用全局种群避免陷入单一任务死锁，又能通过自适应步长精准锁定通才的“能力盲区”。

  **工作流**：生成的 $\xi_{new}$ 交由通才策略进行 Zero-shot Rollout。若成功率处于盲区（Panic Zone），则派发给 Oracle 求解。

------

### 二、 专才策略 (Oracle Specialist Policy)

仅在仿真中被唤醒的“解题机器”，利用特权信息降维打击，为盲区任务生成完美的专家轨迹。

- **网络架构**：MLP Actor-Critic 网络 (PPO 算法)。

- **Input**：

  $O_{oracle, t} = [O_{real, t}, S_{priv, t}, C_{local, t}]$。*(局部视界 $C_{local, t}$ 使网络永远知道“下一步该干什么”，而非“整个任务有多长”。)*

- **Output**：

  单步动作的高斯分布参数 $\pi_\theta(A_t | S_{oracle, t}, Target) = \mathcal{N}(\mu_\theta, \Sigma_\theta)$。

- **Loss (Label)**：

  标准 PPO 截断代理目标函数，加上 Value Loss 和 Entropy Bonus：

  $$\mathcal{L}^{CLIP}(\theta) = \hat{\mathbb{E}}_t \left[ \min(r_t(\theta)\hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t) \right]$$

  $$\mathcal{L}_{total} = \mathcal{L}^{CLIP} - c_1 \mathcal{L}^{VF} + c_2 S[\pi_\theta] - c_3 \mathcal{L}_{Bounded}(\mu_\theta)$$

------

### 三、 通才策略 (Generalist Diffusion Policy)

系统的核心输出大脑，在真机部署时的主力。负责在残缺观测下，通过行为克隆吸收所有专才的知识。
【当前Diffusion确定先从Oracle Policy进行蒸馏，Oracle Policy是认为定义了几组任务分别训练出的专家模型（比如改变了手的朝向、物体的形状、转轴角速度等），现有如下问题：

1. 我希望充分利用到Hindsight Experience Replay的insight，当前如果我的Oracle策略追踪效果不完美（但动力学形态合理），则如果把实际轨迹作为目标轨迹，这是一个100%精度的追踪，也就是Oracle策略rollout出的结果在蒸馏到Diffusion时，输入Diffusion的Condition中的task应该是实际轨迹（而不是原定的目标轨迹），只要判断动力学合理（但这里该如何判断）

   蒸馏的过程中Oracle在IsaacGym中进行rollout，采用 **Asynchronous Experience Rebuffer** 架构：

   - **Worker Node (IsaacGym)**：海量环境并行运行 Oracle，产生 $\tau_{expert} = \{O_{real}, C_{achieved}, A_{oracle}\}$ 存入磁盘或共享内存。
   - **Learner Node (DiT)**：只负责从 Buffer 中采样 Noisy Action Chunk 进行 Denoising Score Matching 更新。

2. 在蒸馏的同时用获得的数据训练World Model，此时World Model见到的大多数都是动力学形态合理的轨迹，没有见过太多会导致失败的动作（实际上导致失败的动作在空间中分布应该是非常广泛的）

3. 在蒸馏结束后，利用Hindsight Experience Replay应该会收集到一个个聚类的任务点，下一步开始任务生成，关键在于是否直接用Diffusion网络直接部署RL进行finetune，Diffusion用的是真机观测，该如何充分利用Oracle Policy？但这里面对新任务Oracle Policy又要从头重新训练，且可能还需要面对不同任务定义不同的奖励函数，没有充分利用到已训练的Oracle Policy、Diffusion、World Model中的动力学先验（比如如何先保证物体不掉落）】

- **网络架构**：Diffusion

  - 前向过程的本质是一个固定的物理热扩散过程，其目的是将有意义的动作序列 $\mathbf{A}$ (即 $x_0$) 逐步破坏成纯高斯噪声。这个破坏过程只依赖于预设的方差表 (Variance Schedule $\beta_t$)，与任务条件 $c$ 毫无关系。

    根据马尔可夫链定义，单步加噪为：

    $$q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1-\beta_t}x_{t-1}, \beta_t I)$$

    利用重参数化技巧（设 $\alpha_t = 1 - \beta_t$, $\bar{\alpha}_t = \prod_{i=1}^t \alpha_i$），我们可以直接从 $x_0$ 采样出任意步 $t$ 的状态：

    $$q(x_t | x_0) = \mathcal{N}(x_t; \sqrt{\bar{\alpha}_t}x_0, (1-\bar{\alpha}_t)I)$$

    $$x_t = \sqrt{\bar{\alpha}_t}x_0 + \sqrt{1-\bar{\alpha}_t}\epsilon, \quad \epsilon \sim \mathcal{N}(0, I)$$

  - 反向单步预测为：

    $$p_\theta(x_{t-1} | x_t, c) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t, t, c), \Sigma_\theta(x_t, t, c))$$

    网络 $\epsilon_\theta(x_t, t, c)$ 的任务是：在给定当前噪声状态 $x_t$、时间步 $t$ 和任务条件 $c$ 的情况下，预测出 $x_t$ 中包含的纯噪声 $\epsilon$。其均值推导为：

    $$\mu_\theta(x_t, t, c) = \frac{1}{\sqrt{\alpha_t}} \left( x_t - \frac{\beta_t}{\sqrt{1-\bar{\alpha}_t}} \epsilon_\theta(x_t, t, c) \right)$$

- **The Input (去噪对象)**：

  网络真正在“处理”的输入，只有 **带有 $k$ 步高斯噪声的动作块 (Noisy Action Chunk)** $\mathbf{A}^{(k)}$，以及当前的 **时间步标量 (Timestep)** $k$。

  它的维度是严格的 `[Batch_size, Chunk_length, Action_dim]`。你可以把它理解为一块布满杂讯的“毛坯大理石”，网络的任务就是预测这块石头上的噪声 $\epsilon_\theta$ 并将其剥离。

- **The Condition (不参与前向加噪过程（热力学第二定律不需要目标导向），指导去噪的上下文)**：

  **Observation（残缺观测序列 $O_{real}$）**和 **Task（局部视界任务 $C_{local,t}$）** 

  Condition 告诉网络：“当前灵巧手的姿态是这样，未来的目标轨迹是那样，请按照这个上下文，把那块毛坯大理石雕刻成正确的动作曲线”。
  **无分类器引导 (Classifier-Free Guidance, CFG)**
  Diffusion 本质上是在估计数据对数似然的梯度（即 Score：$s(x_t) = \nabla_{x_t} \log p(x_t)$）。

  根据贝叶斯定理，引入条件 $c$ 后的条件得分为：

  $$\log p(x_t | c) = \log p(x_t) + \log p(c | x_t) - \log p(c)$$

  两边对 $x_t$ 求梯度（因为 $\log p(c)$ 与 $x_t$ 无关，梯度为 0）：

  $$\nabla_{x_t} \log p(x_t | c) = \nabla_{x_t} \log p(x_t) + \nabla_{x_t} \log p(c | x_t)$$

  等式右边第一项是**无条件先验得分**，第二项是**条件引导得分**。在每一步逆向采样时，更新动作 $dx$ 的力场由两部分矢量叠加而成：

  1. **流形引力（先验得分 $\nabla_x \log p_t(x)$）**：它不关心你要做什么任务，它只负责把当前带有噪声的位姿 $x_t$ 拉回“符合灵巧手运动学限制、不自碰撞”的合理运动流形。
  2. **任务拉力（似然得分 $\nabla_x \log p_t(c|x)$）**：这是一个极其定向的矢量。它度量了“如果当前轨迹是 $x$，它有多大可能完成任务 $c$”。它的梯度方向就是让任务成功率提升最快的方向。

  CFG 为了放大条件 $c$ 的影响力，人为地给第二项乘以一个权重 $w$ ($w \ge 1$)：

  $$\tilde{s}(x_t, c) = \nabla_{x_t} \log p(x_t) + w \nabla_{x_t} \log p(c | x_t)= (1 - w) \nabla_{x_t} \log p(x_t) + w \nabla_{x_t} \log p(x_t | c)$$
  在扩散模型中，得分函数与预测噪声存在严格的等价关系$s(x_t) \propto -\epsilon_\theta(x_t)$

  > **核心结论：** 对于高斯扩散过程，状态点向高密度区域移动的最速上升方向（得分），**严格等于**加在该点上的真实噪声向量 $\epsilon$ 的反方向，并乘以一个随时间衰减的缩放系数。$$\nabla_{x_t} \log q(x_t | x_0) = - \frac{\sqrt{1-\bar{\alpha}_t}\epsilon}{1-\bar{\alpha}_t} = - \frac{1}{\sqrt{1-\bar{\alpha}_t}} \epsilon$$

$$\tilde{\epsilon}_\theta(x_t, t, c) = (1 - w) \epsilon_\theta(x_t, t, \emptyset) + w \epsilon_\theta(x_t, t, c)$$

**训练阶段**：以固定的概率（如 10%）将网络输入的条件 $c$ 置空（替换为全零向量 $\emptyset$）。这样，同一个网络 $\epsilon_\theta$ 同时学会了无条件预测 $\epsilon_\theta(\emptyset)$ 和条件预测 $\epsilon_\theta(c)$。

**推理阶段**：网络在每一步都需要执行两次前向传播。一次带条件，一次不带条件。然后利用上述公式，以 $w$ (通常取 $1.2 \sim 3.0$ 之间) 放大带有条件的噪声方向。

- **Output**： Action Chunking。整个动作序列块 $\mathbf{A} = [A_t, A_{t+1}, \dots, A_{t+K-1}]$。

- **Loss (Label)**：

  Denoising Score Matching (行为克隆损失)。给定来自 Oracle 的专家动作块 $\mathbf{A}^{(0)}$，加入步数为 $k$ 的高斯噪声 $\epsilon$，训练网络 $\epsilon_\theta$ 预测该噪声：

  $$\mathcal{L}_{Diffusion}(\theta) = \mathbb{E}_{\mathbf{A}^{(0)} \sim \mathcal{D}_{oracle}, \epsilon \sim \mathcal{N}(0, I), k} \left[ || \epsilon - \epsilon_\theta(\mathbf{A}^{(k)}, k, O_{real}, C_{local, t}) ||^2_2 \right]$$

------

### 四、 动力学世界模型 (Ensemble World Model)

仿真中的“观察者”，真机中的“安全调度员”。解耦Rigid Dynamic Model（主要在IsaacGym中学）和Actuator Model（只在真机操作过程中学，仿真中是恒等映射）。【问题在于如何把这两个模块合并】

这里的insight是让在慢速任务上学习到的摩擦系数（归属于 Dynamic Model）和电机非线性（归属于 Actuator Model）物理真实的，才有可能安全地外推（Extrapolate）到具有极高科里奥利力和急停的高动态任务上，同时动态学习actuator model也能拟合磨损的过程。

- **网络架构**：Probabilistic Ensemble (如 PETS)。由 $M$ 个独立初始化、结构相同的 MLP 构成。

  引入真机的**电流/力矩反馈 ($T_{feedback}$)** 作为中间监督信号，将梯度强行解耦：

  - 对 Actuator Model 单独提供 Loss: $\left\| T_{feedback}^{real} - \hat{\tau}_{real} \right\|^2$

    执行器模型被定义为 $\hat{\tau}_{link} = f_{act}(s_t, a_t)$。这在实际工程中是**行不通的**！ 因为电机系统存在通信延迟、减速器摩擦以及你提到的反电动势，这些系统的状态并不能由当前时刻的单一状态 $s_t$ 完全描述，这是一个**部分可观测马尔可夫决策过程 (POMDP)** 。传入历史窗口，实际上是把滤波的权利交给了神经网络。MLP 第一层的权重矩阵相当于在学习一个最优的**非线性 FIR 滤波器（Finite Impulse Response filter）**。它不仅隐式地提取了加速度信息，还自动平滑了高频噪声。

    当 4090 跑完一轮 Transformer/PPO 推理，决定对某个手指施加特定的力矩时，指令会经历以下漫长且充满非线性的旅程：

    1. **宿主机阶段 (PC & SDK):** 4090 输出期望力矩 $\tau_{cmd}$，通过 SDK (`torque.py`) 转化为特定的协议帧，经由 USB 转 CAN 模块发送（受限于操作系统的调度抖动和 USB 轮询率）。指令被送入 `CANMessageDispatcher` 的 `_send_queue` 中。后台发送线程以严格的 **0.3毫秒（300μs）** 间隔（`SEND_INTERVAL_S = 0.0003`）串行发送这些 CAN 帧（0x51-0x55）

    2. **通信总线阶段 (CAN Bus):** 指令进入 CAN 总线 (`comm/can/can.py`)。由于灵巧手手指众多，CAN 总线存在带宽上限和帧仲裁（Arbitration），多个手指的指令无法达到绝对意义上的“同时”到达。【由于操作系统的抖动和 CAN 总线的排队，存在 5ms - 20ms 的不确定延迟】

    3. **驱动器阶段 (MCU & FOC):** 手指内部的微控制器（MCU）接收报文，将 $\tau_{cmd}$ 转换为期望的相电流 $I_q$。FOC（磁场定向控制）算法通过极高频（通常 10-20kHz）的 PWM 波控制逆变器，驱动电机。

    4. **电磁转换阶段 (空心杯电机):** 空心杯电机（Coreless Motor）根据输入的电流产生电磁转矩。由于没有铁芯，它响应极快，但热容极小，温度飙升会导致内部电阻显著变大。【**反电动势（Back-EMF）：** 当手指快速挥动时，电机高速旋转产生反电动势，抵消了驱动电压。这意味着在高速运动时，即便你下发了最大力矩指令，电机也根本输出不了那么多力。在同一扭矩指令下，电机静止和电机高速转动时，实际输出的物理扭矩是截然不同的。**热衰减（Thermal Derating）：** 空心杯电机散热极差。温度（`temperature.py` 中可读）升高时，绕组电阻变大，产生相同力矩需要的电流骤增，导致电机力矩常数 $K_t$ 发生动态漂移，相同 PWM 占空比下，实际电流（即输出力矩）大幅衰减。】

    5. **第一级机械传动 (行星滚柱/滚珠丝杠):** 电机的旋转运动，通过极其微小的滚珠丝杠或行星滚柱丝杠，转化为直线推力。【丝杠传动存在极高的静摩擦力（Stiction）和复杂的 **斯特里贝克效应（Stribeck Friction）**。换向瞬间（速度过零点）存在巨大的静摩擦和动态库仑摩擦，当灵巧手试图做极其微小的力矩调整（例如捏住一张纸）时，指令力矩可能全被丝杠的静摩擦力吃掉了，指尖根本没动；一旦突破静摩擦，又会突然发生滑动。在 L25 这种含有丝杠和 PIP/DIP 强耦合连杆的机构中，传动比（Jacobian）和系统内部的静摩擦力是**高度依赖当前手指绝对弯曲角度的**】

    6. **第二级机械传动 (耦合连杆):** 直线推力推动连杆机构（Linkage）。由于连杆的几何约束，PIP（近端指间关节）和 DIP（远端指间关节）产生耦合的角位移。【高负载下，细长的连杆和丝杠本身会发生弹性形变】

    7. **末端交互 (指尖 & 力传感器):** 指尖最终输出力，同时 SDK 能够通过 `force_sensor.py` 和 `angle.py` 读回当前状态，传回 4090 形成闭环。

       angle.py：真实电机的绝对位置是通过编码器（如磁编码器/光电编码器）读取的。位置数据 $q_t$ 本身带有离散的量化噪声。速度通常是通过一次差分 $\dot{q}_t \approx (q_t - q_{t-1}) / \Delta t$ 得到的。通过 `get_snapshot()`（读取内存缓存的最新帧）或 `get_blocking()`（主动发送 `[0x41]` 至 `[0x45]` 的单字节查询帧，并等待所有 5 帧集齐）。因为依赖 CAN 总线的轮询（Polling 线程在后台以 `1/60` 秒的频率主动去刷），你拿到的观测状态（Observation）天然带有 15ms-20ms 的延迟。

       force_sensor.py：`_MCU_INTER_REQUEST_DELAY_S = 0.0025`。因为 MCU 算力有限，请求完一根手指必须硬等 2.5 毫秒才能请求下一根。每次调用 `get_blocking()` 会依次给 5 根手指发送 `[0xB1, 0xC6]` 等请求。每根手指会返回 12 帧 CAN 报文，每帧包含 6 个有效字节。SDK 将其拼装成一个 `12x6` 的 `uint8` 矩阵（共 72 字节/手指）。这大概率是一个高密度的薄膜阵列触觉传感器（Taxel array）。这意味着**收集全手 5 根手指的完整触觉矩阵，理论最小耗时在 12.5ms 以上**。

       torque.py：大多数灵巧手的力矩并非通过末端六维力传感器直接测得，而是底层 MCU 通过采样电机相电流（FOC 中的 Iq 电流），乘以力矩常数 $K_t$ 和减速比估算出来的。由于丝杠摩擦的存在，这个**估算力矩不等于指尖实际输出的力矩**。

    真机收集的数据元组为：

    $$D = \{a_t, \phi_t,  \dot{\phi}_t, \tau_{measured}, \text{Temp}\}_{T,T-1...}$$

    *(其中 $a_t$ 为动作指令 $\tau_{cmd}$，$\phi$为 `angle.py` 读数，$\dot{\phi}$ 为 `speed.py` 读数（是差分出来的，可能不需要），$\tau_{measured}$ 为 `torque.py` 读回的反馈电流力矩)*。神经网络自己去隐式地推断当前丝杠卡在什么摩擦力状态、电机积攒了多少反电动势、底层 PID 累积了多少误差，然后输出一个真实的估算力矩 $\hat{\tau}_{link}$

    

  - 对 Dynamic Model 提供 Loss: $\left\| s_{t+1}^{real} - f_{dyn}(s_t, T_{feedback}^{real}) \right\|^2$

    对于 `Rigid Dynamic Model`，ANYmal**坚决不使用神经网络**，而是采用了基于硬接触模型（Hard contact model）的高效刚体物理求解器 ，因为用 NN 拟合高频、非平滑的刚体碰撞（non-smooth dynamics）往往会遇到灾难性的复合误差。但这不符合World Model的原则。

     当前设计 Rigid Dynamic Model 需要在“真机环境中微调摩擦系数等极少数物理量”。

    但是真机的摩擦系数是多变的（如相同的网球不同部位摩擦系数不同），也无法获得Ground Truth。一般学界的做法采用极其暴力的**域随机化 (Domain Randomization)**，目前初步考虑将随机化的具体参数也输入Rigid Dynamic Model，但这样真机就拿不到了，需要类似system identification

    

- **Input**：当前状态 $S_t$ 和 通才生成的动作 $A_t$。*(注：不输入任务信息 $C$，坚持物理因果律)*

- **Output**：

  每个模型输出下一个状态的对角高斯分布参数 $\hat{P}_m(S_{t+1} | S_t, A_t) = \mathcal{N}(\mu_m, \Sigma_m)$。

- **Loss (Label)**：

  极大似然估计（最大化真实状态分布的对数似然）：

  $$\mathcal{L}_{WM}(\phi_m) = -\sum_{t} \log \mathcal{N}(S_{t+1}^{real/sim} | \mu_{\phi_m}(S_t, A_t), \Sigma_{\phi_m}(S_t, A_t))$$

- **真机应用 (Safety Checker)**：

  当 Generalist 输出长度为 $K$ 的 Action Chunk $\mathbf{A} = [A_t, \dots, A_{t+K-1}]$ 时，World Model 必须进行步进交互： $\hat{S}_{t+1} = \text{WM}_{\phi_m}(\hat{S}_t, A_t)$ $\hat{S}_{t+2} = \text{WM}_{\phi_m}(\hat{S}_{t+1}, A_{t+1})$，相当于把World Model当作物理引擎

### 五、 真机强化微调与调度闭环 (Real-World Fine-Tuning)

由于真机中不存在 Oracle，这个阶段的核心是“基于 Predictor 筛选的安全微调”。

- **步骤 1: 真机安全调度 (Look-ahead Filter)**

  真机获取 $O_{real, t}$，通才推理出 Action Chunk $\mathbf{A}$。

  将 $S_t, \mathbf{A}$ 输入 WM+Predictor 进行内存推演。如果 $\hat{\mathcal{R}}_{succ} < Threshold$，丢弃该动作块，降级执行安全动作（如恢复初始抓握），避免硬件损坏。
  【真机应用该如何生成训练策略（如何安排真机训练的流程），应该结合仿真整个任务隐空间的策略安全率和精度评判任务难易程度，但这个评判需要随着真机逐渐适应真机的动力学、物理引擎环境以及通才策略在真机中微调后改变值，所以是否可以设置在仿真中，就试着把world model当做物理引擎来判断当前策略的成功性，再将成功率和精度与在仿真物理引擎中测出来的进行比较，这是否能传一个梯度。或者说直接另训一个来判断轨迹成功率的模型，这是基于 world model 的某些输出或者隐藏层的，这样就可以将在真机中学习及微调后的 world model 和策略与预测成功任务成功率的模型结合起来了】

  1. 用 WM 的 Epistemic Uncertainty 来做真机的 Out-of-Distribution (OOD) 动作拦截：如果预测方差极大，说明这个动作序列进入了真机动力学与仿真动力学的“严重分歧区”（即 Sim-to-Real Gap 极大的区域，比如接触了未知的摩擦表面）。此时，哪怕均值预测“没有掉落”，也应该**立刻触发降级安全动作**

  2. **“动态对齐的精确度预测器” (Discrepancy-Aware Success Predictor)**

     - **模型构建**：训练一个附加的 Critic 网络 $\mathcal{P}_\psi(\text{success} | h^{WM}_{t}, z_{task})$。它的输入不是原始状态，而是 World Model 的**高层隐特征** $h^{WM}_{t}$ 和任务编码。
       为了真机安全，我们必须避免 False Positive（过度乐观），不能只用 Cross Entropy 预测成功率，**必须在$\mathcal{P}_{\psi}$ 训练中引入 NT-Xent 对比损失 (Contrastive Loss)** 。 将成功任务的隐层特征 $h^{WM}$ 拉近，将失败的（掉落的、没跟上的）推远 。然后在这个 Embedding 空间之上再做 Softmax 分类 。

     - **梯度传递与动态演进**：
       1. $\mathcal{P}_\psi$ 在仿真中与 Oracle 共同训练，掌握了物理引擎下的“成功直觉”。
       2. 进入真机后，利用收集到的真实交互数据 $\tau_{real}$，我们**同时更新 WM 和 $\mathcal{P}_\psi$**。
       3. 因为 WM 被真机数据强制拟合了真实的动力学残差（如将期待力矩与实际反馈力矩的差值编码进隐层），$h^{WM}_{t}$ 的分布会发生漂移。

- **步骤 2: 收集真实数据更新 WM**

  执行通过安检的动作，收集真机 Transitions $\tau_{real}$。计算真实的追踪误差，打上真实的成功/失败标签。还需收集真实的Torque_desired, Torque_target, Torque_feedback数据等，利用这些数据微调 WM 和 Success Predictor 的权重，使其迅速拟合真机的 Actuator 非线性和科里奥利力。

- **步骤 3: 通才的无监督/自监督微调 (Self-Practice)**

  ###### 选择一：通才通过不断模仿自己在真机上的“超常发挥”来实现 Sim-to-Real 的跨越

  通才**不再使用 PPO**。我们采用 **Advantage Weighted Behavior Cloning (AWAC)** 或过滤后的在线 BC。提取 $\tau_{real}$ 中追踪误差最小、执行最完美的顶级轨迹（超常发挥），把它们重新放入 Buffer 进行 Diffusion 蒸馏，以 $\exp(A/\beta)$ 为权重，对 Diffusion 进行**加权行为克隆 (Weighted BC)**：

  $$\mathcal{L}_{Finetune} = \mathbb{E}_{\tau_{real}} \left[ \exp\left( \frac{R(\tau) - V(S)}{\beta} \right) || \epsilon - \epsilon_\theta ||^2_2 \right]$$
  
  ###### 选择二：直接将WM作为真机物理引擎
  
  **冻结微调后的 WM** $\rightarrow$ 在 WM 的隐空间内，使用 DiWA 的 Dream Diffusion MDP 和带有 BC 正则的 PPO 大量更新 Generalist Diffusion Policy。用 WM 矩阵运算在 GPU 内存中推演的速度极快，但 PPO 是极其贪婪的优化器，它可能会在几百步之内找到（Exploit）WM 的物理漏洞，生成一种“在 WM 里能完美完成任务，但在真机上会把手指拧断”的对抗性动作（Adversarial Actions）。