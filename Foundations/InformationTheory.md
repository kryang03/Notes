---
tags:
  - foundation
  - information-theory
  - active-perception
  - entropy
aliases:
  - 信息论
  - 互信息
  - KL散度
  - 主动感知
created: 2026-01-31
related:
  - "[[ReinforcementLearning]]"
  - "[[WorldModels]]"
  - "[[StochasticProcess]]"
  - "[[SignalProcessing]]"
  - "[[RepresentationLearning]]"
  - "[[ControlTheory]]"
---

# 信息论驱动的灵巧操作：从不确定性度量到主动触摸

# Information-Theoretic Dexterous Manipulation: From Uncertainty Measures to Active Touch

> [!tip] 相关领域
> - [[ReinforcementLearning]] — 内在动机、好奇心探索、最大熵；熵是探索目标也是柔顺
> - [[StochasticProcess]] — belief、贝叶斯更新、粒子滤波是信息度量的载体
> - [[SignalProcessing]] — 触觉信息的序列化获取；率失真=压缩-去噪对偶
> - [[RepresentationLearning]] — 信息瓶颈 = 最优表征压缩
> - [[ControlTheory]] — empowerment ↔ 可控性 Gramian；双重控制
>
> **贯穿母题（本讲的"主角"）**：**闭眼、仅凭触摸认出口袋里的钥匙 (identify a key in your pocket by touch alone)**。一个人人都做过的动作，把信息论每一层都点亮——我们让它贯穿全篇。

## 0. 母题与理论大厦构建路线：从不确定性度量到主动触摸策略

> [!abstract] 为什么用"闭眼摸钥匙"做贯穿母题？
> 信息论在灵巧操作里不是抽象的"熵很重要"，而是一条从 **belief 到 action** 的构建链。**闭眼在口袋里摸出钥匙**这一个动作，恰好逐层激活：
> - 一开始不知道摸到的是钥匙、硬币还是纸巾 → **熵**度量当前无知；
> - 每摸一下、感到锯齿状边缘 → 一次观测的**互信息/信息增益**；
> - 摸到意料之外的光滑面（原来是打火机）→ **KL 散度/惊奇**；
> - "下一下该摸哪里最能确认是钥匙" → **下一最佳触点 (NBT)**；
> - 一连串触摸的规划（而非单点贪心）→ **信念空间规划**；
> - 摸到后稳稳捏住、能随意翻转它 → **empowerment（可控性）**；
> - 把丰富的触觉流压成"是钥匙"这一个结论 → **信息瓶颈**。
>
> 全讲每引入一个概念，我们都回到这把钥匙："**它帮我们更快地从'不知道'走到'确认是钥匙'了吗？**"

信息论 Foundation 的主线，是把"不确定性"从模糊直觉提升为可计算、可指导动作的对象。五步构建链：

1. **信念建模**：把未知物体位姿、接触状态、摩擦、刚度写成随机变量，而非单点估计。
2. **不确定性度量**：熵刻画 belief 体积、KL 刻画一次观测的 belief 跳变、互信息刻画候选观测的期望价值。
3. **主动感知目标**：动作 $a$ 的价值 = 未来观测能减少多少不确定性，而非动作本身看起来多接近目标。
4. **物理约束耦合**：触摸既耗能又可能扰动物体，信息增益必须与碰撞风险、接触力、任务代价共同优化。
5. **表征与控制闭环**：信息瓶颈压缩观测、empowerment 衡量可控性，二者共同决定"留什么信息、去哪探索、何时变硬/变软"。

| 层级 | 关键问题 | 理论对象 | 摸钥匙母题的映射 | 讲稿位置 |
|:--|:--|:--|:--|:--|
| **度量层** | 如何量化"不知道"？ | 熵、互信息、KL | 摸之前对"是什么"的无知 | §2 |
| **概率建模层** | 如何用触摸更新认知？ | GPIS、贝叶斯更新 | 每摸一点雕刻一次形状分布 | §3 |
| **主动规划层** | 下一下该摸哪？ | NBT、信念空间规划、EIG | 去最能确认是钥匙的地方 | §3、§4 |
| **表征层** | 该保留哪些信息？ | 信息瓶颈、率失真、VIB | 把触觉流压成"是钥匙" | §5 |
| **内在动机层** | 无奖励时学什么？ | empowerment、DIAYN、VIME | 追求对物体的控制力 | §6 |
| **现实层** | 软体/真机怎么办？ | 现实鸿沟=信息损失 | 软指迟滞、stick-slip 信息 | §7 |

> [!important] Foundation 级判断标准（任何信息论方法进入本库都要回答四问）
> 1. **度量的是哪种不确定性**（epistemic 可消 vs aleatoric 不可消）？只有 epistemic 值得主动探索。
> 2. **信息增益如何与物理代价权衡**（触摸耗能、可能碰翻物体）？
> 3. **是被动压缩还是主动获取**（信息瓶颈 vs NBT/empowerment）？
> 4. **期望如何近似**（未来观测未知，需蒙特卡洛/变分下界）？

> [!note] 本讲在知识图谱中的位置（依赖 / 被依赖）
> ```
>  [[StochasticProcess]] ─belief/PF─┐                    ┌── 内在奖励/最大熵 ──> [[ReinforcementLearning]]
>  [[SignalProcessing]] ─触觉流─┤                         │
>                            ├──> 【InformationTheory】 ──信息瓶颈──> [[RepresentationLearning]]
>      empowerment↔可控性 <──> [[ControlTheory]]            │
>                            └──主动感知目标──> 主动触摸/NBT 控制
> ```
> 读法：随机过程提供 belief 载体、信号处理提供触觉流，信息论在其上定义"该采什么、留什么、去哪探索"，产出喂给 RL（内在动机）、表征（信息瓶颈）、控制（双重控制）。

> [!important] 与 [[SignalProcessing]] 的边界
> SignalProcessing 解"如何从 noisy sensor stream 估计状态"（被动最优重构）；InformationTheory 解"哪个状态值得估、下一次观测去哪、表征保留多少信息"（主动最优获取）。二者通过 belief update 与信息增益闭环相连。

## 1. 从被动观测到具身主动性

> [!tip] 本节四拍
> **直觉**（闭眼摸钥匙：单次静态触摸永远不够，必须主动序列化地"询问"）→ **推导**（信息的物理实体化；epistemic vs aleatoric）→ **对比**（为什么视觉在灵巧操作微观尺度不足）→ **落点**（感知重构为主动的信息获取过程）。

经典"感知-规划-执行"架构隐含一个危险假设：传感器能提供关于状态的**充分统计量**。但高自由度灵巧手在部分可观测环境里，任何单一时刻的静态观测都拿不到完整状态——**这种信息缺失不是传感器精度问题，而是物理交互的内生属性**（手指必然自遮挡）。信息论于是把"感知"从被动接收，重构为**主动的、能量与信息动态交换**的过程：机器人每次运动不只改变物理状态，更改变**信息状态**——通过物理交互"询问"环境，最大化**信息增益 (IG)**。

### 1.1 信息的物理实体化：操作的"热力学"

> [!important] 减熵 = 压缩可行域 = 消耗能量换确定性
> "减少熵"在物理上对应压缩物体构型空间 (C-Space) 的**可行域体积**。每一次触摸、每一次滑动，都在消耗能量换取不确定性降低——这是灵巧操作的"热力学"基础。香农信息论在此不只是通信信道度量，更是**指导物理交互的势能函数**：机器人应流向"信息势能最低（不确定性最大）"的状态空间区域。摸钥匙时，手指自然奔向最能区分"钥匙 vs 硬币"的部位（锯齿边缘），而非反复摸同一处光滑面。

### 1.2 两种不确定性：只有一种值得探索

