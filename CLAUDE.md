# outfit-recommender — 穿搭推荐系统

## 项目概述
基于内容（属性特征相似度）的穿搭推荐系统。用户输入季节、场合、风格偏好，返回 Top-N 搭配推荐。

## 技术栈
- Python 3.10+
- pytest（测试）
- argparse（CLI，标准库）
- Streamlit（Web UI，第5轮添加）

## 目录结构
```
outfit-recommender/
├── CLAUDE.md           # 本文件 — 项目知识（Skills）
├── MEMORY.md           # Memory 索引
├── memory/             # 分主题记忆文件
├── data/               # 数据集（JSON）
├── src/                # 核心代码
│   ├── model.py        # 数据模型
│   ├── features.py     # 特征编码
│   ├── recommender.py  # 推荐引擎
│   └── cli.py          # CLI 入口
├── web/                # Web UI（第5轮）
│   └── app.py
├── tests/              # 测试
└── requirements.txt
```

## 常用命令
```bash
# 运行所有测试
pytest -v

# 运行 CLI
python -m src.cli --season summer --occasion casual --style street

# 运行 Web UI
streamlit run web/app.py
```

## 编码规范
- 类型注解：所有函数必须带 type hints
- 测试：核心逻辑必须有单元测试
- 错误处理：CLI 层捕获异常，核心逻辑用异常向上传递
