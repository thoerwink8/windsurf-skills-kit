#!/usr/bin/env node
/**
 * scaffold-nextjs.mjs — Next.js 项目脚手架
 *
 * 确定性的机械操作全部固化在此脚本，AI Skill 只做创意层。
 *
 * Usage:
 *   node scaffold-nextjs.mjs <project-root> [--name web] [--skip-create] [--dry-run]
 *
 * Examples:
 *   node scaffold-nextjs.mjs d:\frank\resume-project              # 全量：create-next-app + biome + shadcn + 尺寸覆写
 *   node scaffold-nextjs.mjs d:\frank\resume-project --skip-create # 增量：跳过 create-next-app，只补 biome/shadcn/覆写
 *   node scaffold-nextjs.mjs d:\frank\resume-project --dry-run     # 只输出会做什么，不执行
 *
 * 完成后 AI Skill 接手：设计系统生成 → 色彩填充 globals.css → 页面构建
 */

import { execSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, resolve } from "node:path";

// ─── CLI Parsing ───────────────────────────────────────────────
const args = process.argv.slice(2);
const projectRoot = resolve(args.find((a) => !a.startsWith("--")) || ".");
const webName = args.includes("--name")
  ? args[args.indexOf("--name") + 1]
  : "web";
const skipCreate = args.includes("--skip-create");
const dryRun = args.includes("--dry-run");

const webDir = join(projectRoot, webName);
const log = (msg) => console.log(`[scaffold] ${msg}`);
const run = (cmd, cwd = webDir) => {
  log(`> ${cmd}`);
  if (!dryRun) execSync(cmd, { cwd, stdio: "inherit" });
};

// ─── Detection ─────────────────────────────────────────────────
const hasPackageJson = existsSync(join(webDir, "package.json"));
const hasButton = existsSync(join(webDir, "components", "ui", "button.tsx"));
const hasGlobals = existsSync(join(webDir, "app", "globals.css"));
const globalsHasOklch =
  hasGlobals &&
  readFileSync(join(webDir, "app", "globals.css"), "utf-8").includes("oklch");

log(`Project root: ${projectRoot}`);
log(`Web dir:      ${webDir}`);
log(
  `Detection: package.json=${hasPackageJson} button=${hasButton} oklch=${globalsHasOklch}`,
);

if (hasPackageJson && hasButton && globalsHasOklch) {
  log("✅ 前端基建已就绪，无需脚手架。Skill 可直接接手。");
  process.exit(0);
}

// ─── Phase 1: Create Next.js App ───────────────────────────────
if (!hasPackageJson && !skipCreate) {
  log("Phase 1: create-next-app@latest");
  run(
    `pnpm create next-app@latest ${webName} --typescript --tailwind --eslint=false --app --use-pnpm --skip-install`,
    projectRoot,
  );
  run("pnpm install");
} else if (!hasPackageJson && skipCreate) {
  log("⚠️  --skip-create but no package.json. Nothing to scaffold.");
  process.exit(1);
} else {
  log("Phase 1: SKIP (package.json exists)");
}

// ─── Phase 2: Biome ────────────────────────────────────────────
const hasBiome = existsSync(join(webDir, "biome.json"));
if (!hasBiome) {
  log("Phase 2: Install Biome + config");
  run("pnpm add -D @biomejs/biome");

  // Get installed version for schema URL
  let biomeVersion = "2.4.13";
  if (!dryRun) {
    try {
      const out = execSync("pnpm ls @biomejs/biome --json", {
        cwd: webDir,
        encoding: "utf-8",
      });
      const parsed = JSON.parse(out);
      // Extract version from pnpm ls output
      const deps = parsed?.[0]?.devDependencies?.["@biomejs/biome"];
      if (deps?.version) biomeVersion = deps.version;
    } catch {
      /* fallback to default */
    }
  }

  const biomeConfig = {
    $schema: `https://biomejs.dev/schemas/${biomeVersion}/schema.json`,
    organizeImports: { enabled: true },
    formatter: { indentStyle: "tab", indentWidth: 2, lineWidth: 100 },
    linter: {
      enabled: true,
      rules: { recommended: true },
    },
    css: {
      formatter: { enabled: true },
      linter: { enabled: true },
      parser: { tailwindDirectives: true },
    },
  };

  if (!dryRun) {
    writeFileSync(
      join(webDir, "biome.json"),
      JSON.stringify(biomeConfig, null, 2) + "\n",
    );
  }
  log("biome.json written");

  // Remove ESLint artifacts if present
  for (const f of [
    ".eslintrc.json",
    ".eslintrc.js",
    ".eslintrc.cjs",
    "eslint.config.mjs",
    "eslint.config.js",
  ]) {
    const p = join(webDir, f);
    if (existsSync(p) && !dryRun) {
      const { unlinkSync } = await import("node:fs");
      unlinkSync(p);
      log(`Removed ${f}`);
    }
  }

  // Add npm scripts for biome
  if (!dryRun) {
    const pkgPath = join(webDir, "package.json");
    const pkg = JSON.parse(readFileSync(pkgPath, "utf-8"));
    pkg.scripts = {
      ...pkg.scripts,
      lint: "biome check .",
      format: "biome format --write .",
      typecheck: "tsc --noEmit",
    };
    // Remove ESLint-based lint if present
    delete pkg.scripts["lint:next"];
    writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + "\n");
    log("package.json scripts updated");
  }
} else {
  log("Phase 2: SKIP (biome.json exists)");
}

