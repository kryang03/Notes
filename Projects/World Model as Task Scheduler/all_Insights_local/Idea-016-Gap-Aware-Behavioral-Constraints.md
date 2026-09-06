---
tags: [insight, sim2real, in-hand, LinkerHand, behavioral-constraint, RSS]
aliases: [Gap-Aware Behavioral Constraints, GABC, Transfer-by-Avoidance]
created: 2026-09-03
status: proposal-review
feasibility: B+
novelty: B (as stated) → A- (if reframed as "gap-map → constraint" + cross-hand validation)
target-venue: RSS 2027
related:
  - "[[Transmission2JointDynamics_gap]]"
  - "[[report_2026-09_thumb_stiction]]"
  - "[[Idea-013-Stick-Slip-Mode-Switching]]"
  - "[[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]]"
  - "[[Learning Human-like Finger Gaiting on an Anthropomorphic Hand]]"
---

# Idea-016: Reality-Gap-Aware Behavioral Constraints（用行为归纳偏置"躲开" gap）

> [!abstract] 核心假设（用户 2026-09-03 提出）
> Sim-to-Real gap 的大小由**策略的物理交互行为模式**决定，而非任务宏观目标。在仿真中对策略施加强物理归纳偏置（准静态、stick-only、串行换指、指腹接触、TWS 引导），可诱导出主动躲避真实世界未建模非线性的保守策略，实现 zero/low-shot 迁移。丝杠灵巧手 L25 只是第一个实例任务。

## 1. 调研结论：novelty 定位

**理论支点已有**：simulation lemma（Kearns & Singh 1998；Lobel 2024 最优紧界）把 sim-real 价值差界定为 $\gamma L_V \cdot \mathbb{E}_{(s,a)\sim d^\pi}[W(P_{real}(\cdot|s,a),P_{sim}(\cdot|s,a))]$——误差按**策略自己的访问分布**加权。所以"gap 依赖策略行为"在理论上是**已知的**，但把它变成**可操作的策略设计原则并在灵巧手上受控验证**，目前没有一篇做全。

**最近邻（必须在 related work 正面处理）**：
| 工作 | 已做 | 我们的 Delta |
|---|---|---|
| Khandate et al. ICRA 2022 (2109.12720) / RSS 2023 (2303.03486) | 把 finger gaiting 限制在 precision grasp、用 stable-grasp 状态集约束探索，仅本体+触觉 sim2real | 他们的约束是**为探索**，我们的约束**为 gap**；他们没做"行为模式↔gap 大小"的因果实验 |
| Chen, Lu, Colgate, Lynch 2026 (2607.12105) | grasp-quality prior 作 dense reward + 指尖曲率机械先验，声称助 sim2real | 与 TWS 引导重叠；他们只有单一先验、单一手，没有 gap 归因 |
| DexScrew (Hsieh…Qi 2025, 2512.02011) | 用简化物体模型让"正确 gait 涌现"，再真机 BC | 隐含同一哲学（简化 sim 逼出可迁移行为）但没有显式行为约束 |
| SCORE (2606.27475) | 把 sim 内 RL 限制在真实数据策略的 support 内，防止 exploit 接触失配 | 同一哲学的**数据驱动版**；我们是**物理驱动版**，不需真实数据 |
| CAPS (2012.06644) / Grad-CAPS (2407.04315) / LipsNet | 动作平滑正则 | 只覆盖"准静态/限幅"一项，且不区分接触模式 |
| DexNDM (2510.08556) | 关节级 real2sim 残差补偿 | 正交（改 sim/改动作 vs 改行为），是最强 baseline 与可叠加组件 |
| Actuator Reality Shaping (2607.02205) | 用 2-DoF 控制器把真机执行器整形成 sim 参考模型 | 反方向（改真机），高减速比伺服实验，可作对照哲学 |
| Closing the Reality Gap (Zhao 2026, 2601.02778) | 电流→力矩标定 + 执行器非理想效应随机化，五指手零样本 | 传统"提高保真"路线的最新最强代表 |

**结论**：按现稿写（"一堆保守约束 + 一只丝杠手"）novelty 约 B，审稿人会说"这是工程 recipe，每条约束都有人做过"。要到 RSS 水准，故事要升级为：

