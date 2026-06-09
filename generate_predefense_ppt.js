const pptxgen = require("/Users/lishishun/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "OpenAI Codex";
pptx.company = "Zhejiang University";
pptx.subject = "博士学位论文预答辩";
pptx.title = "考虑铸造缩孔的直通式阀体承压性能研究及其高应力区晶粒强化";
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: "Microsoft YaHei",
  bodyFontFace: "Microsoft YaHei",
  lang: "zh-CN",
};

const C = {
  navy: "163A5F",
  blue: "2E5B87",
  teal: "1F8A8A",
  green: "2E8B57",
  orange: "D97A2B",
  red: "B94A48",
  gold: "E3B23C",
  ink: "243447",
  gray: "5F6B7A",
  line: "D7DEE7",
  pale: "F6F8FB",
  white: "FFFFFF",
  sky: "EAF2FA",
};

const title = "考虑铸造缩孔的直通式阀体承压性能研究及其高应力区晶粒强化";
const author = "叶宗豪";
const advisors = "指导教师：金志江  钱锦远";
const meta = "浙江大学 能源工程学院 | 能源动力 | 特种阀门创新设计";

const IMG = {
  gating: "/tmp/thesis_ppt_assets/image98.png",
  stressA: "/tmp/thesis_ppt_assets/image173.png",
  stressB: "/tmp/thesis_ppt_assets/image174.png",
  stressC: "/tmp/thesis_ppt_assets/image183.png",
  nucleation: "/tmp/thesis_ppt_assets/image218.png",
  cafeFlow: "/tmp/thesis_ppt_assets/image275.png",
  micro: "/tmp/thesis_ppt_assets/image298.png",
  thermocouple: "/tmp/thesis_ppt_assets/image332.png",
  rt: "/tmp/thesis_ppt_assets/image368.png",
  oilBath: "/tmp/thesis_ppt_assets/image290.png",
};

function addBg(slide) {
  slide.background = { color: C.white };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 13.333, h: 0.28,
    line: { color: C.navy, transparency: 100 },
    fill: { color: C.navy },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 0.6, y: 7.12, w: 12.1, h: 0,
    line: { color: C.line, pt: 1.2 },
  });
}

function addHeader(slide, titleText, subtitle = "") {
  addBg(slide);
  slide.addText(titleText, {
    x: 0.7, y: 0.45, w: 8.6, h: 0.45,
    fontSize: 24,
    bold: true,
    color: C.navy,
    margin: 0,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.72, y: 0.92, w: 9.8, h: 0.2,
      fontSize: 9.5,
      color: C.gray,
      margin: 0,
    });
  }
}

function addFooter(slide, idx) {
  slide.addText("博士学位论文预答辩", {
    x: 0.72, y: 7.15, w: 2.3, h: 0.18,
    fontSize: 8,
    color: C.gray,
    margin: 0,
  });
  slide.addText(String(idx), {
    x: 12.15, y: 7.12, w: 0.45, h: 0.2,
    align: "right",
    fontSize: 8.5,
    color: C.gray,
    margin: 0,
  });
}

function addTag(slide, text, x, y, w, color) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h: 0.33,
    rectRadius: 0.04,
    line: { color, transparency: 100 },
    fill: { color, transparency: 6 },
  });
  slide.addText(text, {
    x: x + 0.06, y: y + 0.05, w: w - 0.12, h: 0.18,
    fontSize: 9.3,
    bold: true,
    color: C.white,
    align: "center",
    margin: 0,
  });
}

function addCard(slide, cfg) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x: cfg.x, y: cfg.y, w: cfg.w, h: cfg.h,
    rectRadius: 0.04,
    line: { color: cfg.line ?? C.line, pt: 1 },
    fill: { color: cfg.fill ?? C.white },
    shadow: { type: "outer", color: "CBD5E1", blur: 1, angle: 45, distance: 1, opacity: 0.12 },
  });
  if (cfg.title) {
    slide.addText(cfg.title, {
      x: cfg.x + 0.16, y: cfg.y + 0.12, w: cfg.w - 0.32, h: 0.28,
      fontSize: cfg.titleSize ?? 14.5,
      bold: true,
      color: cfg.titleColor ?? C.navy,
      margin: 0,
      fit: "shrink",
    });
  }
  if (cfg.body) {
    slide.addText(cfg.body, {
      x: cfg.x + 0.16, y: cfg.y + 0.43, w: cfg.w - 0.32, h: cfg.h - 0.54,
      fontSize: cfg.bodySize ?? 11.4,
      color: cfg.bodyColor ?? C.ink,
      margin: 0,
      valign: "top",
      fit: "shrink",
      breakLine: true,
      paraSpaceAfterPt: 7,
      lineSpacingMultiple: 1.08,
    });
  }
}

