# Classic new-york + Zinc

shadcn-qt Core uses the classic shadcn/ui `new-york` registry as its visual
profile and Zinc as its neutral light/dark palette. `new-york` controls the
geometry, spacing, elevation, focus states, and interaction rhythm; Zinc
controls semantic colors such as background, foreground, border, and primary.

This is the classic registry profile, not one of the newer Vega, Nova, Maia,
Lyra, Mira, Luma, Rhea, or Sera presets.

## Audited geometry

| Element | Contract |
|---|---|
| Button | 36px; small 32px; large 40px; icon 36px |
| Input and select | 36px, 6px radius, 12px horizontal padding |
| Textarea | 60px minimum, 6px radius |
| Card | 12px radius, semantic border, subtle elevation |
| Checkbox and radio | 16px custom-painted indicator |
| Switch | 36x20px track with an animated 16px thumb |
| Progress | 8px track |
| Dialog | 24px inset, 8px radius, shadow, fade, and dark overlay |

The implementation was audited against the official classic registry entries
for [Button](https://ui.shadcn.com/r/styles/new-york/button.json),
[Input](https://ui.shadcn.com/r/styles/new-york/input.json),
[Card](https://ui.shadcn.com/r/styles/new-york/card.json),
[Checkbox](https://ui.shadcn.com/r/styles/new-york/checkbox.json),
[Switch](https://ui.shadcn.com/r/styles/new-york/switch.json), and
[Dialog](https://ui.shadcn.com/r/styles/new-york/dialog.json).

## Qt translation

Native signals, models, focus behavior, layouts, accessibility hooks, and
Designer properties remain intact. CSS shadows and transitions become Qt
graphics effects and property animations. Glyphs that QSS cannot faithfully
express are painted by the component. Platform font rasterization can vary,
but geometry, semantic states, and hierarchy are automated library contracts.

The repository-level specification is maintained in `docs/STYLE_BASELINE.md`.

shadcn-qt is independent and is not affiliated with shadcn or Vercel.
