---
tags:
  - paper
  - tactile-sensing
  - sim-to-real
  - manipulation
  - contact-geometry
aliases:
  - Tacmap
paper-year: 2026
read-date: 2026-03-13
venue: arXiv
paper-pdf: "[[Papers/Tacmap- Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map.pdf]]"
related:
  - "[[ContactMechanics]]"
  - "[[SignalProcessing]]"
  - "[[ComputationalGeometry]]"
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
---

# Tacmap: Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map

> [!abstract] 核心贡献
> Tacmap 提出一种面向 vision-based tactile sensors (VBTS) 的统一触觉 sim-to-real 表征：不在仿真中复刻复杂光学图像，也不做昂贵 FEM，而是在传感器表面法线方向计算 rigid object 与 elastomer 的 volumetric penetration depth，形成 deform map；真实端通过自动化 3 轴压入台采集 raw tactile image 与几何 ground-truth depth map 的配对数据，训练 Image→Deform translator，使仿真和真实都落到同一个“接触几何公共空间”，并在 SharpaWave dexterous hand 的球体 in-hand rotation 中展示 simulation-trained PPO policy 的 zero-shot deployment。

> [!tip] 与理论基础的关联
> - [[ContactMechanics]] — deform map 是法向穿透量 $\delta(u,v)$ 的空间化近似，捕获接触流形的几何形状，但不显式建模切向剪切。
> - [[ComputationalGeometry]] — 核心运算是沿曲面法线的 ray-mesh intersection；normal-projection space 让曲面指尖不再被平面投影扭曲。
> - [[SignalProcessing]] — 真实端的 raw tactile image → deform map 是从光学伪影恢复接触几何的逆问题。
> - [[ReinforcementLearning]] — Tacmap 解决的是 tactile observation state gap；它给 PPO 提供 sim/real 对齐的触觉观测，而不是改变 RL 算法本身。
> - [[ControlTheory]] — 对灵巧手控制，Tacmap 提供接触几何反馈；若要处理滑移和摩擦调节，还需要切向力/剪切场。
>
> **核心技术**: Penetration Depth Map, Vision-Based Tactile Simulation, Normal-Aligned Ray Casting, Common Geometric Space, Tactile Sim-to-Real, In-Hand Rotation

## 0. 阅读定位与范本价值

Tacmap 是触觉 sim-to-real 里很值得放进知识库的一篇，因为它把问题从“如何生成逼真的触觉图片”重新表述成：

> 策略真正需要对齐的是接触几何，而不是传感器内部光照、反射和相机噪声。

这和 STOLA 的位置互补：

- STOLA 关心触觉如何进入 language reasoning；
- Tacmap 关心触觉如何进入 robot policy 的 sim-to-real observation space。

对 WMTS / LinkerHand / 转笔，Tacmap 的启发是：触觉观测最好先被投影到某个**物理不变量空间**，再进入 world model 或 policy。原始 tactile image / raw taxel reading 往往是传感器特定的；penetration map / contact geometry / slip field 这类中间量才更可能跨 sim-real 保持一致。

最低标准映射：

| 四支柱 | 本文 recap 的落点 | 必须抓住的判断 |
|---|---|---|
| 逻辑与价值 | §1, §4 | 论文的 value add 是“用 deform map 对齐 sim/real 触觉几何”，不是“更像真的触觉渲染” |
| 原理与理论 | §2 | 从双曲面 $S_s,S_u$、法线射线、交点深度 $z_s,z_u,z_o$ 推导 $d(u,v)$ |
| 实验与验证 | §3 | Table I 几何/力一致性 + 16→8192 env scaling + zero-shot in-hand rotation，但成功率报告不充分 |
| 未来与结合 | §5-§7 | 对转笔必须补 tangential shear/slip；对非 VBTS 的 LinkerHand 要改成 taxel→contact-geometry translator |

## 1. 问题设定与动机

### 1.1 一句话核心

Tacmap 用 penetration depth map 作为仿真和真实触觉的共同几何语言，从而绕开原始触觉图像的传感器特定光学复杂性，并保持足够高的计算效率用于大规模 RL。

