---
tags:
  - paper
  - dexterous-manipulation
  - adaptive-control
  - sim-to-real
  - actuator-gap
  - WMTS
aliases:
  - DexCtrl
paper-year: 2025
read-date: 2026-06-15
venue: arXiv 2505.00991 (UC Berkeley, Tomizuka 组)
paper-pdf: "[[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
  - "[[Dynamic Non-Prehensile Manipulation]]"
---

# DexCtrl: Sim-to-Real Dexterity with Adaptive Controller Learning

> [!abstract] 核心贡献
> 指出一个被忽视的 sim-to-real gap：**低层控制器动力学的不匹配**——最终发给电机的力矩 $\tau=K_P(q^d-q^c)+K_D(\dot q^d-\dot q^c)$ 同时取决于轨迹**和控制参数（增益 $K$）**，同一轨迹在不同增益下产生迥异接触力。现有做法靠手调增益或增益随机化（费力、任务特定、增训练难度）。DexCtrl **联合预测动作 $\hat a_t$ 与控制参数 $\hat K_t$**，依据轨迹+控制器的历史窗口，**闭环自适应调增益**，并把控制参数显式放进 observation 以更好推理力交互。LEAP 手（16-DOF）rotation/flipping 上 sim+real 均超基线。**对 WMTS：这是 LAAA 的"控制器级适应"路线（前有 dynamics 级 DyWA/RMA、隐式 Rubik、不确定性 FOWM）——WMTS 的 LinkerHand 同样是 PD/力矩控制，应学自适应增益、把执行器状态入 observation。**

> [!tip] 与理论基础的关联
> - [[ControlTheory]] — PD/阻抗力矩控制 $\tau=K_P\Delta q+K_D\Delta\dot q$；自适应增益 = 学习式变阻抗。
> - [[ReinforcementLearning]] — 策略联合输出 action + 控制参数；历史条件化。
> - [[EmbodiedAI]] — sim-to-real 灵巧；控制器 gap 的闭环自适应。
> - [[Final_WMTS]] — **LAAA 的控制器级适应**：学自适应增益、执行器状态入 obs；与 dynamics 级适应互补。
> - [[Dynamic Non-Prehensile Manipulation]] — rotation/flipping 接触密集；转笔同需精确力/增益控制。
>
> **核心技术**: 联合预测 action + 控制增益 $\hat K_t$, 历史窗口条件 (轨迹+控制器), 闭环自适应阻抗, 控制参数入 observation, PD 力矩控制, LEAP 16-DOF

## 0. 阅读定位与范本价值

DexCtrl 对 WMTS 的价值聚焦在 **LAAA（真机执行器适应）的一个具体、常被忽视的维度：控制器增益**。库内适应论文各管一段——[[SOLVING RUBIK’S CUBE WITH A ROBOT HAND|Rubik]] 隐式 meta-learn 动力学、[[DyWA: Dynamics-adaptive World Action Model|DyWA]]/RMA 显式动力学嵌入、[[Finetuning Offline World Models in the Real World|FOWM]] 不确定性适配——而 **DexCtrl 补上"控制器增益级"适应**：力矩 = f(轨迹, 增益)，光适应动力学不够，还要适应/预测增益。读它要把它放进 WMTS 的 LAAA 多级适应图里。

它与 [[DyWA: Dynamics-adaptive World Action Model|DyWA]]（变阻抗）、[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]（接触力控制）相关，但独特在**把控制器参数当可学、可适应、可观测的一等对象**。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
灵巧 sim-to-real 多关注观测噪声/物体力随机化，却忽视**控制器 gap**：电机力矩由轨迹**和增益 $K$** 共同决定，同一轨迹在 sim/real 不同增益下接触力迥异。手调增益不够精、增益随机化增训练难度。DexCtrl 让策略**联合预测动作 + 增益**、依历史闭环自适应，自动跨过控制器 gap。

### 1.2 直观隐喻
增益 $K$ 像"手指的软硬程度"：太硬（$K_P$ 大）稳态误差小但易震荡，太软（$K_D$ 大）抑制过冲但放大高频噪声。sim 调好的软硬到真机就不对了。DexCtrl 不固定软硬，而是**边做边根据手感历史（期望 vs 实际轨迹 + 当前增益）自动调软硬**——像人接触不同物体自动调整握力。可证伪含义：增益自适应的收益集中在"**接触力敏感、增益 gap 大**"的任务；接触松、增益不敏感时收益小。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| 仅预测动作 + 固定增益 | 轨迹策略 | 增益 gap → 接触力错；需大量手调 |
| 手调增益 | 人对比 sim/real 轨迹 | 难达精度、费力、任务特定 |
| 增益随机化 | 训练时随机 $K$ | 增训练难度、探索难 |
| 观测/力随机化 | 鲁棒轨迹 | 不解决控制器 gap |
| **DexCtrl** | **联合预测 action + 增益、历史条件、增益入 obs** | rotation/flipping（非高速 spin）；动作空间增维；LEAP 16-DOF |

