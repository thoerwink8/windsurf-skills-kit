---
name: database-patterns
description: 数据库设计与优化——Schema 设计、查询优化、Migration 管理、ORM 模式（TypeORM/Prisma）。涉及数据库建模、慢查询、数据迁移时加载。
---

# Database Patterns

> 数据是水，Schema 是河道。河道设计好，水自然流畅。

## 何时触发

- 设计新数据表/集合
- 编写复杂查询或报表
- 遇到慢查询/性能问题
- 执行数据迁移（Migration）
- 选择/配置 ORM
- 设计索引策略

## Schema 设计原则

### 三范式（作为起点，非教条）

| 范式 | 规则 | 何时违反 |
|------|------|---------|
| 1NF | 每列原子值，无重复组 | 几乎不违反 |
| 2NF | 非主属性完全依赖主键 | 几乎不违反 |
| 3NF | 非主属性不传递依赖 | 读多写少场景可适度反范式 |

### 实用准则

```
✅ 做：
- 主键用 UUID 或自增 ID（不用业务字段）
- 时间字段统一 UTC（created_at, updated_at）
- 软删除用 deleted_at 而非 is_deleted
- 枚举值用字符串而非数字（可读性）
- 金额用整数存（分），不用浮点

❌ 不做：
- 不在一张表存 50+ 列（考虑拆分）
- 不用 JSON 列存可查询数据（除非 NoSQL 场景）
- 不在表名/列名用保留字
- 不用复合主键（除关联表）
```

### 关系设计

```typescript
// 一对多：外键在"多"的一方
// users (1) -> posts (N)
// posts 表有 user_id 外键

// 多对多：关联表
// users (N) <-> roles (N)
// user_roles 表有 user_id + role_id

// 一对一：外键在任一方（通常在"扩展"方）
// users (1) <-> profiles (1)
// profiles 表有 user_id 外键
```

## 查询优化

### N+1 问题（最常见性能杀手）

```typescript
// ❌ N+1：1次查用户 + N次查帖子
const users = await User.find();
for (const user of users) {
  user.posts = await Post.find({ userId: user.id }); // N 次查询！
}

// ✅ Eager Loading：1-2 次查询
// TypeORM
const users = await User.find({ relations: ['posts'] });

// Prisma
const users = await prisma.user.findMany({
  include: { posts: true },
});
```

### 索引策略

```sql
-- 必须索引：
-- 1. 外键列
-- 2. WHERE 常用过滤列
-- 3. ORDER BY 排序列
-- 4. JOIN 关联列

-- 复合索引遵循最左前缀
CREATE INDEX idx_posts_user_status ON posts(user_id, status);
-- 可匹配：WHERE user_id = ? AND status = ?
-- 可匹配：WHERE user_id = ?
-- 不可匹配：WHERE status = ?（跳过了 user_id）

-- 不要过度索引：
-- 写操作多的表，每个索引都是写入开销
-- 基数低的列（如 boolean）索引收益低
```

### 分页

```typescript
// ❌ OFFSET 分页（大偏移量慢）
SELECT * FROM posts ORDER BY id LIMIT 20 OFFSET 10000;

// ✅ 游标分页（恒定性能）
SELECT * FROM posts WHERE id > :lastId ORDER BY id LIMIT 20;

// Prisma 游标分页
const posts = await prisma.post.findMany({
  take: 20,
  skip: 1,
  cursor: { id: lastId },
  orderBy: { id: 'asc' },
});
```

## Migration 最佳实践

### 原则

```
✅ 做：
- 每次变更一个 migration 文件
- migration 必须可回滚（up + down）
- 先部署 migration，再部署代码
- 大表变更用渐进式（先加列，再填数据，最后删旧列）
- 生产环境 migration 在低峰期执行

❌ 不做：
- 不手动改生产数据库 Schema
- 不在 migration 中写业务逻辑
- 不删除已执行的 migration 文件
- 不重命名列（先加新列→迁移数据→删旧列）
```

### 破坏性变更安全模式

```
# 重命名列（3步，跨2次部署）
1. 添加新列 + 双写逻辑
2. 迁移历史数据
3. 删除旧列 + 移除双写

# 删除列（2步）
1. 代码停止使用该列（部署）
2. Migration 删除列（部署）
```

## ORM 模式

### TypeORM

```typescript
// Entity 定义
@Entity()
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  email: string;

  @Column({ select: false }) // 默认不查密码
  password: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @DeleteDateColumn() // 软删除
  deletedAt: Date;

  @OneToMany(() => Post, post => post.author)
  posts: Post[];
}

// Repository 模式
const userRepo = dataSource.getRepository(User);
const users = await userRepo.find({
  where: { status: 'active' },
  relations: ['posts'],
  order: { createdAt: 'DESC' },
  take: 20,
});

// QueryBuilder（复杂查询）
const result = await userRepo
  .createQueryBuilder('user')
  .leftJoinAndSelect('user.posts', 'post')
  .where('user.status = :status', { status: 'active' })
  .andWhere('post.createdAt > :date', { date: lastWeek })
  .getMany();
```

### Prisma

```typescript
// schema.prisma
model User {
  id        String   @id @default(uuid())
  email     String   @unique
  password  String
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Post {
  id       String @id @default(uuid())
  title    String
  author   User   @relation(fields: [authorId], references: [id])
  authorId String

  @@index([authorId])
}

// 查询
const users = await prisma.user.findMany({
  where: { status: 'ACTIVE' },
  include: { posts: { where: { createdAt: { gt: lastWeek } } } },
  orderBy: { createdAt: 'desc' },
  take: 20,
});

// 事务
const [user, post] = await prisma.$transaction([
  prisma.user.create({ data: userData }),
  prisma.post.create({ data: postData }),
]);
```

## 连接管理

```typescript
// 连接池配置
// TypeORM
{
  type: 'postgres',
  extra: {
    max: 20,              // 最大连接数
    idleTimeoutMillis: 10000,
  },
}

// Prisma（通过 URL 参数）
DATABASE_URL="postgresql://...?connection_limit=20&pool_timeout=10"

// ✅ 生产环境要点：
// - 连接池大小 = CPU核数 × 2 + 磁盘数（起点）
// - 设置空闲超时，避免连接泄漏
// - Serverless 场景用连接池代理（PgBouncer / Prisma Accelerate）
```

## 审查清单

- [ ] Schema 遵循命名约定（snake_case，复数表名）
- [ ] 所有外键列有索引
- [ ] 查询无 N+1 问题（检查 ORM 日志）
- [ ] 分页使用游标而非 OFFSET（大数据集）
- [ ] Migration 可回滚
- [ ] 敏感数据加密存储（密码哈希，PII 加密）
- [ ] 连接池配置合理
- [ ] 无原始 SQL 拼接（用参数化查询）