### 1.2 直观隐喻

视觉触觉传感器像不同相机拍同一个压痕：每台相机的灯光、镜头、反射、噪声都不同，但物体压入软表面的“地形高度图”本身应该是一致的。Tacmap 不试图复刻每台相机看到的照片，而是让仿真和真实都翻译成同一张地形图。

这个隐喻的关键边界是：地形图主要描述法向凹陷，不描述表面被横向拖拽的剪切纹理。因此它对 normal contact geometry 很强，对 incipient slip 仍不完整。

### 1.3 现有方法的局限

| 方法类别 | 代表 | 注入了什么先验 | 关键局限 |
|---|---|---|---|
| empirical / image translation | Taxim | 用真实数据学习触觉图像外观 | 依赖标定分布，novel geometry 泛化弱 |
| analytical shader / depth rendering | TACTO | 用快速深度/光照近似触觉 imprint | 几何/弹性物理简化，曲面指尖投影畸变明显 |
| GPU spring-damper tactile simulation | TacSL | tensorized depth-to-RGB，高并行 | elastomer 局部细节和体积保持有限 |
| physics-based soft body | TacEx / Taccel | GIPC/IPC/ABD 等高保真软体接触 | 计算重，难以成为大规模 RL 内循环 |
| raw tactile image sim-to-real | 直接渲染或域适应图像 | 保留传感器外观 | 策略会看到光学伪影，而不是稳定接触几何 |

### 1.4 Delta 分析

Tacmap 的 Delta 有三层：

| 层次 | Tacmap 的做法 | 为什么重要 |
|---|---|---|
| 表征层 | 用 deform map $M$ 作为 sim/real 公共空间 | 不需要模拟真实传感器内部光学，只对齐接触几何 |
| 几何层 | 在曲面法线方向做 penetration depth ray casting | 支持 curved tactile fingertips，避免 flat-surface projection artifacts |
| 系统层 | 集成 Isaac Lab / MuJoCo，GPU ray-casting 支持 parallel RL | 保持比 FEM 更适合大规模 PPO 的吞吐 |

这篇论文讲故事最强的地方，是它把 fidelity 和 efficiency 的矛盾换了一个坐标系：不是“光学越逼真越好”，而是“对策略有用且 sim/real 一致的几何量越稳定越好”。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 空间/类型 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $F$ | net force vector/scalar summary | sim contact sensor / real force regressor | real regressor 有梯度 | 全局接触力状态 | 论文只说 ResNet-based regression，未给具体 loss/网络细节 |
| $P$ | contact position | sim contact sensor / real deform centroid | 否或由 translator 间接影响 | 接触位置粗定位 | 真实端 $P$ 来自 predicted deform map 的有效区域质心 |
| $M$ | $\mathbb R^{H\times W}$ deform map | sim ray casting / real translator | translator 有梯度 | dense penetration depth field | Tacmap 的核心公共几何空间 |
| $S_u$ | undeformed sensor surface | sensor geometry | 否 | elastomer resting surface | 不是外部 sensing boundary |
| $S_s$ | virtual sensing surface | sensor geometry | 否 | 位于传感器外侧的虚拟边界，包住 interaction zone | paper 中说与 $S_u$ almost the same one，容易误读 |
| $r_{u,v}$ | ray | grid point + surface normal | 否 | 从 $S_s$ 沿法线投向 sensor interior | 法线空间投射，不是相机 pinhole projection |
| $z_s$ | scalar coordinate | sensing surface ray origin | 否 | ray 上 $S_s$ 的坐标 | 坐标方向由局部法线参数化决定 |
| $z_u$ | scalar coordinate | undeformed surface | 否 | ray 上 $S_u$ 的坐标 | 表示未变形边界 |
| $z_o$ | scalar coordinate | ray-object first intersection | 否 | object mesh 与 ray 的第一个交点 | 若无交点或不在有效区，最终由 max/clamp 处理 |
| $d(u,v)$ | nonnegative scalar | geometric computation | 否 | 第 $(u,v)$ 点的 penetration depth | 只建模法向穿透，不建模切向剪切 |
| $I_{\mathrm{raw}}$ | raw tactile image | real VBTS observation | 否 | 真实传感器图像 | sensor-specific optical artifacts 很强 |
| $\Phi$ | image-to-deform translator | supervised training | 是 | raw image 到 deform map 的映射 | 每类传感器/硬件可能要重新标定 |
| $T_{\mathrm{tool}}$ | 3D pose | 3-axis motion stage encoder | 否 | 真实压入工具相对传感器位姿 | 用于生成几何 ground truth，不是策略输入 |

