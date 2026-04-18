---
name: react-native-expo
description: Expo React Native TypeScript 开发规范。构建/审查 Expo 移动端代码时自动加载，覆盖组件、样式、导航、状态管理、性能、错误处理、安全、无障碍等。
---

# React Native Expo TypeScript Skill

> Source: windsurf.run community (Krish Kalaria) + 项目实践补充

You are an expert in TypeScript, React Native, Expo, and Mobile UI development.

## Code Style and Structure
- Write concise, technical TypeScript code with accurate examples.
- Use functional and declarative programming patterns; avoid classes.
- Prefer iteration and modularization over code duplication.
- Use descriptive variable names with auxiliary verbs (e.g., `isLoading`, `hasError`).
- Structure files: exported component, subcomponents, helpers, static content, types.

## Naming Conventions
- Use lowercase with dashes for directories (e.g., `components/auth-wizard`).
- Favor named exports for components.

## TypeScript Usage
- Use TypeScript for all code; prefer interfaces over types.
- Avoid enums; use maps instead.
- Use functional components with TypeScript interfaces.
- Use strict mode in TypeScript for better type safety.

## UI and Styling
- Use Expo's built-in components for common UI patterns and layouts.
- Implement responsive design with Flexbox and `useWindowDimensions`.
- Use NativeWind (Tailwind CSS) or styled-components for component styling.
- Implement dark mode support using `useColorScheme` or theme context.
- Ensure high accessibility (a11y) standards using ARIA roles and native accessibility props.
- Leverage `react-native-reanimated` and `react-native-gesture-handler` for performant animations and gestures.

## Safe Area Management
- Use `SafeAreaProvider` from `react-native-safe-area-context` to manage safe areas globally.
- Wrap top-level components with `SafeAreaView` to handle notches, status bars, and other screen insets.
- Avoid hardcoding padding or margins for safe areas; rely on `SafeAreaView` and context hooks.

## Performance Optimization
- Minimize the use of `useState` and `useEffect`; prefer context and reducers for state management.
- Optimize images: use WebP format, include size data, implement lazy loading with `expo-image`.
- Implement code splitting and lazy loading for non-critical components with React's `Suspense`.
- Avoid unnecessary re-renders by memoizing components and using `useMemo` and `useCallback` hooks.
- Use `React.memo` for FlatList `renderItem` components.
- Avoid anonymous functions in JSX `onPress`/`onChangeText` — use `useCallback`.

## Navigation
- Use `expo-router` for file-based routing and navigation.
- Leverage deep linking and universal links for better user engagement.
- Handle Android back button with `BackHandler` in `useFocusEffect`.

## State Management
- Use React Context and `useReducer` for managing global state.
- Leverage `react-query` or SWR for data fetching and caching; avoid excessive API calls.
- For complex state management, consider Zustand or Redux Toolkit.

## Error Handling and Validation
- Implement proper error boundaries at root level.
- **Every mutating API call must show success/error feedback** (Toast for success, Dialog for critical errors).
- Handle errors at the beginning of functions; use early returns for error conditions.
- Avoid unnecessary else statements; use if-return pattern.
- Never swallow errors silently (`catch {}` is forbidden on user-facing paths).
- Use `Zod` for runtime validation where applicable.
- Log errors with Sentry or equivalent in production.

## User Feedback (UX 铁律)
- **Success**: Brief toast notification (1-2s, non-blocking).
- **Loading**: `ActivityIndicator` or skeleton screen during async operations.
- **Error**: Contextual error message (toast for recoverable, dialog for critical).
- **Empty state**: Meaningful illustration/text when lists are empty.
- **Optimistic updates**: Update UI immediately, rollback on failure.
- **Pull-to-refresh**: All data screens must support `RefreshControl`.

## Lists (FlatList)
- Use `FlatList` for 50+ items (never `ScrollView` + `map`).
- Provide `keyExtractor` with stable IDs (never array index).
- Memoize `renderItem` with `React.memo`.
- Use `getItemLayout` for fixed-height items.
- Provide `ListEmptyComponent` for empty states.

## Testing
- Write unit tests using Jest and React Native Testing Library.
- Implement integration tests for critical user flows using Detox.
- Consider snapshot testing for components to ensure UI consistency.

## Security
- Sanitize user inputs to prevent XSS attacks.
- Use `expo-secure-store` for secure storage of sensitive data.
- Ensure secure communication with APIs using HTTPS and proper authentication.

## Accessibility
- Add `accessibilityLabel` to all interactive elements.
- Use `accessibilityRole` for semantic meaning.
- Support screen readers (test with TalkBack/VoiceOver).
- Ensure text scaling and font adjustments.

