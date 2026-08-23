# Design Spec: Modern Engineering Diagrams for Sector 2 & Sector 3

- **Date:** 2026-08-24
- **Topic:** AI Engineering Handbook — Diagram Modernization
- **Target Sectors:** Sector 2 (AI Agents & Swarms, `agent_ch1.md` - `agent_ch12.md`), Sector 3 (Frontier AI & Infrastructure, `frontier_ch1.md` - `frontier_ch8.md`)

---

## 1. Objectives & Guidelines

1. **Replace Legacy ASCII Diagrams**: Fully substitute raw terminal/box-drawing code blocks with publication-grade, interactive Mermaid diagrams.
2. **Zero Generic AI Emojis**: Avoid generic AI emojis (🧠, ⚡, 🎯, 🚀, 💡, 🔥, ❌, ✅) inside diagram node labels.
3. **Professional Engineering Aesthetics**:
   - Use clean, structured subgraphs with logical containment.
   - Use standard engineering and computer science notation: mathematical formulas ($c_t$, $W_{DKV}$, $\dim(h_t)$), system labels (`[Host Application]`, `[Transport Layer]`, `[Checkpointer]`, `[Runtime Sandbox]`).
   - Use high-contrast, sector-aligned CSS tokens with rounded corners and distinct border accents.
4. **Theme Adaptability**:
   - Seamlessly adapt between dark theme and light theme in `index.html`.
   - Support vector scaling during PDF generation and export.

---

## 2. Sector Visual Color Tokens

### Sector 2: AI Agents & Swarms
- **Backgrounds**: Slate Dark `#0b0f19` / Deep Emerald `#064e3b` / Deep Indigo `#1e1b4b` / Deep Cyan `#0e7490`
- **Borders & Strokes**: Emerald `#34d399` / Indigo `#818cf8` / Cyan `#22d3ee` / Slate `#334155`
- **Text**: Crisp White `#f8fafc` / Subtext `#94a3b8`

### Sector 3: Frontier AI Breakthroughs & Infrastructure
- **Backgrounds**: Slate Dark `#0b0f19` / Deep Amber `#78350f` / Deep Rose `#831843` / Deep Violet `#4c1d95`
- **Borders & Strokes**: Gold `#fbbf24` / Rose `#f43f5e` / Violet `#a78bfa` / Slate `#334155`
- **Text**: Crisp White `#f8fafc` / Subtext `#94a3b8`

---

## 3. Scope & Inventory

- **Sector 2**: 12 Chapters (`agent_ch1.md` – `agent_ch12.md`), 12 primary architecture diagrams.
- **Sector 3**: 8 Chapters (`frontier_ch1.md` – `frontier_ch8.md`), 14 deep-dive architecture diagrams.
- **Total Diagrams**: 26 modern engineering flowcharts and system diagrams.