### 2.2 三流触觉信息：为什么 deform map 是核心

Tacmap 给机器人提供三类触觉流：

| Stream | Simulation 获取 | Real-world 获取 | 信息类型 |
|---|---|---|---|
| Net force $F$ | physics engine contact sensors | raw tactile image + external force sensor 标注训练 ResNet regressor | 全局接触强度 |
| Contact position $P$ | engine reported contact position | predicted deform map 有效区域几何质心 | 接触点粗定位 |
| Deform map $M$ | ray-cast penetration depth | $\hat M=\Phi(I_{\mathrm{raw}})$ | 高分辨率局部接触几何 |

$F$ 和 $P$ 是低维摘要，能告诉策略“有多大力、在哪里接触”。$M$ 则告诉策略“接触区域长什么形状、哪里压得深、边界如何变化”。对 in-hand rotation 这种需要连续调整指尖接触的任务，$M$ 是最接近局部接触流形的信息。

### 2.3 仿真端 deform map 从零推导

Tacmap 不把传感器看成平面图像，而是定义两个曲面：

- $S_u$：undeformed sensor surface，真实 elastomer 未变形时的物理表面；
- $S_s$：virtual sensing surface，位于传感器外侧固定 offset 的虚拟边界。

这两个曲面之间形成一个 interaction zone。将 $S_s$ 离散为 $H\times W$ grid。对每个 grid point $(u,v)$，沿该点的 surface normal 向 sensor interior 投射 ray：

$$
r_{u,v}.
$$

在这条 ray 上定义三个坐标：

| 坐标 | 含义 |
|---|---|
| $z_s$ | ray 在 sensing surface $S_s$ 的起点坐标 |
| $z_u$ | ray 与 undeformed surface $S_u$ 对应的边界坐标 |
| $z_o$ | ray 与 object mesh $O$ 的 first intersection coordinate |

如果物体没有进入 sensing surface 和 undeformed surface 之间，penetration 应为 0。若物体进入该区间，深度应反映 object 相对虚拟感知面压入了多少。论文公式为：

$$
d(u,v)
=
\max(0,\ z_s-\max(z_u,z_o)).
$$

这个公式的结构有三层：

1. $\max(z_u,z_o)$ 选择有效边界：不能把未变形表面之外的无效区域当成 deformation；
2. $z_s-\max(z_u,z_o)$ 计算从 virtual sensing surface 到有效交点/边界之间的 depth；
3. 外层 $\max(0,\cdot)$ 保证无接触时 depth 非负截断为 0。

最终：

$$
M[u,v]=d(u,v),
\qquad
M\in\mathbb R_{\ge0}^{H\times W}.
$$

关键 insight：对 curved fingertips，ray 是沿每个局部表面法线，而不是沿固定相机轴或平面 z 轴。这就是 Tacmap 相对平面深度渲染的结构性优势。

### 2.4 真实端 Image→Deform 的监督来自哪里

真实传感器没有直接输出 $M$，只有 raw tactile image：

$$
I_{\mathrm{raw}}.
$$

Tacmap 搭建 automated hardware-in-the-loop data collection system：

1. 用 high-precision 3-axis motion stage 控制 geometric indenters 压入传感器；
2. 记录 indenter 的精确 3D pose $T_{\mathrm{tool}}$；
3. 用与仿真端相同的几何投影逻辑，根据已知 indenter mesh 和 pose 计算 ground-truth deform map $M_{\mathrm{gt}}$；
4. 得到同步数据集：

