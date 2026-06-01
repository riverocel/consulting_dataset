from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_output"


SLIDES = [
    {
        "num": 1,
        "section_title": "Executive Summary",
        "title": "Executive Summary",
        "headline": "DPHA must address workforce continuity before vacancies and retirements compound",
        "visual": "No chart. Build six KPI callout boxes from executive_summary.csv.",
        "layout": [
            "Use a clean 16:9 executive summary layout.",
            "Top 15%: slide title and headline.",
            "Middle 55%: six KPI boxes in a 3 x 2 grid.",
            "Right side or lower-right: small 'Recommended action' box.",
            "Bottom 12%: full-width takeaway banner.",
        ],
        "text": [
            "Headline: DPHA has a meaningful continuity risk that requires immediate, targeted action.",
            "Recommendation label: Approve Phase 1 knowledge capture, workforce planning governance, and retirement-transition analysis.",
            "Source note: Retirement eligibility and payroll values are estimated using available fields.",
        ],
        "kpis": [
            "Authorized positions: 366",
            "Occupied positions: 329",
            "Vacancy rate: 10.1%",
            "Actual occupied payroll: $35.8M",
            "Estimated retirement eligible share: 44.4%",
            "Vacant authorized payroll: $3.8M",
        ],
        "banner": "So what: DPHA should act now, but the first decision should be targeted stabilization and governance, not broad workforce reduction.",
        "notes": [
            "Open by framing the issue as mission continuity, not just staffing counts.",
            "The retirement figure is an estimated proxy based on available age and service fields.",
            "Vacant authorized payroll signals planning capacity, but it should not be described as immediately available savings.",
            "The executive ask is to approve Phase 1 work and validate the financial levers before committing to structural changes.",
        ],
        "avoid": [
            "Do not say the vacant authorized payroll is already savings.",
            "Do not present retirement eligibility as an official HR determination.",
            "Do not imply the full transformation recommendation is already quantitatively proven.",
        ],
        "appendix": "executive_summary.csv; assumptions_and_limitations.csv",
        "quality": "KPI boxes reconcile to executive_summary.csv; no chart added; takeaway banner is explicit.",
    },
    {
        "num": 2,
        "section_title": "Diagnostic Framework",
        "title": "Diagnostic Framework",
        "headline": "A structured diagnostic links workforce facts to executive decisions",
        "visual": "chart_diagnostic_approach_framework.png",
        "layout": [
            "Top 15%: slide title and headline.",
            "Center 55%: insert framework chart at full width.",
            "Below chart: one-line caption on how the framework supports decisions.",
            "Bottom 12%: full-width takeaway banner.",
        ],
        "text": [
            "Caption: Six lenses connect roster facts to risk prioritization and decision sequencing.",
            "Small note under 'Scenario Modeling': Qualitative decision frame; quantify in Phase 1.",
            "Use labels only: Demographics, Retirement Exposure, Payroll Concentration, Vacancy Analysis, Risk Prioritization, Scenario Modeling.",
        ],
        "kpis": [
            "No numeric KPI boxes required.",
            "Optional small source tag: Inputs from workforce, payroll, vacancy, retirement, and risk-matrix outputs.",
        ],
        "banner": "So what: The analysis is designed to identify where leadership action is most urgent, not to report isolated metrics.",
        "notes": [
            "This slide should reassure the client that the analysis has a clear management logic.",
            "Each lens maps to a leadership question: who is at risk, where is cost concentrated, and where should intervention start.",
            "Scenario modeling is not yet a quantified savings model.",
            "Use this framework as the governance structure for the next phase of analysis.",
        ],
        "avoid": [
            "Do not over-explain methodology on the slide.",
            "Do not imply scenario modeling has quantified FTE or savings impacts yet.",
            "Do not let the framework become a filler slide; tie it to decisions.",
        ],
        "appendix": "data_dictionary.csv; missing_values.csv; summary_statistics.csv; summary_statistics_categorical.csv",
        "quality": "Framework image is readable; scenario modeling caveat appears in small text; slide answers how the analysis drives decisions.",
    },
    {
        "num": 3,
        "section_title": "Workforce Aging & Succession Risk",
        "title": "Workforce Aging & Succession Risk",
        "headline": "Late-career concentration creates a near-term succession challenge",
        "visual": "chart_occupied_headcount_by_age_band.png",
        "layout": [
            "Top 15%: slide title and headline.",
            "Left 65%: insert age-band chart.",
            "Right 30%: three concise callout boxes.",
            "Bottom 12%: full-width takeaway banner.",
        ],
        "text": [
            "Callout header: Succession exposure is broad, not isolated.",
            "Source note: Age reflects current roster data; it is not a retirement forecast.",
            "Keep the slide language focused on succession exposure; save detailed retirement claims for Slide 4.",
        ],
        "kpis": [
            "Average occupied age: 54.4",
            "Age 55+ headcount: 194",
            "Largest age band: 60-64 with 90 employees",
            "Age 55+ share: 59.0%",
        ],
        "banner": "So what: DPHA should capture critical knowledge and succession coverage before late-career attrition accelerates.",
        "notes": [
            "This is one of the strongest evidence slides because it comes directly from the demographic summary.",
            "Do not equate age 55+ with guaranteed retirement; position it as succession exposure.",
            "The average age of 54.4 shows the issue is enterprise-wide rather than isolated to a few outliers.",
            "Use this slide to establish continuity risk before moving into retirement eligibility and branch prioritization.",
        ],
        "avoid": [
            "Do not say all employees age 55+ are retirement risks.",
            "Do not speculate on retirement intent.",
            "Do not add detailed age tables to the main slide.",
        ],
        "appendix": "workforce_demographics_summary.csv; summary_statistics.csv",
        "quality": "Chart is slide-ready; labels are legible; callouts reinforce succession exposure rather than retirement certainty.",
    },
    {
        "num": 4,
        "section_title": "Retirement Exposure by Branch",
        "title": "Retirement Exposure by Branch",
        "headline": "Retirement risk is uneven and must be managed branch by branch",
        "visual": "chart_retirement_eligibility_by_branch.png",
        "layout": [
            "Top 15%: slide title and headline.",
            "Center 60%: insert retirement eligibility by branch chart.",
            "Right or lower-right: small methodology caution box.",
            "Bottom 12%: full-width takeaway banner.",
        ],
        "text": [
            "Caution box: Estimated proxy based on age and years of service; excludes DOB, retirement system, and service-credit details.",
            "Callout: Current + near-term risk totals an estimated 194 occupied positions.",
            "Chart redesign required before final deck: move legend outside or below the plot because it currently overlaps the lower-right plot area.",
        ],
        "kpis": [
            "Currently eligible: 146 employees",
            "Currently eligible share: 44.4% of occupied headcount",
            "Current + near-term risk: 194 occupied positions",
            "Highest composite risk segment: Central offices / non-branch",
        ],
        "banner": "So what: Retirement transition planning should be sequenced by branch and role criticality, not handled as a uniform enterprise action.",
        "notes": [
            "Treat the retirement categories as an analytical proxy, not an official HR eligibility determination.",
            "The core insight is uneven exposure across branches and central functions.",
            "Branch-level plans should include documentation, cross-training, and succession coverage for critical roles.",
            "Acknowledge the missing fields openly if the client asks about precision.",
        ],
        "avoid": [
            "Do not say HR has confirmed retirement eligibility.",
            "Do not present the proxy as a forecast of who will retire.",
            "Do not use the current chart without fixing the legend overlap.",
        ],
        "appendix": "retirement_eligibility_analysis.csv; assumptions_and_limitations.csv",
        "quality": "Legend moved outside or below chart; methodology caveat appears on slide; headline emphasizes branch-specific action.",
    },
    {
        "num": 5,
        "section_title": "Payroll Concentration & Financial Exposure",
        "title": "Payroll Concentration & Financial Exposure",
        "headline": "Payroll concentration creates both cost pressure and reinvestment capacity",
        "visual": "chart_actual_payroll_by_gs_grade_slide_ready.png",
        "layout": [
            "Top 15%: slide title and headline.",
            "Left 65%: insert slide-ready payroll-by-grade chart.",
            "Right 30%: financial exposure callouts and caution note.",
            "Bottom 12%: full-width takeaway banner.",
        ],
        "text": [
            "Callout header: Validate funding flexibility before using vacancy dollars.",
            "Source note: Payroll is estimated from GS_Payscale by grade and step; excludes locality, benefits, premium pay, and non-salary costs.",
            "Use 'planning pool to validate with finance' instead of 'available savings.'",
        ],
        "kpis": [
            "Actual occupied payroll: $35.8M",
            "Top payroll grade: GS-12 at $17.4M",
            "Vacant authorized payroll: $3.8M",
            "Authorized payroll including vacancies: $39.6M",
        ],
        "banner": "So what: Vacancy dollars may help fund transition, but only after finance validates budget flexibility and mission impacts.",
        "notes": [
            "This slide bridges workforce risk to financial exposure.",
            "Payroll values are salary estimates from the provided GS pay scale and should not be described as full compensation cost.",
            "GS-12 concentration indicates where cost exposure sits, not where cuts should automatically occur.",
            "Use careful language: vacant authorized payroll is an opportunity signal, not guaranteed reinvestment funding.",
        ],
        "avoid": [
            "Do not call vacant authorized payroll immediate savings.",
            "Do not suggest cutting GS-12 simply because it is the largest payroll category.",
            "Do not use the original payroll chart if the slide-ready version is available.",
        ],
        "appendix": "payroll_summary.csv; chart_actual_payroll_by_branch.png; assumptions_and_limitations.csv",
        "quality": "Use slide-ready chart, not the original; funding caveat is visible; all financial language is assumption-aware.",
    },
    {
        "num": 6,
        "section_title": "Branch Prioritization Matrix",
        "title": "Branch Prioritization Matrix",
        "headline": "Leadership should prioritize branches where continuity and cost exposure overlap",
        "visual": "chart_branch_priority_matrix.png",
        "layout": [
            "Top 15%: slide title and headline.",
            "Center 60%: insert branch priority matrix.",
            "Right side: short interpretation box explaining axes and bubble size.",
            "Bottom 12%: full-width takeaway banner.",
        ],
        "text": [
            "Interpretation box: X-axis = vacancy rate; Y-axis = current + near-term retirement risk; bubble size = occupied payroll; color = composite risk score.",
            "Footnote: Composite score uses normalized vacancy, retirement, and payroll exposure; weights are judgment-based proxies.",
            "Optional note: Consider a branch-only version excluding central/non-branch records if leadership wants operating branch comparisons only.",
        ],
        "kpis": [
            "Top segment: Central offices / non-branch",
            "Retirement risk rate: 87.5%",
            "Vacancy rate: 17.9%",
            "Overall risk score: 89.3",
        ],
        "banner": "So what: Start Phase 1 where workforce continuity risk and financial materiality overlap most clearly.",
        "notes": [
            "This is a prioritization tool, not a definitive personnel decision model.",
            "Central offices / non-branch may require a separate follow-up cut because it aggregates distinct central functions.",
            "The matrix helps move the discussion from enterprise averages to sequencing.",
            "Be transparent that the weights are judgment-based and should be validated with leadership priorities.",
        ],
        "avoid": [
            "Do not treat the composite score as mathematically definitive.",
            "Do not compare central offices to branches without acknowledging the grouping issue.",
            "Do not recommend personnel actions solely from this matrix.",
        ],
        "appendix": "workforce_risk_matrix.csv; vacancy_analysis.csv; payroll_summary.csv; retirement_eligibility_analysis.csv",
        "quality": "Axes and bubble size are explained; proxy-weight caveat is included; central/non-branch caveat is ready for questions.",
    },
    {
        "num": 7,
        "section_title": "Strategic Recommendation",
        "title": "Strategic Recommendation",
        "headline": "Balanced transformation best protects mission readiness while creating savings capacity",
        "visual": "chart_transformation_scenario_comparison.png",
        "layout": [
            "Top 15%: slide title and headline.",
            "Center 60%: insert strategic options comparison table image.",
            "Right or lower-right: recommendation callout.",
            "Bottom 12%: full-width takeaway banner.",
        ],
        "text": [
            "Recommendation callout: Select balanced transformation as the Phase 1 design principle.",
            "Caveat: Qualitative decision frame; quantify savings, FTE movement, role redesign, and mission impacts in Phase 1.",
            "Show only three options: Aggressive reduction, Balanced transformation, Minimal disruption.",
        ],
        "kpis": [
            "No numeric KPI boxes required.",
            "Show option dimensions: financial impact, mission risk, workforce continuity, recommended role.",
        ],
        "banner": "So what: Balanced transformation is the right starting point because it sequences savings around mission-critical continuity risk.",
        "notes": [
            "This is the least quantitatively proven slide, so be explicit that it is a design recommendation.",
            "Aggressive reduction may create faster savings but risks mission and knowledge continuity.",
            "Minimal disruption avoids short-term pain but does not solve the retirement exposure.",
            "The next step is quantified scenario modeling before final workforce actions.",
        ],
        "avoid": [
            "Do not imply the scenarios are a completed financial model.",
            "Do not claim a specific savings target from this slide.",
            "Do not overstate balanced transformation as risk-free.",
        ],
        "appendix": "transformation_scenarios.csv; assumptions_and_limitations.csv",
        "quality": "Caveat is visible; recommendation is clear; no unsupported savings numbers appear on the slide.",
    },
    {
        "num": 8,
        "section_title": "Roadmap & Executive Ask",
        "title": "Roadmap & Executive Ask",
        "headline": "Act now to avoid unmanaged knowledge loss",
        "visual": "chart_implementation_roadmap.png",
        "layout": [
            "Top 15%: slide title and headline.",
            "Center 50%: insert three-phase roadmap.",
            "Lower 25%: executive ask box with three bullets.",
            "Bottom 12%: full-width takeaway banner.",
        ],
        "text": [
            "Phase 1, 0-6 months: Stabilize and capture knowledge.",
            "Phase 2, 6-18 months: Modernize and transition.",
            "Phase 3, 18+ months: Optimize and govern.",
            "Executive ask: Approve Phase 1 knowledge capture, workforce planning governance, and retirement-transition analysis.",
            "60-day deliverables: critical-role list; branch succession heatmap; vacancy disposition rules; monthly governance cadence.",
        ],
        "kpis": [
            "No numeric KPI boxes required.",
            "Use time horizons as the primary anchors: 0-6 months, 6-18 months, 18+ months.",
        ],
        "banner": "So what: The decision today is to launch controlled stabilization, not to finalize every workforce action.",
        "notes": [
            "Close with a concrete decision request.",
            "The roadmap sequences stabilization before modernization and optimization.",
            "Leadership should assign owners and require a 60-day branch-level retirement and vacancy action plan.",
            "The purpose is to prevent unmanaged knowledge loss while validating budget and role-design assumptions.",
        ],
        "avoid": [
            "Do not leave the ask generic.",
            "Do not imply all implementation details are solved.",
            "Do not frame the roadmap as a broad reduction program.",
        ],
        "appendix": "executive_summary.csv; workforce_risk_matrix.csv; assumptions_and_limitations.csv",
        "quality": "Ask is concrete and time-bound; roadmap has exactly three phases; final banner reinforces immediate controlled action.",
    },
]


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def write_markdown() -> None:
    lines: list[str] = []
    lines.append("# Manual Slide Build Guide: DPHA Workforce Executive Presentation")
    lines.append("")
    lines.append("Build exactly 8 main slides. Keep detailed evidence in appendix only. Use assumption-aware language throughout: `estimated`, `proxy`, and `based on available fields` where relevant.")
    lines.append("")
    lines.append("Recommended deck style: senior public health executive audience, restrained consulting layout, one message per slide, minimal text, and a bottom takeaway banner on every slide.")
    lines.append("")

    for slide in SLIDES:
        lines.append(f"## Slide {slide['num']}: {slide['section_title']}")
        lines.append("")
        lines.append(f"**Slide title:** {slide['title']}")
        lines.append("")
        lines.append(f"**Executive headline:** {slide['headline']}")
        lines.append("")
        lines.append(f"**Exact visual to insert:** {slide['visual']}")
        lines.append("")
        lines.append("**Exact layout instructions:**")
        lines.append(bullet_list(slide["layout"]))
        lines.append("")
        lines.append("**Exact text to put on slide:**")
        lines.append(bullet_list(slide["text"]))
        lines.append("")
        lines.append("**KPI callout boxes:**")
        lines.append(bullet_list(slide["kpis"]))
        lines.append("")
        lines.append(f"**Bottom takeaway banner:** {slide['banner']}")
        lines.append("")
        lines.append("**Speaker notes, 3-5 sentences:**")
        lines.append(" ".join(slide["notes"]))
        lines.append("")
        lines.append("**What to avoid saying:**")
        lines.append(bullet_list(slide["avoid"]))
        lines.append("")
        lines.append(f"**Appendix backup files:** {slide['appendix']}")
        lines.append("")
        lines.append(f"**Quality check:** {slide['quality']}")
        lines.append("")

    lines.append("## Appendix Guidance")
    lines.append("")
    lines.append("Do not add appendix pages to the 8-slide main deck count. Use appendix files only to answer questions or support a deeper discussion.")
    lines.append("")
    lines.append("- Data definitions: data_dictionary.csv")
    lines.append("- Data quality: missing_values.csv; assumptions_and_limitations.csv")
    lines.append("- Demographics detail: workforce_demographics_summary.csv; summary_statistics.csv")
    lines.append("- Payroll detail: payroll_summary.csv; chart_actual_payroll_by_branch.png")
    lines.append("- Vacancy detail: vacancy_analysis.csv; chart_vacancy_rate_by_branch.png; chart_vacancy_rate_by_gs_grade.png")
    lines.append("- Retirement detail: retirement_eligibility_analysis.csv")
    lines.append("- Risk prioritization detail: workforce_risk_matrix.csv")
    lines.append("- Scenario frame: transformation_scenarios.csv")
    lines.append("")
    lines.append("## Chart Redesign Flags")
    lines.append("")
    lines.append("- `chart_retirement_eligibility_by_branch.png`: redesign before final deck production. Move the legend outside or below the plot because it currently overlaps the lower-right plot area.")
    lines.append("- `chart_actual_payroll_by_gs_grade.png`: use `chart_actual_payroll_by_gs_grade_slide_ready.png` in the main deck instead. Keep the original as backup only.")
    lines.append("- `chart_branch_priority_matrix.png`: chart is usable, but be prepared to explain that central/non-branch records are grouped and risk-score weights are judgment-based proxies.")
    lines.append("")

    (OUT / "manual_slide_build_guide.md").write_text("\n".join(lines), encoding="utf-8")


def write_checklist() -> None:
    rows = []
    for slide in SLIDES:
        rows.append(
            {
                "slide_number": slide["num"],
                "slide_title": slide["section_title"],
                "must_include_visual": slide["visual"],
                "must_include_metrics": "; ".join(slide["kpis"]),
                "exact_takeaway_banner": slide["banner"],
                "appendix_backup": slide["appendix"],
                "quality_check": slide["quality"],
            }
        )
    pd.DataFrame(rows).to_csv(OUT / "manual_slide_build_checklist.csv", index=False)


def main() -> None:
    write_markdown()
    write_checklist()


if __name__ == "__main__":
    main()