function addMetric(slide, x, y, w, label, value, color = C.teal) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h: 0.88,
    rectRadius: 0.05,
    line: { color, pt: 1 },
    fill: { color: C.white },
  });
  slide.addText(value, {
    x: x + 0.1, y: y + 0.08, w: w - 0.2, h: 0.3,
    fontSize: 20.5,
    bold: true,
    color,
    align: "center",
    margin: 0,
    fit: "shrink",
  });
  slide.addText(label, {
    x: x + 0.08, y: y + 0.49, w: w - 0.16, h: 0.17,
    fontSize: 9.3,
    color: C.gray,
    align: "center",
    margin: 0,
    fit: "shrink",
  });
}

function addCaption(slide, text, x, y, w) {
  slide.addText(text, {
    x, y, w, h: 0.22,
    fontSize: 8.4,
    color: C.gray,
    italic: true,
    align: "center",
    margin: 0,
  });
}

function addBullets(slide, items, opts = {}) {
  const x = opts.x ?? 0.9;
  const y = opts.y ?? 1.5;
  const w = opts.w ?? 5.6;
  const h = opts.h ?? 4.8;
  const fs = opts.fontSize ?? 16;
  const color = opts.color ?? C.ink;
  const indent = opts.indent ?? 18;
  const hanging = opts.hanging ?? 4;
  const paras = items.map((text) => ({
    text,
    options: {
      bullet: { indent },
      hanging,
      breakLine: true,
    },
  }));
  slide.addText(paras, {
    x, y, w, h,
    fontSize: fs,
    color,
    valign: "top",
    margin: 0,
    paraSpaceAfterPt: opts.paraSpaceAfterPt ?? 10,
    breakLine: false,
    fit: "shrink",
    lineSpacingMultiple: 1.12,
  });
}

// 1 Cover
{
  const s = pptx.addSlide();
  s.background = { color: C.white };
  s.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 4.85, h: 7.5,
    line: { color: C.navy, transparency: 100 },
    fill: { color: C.navy },
  });
  s.addShape(pptx.ShapeType.rect, {
    x: 4.85, y: 0, w: 8.483, h: 7.5,
    line: { color: C.sky, transparency: 100 },
    fill: { color: C.sky },
  });
  s.addText("博士学位论文预答辩", {
    x: 0.75, y: 0.82, w: 2.5, h: 0.28,
    fontSize: 16,
    color: "D9E7F6",
    bold: true,
    margin: 0,
  });
  s.addText(title, {
    x: 0.75, y: 1.42, w: 3.25, h: 2.1,
    fontSize: 24.5,
    bold: true,
    color: C.white,
    margin: 0,
    breakLine: true,
    fit: "shrink",
    valign: "mid",
  });
  s.addText(`${author}\n${advisors}\n${meta}\n2026年6月`, {
    x: 0.75, y: 4.72, w: 3.2, h: 1.3,
    fontSize: 12.5,
    color: "E9F1F9",
    margin: 0,
    breakLine: true,
    paraSpaceAfterPt: 8,
    lineSpacingMultiple: 1.05,
  });
  s.addImage({
    path: IMG.gating,
    x: 5.28, y: 0.82, w: 7.4, h: 5.2,
    sizing: { type: "contain", x: 5.28, y: 0.82, w: 7.4, h: 5.2 },
  });
  addTag(s, "直通式阀体", 5.55, 6.08, 1.15, C.teal);
  addTag(s, "铸造缩孔", 6.82, 6.08, 1.15, C.orange);
  addTag(s, "承压性能", 8.09, 6.08, 1.15, C.navy);
  addTag(s, "晶粒强化", 9.36, 6.08, 1.15, C.green);
}

// 2 Outline
{
  const s = pptx.addSlide();
  addHeader(s, "汇报提纲", "本次预答辩按问题提出、方法构建、结果验证、结论展望展开");
  const sections = [
    ["01", "研究背景与问题提出", C.navy],
    ["02", "研究目标与技术路线", C.teal],
    ["03", "缩孔形成机理与工艺优化", C.orange],
    ["04", "缩孔群映射与强度评估", C.red],
    ["05", "高应力区晶粒强化与验证", C.green],
    ["06", "创新点、结论与展望", C.blue],
  ];
  let y = 1.55;
  for (const item of sections) {
    s.addShape(pptx.ShapeType.roundRect, {
      x: 1.2, y, w: 10.8, h: 0.66,
      rectRadius: 0.04,
      line: { color: item[2], pt: 1 },
      fill: { color: C.white },
    });
    s.addShape(pptx.ShapeType.roundRect, {
      x: 1.2, y, w: 1.05, h: 0.66,
      rectRadius: 0.04,
      line: { color: item[2], transparency: 100 },
      fill: { color: item[2] },
    });
    s.addText(item[0], {
      x: 1.46, y: y + 0.17, w: 0.53, h: 0.18,
      fontSize: 16,
      color: C.white,
      bold: true,
      align: "center",
      margin: 0,
    });
    s.addText(item[1], {
      x: 2.48, y: y + 0.16, w: 8.8, h: 0.22,
      fontSize: 16,
      color: C.ink,
      bold: true,
      margin: 0,
    });
    y += 0.83;
  }
  addFooter(s, 2);
}