// ─── Phase 3: shadcn/ui ───────────────────────────────────────
if (!hasButton) {
  log("Phase 3: shadcn init + base components");
  run("pnpm dlx shadcn@latest init -d");
  run("pnpm dlx shadcn@latest add button card badge -y");

  // ─── Phase 3b: Apply size overrides ──────────────────────────
  // Strategy: exact substring matching (not regex), because shadcn uses
  // unquoted TS keys (sm:) not JSON keys ("sm":). Regex is too fragile.
  log("Phase 3b: Override button/badge sizes (nextjs-shadcn-standards)");

  const buttonPath = join(webDir, "components", "ui", "button.tsx");
  if (existsSync(buttonPath) && !dryRun) {
    let src = readFileSync(buttonPath, "utf-8");

    // Each pair: [exact old substring, new substring]
    const replacements = [
      // default: h-8 → h-10, gap-1.5 → gap-2, px-2.5 → px-4
      [
        "h-8 gap-1.5 px-2.5 has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2",
        "h-10 gap-2 px-4 has-data-[icon=inline-end]:pr-3 has-data-[icon=inline-start]:pl-3",
      ],
      // xs: h-6 → h-7
      ["xs: \"h-6 gap-1", "xs: \"h-7 gap-1"],
      // sm: h-7 → h-9, px-2.5 → px-3.5, text-[0.8rem] → text-sm
      [
        "h-7 gap-1 rounded-[min(var(--radius-md),12px)] px-2.5 text-[0.8rem]",
        "h-9 gap-1.5 rounded-[min(var(--radius-md),12px)] px-3.5 text-sm",
      ],
      // lg: h-9 → h-12, add text-base, px-2.5 → px-6
      [
        "h-9 gap-1.5 px-2.5 has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2",
        "h-12 gap-2 px-6 text-base has-data-[icon=inline-end]:pr-4 has-data-[icon=inline-start]:pl-4",
      ],
      // icon: size-8 → size-10
      ['icon: "size-8"', 'icon: "size-10"'],
      // icon-lg: size-9 → size-12
      ['"icon-lg": "size-9"', '"icon-lg": "size-12"'],
    ];

    let appliedCount = 0;
    for (const [oldStr, newStr] of replacements) {
      if (src.includes(oldStr)) {
        src = src.replace(oldStr, newStr);
        appliedCount++;
      }
    }

    writeFileSync(buttonPath, src);
    log(`button.tsx: ${appliedCount}/${replacements.length} size overrides applied`);

    if (appliedCount < replacements.length) {
      log(
        "⚠️  Some button overrides didn't match — shadcn API may have changed. Manual review recommended.",
      );
    }
  }

  const badgePath = join(webDir, "components", "ui", "badge.tsx");
  if (existsSync(badgePath) && !dryRun) {
    let src = readFileSync(badgePath, "utf-8");
    // Badge: h-5 → h-6, px-2 py → px-2.5 py (exact match near boundary)
    src = src.replace(" h-5 ", " h-6 ");
    src = src.replace(" gap-1 ", " gap-1.5 ");
    src = src.replace(" px-2 ", " px-2.5 ");
    writeFileSync(badgePath, src);
    log("badge.tsx sizes overridden");
  }
} else {
  log("Phase 3: SKIP (button.tsx exists)");
}

// ─── Phase 4: Layout cleanup ──────────────────────────────────
const layoutPath = join(webDir, "app", "layout.tsx");
if (existsSync(layoutPath) && !dryRun) {
  let layout = readFileSync(layoutPath, "utf-8");
  const hadGoogleFonts = layout.includes("next/font/google");
  if (hadGoogleFonts) {
    // Remove Google Fonts imports
    layout = layout.replace(
      /import\s*\{[^}]*\}\s*from\s*["']next\/font\/google["'];?\n?/g,
      "",
    );
    // Remove font variable instantiations
    layout = layout.replace(
      /const\s+\w+\s*=\s*\w+\(\{[^}]*\}\);?\n?/g,
      "",
    );
    // Clean className that references font variables
    layout = layout.replace(
      /\$\{[\w.]+\}\s*/g,
      "",
    );
    writeFileSync(layoutPath, layout);
    log("layout.tsx: Google Fonts removed (system font stack will be set by AI Skill)");
  }
}

