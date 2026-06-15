---
tags:
  - paper
  - locomotion
  - actuator-network
  - sim-to-real
  - structured-dynamics
  - WMTS
aliases:
  - Agile Dynamic Motor Skills
  - Hwangbo ActuatorNet
paper-year: 2019
read-date: 2026-06-15
venue: Science Robotics 2019 (ETH Zurich + Intel; Hwangbo, Hutter)
paper-pdf: "[[Learning Agile and Dynamic Motor Skills for Legged Robots.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
---

# Learning Agile and Dynamic Motor Skills for Legged Robots (Actuator Net)

> [!abstract] 核心贡献
> 里程碑式 sim-to-real（ANYmal 四足，Science Robotics 2019）：提出 **actuator network（执行器网络）**桥接 sim-real 的**执行器侧 reality gap**。三步法：(1) 识别刚体物理参数；(2) **从真实数据训一个 actuator net**——MLP 把"执行器命令历史 + 关节状态历史"映到"实现的关节力矩"，端到端建模复杂 SEA/软件动力学（解析 SEA 模型不够准）；(3) 把 actuator net 嵌进 rigid-body sim，训控制策略（MLP：状态历史→关节位置目标）并直接部署。sim 跑 ~1000× 实时（一半时间在算 actuator nets），策略推理 25 μs/CPU。ANYmal 实现前所未有的精确节能速度跟踪、最快奔跑、复杂跌倒恢复。**对 WMTS：actuator net 是 WMTS "actuator+rigid 结构化 WM" 的执行器拼图——与 [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]]（刚体 Lagrangian + 接触力残差）拼成完整结构化动力学：actuator net（命令→力矩）+ Lagrangian 刚体 + ensemble 接触力；其"命令历史→力矩"正是 LAAA 要建的执行器延迟/动态。**

> [!tip] 与理论基础的关联
> - [[ControlTheory]] — 执行器动力学（SEA）；命令→力矩映射；rigid-body 模型。
> - [[ReinforcementLearning]] — sim 训策略（actuator net 嵌入）+ 零样本部署。
> - [[EmbodiedAI]] — 真机 sim-to-real；数据驱动提升 sim 保真。
> - [[Final_WMTS]] — **WMTS 结构化 WM 的执行器拼图**（actuator net 命令历史→力矩）；与 SSRL 刚体+接触力互补；LAAA 执行器动态。
>
> **核心技术**: Actuator Network (MLP 命令历史→力矩, 真实数据训), 三步法 (刚体 ID → actuator net → sim 训策略), rigid-body sim + actuator net, ~1000× 实时, 状态历史→关节目标策略

## 0. 阅读定位与范本价值

Hwangbo 2019 是 **actuator network 的原典**，对 WMTS 的价值是补上**结构化 WM 的执行器拼图**。WMTS 主张 "actuator+rigid 结构化 WM"，而库内已有：[[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]] 给"刚体 Lagrangian + 接触力残差"，[[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning|DexCtrl]] 给"自适应增益"——**本篇给"执行器命令→力矩"的 actuator net**。三者拼成 WMTS 完整的结构化动力学：
$$
\text{命令} \xrightarrow{\text{actuator net (Hwangbo)}} \tau \xrightarrow{\text{Lagrangian 刚体 (SSRL)}} \ddot q,\quad +\ \text{ensemble 接触力 (SSRL)} + \text{自适应增益 (DexCtrl)}.
$$
它是 ETH Hutter 系（[[Robotic World Model: A Neural Network Simulator|RWM]]、[[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation|ViserDex]] 同组）的开山之作。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
腿式机器人高维、非光滑、接触多变、解析模型不准（尤其 SEA 执行器动力学），传统控制难。RL 可学但多限于 sim，真机训练贵。本文在 sim 训策略零样本迁 ANYmal——关键是用 **actuator net 从真实数据建准执行器动力学**，弥合 sim-real 执行器 gap。

### 1.2 直观隐喻
sim 里电机是"理想力矩源"，真机 SEA 有弹性、延迟、软件层——理想假设导致 sim-real gap。actuator net 像"给 sim 装一个从真实电机学来的'真实执行器模拟器'"：你发命令，它按真机的脾气（从历史学到的）输出真实力矩。如此 sim 里练的策略到真机就不"水土不服"。可证伪含义：actuator net 的价值在"**执行器动力学是 gap 主因**"时最大；若 gap 主要在接触/几何，actuator net 不够（需 SSRL 接触力）。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| 解析 SEA 模型 | 弹簧-阻尼物理 | 不够准（软件/复杂动力学建不全） |
| 轨迹优化/模块控制 | 刚体 + 数值优化 | 接触不可预设、执行期算、任务特定 |
| 纯 sim RL（理想执行器） | 理想力矩源 | 执行器 reality gap → 迁移失败 |
| domain randomization | 随机执行器参数 | 盲、可能过保守 |
| **本文 actuator net** | **数据驱动执行器动力学** | locomotion SEA（非 in-hand）；需真实执行器数据 |