// 3 Background and significance
{
  const s = pptx.addSlide();
  addHeader(s, "研究背景与意义", "面向高温高压工况下直通式铸钢阀体的安全与轻量化需求");
  addCard(s, {
    x: 0.82, y: 1.32, w: 5.95, h: 4.95,
    fill: C.pale, line: C.line,
    title: "工程背景",
    body: "1. 直通式阀体广泛用于能源、化工、管输等高参数场景，承压可靠性直接决定系统安全。\n2. 复杂流道与挡板结构使其成为典型厚薄不均铸件，天然易形成热节、补缩不足和缩孔缺陷。\n3. 在极端工况和轻量化要求下，仅靠经验增厚已难以兼顾安全、重量和制造成本。\n4. 因此需要建立兼顾制造缺陷与结构完整性的设计评价体系。",
    bodySize: 12.7,
  });
  addCard(s, {
    x: 7.0, y: 1.32, w: 5.45, h: 1.35, fill: "F6FBFB", line: "B7DFDF",
    title: "意义 1：缺陷源头控制",
    body: "在结构参数与铸造工艺层面降低缩孔敏感性，提高阀体成品率与一致性。",
    titleColor: C.teal,
    bodySize: 12,
  });
  addCard(s, {
    x: 7.0, y: 2.92, w: 5.45, h: 1.35, fill: "FFF7EE", line: "F0D0AD",
    title: "意义 2：真实承压评估",
    body: "把制造缺陷引入结构分析，从“理想均质”走向“实际非均质”承压评价。",
    titleColor: C.orange,
    bodySize: 12,
  });
  addCard(s, {
    x: 7.0, y: 4.52, w: 5.45, h: 1.35, fill: "F7FAF7", line: "C7DFC7",
    title: "意义 3：局部强化设计",
    body: "围绕真实高应力区开展微观组织调控，在不显著增重条件下提升安全裕度。",
    titleColor: C.green,
    bodySize: 12,
  });
  addFooter(s, 3);
}

// 4 Current gaps
{
  const s = pptx.addSlide();
  addHeader(s, "现有研究存在的主要问题", "论文第1章问题归纳");
  addCard(s, {
    x: 0.95, y: 1.65, w: 3.75, h: 4.55, fill: "F6FBFB", line: "B7DFDF",
    title: "问题 1\n协同优化不足",
    body: "现有研究多停留于既定结构下的工艺试错优化，较少从阀体几何拓扑源头研究其缩孔敏感性，也缺少结构参数与工艺参数的联合反演框架。",
    titleColor: C.teal,
    bodySize: 12.2,
  });
  addCard(s, {
    x: 4.79, y: 1.65, w: 3.75, h: 4.55, fill: "FFF8F0", line: "E9C89D",
    title: "问题 2\n强度评估脱节",
    body: "传统“等效挖空法”忽略缩孔群的体积分数、海绵状分布与周围基体刚度退化，难以真实反映应力交互机制，导致承压评估偏差较大。",
    titleColor: C.orange,
    bodySize: 12.2,
  });
  addCard(s, {
    x: 8.63, y: 1.65, w: 3.75, h: 4.55, fill: "F7FAF7", line: "C7DFC7",
    title: "问题 3\n强化策略粗放",
    body: "工程实践通常依赖全局增厚补偿强度下降，但高风险往往集中在少数高应力区；缺少与高精度危险区识别联动的局部微观强化路径。",
    titleColor: C.green,
    bodySize: 12.2,
  });
  addFooter(s, 4);
}

// 5 Objectives
{
  const s = pptx.addSlide();
  addHeader(s, "研究目标与主要内容", "形成“结构/工艺优化—缺陷映射—组织强化—实验验证”的闭环");
  addCard(s, {
    x: 0.82, y: 1.28, w: 12.0, h: 1.02, fill: "EEF5FB", line: "C5DCEF",
    title: "总体目标",
    body: "建立一套考虑铸造缩孔缺陷的直通式阀体承压性能高保真评估与高应力区晶粒强化方法，实现从宏观缺陷控制到微观组织补偿的全流程研究。",
    bodySize: 13,
  });
  addCard(s, {
    x: 0.82, y: 2.68, w: 3.8, h: 2.55, fill: "F6FBFB", line: "B7DFDF",
    title: "研究内容一",
    body: "缩孔形成机理与工艺优化\n- 建立宏观流场/温度场模型\n- 研究结构参数对热节与缩孔率的影响\n- 优化浇注系统与温度窗口",
    titleColor: C.teal,
    bodySize: 12,
  });
  addCard(s, {
    x: 4.78, y: 2.68, w: 3.8, h: 2.55, fill: "FFF8F0", line: "E9C89D",
    title: "研究内容二",
    body: "缩孔群映射与承压评估\n- 构建ProCAST-结构有限元映射路径\n- 建立非均质含缺陷阀体模型\n- 识别真实危险区与评价参量",
    titleColor: C.orange,
    bodySize: 12,
  });
  addCard(s, {
    x: 8.74, y: 2.68, w: 3.8, h: 2.55, fill: "F7FAF7", line: "C7DFC7",
    title: "研究内容三",
    body: "高应力区微观组织预测与强化\n- 构建CAFE跨尺度模拟\n- 标定形核与生长参数\n- 实施局部细晶强化并验证",
    titleColor: C.green,
    bodySize: 12,
  });
  addBullets(s, [
    "核心问题 A：哪些结构/工艺因素主导缩孔形成与空间分布？",
    "核心问题 B：如何真实刻画缩孔群对阀体承压能力的削弱机制？",
    "核心问题 C：如何以高应力区为靶点开展微观组织强化？",
  ], { x: 0.95, y: 5.55, w: 11.4, h: 1.15, fontSize: 13 });
  addFooter(s, 5);
}