$$
\mathcal D
=
\{(I_{\mathrm{raw}}^{(i)},M_{\mathrm{gt}}^{(i)})\}_{i=1}^{N}.
$$

训练 translator：

$$
\hat M
=
\Phi(I_{\mathrm{raw}}).
$$

论文写明采用 ResNet-based encoder-decoder，训练目标是 pixel-wise mean squared error：

$$
\min_\Phi
\sum_i
\|\Phi(I_{\mathrm{raw}}^{(i)})-M_{\mathrm{gt}}^{(i)}\|_2^2.
$$

注意：旧稿中写的 IoU loss、10K 样本、Adam/lr/100 epochs 等细节在 PDF 主文没有证据，不能当作论文事实。

### 2.5 为什么这是 sim-to-real 对齐

令仿真端 deform map 为：

$$
M_{\mathrm{sim}}=G_{\mathrm{ray}}(S_s,S_u,O),
$$

真实端为：

$$
M_{\mathrm{real}}=\Phi(I_{\mathrm{raw}}).
$$

Tacmap 的核心假设是：

$$
M_{\mathrm{sim}}
\ \text{and}\
M_{\mathrm{real}}
$$

都锚定到同一个物理量：penetration depth。因此策略训练时看到的 $M$ 不依赖仿真渲染器是否复刻了真实传感器的内部反射和光照。

这不是说 raw image domain gap 消失了，而是 domain gap 被隔离到 $\Phi$ 这个 translator 中。策略只看 common geometric space。

### 2.6 实现机制：为什么能用于大规模 RL

Tacmap 集成到 Isaac Lab 和 MuJoCo：

| 环节 | Isaac Lab | MuJoCo |
|---|---|---|
| Ray query | high-performance Raycaster API | dedicated toolkit using `mj_ray` |
| Sensing grid | dense tactile sensing points + directions | 同样基于 sensor geometry |
| Resolution decoupling | tactile sensing resolution 与 physics collision mesh 解耦 | 避免为了触觉分辨率强行加密物理网格 |
| Runtime | GPU-accelerated ray-casting in vectorized pipeline | efficient penetration depth query |

这个实现判断很重要：它不是 FEM，因此不会为每个 elastomer element 做软体求解；也不是纯 shader，因此保留了 object-sensor geometry intersection 的物理意义。

## 3. 训练、数据与实验

### 3.1 实验问题与平台

论文实验回答三个问题：

| Research question | 对应实验 |
|---|---|
| Sim-to-real fidelity | cylinder/square indenters 下 force alignment + deform map visualization + Table I |
| Computational efficiency | Isaac Lab 中 parallel environments 从 16 scaling 到 8192，记录 GPU memory 和 rendering speed |
| Task effectiveness | SharpaWave dexterous hand 上 in-hand ball rotation，simulation PPO zero-shot real deployment |

硬件平台：

| 项 | 设置 |
|---|---|
| Dexterous hand | SharpaWave dexterous hand |
| Tactile sensors | vision-based tactile fingertips / DTC |
| Real evaluation object | spherical object for in-hand rotation |
| Policy algorithm | PPO |
| Training domain | simulation only |
| Real deployment | no real-world fine-tuning / no domain adaptation |

### 3.2 Table I：sim/real 几何一致性

Table I 报告 diverse contact scenarios 的 median values：

| Object | Contact Position Error | Deform Depth Error | Net Force L2 Error | Deform IoU |
|---|---:|---:|---:|---:|
| Square | 0.66 mm | 18.53% | 0.28 N | 88.21% |
| Cylinder | 0.96 mm | 14.71% | 0.61 N | 85.67% |

因果解释：

- Contact position error 小于 1 mm，说明 predicted deform map 的有效区域质心与真实/仿真接触位置高度一致。
- Deform IoU 85-88%，说明接触区域形状高度重叠；这比只看 force 更能证明 geometry alignment。
- Force L2 error 在 0.28N / 0.61N，说明 penetration depth 作为几何代理也能带来全局力趋势相关性。
- Square 和 Cylinder 都表现较好，说明 Tacmap 不只是对单一平面/圆形接触有效。

