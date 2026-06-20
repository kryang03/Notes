---
tags:
  - foundation
  - signal-processing
  - tactile-sensing
  - state-estimation
aliases:
  - 信号处理
  - 触觉感知
  - GelSight
  - 卡尔曼滤波
  - 状态估计
  - 傅里叶变换
  - Fourier Transform
  - 短时傅里叶变换
  - STFT
  - 小波变换
  - Wavelet Transform
  - Kalman Filter
  - Extended Kalman Filter
created: 2026-01-31
related:
  - "[[ControlTheory]]"
  - "[[StochasticProcess]]"
  - "[[RepresentationLearning]]"
  - "[[ContactMechanics]]"
  - "[[InformationTheory]]"
---

# 触觉信号处理与状态估计：从传感器波形到闭环状态

# Tactile Signal Processing & State Estimation: From Sensor Waveform to Closed-Loop State

> [!tip] 相关领域
> - [[ControlTheory]] — 频率响应/采样延迟是同一套语言；触觉反馈进闭环
> - [[StochasticProcess]] — 贝叶斯滤波 (KF/EKF/UKF/PF) 是状态估计的共同母体
> - [[RepresentationLearning]] — 触觉表征学习与多模态融合；学出来的观测模型
> - [[ContactMechanics]] — 触觉信号的物理来源（接触力、摩擦、滑移）
> - [[InformationTheory]] — "下一步采哪条流、保留哪些信息"；率失真=压缩-去噪对偶
>
> **贯穿母题（本讲的"主角"）**：**判断手中的杯子是否开始打滑 (detect incipient slip)**。一个"杯子要掉了吗"的判断，把信号处理从转导、采样、频域、时频、到状态估计每一层都点亮——我们让它贯穿全篇。
>
> **相关项目**: [[Dynamic Non-Prehensile Manipulation]] — 动态操作中的触觉感知

## 0. 母题与理论大厦构建路线：从传感器波形到闭环状态

> [!abstract] 为什么用"判断杯子是否打滑"做贯穿母题？
> 信号处理 Foundation 的主线，是把物理接触界面的连续变化，变成**控制器可用、带不确定性、带时间戳**的状态估计。**"杯子要打滑了吗"** 这一个判断，恰好逐层激活：
> - 杯子打滑时指尖的**微振动** → 怎么转成电信号（转导）、采样率够不够（Nyquist）；
> - 这振动是真滑移还是电噪声 → 频域/PSD 区分；
> - 滑移是**某一瞬间**突然开始的 → 时频分析（STFT/小波）抓瞬态；
> - "到底滑了没、滑了多少" → 从局部触觉**估计**不可见的接触状态；
> - 判断结果要**及时**进控制器加紧 → 滤波延迟必须低于稳定裕度。
>
> 全讲每引入一个工具，我们都回到这只杯子："**它帮我们更早、更准地判断打滑了吗？它引入的延迟会不会让杯子先掉了？**"

| 层级 | 核心问题 | 工具 | 打滑母题的映射 | 讲稿位置 |
|:--|:--|:--|:--|:--|
| **转导层** | 物理量如何变电信号/图像？ | 电容、光度立体、MEMS、GelSight | 传感器非线性决定"微振动"可信度 | §2、§3 |
| **采样层** | 连续信号如何离散记录？ | Nyquist、ZOH、抗混叠 | 采样不足会把高频滑移折叠成假漂移 | §1 |
| **频域层** | 噪声和事件在哪些频带？ | Fourier、PSD、notch、band-pass | 区分电噪声/机械振动/真 stick-slip | §1、§4 |
| **时频层** | 瞬态事件何时发生？ | STFT、wavelet、谱质心 | 早期滑移是短时高频事件 | §1、§4 |
| **滤波/估计层** | 如何估不可见状态？ | KF/EKF/UKF/PF、因子图 | 从局部触觉恢复位姿、接触模式、摩擦 | §5 |
| **控制接口层** | 估计如何进闭环？ | 延迟补偿、置信度、异常检测 | 估计须带时间戳与不确定性，不只一个数 | §1、§7 |

> [!important] Foundation 级判断标准（任何信号方法进入本库都要回答四问）
> 1. **信号源的物理病态是什么**（非线性、迟滞、漂移、混叠）？不先建模病态，后续估计都建在沙堆上。
> 2. **时间还是频率**（稳态频带用 PSD/STFT，未知时刻的瞬态用小波）？
> 3. **引入多少延迟**（因果滤波必然滞后；延迟是否低于 [[ControlTheory|控制]] 的相位裕度上限）？
> 4. **输出带不带不确定性**（一个数 vs 均值+协方差）？下游 [[StochasticProcess|滤波]]/[[ReinforcementLearning|RL]] 需要后者。

> [!note] 本讲在知识图谱中的位置（依赖 / 被依赖）
> ```
> [[ContactMechanics]] ─力/滑移物理源─┐                  ┌── 带不确定性的状态 ──> [[StochasticProcess]]/[[ReinforcementLearning]]
>                                  ├──> 【SignalProcessing】 │
>     采样/频率响应 <──> [[ControlTheory]]                  └── 触觉 latent ──> [[RepresentationLearning]]
>                                  │
>                  "采哪条流、留哪些信息" <──> [[InformationTheory]]
> ```
> 读法：接触力学提供信号的物理来源，控制论与之共享采样/频率响应语言；信号处理的产出（带不确定性的状态、触觉 latent）喂给随机过程/RL/表征；信息论决定"该采什么、留什么"。