## Key Conventions
1. Rely on Expo's managed workflow for streamlined development and deployment.
2. Prioritize Mobile Web Vitals (Load Time, Jank, and Responsiveness).
3. Use `expo-constants` for managing environment variables and configuration.
4. Implement `expo-updates` for over-the-air (OTA) updates.
5. Ensure compatibility with iOS and Android by testing on both platforms.

## Pre-Delivery Checklist
- [ ] All API mutations have success/error toast feedback
- [ ] No silent `catch {}` on user-facing paths
- [ ] FlatList items memoized with `React.memo`
- [ ] Interactive elements have `accessibilityLabel`
- [ ] Loading states shown during async operations
- [ ] Empty states handled for all lists
- [ ] Pull-to-refresh on all data screens
- [ ] Dark mode tested
- [ ] Keyboard handling for form screens

## UX Audit & Refactor Patterns (validated in prod)

### 1. Tab-click vs swipe desync (horizontal paging)
When implementing `Pager`-style horizontal `FlatList` with tab strip, the tab button's `onPress` must both:
1. Update the active index state, AND
2. Call `flatListRef.current?.scrollToOffset({ offset: index * pageWidth, animated: true })`
Otherwise tapping the tab updates state but content doesn't scroll.
And `onMomentumScrollEnd` should compute `Math.round(e.nativeEvent.contentOffset.x / pageWidth)` to sync state back from swipe.

### 2. Extract repeated UX primitives
Watch for these duplications across 3+ screens — extract to `components/`:
- **SegmentedPills** `<today/week/month>` style pill row → replace hand-rolled `<Pressable>` maps.
- **EmptyState** `<icon + text + optional hint>` → replace inline `<View><MaterialIcons size=48 /><Text /></View>`.
- **ConsumptionSummary** / **MetricPill** → right-aligned stack of value + label.
Consolidating cuts file size 30-50% and enforces visual consistency.

### 3. Label clarity — avoid internal jargon in user UI
Examples of bad → good rewrites validated in audit:
- `W%` → `周耗%` (weekly quota consumed %)
- `按 W% 排序` → `按周额度剩余`
- `贡献排行` (when content is consumption, not donation) → `消耗排行`
Principle: if a first-time user can't decipher the label without training, rename it.

### 4. Nested `Pressable` and `stopPropagation`
React Native `Pressable` bubbles taps. For nested clickables (inner stat card inside outer row):
```tsx
<Pressable onPress={(e) => { (e as any).stopPropagation?.(); onPress(); }}>
```
Without this, tapping inner stat also fires outer card onPress — causing params to be overridden by the outer navigation.

### 5. Role-gated navigation on shared screens
When a tab/screen is visible to both `admin` and `member` roles but some API calls require admin:
- Wrap the admin-API Pressable in `isAdmin ? <Pressable>{body}</Pressable> : body` to make it display-only for non-admin.
- Don't hide the data itself — just remove the navigation affordance.
- In the destination screen, always `if (!isAdmin) return;` before admin-only API calls.

### 6. Tab visibility + role-scoped sub-tabs pattern
When a previously admin-only top tab needs to be exposed to all members:
1. Remove `isAdmin && <Tabs.Screen>` wrapper in `_layout.tsx` so the tab is always visible.
2. Inside the screen, define `allTabs` with `adminOnly?: boolean` flags, then `const tabs = isAdmin ? allTabs : allTabs.filter(t => !t.adminOnly)`.
3. Snap back to a safe tab if a non-admin lands on an admin-only tab via deep-link: `useEffect(() => { if (!isAdmin && tab === 'adminTab') setTab('overview'); }, [isAdmin, tab])`.
4. In render: `{tab === 'adminTab' && isAdmin && <AdminTab />}` — double guard.

### 7. Filtered deep-link navigation from summary stats
Summary stat on home ("充裕 12" / "偏低 3" / "紧张 1") should navigate to the pre-filtered detail screen, not the unfiltered list:
```tsx
router.push({ pathname: '/(tabs)/pool', params: { filter: 'critical' } })
```
Requires destination screen to accept `?filter=` via `useLocalSearchParams` and pre-set state.

### 8. Date-range filter with weekly bucket fallback
For "7天 / 30天 / 全部" usage-history charts:
- 7d/30d → daily buckets (one bar per day).
- All/60d+ → weekly buckets (Monday-aligned, `weekMs = weekIdx * 7 * 86400000`).
- Keep `dailyChart` interface with `useWeekly: boolean` flag so render code stays uniform.
- Cap data points at ~12 bars for chart readability; aggregate older data into weeks.
