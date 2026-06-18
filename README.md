# Fit Recommender

## 项目简介
Fit Recommender 是一个基于规则评分机制的智能穿搭推荐系统。项目通过分析用户偏好、服饰属性和颜色搭配关系，为用户生成多套穿搭方案，并提供推荐分数和搭配建议。

## 核心功能
- 根据用户偏好筛选服饰
- 颜色和风格兼容性计算
- 多套穿搭组合生成
- 推荐结果排序
- CLI 命令行体验
- Streamlit Web 可视化界面
- 单元测试覆盖主要算法模块

## 项目结构

src/
- model.py 数据模型
- features.py 特征计算与评分
- recommender.py 推荐算法核心
- cli.py 命令行入口

web/
- app.py Streamlit Web 页面

data/
- items.json 服饰数据
- demo_outfits.json 示例数据

tests/
- 核心算法测试

## 推荐流程

加载服饰数据
-> 根据用户偏好过滤
-> 计算单品得分
-> 组合穿搭方案
-> 计算颜色协调度
-> 计算风格匹配度
-> 综合评分排序
-> 输出推荐结果

## 技术栈

- Python
- Streamlit
- JSON 数据存储
- Pytest
- 类型注解(dataclass / typing)

## 运行方式

安装依赖：

pip install -r requirements.txt

启动 Web：

streamlit run web/app.py

启动命令行：

python -m src.cli

运行测试：

pytest

## 可优化方向

1. 引入机器学习模型
2. 用户历史行为学习
3. 天气与场景感知推荐
4. 数据库存储
5. API 服务化
6. 个性化排序算法

## 项目特点

该项目采用模块化设计，将数据模型、特征工程、推荐算法和前端展示解耦，方便后续扩展和维护。适合作为推荐系统、Python 工程实践以及 Streamlit 应用开发的学习项目。
