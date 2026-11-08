# Tanuki — PROGRESS

> Declarative Python DSL for procedural geometry; compiles to Blender GN, OpenCascade.js, OpenSCAD and JSCAD.

_Last updated: 2026-11-03_

## Legend

| Status | Meaning |
|---|---|
| ⚪ **To Do** | Not started |
| 🟡 **In Progress** | Being worked on (recent or uncommitted changes) |
| 🟢 **Done** | Finished |
| 🔴 **Blocked** | Blocked by something external or an open problem |

**Priority:** `P0 > P1 > P2 > P3` — sections go from highest to lowest priority.
Within a section all tasks have equal priority (`P1 = P1`) and are listed in suggested execution order.

| Level | Meaning |
|---|---|
| P0 | Critical / blocks the project goal |
| P1 | High: next milestone |
| P2 | Medium: planned improvement |
| P3 | Low / exploratory / long term |

## Tasks

### P0 — Critical

| Status | Task | Notes |
|---|---|---|
| 🟢 Done | Immutable IR + DSL + 4 backends (blender, opencascade, openscad, jscad) |  |

### P1 — High

| Status | Task | Notes |
|---|---|---|
| ⚪ To Do | Close per-backend support gaps (OpenCascade / OpenSCAD / JSCAD vs Blender) | Matrix in `src/tanuki/backends/README.md` |
| ⚪ To Do | Blender integration tests in CI | Today only unit tests without Blender |
| 🟢 Done | Blender node registry codegen |  |
| 🟢 Done | Bevel and SVG import | `c2d1f26` |

### P2 — Medium

| Status | Task | Notes |
|---|---|---|
| ⚪ To Do | Reference models/examples | AGENTS.md: there is no `models/` |
| ⚪ To Do | Keep the backend matrix in sync with new ops |  |
| ⚪ To Do | More custom helpers (`dsl/custom`, e.g. mesh analysis) |  |
| 🟢 Done | Documentation and agent instructions | `cd34d18` |

### P3 — Low

| Status | Task | Notes |
|---|---|---|
| ⚪ To Do | Publish Docusaurus docs (`docs/`) |  |

---

_Statuses inferred from READMEs/roadmaps/git on 2026-11-03; adjust anything that does not reflect reality._