// 6 Technical route
{
  const s = pptx.addSlide();
  addHeader(s, "技术路线", "ICME理念下的多尺度研究框架");
  const steps = [
    ["参数化模型", "阀体几何建模\n材料与边界输入"],
    ["铸造仿真", "流动-传热-凝固\n缩孔分布预测"],
    ["工艺优化", "注入方式/冒口/温度\n降低初始缺陷"],
    ["缺陷映射", "缩孔率场导入力学网格\n建立非均质模型"],
    ["危险区识别", "薄膜应力分析\n定位高风险区"],
    ["CAFE强化", "微观组织预测\n局部细晶补偿"],
    ["实验验证", "热测/解剖/探伤\n校核模型可信度"],
  ];
  let x = 0.62;
  for (let i = 0; i < steps.length; i += 1) {
    addCard(s, {
      x, y: 2.08, w: 1.7, h: 2.6,
      fill: i % 2 === 0 ? "F8FBFE" : "F9FBF9",
      line: i % 2 === 0 ? "C9DBED" : "C9E1D1",
      title: steps[i][0],
      body: steps[i][1],
      titleSize: 12.5,
      bodySize: 10.8,
    });
    if (i < steps.length - 1) {
      s.addShape(pptx.ShapeType.chevron, {
        x: x + 1.78, y: 3.05, w: 0.3, h: 0.34,
        line: { color: C.line, transparency: 100 },
        fill: { color: C.orange, transparency: 16 },
      });
    }
    x += 1.82;
  }
  s.addShape(pptx.ShapeType.roundRect, {
    x: 3.3, y: 5.35, w: 6.8, h: 0.72,
    rectRadius: 0.05,
    line: { color: C.navy, pt: 1.1 },
    fill: { color: "EEF5FB" },
  });
  s.addText("形成“缺陷控制—承压评估—局部强化—实验验证”的闭环研究体系", {
    x: 3.5, y: 5.56, w: 6.4, h: 0.23,
    fontSize: 13,
    bold: true,
    color: C.navy,
    align: "center",
    margin: 0,
  });
  addFooter(s, 6);
}

// 7 Chapter 2 method
{
  const s = pptx.addSlide();
  addHeader(s, "第二章：缩孔形成机理与结构参数设计", "围绕热节形成、补缩通道和结构拓扑开展建模");
  s.addImage({
    path: IMG.gating,
    x: 7.2, y: 1.45, w: 5.15, h: 3.6,
    sizing: { type: "contain", x: 7.2, y: 1.45, w: 5.15, h: 3.6 },
  });
  addCaption(s, "论文图2.6：铸钢阀体浇注系统", 7.28, 5.08, 4.95);
  addBullets(s, [
    "建立直通式 CF8M 铸钢阀体的宏观流场、温度场和凝固耦合模型。",
    "选取长径比、回转体径长比、入口偏转角、挡板壁厚比等结构参数作为研究因素。",
    "通过正交试验分析结构特征对整体与局部缩孔率的影响，寻找缩孔敏感性最低的构型。",
    "在优选结构基础上，继续对注入方式、冒口形式与浇注温度进行协同优化。",
  ], { x: 0.95, y: 1.68, w: 5.8, h: 3.65, fontSize: 13.2 });
  addCard(s, {
    x: 0.98, y: 5.65, w: 5.8, h: 0.74, fill: "F6FBFB", line: "B7DFDF",
    title: "研究关注点",
    body: "结构变化不仅改变几何形状，更会重塑热流传递路径、补缩阻力和热节位置。",
    titleSize: 12.5,
    bodySize: 11.3,
    titleColor: C.teal,
  });
  addFooter(s, 7);
}

