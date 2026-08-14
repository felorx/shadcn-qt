# Visual baseline: classic new-york + Zinc

shadcn-qt Core targets the classic shadcn/ui `new-york` registry with the Zinc
base palette. This is a visual and interaction contract for Qt widgets; it is
not the newer Vega/Nova/Maia preset system and it does not copy React or Radix
source code.

The baseline was audited on 2026-08-14 against the official registry at:

- <https://ui.shadcn.com/r/styles/new-york/button.json>
- <https://ui.shadcn.com/r/styles/new-york/input.json>
- <https://ui.shadcn.com/r/styles/new-york/card.json>
- <https://ui.shadcn.com/r/styles/new-york/checkbox.json>
- <https://ui.shadcn.com/r/styles/new-york/switch.json>
- <https://ui.shadcn.com/r/styles/new-york/dialog.json>

## Geometry contract

| Element | Classic new-york contract | Qt implementation |
|---|---|---|
| Button | 36px; small 32px; large 40px; icon 36px | Fixed control heights and matching horizontal padding |
| Input/select | 36px, 6px radius, 12px horizontal padding | Native editor APIs with new-york metrics |
| Input OTP | Contiguous 36px slots, shared dividers | Only outer corners are rounded; focused slots restore a complete ring |
| Textarea | 60px minimum, 6px radius | Native multiline editor with matching minimum height |
| Card | 12px radius, border, elevation | QFrame plus a subtle drop-shadow effect |
| Checkbox/radio | 16px indicator in a 24px row | 3px edge inset keeps borders and focus rings inside the paint clip |
| Switch | 36x20px track, 16px thumb | Animated custom-painted thumb with checked translation |
| Progress | 8px track | Native progress model with new-york track geometry |
| TabPane / adopted QTabWidget | Chrome-style connected document tabs | Transparent strip, distinct connected page surface, uniform title/close padding, and the same outward-shoulder silhouette for selection and inactive hover |
| Dialog | 24px content inset, 8px radius, dark overlay | Frameless modal QDialog, parent overlay, shadow, and fade |

Qt exposes only one graphics-effect shadow per widget, whereas the browser
presets compose multiple low-opacity layers. The Qt approximation therefore
uses deliberately short blur radii and 5–9% opacity so borders stay crisp and
surfaces do not acquire a heavy grey halo.

## Color contract

`packages/design-tokens/tokens.json` is authoritative. Its light and dark
semantic values are the classic Zinc palette, including `#09090b` foreground,
`#18181b` primary, `#f4f4f5` secondary/muted, and `#e4e4e7` border/input in
light mode. Applications may override semantic colors without changing the
new-york geometry.

## Qt translation rules

- Native signals, models, focus behavior, layouts, accessibility hooks, and
  Designer properties remain intact.
- Browser-only DOM composition becomes QWidget composition.
- CSS shadows and transitions become Qt graphics effects and property
  animations.
- Lucide/Radix state glyphs that Qt cannot express in QSS are painted by the
  component itself.
- Opted-in stock QtWidgets receive the same tokens through component and
  `nativeKind` properties. Checkbox/radio glyphs, editor arrows, elevation,
  and calendar cells use reversible adapter enhancements when QSS alone is
  insufficient.
- `TabPane` and opted-in `QTabWidget` share one Chrome-style document-tab
  contract while the existing `Tabs` component keeps its shadcn segmented
  appearance. The selected tab is joined directly to its page by outward
  curved lower shoulders rather than a boxed lower border. The surrounding
  strip stays transparent, while the active tab/page surface remains distinct
  from its host window. Movable, closable, current-index, page ownership, and
  signals remain the native QTabWidget implementation.
- Rendering can vary slightly with platform font rasterization and display
  scaling, but control geometry, semantic states, and visual hierarchy are
  tested as library contracts.

## Native QtWidgets regression contract

The Gallery contains four pages composed exclusively from stock QtWidgets:
forms, data views, containers, and window chrome. Each page has committed light
and dark screenshot baselines. The regression suite downsamples the images and
checks both mean color delta and the proportion of materially changed pixels,
which catches palette/layout regressions while tolerating small font-rendering
differences.

System-native dialogs and platform window decorations remain operating-system
surfaces unless the application requests Qt's non-native implementation. MDI
title chrome can therefore vary while its content and surrounding tokens stay
themed.

shadcn-qt is independent and is not affiliated with shadcn or Vercel.
