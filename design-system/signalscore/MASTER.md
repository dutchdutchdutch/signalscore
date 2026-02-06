# Design System Master File

> **LOGIC:** When building a specific page, first check `design-system/pages/[page-name].md`.
> If that file exists, its rules **override** this Master file.
> If not, strictly follow the rules below.

---

**Project:** SignalScore
**Generated:** 2026-02-03
**Style Direction:** System Minimal (Linear/Vercel Aesthetic)

---

## Global Rules

### Color Palette (Dark Mode System)

| Role | Hex | CSS Variable | Usage |
|------|-----|--------------|-------|
| Background | `#0A0A0A` | `--bg-base` | Main app background (Near black, not pitch black) |
| Surface | `#171717` | `--bg-surface` | Cards, Sidebar (Subtle contrast) |
| Border | `#262626` | `--border-subtle` | 1px borders (The primary structure) |
| Text Primary | `#EDEDED` | `--text-primary` | Headings, Key Data |
| Text Secondary | `#A1A1AA` | `--text-secondary` | Labels, Metadata |
| Accent/Success | `#22C55E` | `--color-success` | High Scores, Positive Signals |
| Warning | `#F59E0B` | `--color-warning` | Medium Scores |
| Error/Danger | `#EF4444` | `--color-danger` | Low Scores, Missing Data |

**Philosophy:** Opaque surfaces. High contrast text. Zero gradients. Colors are semantic only (Signal = Color, Decoration = None).

### Typography

- **Font Family:** `Inter`, system-ui, sans-serif. (+ `JetBrains Mono` for tabular numbers).
- **Weights:** Regular (400), Medium (500). Bold (700) is reserved *only* for huge numbers.
- **Tracking:** Tight (-0.02em) for headings. Normal for body.
- **Google Fonts:** [Inter](https://fonts.google.com/specimen/Inter)

**CSS Import:**
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
```

### Spacing & Layout

- **Grid:** 4px baseline grid.
- **Card Padding:** Compact (`16px`).
- **Gap:** Tight (`12px`).
- **Borders:** 1px solid `var(--border-subtle)`. No shadows. No glow.

### Component Specs

#### Buttons
```css
.btn-primary {
  background: #EDEDED;
  color: #0A0A0A;
  border: 1px solid #EDEDED;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
}

.btn-secondary {
  background: transparent;
  color: #EDEDED;
  border: 1px solid #262626; /* Subtle border */
  border-radius: 6px;
}
```

#### Cards (The "Block")
```css
.card {
  background: #0A0A0A; /* Opaque */
  border: 1px solid #262626;
  border-radius: 8px; /* Small radius */
  box-shadow: none; /* Flat */
}
```

#### Sparklines/Charts
- **Line Color:** `#22C55E` (Success) or `#525252` (Neutral).
- **Line Width:** 1.5px.
- **Fill:** Zero opacity (Line only) or hard vertical gradient.

---

## Pattern: Data-First Dashboard

**Core Concept:** "The database is the UI."
Users trust data that looks raw and unpolished. Marketing fluff reduces trust.

### Layout Strategy
1.  **Top Bar:** Global Search (The primary interaction). 
2.  **Sidebar:** Navigation (Minimal icons).
3.  **Main Content:** Grid of Data Cards.
4.  **Density:** High. Information density > White space.

### Interaction Model
- **Hover:** Immediate color shift (e.g., border color `#262626` -> `#525252`). No layouts shifting.
- **Transitions:** `<100ms`. Instant feedback.

---

## Anti-Patterns (Forbidden)
- ❌ **Gradients** (Except for subtle data viz).
- ❌ **Drop Shadows** (Use borders for hierarchy).
- ❌ **Rounded Corners > 8px** (Keep it sharp).
- ❌ **Decorative Icons** (Icons must represent actions or data).
- ❌ **Glassmorphism / Blur** (Keep surfaces opaque for rendering speed).

---

## Pre-Delivery Checklist
- [ ] Font is Inter.
- [ ] Background is `#0A0A0A` (Not `#000`).
- [ ] Borders are 1px `#262626`.
- [ ] No drop shadows used on cards.
- [ ] Numbers use `font-variant-numeric: tabular-nums`.