### 1.4 Delta 分析
精确增量：**actuator net**——用真实数据训一个 MLP（命令历史 + 关节状态历史 → 实现力矩），嵌进 rigid-body sim，端到端建执行器/软件动力学（替不够准的解析 SEA 模型）。把"理想执行器 sim"换成"数据驱动准执行器 sim"，从而零样本迁移敏捷动作。

## 2. 核心方法（原理与方法：三步 + actuator net）

### 2.1 三步法（无跳步）
1. **刚体识别**：ANYmal 经高质量轴承连接，近似理想多体系统；识别刚体物理参数（惯量等）。
2. **训 actuator net**：SEA 执行器动力学复杂（解析模型不足）。训一个 **MLP**：输入**执行器命令历史 + 关节位置误差/速度历史**，输出**实现的关节力矩**——端到端学"命令→力矩"映射，从真实数据。
3. **sim 训策略 + 部署**：把 actuator net 嵌进 rigid-body sim（sim ~1000× 实时，半数时间算 actuator nets），训控制策略（MLP：**机器人状态历史 → 关节位置目标**），直接部署真机（25 μs/CPU 推理）。

### 2.2 为什么 actuator net 有效
SEA/软件动力学的"命令→力矩"关系含弹性、延迟、非线性——**历史依赖**（故输入历史）。解析模型抓不全，但**真实数据 + MLP** 能拟合。嵌进 sim 后，sim 的力矩响应匹配真机 → 策略在准 sim 里练 → 零样本迁移。

### 2.3 概念边界与符号陷阱
- actuator net 建**执行器侧** gap（命令→力矩），不建接触/几何（那是 SSRL 的接触力残差）。
- 输入**历史** → 捕捉延迟/动态（LAAA 相关）。
- 策略也用状态历史 → 部分可观补偿。
- locomotion SEA；in-hand 执行器（LinkerHand）需自己的 actuator net。

## 3. 实验与验证
- ANYmal：精确节能速度跟踪、最快奔跑、复杂跌倒恢复——前所未有。**因果**：actuator net 使 sim 执行器响应准 → 敏捷策略零样本迁移。
- sim ~1000× 实时；策略 25 μs/CPU（无需特殊硬件）。
- 换网络参数即换行为（共享代码、只改任务）。
- 边界：locomotion SEA；需真实执行器数据。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 真正的 insight
**sim-to-real 的执行器侧 reality gap 可由一个从真实数据学的 actuator net（命令历史→力矩 MLP）弥合——嵌进 rigid-body sim 使其执行器响应匹配真机，从而 sim 训的敏捷策略零样本迁移。** 一句话：**别用理想执行器——用数据驱动的 actuator net 把 sim 的"命令→力矩"建准。**

### 4.2 为什么有效
(1) actuator net 拟合解析模型抓不全的执行器动力学；(2) 历史输入捕捉延迟/非线性；(3) 嵌 sim → 力矩响应匹配真机；(4) 快 sim（1000×）+ 快推理（25 μs）。

### 4.3 什么时候会失效
- gap 主因在接触/几何（actuator net 不管）→ 需 SSRL 接触力。
- 真实执行器数据不足/不覆盖工况。
- 执行器随时间漂移（温漂）→ 需在线适应（LAAA/DexCtrl）。

## 5. 替代方案与局限（未来与结合）

### 5.1 理论维度
actuator net 是数据驱动的执行器系统辨识（替解析 SEA 模型）：把"命令→力矩"建成历史依赖的 MLP。与 SSRL（接触力残差）、DexCtrl（增益）共同构成结构化动力学的不同组件。

### 5.2 算法维度（结构化动力学组件，对 WMTS 关键）
| 组件 | 代表 | 建什么 |
|---|---|---|
| **执行器（命令→力矩）** | 本文 actuator net | SEA/软件动力学 |
| 刚体（力矩→加速度） | [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]] Lagrangian | $M(q)\ddot q$ |
| 接触力 $F^e$ | SSRL ensemble | 环境接触 |
| 自适应增益 | [[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning|DexCtrl]] | $K_P,K_D$ |