### 1.4 Delta 分析
精确增量：(1) **识别控制器 gap** 为关键 sim-to-real 因素（被忽视）；(2) **联合学 action + 增益**（而非固定/随机）；(3) **历史条件 + 增益入 observation** → 闭环自适应 + 更好力推理。把"手调/随机增益"换成"学到的闭环自适应增益"。

## 2. 核心方法与理论（原理与理论：联合预测 action + 增益）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $[q^d,\dot q^d]$ | $\mathbb R^{32}$ | 期望轨迹 | 策略输出 | 期望关节位/速 | LEAP 16 关节 |
| $[q^c,\dot q^c]$ | $\mathbb R^{32}$ | 真机/sim | observed | 当前关节位/速 | 反馈 |
| $\tau$ | $\mathbb R^{16}$ | 控制器 | computed | 电机力矩 | = f(轨迹, $K$) |
| $K=(K_P,K_D)$ | 刚度/阻尼 | **策略预测 $\hat K_t$** | learned | 控制增益 | **一等可学对象** |
| $\hat a_t$ | 关节位置动作 | 策略 | learned | 期望动作 | 与 $\hat K_t$ 联合输出 |
| 历史窗口 | $(q^c,q^d,a,K)$ 序列 | replay | 条件 | 自适应依据 | 闭环 |
| obs（含 $K$） | 观测 | — | — | 含控制参数 | 利于力推理 |

### 2.2 控制器与 gap（无跳步）
LEAP 手关节力矩控制（PD/阻抗）：
$$
\tau=K_P(q^d-q^c)+K_D(\dot q^d-\dot q^c),
$$
$K_P$ 刚度、$K_D$ 阻尼。**力矩被 $K$ 直接调制** → $K$ 必须careful tune：$K_P\uparrow$ 减稳态误差但易震荡；$K_D\uparrow$ 抑过冲但放大高频噪声。**sim/real 的 $K$ 不匹配 → 同轨迹接触力迥异 → sim-to-real gap**。

### 2.3 DexCtrl：联合预测 + 闭环自适应
策略**每步联合输出** $\hat a_t$（关节位置动作）与 $\hat K_t$（控制增益），条件于**历史窗口**内的期望/实际轨迹 $(q^d,q^c)$ + 对应增益 $K$。于是：
- **闭环自适应增益**：根据"期望 vs 实际"的历史偏差自动调 $K$，跨过控制器 gap，免手调/随机化。
- **增益入 observation**：策略显式知道当前 $K$ → 更好推理力交互（力 = f(轨迹偏差, $K$)）、抑制随机化带来的探索难。

### 2.4 概念边界与符号陷阱
- DexCtrl 适应的是**控制器增益**，不是动力学模型（≠ DyWA/RMA）也不是 WM——适应维度不同。
- $\hat K_t$ 是**学习式变阻抗**：与 [[DyWA: Dynamics-adaptive World Action Model|DyWA]] 的固定变阻抗动作空间不同，这里增益本身被预测、自适应。
- 增益入 obs 是关键设计（力推理）。
- 仍是 rotation/flipping，非高速 spin。

## 3. 训练、数据与实验（实验与验证）

### 3.1 实验设置
LEAP 手（16-DOF），joint torque control。两任务：in-hand rotation（指尖绕轴转物不掉）、flipping。sim + 真机。对照仅预测动作 + 固定增益、增益随机化等。

### 3.2 关键结果与因果解释
- **sim + real 均超基线**（rotation/flipping）。**因果**：自适应增益跨控制器 gap，接触力匹配更好。
- **减人工 + 减训练难度**：免手调、免大范围增益随机化。**因果**：策略直接学增益、增益入 obs → 探索更易。
- **更好力交互推理**：增益入 obs → 力 = f(偏差, K) 可被策略推理。

### 3.3 Ablation / 对照因果链
- `固定增益 → 控制器 gap → 接触力错 → 失败`。
- `增益随机化替自适应 → 训练难度增、探索难`。
- `增益不入 obs → 力推理变差`。

### 3.4 工程约束与实验边界
- rotation/flipping（非高速 spin）。
- 动作空间增维（action + K）。
- LEAP 16-DOF；力矩控制设定。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 论文真正的 insight
**sim-to-real gap 的一个关键且被忽视的来源是控制器增益不匹配（力矩 = f(轨迹, 增益)）；让策略联合预测动作与增益、依历史闭环自适应、并把增益放进观测，能自动跨过控制器 gap，免手调/大随机化。** 一句话：**别固定/随机增益——把增益当可学、可适应、可观测的一等对象。**

### 4.2 为什么这个设计有效
(1) 闭环自适应增益按历史偏差调软硬、匹配真机接触力；(2) 增益入 obs → 策略能推理力交互；(3) 学增益免手调精度不足、免随机化训练难。

### 4.3 什么时候会失效
- 增益不敏感/接触松的任务收益小。
- 高速动态接触（spin）增益变化更剧，窗口自适应可能跟不上。
- 动作+增益联合预测增维、训练更复杂。

## 5. 替代方案与理论局限（未来与结合）

