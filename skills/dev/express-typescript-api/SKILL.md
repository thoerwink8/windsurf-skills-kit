---
name: express-typescript-api
description: Express.js + TypeScript REST API 开发规范。构建/审查后端路由、中间件、认证、错误处理、数据库操作时自动加载。覆盖 TypeScript 纪律、路由设计、RBAC 中间件、统一响应格式、批量操作、安全与测试。
---

# Express TypeScript API Skill

> Source: windsurf.run/clean-nestjs-typescript (TypeScript 纪律) + cursorrules.org/express (API 设计) + 项目实战补充

You are an expert in TypeScript, Node.js, Express.js, and REST API development.

## TypeScript 纪律（必须遵守）

### 基本原则
- 所有变量、函数参数、返回值必须声明类型；**禁止使用 `any`**，确实需要时用 `unknown` + 类型收窄。
- 用 `interface` 定义数据契约，用 `type` 定义联合/工具类型。
- 优先 `readonly` 修饰不变数据；用 `as const` 修饰字面量常量。
- 每个文件只有一个主 export（路由文件除外）。

### 命名规范
- 类：`PascalCase`；变量/函数/方法：`camelCase`；文件/目录：`kebab-case`；环境变量：`UPPER_SNAKE_CASE`。
- 函数以动词开头：`getUser`、`validateAccount`、`removeAccount`。
- 布尔变量用动词前缀：`isLoading`、`hasError`、`canDelete`、`isFrozen`。
- 中间件参数固定缩写：`req, res, next`；循环变量：`i, j`；错误：`err`。

### 函数设计
- 单一职责，**少于 20 条指令**；复杂逻辑抽取为命名函数。
- 用**早返回（early return）**替代嵌套 if-else：先校验参数，验证失败立即 `return`。
- 多参数用对象传入（RO-RO 模式）；返回多字段也用对象，并声明 interface。
- 禁止在回调地狱中处理异步；全面使用 `async/await`。

### 异常处理
- 用 `try/catch` 包裹每个 route handler；catch 块必须返回具体错误信息，不可静默吞掉。
- 预期错误（校验失败、重复、权限不足）用特定 HTTP 状态码返回；非预期错误统一返回 500。

---

## 路由设计

### 双路由架构模式
大型 Express 服务可拆分为多个 Router 文件，职责清晰：

```
routes.ts       → VS Code 扩展 / 原生客户端（authCode in body/query）
app-routes.ts   → 移动 App（authCode in header x-auth-code，含 role）
```

- 每个 Router 文件负责一个客户端类型，**不混用**。
- 用 `// ===== 分组名 =====` 注释对路由分段（成员接口 / 管理员接口 / 资源名）。

### 路由 Handler 模板

```typescript
router.post('/resource', requireAuth, async (req: Request, res: Response) => {
  try {
    const { field } = req.body;
    if (!field) { res.status(400).json({ error: '请提供 field' }); return; }

    const result = await doSomething(field);
    res.json({ ok: true, result });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});
```

**要求**：
- 必填字段校验放在最前；校验失败立即 `return`，不进入业务逻辑。
- 所有 async handler 必须有 try/catch；catch 块必须 `return` 或终止响应。
- 禁止 `res.send()` 混用，统一用 `res.json()`。

---

## 统一响应格式

### 成功响应
```json
{ "ok": true, "data": "..." }
```
- 顶层固定字段 `ok: true`；业务数据作为具名字段附加（不要用 `data` 包裹数组）。

### 错误响应
```json
{ "error": "可读的错误信息" }
```

### HTTP 状态码分类（必须一致）

| 状态码 | 场景 |
|--------|------|
| `400` | 缺少必填字段 / 参数格式错误 |
| `401` | 未提供凭证（Admin Token 场景） |
| `403` | 凭证无效 / 权限不足 |
| `404` | 资源不存在（`changes === 0` 也算） |
| `409` | 唯一性冲突（UNIQUE constraint） |
| `422` | 业务逻辑校验失败（如登录验证失败、账号无效） |
| `500` | 未预期服务端错误 |

---

## 中间件与认证（RBAC）

### 双层守卫模式
```typescript
// 推荐：用 declare global 扩展 Request，消除 (req as any)
declare global {
  namespace Express {
    interface Request {
      authCode?: string;
      role?: string;
      displayName?: string;
    }
  }
}

// 第一层：验证凭证 + 附加 role 到 req
function requireAppAuth(req: Request, res: Response, next: NextFunction): void {
  const authCode = req.headers['x-auth-code'] as string || req.body?.authCode;
  if (!authCode) { res.status(400).json({ error: '请提供授权码' }); return; }
  const validation = validateAuthCode(authCode);
  if (!validation.valid) { res.status(403).json({ error: validation.reason }); return; }
  req.authCode = authCode;
  req.role = lookupRole(authCode);
  next();
}

// 第二层：仅检查 role（必须在第一层之后使用）
function requireAppAdmin(req: Request, res: Response, next: NextFunction): void {
  if (req.role !== 'admin') {
    res.status(403).json({ error: '需要管理员权限' }); return;
  }
  next();
}

// 用法：管理员路由串联两个守卫
router.get('/admin/xxx', requireAppAuth, requireAppAdmin, handler);
```