// 8 Chapter 2 results
{
  const s = pptx.addSlide();
  addHeader(s, "第二章：工艺优化结果", "注入方式、冒口形式与温度窗口共同决定缩孔与卷气行为");
  addCard(s, {
    x: 0.82, y: 1.45, w: 3.9, h: 4.8, fill: C.pale, line: C.line,
    title: "关键结论",
    body: "1. 阀体长径比等结构参数会显著影响孤立热节形成及补缩通道通畅性。\n2. 中间注入可有效抑制跌落式充型引起的卷气与紊流，优于顶部注入。\n3. T型冒口补缩效率高于参考法兰冒口，更有利于阀体上部和中部顺序凝固。\n4. 浇注温度过低会恶化充型与补缩，过高又会导致热焓过剩与组织粗化。",
    bodySize: 12.1,
  });
  addMetric(s, 5.25, 2.0, 2.0, "优选注入方式", "中间注入", C.teal);
  addMetric(s, 7.55, 2.0, 2.0, "优选冒口", "T型冒口", C.orange);
  addMetric(s, 9.85, 2.0, 2.0, "温度窗口", "1560–1580 ℃", C.navy);
  addCard(s, {
    x: 5.05, y: 3.32, w: 6.9, h: 2.08, fill: "FFF8F0", line: "E9C89D",
    title: "工程取值",
    body: "综合缺陷控制与后续高应力区组织细化需求，论文实际试验将浇注温度定为 1570 ℃。这一窗口在保证平稳充型与顺序补缩的同时，避免盲目追求高温导致晶粒粗化。",
    titleColor: C.orange,
    bodySize: 12.2,
  });
  addCard(s, {
    x: 5.05, y: 5.65, w: 6.9, h: 0.62, fill: "F7FAF7", line: "C7DFC7",
    title: "结论",
    body: "缺陷控制不能只看缩孔体积最小值，还要兼顾后续强度和组织演化。",
    titleColor: C.green,
    titleSize: 12,
    bodySize: 10.8,
  });
  addFooter(s, 8);
}

// 9 Chapter 3 method
{
  const s = pptx.addSlide();
  addHeader(s, "第三章：缩孔群映射与非均质承压模型", "从制造缺陷数据到结构有限元评价");
  addCard(s, {
    x: 0.85, y: 1.45, w: 5.8, h: 4.9, fill: C.pale, line: C.line,
    title: "建模思路",
    body: "1. 提取 ProCAST 计算得到的三维局部缩孔率场。\n2. 通过映射算法将离散孔隙信息无损传递到结构力学网格。\n3. 在有限元模型中以连续体积损伤形式反映材料刚度与强度退化。\n4. 在此基础上对阀体危险服役边界进行多轴受力分析与失效评估。",
    bodySize: 12.5,
  });
  s.addImage({
    path: IMG.stressA,
    x: 7.0, y: 1.58, w: 5.55, h: 4.1,
    sizing: { type: "contain", x: 7.0, y: 1.58, w: 5.55, h: 4.1 },
  });
  addCaption(s, "论文图3.8：不同工况下的 Mises 应力对比", 7.08, 5.72, 5.3);
  addCard(s, {
    x: 7.1, y: 5.95, w: 5.2, h: 0.42, fill: "F6FBFB", line: "B7DFDF",
    title: "目标",
    body: "识别真实危险区，而不是仅追踪表面峰值应力。",
    titleSize: 11.6,
    bodySize: 10.6,
    titleColor: C.teal,
  });
  addFooter(s, 9);
}

// 10 Chapter 3 results: asymmetric mechanism
{
  const s = pptx.addSlide();
  addHeader(s, "第三章：缩孔群的非对称演化机制", "宏观几何对称并不意味着缺陷分布对称");
  s.addImage({
    path: IMG.stressB,
    x: 0.8, y: 1.48, w: 6.45, h: 4.95,
    sizing: { type: "contain", x: 0.8, y: 1.48, w: 6.45, h: 4.95 },
  });
  addCaption(s, "论文图3.10：理想阀体与含缩孔阀体的应力分布对比", 1.0, 6.42, 6.0);
  addCard(s, {
    x: 7.55, y: 1.65, w: 4.85, h: 4.65, fill: "FFF8F0", line: "E9C89D",
    title: "机理认识",
    body: "1. 虽然阀体宏观几何近似对称，但充型末期受中腔挡板阻流影响，会形成大尺度环流。\n2. 环流导致热焓输运出现明显偏置，热中心漂移并诱发非对称糊状区闭合。\n3. 最终在局部形成空间分布与体量均失衡的缩孔群，而非理想的均匀小缺陷。\n4. 这类非对称缩孔群会进一步干预局部刚度与应力传递路径。",
    titleColor: C.orange,
    bodySize: 12.1,
  });
  addFooter(s, 10);
}

