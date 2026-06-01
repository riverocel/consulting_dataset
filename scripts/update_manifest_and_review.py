from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_output"


CHART_METADATA = {
    "chart_actual_payroll_by_branch.png": {
        "purpose": "Appendix backup showing branch-level occupied payroll exposure.",
        "executive_insight": "Payroll exposure varies by branch and should be considered when sequencing workforce actions.",
    },
    "chart_actual_payroll_by_gs_grade.png": {
        "purpose": "Original payroll-by-grade view; use as backup to the slide-ready version.",
        "executive_insight": "GS-12 payroll dominates the cost profile, but the original chart is less presentation-ready.",
    },
    "chart_actual_payroll_by_gs_grade_slide_ready.png": {
        "purpose": "Main-deck financial exposure chart showing occupied payroll by GS grade.",
        "executive_insight": "Payroll concentration creates a practical funding and cost-management lens for transformation.",
    },
    "chart_authorized_positions_by_branch.png": {
        "purpose": "Appendix scale context for authorized positions by branch.",
        "executive_insight": "Branch size should be normalized before comparing vacancy and retirement risk.",
    },
    "chart_branch_priority_matrix.png": {
        "purpose": "Main-deck synthesis chart combining vacancy, retirement, and payroll exposure.",
        "executive_insight": "Leadership should prioritize segments where continuity risk and cost exposure overlap.",
    },
    "chart_diagnostic_approach_framework.png": {
        "purpose": "Main-deck framework explaining how the analysis was structured.",
        "executive_insight": "The diagnostic moves from facts to prioritization and decision-making rather than isolated metrics.",
    },
    "chart_implementation_roadmap.png": {
        "purpose": "Main-deck roadmap translating the recommendation into sequenced executive action.",
        "executive_insight": "DPHA should stabilize knowledge and governance before broader modernization.",
    },
    "chart_occupied_headcount_by_age_band.png": {
        "purpose": "Main-deck demographic risk chart showing the age distribution of occupied positions.",
        "executive_insight": "Headcount is concentrated in late-career bands, creating succession and knowledge-continuity risk.",
    },
    "chart_retirement_eligibility_by_branch.png": {
        "purpose": "Main-deck retirement risk chart showing retirement exposure by branch.",
        "executive_insight": "Retirement risk is unevenly distributed and requires branch-by-branch management.",
    },
    "chart_transformation_scenario_comparison.png": {
        "purpose": "Main-deck strategic options table comparing transformation paths.",
        "executive_insight": "Balanced transformation best protects mission readiness while creating savings capacity.",
    },
    "chart_vacancy_rate_by_branch.png": {
        "purpose": "Appendix backup chart showing where vacancy pressure is highest by branch.",
        "executive_insight": "Branch B and central/non-branch positions show elevated vacancy pressure.",
    },
    "chart_vacancy_rate_by_gs_grade.png": {
        "purpose": "Appendix backup chart showing vacancy pressure by GS grade.",
        "executive_insight": "Vacancy pressure differs by grade, which should inform recruiting and backfill prioritization.",
    },
}


def extract_chart_refs(plan: pd.DataFrame) -> dict[str, list[int]]:
    refs: dict[str, list[int]] = {}
    pattern = re.compile(r"chart_[A-Za-z0-9_]+\.png")
    for _, row in plan.iterrows():
        for chart in pattern.findall(str(row["visual_to_use"])):
            refs.setdefault(chart, []).append(int(row["slide_number"]))
    return refs


def update_charts_manifest() -> None:
    plan = pd.read_csv(OUT / "slide_content_plan.csv")
    refs = extract_chart_refs(plan)

    rows = []
    for path in sorted(OUT.glob("chart_*.png")):
        slides = refs.get(path.name, [])
        meta = CHART_METADATA.get(
            path.name,
            {
                "purpose": "Supporting chart available for appendix or future deck iteration.",
                "executive_insight": "Use as backup evidence if the executive discussion goes deeper than the main storyline.",
            },
        )
        if slides:
            recommended_slide = "; ".join(str(s) for s in slides)
            deck_usage = "Main deck"
        elif path.name in {
            "chart_actual_payroll_by_branch.png",
            "chart_authorized_positions_by_branch.png",
            "chart_vacancy_rate_by_branch.png",
            "chart_vacancy_rate_by_gs_grade.png",
        }:
            recommended_slide = "Appendix"
            deck_usage = "Appendix"
        else:
            recommended_slide = "Backup only"
            deck_usage = "Backup"
        rows.append(
            {
                "chart_file": path.name,
                "path": str(path),
                "purpose": meta["purpose"],
                "recommended_slide": recommended_slide,
                "executive_insight": meta["executive_insight"],
                "deck_usage": deck_usage,
                "referenced_in_slide_content_plan": "Yes" if slides else "No",
            }
        )

    manifest = pd.DataFrame(rows)
    manifest.to_csv(OUT / "charts_manifest.csv", index=False)


