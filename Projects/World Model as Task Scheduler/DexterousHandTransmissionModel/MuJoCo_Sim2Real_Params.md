---
tags: [MuJoCo, mjlab, Sim2Real, Solver, Friction, Contact, L25_Hand, WMTS]
aliases: [MuJoCo 求解器参数, solimp solref impratio, mjlab sim2real 参数]
date: 2026-09-02
related:
  - "[[Transmission2JointDynamics_gap]]"
  - "[[Actuator2RigidDynamicsModel_gap]]"
  - "[[ContactMechanics]]"
  - "[[LinkerSysId]]"
  - "[[Dynamics]]"
---

# MuJoCo / mjlab 求解器参数与 sim2real

> [!abstract] 本篇在链路中的位置
> 链路 `电机 → FOC → 传动 → 关节力矩 → 刚体+接触` 的**最后一格：引擎参数落地**。
> 上一篇 [[Transmission2JointDynamics_gap]] 已经从真机数据拟出了 $F_S / F_C / k_d / I_a$ 这些**物理量**，
> [[LinkerSysId]] 给了 `armature` 的 CAD 折算 worked example；本篇回答的是：**这些物理量写进 MJCF 之后，
> 求解器真的按物理意义执行了吗？** 答案是"默认参数下不会"，而且踩坑的方式很隐蔽。
> 理论根源在 [[Dynamics#6.2 凸优化流派（MuJoCo）：放弃硬约束|Dynamics §6.2]] 与
> [[ContactMechanics#5.3 凸优化范式（MuJoCo）与位置层（XPBD）|ContactMechanics §5.3]]：MuJoCo 的约束是**软的、被正则化的**，
> 而"软到什么程度"由本篇讲的 `solref` / `solimp` 决定。

> [!tip] 读完你应该能回答
> 1. 为什么 `frictionloss=0.193` 写对了、`nefc` 里也多了一行摩擦约束，关节却仍然像"弱阻尼"而不像"干摩擦"？唯一有用的旋钮是哪个数？
> 2. `solimp` 的 $d$ 从 0.9 抬到 0.9999，约束刚度到底变了多少倍？为什么"相对刚度"对 $d$ 是高度非线性的？
> 3. `impratio` 与 `cone` 各自管接触的哪个方向？"策略靠滑动驱动物体"这个观察，多大程度上是求解器正则化的产物？
> 4. 为什么 CAD 折算的 `armature` 一旦写对，阻尼就**必须**从显式 PD 挪进关节 `damping` 字段？两者为什么是绑定的？
> 5. 拿到一份新的 MJCF，30 秒内怎么验证"关节摩擦真的饱和了"？

> [!example] 没打开过 MJCF 的人怎么读本篇
> - **MJCF** 是 MuJoCo 的 XML 模型格式。一个 `<joint>` 元素描述一个关节自由度（DoF），本篇反复出现的
>   `armature` / `damping` / `frictionloss` / `solreffriction` / `solimpfriction` 全是它的属性——分别是
>   折算转子惯量（kg·m²）、粘滞阻尼（N·m·s/rad）、库仑摩擦力矩（N·m）、以及后两个"求解器怎么执行这条摩擦"的参数。
> - **`<option>`** 是模型的全局设置元素：物理步长 `timestep`（s）、积分器 `integrator`、摩擦锥类型 `cone`、
>   法向/切向阻抗比 `impratio`、求解器 `solver` 与迭代次数——一份模型只有一个 `<option>`，作用于所有关节和接触。
> - **约束行 (constraint row)**：MuJoCo 每个物理步先把"当前有哪些东西不能随便动"列成一张表，**每行一个标量约束**：
>   一个接触点贡献 1 行法向 + 若干行切向；一个 `frictionloss>0` 的关节贡献 1 行；一个到限位的关节贡献 1 行。
>   求解器对这张表统一求解，得到每行的约束力 `efc_force`；行数就是 `nefc`。本篇的核心观点就是：**所有行用同一套
>   `solref`/`solimp` 语法配软硬**，所以摩擦和接触是一个坑的两面。
> - **mjlab**：本项目使用的 RL 训练框架，基于 **MuJoCo Warp**（MuJoCo 的 GPU 批量并行版，`mujoco_warp`）构建，
>   API 风格接近 Isaac Lab（`num_envs` 批量、逐 env 写模型字段）——§8.1 提到的 `set_dof_physical_props` /
>   `expand_model_fields` 就是它的接口（框架来源与版本待核实，以项目代码为准）。本篇所有约束公式在
>   `mujoco` C 版、`mjx`（JAX 版）、`mujoco_warp` 三个实现里一致，已逐条与官方源码/文档核对。

> [!abstract] 核心命题
> MuJoCo 把**接触、关节限位、关节摩擦**全部当成同一种东西——**约束**，用同一组
> `solref` / `solimp` 参数化。所以「摩擦锥调不准」和「关节摩擦不起作用」是同一套
> 机理的两个表现，必须放在一起理解。
>
> 本文给出这套参数的精确定义、它们各自作用在哪、以及 L25NS 上实测踩过的两个坑：
> **默认 `solimp` 会让 `frictionloss` 退化成弱阻尼**（实测差 1110 倍），
> **默认 `impratio` 会让接触在摩擦锥内蠕变**（实测接触保持 $\kappa$ 0.74 vs 0.96）。

---

## 一、统一框架：所有约束都落在 $(k,b,d)$ 三个量上

**为什么先讲这个**：后面每一节（摩擦、接触、impratio）都是同一组公式在不同 $pos$ 取值下的特例；不先把公式立起来，"摩擦为什么退化成阻尼"就只能靠记结论。

每一行约束（一个接触方向、一个关节摩擦、一个关节限位）在求解前都会算出三个量：刚度 $k$、阻尼 $b$、阻抗 $d$。
下面是 MuJoCo 源码里的原式（`mjx/_src/constraint.py::_kbi`、`mujoco_warp/_src/constraint.py::_efc_row`；已核对官方文档与源码）。
符号：`timeconst`（s）与 `dampratio`（无量纲）来自 `solref`；$d_{\min}, d_{\max}$、`width`（约束违约量的长度尺度，m 或 rad）、`mid`、`power` 来自 `solimp`；$pos$ 是违约量（接触=穿透深度 m，限位=越界角 rad）：

$$k=\frac{1}{d_{\max}^2\,\text{timeconst}^2\,\text{dampratio}^2},\qquad
b=\frac{2}{d_{\max}\,\text{timeconst}}$$

$$d=\underbrace{d_{\min}+\text{imp}_y\cdot(d_{\max}-d_{\min})}_{\text{随违约量 }|pos|\text{ 变的 sigmoid}},\qquad
\text{imp}_x=\frac{|pos|}{\text{width}}$$

然后是**真正进求解器的两个量**：

$$\boxed{D=\frac{1}{\text{invweight}\cdot\dfrac{1-d}{d}}},\qquad
\boxed{a_{\rm ref}=-k\,d\,pos-b\,\text{vel}}$$

- **$D$ 是这一行约束的「有效刚度」**（源码里先算正则化项 $R=\text{invweight}\cdot\frac{1-d}{d}$，再取 $D=1/R$；已核对）。
  注意 $\frac{1-d}{d}$：$d\to1$ 时它趋于 0，$D\to\infty$。
  **约束的刚硬程度对 $d$ 是高度非线性的**——这是全文最要紧的一句话。
  这个 $R$ 正是 [[Dynamics#6.2 凸优化流派（MuJoCo）：放弃硬约束|Dynamics §6.2]] 讲的"放弃硬约束"的代价项：
  MuJoCo 不解互补条件，而是在凸目标里加 $\tfrac12 f^\top R f$ 让问题严格凸、有唯一解；$R$ 越大，约束越"软"。
- $a_{\rm ref}$ 是约束想把系统推向的参考加速度（已核对：$a_{\rm ref}=-b\,\text{vel}-k\,d\,pos$）。
- `invweight` 是该自由度的等效逆惯量（关节行 $\approx1/I_a$，接触行为两 body 逆质量之和），**所以同一组 solimp 在不同惯量的
  关节上给出的实际刚度不同**——这也是为什么 `armature`（§七）改了之后摩擦行的软硬会跟着变。

| $d$ | $\frac{1-d}{d}$ | 相对刚度（$D\propto\frac{d}{1-d}$，同一 invweight 下） |
|---:|---:|---:|
| 0.9（默认） | 0.1111 | 1× |
| 0.99 | 0.0101 | 11× |
| 0.999 | 0.0010 | 111× |
| **0.9999** | **0.0001** | **1111×** |

（算术已复核：$0.1111/0.010101=11.0$，$0.1111/0.001001=111.0$，$0.1111/0.00010001=1111.0$；MuJoCo 把 $d$ 夹在 `mjMINIMP`=0.0001 与 `mjMAXIMP`=0.9999 之间，所以 0.9999 已是能写的上限，再大等于没写。）

---

## 二、`solref = (timeconst, dampratio)`：约束的时间尺度

把约束想成一个二阶系统：违约量以 `timeconst` 为时间常数、`dampratio` 为阻尼比被推回零。

**为什么现在讲这个**：§一的 $k,b$ 两个量全部由 `solref` 决定，先把它的语义与安全钳位说清，§三讲 `solimp` 时才不会把两者的作用混在一起。

- 默认 `(0.02, 1)`：20 ms 临界阻尼（已核对官方文档）。
- **`timeconst` 被强制 $\ge2\times$ timestep**（`refsafe` 标志，默认开启；源码 `timeconst = max(timeconst, 2*timestep)`），写更小的值无效。
  官方原话：*"The timeconst parameter should be at least two times larger than the simulation time step, otherwise the system can become too stiff relative to the numerical integrator."*（已核对官方文档）
- 负值为**直接格式**：`solref = (-stiffness, -damping)`。注意它**并不绕过阻抗缩放**——源码里仍是
  $k=\dfrac{-\text{solref}[0]}{d_{\max}^2}$、$b=\dfrac{-\text{solref}[1]}{d_{\max}}$（已核对源码 `_kbi`）。官方文档明确写直接格式是**系统辨识的推荐格式**，因为 stiffness/damping 可以直接对上你拟出的物理量。

> [!important] 对**摩擦**约束，`solref` 只剩半条命
> 关节摩擦与 elliptic 锥的切向摩擦，其**位置违约恒为零**（$pos\equiv0$）。代入 $a_{\rm ref}$：
> $$a_{\rm ref}=-k\,d\cdot0-b\,\text{vel}=-b\,\text{vel}$$
> **刚度项整个消失，`dampratio` 被忽略**，只剩 $b=2/(d_{\max}\cdot\text{timeconst})$ 在起作用。
> 官方文档原话（已核对，逐字）：*"Friction loss constraints (in joints and tendons) and friction dimensions of elliptic
> contact cones have zero position violation: r ≡ 0. … The impedance is always d₀ (solimp[0]), since d(r) is evaluated at r=0.
> In the standard solref format, the time constant controls exponential velocity decay. The damping ratio is ignored."*
> 文档还补了一句常被忽略的：*"d_width (solimp[1]) still affects the damping b as a scaling denominator, even though it does not
> affect the impedance."*——即 `solimp` 的第二个数（$d_{\max}$）通过 $b$ 影响摩擦行的**速度衰减时间尺度**，但不影响它的**软硬**（$D$）。

---

## 三、`solimp = (dmin, dmax, width, mid, power)`：阻抗，即「能生成多大力」

**为什么现在讲这个**：§一说了刚度 $D$ 对 $d$ 高度非线性，$d$ 就由 `solimp` 决定；本节把五个数的语义讲清，然后用一个单自由度探针证明"默认值下摩擦根本没饱和"。

阻抗 $d\in[0,1]$ 决定约束的出力能力：0 = 完全不约束，1 = 完全刚性（已核对官方文档；默认 `solimp="0.9 0.95 0.001 0.5 2"`）。五个数定义了
$d$ 随违约量 $|pos|$ 变化的 S 形曲线：

- `dmin`：**零违约处**的阻抗
- `dmax`：违约达到 `width` 及以上时的阻抗
- `width`：过渡区宽度
- `mid`, `power`：S 形的中点与幂次

**对接触**：刚碰上（穿透 ≈ 0）时软（$d=d_{\min}$），压深了变硬（$d\to d_{\max}$）。
这个 softening zone 让接触可微、不弹飞。

> [!danger] 对**摩擦**：$d$ 恒等于 `dmin`，与 `dmax` 无关
> 摩擦约束 $pos\equiv0\Rightarrow\text{imp}_x=0\Rightarrow\text{imp}_y=0\Rightarrow d=d_{\min}$（已核对源码：`imp = dmin + imp_y*(dmax-dmin)`，$\text{imp}_x=0$ 时 $\text{imp}_y=0$）。
> **所以调关节摩擦的软硬，唯一有用的旋钮是 `solimp` 的第一个数。**
> 后三个数（width / mid / power）在摩擦上完全不起作用。
>
> **修正**（原文把 `dmax` 的影响写成"二阶效应"，不准确）：`dmax` 通过 $b=2/(d_{\max}\text{timeconst})$ 决定摩擦行的
> **速度衰减速率**——对摩擦行来说 $a_{\rm ref}=-b\,\text{vel}$ 是**唯一**的驱动项，谈不上"二阶"。
> 准确的说法是：`dmax` 管"多快把速度拉向零"，`dmin` 管"能顶住多大力"（$D$）。§3.1 的坑是**后者**——
> 力顶不住、随外力线性增长——所以对"饱和不饱和"这个问题，`dmax` 确实无关，而 `dmin` 是全部。

### 3.1 实测：默认 `solimp` 让 `frictionloss` 退化成弱阻尼

单自由度探针（`thumb_mcp` 参数：$I_a=2.84\times10^{-4}$，`frictionloss`$=0.193$ N·m，
$k_d=1.668$）。施加**恒定力矩 2 s**，看关节漂多远：

| `solimpfriction` | $\tau=0.10$（$<F_C$，应当不动） | $\tau=0.30$（$>F_C$，应走 128 mrad） |
|---|---:|---:|
| `0.9 0.95 …`（默认） | **89.11 mrad** ❌ | 269.08 mrad ❌ |
| `0.99 0.999 …` | 25.86 mrad ❌ | 128.29 mrad ✅ |
| **`0.9999 0.99999 …`** | **0.33 mrad** ✅ | **128.29 mrad** ✅ |

约束力同步：默认下只顶住 0.0244 N·m（该顶住 0.10），`0.9999` 下顶住 0.0997。

**为什么会这样（把 §一公式代进来，不跳步）**：求解器里 `frictionloss` 行的判据是（`mjx/_src/solver.py`，已核对）
$$\text{饱和}\iff |J a - a_{\rm ref}|\ \ge\ r\,f,\qquad r=\frac1D=\text{invweight}\cdot\frac{1-d}{d}$$
即只有当"约束空间加速度残差"超过 $r f$ 时，摩擦力才被钳在 $\pm f$；残差在 $\pm rf$ 之内时，摩擦力是**线性的** $-D\cdot(\text{残差})$——
这就是弱阻尼。$d=0.9$ 时 $r$ 比 $d=0.9999$ 大 1111 倍，线性区宽 1111 倍，所以 $\tau=0.10<f$ 的力矩根本到不了饱和区。

> [!success] 结论
> **`frictionloss` 要真的表现为「饱和的干摩擦」而不是「弱阻尼」，必须把
> `solimpfriction` 的第一个数抬到 0.9999。** 默认值下它只顶住约 1/4 的力矩，
> 且力随外力线性增长——那不是摩擦，那是阻尼。
>
> 这个坑很隐蔽：模型能跑、`nefc` 里确实多了一行摩擦约束、`frictionloss` 的值也读得出来，
> 只是**力从来没饱和过**。

### 3.2 怎么验证参数真的生效了

不要看轨迹像不像，做这个 30 秒的探针：

1. 单自由度、零重力、关节 `frictionloss = f`；
2. 施加恒定力矩 $\tau=0.5f$，跑 2 s → **位移应当 < 1 mrad**；
3. 施加 $\tau=1.5f$ → **终速应当精确等于 $(\tau-f)/k_d$**。

两条都对了，摩擦才算建对。任何一条不对，先查 `solimp[0]`。

---

## 四、`impratio`：法向与切向的阻抗比

**为什么现在讲这个**：§三讲的是关节内部的摩擦行；接触的**切向**行是同一种"$pos\equiv0$ 的摩擦约束"，只是它的软硬不单独给 `solimp`，而是用一个比值挂在法向上。

$$\text{impratio}=\frac{d_{\text{切向}}}{d_{\text{法向}}}$$

官方定义（已核对 XML reference）：*ratio of frictional-to-normal constraint impedance*；实现上它进入切向行的 `invweight` 分母（切向 invweight 被除以 impratio，等效于把切向 $R$ 缩小、$D$ 放大）。
官方明确：**只对 elliptic 摩擦锥推荐**——pyramidal 锥把法向和切向混在同一组基向量里，高 impratio 不建议。默认 `impratio=1` 时切向约束与法向一样软，后果是
**锥内蠕变**：接触点在摩擦锥内部（本该完全粘着）仍然持续微动，因为切向约束的
正则化柔度 $r=1/D$ 不为零。

这与 §3 那段「摩擦是被正则化的」是**同一个机理**，只是发生在接触的切向而非关节内部。

**L25NS 实测**：切到 `cone=elliptic` + `impratio=10` 后，接触保持指标 $\kappa$
从 **0.74 升到 0.96**，代价是仿真吞吐 **−12%**。

> [!warning] 一条被这个默认值坑过的结论
> 此前认为「策略靠滑动来驱动物体」——**那主要是求解器的正则化产物，不是策略学到的物理**。
> 任何关于「滑动份额」「接触稳定性」的结论，都必须先固定 `cone` 与 `impratio` 再谈。

---

## 五、`cone`：pyramidal 还是 elliptic

**为什么现在讲这个**：§四的 `impratio` 只在 elliptic 下有意义，所以必须知道两种锥各自是什么、默认为什么是 pyramidal。

| | pyramidal（默认） | elliptic |
|---|---|---|
| 原理 | 把摩擦锥用一组基向量 $n\pm\mu t_i$ 张成的金字塔近似 | 真正的二阶锥 $\|f_t\|\le\mu f_n$ |
| 优点 | 约束集是**线性**的（各基向量系数非负），求解更便宜 | 物理准确、各向同性 |
| 缺点 | 各向异性：**沿对角方向有效摩擦系数只有 $\mu/\sqrt2$**（见下方修正） | 略慢（L25NS 实测 −12% 吞吐） |
| 官方建议 | 性能优先时用 | **抑制接触滑移时用** |

> [!warning] 修正：原文"对角方向摩擦偏大 $\sqrt2$ 倍"方向反了
> 官方文档（已核对）：*"The scaling by the friction coefficients ensures that all basis vectors lie within the elliptic
> friction cone we are approximating."*——金字塔**内切**于圆锥，不是外接。推导：两条相邻棱 $n+\mu t_1$、$n+\mu t_2$
> 以权重 $\lambda_1,\lambda_2\ge0$ 合成，法向力 $f_n=\lambda_1+\lambda_2$，切向力 $\|f_t\|=\mu\sqrt{\lambda_1^2+\lambda_2^2}\le\mu f_n$，
> 沿对角（$\lambda_1=\lambda_2$）取等号时 $\|f_t\|=\mu f_n/\sqrt2$。所以 pyramidal 在对角方向**低估**摩擦、更容易滑，
> 与"pyramidal 更易滑移"的官方结论一致。
>
> 另一处修正：原文写 pyramidal"是 LCP"。MuJoCo 的两种锥**都是凸优化**（Gauss 原理 + 正则化，见
> [[ContactMechanics#5.3 凸优化范式（MuJoCo）与位置层（XPBD）|ContactMechanics §5.3]]），区别只在约束集是线性不等式还是二阶锥；
> LCP 是 [[Dynamics#6.1 LCP 流派|Dynamics §6.1]] 那条路线（PhysX/Bullet 等），MuJoCo 恰恰是放弃了它。

官方原文（已核对，逐字）：*"Elliptic cones correspond more closely to physical reality. However pyramidal cones can improve the
performance of the algorithms."* 以及 *"When contact slip is a problem, the best way to suppress it is to use elliptic cones,
large impratio, and the Newton algorithm with very small tolerance."*

**抑制滑移的推荐组合**：`cone=elliptic` + 高 `impratio` + Newton 求解器 + 很小的 tolerance。
`noslip_iterations` 是最后手段：官方描述（已核对）它是一个**后处理步**——主求解器收敛后，只对摩擦维度用 $R=0$（硬约束）
再做一轮 PGS 扫描；能压住软约束固有的滑移，但文档明言它是 *ad-hoc* 机制，多接触复杂场景下**可能引入不稳定**。
实测能把摩擦顶死，但它不进主求解，所以不建议当默认配置。

---

## 六、关节摩擦 vs 接触摩擦：分工，以及为什么不能互相顶

**为什么现在讲这个**：§三与 §四/§五分别把两种摩擦调对了，但标定时它们会在同一个指标上互相掩盖，先定顺序。

| | 关节摩擦 | 接触摩擦 |
|---|---|---|
| 物理位置 | 传动内部（丝杠、减速箱、轴承） | 指面与物体之间 |
| 量纲 | N·m | 无量纲系数 $\mu$ |
| MuJoCo 表达 | `frictionloss`（DOF 约束行） | `friction` + 摩擦锥 |
| 与接触的关系 | **无关**，空载也存在 | 只在接触时存在 |
| 调它影响什么 | 换向死区、跟随误差 | 物体滑不滑 |

**两者物理独立，但在「物体拿不拿得住」这个指标上会互相掩盖。**
关节摩擦调大了，手指更「僵」，物体也更不容易被蹭掉——看起来像接触摩擦够了。
所以标定顺序必须是：**先空载定关节摩擦（§三的探针），再带载定接触摩擦。**

---

## 七、`armature` 与 `damping`：放哪里决定了能不能跑

**为什么现在讲这个**：§一说过摩擦行的软硬还乘着 `invweight`$\approx1/I_a$，而 $I_a$ 主要就是 `armature`；它写错，前面调好的一切都跟着偏。

### 7.1 `armature`

以对角阵注入质量矩阵（已核对源码：`M(i,i)` 初始化为 `dof_armature[i]`，再叠加刚体项）：

$$\big(M(q)+\mathrm{diag}(a)\big)\ddot q+C\dot q+G=\tau$$

它有两重身份：**物理上**是折算转子惯量（$a=kJ_{rotor}N_{eq}^2$，推导与 L25 数值见 [[LinkerSysId]]，
减速比平方折算的原理见 [[Actuation#7.2 Reflected Inertia：为什么减速比是把双刃剑|Actuation §7.2]]）；**数值上**是 Tikhonov
正则化，强迫质量矩阵对角占优。正因为第二重身份，它极易被当成「调大点更稳」的旋钮
而偏离物理值——而**自由空间看不出来**（只影响测量带外的快极点），**接触时直接错**
（碰撞冲量 $\propto I_a$）。

**取 CAD 折算值，不要当旋钮。** 不稳就降子步或降 $k_p$。

### 7.2 阻尼必须放进关节的 `damping` 字段，不要走显式 PD 力矩

显式积分的阻尼有稳定性上界 $k_d h/I_a<2$。推导（单自由度，忽略其它力）：显式 Euler 对 $I_a\dot v=-k_d v$ 给出
$v_{n+1}=v_n\,(1-k_d h/I_a)$，$|1-k_d h/I_a|<1\iff 0<k_d h/I_a<2$；超过 2 则每步符号翻转且幅值放大。
这里的"显式"指 PD 力矩在 Python 侧按上一步速度算好、作为外力写进引擎（mjlab 的 actuator/`qfrc_applied` 路径）——
引擎对这种外力**不知道它依赖速度**，只能显式处理。L25NS 拇指用 CAD 的 armature：

$$\frac{k_d h}{I_a}=\frac{1.668\times0.005}{2.84\times10^{-4}}=\mathbf{29.4}\gg2$$

**实测确实发散**（关节幅值涨到命令的 40~120 倍）。把 $k_d$ 写进关节 `damping`、
用 `integrator="implicitfast"` 隐式积分之后立刻稳定。

补充（已核对官方文档）：关节 `damping` 字段即使在默认 `Euler` 积分器下也是**隐式**积分的（`eulerdamp` 标志，
默认开启：把 $h\,k_d$ 加到质量矩阵对角再求解），所以"写进 `damping` 字段"本身就是稳定性的来源；`implicitfast`
的额外价值是把**其它**速度相关力（执行器阻尼、流体力等）也隐式化，且不含 Coriolis 导数项、开销接近 Euler——
对本项目取 `implicitfast` 是稳妥选择，但不必把"稳定"归功于它。

> [!danger] 这个不稳定性曾被错误的 armature 掩盖
> 之前表里拇指 armature 被抬高 37 倍，于是 $k_dh/I_a=0.80<2$，显式 PD 侥幸稳定。
> **换回物理正确的 armature，就必须同时把阻尼改成隐式**——两处改动是绑定的。

---

### 7.3 推广：**任何**速度相关的阻力都必须走 `dof_damping`

§7.2 说的是线性 $k_d$。这条规则比它宽——**只要一项阻力对速度有非零雅可比，
显式发它就受同一个稳定性上界夹住**：

$$\left|\frac{\partial\tau}{\partial\dot q}\right|\cdot\frac{h}{I_a}<2$$

以二次阻尼 $\tau=k_{d2}\dot q|\dot q|$ 为例，$\partial\tau/\partial\dot q=2k_{d2}|\dot q|$。
L25NS 拇指实测标定出 $k_{d2}\approx3.1$，在 $\dot q=0.5$ rad/s 时

$$\frac{2\times3.1\times0.5\times0.005}{2.84\times10^{-4}}=54.6\gg2$$

**实测确实炸**：半迟滞从 13~87 mrad 跳到 200~290 mrad。

**做法**：把非线性阻力折成「随当前速度变的等效线性阻尼」，每个物理步写进关节字段：

```python
# 二次阻尼：k_d(v) = k_d,lin + k_d2·|v|，交给 implicitfast 隐式积分
m.dof_damping[jnt] = kd_lin + kd2 * abs(d.qvel[jnt])
```

改完之后同一组参数在 **63 倍速度跨度**（0.008~0.5 rad/s）内把稳态迟滞复现到真机的 7% 以内。

> [!important] 这与 §3 的 `frictionloss` 改写是同一套手法
> **凡是能表达成「随状态变的模型字段」的，就不要发显式力矩。**
> 摩擦改写 `dof_frictionloss`、速度相关阻力改写 `dof_damping`——
> 两者都留在隐式求解器里，都不吃稳定性预算。
> 显式力矩只留给**对速度雅可比为零**的项（例如与速度无关的常值补偿）。

## 八、L25NS 取值表

**为什么现在讲这个**：前七节每节定了一个旋钮，这里把它们合成一份可直接粘贴的 MJCF 片段，并给每个值的出处。

```xml
<option timestep="0.005" integrator="implicitfast"
        cone="elliptic" impratio="10" solver="Newton" iterations="100"/>
...
<joint name="thumb_mcp" type="hinge"
       armature="0.000284"                        <!-- CAD 折算，不当旋钮 -->
       damping="1.668"                            <!-- k_d，隐式积分 -->
       frictionloss="0.193"                       <!-- = F_C = k_p·d_C -->
       solreffriction="0.005 1"                   <!-- = 一个物理步 -->
       solimpfriction="0.9999 0.99999 0.001 0.5 2"/>  <!-- 第一个数是关键 -->
```

| 参数 | 值 | 作用对象 | 取值理由 |
|---|---|---|---|
| `cone` | `elliptic` | 接触 | 抑制锥内蠕变 |
| `impratio` | 10 | 接触 | $\kappa$ 0.74→0.96，吞吐 −12% |
| `integrator` | `implicitfast` | 全局 | 隐式积分关节 damping |
| `armature` | CAD 折算 | 关节 | $kJ_{rotor}N_{eq}^2$ |
| `damping` | $k_d(v)=k_{d,\rm lin}+k_{d2}|v|$ | 关节 | 显式走 PD 会发散（§7.2、§7.3）；L25NS 拇指 $k_{d2}\approx3.1$ |
| `frictionloss` | $F_C=k_pd_C$ | 关节 | 换向死区 |
| `solreffriction[0]` | ≈ 一个物理步 | 关节摩擦 | 影响小，取小即可 |
| **`solimpfriction[0]`** | **0.9999** | 关节摩擦 | **默认 0.9 会让它退化成弱阻尼** |

### 8.1 $F_S\ne F_C$ 怎么在引擎里表达

`frictionloss` 只有**一个**标量，没有静 / 动之分。做法是**每个物理步按当前速度改写它**：

$$f(t)=F_C+(F_S-F_C)\,e^{-(v/v_S)^2}$$

粘着时 $v\to0$，$f\to F_S$（起动阈值高）；滑动时 $f\to F_C$。
**全程留在隐式求解器里，不加任何显式摩擦力矩，因此没有稳定性预算问题。**

mjlab 侧逐 env 写值走 `MjDexHandBaseEnv.set_dof_physical_props(friction=...)`
（内部先 `expand_model_fields(("dof_frictionloss",))` 再写 `[num_envs, num_dofs]`）。

> [!important] $v_S$ 要按**控制步能分辨的速度**取，不是按物理直觉取
> 实测 $v_S=0.003$ rad/s 时 $F_S$ 几乎不起作用（平台 0.75 s），
> 取 $v_S=0.02$ rad/s 才充分 engage（平台 0.90 s）。
> 原因：粘着相在正则化求解器里不是绝对静止，$v_S$ 太小则 $g(v)$ 来不及升到 $F_S$。

---

## 九、检查清单

跑任何 sim2real 结论之前逐条过：

1. **关节摩擦真的饱和了吗？** §3.2 的恒定力矩探针，两条判据。
2. **`solimpfriction[0]` ≥ 0.9999 吗？** 默认 0.9 差 1111 倍。
3. **`cone=elliptic` + `impratio`≥10 吗？** 否则接触结论里混着求解器蠕变。
4. **`armature` 是 CAD 值还是被调过的？** 自由空间看不出来，接触时直接错。
5. **阻尼在关节字段还是在显式 PD 里？** CAD armature 下后者会发散。
   **非线性阻力（二次阻尼等）同样适用**——判据是 $|\partial\tau/\partial\dot q|\cdot h/I_a<2$（§7.3）。
6. **`timeconst` 有没有被 REFSAFE 顶到 $2h$？** 写了更小的值等于没写。
7. **仿真与真机比之前，量化口径统一了吗？** 真机是 8-bit 反馈，仿真是连续的；
   不吸附到同一张栅格就比，等于拿量化过的真机比没量化的仿真（量化与延迟预算见 [[Actuator2RigidDynamicsModel_gap]]）。

---

## 回扣与承接

用 L25 的一根手指把本篇串一遍：**空心杯电机 → 丝杠电缸 → 连杆 → 关节**（拇指多一级 17:1 折返减速箱）。

1. 电机转子惯量 $J_{rotor}$ 经丝杠与连杆折算成关节侧 $I_a=kJ_{rotor}N_{eq}^2$（[[LinkerSysId]]）——它进 MJCF 的 `armature`（§7.1），
   同时决定了这个关节所有约束行的 `invweight`$\approx1/I_a$（§一）。
2. 丝杠与减速箱的库仑摩擦，从真机换向死区拟出 $F_C=k_pd_C$、$F_S$（[[Transmission2JointDynamics_gap]]）——进 `frictionloss`（§三），
   $F_S\ne F_C$ 用逐步改写实现（§8.1）。但**默认 `solimpfriction[0]=0.9` 下它永远不饱和**，必须抬到 0.9999。
3. 关节粘滞项 $k_d$ 进 `damping` 字段而不是显式 PD，否则 CAD 正确的 $I_a$ 会让 $k_dh/I_a=29.4$ 发散（§7.2）。
4. 指面碰到物体后，切向约束行与关节摩擦行是同一套 $pos\equiv0$ 的软约束；`cone=elliptic`+`impratio=10` 把切向蠕变压下去（§四/§五），
   $\kappa$ 从 0.74 到 0.96。
5. 全部写完后，跑 §3.2 探针与 §九清单，再谈任何 sim2real 结论。

**这一段的暗线**：MuJoCo 用**一个**正则化项 $R=\text{invweight}\cdot\frac{1-d}{d}$ 换来了凸性与可微性
（[[Dynamics#6.2 凸优化流派（MuJoCo）：放弃硬约束|Dynamics §6.2]]），代价是每一条约束——摩擦、接触、限位——都天然"软"。
策略在这种软约束里学到的滑动、蠕变、换向行为，一部分是求解器伪影而非物理
（[[Dynamics#6.4 仿真伪影：策略学到的是真物理还是 bug？|Dynamics §6.4]]）；本篇的全部工作就是把这部分伪影压到低于真机噪声。

**下一篇去哪**：
- 整条链路的 gap 总图与分流 → `sim2real.md`（主 Agent 的阅读地图 `DexterousHand_Tutorial_Map.md`）。
- 引擎参数之外、PD 没覆盖的残差怎么用数据学 → [[Actuation#10.1 Actuator Net：学"仿真 PD 没覆盖的那段残差"|Actuation §10.1]]。
- 域随机化时哪些参数该随机、哪些（如 `solimp`）绝不能随机 → [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|ReinforcementLearning §9]]。

## 对开发与科研的启示

1. **开发**：把 §九清单做成 CI——加载任何 MJCF 后自动跑 §3.2 的两条探针（$\tau=0.5f$ 位移 <1 mrad；$\tau=1.5f$ 终速 $=(\tau-f)/k_d$），
   不通过就拒绝训练。这意味着下一步可以把 `verify_mjlab_stiction.py` 从手动脚本变成 mjlab env 的启动断言。
2. **开发**：域随机化只随机**物理量**（`frictionloss`、`damping`、`armature` 在 CAD 值 ±20% 内、接触 $\mu$），
   **固定**求解器量（`solimp`、`solref`、`impratio`、`cone`）。随机后者等于随机"引擎错得多厉害"，策略学到的鲁棒性是对 bug 的鲁棒性。
3. **科研**：§四的观察——"策略靠滑动驱动物体"曾是求解器产物——意味着已发表工作里关于 in-hand 滑动份额的结论
   可能依赖 `cone`/`impratio` 默认值。一个可做的 idea：在 WMTS 的世界模型里把接触**显式建成 elliptic 软约束**（含 $d$），
   让 WM 的物理先验与训练引擎一致，而不是学一个黑盒接触残差。
4. **科研**：直接格式 `solref=(-k,-b)` 是官方推荐的系统辨识格式（§二）。可以把 [[Transmission2JointDynamics_gap]] 拟出的 $F_S/F_C/k_d$
   与接触实验的 $k,b$ 一起做成一个**可微的参数辨识回路**（MJX/Warp 都可微），用真机换向数据直接反推 `solref`，而不是手调。
