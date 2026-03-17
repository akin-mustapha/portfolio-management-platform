---
name: dashboard-redesign.md
---

You are acting as a senior UI/UX developer with experience building dashboards using Python and Dash.

Your task is to prepare a plan to redesign the dashboard layout while preserving existing functionality where possible.

The redesign should focus on improving usability, visual hierarchy, and analytical workflow.

---

Objective

The dashboard should allow users to quickly:

*	view portfolio KPIs
*	filter data
*	browse assets
*	analyze assets through charts and insights

The layout should prioritize fast navigation between assets and analytical context.

---

Sections

The dashboard must contain the following sections:
*	KPI summary
*	Filter controls
*	Asset table
*	Chart analysis area

---

Layout Structure

The layout should use three main rows.

Row 1 — KPI Summary

A horizontal KPI row containing:
*	Portfolio Value
*	Total Invested
*	Unrealized P&L
*	Realized P&L
*	Beta

Important behavior:
*	KPIs should always represent portfolio-level metrics
*	Selecting an individual asset must NOT change the KPI values
*	The timeframe filter should affect KPI calculations
*	KPIs should update when the timeframe changes but remain portfolio-scoped

Example:

User selects AAPL → KPIs remain portfolio metrics
User changes timeframe to 3M → KPIs update for that timeframe

---

Row 2 — Filter Controls

This row should contain:
*	Timeframe selector (1M, 3M, 6M, 1Y, All)
*	Add Tag button
*	Create Tag button
*	Advanced Filter toggle

Advanced filter behavior:
*	The Advanced Filter button toggles visibility of a filter panel
*	This panel may include controls such as:
*	custom date ranges
*	asset filters
*	tag filters
*	additional analytical filters

---

Row 3 — Analysis Workspace

This row contains two panels.

Left panel:
*	Asset table
*	Scrollable list of assets
*	Selectable rows
*	The existing navigation footer must remain visible under the asset table

The footer should remain fixed below the table and preserve its current behavior.

Right panel:
*	Chart analysis area
*	Tabbed interface

Tabs include:
*	Portfolio
*	Valuation
*	Risk
*	Opportunities

---

Panel Behaviour

The left and right panels should be resizable.

Users should be able to drag a divider between the panels.

Constraints:
*	Left panel has a minimum and maximum width
*	Asset table must remain scrollable
*	Navigation footer must remain visible at the bottom
*	Right panel should expand or shrink responsively

---

Chart Behaviour

The chart panel should adapt its layout depending on available width.

Example behavior:

Wide layout:

Chart A | Chart B
Chart C | Chart D

Narrow layout:

Chart A
Chart B
Chart C
Chart D

Charts should rearrange automatically when the user resizes the workspace.

---

Interaction Model

Primary interaction flow:
	1.	User selects an asset from the table
	2.	KPI row remains unchanged
	3.	Chart tabs update to reflect the selected asset

Switching tabs changes the analytical perspective while maintaining the selected asset.

Example:

Asset = Apple
Tabs = Portfolio | Valuation | Risk | Opportunities

Each tab represents a different analytical lens.

---

Constraints
*	Preserve existing navigation footer
*	Avoid unnecessary refactoring of working components
*	Focus primarily on layout and interaction improvements
*	Existing functionality should remain intact unless clearly improved

---

Deliverables

Provide a redesign plan that includes:
	1.	Proposed Dash layout structure
	2.	Component hierarchy
	3.	Suggested Dash components
	4.	Callback and interaction architecture
	5.	Any UI/UX improvements that enhance analytical workflow


ASKYOURQUESTION