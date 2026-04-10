---
name: security-audit
description: 安全审计——编写或审查代码时检查 OWASP Top 10 风险、输入验证、认证授权、密钥管理。涉及安全敏感功能（登录/支付/API/数据库/文件上传）时加载。
---

# Security Audit

> 安全不是功能，是地基。地基有裂缝，楼再高也要塌。

## 何时触发

- 编写/修改认证、授权、登录、注册逻辑
- 处理用户输入（表单、API 参数、文件上传）
- 编写数据库查询（尤其是动态拼接）
- 配置 API 端点权限
- 处理敏感数据（密码、token、支付信息）
- 代码审查中发现潜在安全问题

## OWASP Top 10 速查

每次涉及安全敏感代码时，过一遍：

| # | 风险 | 核心防御 |
|---|------|---------|
| A01 | 访问控制失效 | 默认拒绝，RBAC，服务端校验 |
| A02 | 加密失败 | HTTPS，bcrypt/argon2 哈希密码，AES-256 加密 |
| A03 | 注入 | 参数化查询，ORM，输入验证 |
| A04 | 不安全设计 | 威胁建模，最小权限，纵深防御 |
| A05 | 安全配置错误 | 关闭调试模式，最小化暴露面，安全 headers |
| A06 | 脆弱过时组件 | 定期 `npm audit`，锁定版本 |
| A07 | 认证失败 | MFA，JWT 短过期+刷新，账号锁定 |
| A08 | 数据完整性失败 | 签名验证，CI/CD 安全，SRI |
| A09 | 日志监控不足 | 记录安全事件，异常告警 |
| A10 | SSRF | 白名单 URL，禁止内网访问 |

## 输入验证模式

### 原则：永远不信任外部输入

```typescript
// ❌ 危险：直接使用用户输入
app.get('/user/:id', (req, res) => {
  db.query(`SELECT * FROM users WHERE id = ${req.params.id}`);
});

// ✅ 安全：参数化查询 + 类型验证
app.get('/user/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (isNaN(id) || id <= 0) return res.status(400).json({ error: 'Invalid ID' });
  db.query('SELECT * FROM users WHERE id = $1', [id]);
});
```

### 验证清单

- **类型**：确认参数类型（string/number/boolean）
- **长度**：限制字符串最大长度
- **范围**：数字在合理范围内
- **格式**：邮箱/手机号/URL 用正则校验
- **白名单**：枚举值用白名单，不用黑名单
- **编码**：输出到 HTML 时转义（防 XSS）

## 认证与授权

### JWT 最佳实践

```typescript
// Token 配置
const ACCESS_TOKEN_EXPIRY = '15m';    // 短过期
const REFRESH_TOKEN_EXPIRY = '7d';    // 长刷新
const JWT_ALGORITHM = 'RS256';        // 非对称签名

// ❌ 不要
// - 在 JWT payload 里存密码
// - 用 HS256 + 弱密钥
// - 把 token 存 localStorage（XSS 可窃取）

// ✅ 要做
// - httpOnly + Secure + SameSite cookie 存 token
// - 实现 token 黑名单/吊销
// - 刷新 token 时轮换（rotation）
```

### RBAC 实现模式

```typescript
// 中间件模式
const requireRole = (...roles: string[]) => (req, res, next) => {
  if (!req.user || !roles.includes(req.user.role)) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  next();
};

// 使用
app.delete('/users/:id', requireRole('admin'), deleteUser);
app.get('/profile', requireRole('user', 'admin'), getProfile);
```

## 密钥管理

### 铁律：密钥永不入代码

```bash
# .env（本地开发，已在 .gitignore）
DATABASE_URL=postgresql://...
JWT_SECRET=...
API_KEY=...

# 生产环境：用环境变量或 Vault
# 永远不要：
# - 提交 .env 到 Git
# - 在代码中硬编码密钥
# - 在日志中打印密钥
# - 在错误信息中暴露连接字符串
```

### 检查清单

- [ ] `.env` 在 `.gitignore` 中
- [ ] 无硬编码密钥（搜索 `password=`, `secret=`, `key=`）
- [ ] API Key 有权限范围限制
- [ ] 数据库连接使用最小权限用户

## XSS / CSRF 防御

### XSS

```typescript
// ❌ 危险：直接渲染用户输入
element.innerHTML = userInput;

// ✅ 安全：转义或用 textContent
element.textContent = userInput;
// 或使用框架的自动转义（React JSX, Vue template）

// 安全 Headers
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],  // 禁止内联脚本
    }
  }
}));
```

### CSRF

```typescript
// 使用 CSRF token（非 SPA 场景）
app.use(csrf({ cookie: true }));

// SPA 场景：SameSite cookie + CORS 白名单
app.use(cors({
  origin: ['https://yourdomain.com'],
  credentials: true,
}));
```

## 依赖安全

```bash
# 定期检查
npm audit
npm audit fix

# CI/CD 中自动化
# package.json
"scripts": {
  "security:check": "npm audit --audit-level=high"
}
```

## 安全审查清单（代码审查时逐项过）

- [ ] 所有用户输入已验证和清理
- [ ] 数据库查询使用参数化/ORM
- [ ] 认证端点有速率限制
- [ ] 敏感操作需要授权检查
- [ ] 错误信息不泄露内部细节
- [ ] 密钥不在代码/日志中
- [ ] HTTPS 强制（生产环境）
- [ ] 安全 Headers 已设置（helmet 等）
- [ ] 文件上传有类型和大小限制
- [ ] 第三方依赖无已知高危漏洞