这张表支撑的是“common geometric space 足够一致”，不是证明所有动态接触都准确。它主要是标准压入测试，不是高速滑移/滚动。

### 3.3 Computational efficiency：证据边界

论文 Figure 6 做了两个 scaling 检查：

1. GPU memory usage 随 parallel environments 从 16 增加到 8192；
2. simulation rendering speed with / without Tacmap。

论文结论：

- ray-casting 方法让 memory footprint near-linear growth；
- 即使 thousands of concurrent environments，仍保持 reasonable rendering frequency；
- inclusion of Tacmap has negligible degradation of overall simulation speed；
- 可在 single consumer-grade GPU 上支持 large-scale tactile RL。

这里没有给出精确数值表，因此 recap 不应伪造 FPS 或 memory 数字。正确的写法是：Fig. 6 支持 scaling trend，而非给出可复用的绝对吞吐 benchmark。

### 3.4 Zero-shot in-hand rotation

Tacmap 用 PPO 在仿真中训练 in-hand object rotation：

$$
\pi_\theta(a_t|o_t),
\qquad
o_t \supset M_t.
$$

观测包含实时 Tacmap stream，给策略 dense geometric information about the contact manifold。策略在仿真中经历 millions of diverse contact interactions，然后直接部署到真实 SharpaWave hand，无真实微调和域适应。

论文展示的结论：real-world tactile images 经 $\Phi$ 转成 deform maps 后，simulation-trained policy 能完成 spherical object 的 smooth continuous rotation。

Critical reading：

- 这是强证据，因为任务是 contact-rich in-hand rotation；
- 但论文没有报告多次 trials 的成功率、角速度、持续时间、失败率或 object variation；
- 因此它证明 feasibility / mechanism plausibility，不足以单独证明 broad robustness。

### 3.5 实验因果链

| 证据 | 观察 | 支撑的机制 | 边界 |
|---|---|---|---|
| Table I contact position | Square 0.66mm, Cylinder 0.96mm | real $\Phi(I)$ 与 sim ray-cast 的接触几何对齐 | 标准压入，不是高速动态 |
| Table I Deform IoU | 88.21%, 85.67% | deform map 捕获接触区域形状 | IoU 不含切向剪切 |
| Force comparison Fig. 4 | sim force 与 real estimated force highly correlated | penetration depth 是 force dynamics 的有用 proxy | 不是完整 contact mechanics |
| Fig. 6 scaling | 16→8192 env near-linear memory | ray casting 适合 RL 内循环 | 无具体 FPS 表 |
| zero-shot rotation | sim PPO → real SharpaWave ball rotation | common geometric space 降低 observation gap | 缺系统成功率统计 |

## 4. 核心洞见

### 4.1 Tacmap 的真正 insight

Tacmap 的 insight 是：

$$
\text{tactile sim-to-real}
\neq
\text{photo-realistic tactile image simulation}.
$$

更可迁移的路线是：

$$
I_{\mathrm{raw}}
\rightarrow
\text{contact geometry}
\leftarrow
\text{simulation geometry}.
$$

仿真端直接从几何计算 $M_{\mathrm{sim}}$；真实端学习 $\Phi(I_{\mathrm{raw}})$ 得到 $M_{\mathrm{real}}$；策略只在 $M$ 空间工作。

### 4.2 为什么 normal-projection space 重要

很多触觉 simulator 隐含 flat sensor 假设：把接触投到一个平面 depth buffer 上。对拟人灵巧手，指尖通常是曲面，这会导致：

- 边缘区域投影拉伸；
- contact patch 形状失真；
- 不同传感器曲率下同一接触产生不同伪几何；
- sim-trained policy 在真实 curved fingertip 上看到不同 observation。

Tacmap 沿每个 sensing point 的 local surface normal 计算 penetration depth，所以表示绑定到传感器自身曲面，而不是外部平面。

### 4.3 最需要保留的批判