// 11 Chapter 3 results: criterion
{
  const s = pptx.addSlide();
  addHeader(s, "第三章：应力畸变与评价参量", "局部最大应力并非含缺陷超静定壳体的最佳判据");
  s.addImage({
    path: IMG.stressC,
    x: 0.8, y: 1.45, w: 7.0, h: 4.95,
    sizing: { type: "contain", x: 0.8, y: 1.45, w: 7.0, h: 4.95 },
  });
  addCaption(s, "论文图3.11–3.15：缩孔对壁厚内应力与危险截面的影响", 1.0, 6.4, 6.6);
  addCard(s, {
    x: 8.1, y: 1.62, w: 4.25, h: 1.25, fill: "F6FBFB", line: "B7DFDF",
    title: "发现 1",
    body: "缩孔群会引发局部软化、卸载和应力绕流，峰值位置出现空间游离。",
    titleColor: C.teal,
    bodySize: 11.5,
  });
  addCard(s, {
    x: 8.1, y: 3.06, w: 4.25, h: 1.25, fill: "FFF7EE", line: "F0D0AD",
    title: "发现 2",
    body: "危险区本质上是“高应力需求”与“低承载容量”发生空间重叠的区域。",
    titleColor: C.orange,
    bodySize: 11.5,
  });
  addCard(s, {
    x: 8.1, y: 4.5, w: 4.25, h: 1.25, fill: "F7FAF7", line: "C7DFC7",
    title: "结论",
    body: "截面壁厚平均应力（薄膜应力）与缺陷拓扑更同频，可作为更可靠的损伤容限评价参量。",
    titleColor: C.green,
    bodySize: 11.5,
  });
  addFooter(s, 11);
}

// 12 Chapter 4 method
{
  const s = pptx.addSlide();
  addHeader(s, "第四章：高应力区晶粒组织预测方法", "CAFE跨尺度耦合模型与参数标定");
  s.addImage({
    path: IMG.cafeFlow,
    x: 0.95, y: 1.58, w: 3.55, h: 4.7,
    sizing: { type: "contain", x: 0.95, y: 1.58, w: 3.55, h: 4.7 },
  });
  addCaption(s, "论文图4.2：CAFE凝固组织模拟流程", 1.0, 6.3, 3.4);
  s.addImage({
    path: IMG.nucleation,
    x: 4.85, y: 1.76, w: 2.65, h: 3.0,
    sizing: { type: "contain", x: 4.85, y: 1.76, w: 2.65, h: 3.0 },
  });
  addCaption(s, "论文图4.1：体/面形核参数高斯分布", 4.95, 4.82, 2.45);
  addBullets(s, [
    "宏观有限元负责计算全域温度场与凝固边界条件，元胞自动机负责局部相变和晶粒竞争生长。",
    "模型区分面形核与体形核参数，采用连续非均匀形核模型描述异质形核过程。",
    "结合标准圆柱试块的低倍酸洗与金相实验，对形核和生长动力学参数进行标定。",
  ], { x: 7.95, y: 1.72, w: 4.1, h: 3.25, fontSize: 12.2 });
  addCard(s, {
    x: 4.85, y: 5.35, w: 7.3, h: 0.85, fill: "F7FAF7", line: "C7DFC7",
    title: "目的",
    body: "把第三章识别出的高应力危险区，进一步转化为微观组织强化的精确干预靶点。",
    titleColor: C.green,
    titleSize: 12.4,
    bodySize: 11.2,
  });
  addFooter(s, 12);
}

// 13 Chapter 4 results
{
  const s = pptx.addSlide();
  addHeader(s, "第四章：高应力区晶粒组织演化与强化思路", "高风险区同时对应粗大柱状晶与缩孔伴生");
  s.addImage({
    path: IMG.micro,
    x: 0.85, y: 1.55, w: 5.55, h: 4.15,
    sizing: { type: "contain", x: 0.85, y: 1.55, w: 5.55, h: 4.15 },
  });
  addCaption(s, "论文图4.10：阀体微观组织预测图", 1.0, 5.74, 5.25);
  s.addImage({
    path: IMG.oilBath,
    x: 6.85, y: 1.72, w: 2.2, h: 2.15,
    sizing: { type: "contain", x: 6.85, y: 1.72, w: 2.2, h: 2.15 },
  });
  addCaption(s, "论文图4.4：实验标定装置", 6.95, 3.88, 2.0);
  addCard(s, {
    x: 9.3, y: 1.62, w: 3.2, h: 2.4, fill: "FFF8F0", line: "E9C89D",
    title: "主要认识",
    body: "高应力区因孤立热节散热差，易形成粗大柱状晶网络；柱状晶连续生长又会加剧补缩通道阻断，与缩孔缺陷形成空间伴生。",
    titleColor: C.orange,
    bodySize: 11.5,
  });
  addMetric(s, 6.9, 4.55, 1.65, "挡板区平均晶粒", "0.615 mm", C.orange);
  addMetric(s, 8.78, 4.55, 1.65, "主截面平均晶粒", "0.688 mm", C.teal);
  addMetric(s, 10.66, 4.55, 1.65, "取向偏差角", "≈31.8°", C.navy);
  addCard(s, {
    x: 6.85, y: 5.7, w: 5.55, h: 0.55, fill: "F7FAF7", line: "C7DFC7",
    title: "强化路径",
    body: "通过局部随形冷铁/激冷干预打断柱状晶连续生长，促进等轴晶形成，实现高应力区细晶强化。",
    titleColor: C.green,
    titleSize: 11.7,
    bodySize: 10.6,
  });
  addFooter(s, 13);
}

