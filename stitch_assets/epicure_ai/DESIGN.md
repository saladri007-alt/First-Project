---
name: Epicure AI
colors:
  surface: '#131315'
  surface-dim: '#131315'
  surface-bright: '#39393b'
  surface-container-lowest: '#0e0e10'
  surface-container-low: '#1c1b1d'
  surface-container: '#201f21'
  surface-container-high: '#2a2a2c'
  surface-container-highest: '#353437'
  on-surface: '#e5e1e4'
  on-surface-variant: '#e4bebc'
  inverse-surface: '#e5e1e4'
  inverse-on-surface: '#313032'
  outline: '#ab8987'
  outline-variant: '#5b403f'
  surface-tint: '#ffb3b1'
  primary: '#ffb3b1'
  on-primary: '#680011'
  primary-container: '#ff535a'
  on-primary-container: '#5b000e'
  inverse-primary: '#bb162c'
  secondary: '#e9c349'
  on-secondary: '#3c2f00'
  secondary-container: '#af8d11'
  on-secondary-container: '#342800'
  tertiary: '#b9c8de'
  on-tertiary: '#233143'
  tertiary-container: '#8392a6'
  on-tertiary-container: '#1c2b3c'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#ffe088'
  secondary-fixed-dim: '#e9c349'
  on-secondary-fixed: '#241a00'
  on-secondary-fixed-variant: '#574500'
  tertiary-fixed: '#d4e4fa'
  tertiary-fixed-dim: '#b9c8de'
  on-tertiary-fixed: '#0d1c2d'
  on-tertiary-fixed-variant: '#39485a'
  background: '#131315'
  on-background: '#e5e1e4'
  surface-variant: '#353437'
typography:
  display:
    fontFamily: Plus Jakarta Sans
    fontSize: 3.5rem
    fontWeight: '700'
    lineHeight: 4rem
    letterSpacing: -0.03em
  display-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 2.25rem
    fontWeight: '700'
    lineHeight: 2.75rem
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 2.5rem
    fontWeight: '600'
    lineHeight: 3rem
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.75rem
    fontWeight: '600'
    lineHeight: 2.25rem
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.75rem
    fontWeight: '600'
    lineHeight: 2.25rem
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.25rem
    fontWeight: '600'
    lineHeight: 1.75rem
    letterSpacing: -0.01em
  title-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.125rem
    fontWeight: '500'
    lineHeight: 1.5rem
    letterSpacing: 0em
  body-lg:
    fontFamily: Inter
    fontSize: 1.125rem
    fontWeight: '400'
    lineHeight: 1.75rem
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: 1.5rem
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: 1.25rem
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: '600'
    lineHeight: 1rem
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 0.6875rem
    fontWeight: '500'
    lineHeight: 0.875rem
    letterSpacing: 0.06em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 3rem
  margin-mobile: 1.25rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style
This design system captures high-end gastronomy through the precision lens of artificial intelligence. It addresses discerning diners, sommeliers, and culinary travelers who value curation over crowdsourcing. The aesthetic merges luxury editorial sophistication with a futuristic, atmospheric digital experience. 

The aesthetic is built on a dark, layered foundation with glassmorphism and radiant micro-accents. Interfaces resemble a private evening dining room: matte obsidian depths, smoky translucent surfaces, hairline glass borders, and vivid points of crimson and gold light that guide the eye naturally to AI-driven insights and reservations.

## Colors
The palette balances deep spatial absorption with sharp, intentional illumination. 

- **Primary Accent (`#E23744`)**: Vibrant culinary crimson. Reserved for conversion actions, active navigation states, interactive highlights, and high-confidence AI match percentages.
- **Secondary Accent (`#D4AF37`)**: Polished champagne gold. Dedicated to prestige tier markers, Michelin star indicators, AI recommendation sparkles, and elevated review badges.
- **Tertiary Accent (`#94A3B8`)**: Cool slate. Manages meta-information, contextual microcopy, deactivated controls, and secondary UI metadata.
- **Neutral Base (`#0A0A0C`)**: Matte obsidian canvas. Paired with elevated charcoal tiers:
  - Surface Low: `#121216` (base cards and section blocks)
  - Surface Mid: `#1A1A22` (interactive hover states, floating menus, and popovers)
  - Surface High: `#242430` (elevated modals and sticky headers)
- **Hairline Dividers**: `rgba(255, 255, 255, 0.06)` for structure without visual noise.

## Typography
The typographic architecture pairs the expressive geometric precision of Plus Jakarta Sans for titles with the pragmatic legibility of Inter for body text and metadata. 

