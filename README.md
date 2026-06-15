# LoopFit — 穿搭推荐系统

基于 [Loop Engineering](https://addyosmani.com/blog/loop-engineering/) 方法论构建的穿搭推荐系统。用户输入季节、场合、风格偏好，系统基于内容相似度算法返回 Top-N 搭配推荐。

## 快速开始

```bash
pip install -r requirements.txt

# CLI 模式
python -m src.cli --season summer --occasion casual --style street

# Web UI 模式
streamlit run web/app.py
```

## 项目结构

```
├── CLAUDE.md            # Skills：项目知识文档
├── MEMORY.md            # Memory 索引
├── memory/              # 进度/决策/设计记录
├── src/                 # 核心代码
│   ├── model.py         # 数据模型
│   ├── features.py      # 特征编码（颜色相似度矩阵）
│   ├── recommender.py   # 推荐引擎（过滤→打分→组合→排序）
│   └── cli.py           # CLI 入口
├── web/app.py           # Streamlit 界面
├── data/items.json      # 20件衣物样本数据
└── tests/               # 26个测试，全部通过
```

## 推荐算法

基于内容的属性特征相似度：风格匹配（权重 2）+ 场合匹配（权重 2）+ 季节匹配（权重 1）+ 颜色和谐度（权重 1），按加权总分排序返回最优搭配。

## 构建方式

本项目的开发过程本身就是 Loop Engineering 的实践——共 6 轮迭代：

| 轮次 | 内容 | Loop 概念 |
|------|------|-----------|
| 1 | 项目骨架 + Skills + Memory | Skills & Memory |
| 2 | 推荐引擎 + 测试 | 自动验证 |
| 3 | CLI 界面 | 端到端验收 |
| 4 | Checker 代码审查 | 生成器 ≠ 验证器 |
| 5 | Web UI（Streamlit） | 并行扩展 |
| 6 | 复盘 + 模板化 | 框架复用 |

详细设计模板见 `memory/loop-design-summary.md`。

## 技术栈

- Python 3.10+
- pytest（测试）
- argparse（CLI）
- Streamlit（Web UI）