// 14 Experimental validation: casting and thermal
{
  const s = pptx.addSlide();
  addHeader(s, "第五章：铸造试验与温度场验证", "用实测边界条件和工艺过程校核仿真模型");
  s.addImage({
    path: IMG.thermocouple,
    x: 0.82, y: 1.48, w: 6.7, h: 4.65,
    sizing: { type: "contain", x: 0.82, y: 1.48, w: 6.7, h: 4.65 },
  });
  addCaption(s, "论文图5.6相关：阀体铸造过程多通道温度采集系统", 1.0, 6.16, 6.35);
  addCard(s, {
    x: 7.82, y: 1.62, w: 4.45, h: 4.4, fill: C.pale, line: C.line,
    title: "验证内容",
    body: "1. 在砂箱关键位置预埋热电偶，采集浇注与冷却全过程的温度曲线。\n2. 对同炉 CF8M 熔体进行成分和浇注温度控制，保证工艺输入可复现。\n3. 实测温度场用于校核凝固边界条件与热物性参数设置。\n4. 通过铸造试验确认优选工艺在真实制造场景下可落地。",
    bodySize: 12.1,
  });
  addFooter(s, 14);
}

// 15 Experimental validation: shrinkage
{
  const s = pptx.addSlide();
  addHeader(s, "第五章：缩孔仿真与解剖验证", "先验证材料与凝固求解，再推广到复杂阀体");
  addCard(s, {
    x: 0.92, y: 1.55, w: 5.55, h: 4.85, fill: "F6FBFB", line: "B7DFDF",
    title: "圆柱试块验证",
    body: "1. 采用与阀体同炉的 CF8M 标准圆柱试样开展宏观凝固仿真与破坏性解剖实验。\n2. 仿真预测的缩孔位置与真实试样纵截面观察结果高度一致。\n3. 等效球形体积反演显示：仿真 57.26 cm³，实测 57.91 cm³，相对误差约 1.2%。\n4. 说明热物性参数和凝固求解路径具备较高保真度。",
    bodySize: 12.3,
  });
  addMetric(s, 7.1, 1.95, 1.55, "仿真体积", "57.26 cm³", C.navy);
  addMetric(s, 8.95, 1.95, 1.55, "实测体积", "57.91 cm³", C.teal);
  addMetric(s, 10.8, 1.95, 1.2, "误差", "1.2%", C.orange);
  addCard(s, {
    x: 7.08, y: 3.2, w: 4.95, h: 2.25, fill: "FFF8F0", line: "E9C89D",
    title: "意义",
    body: "先在简单试样层面验证“材料—工艺—求解”的可信度，再将模型推广到全尺寸复杂阀体，避免直接在复杂模型上堆叠不确定性。",
    titleColor: C.orange,
    bodySize: 12,
  });
  addFooter(s, 15);
}

// 16 Experimental validation: RT
{
  const s = pptx.addSlide();
  addHeader(s, "第五章：阀体射线探伤验证", "仿真风险区与实际探伤结果相互印证");
  s.addImage({
    path: IMG.rt,
    x: 0.9, y: 1.55, w: 5.85, h: 4.65,
    sizing: { type: "contain", x: 0.9, y: 1.55, w: 5.85, h: 4.65 },
  });
  addCaption(s, "论文图5.14：直通式阀体伽马射线探伤实验", 1.02, 6.22, 5.6);
  addCard(s, {
    x: 7.15, y: 1.65, w: 5.15, h: 4.42, fill: C.pale, line: C.line,
    title: "验证结论",
    body: "1. 采用 Ir-192 伽马射线对阀体核心风险区进行单壁透照。\n2. 探伤区域的布置依据前文数值仿真预测的缩孔高风险位置确定。\n3. 实测底片结果与仿真预测的缺陷区具有较好一致性，支持映射模型的空间定位能力。\n4. 说明“工艺仿真—缺陷映射—危险区识别”链条具备工程可用性。",
    bodySize: 12.2,
  });
  addFooter(s, 16);
}

// 17 Innovations
{
  const s = pptx.addSlide();
  addHeader(s, "主要创新点", "围绕源头控制、强度评价与局部强化形成完整链条");
  addCard(s, {
    x: 0.95, y: 1.72, w: 3.75, h: 4.55, fill: "F6FBFB", line: "B7DFDF",
    title: "创新点 1\n结构—工艺协同优化",
    body: "将阀体几何拓扑参数与铸造工艺参数纳入统一研究框架，系统分析缩孔敏感性的形成机制，提出适用于直通式阀体的源头控制思路。",
    titleColor: C.teal,
    bodySize: 12.2,
  });
  addCard(s, {
    x: 4.79, y: 1.72, w: 3.75, h: 4.55, fill: "FFF8F0", line: "E9C89D",
    title: "创新点 2\n非均质缩孔群承压评估",
    body: "建立 ProCAST 到结构网格的高保真缺陷映射路径，揭示缩孔引发的软化、卸载和应力绕流机制，并提出薄膜应力评价参量。",
    titleColor: C.orange,
    bodySize: 12.2,
  });
  addCard(s, {
    x: 8.63, y: 1.72, w: 3.75, h: 4.55, fill: "F7FAF7", line: "C7DFC7",
    title: "创新点 3\n高应力区晶粒靶向强化",
    body: "将高精度危险区识别与 CAFE 微观组织模拟相联动，提出面向高应力区的局部细晶强化路径，实现宏观缺陷与微观补偿协同。",
    titleColor: C.green,
    bodySize: 12.2,
  });
  addFooter(s, 17);
}