Tacmap 解决的是**法向几何对齐**，不是完整触觉物理。对转笔/高速滚动，以下变量非常关键：

$$
f_t,\quad \tau_{\mathrm{shear}},\quad \dot s,\quad \mu,\quad \mathrm{stick/slip}.
$$

论文 discussion 也明确说当前版本不显式建模 tangential force distribution / shear strain，而这些正是 predicting incipient slip 所必需的。因此 Tacmap 是很好的基础，但不能单独承担全部触觉 sim-to-real。

## 5. 替代方案与理论局限

### 5.1 理论维度

Tacmap 的 $d(u,v)$ 可以理解为空间化的法向 penetration：

$$
\delta
\rightarrow
\delta(u,v).
$$

在 Hertz 接触里，法向力和穿透量有非线性关系：

$$
F_n
=
\frac{4}{3}E^*\sqrt{R^*}\delta^{3/2}.
$$

Tacmap 没有显式使用 Hertz 模型，但它选择 $d(u,v)$ 作为 contact geometry proxy，隐含假设是：对 policy 来说，局部 penetration field 足以反映关键法向接触状态。

失效边界：当任务瓶颈是切向摩擦、微滑、材料粘弹性、传感器滞后时，仅靠 $d(u,v)$ 不够。

### 5.2 算法维度

| 局限 | 影响 | 可能补法 |
|---|---|---|
| 只建模 normal penetration | incipient slip / tangential shear 弱 | 增加 2D shear displacement field 或 tactile optical flow |
| Image→Deform 每传感器标定 | 换硬件需重新采集配对数据 | 学 sensor-conditioned translator 或物理光学参数 |
| ray-casting 依赖 mesh | object mesh 复杂时 latency 上升 | BVH / SDF query / cached distance fields |
| real translator 是 supervised | 标定台覆盖不足会造成 extrapolation error | active calibration + uncertainty estimation |
| zero-shot 结果任务单一 | 泛化到多物体/动态操作未知 | 多物体、多速度、多材质 benchmark |

### 5.3 工程/实验维度

- 没有报告 in-hand rotation 的成功率分布、trial 数、持续时间和失败案例。
- Table I 只包含 square/cylinder 两类标准 indenter 的 median 指标。
- 真实端依赖 automated motion stage 和已知 tool pose；这是强标定条件。
- 如果真实部署物体 mesh 不准，sim deform map 与 real deform map 的“共同几何”也会偏。

## 6. 对用户研究的启发

### 6.1 对 LinkerHand / WMTS 的直接迁移

Tacmap 对 WMTS 的最佳位置是 tactile observation alignment：

$$
\text{sim contact geometry}
\leftrightarrow
\text{real tactile observation}
\rightarrow
\text{shared contact latent}
\rightarrow
\text{PPO / world model / diffusion policy}.
$$

若 LinkerHand 使用的是非 VBTS 的 tactile tensor，而不是 GelSight 类图像，迁移方式应改成：

| Tacmap 元件 | LinkerHand 对应物 | 修改 |
|---|---|---|
| raw tactile image $I_{\mathrm{raw}}$ | taxel pressure / multi-channel tactile tensor | 用 taxel encoder 替代 ResNet image encoder |
| deform map $M$ | contact pressure/penetration latent map | 用标定压入或仿真生成 ground-truth contact geometry |
| normal ray-casting | fingertip mesh + object mesh contact query | 按 LinkerHand 指尖几何定义 sensing points/normals |
| PPO observation stream | tactile-contact latent | 接入 PPO Oracle、ensemble world model、DP denoiser |

关键不是复用 Tacmap 的代码，而是复用它的原则：**不要让策略直接吃传感器特定读数，先转成 sim/real 共享的接触几何空间。**

### 6.2 对转笔任务的必要扩展

转笔不是静态压入任务，它需要处理：

- stick → slip → rolling → recontact 的快速模式切换；
- 笔的细长曲面与指腹曲面的线/点接触；
- 切向速度和摩擦锥约束；
- 执行器延迟导致的接触错位。