def create_review() -> None:
    plan = pd.read_csv(OUT / "slide_content_plan.csv")

    review_rows = [
        {
            "slide_number": 1,
            "slide_title": plan.loc[plan.slide_number.eq(1), "slide_title"].iat[0],
            "em_review_take": "Strong opener, but it risks sounding like the recommendation is fully proven before the branch-level logic is shown.",
            "skeptical_question": "What exactly is the senior client being asked to approve today versus merely acknowledge?",
            "evidence_check": "KPI evidence is strong from executive_summary.csv; retirement eligibility and vacant payroll need explicit proxy / estimated language.",
            "risk_or_gap": "Vacant authorized payroll could be misread as immediately available savings.",
            "recommended_revision": "Make the ask narrower: approve Phase 1 knowledge capture and governance, then validate savings and role redesign in the next wave.",
            "priority": "High",
        },
        {
            "slide_number": 2,
            "slide_title": plan.loc[plan.slide_number.eq(2), "slide_title"].iat[0],
            "em_review_take": "Useful structure slide, but frameworks can feel like filler unless each box maps to a decision.",
            "skeptical_question": "How does this approach change what leadership will do next week?",
            "evidence_check": "The six lenses are supported by existing outputs, but scenario modeling is qualitative unless additional quantitative work is added.",
            "risk_or_gap": "Scenario modeling may appear more mature than it is.",
            "recommended_revision": "Add a small caption under scenario modeling: 'qualitative decision frame; quantify in Phase 1.'",
            "priority": "Medium",
        },
        {
            "slide_number": 3,
            "slide_title": plan.loc[plan.slide_number.eq(3), "slide_title"].iat[0],
            "em_review_take": "Good 'so what' and clean use of age bands; this is one of the more defensible slides.",
            "skeptical_question": "Does age 55+ automatically imply retirement risk, or only succession-planning exposure?",
            "evidence_check": "Age-band chart and average age are directly supported by workforce_demographics_summary.csv.",
            "risk_or_gap": "Could overstate retirement timing because the dataset has age but not retirement intent or exact eligibility details.",
            "recommended_revision": "Frame as 'succession exposure' on this slide and reserve retirement eligibility claims for Slide 4.",
            "priority": "Medium",
        },
        {
            "slide_number": 4,
            "slide_title": plan.loc[plan.slide_number.eq(4), "slide_title"].iat[0],
            "em_review_take": "Important slide, but the visual needs cleanup and the eligibility methodology needs visible guardrails.",
            "skeptical_question": "Would HR agree with the retirement eligibility proxy, and what fields are missing?",
            "evidence_check": "Retirement counts are supported by retirement_eligibility_analysis.csv, but based on available age and service fields only.",
            "risk_or_gap": "The legend overlaps the plot and the proxy could be mistaken for an official eligibility determination.",
            "recommended_revision": "Move legend outside the chart and add a source note: 'estimated proxy; excludes DOB, retirement system, and service-credit details.'",
            "priority": "High",
        },
        {
            "slide_number": 5,
            "slide_title": plan.loc[plan.slide_number.eq(5), "slide_title"].iat[0],
            "em_review_take": "The financial bridge is useful, but the funding implication needs tighter language.",
            "skeptical_question": "Is vacant authorized payroll actually fungible for transformation investment?",
            "evidence_check": "Payroll by grade and total payroll tie to payroll_summary.csv and executive_summary.csv; budget flexibility is not proven.",
            "risk_or_gap": "The phrase 'transformation funding opportunity' may overpromise without finance validation.",
            "recommended_revision": "Say 'planning pool to validate with finance' rather than implying available savings.",
            "priority": "High",
        },
        {
            "slide_number": 6,
            "slide_title": plan.loc[plan.slide_number.eq(6), "slide_title"].iat[0],
            "em_review_take": "The risk matrix is consultant-friendly and helps prioritize, but central/non-branch being the top segment may surprise the client.",
            "skeptical_question": "Are central offices comparable to branches, or should they be split out in a separate leadership/central-functions view?",
            "evidence_check": "Risk score is derived from workforce_risk_matrix.csv using normalized vacancy, retirement, and payroll metrics.",
            "risk_or_gap": "Composite score weights are judgment-based; central-office aggregation may hide different operating units.",
            "recommended_revision": "Add a footnote on weights and consider a second cut excluding central/non-branch records for branch-only prioritization.",
            "priority": "High",
        },
        {
            "slide_number": 7,
            "slide_title": plan.loc[plan.slide_number.eq(7), "slide_title"].iat[0],
            "em_review_take": "The recommendation is directionally right, but this slide is the least evidence-backed because scenarios are qualitative.",
            "skeptical_question": "What financial target does balanced transformation meet, and what mission metrics are protected?",
            "evidence_check": "transformation_scenarios.csv is a qualitative frame created for the deck plan, not an analytical model.",
            "risk_or_gap": "Could look like a predetermined recommendation without quantified tradeoffs.",
            "recommended_revision": "Label as 'recommended design principle' and tee up quantified scenario modeling as a Phase 1 deliverable.",
            "priority": "High",
        },
        {
            "slide_number": 8,
            "slide_title": plan.loc[plan.slide_number.eq(8), "slide_title"].iat[0],
            "em_review_take": "Good close, but the executive ask should be even more concrete and time-bound.",
            "skeptical_question": "Who owns the 60-day action plan and what decision rights are being requested?",
            "evidence_check": "Roadmap follows logically from the diagnostic but is not itself derived from source data.",
            "risk_or_gap": "Implementation can sound generic unless owners, outputs, and governance cadence are specified.",
            "recommended_revision": "Add named decision artifacts: critical-role list, branch succession heatmap, vacancy disposition rules, and monthly governance cadence.",
            "priority": "Medium",
        },
    ]

    pd.DataFrame(review_rows).to_csv(OUT / "slide_content_plan_review.csv", index=False)


def main() -> None:
    update_charts_manifest()
    create_review()


if __name__ == "__main__":
    main()