### 5.1 理论维度
DexCtrl 是学习式自适应控制（adaptive control）：把经典自适应控制的"在线辨识 + 调参"用 RL 历史条件化实现。无显式稳定性证书；自适应质量取决于历史窗口与训练覆盖。

### 5.2 算法维度（适应维度对照，对 WMTS 关键）
| 适应维度 | 代表 | 适应什么 |
|---|---|---|
| **控制器增益** | 本文 DexCtrl | $K_P,K_D$（接触力） |
| 动力学（显式） | [[DyWA: Dynamics-adaptive World Action Model|DyWA]]/RMA | 物体/物理嵌入 |
| 动力学（隐式） | [[SOLVING RUBIK’S CUBE WITH A ROBOT HAND|Rubik]] | LSTM 隐状态 meta-learn |
| 不确定性/WM | [[Finetuning Offline World Models in the Real World|FOWM]] | epistemic uncertainty |

### 5.3 工程/实验维度
增益敏感度、历史窗口长度、动作增维、力矩控制设定是主要边界；高速 spin、触觉、WM 未覆盖。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM 的迁移（LAAA 控制器级）

| WMTS 模块 | DexCtrl 对应 | 迁移设计 |
|---|---|---|
| **LAAA（执行器适应）** | 联合预测 action + 自适应增益 | WMTS LinkerHand 学自适应 $K_P,K_D$，跨 CAN 控制器 gap |
| observation | 增益入 obs | WMTS obs 加执行器状态（增益/温度/延迟）→ 力推理 |
| 接触力控制 | 自适应阻抗 | 转笔接触力精控用学习式变阻抗 |
| 多级适应 | 控制器级 | 与 dynamics 级（DyWA）+ 不确定性（FOWM）组合 |

**核心论证（critical thinking）**：DexCtrl 给 WMTS 的 **LAAA 补上"控制器增益级适应"这一层**。库内适应论文各覆盖一个维度，而 DexCtrl 指出一个常被忽视但对接触力至关重要的源头：**力矩 = f(轨迹, 增益)，光适应动力学/物体不够，增益不匹配照样产生错误接触力**。WMTS 的 LinkerHand 是 CAN 力矩控制，同样面临增益/延迟 gap——所以 WMTS 的 LAAA 应当是**多级**的：(1) **控制器级**（DexCtrl：学自适应 $K_P,K_D$、增益入 obs）；(2) **动力学级**（DyWA/RMA：历史估物理嵌入）；(3) **不确定性级**（FOWM：ensemble-LCB）；可选 (4) **隐式**（Rubik：循环 + DR meta-learn）。DexCtrl 还给一条具体工程建议：**把执行器状态（增益、温度、延迟）显式放进 observation**，让策略/WM 能推理力交互——这对触觉 + 力主导的转笔尤其重要。**但要注意**：DexCtrl 做 rotation/flipping（中低速），转笔的高速接触下增益变化更剧烈，窗口自适应能否跟上需验证；且联合预测 action+增益增大动作空间，WMTS 需权衡。

### 6.2 可验证实验建议
- WMTS LAAA 控制器级：LinkerHand 学自适应 $K_P,K_D$，对照固定增益/随机化，测转笔接触力匹配与成功率。
- 增益入 obs 消融：测执行器状态入观测对力推理与 sim-to-real 的影响。
- 多级适应组合：控制器级（DexCtrl）+ 动力学级（DyWA）+ LCB（FOWM）在转笔上的叠加收益。

### 6.3 不应过度外推的点
- rotation/flipping 中低速成功不能直接外推高速 spin（增益变化更剧）。
- 增益自适应窗口在高速下可能滞后。
- 动作+增益联合预测增维，训练成本上升。

## 7. 与知识体系的联系

### 与 [[ControlTheory]] 的联系
PD/阻抗力矩控制 $\tau=K_P\Delta q+K_D\Delta\dot q$；DexCtrl = 学习式自适应控制（在线调增益），是经典 adaptive control 的 RL 实现。

### 与 [[ReinforcementLearning]] 的联系
策略联合输出 action + 控制参数，历史窗口条件化；增益入 obs 改善力交互推理。

### 与 [[EmbodiedAI]] 的联系
sim-to-real 灵巧；识别并闭环自适应控制器 gap，免手调/大随机化。

### 与 [[Final_WMTS]] 的联系
WMTS LAAA 的控制器增益级适应；执行器状态入 obs；与 dynamics 级（DyWA）+ 不确定性（FOWM）+ 隐式（Rubik）组成多级适应。

## References
- 原始 PDF：[[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning.pdf]]（UC Berkeley，arXiv 2505.00991）
- 适应维度对照：[[DyWA: Dynamics-adaptive World Action Model|DyWA]]（动力学）、[[SOLVING RUBIK’S CUBE WITH A ROBOT HAND|Rubik]]（隐式）、[[Finetuning Offline World Models in the Real World|FOWM]]（不确定性）
- 变阻抗相关：[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]、[[DyWA: Dynamics-adaptive World Action Model|DyWA]]
- 项目入口：[[Final_WMTS]]、[[Dynamic Non-Prehensile Manipulation]]
