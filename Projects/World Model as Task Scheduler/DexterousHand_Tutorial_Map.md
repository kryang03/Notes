---
tags: [Dexterous_Manipulation, Tutorial, Actuation, Transmission, Sim-to-Real, L25_Hand, WMTS]
aliases: [灵巧手 Tutorial 阅读地图, Hand Tutorial Map]
date: 2026-09-02
related:
  - "[[Actuation]]"
  - "[[Final_WMTS]]"
  - "[[sim2real]]"
---

# 灵巧手硬件 Tutorial 阅读地图：从电能到关节力矩

> [!abstract] 这三个文件夹在讲什么
> `DexterousHandMechanicalStructure/`、`DexterousHandActuatorModel/`、`DexterousHandTransmissionModel/` 是同一条**力矩传递链路**被切成的三段。仿真器把 RL 的 action 当成关节力矩 $\tau$ 直接施加；真机上 $\tau$ 却是**电能 → 电磁力矩 → 电流环 → 减速/丝杠/连杆 → 关节**这条链的输出。链上每一个非理想环节都是 Sim-to-Real gap 的物理来源——这正是 [[Actuation]] Foundation 的母题"一个力矩指令的旅程"，这里是它在 LinkerHand L25 上的具体落地。

> [!tip] 读完整套你应该能回答
> 1. 为什么 20 mm 以内的手指关节几乎不可能直驱，必须靠减速器或丝杠？（[[电机]] 气隙剪应力律）
> 2. 为什么策略给的"力矩"在真机上既不是电流、也不是关节力矩？（[[FOC_Control]] + [[Actuator2RigidDynamicsModel_gap]]）
> 3. 拇指为什么有 24 mrad 的换向死区、四指为什么没有？只需哪两个参数就能在 MuJoCo 里复现？（[[Transmission2JointDynamics_gap]]）
> 4. 仿真关节的 `armature` 该填多少，填 0 会怎样？（[[LinkerSysId]]）
> 5. MuJoCo 的 `frictionloss` 为什么默认参数下"不像摩擦像阻尼"？（[[MuJoCo_Sim2Real_Params]]）

---

## 1. 链路总图

```
 电能 ──▶ ① 电机层 ──▶ ② 驱动层 ──▶ ③ 减速层 ──▶ ④ 传动层 ──▶ 关节力矩 ──▶ ⑤ 刚体 + 接触
         电磁力矩       FOC 电流环     减速器/丝杠     连杆/腱绳/电缸                 Dynamics / ContactMechanics
         [[电机]]       [[FOC_Control]] [[减速器]]      [[传动]]                     (Foundation)
                        ┃                                ┃
        指令 → 电机轴: [[Actuator2RigidDynamicsModel_gap]]   电机轴 → 关节: [[Transmission2JointDynamics_gap]]
        (串级环 / CAN / 延迟 / 8-bit 量化 / 热)              (摩擦 N¹ 折算 / 换向死区 / set-valued 摩擦)
                                     ┃
                    worked example: [[LinkerSysId]]  ──▶  引擎落地: [[MuJoCo_Sim2Real_Params]]
                                     ┃
                    全链路 gap 总图与分流: [[sim2real]]
```

## 2. 推荐阅读顺序（按"先建直觉、再深挖、最后落地"）

| 序 | 文件 | 文件夹 | 管链路哪一段 | 一句话 |
|:-:|:--|:--|:--|:--|
| 1 | [[电机]] | MechanicalStructure | 电能 → 电磁力矩 | 直流电机统一模型、$K_t=K_e$、力矩随体积缩小的 $D^2L$ 律、四类电机与微型空心杯电缸 |
| 2 | [[减速器]] | MechanicalStructure | 电机轴 → 减速输出 | 背隙 / 效率 / 反驱 / 自锁判据；丝杠三兄弟；惯量按 $N^2$、摩擦按 $N^1$ |
| 3 | [[传动]] | MechanicalStructure | 减速输出 → 关节 | 连杆 / 腱绳 / 直驱 / QDD / **直线电缸+连杆**（L25 路线）五条路线对比 |
| 4 | [[sim2real]] | MechanicalStructure | 全链路 | 按层列 gap、DR 建议、action space 选择，并分流到 5–9 |
| 5 | [[FOC_Control]] | ActuatorModel | 电流 → 电磁力矩 | Clarke/Park、$T_e=K_tI_q$、无感观测、温度漂移、高速包络、Actuator Model 输入集 |
| 6 | [[Actuator2RigidDynamicsModel_gap]] | ActuatorModel | 指令 → 电机轴 | 串级三环、CAN 串行落地、归一化指令、延迟预算、可信观测 |
| 7 | [[LinkerSysId]] | MechanicalStructure | 丝杠折算 | $J_{armature}=N_{eq}^2J_{rotor}$ 的 worked example（四指 + 拇指） |
| 8 | [[Transmission2JointDynamics_gap]] | TransmissionModel | 电机轴 → 关节 | 拇指换向死区的全部来源、两参数模型、辨识与激励设计 |
| 9 | [[MuJoCo_Sim2Real_Params]] | TransmissionModel | 引擎参数 | `solref/solimp/impratio/cone/armature/damping/frictionloss` 的精确语义与 L25NS 取值 |

