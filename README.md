# ICT Asset Relationship & Dependency Dashboard

> **Interactive visualisation of ICT assets, roles, and third-party dependencies — built for DORA Register of Information compliance.**

![Dashboard screenshot](docs/ICT Asset Dashboard_Sample)

A single-file, browser-based tool that reads your existing Excel asset registers and renders an interactive force-directed network graph. Instantly see how hardware, software, and information assets connect to organisational roles, departments, and third-party providers — no server, no installation, no data leaves your browser.

---

## Why this exists

Financial entities regulated under **DORA (EU 2022/2554)** must maintain a **Register of Information** (RoI) mapping ICT assets to business functions, internal roles, and ICT third-party service providers. Building and maintaining that view from flat spreadsheets is slow and error-prone.

This dashboard turns your existing asset registers into a live, explorable dependency map — in one click.

---

## Key features

- **Force-directed network graph** — powered by D3.js v7; drag, zoom, and explore up to 300 nodes
- **Five node types**: Hardware · Software · Information · Roles · ROI/Third-party Providers
- **Four KPI tiles** — total assets, classification risk breakdown (High/Medium/Low), external network exposure, and uncontracted software
- **Layer toggling** — incrementally add/remove asset layers for performance at scale
- **Criticality & department filters** — drill into high-risk or externally exposed assets instantly
- **Click-to-inspect** — info chip shows asset metadata, owner, classification, and linked dependencies
- **Search highlight** — find any asset or role across the entire graph
- **Upload your own workbook** — drop any `.xlsx` / `.xlsm` file; the dashboard parses it client-side with SheetJS
- **Zero dependencies to install** — one `.html` file, runs in any modern browser offline

---

## Live demo

> **[Try it now → GitHub Pages link here]**

Upload the sample workbook (`sample_data.xlsx`) to explore the dashboard with synthetic data.

---

## How to use

### 1. Prepare your Excel workbook

Your workbook must contain the following sheets (names must match exactly):

| Sheet name | Contents |
|---|---|
| `Fixed Asset Register (IT)` | Hardware assets — prefixed `HW_` |
| `Software Asset Register` | Software/application assets — prefixed `APP_` |
| `Information Asset Register` | Information assets — prefixed `INF_` |
| `Staff` | People / staff directory |
| `RoleIDs` | Role definitions |
| `Dependency Map` | Asset-to-role dependency rows (Role_ID must start `R_`) |
| `ROI` | Register of Information — ICT third-party providers (provider name in column C) |

### 2. Open the dashboard

Open `index.html` in any modern browser (Chrome, Edge, Firefox, Safari).

### 3. Load your data

Click **Load data file**, browse to your workbook, and the graph renders automatically.

### 4. Explore

- **Checkboxes** in the left panel toggle asset layers
- **Filters** narrow by department, criticality, or external exposure
- **Click any node** to see its full metadata and linked assets
- **Search** highlights matching nodes across the graph
- **KPI tiles** are clickable — clicking "External exposure" filters to exposed assets

---

## Tech stack

| Library | Version | Purpose |
|---|---|---|
| [D3.js](https://d3js.org) | v7.8.5 | Force-directed graph, SVG rendering |
| [SheetJS (xlsx)](https://sheetjs.com) | community | Client-side Excel parsing |
| Vanilla JS / CSS | — | UI, filtering, interactions |

No build step. No framework. No backend.

---

## Roadmap / ideas for contribution

- [ ] Export graph as PNG / SVG
- [ ] DORA Article 28 third-party risk scoring overlay
- [ ] CSV export of dependency relationships
- [ ] Configurable sheet-name mapping (remove hardcoded names)
- [ ] Dark/light theme toggle
- [ ] Sample data generator script

Contributions are very welcome — please open an issue first to discuss what you'd like to change.

---

## Contributing

1. Fork the repository
2. Make your changes to `index.html`
3. Test with a real or sample workbook
4. Open a pull request with a brief description of the change and why

Since this is a single-file tool, there's no build process — just edit and reload.

---

## Licence

MIT — free to use, adapt, and share. Attribution appreciated.

---

## About

Built by **Mark Camilleri** — technology risk and operational resilience professional with expertise in ICT governance, DORA compliance, and fintech/regtech transformation.

[LinkedIn](https://www.linkedin.com/in/markcamille) · [Issues & feedback](https://github.com/mcamilleri21/ict-asset-dashboard/issues)