这一区分与 [[StochasticProcess#3.2 一个必须刻进脑子的区分：Aleatoric vs Epistemic|随机过程的 aleatoric/epistemic]] 完全一致，但在信息论里有更锋利的用途：

- **认知不确定性 (Epistemic)**：源于模型/数据匮乏（没摸过的物体背面、没掂过的质量）。**可通过主动探索消除**——对应高熵先验，观测累积使后验熵降低。
- **偶然不确定性 (Aleatoric)**：源于系统固有随机（摩擦锥边缘微滑、软指非线性形变、传感热噪）。**无法通过收集数据消除**，只能用鲁棒/风险敏感控制应对。

> [!important] 主动感知的第一铁律
> **只对 epistemic 不确定性做信息获取。** 摸钥匙时去摸"还没摸过的部位"（epistemic）有意义；反复在同一处感受热噪声抖动（aleatoric）则是浪费。混淆二者，机器人会"对着噪声电视机发呆"（§6 的 ICM 噪声电视机问题正源于此）。

### 1.3 为什么视觉在灵巧操作微观尺度不足

视觉再强，在灵巧操作的微观尺度也有三重局限：**遮挡**（手指必挡住接触区）、**光照/材质**（透明、反光、无纹理物体让深度相机失效）、**接触属性不可见**（摩擦系数、局部刚度、表面粗糙本质上看不见，只能摸）。于是触觉成了灵巧操作的"暗物质探测器"——它**局部、序列、主动**，必须通过时间累积构建空间认识，天然需要 [[StochasticProcess#5. 学习未知动力学：高斯过程与残差学习|高斯过程]]/[[StochasticProcess#4. 信念更新：从 EKF 失效到粒子滤波|粒子滤波]] 这类概率序列模型来整合碎片信息。**闭眼摸钥匙，正是"纯触觉、序列化、主动"的极致样例。**

------

## 2. 操作中的信息度量：熵、互信息、KL

> [!tip] 本节四拍
> **直觉**（要优化"信息增益"，先得能量化"信息"）→ **推导**（微分熵→互信息→KL）→ **对比**（三种度量各管什么）→ **联系**（互信息=期望 KL；EIG 是一切主动感知的目标函数）。

### 2.1 熵：可行域的体积

物理属性 $X$（表面几何、质心、摩擦）的密度 $p(x)$，其**微分熵** $H(X)=-\int p(x)\log p(x)\,dx$ 度量机器人对物体的"无知程度"。摸钥匙前，"是什么"的分布覆盖 {钥匙, 硬币, 纸巾, 打火机…}，$H$ 很大；摸到锯齿边缘后分布迅速收缩成尖峰，$H$ 骤降。**触觉探索本质是序列化熵减**——每一次接触都是对概率分布的一次切割。（微分熵在连续空间可为负，但我们只关心其**变化量**=信息增益。）

### 2.2 互信息：观测的"切割能力"

互信息 $I(X;Z)$ 量化观测 $Z$ 含多少关于 $X$ 的信息——**主动感知最核心的目标函数**：

$$
I(X;Z)=H(X)-H(X\mid Z)=\mathbb E_{z\sim p(z)}\big[D_{KL}(p(X\mid z)\,\|\,p(X))\big].
$$

（先验熵 − 观测后剩余熵 = 信息增益；亦等于"先验→后验"的期望 KL。）

> [!note] 逐步推导：三个等价形式从哪来（不跳步）
> 先把两个前置对象定义清楚，符号单位统一取 **nats**（$\log=\ln$；换 $\log_2$ 即得 bits）：
> - **条件熵** $H(X\mid Z)=\mathbb E_{z\sim p(z)}\big[H(X\mid Z=z)\big]=-\iint p(x,z)\,\log p(x\mid z)\,dx\,dz$：观测到 $Z$ **之后**、对 $X$ **平均**还剩多少无知（单位 nats）。注意是先对每个具体 $z$ 求 $H(X\mid Z=z)$，再按 $p(z)$ 加权——**不是**某个特定 $z$ 的结果。
> - **链式法则** $H(X,Z)=H(Z)+H(X\mid Z)=H(X)+H(Z\mid X)$：联合无知 = 先知道一个、再补另一个的条件无知（把 $\log p(x,z)=\log p(z)+\log p(x\mid z)$ 代入联合熵定义即得，无省略）。
>
> **① 互信息的对称性**。把定义 $I(X;Z)=\iint p(x,z)\log\frac{p(x,z)}{p(x)p(z)}\,dx\,dz$ 拆开：用 $p(x,z)=p(x)\,p(z\mid x)=p(z)\,p(x\mid z)$，两种拆法分别给出
> $$I(X;Z)=H(X)-H(X\mid Z)=H(Z)-H(Z\mid X)=H(X)+H(Z)-H(X,Z).$$
> 最后一式对 $X,Z$ 对称，故 $I(X;Z)=I(Z;X)$——**"$Z$ 告诉我们多少关于 $X$"恒等于"$X$ 告诉我们多少关于 $Z$"**。主动感知正利用这一点：难算的"观测能减少多少状态熵"可换算成好算的"状态如何切割观测分布"。
>
> **② 为什么等于期望 KL**。把外层 $p(z)$ 提出来：
> $$I(X;Z)=\int p(z)\underbrace{\Big[\int p(x\mid z)\log\tfrac{p(x\mid z)}{p(x)}\,dx\Big]}_{=\,D_{KL}(p(X\mid z)\,\|\,p(X))}dz=\mathbb E_{z}\big[D_{KL}(p(X\mid z)\|p(X))\big].$$
> 即：**每个观测把先验 $p(X)$ 推成后验 $p(X\mid z)$，推动幅度用 KL 量，按观测出现概率 $p(z)$ 一平均，就是互信息。** 摸钥匙每一下都在做一次这样的"推动"。
>
> **③ 为什么信息不会平均帮倒忙**。由 Jensen 不等式（$-\log$ 是凸函数）得 **Gibbs 不等式** $D_{KL}(\cdot\|\cdot)\ge0$，取等当且仅当两分布处处相等；故 $I(X;Z)\ge0$，即 $H(X\mid Z)\le H(X)$——**观测在期望意义下绝不增加无知**（对某个"倒霉" $z$，后验熵可能反而上升，但按 $p(z)$ 平均一定下降）。这是"多摸一下总不亏"的信息论保证，也是下面 EIG 恒为非负、值得优化的前提。

机器人选动作 $a$ 以最大化**预期信息增益 (EIG)**：

$$
a^*=\arg\max_a\ \mathbb E_{z\sim p(z\mid a)}\big[I(X;Z)\big].
$$

> [!note] 把 EIG 写清楚：期望在"未来未知观测"上（最易写混的一步）
> 上式紧凑但易误读——真正要最大化的是**给定动作 $a$ 后的条件互信息**，展开无跳步为：
> $$\mathrm{EIG}(a)=I(X;Z\mid a)=\underbrace{H(X)}_{\text{当前无知，与 }a\text{ 无关}}-\underbrace{\mathbb E_{z\sim p(z\mid a)}\big[H(X\mid z,a)\big]}_{\text{执行 }a\text{ 后的期望剩余无知}}.$$
> 逐符号：$a$=候选探测动作（去哪摸/传感器往哪放）；$p(z\mid a)=\int p(z\mid x,a)\,p(x)\,dx$=执行 $a$ 后的**边缘**观测分布（对当前信念 $p(x)$ 把未知真值积掉）；$H(X\mid z,a)$=**假设**看到 $z$ 后的后验熵（单位 nats）。因 $H(X)$ 是与 $a$ 无关的常数，故 $a^*=\arg\min_a\mathbb E_{z}[H(X\mid z,a)]$——**选那个让期望后验熵最低的动作**。全部难点都在这个对"尚未发生的 $z$"的期望：它逼出 §4 的蒙特卡洛**双重采样**（先从信念采假设真值、再从传感器模型采模拟观测）。

> [!important] 这一式是所有主动感知策略的数学基石
> 它说"去那个你预期能获得最多信息的地方"。难点在于：期望要对**未来未知的观测 $z$** 积分——这逼出蒙特卡洛采样（§4）或变分近似。摸钥匙时，大脑下意识算的就是这个 $a^*$：手指奔向"最可能一摸定音"的部位。

> [!important] BALD：把"信息增益"锋利地对准 epistemic —— disagreement = 认知不确定性（暗线枢纽）
> §1.2 立了铁律"只对 epistemic 探索"，但上面的 EIG 若把 $X$ 直接当"真值状态"，其熵里**混着不可消的 aleatoric 噪声**——机器人会被高噪声区（噪声电视机）骗走。**BALD (Bayesian Active Learning by Disagreement)** 用一个减法把 aleatoric 精确扣掉：把不确定性归到**模型参数 $\theta$**（epistemic 的载体），对候选查询 $x$ 求预测 $y$ 与 $\theta$ 的互信息作为采集函数：
> $$\underbrace{I(Y;\theta\mid x,\mathcal D)}_{\text{采集函数}}=\underbrace{H\big[\,\mathbb E_{\theta\sim p(\theta\mid\mathcal D)}\,p(y\mid x,\theta)\,\big]}_{\text{①总预测熵（先平均后求熵）}}-\underbrace{\mathbb E_{\theta\sim p(\theta\mid\mathcal D)}\big[H(y\mid x,\theta)\big]}_{\text{②各模型平均熵（先求熵后平均）}}.$$
> 逐项（单位 nats）：$\mathcal D$=已有触觉数据；$p(\theta\mid\mathcal D)$=参数后验（实践中用 ensemble / MC-dropout 近似）；**①** 把各模型预测先**平均**成一个 Bayesian model average 再求熵 = **总不确定 = epistemic + aleatoric**；**②** 对每个固定 $\theta$ 先求熵再平均 = 每个模型自认的**不可消噪声 = aleatoric**。此式正是 §2.2 的 $I=H(Y)-H(Y\mid\theta)$ 换了条件变量，二者之差 = **epistemic = 模型间分歧 (disagreement)**。
> **为什么恰是"分歧"**：当所有模型个个自信（②小）却彼此不一致（①大）时差最大——"我们每个都很确定，但答案互相打架"正是"再采一个样最能长知识"的信号；反之若各模型都对同一点同样困惑（①②都大、差≈0），那是 aleatoric 噪声，BALD 自动**不去**。这就把 §1.2 的铁律从口号变成了可计算的公式。
> **暗线归位（认知不确定性三用 = 信息增益）**：BALD 的分歧项，与 [[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性|PETS 里 Bootstrap Ensemble 的预测方差]] 是同一个 epistemic（规划里当护栏，别钻模型空子），也等同 [[StochasticProcess#3.2 一个必须刻进脑子的区分：Aleatoric vs Epistemic|随机过程里的 epistemic]]；把它当**采集函数**去主动采样，就是 [[ReinforcementLearning#7.1 用信息论刻画探索|RL 用信息论刻画探索]] 里的"信息增益探索罗盘"；把它当**任务难度信号**反向生成课程，就是 [[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成|无知即课程]]。**一个减法（总熵 − 期望条件熵），三处复用——这是全库最硬的一条暗线在信息论里的原始定义。**

### 2.3 KL 散度：信念跳变与"贝叶斯惊奇"

$D_{KL}(P\|Q)$ 衡量两分布的非对称差异，常用来量化先验信念 $b_t$→后验 $b_{t+1}$ 的跳变幅度。**贝叶斯惊奇 (Bayesian Surprise)**：若触觉实际接触位置与视觉预估差异巨大，KL 极高——这意味着模型需大修，或当前探索动作极有价值。主动探索常倾向"去最令我惊讶的地方看看"（这正是 §6 内在动机的信息论形式）。

| 度量 | 符号 | 物理含义 | 摸钥匙/操作场景 |
|:--|:--|:--|:--|
| 微分熵 | $H(X)$ | 可行域体积、不确定总量 | 摸之前"是什么"的无知 |
| 互信息 | $I(X;Z)$ | 观测对状态空间的切割力 | 评估"该摸哪、传感器放哪" |
| KL 散度 | $D_{KL}(P\|Q)$ | 信念更新幅度、惊奇程度 | 内在动机奖励、sim-real 分布对齐 |

> [!note] 跨原理联系
> 互信息=期望 KL 这一等式，把 §2.2 与 §2.3 缝在一起；而"$Q-\beta\,$KL-到-参考"的最大熵 RL（[[ReinforcementLearning#5.0 先立统一框架：一切都是"在参考分布附近改进"|RL §5.0]]）、信息瓶颈（§5）、empowerment（§6）全是这三个度量的不同组合。**熵、互信息、KL 是信息论的"三原色"，后面所有算法都是它们的调色。**

### 2.3.1 前向 KL vs 反向 KL 的几何：为什么方向决定 covering vs seeking（SFT vs RL）

> [!tip] 本小节四拍
> **直觉**（同一个 KL，方向一换训练行为就翻脸：一个"重召回、别漏"、一个"重精确、别越界"）→ **推导**（把 $\int p\ln(p/q)$ 的被积函数在 $q\to0$ 处摊开，逐符号标 nats，看惩罚落在谁头上）→ **对比**（前向 KL=SFT="学会做" vs 反向 KL=RL="学会选"）→ **联系**（[[ReinforcementLearning#5.0 先立统一框架：一切都是"在参考分布附近改进"|RL §5.0]] 的统一框架、[[StochasticProcess#6.4 扩散策略 = 学出来的逆向 SDE：把 §2 的 SDE 倒过来跑|扩散的前向/反向]]、[[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器|模仿的均值坍缩]]）。

§2.3 说 KL 度量"信念跳变"，但故意藏了一件事：**KL 不对称，而这份不对称恰好把"模仿"与"强化"两种学习范式在几何上分开了**。一句话点破根源——

> [!abstract] KL 方向的唯一来源：期望在谁的分布上取
> $D_{KL}(p\|q)=\mathbb E_{x\sim p}[\ln\frac{p(x)}{q(x)}]$。**期望符号下面站着谁，谁就是采样源、就是每个位置的权重来源**。某个 $x$ 在这个分布里越常被采到，它对 KL 总值的贡献权重就越大。$p\|q$ 与 $q\|p$ 差的不是被比较的两个分布，而是**从哪个分布采样去做这个平均**。摸钥匙母题里：前向 = "口袋里真实会出现的每样东西，我的信念都得接住"；反向 = "我信念里认定会摸到的，必须是口袋里真的有的"。

**推导（被积函数在支撑错配处的行为，不跳步）**。约定自然对数 $\ln$，故单位 **nats**（换 $\log_2$ 即 bits）；$p,q$ 为概率密度（无量纲）。

**① 前向 KL** $D_{KL}(p\|q)=\int p(x)\ln\dfrac{p(x)}{q(x)}\,dx$，取 $p$=**目标/数据分布**、$q$=**模型分布**。被积函数 $g(x)=p(x)\ln\dfrac{p(x)}{q(x)}$。
- **情形 A（$p(x)>0$ 而 $q(x)\to0^+$）**：$\ln\frac{p}{q}\to+\infty$，且前面乘的是**正权重** $p(x)>0$ → $g(x)\to+\infty$，积分爆炸。**结论：凡 $p>0$ 处 $q$ 都不敢为 0**——$q$ 被迫铺满 $p$ 的**全部**支撑 = **mode-covering / mass-covering**。代价：为同时覆盖多个峰，$q$ 连峰间谷底都得摊概率，于是被"抹平"成跨峰的均值（这就是别名 **mean-seeking** 的来历）。
- **情形 B（$p(x)=0$）**：$g(x)=0\cdot\ln\frac{0}{q}$，用极限约定 $\lim_{p\to0^+}p\ln p=0$ 得 $g\to0$——**不惩罚**。即 $q$ 在"目标本没有"的地方放概率，前向 KL 不管。$q$ 可以过度铺展、宁滥勿缺。

**② 反向 KL** $D_{KL}(q\|p)=\int q(x)\ln\dfrac{q(x)}{p(x)}\,dx$，**期望改到 $q$（模型）上取**。被积函数 $h(x)=q(x)\ln\dfrac{q(x)}{p(x)}$。
- **情形 A'（$q(x)>0$ 而 $p(x)\to0^+$）**：$\ln\frac{q}{p}\to+\infty$ 乘正权重 $q>0$ → $h\to+\infty$。**结论：凡 $p=0$ 处 $q$ 必须严格 =0**（**zero-forcing / 零强迫**）——$q$ 绝不敢跑到目标支撑之外。
- **情形 B'（$q(x)=0$）**：$h\to0$，**不惩罚**。→ $q$ 可以**主动丢弃** $p$ 的某些峰（那里令 $q=0$ 零代价）。合起来：$q$ 缩到 $p$ 的**某一个高概率峰**、越贴越尖 = **mode-seeking / mode-selecting**。

| 维度 | 前向 KL $D_{KL}(p\|q)$ | 反向 KL $D_{KL}(q\|p)$ |
|:--|:--|:--|
| 期望/采样源 | 目标 $p$（数据、老师） | 模型 $q$（自己生成） |
| 无穷惩罚的触发 | 目标有、模型没有（漏峰） | 模型有、目标不认（越界） |
| 几何行为 | mode-covering（抹平、跨峰均值） | mode-seeking（锐化、择一峰） |
| 检索直觉类比 | 重召回（别漏） | 重精确（别错） |
| 对应后训练 | **SFT / 传统蒸馏 = 学会做** | **KL 正则 RL/RLHF = 学会选** |

**为什么 SFT ≈ 最小化前向 KL（"学会做"）**。SFT 是对人工演示 $y^\*\sim p_{\text{data}}$ 做最大似然：$\max_\pi\ \mathbb E_{x\sim D,\,y\sim p_{\text{data}}}[\ln\pi(y\mid x)]$。因为 $p_{\text{data}}$ 固定（其熵是与 $\pi$ 无关的常数），把它加进来配平即得
$$\arg\max_\pi\ \mathbb E_{y\sim p_{\text{data}}}[\ln\pi]\ \equiv\ \arg\min_\pi\ \mathbb E_{y\sim p_{\text{data}}}\Big[\ln\tfrac{p_{\text{data}}}{\pi}\Big]=\arg\min_\pi D_{KL}(p_{\text{data}}\|\pi).$$
期望在**数据分布**上取 → 前向 KL → covering：**演示里出现过的每一种答法，模型都被推着去覆盖**。好处=学会格式/风格/指令跟随；病灶=噪声答案、平庸答案、混杂风格全都照单全收，且**没有"选优"压力**。这正是灵巧操作里模仿学习的老毛病：多峰演示被抹成均值动作（[[RepresentationLearning#1.2 接触的非凸非光滑：神经网络的"均值化"陷阱|均值化陷阱]]），也是为什么要用[[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器|扩散策略]]把"覆盖"做对——扩散用 score matching 建**整条分布**而非其均值，于是 covering 多峰而不坍缩。

**为什么 RL/RLHF ≈ 最小化反向 KL（"学会选"）**。带 KL 正则的 RLHF 目标 $\max_\pi \mathbb E_{y\sim\pi}[r(x,y)]-\beta\,D_{KL}(\pi\|\pi_{\text{ref}})$，其闭式最优是一个**由奖励诱导的目标分布** $p^\*(y\mid x)\propto\pi_{\text{ref}}(y\mid x)\,e^{r(x,y)/\beta}$，代回可整理成 $\arg\min_\pi D_{KL}(\pi\|p^\*)$。**期望在当前策略 $\pi$（模型自己生成的轨迹）上取** → 反向 KL → seeking：**先暴露自己的生成分布，再把概率质量往高奖励峰上收**，主动丢弃低奖励模式。好处=偏好对齐、行为压缩、"从会做到会选"；这与 [[ReinforcementLearning#5.0 先立统一框架：一切都是"在参考分布附近改进"|RL §5.0 的"KL-到-参考"统一框架]]、[[ReinforcementLearning#5.4.2 统一梯度视角：SFT、蒸馏与 RL 本是一家|§5.4.2 的统一梯度视角]] 是同一件事的信息论侧写，也接上 §2.4 由最大熵原理导出的 Boltzmann 目标分布 $p^\*\propto e^{r/\beta}$。

> [!important] 更深一层：为什么反向 KL 的 RL "天然 KL 小"——交替投影 = EM
> 反向 KL 优化在二元奖励下等价于信息几何的**交替投影 (Alternating Projection)**，即 EM：
> - **I-projection（E 步）**：$q_t=\arg\min_{q\in\mathcal O}D_{KL}(q\|\pi_t)$，闭式解 $q_t(y\mid x)\propto\pi_t(y\mid x)\,e^{\beta R(x,y)}$——在二元奖励下就是"**把 $\pi_t$ 自采样的池子里奖励为 0 的样本删掉**"。这正是"采样并按奖励筛选"。
> - **M-projection（M 步）**：$\pi_{t+1}=\arg\min_{\pi}D_{KL}(q_t\|\pi)$，等价于**对筛出的好样本做一次局部 MLE = 一次小 SFT**。
>
> 关键：$q_t$ 脱胎于 $\pi_t$ 自身支撑，两步都在**自己已经会说的话**里 reweight，参数只在流形上"拓扑保距"地小步滑动 → 这从数学底层解释了 RL 微调不易灾难性遗忘。对照之下，SFT 是朝**远方固定靶心** $p_{\text{data}}$ 的前向 KL 拉扯，梯度 $-\nabla_\theta\ln\pi(y^\*\mid x)$ 要强行拔高原本概率极低的答案，猛撕参数流形。**同一支笔：前向 KL 从外部拽，反向 KL 从内部收。**

> [!warning] 边界澄清（别把两件事混成一件）：on-policy ≠ 反向 KL
> "RL 对应反向 KL"只在 **KL 正则 / 最大熵 / 带 reference policy** 的框架下严格成立；纯粹最大化累计奖励的传统 RL 虽也在当前策略上采样，却不天然写成反向 KL。要拆成**两层独立的问题**：
> - **第一层：轨迹从谁来？**（on-policy＝来自 student/model；off-policy＝来自 data/teacher）——这是**采样源**。
> - **第二层：KL 往哪个方向写？**（$D_{KL}(\pi\|\cdot)$ 才是反向）——这是**分布比较方向**。
>
> 反例：on-policy distillation 的轨迹来自 student（on-policy），但每个 student 访问到的状态上仍可能用 teacher→student 的 token 级 $D_{KL}(\text{teacher}\|\text{student})$——**状态分布 on-policy，动作分布上的 KL 却是前向**。所以"老师先走学生学"（传统蒸馏，前向）和"学生先走老师纠"（on-policy distillation）区别在**采样源**，而非一定在 KL 方向。一句话：**谁在采样 ≠ 谁在评价**。

**灵巧操作落点**。同一支笔（[[ReinforcementLearning#1.1 母题解剖：转一支笔到底在求解什么？|转笔母题]]）上，这条几何直接指导"先模仿后强化"的分工：
- **模仿学习阶段 = 前向 KL covering**：BC / 扩散策略去**覆盖**人类演示里所有转笔打法（含平庸的、别扭的），先把动作分布铺开、把格式学会；
- **RL 微调阶段 = 反向 KL seeking**：从覆盖好的分布里**挑出**那一种最稳、最高奖励的转法，把质量往它身上收、丢掉其余模式——这正是 [[ReinforcementLearning#7.4 模仿学习与策略蒸馏：把演示收编进统一梯度|§7.4 把演示收编进统一梯度]] 与 [[ReinforcementLearning#9.3 真机高效 RL：把"模仿×强化"缝合线收口|§9.3 "模仿×强化"缝合]] 在做的事。**covering 给"会做的底"，seeking 给"选优的锐"——缺一不可。**

> [!note] 提议第 8 条全库暗线：「KL 方向决定 covering vs seeking」
> 这条几何贯穿多个 Foundation，值得单列为一条记忆暗线（区别于本讲"认知不确定性/主动感知"两条主线）：
> **前向 KL（在目标上取期望）→ covering / 抹平 / 模仿 / "学会做"；反向 KL（在模型上取期望）→ seeking / 锐化 / 强化 / "学会选"。** 落点：本讲 §2（度量）· [[ReinforcementLearning#5.0 先立统一框架：一切都是"在参考分布附近改进"|RL §5.0/§5.4.2/§7.4]]（后训练分工）· [[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器|RepLearning §2.2]]（covering 多峰的正确做法）· [[StochasticProcess#6.4 扩散策略 = 学出来的逆向 SDE：把 §2 的 SDE 倒过来跑|StochProc §6.4]]。
> **一个必须澄清的假朋友**：扩散模型的"**前向/反向**"指的是加噪/去噪的**时间方向**（forward/reverse SDE），与这里 KL 的"前向/反向"（分布比较方向）**不是同一回事**——两者同属"方向性对偶"的美学，但机制无关，切勿混为一谈。（这类"名字撞车"正是逻辑跳步的高发地，特此点破。）

### 2.4 最大熵原理：belief 从哪来，兼通往最大熵 RL 的桥

> [!tip] 本小节补的是 §2 漏掉的一步——"度量都有了，可 belief/策略这个分布本身该长什么样？"

前面 §2.1–2.3 全都**假设已有** belief $p(x)$，但闭眼摸钥匙的**第一瞬间**——还没摸、只知道"口袋里常见物件就那几样、平均重约几十克"——该拿什么当先验？**最大熵原理 (Maximum Entropy Principle, Jaynes 1957)**：在满足所有已知约束的分布里，选**熵最大**那个——因为熵最大 ⇔ 假设最少 ⇔ 只承认约束、绝不偷塞没有依据的信息。

**直觉**：任何比"最大熵解"更尖的分布，都在某处悄悄断言"这里更可能"，而这份自信无数据支撑——那是幻觉式的过度确定，会让主动感知从错误先验出发、把手伸错地方。

**推导（Lagrange 乘子，不跳步）**。设离散状态 $x\in\{1,\dots,n\}$，约束为若干期望 $\sum_x p(x)f_k(x)=\mu_k$（$f_k$=第 $k$ 个可测特征，如"是否金属""质量"；$\mu_k$=其已知均值）外加归一化 $\sum_x p(x)=1$。求
$$\max_{p}\ H(p)=-\sum_x p(x)\ln p(x)\quad\text{s.t.}\ \sum_x p(x)f_k(x)=\mu_k,\ \sum_x p(x)=1.$$
构造 Lagrangian（$\lambda_k,\nu$=乘子）：$\mathcal L=-\sum_x p\ln p-\sum_k\lambda_k(\sum_x pf_k-\mu_k)-\nu(\sum_x p-1)$。对**单个** $p(x)$ 求偏导并令零（用 $\partial_p(-p\ln p)=-\ln p-1$）：
$$-\ln p(x)-1-\sum_k\lambda_k f_k(x)-\nu=0\ \Longrightarrow\ p(x)=\frac1Z\exp\!\Big(-\sum_k\lambda_k f_k(x)\Big),$$
其中 $Z=\sum_x\exp(-\sum_k\lambda_k f_k(x))$=配分函数（吸收常数 $\nu$、保证归一），乘子 $\lambda_k$ 反解自约束 $\mu_k$。**结论：最大熵解一定是指数族/Boltzmann 分布。** 物理对应：$\lambda_k$ = "温度倒数 × 每单位特征的能量代价"——这正是统计力学 Boltzmann 分布 $p\propto e^{-E/kT}$ 的信息论来历（§1.1 "操作的热力学"在此闭合）。

> [!important] 通往最大熵 RL 的桥（最大熵原理 = SAC 的地基）
> 把上式的"状态 $x$"换成"动作 $a$"、"特征约束"换成"期望回报约束 $\mathbb E_\pi[Q(s,a)]\ge$ 常数"，**同一条 Lagrange 推导**立刻给出 **Boltzmann 策略** $\pi(a\mid s)\propto\exp\!\big(Q(s,a)/\alpha\big)$——"在给定平均回报下最随机"的策略。这正是 [[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|SAC 的"熵即柔顺"]] 与 [[ReinforcementLearning#5.0 先立统一框架：一切都是"在参考分布附近改进"|RL §5.0 的"KL-到-参考"统一框架]] 的信息论根：温度 $\alpha$（单位与 $Q$ 同，nats·回报量纲）就是这里乘子的倒数，$\alpha$ 大→熵项主导→策略软、探索广；$\alpha$ 小→回报主导→策略贪、尖锐。**最大熵原理 / Boltzmann 分布 / SAC 策略 / §4.3 的"熵→刚度"，是同一式子在 belief、统计力学、策略、阻抗四处的化身。**

> [!note] 落回 belief——主动感知的初始条件（主动感知暗线）
> 主动感知是一台"熵减机器"：§2–4 的 EIG/NBT/信念空间规划全在**降低** belief 的熵。最大熵原理补的是这台机器的**初始条件**——[[StochasticProcess#4.0 贝叶斯滤波的骨架：预测-更新递推（KF→EKF→UKF→PF 一张阶梯）|贝叶斯滤波的先验]] 应取"满足已知约束的最大熵分布"（最诚实的"我不知道"），随后每次触摸用 §2.2 的互信息把它一刀刀削尖。**先验不能拍脑袋，必须是最大熵；否则你从虚假的自信出发，越摸越偏。**

------

## 3. 概率接触模型与高斯过程探索

> [!tip] 本节四拍
> **直觉**（摸钥匙时，大脑在"已摸到的点"之间脑补出整个形状，并知道哪里还没把握）→ **推导**（GPIS 把表面建成隐函数，GP 给均值+方差）→ **对比**（最大方差 vs EI vs 轮廓信息增益，哪种采集函数适合触觉）→ **落点**（NBT：去物体表面附近最不确定处）。

### 3.1 隐式曲面高斯过程 (GPIS)

把物体表面建成隐函数 $f(x)=0$：空间点 $x$ 的函数值 $f(x)$ = 到表面的有向距离 (SDF，见 [[ComputationalGeometry|SDF]])。接触点 $y=0$、自由空间 $y>0$、内部 $y<0$。GP 给函数上的分布 $f(x)\sim\mathcal{GP}(m,k)$，对查询点输出高斯 $\mathcal N(\mu_*,\sigma_*^2)$——**均值是形状估计、方差是该估计的把握**，天然契合主动探索。核函数 $k(x,x')$（RBF/Matérn）的长度尺度对应物体的**特征尺度**（纹理粗糙度/几何特征大小）：太大则过度平滑掉钥匙齿，太小则泛化差（认为相邻两点无关）。

### 3.2 采集函数与下一最佳触点 (NBT)

下一个探测点 $x_{next}$ 选哪？这是贝叶斯优化问题，需定义**采集函数** $\alpha(x)$ 平衡探索-利用：

| 采集函数 | 形式 | 触觉探索中的问题 |
|:--|:--|:--|
| **最大方差** | $\alpha=\sigma^2(x)$ | 纯探索，但**远离物体的空气也方差大**——机器人会去"摸空气" |
| **期望改进 EI** | $\mathbb E[\max(0,f_{best}-f)]$ | 找极值，但触觉重建要找**零水平集**而非极值，不直接适用 |
| **轮廓信息增益** | $\alpha=\sigma(x)\exp(-\mu(x)^2/2w^2)$ | ✅ 高斯加权当"注意力"，只在**表面附近** $\mu\approx0$ 做高不确定探索 |

> [!important] 轮廓跟随：把探索"钉"在物体表面
> 单纯降低全局方差是不够的——我们只关心**物体表面附近**的方差。轮廓信息增益 $\alpha_{surface}=\sigma(x)\exp(-\mu^2/2w^2)$ 用高斯加权项当注意力，使探索集中在边界（"轮廓跟随"）。这就是闭眼摸钥匙的策略：**沿着已摸到的边缘往下摸，而不是把手伸到口袋空处乱抓。**

> [!important] NBT 的 $\sigma^2(x)$ 就是 epistemic 不确定性——"认知不确定性三用"暗线的探索罗盘
> GP 后验方差有闭式 $\sigma_*^2(x)=k(x,x)-\mathbf k_*^\top(K+\sigma_n^2 I)^{-1}\mathbf k_*$（$k(x,x)$=先验方差；$\mathbf k_*$=查询点与已测点的核向量；$K$=训练核阵；$\sigma_n^2$=观测噪声方差；单位=SDF 值的平方，离已测点越远越大）。它度量的是**"这里我还没摸过、模型没把握"——可通过采样消除的 epistemic 不确定性**，而非 §1.2 的 aleatoric 噪声（后者由核里的 $\sigma_n^2$ 项承载，采再多点也不降）。所以 NBT 去"表面附近最高 $\sigma$ 处"，本质就是把探测器对准 **epistemic 最大处**。
> **暗线归位**：§2.2 BALD 的"模型分歧"、[[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性|PETS 里 Bootstrap Ensemble 的预测方差]]、这里 GP 的后验方差，是**同一个 epistemic 的三种估计器**（ensemble 分歧 / bootstrap 方差 / GP 闭式方差）；把它当采集函数去主动采样，正是 [[ReinforcementLearning#7.1 用信息论刻画探索|RL 用信息论刻画探索]] 里的"信息增益探索罗盘"（三用之第二用）。用 GP 而非神经网络给这个 epistemic 的理由（小样本、闭式方差、无需训一堆模型）见 [[StochasticProcess#5.2 为什么用高斯过程 (GP) 而非神经网络|随机过程 §5.2]]。**一句话：NBT 不是"去方差大处"，而是"去还能长知识（epistemic）的地方"——认知不确定性三用落在触觉探索上的样子。**

```python
import numpy as np
# GPIS 触觉探索器：用 GP 指导"下一最佳触点"（去防御代码，聚焦逻辑）
class GPIS_Tactile_Explorer:
    def __init__(self, length_scale=0.05, noise_var=1e-4):
        self.l, self.noise = length_scale, noise_var
        self.X_train, self.Y_train = [], []          # 接触点坐标 / SDF 值（接触点=0）

    def rbf_kernel(self, x1, x2):                     # 相关性随距离衰减
        sq = np.sum(x1**2,1).reshape(-1,1) + np.sum(x2**2,1) - 2*x1@x2.T
        return np.exp(-0.5/self.l**2 * sq)

    def update_model(self, contact_point, is_contact=True):
        self.X_train.append(contact_point)
        self.Y_train.append(0.0 if is_contact else 0.01)   # 接触 SDF=0，自由空间>0
        # 实战还需加基于法向的虚拟点约束梯度，否则曲面可任意穿过接触点

    def predict(self, x_query):
        X = np.array(self.X_train)
        K  = self.rbf_kernel(X, X) + self.noise*np.eye(len(X))
        Ks = self.rbf_kernel(X, x_query)
        Kss = self.rbf_kernel(x_query, x_query) + self.noise
        L = np.linalg.cholesky(K)                     # Cholesky 数值稳定
        alpha = np.linalg.solve(L.T, np.linalg.solve(L, np.array(self.Y_train)))
        mu = Ks.T @ alpha
        v = np.linalg.solve(L, Ks)
        var = np.diag(Kss - v.T @ v)
        return mu, var

    def next_best_touch(self, bounds, n=1000):
        cand = np.random.uniform(bounds[:,0], bounds[:,1], (n, 3))   # 候选触点
        mu, var = self.predict(cand)
        sigma = np.sqrt(np.maximum(var, 0))
        surface_w = np.exp(-(mu**2)/(2*0.02**2))      # ★ 表面注意力：只在 μ≈0 处探索
        return cand[np.argmax(sigma * surface_w)]     # 采集值 = 不确定性 × 表面权重
```

### 3.3 扩展到物理属性：摩擦图与刚度图

GPIS 不限于几何：同一框架可建**摩擦图**（手指滑动时 GP 输出 $\mu$，高方差=不知道这里滑不滑——对防钥匙滑落至关重要）或**刚度图**。**多模态融合**：视觉 RGB-D 提供 GP 的均值先验、大减触觉次数，触觉修正视觉在高光/透明/遮挡处的错误方差，通过贝叶斯融合或专家乘积实现（接 [[RepresentationLearning|表征学习]] 的多模态融合）。

------

## 4. 信念空间规划：从单点贪心到序列主动感知

> [!tip] 本节四拍
> **直觉**（摸钥匙不是"摸一下最优的点"，而是规划一连串触摸）→ **推导**（POMDP→信念空间；粒子滤波表多峰信念）→ **对比**（KF/EKF/PF/RBPF 在操作中的适用性）→ **落点**（不确定性驱动柔顺=双重控制的物理涌现）。

单步 NBT 易陷局部最优——降低了局部不确定，却对最终目标无益。需在时间视界上规划，引入 **POMDP**：不在物理状态空间、而在**信念空间**（概率分布的空间，维度通常无穷）规划。

### 4.1 粒子滤波与 RBPF：表达多峰信念

接触遮挡造成**多峰分布**（钥匙齿朝左还是朝右？双峰），高斯假设的 EKF 失效。**粒子滤波**用加权粒子 $\{x^{(i)},w^{(i)}\}$ 近似任意 belief（与 [[StochasticProcess#4. 信念更新：从 EKF 失效到粒子滤波|随机过程 §4]] 同一对象）。**Rao-Blackwellized PF (RBPF)** 把状态分解 $x=(x_{pose},m_{shape})$，利用条件独立 $p(x_{pose},m_{shape}\mid z)=p(m_{shape}\mid x_{pose},z)\,p(x_{pose}\mid z)$：每个粒子维护一个位姿假设 + 一个条件化的形状图——"粒子 A 认为钥匙在左且齿朝上、粒子 B 认为在右且齿朝下"，触觉数据进来后错误假设权重衰减、收敛到真相。

| 滤波器 | 状态表示 | 适用 | 局限 |
|:--|:--|:--|:--|
| KF | 高斯 $(\mu,\Sigma)$ | 线性、微扰跟踪 | 不能表多峰 |
| EKF | 高斯（线性化） | 简单几何接触 | "在左还是在右"的歧义无解 |
| PF | 粒子集 | 非线性/非高斯/全局定位 | 高维粒子数指数爆炸 |
| RBPF | 粒子 + 解析分布 | 联合定位与建图、复杂物体 | 需特定条件独立结构 |

### 4.2 信息增益目标与粒子近似

信念空间规划的目标函数把探索-利用写进一式：

$$
J=\sum_t\Big(\underbrace{C(b_t,u_t)}_{\text{任务代价}}-\lambda\underbrace{I(X;Z_{t+1}\mid b_t,u_t)}_{\text{信息增益}}\Big).
$$

$\lambda$ 大则强好奇、$\lambda$ 小则专注任务。难点：计算连续状态/观测的互信息极贵，且要算**尚未发生的观测**的增益——需**模拟测量（双重采样）**：① 从 belief 采假设状态 → ② 从传感器模型采模拟观测 → ③ 用模拟观测更新 belief、算后验-先验 KL：

$$
\mathrm{MI}(b,u)\approx\sum_{z_j\in Z_{MC}}p(z_j\mid b,u)\,D_{KL}\big(b'(x\mid z_j,u)\,\|\,b^-(x\mid u)\big).
$$

```python
import numpy as np
# 粒子框架下估计候选动作的预期信息增益（去防御代码）
def expected_information_gain(particles, weights, action,
                             motion_model, sensor_model, n_sim=10):
    pred = motion_model.propagate(particles, action)        # 1) 预测：执行候选动作后粒子如何动
    total_kl = 0.0
    for _ in range(n_sim):                                   # 2) 模拟未来可能的观测（对 p(z|b,u) 采样）
        idx = np.random.choice(len(particles), p=weights)
        sim_z = sensor_model.sample(pred[idx])              #    从"假设真值"生成合成观测
        new_w = weights * np.array([sensor_model.likelihood(sim_z, p) for p in pred])  # 3) 虚拟更新
        new_w = new_w/new_w.sum() if new_w.sum()>0 else weights
        total_kl += np.sum(new_w * np.log(new_w/(weights+1e-9) + 1e-9))  # 4) 后验-先验 KL ≈ 信息增益
    return total_kl / n_sim
```

实时控制中常用剪枝或 Unscented Transform 加速。

### 4.3 不确定性驱动柔顺：双重控制的物理涌现

> [!important] "软-硬"切换不是编程规则，而是信息论的自然涌现
> 闭眼摸钥匙时，**不确定时手会变软、大范围扫掠**（防意外碰撞损伤、增大接触面积获取更多触觉信息）；**一旦摸到并确定位置（熵减），手瞬间变硬精确捏取**。这正是信念空间规划在力学层面的投射——为最大化信息增益、最小化期望碰撞代价，系统自动选择柔顺控制。这就是**双重控制 (Dual Control)**：控制不仅为改变状态，也为探测系统参数。它把信息论与 [[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|阻抗控制]]、[[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|SAC 的熵即柔顺]] 在物理层面统一了起来——**高熵→低刚度→探索，低熵→高刚度→执行**，一条线贯穿信息论、控制、RL。

------

## 5. 信息瓶颈：最优表征的信息论基础

> [!tip] 本节四拍
> **直觉**（GelSight 一帧含百万像素，但控制只需"是钥匙、接触在指尖偏左"几个 bit——该扔掉什么？）→ **推导**（率失真→信息瓶颈→变分 VIB）→ **对比**（IB vs 率失真：保留对 $X$ 自身 vs 对目标 $Y$）→ **联系**（压缩=去噪；IB↔empowerment 对偶）。

### 5.1 率失真：压缩的理论下界

> [!theorem] 率失真函数 (Shannon, 1959)
> 给定信源 $X\sim p(x)$ 与失真度量 $d(x,\hat x)$，在平均失真 $\le D$ 时的最小编码速率：
> $$R(D)=\min_{p(\hat x\mid x):\,\mathbb E[d]\le D}I(X;\hat X).$$

> [!note] 为什么 $R(D)$ 是"下界"、形状如何（不跳步）
> **下界的来历**：任何把 $X$ 编码成 $\hat X$ 的方案都构成马尔可夫链 $X\to\text{码字}\to\hat X$，由**数据处理不等式**（$X-\text{码}-\hat X$ 上互信息不增），传输码率 $\ge I(X;\hat X)$；在失真约束 $\mathbb E[d]\le D$ 下对所有合法的 $p(\hat x\mid x)$ 取下确界，就得到"再省也省不过"的 $R(D)$——它是压缩率的**信息论地板**，不是某个算法的性能而是极限。
> **形状（三个必背性质/端点）**：① $R(D)$ **非增且凸**（$I(X;\hat X)$ 关于 $p(\hat x\mid x)$ 是凸的，而约束集随 $D$ 增大只会放松，取 min 只会更小）；② $D=0$（无损）时 $R(0)=H(X)$——退回香农信源编码，无损压缩极限就是熵；③ 存在 $D_{\max}$（令 $\hat X$ 恒取最优常数即可达）使 $R(D_{\max})=0$，即"允许糊到某程度，一个 bit 都不用传"。触觉带宽设计就是在这条凸曲线上，按控制能容忍的失真 $D$ 反读所需 bit 数。$R(D)$ 无闭式时用 **Blahut–Arimoto** 交替迭代求解（与 §6.1 empowerment 变分界同源的交替优化思路）。

**触觉含义**：GelSight 的 $640\times480$ 图是高带宽流，控制只需极低维信息（接触法向、滑移方向）。率失真给出"**最少多少 bit 才能保证控制精度**"的理论下界，直接指导传感器-控制器带宽与嵌入式触觉编码器的压缩率。

> [!abstract] 好的压缩即好的去噪 — 压缩-去噪对偶（Song, Özgür & Weissman 2025）
> **核心定理**：对经无记忆信道 $P_{Z\mid X}$ 观测到的平稳遍历源 $X^n$，若选**与信道匹配的失真度量** $\rho(z,y)=-\log P_{Z\mid X}(z\mid y)$，则"好的"有损编码器的重构 $Y^n$ **同时也是对源 $X^n$ 的最优去噪**——重构序列渐近等价于从后验 $P_{X\mid Z}$ 独立采样（满足 $X^n-Z^n-Y^n$ 马尔可夫链）。
> **深化**：传统理解 IB 是率失真在 $Y\ne X$ 时的推广；新理解是——**即使 $Y=X$（自编码去噪），选对失真度量就能让压缩自动实现最优去噪**，这解释了为何 autoencoder/VAE 天然能去噪：**压缩本质上就是在去噪**。
> **灵巧操作关联**：① 电容触觉的非线性噪声（[[SignalProcessing#2.1 电容式触觉：超弹性与边缘场的非线性纠缠|超弹性与边缘场]]）可用此框架去噪；② VIB/VAE 在接触状态估计中的压缩行为本身就在去噪，失真水平应匹配观测噪声熵率；③ sim-real 域差异可视为"信道噪声"，压缩表征自然滤掉域特异细节、保留域不变任务信息（接 [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|sim-to-real]]）。

### 5.2 信息瓶颈：压缩与预测的权衡

> [!note] 教科书参考
> IB 由 Tishby, Pereira & Bialek (1999) 提出，是表征学习的核心信息论框架（深关联 [[RepresentationLearning]]）。

**IB 解答表征学习的核心问题**：给定输入 $X$，学一个压缩表征 $Z$，**保留对目标 $Y$ 的预测能力、丢弃无关细节**。在灵巧操作里：$X$=高维原始观测（触觉图/点云/关节序列）、$Z$=低维 latent（策略输入/世界模型）、$Y$=任务信息（位姿/接触状态/抓取成败）。目标函数：

$$
\mathcal L_{IB}=I(Z;X)-\beta\,I(Z;Y),
$$

$I(Z;X)$=表征复杂度（越小越压缩）、$I(Z;Y)$=预测能力（越大越有用）、$\beta$=权衡旋钮。$\beta\to0$ 过度压缩成废表征、$\beta\to\infty$ 不压缩则对噪声敏感、**适中 $\beta$ 才得鲁棒泛化**。

> [!note] IB 的拉格朗日结构与 deterministic annealing：$\beta$ 是一支"温度旋钮"（不跳步）
> **① 为什么是拉格朗日式**。IB 原问题是**带约束的压缩**：在"保留对 $Y$ 至少这么多预测信息" $I(Z;Y)\ge I_0$ 前提下最小化编码率 $I(Z;X)$。写成 Lagrangian（$\beta\ge0$=约束乘子）即 $\min_{p(z\mid x)}I(Z;X)-\beta\,I(Z;Y)$——正是上面的 $\mathcal L_{IB}$。所以 $\beta$ 不是随手加的权重，而是"预测信息约束"的**影子价格**（每多要 1 nat 预测信息，愿付几 nat 压缩率）。
> **② 自洽方程（representation 的显式解）**。对 $p(z\mid x)$ 变分求极值（同 §2.4 的 Lagrange 套路，只是决策变量换成条件分布），得三条耦合的自洽方程，其编码器解为
> $$p(z\mid x)=\frac{p(z)}{Z(x,\beta)}\exp\!\big(-\beta\,D_{KL}\big(p(y\mid x)\,\|\,p(y\mid z)\big)\big),$$
> 逐符号（nats）：$D_{KL}(p(y\mid x)\|p(y\mid z))$=把 $x$ 归到码字 $z$ 造成的**预测失真**（$z$ 越不能代表 $x$ 的预测行为、失真越大）；$Z(x,\beta)$=逐样本配分函数。**读法**：$x$ 优先分给"预测行为最像它"的码字，$\beta$ 决定这偏好有多硬——与 §2.4 的 Boltzmann 解**同构**（把"能量"换成"预测失真"）。
> **③ deterministic annealing = 沿 $\beta$ 的相变**。把 $\beta$ 视作**逆温度**：$\beta\to0$（高温）指数被抹平，所有 $x$ 塌成同一码字、$Z$ 什么也不编码（$I(Z;X)=0$）；缓慢升 $\beta$（降温），表征在一串**临界 $\beta$** 处发生"相变"——码字逐个**分裂**，先分出最能区分 $Y$ 的粗特征（钥匙 vs 非钥匙），再分细（哪把钥匙）。这条"先解糊、再逐步加清晰度"正是 [[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|Continuation / 平滑化]] 暗线在表征学习里的化身：**annealing $\beta$ ≡ 课程/同伦——先学好分的、再学难分的**，远比直接在大 $\beta$ 处硬优化（非凸、易陷坏局部极小）稳。§5.1 的 Blahut–Arimoto 正是 $\beta$ 固定时求这组自洽方程的交替迭代。

### 5.3 变分信息瓶颈 (VIB) 与应用

高维下精确算 $I$ 不可行，**VIB** 用变分界：$I(Z;X)\le\mathbb E_{p(x)}[D_{KL}(p(z\mid x)\|q(z))]$、$I(Z;Y)\ge\mathbb E[\log q(y\mid z)]+H(Y)$，得可训损失 $\mathcal L_{VIB}=\mathbb E[D_{KL}(p_\theta(z\mid x)\|q(z))]-\beta\,\mathbb E[\log q_\phi(y\mid z)]$。**当 $Y=X$ 时 VIB 退化为 $\beta$-VAE**——$\beta$-VAE 的 $\beta$ 正是 IB 的拉格朗日乘子。

```python
# 触觉 VIB 编码器：把高分辨触觉图压成任务相关 latent（保留接触/滑移，丢弃纹理噪声）
class TactileVIBEncoder(nn.Module):
    def __init__(self, beta=0.01):
        self.encoder = ResNet18()                      # 提特征
        self.fc_mu, self.fc_logvar = nn.Linear(512,32), nn.Linear(512,32)
        self.beta = beta
    def forward(self, tactile_img, contact_label):
        h = self.encoder(tactile_img)
        mu, logvar = self.fc_mu(h), self.fc_logvar(h)
        z = mu + torch.exp(0.5*logvar) * torch.randn_like(mu)        # 重参数化
        kl   = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())  # 压缩项 I(Z;X) 上界
        pred = F.cross_entropy(self.classifier(z), contact_label)        # 预测项 I(Z;Y) 下界
        return z, self.beta * kl + pred
```

> [!tip] IB 与 Empowerment 的信息论对偶（被动感知 ↔ 主动控制）
> | 原理 | 目标 | 信息流方向 | 灵巧操作意义 |
> |:--|:--|:--|:--|
> | **信息瓶颈** | min $I(Z;X)$、max $I(Z;Y)$ | 观测→表征→预测 | 高效感知压缩 |
> | **Empowerment** | max $I(A;S')$ | 动作→未来状态 | 最大化控制力 |
>
> IB 管"如何从观测提取有用信息"（被动），Empowerment 管"如何通过动作影响未来"（主动）。二者构成灵巧操作的信息论闭环——**摸钥匙时，IB 把触觉压成'是钥匙'，empowerment 驱动'把它稳稳捏住'**。

**信息平面假说**（Tishby）：深度网络训练 = 先"拟合阶段"（$I(Z;Y)$ 快增）再"压缩阶段"（$I(Z;X)$ 缓降）。虽有争议（依赖互信息估计），但核心洞见——**泛化需要压缩**——在灵巧操作得到验证：经 VIB 正则的网络 Sim-to-Real 鲁棒性更强（与 [[RepresentationLearning|表征学习的泛化理论]]呼应）。

------

## 6. 内在动机：无需外部奖励的智能

> [!tip] 本节四拍
> **直觉**（让机器人"玩"魔方，只在复原时给奖励它永远学不会——需要内在好奇心）→ **推导**（empowerment=动作与未来的互信息；变分下界）→ **对比**（ICM/VIME/Empowerment/RND/DIAYN）→ **落点**（追求"对未来的控制力"自发涌现抓取）。

许多灵巧任务外部奖励**稀疏甚至缺失**。信息论给出**内在动机**的数学形式，驱动机器人像婴儿一样自主学操作技能。

### 6.1 Empowerment：最大化对未来的控制力

**赋能**定义代理对环境的潜在控制力——当前动作 $A$ 与未来状态 $S_{t+k}$ 的互信息最大值：

$$
\mathcal E(s_t)=\max_{\pi(a\mid s_t)}I(A_t;S_{t+k}\mid s_t).
$$

把机器人看作发射机、环境看作信道、未来状态看作接收信号，empowerment = **信道容量** $C=\max_{p(a)}I(A;S'\mid s)$。物理意义：**高赋能**=稳定抓持（微小指尖动作就能精确改变物体位姿，"掌控"了物体）；**低赋能**=物体将滑落/手指卡死（无论怎么动，状态不可控）。**追求最大赋能 = 追求可操作性与稳定性**——即使不定义"抓取"为目标，仅最大化 $I(A;S)$，机器人就会自动学会抓取（抓取赋予对物体状态最大控制权）。这正是闭眼摸到钥匙后"自然捏稳并翻转"的动机。

> [!note] 把"信道容量"讲透：$\max_{p(a)}$ 为何良定义且可算（不跳步）
> 香农信道容量 $C=\max_{p(a)}I(A;S'\mid s)$ 是"这条'动作→未来状态'信道**每步最多能可靠传多少控制信息**"（单位 bits/step，取 $\ln$ 则 nats/step）。三点让它可算、可解释：
> **① 上确界一定取得到**：$I(A;S')$ 作为**输入分布 $p(a)$ 的函数是凹的**（互信息对输入分布凹、对信道 $p(s'\mid a)$ 凸），而 $p(a)$ 落在概率单纯形（紧凸集）上——紧集上的凹函数必达最大。故 $\max$ 良定义，empowerment 是个良定义的标量场 $\mathcal E(s)$，可当势能函数来爬。
> **② 怎么解——Blahut–Arimoto**：与 §5.1 率失真同一台交替迭代机（率失真是它对偶）。固定信道，交替更新输入分布 $p(a)$ 与后验 $p(a\mid s')$，单调收敛到容量；每步闭式、无需梯度，正适合 empowerment"每个状态 $s$ 上都要算一次容量"的场景。
> **③ 物理直觉——注水 (water-filling)**：最优 $p(a)$ 把"动作预算"注到**最能改变未来、且改变可被区分**的动作维度上（类比频域注水把功率注到高信噪比子信道）。灵巧手上：稳定抓持时指尖微动即可精确、可区分地改变物体位姿→高容量；将滑落时动作与结果的关系混乱不可区分→容量塌陷。**empowerment 高 = 这条动作信道没被浪费。** 与 §5.3 "IB 管源压缩、empowerment 管控制信道"合起来，整套灵巧操作嵌进一张"感知信道 + 控制信道"的通信图。

> [!important] 跨原理联系：Empowerment ↔ 可控性 Gramian
> 对确定性线性系统 $s'=As+Ba$，empowerment 与控制论的**可控性 Gramian** 行列式成正比：$\mathcal E(s)\propto\log\det(BB^T)$。**高 empowerment = 高可控性**——这在信息论与经典控制论（[[ControlTheory#10. 稳定性理论的统一基石|稳定性/可控性]]）之间架了一座精确的桥。稳定抓取=完全可控、物体滑落边缘=丧失可控、手指卡死=约束致奇异。

**变分下界与实现**：精确算 $I(A;S')$ 不可行（要边缘化出 $s'$ 上的真后验 $p(a\mid s')$），用 Barber–Agakov / Blahut–Arimoto 风格变分下界。

> [!note] 变分下界逐步推导（不跳步）
> 从 §2.2 的对称展开取 $I(A;S'\mid s)=H(A\mid s)-H(A\mid S',s)$。第二项按条件熵定义 $H(A\mid S',s)=-\mathbb E_{a,s'}[\log p(a\mid s')]$，其中 $p(a\mid s')$ 是"看到结果 $s'$ 反推是哪个动作"的**真后验（逆模型）**，一般算不出。引入任意变分分布 $\omega(a\mid s')$ 顶替，关键一步是**非负的 KL 差**（Gibbs 不等式，见 §2.2③）：
> $$\mathbb E_{s'}\big[D_{KL}(p(a\mid s')\,\|\,\omega(a\mid s'))\big]\ge0\ \Longrightarrow\ \mathbb E_{a,s'}[\log p(a\mid s')]\ \ge\ \mathbb E_{a,s'}[\log\omega(a\mid s')].$$
> 代回即得下界
> $$I(A;S'\mid s)\ \ge\ \underbrace{H(A\mid s)}_{\text{动作要够丰富}}+\underbrace{\mathbb E_{a\sim\pi(\cdot\mid s),\,s'\sim p(\cdot\mid s,a)}[\log\omega(a\mid s')]}_{\text{结果要能反推动作}},$$
> 当 $\omega=p$（逆模型完美）时取等——界紧。符号：$H(A\mid s)$=策略在状态 $s$ 的动作熵（鼓励多样尝试，单位 nats）；$\omega(a\mid s')$="规划/逆模型"分布，从达成的未来 $s'$ 反推"是哪个 $a$ 干成的"。

深度实现：源/策略网络 $\pi_\theta(a\mid s)$ + 逆模型 $\omega_\phi(a\mid s')$，目标 $\max_{\theta,\phi}\mathbb E[\log\omega_\phi(a\mid s')-\log\pi_\theta(a\mid s)]$（正是上界两项）。直觉：**只有"不常见（$-\log\pi$ 大）、却精准导致特定结果（$\log\omega$ 大、$s'$ 可从 $a$ 反推）"的动作获高赋能**——这导致机器人学精细指尖调整而非随机大挥动。这台"无奖励也能长出抓取"的引擎，正是 [[ReinforcementLearning#7. 探索：稀疏奖励下，如何"撞见"转笔成功|RL 稀疏奖励下技能发现探索]] 的信息论内核。

### 6.2 内在动机的谱系：好奇心、惊奇、赋能、多样性

| 方法 | 核心机制 | 物理驱动力 | 优缺点 |
|:--|:--|:--|:--|
| **ICM** | 预测误差 $\|\hat s'-s'\|$ | 找预测失败处 | **噪声电视机问题**（无法预测随机噪声→对着噪声发呆，正是 §1.2 错把 aleatoric 当探索目标） |
| **VIME** | 贝叶斯惊奇 $D_{KL}(p(\theta\mid\xi_{1:t})\|p(\theta\mid\xi_{1:t-1}))$ | 找能改善模型参数处 | 理论严谨，但贝叶斯网络训练复杂 |
| **Empowerment** | 互信息 $I(A;S')$ | 找最大化控制权处 | 计算昂贵，但行为最自然 |
| **RND** | 随机网络蒸馏误差 | 找没访问过的状态 | 实现简单，但不理解物理 |

**VIME** 把内在奖励定义为动力学模型后验的 KL 跳变——**新转换让模型参数大更新（学到新知识）就给高奖励**。这驱动机器人去推不同重量物体、探摩擦边界（最能修正动力学的地方）——**这解释了婴儿为何爱扔东西：他们在校准物理模型**。

### 6.3 DIAYN：多样性就是一切

DIAYN 无监督学多样技能，最大化状态 $S$ 与技能 ID $Z$ 的互信息：$\text{目标}=I(S;Z)+H(A\mid S)$。无任何外部奖励下，灵巧手自发涌现推/滚/抓等原语。**鉴别器** $q_\phi(z\mid s)$ 试图从状态猜当前技能——猜得越准，技能可辨识性越高；熵项 $H(A\mid S)$ 鼓励动作随机（防策略坍缩）。

```python
# DIAYN 内在奖励：r = log q(z|s) - log p(z)，奖励"可辨识的技能"
def compute_diayn_rewards(discriminator, states, skills, num_skills):
    log_q = F.log_softmax(discriminator(states), dim=1)          # 鉴别器 q(z|s)
    log_q_z = log_q.gather(1, skills.unsqueeze(1)).squeeze(1)     # 当前技能的对数概率
    log_p_z = np.log(1.0 / num_skills)                           # 先验 p(z) 均匀
    return log_q_z - log_p_z                                     # 越可辨识，奖励越高
```

> [!tip] DIAYN = 离散化的 Empowerment
> DIAYN 里 $z\in\{1,\dots,K\}$ 是离散技能、鉴别器 $q(z\mid s)$ 正是 empowerment 变分界里 $\omega(a\mid s')$ 的离散版。最大化 $I(Z;S)$ 等价于在离散技能空间最大化赋能。这条把 §6.1 与 §6.3 缝在一起，也接上 [[ReinforcementLearning#7. 探索：稀疏奖励下，如何"撞见"转笔成功|RL 的技能发现探索]]——**信息论的 empowerment/DIAYN 就是 RL 无奖励探索的数学引擎**。

------

## 7. 现实挑战：软体与 Sim-to-Real

> [!tip] 本节四拍
> **直觉**（理论优美，但真机的软体形变与摩擦含大量刚体仿真丢失的信息）→ **推导**（现实鸿沟=信息损失；软体触觉的高维与迟滞）→ **对比**（DR 稀释信息 vs 信息论自适应主动缩不确定）→ **落点**（stick-slip 临界点是信息增益最高的时刻）。

### 7.1 现实鸿沟作为信息损失

把 Sim-to-Real 形式化为 $P_{sim}$ 与 $P_{real}$ 的 KL 最小化。**域随机化 (DR)** 靠增大 $P_{sim}$ 的熵（加噪）去覆盖 $P_{real}$——本质是在**稀释信息**，致策略保守。**信息论自适应**则取攻势：部署时用实时数据**在线最小化不确定性**——先用探索策略（不为完成任务、只为高效收数据）做"摩擦测试"，迅速把 $\mu$ 的不确定从 $[0.1,1.0]$ 缩到 $[0.4,0.5]$，再执行任务（这与 [[StochasticProcess#5. 学习未知动力学：高斯过程与残差学习|在线 SysID]]、[[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|RMA]] 同思想）。

### 7.2 软体触觉的特殊挑战

VTS（GelSight/TacTip）引入软体接触，带来新信息论问题：① **高维**——直接算 $H(\text{Image})$ 无意义（像素熵由噪声主导），须用 VAE 映到低维 latent，主动探索变为在 latent 空间最大化信息增益 $H(X_{contact})\approx H(z_{latent})$；② **迟滞**——软体接触有记忆，当前信息状态依赖历史形变路径，违反马尔可夫，须用 RNN/Transformer 构非马尔可夫信息状态（呼应 [[SignalProcessing#2.2 迟滞：Prandtl–Ishlinskii 模型与逆补偿|PI 迟滞]]、[[StochasticProcess#2.3 马尔可夫性：它如何在推冰球里被破坏，又如何被"信念"救回|非马尔可夫]]）。

### 7.3 摩擦与滑动的信息内容：钥匙打滑的那一刻

> [!important] Slip Onset = 信息增益最高的相变点
> 摩擦不只是阻力，更是**信息的载体**。指尖滑过表面产生的 **stick-slip 振动**蕴含纹理与摩擦系数的高频信息；而从静摩擦到动摩擦的转变点（**slip onset**）是状态突变（相变），**信息增益最高**。优秀策略会故意让手指处于**微滑移 (incipient slip) 边缘**，以维持对摩擦状态的最高敏感度——一种"混沌边缘"控制。这把信息论、非线性动力学与 [[SignalProcessing#4.1 早期滑移 (Incipient Slip) 检测|滑移检测]] 深度融合：**钥匙快滑落的那一刻，既是危险，也是关于"它有多滑"的最大信息来源。**

------

## 8. 知识回扣与记忆图：一把钥匙串起信息论六层

> [!abstract] 用一条故事线把全讲复述一遍（刻意复述，为了记忆）
> 我们闭眼在口袋里摸钥匙。**(§1)** 单次静态触摸不够，必须主动序列化地"询问"——感知被重构为信息获取，且只对 epistemic 不确定性（没摸过的部位）探索，别对噪声发呆。**(§2)** 用熵度量"是什么"的无知、用互信息度量每一摸的切割力、用 KL 度量摸到意外时的惊奇。**(§3)** 用 GPIS 在已摸点间脑补整个形状、用轮廓信息增益把下一摸钉在表面边缘（NBT）。**(§4)** 不是单点贪心，而在信念空间规划一连串触摸；不确定时手变软扫掠、确定后变硬捏取（双重控制）。**(§5)** 把百万像素的触觉流用信息瓶颈压成"是钥匙"几个 bit——且压缩本身就在去噪。**(§6)** 摸到后稳稳捏住、能随意翻转，这种"对未来的控制力"就是 empowerment；无奖励时它能自发涌现抓取，DIAYN 还能发现推/滚/捏等触摸原语。**(§7)** 上真机时，钥匙快滑落的那一刻既最危险、又含最大信息。**一把钥匙，摸完了整座信息论大厦。**

> [!important] 一张表记住全篇（层 → 问题 → 工具 → 摸钥匙角色）
> | 层 | 核心问题 | 关键工具 | 摸钥匙的哪一环 |
> |:--|:--|:--|:--|
> | §2 度量 | 如何量化无知 | 熵、互信息、KL | 摸前的不确定 |
> | §3 概率建模 | 怎么用触摸更新 | GPIS、采集函数 | 脑补形状、定下一摸 |
> | §4 主动规划 | 下一连串摸哪 | 信念空间、EIG、双重控制 | 序列触摸、软硬切换 |
> | §5 表征 | 留什么信息 | 信息瓶颈、率失真、VIB | 压成"是钥匙" |
> | §6 内在动机 | 无奖励学什么 | empowerment、DIAYN | 稳稳捏住、发现原语 |
> | §7 现实 | 软体/真机 | 信息论自适应、stick-slip | 钥匙打滑那一刻 |

> [!tip] 三条贯穿全讲的"暗线"（抓住它们，细节自来）
> 1. **熵/互信息/KL 是三原色**：所有目标（EIG、IB、empowerment、VIME 惊奇）都是这三者的调色（§2）。
> 2. **被动压缩 ↔ 主动控制的对偶**：信息瓶颈 max $I(Z;Y)$/min $I(Z;X)$（被动），empowerment max $I(A;S')$（主动）——同一信息论闭环的两端（§5.3）。
> 3. **熵→刚度的物理桥**：高熵→低刚度→探索，低熵→高刚度→执行（§4.3）——把信息论、[[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|阻抗控制]]、[[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|SAC 熵即柔顺]]统一；而 empowerment↔可控性 Gramian（§6.1）把这座桥钉死在控制论上。

> [!note] 跨领域链接（双向、点对点）
> - **↔ [[ReinforcementLearning]]**：内在动机/empowerment/DIAYN=无奖励探索引擎（§6）；最大熵 = KL-到-均匀（§2.3）；好奇心内在奖励。
> - **↔ [[StochasticProcess]]**：belief/PF/RBPF 是信息度量的载体（§4）；aleatoric/epistemic（§1.2）；信念空间规划（§4）。
> - **↔ [[SignalProcessing]]**：触觉流的序列获取；压缩=去噪（§5.1）；滑移检测=最大信息时刻（§7.3）；迟滞=非马尔可夫（§7.2）。
> - **↔ [[RepresentationLearning]]**：信息瓶颈=最优表征压缩（§5）；VIB↔β-VAE；泛化需要压缩。
> - **↔ [[ControlTheory]]**：empowerment↔可控性 Gramian（§6.1）；双重控制（§4.3）；熵→刚度。
> - **↔ [[ComputationalGeometry]]**：GPIS 的 SDF 隐式曲面（§3.1）。
> - **↔ [[Optimization]]**：率失真/IB 是约束优化；采集函数=贝叶斯优化（§3.2）。

------

## 9. 结论与展望

1. **主动性是根本**：不确定性主导的环境里，被动静态感知是死路。机器人必须以 NBT/信念空间规划、用物理交互主动重塑信念分布。
2. **熵的物理对应**：熵 = 接触空间可行域体积；操作本质是把这一体积压缩到满足任务约束（如力闭合）。
3. **双重控制的统一**：控制不只是执行，也是感知；刚度调节是信念不确定性在力学层的直接投射（§4.3）。
4. **内在动机的潜力**：empowerment 证明，即使无具体任务，追求"对未来的控制力"也能自发产生稳定抓取——为通用机器人预训练提供理论基础（§6）。

> [!important] 一句话钥匙
> 信息论教给灵巧操作的，是把"感知"从被动接收升级为主动获取，把"不确定性"从敌人变成导航的势能场。叠上"熵/互信息/KL 三原色"与"empowerment↔可控性、熵↔刚度"两座桥，信息论、随机过程、控制、RL、表征在你眼里就连成一张图——而那把口袋里的钥匙，就是这张图的试金石。未来方向：高频触觉流的实时互信息估计，以及把**因果推断**引入主动探索，使机器人不仅知"是什么"（关联），更懂"为什么"（因果），迈向认知灵巧操作。

------

## 10. 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文涉及本 Foundation 的信息论概念。

### 熵与探索策略
- [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration|DemoSpeedup]]：熵引导示教加速
- [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach|Exploration vs Exploitation]]：信息论视角的探索-利用
- [[EUREKA: Human-Level Reward Design via Coding Large Language Models|EUREKA]]：LLM 引导的奖励信息编码

### 互信息与表示学习
- [[Weight-sparse transformers have interpretable circuits|Weight-sparse Transformers]]：信息瓶颈与稀疏表示
- [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing|Robot Synesthesia]]：跨模态信息融合

### 主动感知与信念更新
- [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation|Curriculum Sensing Reduction]]：传感信息的课程式简化
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]]：触觉信息的 Sim-to-Real 对齐

### 项目级真机信息利用 Idea（WMTS）
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-005-Saturation-Boundary-Active-Learning|SBAL]]：基于执行器饱和与触觉边界的信息增益主动采集
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-010-EBM-Mode-Mismatch|EBM Mode-Mismatch]]：能量模型刻画 sim 分布支撑，OOD 检测真机分布漂移