> **Transfer by Avoidance**：先测出 sim-real **分歧图**（gap map：哪些 (s,a) 区域 sim 与 real 不一致），再把它翻译成一族**物理可解释的行为约束**，让策略的访问分布 $d^\pi$ 落在"sim-real 一致集"内。约束不是"保守"，而是"绕开已知的不一致区"。

## 2. 最尖锐的反例（来自本库自己的数据）
[[report_2026-09_thumb_stiction]]：拇指 MCP 库仑死区 $d_C\approx12$ mrad（≈1.7 LSB），$F_S/F_C\approx4$，且 Stribeck 让**低速段**摩擦最大。→ "准静态 + 小步 Δaction" 会让命令长期落在死区内、换向时卡死——**慢反而更糟**。正确的约束是"避免换向 / 单调分段运动 / 最小步长高于死区"，而非"慢"。这正好证明：**约束必须从 gap map 推导，不能凭'保守'直觉**——这是论文最有力的论证。

## 3. 约束族与其对应的未建模物理（论文主表雏形）
| 行为约束 | 躲开的物理不一致 | sim 中的测量量（privileged） | 真机可验证量 |
|---|---|---|---|
| Stick-only（切向滑移≈0，纯滚动） | 摩擦系数/锥形状/软指扭转摩擦误差 | 接触点相对切向速度 | 指腹触觉剪切/滑移检测 |
| 串行换指（≥N-1 指保持力闭合） | 冲击/多接触同时切换时求解器误差 | 接触 make/break 事件计数 | 触觉接触事件 |
| 避免换向 + 最小步长（非"慢"） | 丝杠 stiction 死区、Stribeck、量化阶梯 | 命令速度过零次数、Δq 与 $d_C$ 之比 | 编码器停滞时长 |
| 加速度/jerk 限幅 | 惯量/执行器带宽误差 | $\ddot q$、末端加速度 | 本体 |
| 指腹接触 | 传感器覆盖不足 → 不可观测 | 接触位置 | 触觉 |
| TWS/抓取品质引导 | 抓取裕度对摩擦误差的敏感度 | $\epsilon$-metric / GWS | — |

## 4. 实验必须验证的
E1 因果实验：同任务同速度上限，只改行为约束 → sim2real drop 与"行为统计量"相关；同时做 sim-to-sim（喂入已辨识 stiction 模型的 MuJoCo 作 "伪真机"）作廉价代理。
E2 跨手验证：L25（丝杠）+ 一只直驱手（LEAP/Allegro）；预测：换向约束对 L25 关键、对直驱手弱；接触切换约束对两者都关键。
E3 baselines：重 DR；real2sim（把本库辨识的 $F_C,F_S,\rho,T_f$ 喂入 sim）；DexNDM 残差；CAPS；以及叠加组合——证明互补而非替代。
E4 代价曲线：约束强度扫 → 成功率 vs 完成时间 Pareto，回答"牺牲多少灵巧度买多少 gap"。
E5 真机行为核验：策略在真机是否真的停留在约束区（滑移、换向次数、死区停滞）。
E6 长时程与鲁棒：多物体、多腕姿态、扰动、time-to-fall。

## 5. 需注意
- 可行性：stick-only + 滚动 + 串行换指下任务是否可达？需用 Montana 接触运动学论证滚动可达性（曲率决定），三指力闭合裕度小。
- 约束用 privileged 量定义，部署时不需要，但要在真机验证行为不漂移。
- MuJoCo 摩擦锥：pyramidal 各向异性；软指 condim=4/6；硅胶指套的扭转摩擦。
- 位置环饱和 → 本体不可感知力，"指腹接触"约束应表述为"约束到可观测区"。
- "策略 hack 物理"要有证据：列出被利用的仿真漏洞（穿透力、时间步级 chatter、锥各向异性）。

## 6. 参考文献
见本文件同名回复（2026-09-03 会话）；核心：Khandate 2022/2023、Chen-Lynch 2026、DexScrew、SCORE、CAPS/Grad-CAPS、DexNDM、Actuator Reality Shaping、Zhao 2026、Beyond Binary、DexCtrl、OmniReset、Lin 2025 humanoid、Visual Dexterity、Dextreme、HORA、Spin Pens、AnyRotate、Pang & Tedrake 2023、Hou & Mason、Morgan 2022、Hwangbo 2019、Reality Gap survey 2510.20808、Simulation Lemma (Lobel 2024)。
