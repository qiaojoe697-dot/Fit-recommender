# Loop Design 模板

**从穿搭推荐系统项目中提炼的可复用框架**

---

## 一、Loop 设计五问法

接到一个新任务时，回答这 5 个问题就能设计出一个完整的 Loop：

```
Q1. 目标定义 — 怎样才算"做完"？
    → 列出可验证的完成条件（测试全过？CLI 跑通？页面能打开？）

Q2. 分解策略 — 切成几轮循环？
    → 每轮产出必须是可验证的增量
    → 先骨架 → 核心功能 → 交互 → 审查 → 扩展 → 复盘

Q3. 角色设计 — 谁做什么？
    → Maker（写代码）
    → Checker（验证代码，必须是不同的人/Agent）
    → You（做关键决策）

Q4. 状态管理 — 信息存在哪？
    → Memory 文件结构怎么设计？
    → 进度怎么追踪？

Q5. 验证机制 — 怎么确保没跑偏？
    → 自动验证（测试/lint/type check）
    → 人工验证点（你什么时候介入检查？）
```

---

## 二、一轮 Loop 的标准流程

```
1. [触发]  你输入 /loop "第N轮：实现..."
2. [读取]  Agent 读取 CLAUDE.md + MEMORY.md
3. [执行]  Maker Agent 实现功能 + 写测试
4. [验证]  自动运行测试 / lint / type check
5. [审查]  Checker Agent 审查代码
6. [记录]  更新 MEMORY.md
7. [报告]  向你报告成果
8. [决策]  你评估 → 继续下一轮 / 调整方向
```

---

## 三、Loop 六大组件速查

| 组件 | 作用 | 文件/机制 |
|------|------|----------|
| **Skills** | 项目知识，让 Agent 不用猜 | `CLAUDE.md` — 技术栈、目录、命令、规范 |
| **Memory** | 跨轮状态，Agent 会忘但仓库不会 | `MEMORY.md` + `memory/` 分主题文件 |
| **Automation** | 自动触发循环 | `/loop` 命令、cron、hooks |
| **Worktrees** | 隔离并行开发 | `git worktree`、`isolation: worktree` |
| **Sub-agents** | 生成器≠验证器 | Maker Agent vs Checker Agent |
| **Plugins** | 接入真实工具 | MCP 协议连接 GitHub/Linear/Slack |

---

## 四、关键原则

1. **生成器 ≠ 验证器** — 写代码的人不要检查自己的代码，用独立角色/Agent 审查
2. **Memory 在磁盘，不在上下文** — Agent 会忘记一切，但仓库不会
3. **每轮可验证** — 每轮迭代必须有客观的"完成"标准（测试、构建、截图）
4. **增量产出** — 每轮的产出比上一轮多一点点，不要一回合做所有事

---

## 五、Memory 文件的最佳实践

```
project/
├── CLAUDE.md           # Skills：Agent 启动时自动读取
├── MEMORY.md           # Memory 索引（简短，只放目录指针）
├── memory/
│   ├── progress.md     # 已完成/未完成清单
│   ├── next-steps.md   # 下一步计划
│   └── decisions.md    # 设计决策记录（避免重复踩坑）
```

Memory 内容三要素：
- ✅ **已完成** — 让 Agent 不用重复造轮子
- ❌ **已排除** — 让 Agent 不会踩同一个坑
- ➡️ **下一步** — 让下一轮无缝衔接

---

## 六、空白模板（可直接复制到新项目使用）

```markdown
# Loop 设计：项目名称

## Q1：目标定义
- 功能目标：
- 验证标准：

## Q2：分解策略（共 X 轮）
| 轮次 | 产出 | 验证方式 |
|------|------|---------|
| 第1轮 |      |         |
| 第2轮 |      |         |
| 第3轮 |      |         |

## Q3：角色设计
- Maker：
- Checker：
- Human（你）：

## Q4：状态管理
- CLAUDE.md：
- MEMORY.md：
- memory/ 文件：

## Q5：验证机制
- 自动验证：
- 人工验证：
```

---

## 七、本项目的 Memory 文件结构（参考）

```
outfit-recommender/
├── CLAUDE.md                   # 项目 Skills
├── MEMORY.md                   # Memory 索引
├── memory/
│   ├── progress.md             # 进度追踪
│   ├── next-steps.md           # 下一步计划
│   ├── decisions.md            # 设计决策
│   └── loop-design-summary.md  # ← 就是这个文件
```

---

*从穿搭推荐系统项目提炼，2026-06-15*