- Display and Headline tiers feature tight tracking (`-0.01em` to `-0.03em`) and crisp white values (`#F8FAFC`) to evoke editorial authority.
- Body copy relies on neutral off-white (`#E2E8F0`) to preserve contrast against the deep black canvas without causing glare.
- Label tiers use uppercase formatting with widened tracking (`0.05em` to `0.06em`) in `#94A3B8` for menu categorizations, tags, and AI attributes.

## Layout & Spacing
The layout follows a fluid 12-column grid anchored by a 1440px maximum content width. 

- **Desktop (1024px+)**: 12 columns, 1.5rem gutters, and 3rem side margins. Asymmetrical card arrangements and generous vertical rhythm establish a gallery feel.
- **Tablet (768px - 1023px)**: 8 columns, 1.25rem gutters, and 2rem side margins. Horizontal scrolls compress dense restaurant discovery cards.
- **Mobile (<768px)**: 4 columns, 1rem gutters, and 1.25rem screen margins. Interfaces simplify into full-bleed vertical stacks and bottom-anchored sheets.

Vertical rhythm relies on multiples of 8px, prioritizing negative space around photography and curation metrics to avoid crowded culinary interfaces.

## Elevation & Depth
Depth avoids heavy drop shadows, utilizing luminous translucent layers, delicate borders, and subtle glows:

- **Level 0 (Canvas)**: Solid `#0A0A0C` background.
- **Level 1 (Default Containers & Cards)**: Charcoal `#121216` at 85% opacity, `backdrop-filter: blur(16px)`, surrounded by a hairline boundary (`rgba(255, 255, 255, 0.06)`).
- **Level 2 (Hover & Floating Elements)**: Charcoal `#1A1A22` at 92% opacity, `backdrop-filter: blur(24px)`, hairline boundary (`rgba(255, 255, 255, 0.12)`), with an ambient shadow of `0 16px 32px -8px rgba(0, 0, 0, 0.65)`.
- **Level 3 (Overlays & Dialogs)**: Deep matte `#242430` at 96% opacity, `backdrop-filter: blur(32px)`, with a subtle crimson or gold ambient under-glow (`0 0 40px -10px rgba(226, 55, 68, 0.12)` or `0 0 40px -10px rgba(212, 175, 55, 0.1)`).

## Shapes
A unified rounded geometry (`0.5rem` base, scaling to `1rem` on larger cards and `1.5rem` on floating overlays) balances modern interface design with high-end luxury. Controls maintain refined, gentle corners, avoiding circular pills except for compact metadata badges and status pills.

## Components

### Buttons
- **Primary**: Solid `#E23744` fill with white text, transitioning on hover to an inner crimson glow (`box-shadow: 0 0 20px rgba(226, 55, 68, 0.4)`).
- **Secondary/AI Action**: Frosted `#1A1A22` container with a hairline metallic border (`rgba(212, 175, 55, 0.4)`), gold text, and a micro-glow on hover.
- **Ghost**: Transparent fill with `#94A3B8` text, shifting to `#F8FAFC` with an ambient `rgba(255, 255, 255, 0.05)` background fill on interaction.

### Cards (Restaurant & Sommelier Curation)
- Built on Level 1 elevation with an aspect-ratio-locked imagery container at the top.
- Hairline borders (`rgba(255, 255, 255, 0.06)`) illuminate subtly on hover to `rgba(226, 55, 68, 0.3)`.
- Image gradients use a linear mask transitioning from `transparent` to `#121216` at the card body seam.

### AI Match & Rating Chips
- **AI Recommendation Badge**: Matte charcoal pill with a thin `#D4AF37` hairline border, gold sparkle icon, and micro-label typography.
- **Filter Chips**: Dark translucent pills (`#1A1A22`) with `#94A3B8` labels; selected states transition to primary crimson tint (`rgba(226, 55, 68, 0.15)`) with a `#E23744` hairline ring.

### Input Fields
- Understated `#121216` background with an inset 1px border (`rgba(255, 255, 255, 0.08)`).
- On focus: shifts to `#1A1A22`, with the border transitioning to active crimson (`#E23744`) accompanied by a 2px outer glow (`rgba(226, 55, 68, 0.2)`).

### Lists & Menu Items
- Separated by razor-thin `rgba(255, 255, 255, 0.04)` borders.
- Interactive rows show a subtle horizontal crimson light indicator (`2px` wide) on hover along the leading edge.

### Checkboxes & Radios
- Square-round (4px radius) for checkboxes, circular for radios, surfaced in `#1A1A22` with a `rgba(255, 255, 255, 0.15)` border.
- Selected state fills with `#E23744`, rendering a clean white checkmark or center pip.