// ─── Phase 5: globals.css template ─────────────────────────────
if (!globalsHasOklch && hasGlobals && !dryRun) {
  log("Phase 5: globals.css — writing oklch placeholder structure");
  // We write the STRUCTURE with placeholder values.
  // The AI Skill fills in actual colors based on design system generation.
  const cssTemplate = `@import "tailwindcss";

@custom-variant dark (&:is(.dark *));

@theme inline {
  --radius: 0.625rem;
  --font-sans: "Inter", ui-sans-serif, system-ui, -apple-system, sans-serif;
  --radius-sm: calc(var(--radius) * 0.6);
  --radius-md: calc(var(--radius) * 0.8);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) * 1.4);
  --radius-2xl: calc(var(--radius) * 1.8);
  --radius-3xl: calc(var(--radius) * 2.2);
  --radius-4xl: calc(var(--radius) * 2.6);
}

/* ─── Light Mode ─── */
/* TODO: AI Skill fills oklch values via ui-ux-pro-max design system */
:root {
  --background: oklch(0.97 0.014 245);
  --foreground: oklch(0.15 0.05 245);
  --card: oklch(0.995 0.003 245);
  --card-foreground: oklch(0.15 0.05 245);
  --popover: oklch(0.995 0.003 245);
  --popover-foreground: oklch(0.15 0.05 245);
  --primary: oklch(0.55 0.24 255);
  --primary-foreground: oklch(0.99 0 0);
  --secondary: oklch(0.93 0.03 245);
  --secondary-foreground: oklch(0.22 0.08 245);
  --muted: oklch(0.94 0.025 245);
  --muted-foreground: oklch(0.45 0.05 245);
  --accent: oklch(0.93 0.03 245);
  --accent-foreground: oklch(0.22 0.08 245);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.9 0.025 245);
  --input: oklch(0.9 0.025 245);
  --ring: oklch(0.55 0.24 255);
  --chart-1: oklch(0.55 0.24 255);
  --chart-2: oklch(0.65 0.2 200);
  --chart-3: oklch(0.55 0.18 160);
  --chart-4: oklch(0.65 0.22 145);
  --chart-5: oklch(0.72 0.19 70);
  --radius: 0.625rem;
  --sidebar: oklch(0.98 0.01 245);
  --sidebar-foreground: oklch(0.15 0.05 245);
  --sidebar-primary: oklch(0.55 0.24 255);
  --sidebar-primary-foreground: oklch(0.99 0 0);
  --sidebar-accent: oklch(0.93 0.03 245);
  --sidebar-accent-foreground: oklch(0.22 0.08 245);
  --sidebar-border: oklch(0.9 0.025 245);
  --sidebar-ring: oklch(0.55 0.24 255);
}

/* ─── Dark Mode ─── */
.dark {
  --background: oklch(0.13 0.03 250);
  --foreground: oklch(0.95 0.01 245);
  --card: oklch(0.17 0.035 250);
  --card-foreground: oklch(0.95 0.01 245);
  --popover: oklch(0.17 0.035 250);
  --popover-foreground: oklch(0.95 0.01 245);
  --primary: oklch(0.65 0.24 250);
  --primary-foreground: oklch(0.12 0.03 250);
  --secondary: oklch(0.22 0.04 250);
  --secondary-foreground: oklch(0.95 0.01 245);
  --muted: oklch(0.22 0.04 250);
  --muted-foreground: oklch(0.65 0.04 245);
  --accent: oklch(0.22 0.04 250);
  --accent-foreground: oklch(0.95 0.01 245);
  --destructive: oklch(0.704 0.191 22.216);
  --border: oklch(1 0 0 / 12%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.65 0.24 250);
  --chart-1: oklch(0.65 0.24 250);
  --chart-2: oklch(0.58 0.2 200);
  --chart-3: oklch(0.55 0.18 160);
  --chart-4: oklch(0.65 0.22 145);
  --chart-5: oklch(0.72 0.19 70);
  --sidebar: oklch(0.15 0.035 250);
  --sidebar-foreground: oklch(0.95 0.01 245);
  --sidebar-primary: oklch(0.65 0.24 250);
  --sidebar-primary-foreground: oklch(0.12 0.03 250);
  --sidebar-accent: oklch(0.22 0.04 250);
  --sidebar-accent-foreground: oklch(0.95 0.01 245);
  --sidebar-border: oklch(1 0 0 / 12%);
  --sidebar-ring: oklch(0.65 0.24 250);
}

@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}
`;
  writeFileSync(join(webDir, "app", "globals.css"), cssTemplate);
  log("globals.css: oklch template written (blue placeholder, AI Skill will customize)");
}

// ─── Done ──────────────────────────────────────────────────────
log("");
log("═══════════════════════════════════════════════════");
log("✅ 脚手架完成。以下由 AI Skill (ui-ux-pro-max) 接手：");
log("   1. 运行 --design-system 生成项目专属设计系统");
log("   2. 根据设计系统调整 globals.css 的 oklch 色彩值");
log("   3. 构建业务页面（Hero / Features / etc.）");
log("   4. 运行验证（typecheck + lint + build）");
log("═══════════════════════════════════════════════════");