### 5.3 工程/实验维度
执行器数据覆盖、actuator net 输入历史长度、温漂、locomotion vs in-hand 是主要边界；接触/触觉、在线适应未覆盖（其它组件补）。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM 的迁移

| WMTS 模块 | 本文对应 | 迁移设计 |
|---|---|---|
| **结构化 WM 执行器拼图** | actuator net（命令历史→力矩） | WMTS 为 LinkerHand 训 actuator net（CAN 命令→指节力矩），嵌结构化 sim |
| LAAA | 历史输入捕捉延迟 | actuator net 条件温度/延迟 → 在线适应执行器漂移 |
| 完整结构化动力学 | + SSRL 刚体/接触 + DexCtrl 增益 | 命令→[actuator net]→力矩→[Lagrangian]→运动 + [ensemble 接触力] + [自适应增益] |
| sim 速度 | 1000× 实时 | WMTS Oracle 训练需快 sim |

**核心论证（critical thinking）**：Hwangbo 2019 给 WMTS 补上**结构化 WM 的执行器拼图**，是 WMTS "actuator+rigid 结构化 WM" 的 "actuator" 字面来源。把库内三篇拼起来，WMTS 的结构化动力学就完整了：**命令 →[actuator net (Hwangbo)]→ 力矩 →[Lagrangian 刚体 (SSRL)]→ 运动，外加 [ensemble 接触力残差 (SSRL)] 与 [自适应增益 (DexCtrl)]**。这套"组件化结构化 WM"正是 WMTS 区别于纯神经 WM（[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]）的物理结构所在——每个组件都有明确物理意义、可分别用真实数据校准、样本效率高、无 model-exploitation（结构正确处）。**对 LAAA 尤其关键**：actuator net 输入**命令历史**，天然捕捉执行器延迟/动态；WMTS 可让 actuator net **条件于温度/延迟**，实现执行器漂移的在线适应（与 [[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning|DexCtrl]] 增益自适应、[[SOLVING RUBIK’S CUBE WITH A ROBOT HAND|Rubik]] 隐式 meta-learn 组成 LAAA 多级）。**边界**：ANYmal SEA 执行器与 LinkerHand 执行器（CAN、可能腱驱）动力学不同，WMTS 需用 LinkerHand 真实数据训自己的 actuator net；且这是 locomotion，接触侧仍靠 SSRL/触觉。

### 6.2 可验证实验建议
- LinkerHand actuator net：从真机采"命令→指节力矩"数据训 actuator net，嵌结构化 sim，测转笔 sim-to-real gap 闭合。
- 组件化结构化 WM：actuator net + Lagrangian + ensemble 接触力 在转笔上的预测精度 vs 纯神经 WM。
- LAAA：actuator net 条件温度/延迟，测执行器漂移在线适应。

### 6.3 不应过度外推的点
- ANYmal SEA ≠ LinkerHand 执行器；需自采数据训。
- actuator net 只管执行器侧；接触/几何需 SSRL/触觉。
- locomotion 验证，in-hand 接触更复杂。

## 7. 与知识体系的联系

### 与 [[ControlTheory]] 的联系
执行器动力学（SEA）的数据驱动辨识（命令→力矩 MLP）替解析模型；rigid-body 模型 + actuator net 的混合 sim。

### 与 [[ReinforcementLearning]] 的联系
sim 训策略（actuator net 嵌入准 sim）+ 零样本部署；状态历史→关节目标策略。

### 与 [[EmbodiedAI]] 的联系
真机 sim-to-real 里程碑；数据驱动提升 sim 保真（actuator net）；敏捷 locomotion + 跌倒恢复。

### 与 [[Final_WMTS]] 的联系
WMTS 结构化 WM 的执行器拼图（actuator net 命令历史→力矩）；与 SSRL 刚体/接触力、DexCtrl 增益拼成完整结构化动力学；actuator net 历史输入 = LAAA 执行器动态适应。

## References
- 原始 PDF：[[Learning Agile and Dynamic Motor Skills for Legged Robots.pdf]]（ETH/Intel，Science Robotics 2019，arXiv 1901.08652）
- 结构化动力学组件：[[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]]（刚体+接触力）、[[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning|DexCtrl]]（增益）
- ETH Hutter 系：[[Robotic World Model: A Neural Network Simulator|RWM]]、[[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation|ViserDex]]
- 项目入口：[[Final_WMTS]]