因此 Tacmap-style observation 至少应扩展为：

$$
h_t
=
\left[
d_t(u,v),
\ \Delta_{\mathrm{shear},t}(u,v),
\ \dot d_t(u,v),
\ c_t(u,v),
\ u_{\mathrm{contact},t}
\right],
$$

其中 $d_t$ 是法向 penetration，$\Delta_{\mathrm{shear}}$ 是切向位移或触觉光流，$\dot d_t$ 是接触变化速度，$c_t$ 是 contact mask，$u_{\mathrm{contact}}$ 是接触相位/模式 latent。

### 6.3 可验证实验建议

| 实验 | 设计 | 证伪条件 |
|---|---|---|
| raw tactile vs contact map | PPO/DP 分别使用 raw tactile、Tacmap-style map、force+position | contact map 不提升 sim-to-real 或降低稳定性 |
| normal-only vs normal+shear | 转笔中加入 shear/tactile flow | normal-only 与 full 一样好，说明任务不需要切向信息 |
| translator uncertainty | 训练 ensemble $\Phi_k(I)$，用 disagreement 预测触觉 OOD | disagreement 与失败无关，则 translator 不适合作 safety signal |
| mesh fidelity ablation | 物体 mesh 精度高/低对 sim-to-real 影响 | mesh 不准也不影响，说明 policy 可能没用到几何细节 |
| multi-object zero-shot | 球体之外加入笔、柱体、偏心物体 | 只在球体成功，泛化不足 |

### 6.4 与 WMTS pipeline 的结合

| WMTS 模块 | Tacmap-style 作用 |
|---|---|
| latent task generation | 生成不同 contact geometry / slip / regrasp tasks |
| PPO Oracle | 用 shared contact map 训练 tactile-aware policy |
| Diffusion/Flow generalist | 把 contact map history 作为 denoising condition |
| Ensemble World Model | 预测下一步 contact map 与 uncertainty |
| real-robot fine-tuning | 通过 $\Phi(I_{\mathrm{real}})$ 对齐真实触觉，减少 observation gap |

最关键的 project insight：Tacmap 可以成为 WMTS 中 “world model 预测触觉接触状态” 的 observation language。世界模型不应只预测 $q,\dot q$ 和 object pose，还应预测 $M_{t+1}$ 或 contact latent。

## 7. 与知识体系的联系

### 7.1 与 [[ContactMechanics]] 的联系

Tacmap 的 $d(u,v)$ 是法向穿透量的二维场。它和 Hertz contact 的 $\delta$ 同源，但论文没有把 $d$ 转成严格压力分布或力学闭式解。应把它看作 contact geometry proxy，而不是完整 contact model。

### 7.2 与 [[ComputationalGeometry]] 的联系

Tacmap 的核心是 ray-mesh intersection 和局部法线坐标。它与 SDF 表征相邻：对 sensor surface point $\mathbf p(u,v)$，若有 object signed distance $\phi_O$，可以把 penetration 直观理解为负 SDF 的截断形式：

$$
d(u,v)\sim \max(0,-\phi_O(\mathbf p(u,v))).
$$

但论文实现采用 ray-casting 而不是直接 SDF 查询。

### 7.3 与 [[SignalProcessing]] 的联系

真实端 $\Phi(I_{\mathrm{raw}})$ 是触觉信号处理的逆问题：从光学图像中恢复几何变形。它比直接做 image-domain adaptation 更物理，因为目标空间是 penetration depth，而不是另一种图像风格。

### 7.4 与 [[ReinforcementLearning]] 的联系

Tacmap 解决的是 MDP 中 observation function 的 sim-to-real gap：

$$
o_t^{\mathrm{sim}}
=
h(s_t,\xi_{\mathrm{sim}}),
\qquad
o_t^{\mathrm{real}}
=
h(s_t,\xi_{\mathrm{real}}).
$$

Tacmap 试图构造新的 observation：

$$
\tilde o_t=M_t,
$$

使得 sim/real 的 $\tilde o_t$ 在相同接触状态下更一致。PPO 仍是 PPO；变的是 policy 所见状态。

