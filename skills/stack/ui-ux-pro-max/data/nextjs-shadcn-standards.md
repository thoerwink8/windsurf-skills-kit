# Next.js + shadcn/ui 标准规范

> 此文件是 dao-frontend-init 工作流的硬约束参考。
> 每次新建 Next.js 项目或修改 UI 组件时自动加载。

## 1. 按钮尺寸标准 (Button Sizes)

shadcn/ui 默认尺寸偏紧凑（dashboard 导向），着陆页/通用场景需要放大。

| size | 高度 | 字号 | 水平 padding | 触摸目标 |
|------|------|------|-------------|---------|
| `xs` | `h-7` (28px) | `text-xs` (12px) | `px-2.5` | 辅助操作 |
| `sm` | `h-9` (36px) | `text-sm` (14px) | `px-3.5` | 次级按钮 |
| `default` | `h-10` (40px) | `text-sm` (14px) | `px-4` | 标准按钮 |
| `lg` | `h-12` (48px) | `text-base` (16px) | `px-6` | CTA / Hero ≥44px ✅ |
| `icon` | `size-10` (40px) | — | — | 图标按钮 |
| `icon-lg` | `size-12` (48px) | — | — | 大图标按钮 |

**规则**：
- Hero CTA 必须用 `size="lg"` (h-12, 48px)
- Navbar 操作按钮用 `size="sm"` (h-9, 36px)
- 所有按钮加 `cursor-pointer`
- 移动端触摸目标 ≥ 44×44px (WCAG 2.2 Level AA)

## 2. Badge 尺寸标准

| 属性 | 值 |
|------|------|
| 高度 | `h-6` (24px) |
| 字号 | `text-xs` (12px) — 全局最小字号 |
| 内边距 | `px-2.5 py-0.5` |
| 间距 | `gap-1.5` |

## 3. Root Font-Size 锁定（最高优先级）

```css
html {
  font-size: 16px;              /* 锁定 root，所有 rem 计算基于此值 */
  -webkit-text-size-adjust: 100%; /* 防止移动端自动缩放 */
}
```

**为什么**：Tailwind 所有 text-* 工具用 rem。如果 root 不是 16px（浏览器设置/CSS 覆写/扩展），所有字号偏移，产生如 11.375px 这类非标准值。**必须在 globals.css 的 `@layer base` 中显式设置**。

## 4. Type Scale（显式定义在 @theme 中）

必须在 `@theme inline` 中显式声明，不依赖 Tailwind 默认值：

```css
@theme inline {
  --text-xs: 0.75rem;           /* 12px */
  --text-xs--line-height: 1rem;
  --text-sm: 0.875rem;          /* 14px */
  --text-sm--line-height: 1.25rem;
  --text-base: 1rem;            /* 16px */
  --text-base--line-height: 1.5rem;
  --text-lg: 1.125rem;          /* 18px */
  --text-lg--line-height: 1.75rem;
  --text-xl: 1.25rem;           /* 20px */
  --text-xl--line-height: 1.75rem;
}
```

| 级别 | 工具类 | 像素值 | 用途 |
|------|--------|--------|------|
| xs | `text-xs` | 12px | badge, 次级注释, footer 技术栈 |
| sm | `text-sm` | 14px | 辅助文本, 表单 label, 按钮(default/sm) |
| base | `text-base` | 16px | 正文最小值, 卡片描述, 按钮(lg) |
| lg | `text-lg` | 18px | 卡片标题, 小标题 |
| xl | `text-xl` | 20px | Lead 文本, Hero 副标题(mobile) |
| 2xl | `text-2xl` | 24px | 区域标题(mobile) |
| 3xl | `text-3xl` | 30px | h2(desktop) |
| 4xl | `text-4xl` | 36px | h1(mobile) |
| 5xl | `text-5xl` | 48px | h1(tablet) |
| 6xl | `text-6xl` | 60px | h1(desktop hero) |

**铁律**：
- body 正文 ≥ `text-base` (16px)
- 12px (`text-xs`) 仅用于 badge/footer/辅助标注
- **所有计算出的字号必须是整数像素**。如果 DevTools 显示小数 → root font-size 有问题
- h1 必须响应式：`text-4xl md:text-5xl lg:text-6xl`
- 段落 `leading-relaxed` 或 `leading-7`

## 5. oklch 色彩约束

| Token | chroma 最小值 | 说明 |
|-------|-------------|------|
| `--primary` | **0.20** | 主色必须鲜明可辨 |
| `--ring` | **0.20** | 聚焦环与 primary 同调 |
| `--background` | **0.01** | 可感知的色调倾向 |
| `--muted` | **0.02** | 区块底色需有色感 |
| `--secondary` | **0.025** | 次级背景明显区分 |
| `--border` | **0.02** | 边框带色调 |
| `--destructive` | **0.20** | 错误色鲜明 |

**hue 选择**：项目色调统一在 ±15° 以内（如全蓝 240-255）。

## 6. 字体策略

优先级：
1. `next/font/local` + 打包 woff2 (零网络依赖)
2. 系统字体栈：`"Inter", ui-sans-serif, system-ui, -apple-system, sans-serif`
3. `next/font/google` (仅确认网络可达时)

**应用位置**：仅在 `globals.css` 的 `@theme inline` 中设置 `--font-sans`，layout.tsx 通过 `font-sans` 类继承。

## 7. shadcn/ui 初始化标准

```bash
pnpm dlx shadcn@latest init -d    # 默认配置
pnpm dlx shadcn@latest add button card badge -y  # 基础三件套
```

初始化后立即按本文件规范覆写 button/badge 尺寸。

## 8. Biome 配置

- `$schema` 版本必须与 `pnpm ls @biomejs/biome` 输出一致
- CSS parser 开启 `tailwindDirectives: true`
- oklch 数值不写尾零（`0.9` 而非 `0.90`）

## 9. 布局约束

- 全局 `max-w-6xl` 或 `max-w-7xl` 统一容器宽度
- Navbar: `sticky top-0 z-40` + `backdrop-blur-md` + `bg-background/80`
- Navbar 高度: `h-16` (64px)
- Hero 上间距: `pt-28 md:pt-36`
- Feature grid: `md:grid-cols-3 gap-8`
- Section 间距: `py-24`

## 10. 可访问性必检项

- [ ] 装饰图标加 `aria-hidden="true"`
- [ ] 所有 `<img>` 有 `alt`
- [ ] 色彩对比度 ≥ 4.5:1
- [ ] 键盘 tab 可导航
- [ ] `prefers-reduced-motion` 尊重动画偏好