> [!tip] 与 [[InformationTheory]] 的边界
> SignalProcessing 负责"这条传感流如何变成可靠状态"；InformationTheory 负责"下一步该采哪条流、哪些信息值得保留"。前者是被动的最优重构，后者是主动的最优获取。

## 1. 从波形到状态：信号处理的系统骨架

> [!tip] 本节四拍
> **直觉**（判断打滑需要一整条流水线：采得到→看得清频带→定位到瞬间→估出状态）→ **推导**（采样/Nyquist→Fourier→STFT/小波→数字滤波→贝叶斯估计）→ **对比**（STFT 固定窗 vs 小波多尺度；因果滤波的去噪-延迟权衡）→ **联系**（卷积定理 ↔ [[ControlTheory|频率响应]]；贝叶斯递推 ↔ [[StochasticProcess|滤波]]）。

灵巧操作的核心矛盾已从"机械设计"转移到**感知与认知的鸿沟**：如何从高维、嘈杂、非线性的触觉原始数据里实时提取接触状态、物体位姿与物理属性。触觉与视觉不同——它**局部、交互、直接**，是主动探索的结果。综述把触觉用法分三层：**门控信号**（用力的不连续触发状态机相位）→ **几何推理**（用高密度触觉重建接触微观形貌）→ **力主导控制**（完全靠力/触觉闭环）。支撑这三层的，是下面这条从波形到状态的流水线。

### 1.1 采样与混叠：离散化不是无损记录

机器人里的"信号"可以是电机电流、关节角、IMU 角速度、指尖法向力、GelSight 亮度、触觉阵列压力、策略动作。采样频率 $f_s=1/T_s$ 必须满足 **Nyquist 条件** $f_s>2f_{\max}$。