### 7.5 与 [[ControlTheory]] 的联系

接触几何对控制的价值在于决定何时增大/减小法向力、何时切换手指、何时触发 regrasp。Tacmap 当前缺少切向剪切，因此对 slip-aware impedance control 还不够，但它给了法向接触分布这个关键输入。

### 7.6 簇内定位与暗线锚点（触觉操作簇）

在“触觉表征丰富度谱”上，Tacmap 位于**稠密接触几何**这一档：不复刻光学图像，而对齐 penetration depth map $M$。它与 AnyRotate 同属“物理中间表征优先”同盟。

| 簇内对照 | Delta（本文相对它） |
|---|---|
| [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] | 同盟（AnyRotate §7.4 已点名 Tacmap）：AnyRotate 选低维稀疏 $(R_x,R_y,\|F\|)$（可解释），Tacmap 选稠密 penetration map $M$（几何细节）。都在找 gap-invariant observation subspace；且都用 CNN 从触觉图预测中间量（AnyRotate 预测 $(P,F)$，Tacmap 预测 $M$）。 |
| [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] | 反向路径解同一 tactile sim-to-real gap：Touch Dexterity 用 threshold **截断**连续力进 binary，Tacmap 沿法线 ray-cast **恢复**接触几何。二值丢幅值，deform map 丢切向。 |
| [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding]] | 互补：Tacmap 给 sim/real 对齐的触觉 **observation**，CGP 给 executable contact **target**。Tacmap 供输入，CGP 供输出。 |

**精确 Foundation 锚点（把 §7.1/§7.2 的泛链落实）**：

- [[ContactMechanics#4.2 软指模型：接触斑与扭转摩擦|ContactMechanics §4.2]]：deform map $d(u,v)$ 是 §4.2 软指接触斑的空间化，但缺其中的 torsional/切向摩擦——正是它对转笔/滚动的空缺。
- [[ComputationalGeometry#4. 有向距离场 (SDF)：连续优化的基石|ComputationalGeometry §4]]：$d(u,v)\sim\max(0,-\phi_O(\mathbf p(u,v)))$ 是截断的负 SDF，与 §4 SDF 表征相邻（论文以 ray-casting 实现该量）。

**暗线挂载（认知不确定性当护栏 + POMDP observation 对齐）**：Tacmap 的本质是把 MDP observation function 的 sim/real 版本对齐到同一 $M$（$o^{\text{sim}}_t,o^{\text{real}}_t\to\tilde o_t=M_t$），使 belief 输入一致，见 [[ReinforcementLearning#2.1 MDP 与 POMDP：把"试错"写成数学|ReinforcementLearning §2.1]]。§6.3 建议的 ensemble $\Phi_k(I)$ 用 disagreement 预测触觉 OOD 当 safety signal，即认知不确定性护栏。

---

## 8. 应主动追问的颗粒度

| 用户式追问 | recap 应主动补充 |
|---|---|
| “Tacmap 相对 TACTO 的核心差别是什么？” | 不是渲染更漂亮，而是沿曲面法线计算 penetration depth，支持 curved fingertips |
| “真实端 ground truth deform map 怎么来？” | 3-axis motion stage 记录 tool pose，用同一几何投影逻辑生成 $M_{\mathrm{gt}}$ |
| “Table I 证明了什么？” | 接触位置 <1mm、Deform IoU 85-88%，证明几何公共空间一致，但不证明高速滑移 |
| “Zero-shot 证据够强吗？” | 证明 feasibility；但缺 trial success rate/object diversity，不能过度外推 |
| “对转笔怎么用？” | normal penetration map 是基础，还必须加入 shear/slip/contact-mode temporal field |

## References

- Su, L. et al. **Tacmap: Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map**. arXiv:2602.21625, 2026.
- [[STOLA - Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning]]
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]]
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]]
- [[Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture]]
- [[ContactMechanics]]
- [[SignalProcessing]]
- [[ComputationalGeometry]]
- [[ReinforcementLearning]]
- [[ControlTheory]]
