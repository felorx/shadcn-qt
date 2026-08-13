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
| Textarea | 60px minimum, 6px radius | Native multiline editor with matching minimum height |
| Card | 12px radius, border, elevation | QFrame plus a subtle drop-shadow effect |
| Checkbox/radio | 16px indicator | Antialiased Qt painting for the check and radio glyphs |
| Switch | 36x20px track, 16px thumb | Animated custom-painted thumb with checked translation |
| Progress | 8px track | Native progress model with new-york track geometry |
| Dialog | 24px content inset, 8px radius, dark overlay | Frameless modal QDialog, parent overlay, shadow, and fade |

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
- Rendering can vary slightly with platform font rasterization and display
  scaling, but control geometry, semantic states, and visual hierarchy are
  tested as library contracts.

shadcn-qt is independent and is not affiliated with shadcn or Vercel.