// 18 Conclusions
{
  const s = pptx.addSlide();
  addHeader(s, "主要结论", "从缺陷形成、承压机理到强化思路的整体认识");
  addCard(s, {
    x: 0.85, y: 1.45, w: 5.85, h: 4.95, fill: C.pale, line: C.line,
    title: "结论 1–2",
    body: "1. 直通式阀体缩孔形成受结构拓扑、热节分布和补缩路径的强耦合控制，中间注入 + T型冒口 + 中温窗口更有利于缺陷控制。\n2. 含缩孔群阀体的危险区识别不能仅依赖局部最大应力，必须结合非均质映射与应力线性化分析。",
    bodySize: 12.5,
  });
  addCard(s, {
    x: 6.95, y: 1.45, w: 5.5, h: 2.2, fill: "FFF7EE", line: "F0D0AD",
    title: "结论 3",
    body: "缩孔群会导致刚度软化、跨区卸载和应力绕流，薄膜应力与缺陷拓扑更同频，适合作为损伤容限评价参量。",
    titleColor: C.orange,
    bodySize: 12.2,
  });
  addCard(s, {
    x: 6.95, y: 4.0, w: 5.5, h: 2.4, fill: "F7FAF7", line: "C7DFC7",
    title: "结论 4",
    body: "高应力区往往伴生粗大柱状晶和缩孔集中，通过局部细晶强化有望在不显著增重条件下补偿承压性能劣化。多项实验验证支持模型可信度。",
    titleColor: C.green,
    bodySize: 12.2,
  });
  addFooter(s, 18);
}

// 19 Outlook
{
  const s = pptx.addSlide();
  addHeader(s, "研究展望", "面向工程应用继续完善评价与设计准则");
  addCard(s, {
    x: 0.95, y: 1.7, w: 3.75, h: 4.45, fill: "F6FBFB", line: "B7DFDF",
    title: "展望 1",
    body: "进一步建立考虑缩孔缺陷尺寸与位置影响的改进型射线检测标准，使无损检测结果更直接服务于结构设计与验收判定。",
    titleColor: C.teal,
    bodySize: 12.1,
  });
  addCard(s, {
    x: 4.79, y: 1.7, w: 3.75, h: 4.45, fill: "FFF8F0", line: "E9C89D",
    title: "展望 2",
    body: "继续补强“局部细晶强化后承压提升量”的定量验证，推动从机理证明走向可复制的工程工艺方案。",
    titleColor: C.orange,
    bodySize: 12.1,
  });
  addCard(s, {
    x: 8.63, y: 1.7, w: 3.75, h: 4.45, fill: "F7FAF7", line: "C7DFC7",
    title: "展望 3",
    body: "最终形成面向铸钢阀体的设计指南，提升成品率、增强终端用户信心，并通过减少设计迭代缩短研发周期、降低成本。",
    titleColor: C.green,
    bodySize: 12.1,
  });
  addFooter(s, 19);
}

// 20 Thanks
{
  const s = pptx.addSlide();
  s.background = { color: "F7FAFC" };
  s.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 13.333, h: 0.32,
    line: { color: C.navy, transparency: 100 },
    fill: { color: C.navy },
  });
  s.addText("请各位老师批评指正", {
    x: 2.1, y: 2.05, w: 9.1, h: 0.8,
    fontSize: 28,
    bold: true,
    color: C.navy,
    align: "center",
    margin: 0,
  });
  s.addText("Thanks", {
    x: 5.35, y: 3.18, w: 2.65, h: 0.45,
    fontSize: 20,
    color: C.teal,
    bold: true,
    align: "center",
    margin: 0,
  });
  s.addShape(pptx.ShapeType.line, {
    x: 3.85, y: 3.75, w: 5.6, h: 0,
    line: { color: C.line, pt: 1.2 },
  });
  s.addText(`${author} | ${meta}`, {
    x: 3.0, y: 4.15, w: 7.3, h: 0.32,
    fontSize: 12,
    color: C.gray,
    align: "center",
    margin: 0,
  });
}

(async () => {
  await pptx.writeFile({ fileName: "/Users/lishishun/Documents/New project/直通式阀体预答辩PPT.pptx" });
})();
