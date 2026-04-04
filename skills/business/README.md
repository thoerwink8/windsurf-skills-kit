# business — 商业诊断 Skills

dontbesilent 商业工具箱 + 奥派经济学聊天室。帮创业者诊断商业模式、找对标、优化内容、破解执行力卡点。

## 包含 Skills（9 个）

| 名称 | 用途 | 触发方式 |
|------|------|---------|
| **dbs** | 工具箱主入口，自动路由到对应诊断工具 | `/dbs`、`/商业`、「帮我看看」 |
| **dbs-diagnosis** | 商业模式诊断（问诊 + 体检） | `/dbs-diagnosis`、`/问诊` |
| **dbs-benchmark** | 五重过滤法对标分析 | `/dbs-benchmark`、`/对标` |
| **dbs-content** | 内容创作五维诊断 | `/dbs-content`、`/内容诊断` |
| **dbs-hook** | 短视频开头诊断 + 优化方案 | `/dbs-hook`、`/hook` |
| **dbs-action** | 阿德勒框架执行力诊断 | `/dbs-action`、`/action` |
| **dbs-deconstruct** | 维特根斯坦式概念拆解 | `/dbs-deconstruct`、`/拆概念` |
| **chatroom-austrian** | 哈耶克 × 米塞斯 × Claude 奥派经济学讨论 | `/chatroom-austrian`、`/奥派` |
| **dbskill-upgrade** | dbs 系列升级工具 | `/dbskill-upgrade` |

## 推荐用法

- **最小配置**：`dbs`（路由入口会自动调用其他 skill）
- **完整配置**：全部 9 个（让每个 skill 都能被直接触发）
- **入口即一切**：不确定装哪些？只装 `dbs`，它会告诉你需要什么

## 内部路由关系

```
用户 → dbs（路由入口）
        ├→ dbs-diagnosis    商业模式诊断
        ├→ dbs-benchmark    对标分析
        ├→ dbs-content      内容创作诊断
        ├→ dbs-hook         短视频开头优化
        ├→ dbs-action       执行力诊断
        └→ dbs-deconstruct  概念拆解

chatroom-austrian   独立入口，讨论中可路由到 dbs 系列
dbskill-upgrade     维护工具，按需使用
```