**原则**：
- 用 `declare global { namespace Express { interface Request {} } }` 扩展 `req` 字段类型，**禁止** `(req as any).field`。
- 中间件必须声明 `void` 返回类型；所有 `return` 路径都必须在 `return` 前调用 `res.xxx()`。
- 永远不在中间件里 `throw`；用 `res.status(xxx).json(...); return;` 终止链。

---

## 数据库操作模式（SQLite / better-sqlite3 风格）

### 计数工具函数

提取到数据库模块（`db.ts`），**禁止**在 route handler 内内联定义：

```typescript
// db.ts — 导出一次，全局复用
export function count(sql: string, ...params: any[]): number {
  return get<{ c: number }>(sql, ...params)?.c || 0;
}

// route handler 中直接调用（不重复定义）
import { get, all, run, count } from './db';

const total = count(`SELECT COUNT(*) as c FROM accounts WHERE frozen = 0`);
const active = count(`SELECT COUNT(*) as c FROM leases WHERE expires_at > ?`, now);
```

### 验证后入库（validate-then-insert）
```typescript
// 先验证（可能耗时，如外部 API 调用）
const auth = await externalValidate(credential);

// 非阻塞辅助信息（失败不阻止主流程）
let extra = {};
try { extra = await enrichData(auth.token); } catch { /* 允许失败 */ }

// 验证通过后入库
const id = crypto.randomUUID();
run(`INSERT INTO table (...) VALUES (?, ?, ?)`, id, ...fields);
```

### 唯一性冲突处理
```typescript
} catch (err: any) {
  if (err.message?.includes('UNIQUE')) {
    res.status(409).json({ error: '该记录已存在' });
  } else {
    res.status(500).json({ error: err.message });
  }
}
```

---

## 安全规范

- **参数化查询**：所有 SQL 必须用占位符 `?`，禁止字符串拼接。
- **敏感信息脱敏**：日志和响应中的邮箱必须脱敏：
  ```typescript
  email.replace(/^(..)[^@]*(@.*)$/, '$1***$2')  // → ab***@domain.com
  ```
- **密码加密存储**：入库前必须加密（`encrypt(password)`），绝不明文。
- **硬编码禁止**：API Key、Token、密钥必须通过 `process.env` 注入；`.env` 不入版本库。
- **批量操作限流**：批量接口必须设置服务端 hard limit（如 `if (items.length > 50) return 400`）。

---

## 批量操作模式

```typescript
const results: { email: string; ok: boolean; error?: string }[] = [];
for (const item of items) {
  try {
    await processOne(item);
    results.push({ email: item.email, ok: true });
  } catch (e: any) {
    const msg = e.message?.includes('UNIQUE') ? '已存在' : e.message;
    results.push({ email: item.email, ok: false, error: msg });
  }
}

const succeeded = results.filter(r => r.ok).length;
res.json({ ok: true, total: items.length, succeeded, failed: items.length - succeeded, results });
```

**规则**：
- 单个失败不中断整体，逐条 try/catch。
- 响应体必须包含 `total / succeeded / failed / results[]`。
- 服务端强制 `items.length > N` 时提前返回 400，不进入循环。

---

## 测试

- 用 **Jest + Supertest** 测试 API 端点（不依赖真实数据库，用内存 SQLite 或 mock）。
- 每个测试文件对应一个路由模块；用 `describe` 分组，`it` 描述单个场景。
- AAA 模式：Arrange（准备数据）→ Act（调用接口）→ Assert（断言响应）。
- 必须覆盖的场景：正常路径 / 缺少参数（400）/ 无效凭证（403）/ 资源不存在（404）/ 重复（409）。

---

## 反模式（禁止）

- ❌ `catch {}` 静默吞错 — 必须返回错误响应或 rethrow
- ❌ SQL 字符串拼接 — 必须用 `?` 占位符
- ❌ `any` 类型滥用 — 用 `unknown` + 类型守卫
- ❌ 同一路由文件既做成员又做管理员（路由分组混淆）
- ❌ 批量操作无 hard limit — 必须服务端限制最大条数
- ❌ 敏感信息明文响应 — 邮箱脱敏、密码不出现在任何响应
- ❌ `res.status(500)` 用于业务错误 — 业务错误用 409/422/404