> [!warning] 打滑母题里的混叠陷阱
> 若滑移微振动含 $f_{\max}=300\,$Hz 的有效能量，而记录只有 $200\,$Hz，高频会**折叠 (alias)** 到低频，被误读成慢漂移或低频振荡——**你会以为杯子在缓慢下沉，其实它在高频抖动、马上要滑脱**。对策：① 采样前用**抗混叠模拟低通**切掉 $f_s/2$ 以上；② **零阶保持 (ZOH)** 等价于给闭环引入相位滞后（这就是信号处理与 [[ControlTheory#1.3 频率响应：Bode、相位裕度与带宽|控制延迟]] 的接口）；③ **多速率**：触觉/电流高频采、视觉低频更新，在控制器同步融合。

> [!tip] 采样率不是越高越好，要匹配任务带宽
> 准静态装配可低频；stick-slip、碰撞、转笔 snap 需高频；惯性飞行段可降频。这正是 [[TARC - Time-Adaptive Robotic Control]]、[[Elastic Time Step Reinforcement Learning, VTS-RL|VTS-RL]] 背后的信号处理约束，也呼应 [[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|RL 的控制频率自适应]]。

### 1.2 傅里叶变换：把波形拆成频率模式

连续时间傅里叶变换 (CTFT)：

$$
X(\omega)=\int_{-\infty}^{\infty}x(t)e^{-j\omega t}\,dt.
$$

它回答："信号里哪些频率模式在贡献能量？" 三个读法：幅值谱 $|X(\omega)|$（哪些振动最强）、相位谱 $\angle X(\omega)$（滞后多少）、能量谱 $|X(\omega)|^2$（噪声/滑移/共振的能量分布）。

> [!important] 卷积定理：滤波=频域相乘（与控制论同语言）
> $$(x*h)(t)\ \Longleftrightarrow\ X(\omega)H(\omega).$$
> 时域用滤波器 $h$ 平滑触觉，等价于频域乘以频率响应 $H(\omega)$——**这与 [[ControlTheory#1.3 频率响应：Bode、相位裕度与带宽|控制系统频率响应]] 是同一套语言**：信号处理看"噪声如何被削弱"，控制看"闭环如何放大/抑制扰动"。离散版 DFT $X[m]=\sum_k x[k]e^{-j2\pi mk/N}$；**FFT 不是新变换，而是 DFT 的 $O(N\log N)$ 快速算法**，工程上用来找电机/减速器共振、判断触觉是否出现滑移高频能量、辅助选 $K_p,K_d$ 或 notch。

### 1.3 STFT 与小波：非平稳信号的时频显微镜

普通傅里叶假设频率成分不随时间变。但灵巧操作信号高度**非平稳**——接触、滑移、撞击、脱离都是瞬态。需时频分析。

**短时傅里叶 (STFT)** 对滑动窗口做傅里叶：$X(\tau,\omega)=\int x(t)w(t-\tau)e^{-j\omega t}dt$。窗短则时间定位准但频率分辨差，窗长则反之——这是**时频不确定性原理**的工程体现。

**小波 (CWT)** 用可伸缩平移的母小波：$W_x(a,b)=\frac1{\sqrt a}\int x(t)\psi^*(\frac{t-b}a)dt$。尺度 $a$ 大看低频慢变、$a$ 小看高频瞬态——天然"低频看趋势、高频抓突变"。**DWT** 递归分解为近似系数 $A_L$ + 各尺度细节 $D_i$；滑移检测监测某 $D_i$ 的能量突增 $E_i[t]=\sum_{k}D_i[k]^2$。

> [!important] STFT vs 小波选型（打滑判断的关键抉择）
> - 监测**已知频带**（电机齿槽、结构共振）→ STFT/PSD；
> - 捕捉**未知时刻的短促冲击**（滑移起点、接触切换）→ DWT/CWT；
> - 结果进实时闭环 → 窗口长度/小波层级带来的延迟必须计入 [[ControlTheory|控制]] 的相位裕度。**判断打滑的本质是"在杯子掉之前，用尽量短的窗口抓到那个高频瞬态"——这就是时频不确定性原理与控制延迟的双重夹击。**

### 1.4 数字滤波器：去噪、延迟与可控性的三角权衡

| 滤波器 | 作用 | 打滑/灵巧操作例子 | 风险 |
|:--|:--|:--|:--|
| Low-pass | 去高频噪声 | 平滑力读数 | 过度平滑会**延迟**接触/滑移检测 |
| High-pass | 保留突变 | 滑移微振动检测 | 放大电子噪声 |
| Band-pass | 只留目标频带 | 齿啮/滑移频带 | 需先验频带 |
| Notch | 抑窄带共振 | 电机/结构共振点 | 误设会削弱真接触信号 |
| MA / EMA | 轻量实时平滑 | RL observation 预处理 | 引入群延迟 |

> [!warning] 因果滤波必然滞后
> 因果滤波器只用当前+过去数据，**一定引入延迟**；离线零相位滤波（forward-backward）能去相位滞后但**不可用于实时**。触觉闭环里最重要的不是"滤得多干净"，而是**滤波延迟是否低于控制稳定裕度的上限**——滤得太干净却太慢，杯子已经掉了。

### 1.5 状态估计：从滤波波形到估计不可见状态

滤波处理观测 $z_t$；**状态估计器要反推不可直接观测的 $x_t$**（物体位姿、接触点、摩擦系数、执行器温度隐变量）。标准贝叶斯递推两步：

$$
\underbrace{p(x_t\mid z_{1:t-1})}_{\text{预测}}=\int p(x_t\mid x_{t-1},u_{t-1})\,p(x_{t-1}\mid z_{1:t-1})\,dx_{t-1},\qquad
\underbrace{p(x_t\mid z_{1:t})}_{\text{更新}}\propto p(z_t\mid x_t)\,p(x_t\mid z_{1:t-1}).
$$

> [!note] 跨原理联系：这两步是整个 [[StochasticProcess#4. 信念更新：从 EKF 失效到粒子滤波|随机过程信念更新]] 的心脏
> KF、EKF、UKF、PF、因子图都是这两步的不同近似（§5 详述）。**信号处理用它从触觉估状态、随机过程用它做接触定位、RL 用它当 belief 编码器——同一个贝叶斯递推，三处现身。** 这是"判断打滑"从波形上升到"杯子状态"的桥。

------

## 2. 转导物理与信号病态：一切估计的地基

> [!tip] 本节四拍
> **直觉**（判断打滑前，先问：传感器读数本身可信吗？）→ **推导**（电容的超弹性+边缘场非线性、粘弹性迟滞、MEMS 噪声谱）→ **对比**（电容皮肤 vs MEMS 气压阵列）→ **落点**（不先建模信号病态，后续状态估计都建在沙堆上）。

一切信号处理的前提，是对信号源物理特性的深刻理解。触觉传感器本质是把机械应力转成电信号的换能器，但这一转换**绝非线性**，充满噪声、迟滞与漂移。

### 2.1 电容式触觉：超弹性与边缘场的非线性纠缠

电容皮肤 (E-Skin) 灵敏柔顺，但教科书的 $C=\varepsilon A/d$ 在此**完全失效**：弹性体基底是**不可压缩非线性超弹性**材料，须用 **Mooney–Rivlin 应变能函数**描述大变形；受压时泊松效应使横向膨胀，电极重叠面积 $A$ 与间距 $d$ 复杂耦合。电学上还有**边缘场效应**致饱和，改进模型引入经验幂律：

$$
\Delta C=C-C_0=q\Big(\frac U{D_e}\Big)^{\gamma}
$$

（$U$ 顶层形变位移、$D_e$ 初始电极间距、$q,\gamma$ 拟合参数）。**含义**：$\Delta C$ 与形变是**幂律而非线性**关系，信号调理电路必须含基于此的**逆映射**才能把原始电容线性化为力。

### 2.2 迟滞：Prandtl–Ishlinskii 模型与逆补偿

迟滞是软触觉的顽疾——粘弹性使输出不仅取决于当前输入，**还取决于加载历史路径**（这正是 [[StochasticProcess#2.3 马尔可夫性：它如何在推冰球里被破坏，又如何被"信念"救回|随机过程里破坏马尔可夫性的隐变量]]）。未补偿的迟滞致力控稳态误差甚至震荡。**PI 模型**把迟滞环分解为一系列 Play/Stop 算子的加权叠加；其**逆模型有解析解**，故可级联一个逆 PI 滤波器**实时抵消**迟滞、恢复线性输入输出。资源受限时也可用多项式拟合（精度逊于 PI）。

### 2.3 MEMS 气压阵列：用 PSD 分析噪声谱

MEMS 气压触觉线性度高（<1%）、噪声低（<0.01N）。表征其噪声的金标准是**功率谱密度 (PSD)**：

$$
S_x(f)=\lim_{T\to\infty}\frac1T\mathbb E\big[|X_T(f)|^2\big].
$$

PSD 能分离两类噪声：**白噪声**（全频段均匀，热噪声）与 **1/f 闪烁噪声**（低频主导，零点漂移之源）。据此设计最优数字滤波或自适应陷波，在**保留滑移高频瞬态**的同时压制低频漂移与宽带噪声——这是高信噪比触觉系统的频域基础。

> [!note] 三种转导方式对打滑判断的影响
> 电容皮肤：覆盖广但迟滞重，**滑移微振动易被迟滞伪影淹没**；MEMS 阵列：线性低噪，**最适合抓滑移高频**；VTS（§3）：高分辨几何，**用标记点散度直接看滑移**。选传感器，本质是选"打滑信号能否干净地浮出噪声底"。

------

## 3. 视觉触觉传感 (VTS)：把触觉变成视觉问题

> [!tip] 本节四拍
> **直觉**（用摄像头看弹性膜的形变，把"摸"变成"看"）→ **推导**（光度立体逆光学 → 泊松重建几何；逆力学求力场）→ **对比**（GelSight 局部 vs Punyo 气泡全局 FEM）→ **联系**（泊松快速解 ↔ [[ComputationalGeometry|几何]]；L1 稀疏力 ↔ [[Optimization#2.1 凸集与凸函数：为什么"凸"是分水岭|凸优化]]）。

GelSight/GelSlim/Soft-Bubble/Punyo 把触觉变成计算机视觉问题，核心是解两个逆问题：**逆光学**（图像→几何）与**逆力学**（形变→力）。

### 3.1 光度立体：从光影到微米形貌

假设涂层朗伯反射，像素强度 $I=\rho(\mathbf L\cdot\mathbf n)$。用多色 LED（红绿蓝）从不同方位照射，单帧 RGB 三通道编码三种光照下的亮度，解线性方程组逐像素估表面梯度 $(p,q)=(\partial z/\partial x,\partial z/\partial y)$。

**从梯度重建高度图** $z(x,y)$ 等价于解**泊松方程** $\nabla^2z=\partial_xp+\partial_yq$。迭代解（Jacobi/SOR）太慢，标准做法是基于**离散正弦变换 (DST)** 的快速泊松求解器，把空间微分变频域乘法、复杂度 $O(N^2)\to O(N\log N)$。最新还有**可微泊松重建**层，端到端嵌进网络、直接优化下游位姿损失。

### 3.2 逆力学：从形变场到力矢量场

几何只给形状，要力须结合弹性模型。

- **标记点追踪 + 光流**（Lucas-Kanade/Farneback）测位移场：法向力 ∝ 标记点扩散/深度积分；切向力由横向位移矢量定；**滑移检测靠分析位移场的局部散度或非仿射分量**——这正是"判断杯子打滑"在 VTS 上最直接的兑现：杯子开始滑，标记点出现非仿射"流动"。
- **气泡膜 (Punyo/Soft-Bubble)** 形变全局，须 **FEM** 建模。Punyo 把力估计建成平面应力问题：视觉追踪得节点位移 $\mathbf u$，解逆问题求节点力 $\mathbf f$；为治病态、强制接触稀疏，加 **L1 正则**：

$$
\min_{\mathbf f}\ \|\mathbf K\mathbf u-\mathbf f\|_2^2+\lambda\|\mathbf f\|_1.
$$

这是标准凸优化（CVXPY 可解，见 [[Optimization#2.3 KKT 条件：约束最优的"语法"|KKT]]）；基于物理模型只需标定少量参数（如杨氏模量 $E$），泛化强于纯数据驱动。

------

## 4. 时序处理：滑移检测与在线摩擦估计【母题核心】

> [!tip] 本节四拍
> **直觉**（杯子打滑前，接触边缘已在微观滑动、中心仍粘滞——产生高频微振动）→ **推导**（STFT 谱质心 / 小波能量抓瞬态；RLS 在线估 $\mu$）→ **对比**（阈值法 vs STFT vs 小波 vs ConvLSTM）→ **落点**（检测到滑移→控制器加紧/降速/切柔顺，构成触觉反射）。

灵巧操作不止静态接触，更在动态稳定。**滑移是失败的前兆**，**摩擦系数 $\mu$ 是抓力规划的关键环境参数**。二者的实时估计，是触觉时域处理最难的任务，也是"判断杯子是否打滑"的正面战场。

### 4.1 早期滑移 (Incipient Slip) 检测

早期滑移：接触面**边缘**开始微观相对运动、**中心仍粘滞**，信号特征是高频微振动。三条技术路线：

**(a) STFT + 谱质心**：滑移时频谱能量向高频转移。**谱质心**（频谱重心）

$$
\text{Centroid}[t]=\frac{\sum_k S[k,t]\,f[k]}{\sum_k S[k,t]}
$$

突然升高 + 能量激增 → 判定滑移。窗口长度须由物理时间尺度定：太长则滑移起点被平均掉、太短则频率分辨不足、分不清滑移与电噪。

**(b) 小波**：STFT 受测不准原理限，小波多尺度更善抓**滑移起始瞬间的奇异点**。流水线：DWT → 选滑移频带层 $D_i$ → 滑窗能量 $E_i[t]=\sum D_i[k]^2$ → 超自适应阈值且持续若干采样点则判滑移。**关键优势：把"突变"与"慢漂移"分开**——温漂/慢加载进低频近似 $A_L$，滑移/碰撞进高频细节 $D_i$，尤其适合迟滞重的软触觉。

**(c) ConvLSTM**：阵列传感器的滑移既是时间序列也是空间模式演变。ConvLSTM = CNN 空间特征 + LSTM 时序记忆，输入连续触觉图像帧，输出滑移方向/类型（平移 vs 旋转），准确率 >80%。

> [!tip] 与控制闭环的接口（判断之后做什么）
> 检测到滑移，控制器通常不是直接"停"，而是**提高法向力、降低切向速度、切到更柔顺的 [[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|阻抗控制]]、或触发 stick-slip 模态策略**（见 [[ControlTheory#7.3 滑移检测与闭环防滑|控制论的闭环防滑]]）。**这就是 §0 那句"检测延迟必须低于稳定裕度"的落点——晚一拍，杯子就掉了。**

### 4.2 RLS 在线摩擦估计

$\mu$ 随材质、清洁度、压力时变，须在线估。临界滑动时 $F_t=\mu F_n$，定义观测 $y(t)=\phi^T(t)\theta(t)+e(t)$（$y=F_t$、$\phi=F_n$、$\theta=\mu$）。**递归最小二乘 (RLS)** 迭代：

$$
K_k=\frac{P_{k-1}\phi_k}{\lambda+\phi_k^TP_{k-1}\phi_k},\quad
\hat\theta_k=\hat\theta_{k-1}+K_k(y_k-\phi_k^T\hat\theta_{k-1}),\quad
P_k=\tfrac1\lambda(I-K_k\phi_k^T)P_{k-1}.
$$

> [!important] 遗忘因子 $\lambda$ 的至关重要
> $\lambda\in[0.95,0.99]$：$\lambda<1$ 使旧数据权重指数衰减。**当手指从粗糙滑到光滑、$\mu$ 突变时，较小的 $\lambda$ 让估计快速跟踪**（牺牲一点稳态精度）。这与 [[StochasticProcess#5. 学习未知动力学：高斯过程与残差学习|GP 残差学习]]、[[ControlTheory#12. 自适应控制与确定性等价|自适应控制]] 是同一件事——在线辨识时变参数。估出的 $\mu$ 直接进力控的摩擦锥约束 $\|F_t\|\le\mu F_n$：若 RLS 测到 $\mu$ 下降，控制器立即加 $F_n$ 防脱手——这就是**触觉反射**的数学基础（也是防"杯子打滑掉落"的闭环）。

------

## 5. 状态估计：从局部触觉到全局语义

> [!tip] 本节四拍
> **直觉**（信号处理的终极目标不是测力，而是感知世界："杯子在哪、滑了没、摩擦多大"）→ **推导**（贝叶斯递推的五种近似 KF→EKF→UKF→PF→因子图）→ **对比**（高斯单峰 vs 任意多峰；滤波 vs 平滑）→ **联系**（与 [[StochasticProcess#4. 信念更新：从 EKF 失效到粒子滤波|随机过程的 CPF]] 完全同源）。

### 5.1 接触定位

先定接触发生在传感器表面何处：**压力中心 (CoP)** 算压力一阶矩，快但对多点接触不鲁棒；**高斯拟合**对软体连续压力分布做非线性最小二乘，亚像素精度、协方差还能估接触面积；**学习型回归**（ResNet 变体）直接从触觉图回归接触位置（MAE <2.5mm）并分类接触类型。

### 5.2 演进脉络：KF → EKF → UKF → PF → 因子图

这条演进反映灵巧操作从"线性高斯"到"非线性非高斯"的需求升级——而**驱动它的，正是接触的不连续与多峰**（§0 的母题：杯子"滑了/没滑"是双峰）。

**KF（线性高斯最优）**：$x_{t+1}=Ax_t+Bu_t+w_t,\ z_t=Hx_t+v_t$。预测 $\hat x_{t|t-1}=A\hat x+Bu,\ P_{t|t-1}=APA^T+Q$；更新 $K_t=P_{t|t-1}H^T(HP_{t|t-1}H^T+R)^{-1},\ \hat x_{t|t}=\hat x_{t|t-1}+K_t(z_t-H\hat x_{t|t-1})$。**创新项** $z_t-H\hat x$ 是"观测与预测的冲突"，卡尔曼增益 $K_t$ 决定信模型还是信传感器。**局限**：线性+高斯，对接触非线性完全失效。

**EKF（一阶线性化）**：在当前估计处 Taylor 展开 $F_t=\partial f/\partial x,\ H_t=\partial h/\partial x$ 再套 KF。**失效场景**：接触/脱离瞬间动力学不连续跳变，一阶线性化误差巨大（这正是杯子刚滑那一刻）。

**UKF（sigma 点）**：不求 Jacobian，取 $2n+1$ 个 sigma 点 $\mathcal X_i=\bar x\pm\sqrt{(n+\kappa)P}$ 传播均值/协方差，捕获二阶统计、对中等非线性更准。**局限**：仍假设高斯，**无法表示多峰**。

**PF（蒙特卡洛）**：$N$ 个加权粒子近似任意后验 $p(x_t\mid z_{1:t})\approx\sum_i w_t^{(i)}\delta(x_t-x_t^{(i)})$。预测→权重更新 $w_t^{(i)}\propto w_{t-1}^{(i)}p(z_t\mid x_t^{(i)})$→重采样（当有效粒子数 $N_{\text{eff}}=1/\sum_i(w^{(i)})^2$ 过低时）。**天然处理多峰**（杯子"滑了/没滑"两假设并存）、支持非高斯似然（摩擦锥约束），可与 [[StochasticProcess#4.2 Contact Particle Filter (CPF) 与 Manifold Particle Filter (MPF)|接触粒子滤波 (CPF)]] 结合——**这两节是同一对象在两份讲稿里的呼应**。

> [!tip] 演进总结
> | 方法 | 分布假设 | 非线性 | 复杂度 | 灵巧操作适用 |
> |:--|:--|:--|:--|:--|
> | KF | 高斯 | 线性 | $O(n^3)$ | ❌ 仅无接触 |
> | EKF | 高斯 | 一阶线性化 | $O(n^3)$ | ⚪ 连续接触阶段 |
> | UKF | 高斯 | sigma 点 | $O(n^3)$ | ⚪ 中等非线性 |
> | PF | 任意 | 蒙特卡洛 | $O(Nn^2)$ | ✅ 接触切换/多峰 |
> | 因子图 | 任意 | MAP 优化 | 视稀疏性 | ✅ 多模态融合/平滑 |

### 5.3 因子图：多模态融合与触觉里程计

EKF 有线性化误差累积、难处理非高斯约束。**因子图**在滑动窗口内对所有历史状态做**最大后验 (MAP) 平滑**：二部图含**变量节点**（位姿、速度、$\mu$）与**因子节点**（测量/物理约束），$P(X\mid Z)\propto\prod_i\phi_i(X_i;z_i)$，MAP 等价于非线性最小二乘 $\hat X=\arg\min_X\sum_i\|h_i(X_i)-z_i\|^2_{\Sigma_i}$。

- **触觉因子**：训孪生网络从两帧触觉图输出相对位姿 $\Delta T$，作二元因子连接连续位姿节点——**仅凭触觉流就能推断物体相对运动（触觉里程计）**，无需全局视觉。
- **几何因子（ECD）**：惩罚触觉点云到 CAD 表面的距离，用**指数倒角距离** $\mathcal L=\sum_p[1-\exp(-d(p,\mathcal M)^2/\sigma^2)]$ 提鲁棒——远距饱和、避免离群点把优化带进局部极小（与 [[StochasticProcess#5. 学习未知动力学：高斯过程与残差学习|GP]] 的鲁棒核、[[Optimization#3.2 非凸景观：鞍点、虚假极小与"好景观"的判据|非凸景观]]同理）。

> [!note] Sim-to-Real
> 训练触觉观测模型需海量标注，故用**触觉仿真器**（在 Gazebo/PyBullet 渲染深度图模拟 GelSight）生成合成"触觉图-位姿"对，再用**域随机化**（扰动光照/纹理/材料）逼网络学几何本质而非仿真伪影（与 [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|RL sim-to-real]]、[[ContactMechanics#7. Sim-to-Real 与工程实现|接触 sim-to-real]] 同框架）。穿透深度图等新表征见 [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]]。

------

## 6. 近距传感与接触力预处理

> [!tip] 本节四拍
> **直觉**（接触发生前就"看见"物体——第六感；接触后把力处理成策略能用的燃料）→ **推导**（ToF 测距→点云→PCA 几何特征；力归一化）→ **对比**（二值接触 vs 3D 力向量）→ **落点**（估计/力都要预处理成带尺度、去异常的干净信号）。

### 6.1 近距传感 (Proximity)

ToF 传感器（如 VL6180X）在物理接触前感知环境：$d=c\Delta t/2$，量程 ~10cm、噪声 ~2mm、对颜色/环境光不敏感。把分布式 ToF 阵列测量变点云：$p_i^{world}=T_{hand}^{world}\,T_{sensor_i}^{hand}\,[0,0,d_i,1]^T$，再按最小点距/可抓取空间/地面分离三规则优化。**PCA** $\Sigma=\frac1N\sum(p_i-\bar p)(p_i-\bar p)^T$ 给紧凑几何描述：第一主成分=物体主轴/尺度，主成分比值揭示对称性（球 vs 棒），点云中心相对手掌位置编码抓握意图（power grasp 手掌靠中心、precision pinch 指尖靠中心）。

### 6.2 接触力归一化与异常处理

动态非抓持操作（finger gaiting）里，接触力的精细处理是策略学习关键。**为什么要 3D 力而非二值接触**：二值不足以区分"支撑/推进/引导"，力的方向对动态操作至关重要。归一化两方案：线性裁剪 $F'=\frac{\text{clip}(F,F_{min},F_{max})-F_{min}}{F_{max}-F_{min}}\to[0,1]$；Tanh $F_{norm}=\tanh(kF)\to[-1,1]$。再加 **Isolation Forest** 检测力/熵时序异常、邻值替换，与 MA/EMA 时序平滑——平衡响应速度与噪声抑制（这是喂给 [[ReinforcementLearning#8.1 状态表征：触觉是灵巧操作的"暗感官"|RL 触觉状态表征]] 的"燃料预处理"）。

------

## 7. 技术比较与选型指南

> [!abstract] 选传感器=选"打滑信号能否干净浮出噪声底"
> | 传感模态 | 核心信号处理 | 关键工具 | 主要误差源 | 最佳场景 |
> |:--|:--|:--|:--|:--|
> | **MEMS 气压阵列** | 时频分析 | PSD, STFT, Wavelet, KF | 电子噪声(1/f)、串扰 | **高频事件（滑移/碰撞）**、力控 |
> | **电容皮肤** | 非线性校准 | Mooney-Rivlin, PI 迟滞 | 迟滞、边缘场、温漂 | 大面积安全覆盖、接触门控 |
> | **视觉触觉 (GelSight)** | 计算摄影 | 光度立体, 泊松/DST | 积分漂移、高光、计算延迟 | 几何纹理、精密装配、位姿 |
> | **气泡 (Punyo)** | FEM 物理建模 | FEM, 光流, CVXPY | 模型失配、气压波动 | 柔性物体、3D 力矢量 |
> | **多模态融合** | 概率图模型 | 因子图(GTSAM), RLS, ConvLSTM | 同步抖动、外参误差 | 全局状态估计、盲操作 |

------

## 8. 知识回扣与记忆图：一只杯子串起信号处理六层

> [!abstract] 用一条故事线把全讲复述一遍（刻意复述，为了记忆）
> 我们要判断手里的杯子是否开始打滑。**(§1)** 先搭流水线：滑移微振动若高于采样率一半就会混叠成假漂移（Nyquist），用傅里叶看它落在哪个频带、用 STFT/小波抓它发生的瞬间、用因果滤波去噪但必须控制延迟、最后用贝叶斯递推从观测反推状态。**(§2)** 但读数本身有病——电容皮肤的超弹性幂律与迟滞、MEMS 的 1/f 漂移——不先建模就是沙堆。**(§3)** 换 VTS 把"摸"变"看"：光度立体+泊松重建几何、标记点非仿射流动直接显形滑移、气泡膜用 L1 稀疏 FEM 求力。**(§4)** 正面抓滑移：谱质心升高+能量激增、小波细节系数能量突增、RLS 在线追踪突变的 $\mu$——检测到就加紧力、切阻抗，构成触觉反射。**(§5)** 升到状态：从 KF 的线性高斯，一路被接触的不连续与"滑了/没滑"双峰逼到 PF 与因子图。**(§6)** 顺便处理好近距点云与力的归一化喂给策略。**一只杯子，串起了从波形到闭环状态的全链路。**

> [!important] 一张表记住全篇（层 → 问题 → 工具 → 打滑角色）
> | 层 | 核心问题 | 关键工具 | 打滑判断的哪一环 |
> |:--|:--|:--|:--|
> | §1 采样 | 离散会失真吗 | Nyquist、ZOH、抗混叠 | 别把高频滑移折叠成假漂移 |
> | §1 频域 | 在哪个频带 | Fourier、PSD、卷积定理 | 分清电噪/共振/真滑移 |
> | §1 时频 | 何时发生 | STFT、小波、测不准 | 抓滑移起始瞬间 |
> | §2 转导 | 读数可信吗 | Mooney-Rivlin、PI、PSD | 迟滞会淹没微振动 |
> | §3 VTS | 摸变看 | 光度立体、泊松、FEM | 标记点非仿射流动=滑移 |
> | §4 时序 | 检测+估摩擦 | 谱质心、小波能量、RLS | 母题正面战场 |
> | §5 状态估计 | 滑了没/在哪 | KF→PF→因子图 | "滑了/没滑"双峰 |
> | §6 预处理 | 喂给策略 | ToF 点云、力归一化 | 干净燃料 |

> [!tip] 三条贯穿全讲的"暗线"（抓住它们，细节自来）
> 1. **去噪 vs 延迟是永恒权衡**：滤得越干净越滞后（§1.4）；判断打滑须在杯子掉之前完成——这把信号处理与 [[ControlTheory#1.3 频率响应：Bode、相位裕度与带宽|控制相位裕度]]死死绑定。
> 2. **贝叶斯递推一以贯之**：KF/EKF/UKF/PF/因子图（§5）= [[StochasticProcess#4. 信念更新：从 EKF 失效到粒子滤波|CPF]] = [[ReinforcementLearning#2.1 MDP 与 POMDP：把"试错"写成数学|RL belief]]——同一个"预测×更新"。
> 3. **接触的不连续与多峰是演进引擎**：从 KF 到因子图、从阈值法到小波，每一步升级都是被"滑了/没滑"这种非高斯多峰逼出来的。
>
> **跨域：压缩=去噪**（[[InformationTheory|率失真理论]]）：选与噪声信道匹配的失真度量做有损压缩，可自动实现最优去噪。电容噪声建模为信道 $P_{Z\mid X}$、取失真 $\rho(z,y)=-\log P_{Z\mid X}(z\mid y)$，则有损压缩器的重构 = 后验采样去噪——这解释了为何 VAE/VIB 触觉编码器（[[RepresentationLearning|表征学习]]）天然具备去噪能力：**压缩本质上就是在去噪**。

> [!note] 跨领域链接（双向、点对点）
> - **↔ [[ControlTheory]]**：卷积定理↔频率响应（§1.2）；ZOH 延迟↔相位裕度（§1.1）；滑移→阻抗控制（§4.1）。
> - **↔ [[StochasticProcess]]**：贝叶斯递推↔CPF（§1.5、§5.2）；迟滞=非马尔可夫隐变量（§2.2）。
> - **↔ [[ContactMechanics]]**：触觉信号的物理源（力/摩擦/滑移）；摩擦锥约束（§4.2）。
> - **↔ [[RepresentationLearning]]**：学出来的观测模型/触觉因子（§5.3）；触觉 latent、压缩=去噪（§8）。
> - **↔ [[Optimization]]**：L1 稀疏力 FEM（§3.2）；ECD 鲁棒核避局部极小（§5.3）。
> - **↔ [[InformationTheory]]**：率失真的压缩-去噪对偶（§8）；主动感知"采哪条流"（§0）。
> - **↔ [[ReinforcementLearning]]**：控制频率自适应（§1.1）；触觉状态表征燃料（§6.2）。

------

## 9. 结论与展望

我们不再把触觉传感器当"按钮"，而是当需要物理建模 + 概率推理的高维信息源。四条核心洞察：

1. **物理模型不可或缺**：软体传感器的线性映射是错的，必须 Mooney-Rivlin + 非线性电容模型（§2）。
2. **视觉是触觉的新形式**：VTS 通过解逆光学/逆力学提供前所未有的几何分辨率，但泊松/FEM 的计算成本仍是实时挑战（§3）。
3. **概率融合是必由之路**：触觉的局部性与歧义决定它不能单打独斗，因子图把触觉/视觉/运动学严谨融合（§5）。
4. **动态感知决定成败**：静态力控不够，频域滑移检测 + RLS 在线摩擦估计是类人稳定性的关键（§4）。

> [!important] 一句话钥匙
> 信号处理教给灵巧操作的，是把"一串电压"变成"带时间戳、带不确定性的世界状态"，且全程被"去噪 vs 延迟"的权衡所统治。叠上"贝叶斯递推一以贯之"与"卷积定理=频率响应"两座桥，信号处理、随机过程、控制论在你眼里就连成一张图——而那只快要打滑的杯子，就是这张图的试金石。

------

## 10. 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文涉及本 Foundation 的信号处理技术。

### 触觉信号处理与传感融合
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]]：触觉 Sim-to-Real，信号对齐与噪声建模
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch|Touch Dexterity]]：纯触觉策略的接触信号处理
- [[Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture|Dextrous Tactile]]：模块化触觉信号流架构
- [[RotateIt - General In-Hand Object Rotation with Vision and Touch|RotateIt]]：触觉/本体感觉融合的滤波与同步
- [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]]：穿透深度=域不变触觉几何空间
- [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding|CGP]]：KL-正则触觉 VAE 压缩 + 接触一致性映射
- [[STOLA - Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning|STOLA]]：MoE 路由触觉-语言常识推理

### 时序信号与频率域
- [[Autoregressive Policies for Continuous Control Deep Reinforcement Learning|Autoregressive Policies]]：自回归时序建模
- [[The Sampling Theorem With Constant Amplitude Variable Width Pulses|Sampling Theorem]]：采样基础理论，连接 Nyquist、PWM 与傅里叶
- [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration|DemoSpeedup]]：时序示教的熵引导采样
- [[TARC - Time-Adaptive Robotic Control|TARC]]：按局部动力学带宽调控制频率

### 多模态信号融合
- [[Learning Visuotactile Skills with Two Multifingered Hands (HATO)|HATO]]：视觉-触觉多模态融合
- [[Proximity Perception-Based Grasping Intelligence (P2GI)|P2GI]]：部件级多模态感知
- [[Visual-tactile Pretraining for Humanlike Manipulation Dexterity]]：二值触觉有效性
- [[Vision-force-fused Curriculum Learning for Robotic Assembly]]：视觉-力融合课程

### 触觉 Sim-to-Real 与新表征
- [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]]：穿透深度图统一表征
- [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding|CGP]]：潜在触觉 VAE + 耦合扩散

### 触觉-语言跨模态推理
- [[STOLA - Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning|SToLa]]：MoE 触觉-语言框架