> [!note] 为什么 LinkerSysId 放在 MechanicalStructure 文件夹却排在第 7
> 它是 [[减速器]]（旋转→直线折算）与 [[Transmission2JointDynamics_gap]]（摩擦折算）之间的桥。文件夹按"内容类型"分，阅读顺序按"链路位置"排，两者不必一致。

## 3. 贯穿例子：L25 的一根手指

全套 tutorial 共用同一个例子，读到任何一篇都能回到它：

- **四指（如 `index_pip`）**：微型空心杯电机 → 丝杠电缸（导程 $l=0.7$ mm）→ 推杆 → 力臂 $r(\theta)\approx12$ mm 的连杆 → 关节。等效减速比 $N_{eq}=2\pi r/l\approx108$，`armature`$\approx1.65\times10^{-3}$ kg·m²，上电可反驱。
- **拇指（`thumb_mcp` / `thumb_cmc_pitch`）**：同样的电缸前面多一级 **17:1 折返减速箱**，$l=0.6$ mm，$N_{eq}\approx1400\sim1800$。转子轻 1018 倍所以 `armature` 反而更小（$2.84\times10^{-4}$），但摩擦按 $N^1$ 折算被放大 11–28 倍 → **24 mrad 换向死区**，且因减速箱反向效率跌破零而不可反驱。
- **接口**：CAN 1 Mbps、指令与反馈共用 8-bit 栅格（LSB = 量程/255）、位控命令 20–50 Hz、MCU 命令预滤波 $T_f\approx120$ ms、纯传输延迟 $T_d\lesssim10$ ms。

## 4. 与 WMTS 项目的接口

| Tutorial 结论 | 进入 WMTS 哪个模块 |
|:--|:--|
| 力矩反馈只能当输入不能当目标；关节角 + 触觉是可信观测 | [[Final_WMTS#4.D 可靠信号与预测目标|Final_WMTS §4.D]] |
| Actuator Model 需要历史窗口 + 温度 + 延迟编码 $z_\delta$ | [[Final_WMTS#4.A Actuator Model：指令 → 关节力矩|Final_WMTS §4.A]] |
| 换向死区是时序事件而非全程延迟；拇指两关节动作带宽应受硬约束 | [[Idea-013-Stick-Slip-Mode-Switching]] · [[Idea-002-Latency-Aware-Actuator]] |
| 力矩标度整体缩放 DR 补不了，摩擦/空程的构型依赖适合宽幅 DR | [[Idea-005-Saturation-Boundary-Active-Learning]] |

## 5. 本轮（2026-09-02）修订记录

- 事实纠错：LEAP/Allegro v4/DLR-HIT II/Shadow/HATO/BRUCE/Ability/Faive 的传动方式；BLDC 起动力矩、DLRK/12N14P 原因；RV 减速比公式；滚珠丝杠自锁残句；LinkerSysId 的 $R$ 数字不一致；Isaac Gym 关节摩擦语义；FOC 文档丢失的 §三 标题；L25 丝杠型式三处说法不一（统一为"待核实"）。
- 结构重构：九篇统一为"位置 → 读完能回答 → 编号章节 → 回扣与承接 → 对开发与科研的启示"骨架，贯穿 L25 一根手指的例子。
- 新增知识面：气隙剪应力律、$K_v$ 换算、连续/峰值力矩热限、丝杠三兄弟与自锁判据、多级折返减速箱、惯量匹配最优减速比、直线电缸+连杆第五路线、串级环带宽分离、延迟预算、固件/通信/量化层 gap、Actuator Net 路线。
- 同步修正 Foundation：[[Actuation#7.1 四条传动路线|Actuation §7.1]] 代表手表与 §7.2 L25 `armature` 数值。
