from __future__ import annotations

from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_output"


def currency_m(value: float) -> str:
    return f"${value / 1_000_000:.1f}M"


def pct(value: float) -> str:
    return f"{value:.1f}%"


def wrap(text: str, width: int = 26) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def save_framework() -> str:
    labels = [
        "Workforce\nDemographics",
        "Retirement\nExposure",
        "Payroll\nConcentration",
        "Vacancy\nAnalysis",
        "Risk\nPrioritization",
        "Scenario\nModeling",
    ]
    fig, ax = plt.subplots(figsize=(12, 3.2))
    ax.axis("off")
    x_positions = np.linspace(0.08, 0.92, len(labels))
    for i, (x, label) in enumerate(zip(x_positions, labels)):
        ax.add_patch(
            plt.Rectangle(
                (x - 0.07, 0.38),
                0.14,
                0.28,
                facecolor="#EAF1F8",
                edgecolor="#2F5597",
                linewidth=1.8,
            )
        )
        ax.text(x, 0.52, label, ha="center", va="center", fontsize=11, fontweight="bold", color="#1F2933")
        if i < len(labels) - 1:
            ax.annotate(
                "",
                xy=(x_positions[i + 1] - 0.085, 0.52),
                xytext=(x + 0.085, 0.52),
                arrowprops=dict(arrowstyle="->", color="#5B6770", linewidth=1.6),
            )
    ax.text(
        0.5,
        0.18,
        "Integrated view: identify where continuity risk, vacancy pressure, and cost exposure overlap",
        ha="center",
        va="center",
        fontsize=12,
        color="#394B59",
    )
    path = OUT / "chart_diagnostic_approach_framework.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path.name


def save_payroll_grade_chart(payroll: pd.DataFrame) -> str:
    grade = (
        payroll[payroll["segment_type"].eq("GS Paygrade")]
        .sort_values("segment_value")
        .copy()
    )
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    bars = ax.bar(grade["segment_value"], grade["actual_payroll"] / 1_000_000, color="#2F5597")
    ax.set_title("Actual Occupied Payroll by GS Grade", loc="left", fontsize=15, fontweight="bold")
    ax.set_ylabel("Actual payroll ($M)")
    ax.set_xlabel("")
    ax.grid(axis="y", alpha=0.25)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for bar, value in zip(bars, grade["actual_payroll"] / 1_000_000):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.15, f"${value:.1f}M", ha="center", va="bottom", fontsize=10)
    ax.text(
        0.01,
        -0.18,
        "Note: salary values are estimated from the GS_Payscale tab and reflect occupied positions only.",
        transform=ax.transAxes,
        fontsize=9,
        color="#5B6770",
    )
    path = OUT / "chart_actual_payroll_by_gs_grade_slide_ready.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path.name


def save_branch_priority_matrix(retirement: pd.DataFrame, vacancy: pd.DataFrame, payroll: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    occupied_ret = retirement[
        retirement["retirement_eligibility_status"].isin(
            ["Currently eligible", "Near-term eligible / high risk", "Medium-term eligibility watch", "Longer-term workforce"]
        )
    ].copy()
    branch_totals = occupied_ret.groupby("DPHA Branch")["positions"].sum().rename("occupied_headcount")
    current = (
        occupied_ret[occupied_ret["retirement_eligibility_status"].eq("Currently eligible")]
        .groupby("DPHA Branch")["positions"]
        .sum()
        .rename("current_retirement_eligible")
    )
    near = (
        occupied_ret[occupied_ret["retirement_eligibility_status"].eq("Near-term eligible / high risk")]
        .groupby("DPHA Branch")["positions"]
        .sum()
        .rename("near_term_retirement_risk")
    )
    branch_vacancy = (
        vacancy[vacancy["segment_type"].eq("DPHA Branch")]
        .set_index("segment_value")[["authorized_positions", "vacant_positions", "vacancy_rate", "vacant_authorized_payroll"]]
    )
    branch_payroll = (
        payroll[payroll["segment_type"].eq("DPHA Branch")]
        .set_index("segment_value")[["actual_payroll"]]
    )
    risk = pd.concat([branch_totals, current, near, branch_vacancy, branch_payroll], axis=1).fillna(0)
    risk.index.name = "branch"
    risk["retirement_risk_rate"] = (risk["current_retirement_eligible"] + risk["near_term_retirement_risk"]) / risk[
        "occupied_headcount"
    ].replace(0, np.nan) * 100
    risk["payroll_exposure_share"] = risk["actual_payroll"] / risk["actual_payroll"].sum() * 100
    for col in ["retirement_risk_rate", "vacancy_rate", "payroll_exposure_share"]:
        max_value = risk[col].max()
        risk[f"{col}_score"] = np.where(max_value > 0, risk[col] / max_value * 100, 0)
    risk["overall_risk_score"] = (
        0.45 * risk["retirement_risk_rate_score"]
        + 0.35 * risk["vacancy_rate_score"]
        + 0.20 * risk["payroll_exposure_share_score"]
    )
    risk = risk.sort_values("overall_risk_score", ascending=False).reset_index()
    risk["branch_display"] = risk["branch"].replace({" -": "Central offices / non-branch", "-": "Central offices / non-branch"})
    risk["branch_chart_label"] = risk["branch_display"].replace({"Central offices / non-branch": "Central offices"})
    risk.to_csv(OUT / "workforce_risk_matrix.csv", index=False)

    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    scatter = ax.scatter(
        risk["vacancy_rate"],
        risk["retirement_risk_rate"],
        s=np.clip(risk["actual_payroll"] / 35_000, 120, 680),
        c=risk["overall_risk_score"],
        cmap="YlOrRd",
        edgecolor="#333333",
        linewidth=0.8,
    )
    for _, row in risk.iterrows():
        ax.annotate(row["branch_chart_label"], (row["vacancy_rate"], row["retirement_risk_rate"]), xytext=(6, 5), textcoords="offset points", fontsize=10)
    ax.axvline(risk["vacancy_rate"].mean(), color="#7F7F7F", linewidth=1, linestyle="--")
    ax.axhline(risk["retirement_risk_rate"].mean(), color="#7F7F7F", linewidth=1, linestyle="--")
    ax.set_xlim(max(0, risk["vacancy_rate"].min() - 0.8), risk["vacancy_rate"].max() + 4.0)
    ax.set_title("Branch Workforce Risk Matrix", loc="left", fontsize=15, fontweight="bold")
    ax.set_xlabel("Vacancy rate (%)")
    ax.set_ylabel("Current + near-term retirement risk rate (%)")
    ax.grid(alpha=0.25)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Overall risk score")
    ax.text(
        0.01,
        -0.16,
        "Bubble size reflects actual occupied payroll; retirement risk is a proxy based on available age and service fields.",
        transform=ax.transAxes,
        fontsize=9,
        color="#5B6770",
    )
    path = OUT / "chart_branch_priority_matrix.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path.name, risk


def save_strategy_table() -> tuple[str, pd.DataFrame]:
    scenarios = pd.DataFrame(
        [
            {
                "scenario": "Aggressive reduction",
                "financial_impact": "Highest near-term savings",
                "mission_risk": "High",
                "workforce_continuity": "Disruptive",
                "recommended_role": "Use selectively in low-risk roles",
            },
            {
                "scenario": "Balanced transformation",
                "financial_impact": "Moderate savings plus reinvestment capacity",
                "mission_risk": "Managed",
                "workforce_continuity": "Protects critical knowledge",
                "recommended_role": "Recommended path",
            },
            {
                "scenario": "Minimal disruption",
                "financial_impact": "Lowest savings",
                "mission_risk": "Lower immediate disruption",
                "workforce_continuity": "Does not resolve retirement exposure",
                "recommended_role": "Insufficient as primary strategy",
            },
        ]
    )
    scenarios.to_csv(OUT / "transformation_scenarios.csv", index=False)

    fig, ax = plt.subplots(figsize=(12, 4.2))
    ax.axis("off")
    columns = ["Scenario", "Financial impact", "Mission risk", "Continuity", "Recommended role"]
    rows = [
        [r.scenario, r.financial_impact, r.mission_risk, r.workforce_continuity, r.recommended_role]
        for r in scenarios.itertuples(index=False)
    ]
    wrapped_rows = [[wrap(str(cell), 22) for cell in row] for row in rows]
    table = ax.table(cellText=wrapped_rows, colLabels=columns, loc="center", cellLoc="left", colLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.25)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#D9E2EC")
        if row == 0:
            cell.set_facecolor("#2F5597")
            cell.set_text_props(color="white", fontweight="bold")
        elif row == 2:
            cell.set_facecolor("#E2F0D9")
        else:
            cell.set_facecolor("#FFFFFF")
    ax.set_title("Strategic Options Comparison", loc="left", fontsize=15, fontweight="bold", pad=20)
    path = OUT / "chart_transformation_scenario_comparison.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path.name, scenarios


def save_roadmap() -> str:
    phases = [
        ("Phase 1\n0-6 months", "Stabilize\nCapture knowledge\nStand up governance"),
        ("Phase 2\n6-18 months", "Modernize\nTransition roles\nPrioritize vacancies"),
        ("Phase 3\n18+ months", "Optimize\nGovern portfolio\nTrack outcomes"),
    ]
    fig, ax = plt.subplots(figsize=(12, 3.6))
    ax.axis("off")
    x_positions = [0.18, 0.5, 0.82]
    colors = ["#EAF1F8", "#E2F0D9", "#FFF2CC"]
    for i, ((phase, body), x) in enumerate(zip(phases, x_positions)):
        ax.add_patch(plt.Rectangle((x - 0.13, 0.34), 0.26, 0.36, facecolor=colors[i], edgecolor="#5B6770", linewidth=1.5))
        ax.text(x, 0.61, phase, ha="center", va="center", fontsize=12, fontweight="bold")
        ax.text(x, 0.45, body, ha="center", va="center", fontsize=10)
        if i < 2:
            ax.annotate("", xy=(x_positions[i + 1] - 0.15, 0.52), xytext=(x + 0.15, 0.52), arrowprops=dict(arrowstyle="->", linewidth=1.8, color="#5B6770"))
    ax.text(
        0.5,
        0.17,
        "Executive ask: approve Phase 1 knowledge capture, workforce planning governance, and retirement-transition analysis",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color="#1F2933",
    )
    path = OUT / "chart_implementation_roadmap.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path.name


def main() -> None:
    executive = pd.read_csv(OUT / "executive_summary.csv").set_index("metric")["value"]
    demographics = pd.read_csv(OUT / "workforce_demographics_summary.csv")
    payroll = pd.read_csv(OUT / "payroll_summary.csv")
    retirement = pd.read_csv(OUT / "retirement_eligibility_analysis.csv")
    vacancy = pd.read_csv(OUT / "vacancy_analysis.csv")

    framework_chart = save_framework()
    payroll_chart = save_payroll_grade_chart(payroll)
    risk_chart, risk = save_branch_priority_matrix(retirement, vacancy, payroll)
    scenario_chart, scenarios = save_strategy_table()
    roadmap_chart = save_roadmap()

    age_demo = demographics[demographics["segment_type"].eq("age_band")].copy()
    late_career = age_demo[age_demo["segment_value"].isin(["55-59", "60-64", "65+"])]["occupied_headcount"].sum()
    late_career_share = late_career / executive["Occupied positions"] * 100
    largest_age = age_demo.sort_values("occupied_headcount", ascending=False).iloc[0]

    retirement_occupied = retirement[retirement["retirement_eligibility_status"].ne("Not applicable - vacant")].copy()
    current_eligible = int(executive["Current retirement eligible headcount"])
    current_eligible_share = executive["Current retirement eligible share of occupied"]
    current_near = retirement_occupied[
        retirement_occupied["retirement_eligibility_status"].isin(["Currently eligible", "Near-term eligible / high risk"])
    ]["positions"].sum()
    branch_risk = risk.iloc[0]

    grade_payroll = payroll[payroll["segment_type"].eq("GS Paygrade")].sort_values("actual_payroll", ascending=False)
    top_grade = grade_payroll.iloc[0]
    total_payroll = executive["Actual occupied payroll"]
    vacant_payroll = executive["Vacant authorized payroll"]

    assumptions = pd.DataFrame(
        [
            {
                "assumption_or_limitation": "Retirement eligibility is estimated from age and years of service only.",
                "implication": "Exact federal retirement eligibility would require date of birth, retirement system, and service-credit details.",
            },
            {
                "assumption_or_limitation": "Payroll values are derived from the GS_Payscale tab by grade and step.",
                "implication": "Figures exclude locality, premium pay, benefits, vacancies beyond authorized salary, and non-salary operating costs.",
            },
            {
                "assumption_or_limitation": "Vacant positions have zero employee-specific age, service, training, and remote-work fields.",
                "implication": "Those zeros are treated as structural not-applicable values rather than true employee metrics.",
            },
            {
                "assumption_or_limitation": "Strategic scenarios are qualitative because no transformation_scenarios.csv was available before this plan.",
                "implication": "Financial savings and FTE movement should be modeled before decisions are finalized.",
            },
            {
                "assumption_or_limitation": "Branch priority scores are normalized proxies built from vacancy, retirement, and payroll exposure.",
                "implication": "They are appropriate for prioritization discussions, not as a sole basis for personnel actions.",
            },
        ]
    )
    assumptions.to_csv(OUT / "assumptions_and_limitations.csv", index=False)

    slide_rows = [
        {
            "slide_number": 1,
            "slide_title": "DPHA must address workforce continuity before vacancies and retirements compound",
            "executive_message": "DPHA has a meaningful continuity risk: 10.1% of authorized positions are vacant and an estimated 44.4% of occupied employees are currently retirement eligible.",
            "visual_to_use": "KPI callout boxes only; no chart. Use executive_summary.csv.",
            "key_metrics_to_show": f"Authorized positions: {int(executive['Authorized positions'])}; occupied positions: {int(executive['Occupied positions'])}; vacancy rate: {pct(executive['Vacancy rate'])}; actual occupied payroll: {currency_m(total_payroll)}; retirement eligible share: {pct(current_eligible_share)}; vacant authorized payroll: {currency_m(vacant_payroll)}.",
            "analysis_result": "The workforce is large, senior, and financially material, with vacancies representing both service-delivery risk and potential transformation funding capacity.",
            "recommendation_or_implication": "Approve a targeted transformation program focused first on knowledge capture, branch-level succession planning, and vacancy prioritization.",
            "speaker_notes": "Open with the problem: this is not only a staffing count issue; it is a continuity and mission-readiness issue. The retirement figure is an estimate based on available age and service fields. Vacant authorized payroll indicates budget capacity tied to open positions, not automatically available savings. The recommended path is deliberate and branch-specific rather than across-the-board reduction.",
            "appendix_backup_outputs": "executive_summary.csv; assumptions_and_limitations.csv",
        },
        {
            "slide_number": 2,
            "slide_title": "A structured diagnostic links workforce facts to executive decisions",
            "executive_message": "The analysis connects six lenses: demographics, retirement exposure, payroll concentration, vacancy pressure, risk prioritization, and scenario choices.",
            "visual_to_use": framework_chart,
            "key_metrics_to_show": "Framework steps only; note source outputs used across each lens.",
            "analysis_result": "The available dataset supports a practical leadership diagnostic even though several items, such as exact retirement eligibility and transformation savings, require additional validation.",
            "recommendation_or_implication": "Use this framework as the standing governance structure for Phase 1 workforce decisions.",
            "speaker_notes": "This slide explains how the case was built and avoids jumping straight to conclusions. Each diagnostic lens maps to a specific executive question. Scenario modeling is included as a decision lens, but current scenario outputs are qualitative because a pre-existing transformation scenario file was not available. The framework can be refreshed as better data becomes available.",
            "appendix_backup_outputs": "data_dictionary.csv; missing_values.csv; summary_statistics.csv; summary_statistics_categorical.csv",
        },
        {
            "slide_number": 3,
            "slide_title": "Late-career concentration creates a near-term succession challenge",
            "executive_message": f"An estimated {pct(late_career_share)} of occupied headcount is age 55+, with the largest age band at {largest_age['segment_value']}.",
            "visual_to_use": "chart_occupied_headcount_by_age_band.png",
            "key_metrics_to_show": f"Average occupied age: {executive['Average occupied age']:.1f}; age 55+ headcount: {int(late_career)}; largest band: {largest_age['segment_value']} with {int(largest_age['occupied_headcount'])} employees.",
            "analysis_result": "The age profile is weighted toward late-career groups, increasing the risk of unmanaged knowledge loss and leadership gaps.",
            "recommendation_or_implication": "Prioritize role-critical knowledge capture and succession plans for late-career segments before attrition accelerates.",
            "speaker_notes": "This chart is slide-ready but should be paired with a brief note that age is available only as a current field, not a full retirement forecast. The key point is concentration, not precision forecasting. The average age of 54.4 reinforces that the issue is system-wide. Use this slide to make the continuity case before discussing dollars.",
            "appendix_backup_outputs": "workforce_demographics_summary.csv; summary_statistics.csv",
        },
        {
            "slide_number": 4,
            "slide_title": "Retirement risk is uneven and must be managed branch by branch",
            "executive_message": f"Current retirement eligibility affects {current_eligible} employees, and current plus near-term risk totals an estimated {int(current_near)} occupied positions across branches.",
            "visual_to_use": "chart_retirement_eligibility_by_branch.png; redesign flag: legend overlaps lower-right plot area and should be moved outside or below before final deck production.",
            "key_metrics_to_show": f"Currently eligible: {current_eligible} employees / {pct(current_eligible_share)} of occupied headcount; current + near-term risk: {int(current_near)}; highest composite risk segment from matrix: {branch_risk['branch_display']}.",
            "analysis_result": "Retirement exposure is concentrated differently by branch, so a uniform workforce action would miss operational hot spots.",
            "recommendation_or_implication": "Create branch-specific retirement transition plans, beginning with the highest-risk branches and roles with limited redundancy.",
            "speaker_notes": "The retirement categories are proxy estimates based on age and years of service. The chart shows that the risk is not evenly distributed, which is the management insight. Branch-level action should include succession coverage, documentation of critical processes, and cross-training. Avoid presenting the proxy as an HR eligibility determination.",
            "appendix_backup_outputs": "retirement_eligibility_analysis.csv; assumptions_and_limitations.csv",
        },
        {
            "slide_number": 5,
            "slide_title": "Payroll concentration creates both cost pressure and reinvestment capacity",
            "executive_message": f"Actual occupied payroll is {currency_m(total_payroll)}, with {top_grade['segment_value']} representing the largest payroll concentration and {currency_m(vacant_payroll)} in vacant authorized payroll.",
            "visual_to_use": f"{payroll_chart}; original chart_actual_payroll_by_gs_grade.png is usable but less slide-ready because horizontal ranking is harder to compare by grade progression.",
            "key_metrics_to_show": f"Actual occupied payroll: {currency_m(total_payroll)}; top payroll grade: {top_grade['segment_value']} at {currency_m(top_grade['actual_payroll'])}; vacant authorized payroll: {currency_m(vacant_payroll)}.",
            "analysis_result": "The payroll profile shows where financial exposure sits and where vacancy dollars could help fund modernization if leadership confirms budget flexibility.",
            "recommendation_or_implication": "Use vacant authorized payroll as a planning pool for targeted modernization, backfills, and critical-role transitions rather than simple cost takeout.",
            "speaker_notes": "Salary values are estimated from the provided GS pay scale and should not be treated as full compensation cost. The main insight is concentration by grade, not exact budget authority. Vacant authorized payroll is an opportunity signal, but it requires finance validation before use. This slide bridges workforce risk to transformation funding.",
            "appendix_backup_outputs": "payroll_summary.csv; chart_actual_payroll_by_branch.png; assumptions_and_limitations.csv",
        },
        {
            "slide_number": 6,
            "slide_title": "Leadership should prioritize branches where continuity and cost exposure overlap",
            "executive_message": f"The branch risk matrix places {branch_risk['branch_display']} at the top of the composite risk ranking based on retirement risk, vacancy rate, and payroll exposure.",
            "visual_to_use": risk_chart,
            "key_metrics_to_show": f"Top segment: {branch_risk['branch_display']}; retirement risk rate: {pct(branch_risk['retirement_risk_rate'])}; vacancy rate: {pct(branch_risk['vacancy_rate'])}; overall risk score: {branch_risk['overall_risk_score']:.1f}.",
            "analysis_result": "Risk is highest where vacancy pressure, retirement exposure, and payroll scale intersect, making branch prioritization more actionable than enterprise averages.",
            "recommendation_or_implication": "Focus Phase 1 intervention on the highest-risk branches, then expand governance to lower-risk groups once critical exposures are stabilized.",
            "speaker_notes": "This matrix is a prioritization tool, not a definitive personnel decision model. Scores are normalized proxies built from available outputs. The bubble size reflects payroll exposure, so larger bubbles indicate more financial materiality. Use this slide to move the conversation from diagnosis to sequencing.",
            "appendix_backup_outputs": "workforce_risk_matrix.csv; vacancy_analysis.csv; payroll_summary.csv; retirement_eligibility_analysis.csv",
        },
        {
            "slide_number": 7,
            "slide_title": "Balanced transformation best protects mission readiness while creating savings capacity",
            "executive_message": "Balanced transformation is the recommended option because it combines targeted efficiency with knowledge continuity and controlled implementation risk.",
            "visual_to_use": scenario_chart,
            "key_metrics_to_show": "Options: aggressive reduction; balanced transformation; minimal disruption. Show qualitative tradeoffs for financial impact, mission risk, continuity, and recommended role.",
            "analysis_result": "Aggressive reduction may create savings faster but heightens mission and knowledge-loss risk; minimal disruption avoids short-term pain but leaves the retirement exposure unresolved.",
            "recommendation_or_implication": "Select balanced transformation as the design principle for Phase 1 and require quantified scenario modeling before final workforce actions.",
            "speaker_notes": "Because no pre-existing transformation_scenarios.csv was available, this comparison is qualitative and should be treated as a decision frame. The balanced path does not mean slow; it means sequenced around mission-critical roles. Quantified savings, role redesign, and service impacts should be modeled next. This slide sets up the executive ask.",
            "appendix_backup_outputs": "transformation_scenarios.csv; assumptions_and_limitations.csv",
        },
        {
            "slide_number": 8,
            "slide_title": "Act now to avoid unmanaged knowledge loss",
            "executive_message": "DPHA should launch Phase 1 immediately: stabilize critical functions, capture knowledge, and establish workforce planning governance before retirements become unmanaged attrition.",
            "visual_to_use": roadmap_chart,
            "key_metrics_to_show": "Phase 1: stabilize and capture knowledge, 0-6 months; Phase 2: modernize and transition, 6-18 months; Phase 3: optimize and govern, 18+ months; decision ask: approve Phase 1 knowledge capture, workforce planning governance, and retirement-transition analysis.",
            "analysis_result": "The risk profile supports immediate action, but the next step should be controlled implementation rather than broad workforce reduction.",
            "recommendation_or_implication": "Approve Phase 1 scope, name accountable owners, and require a 60-day branch-level retirement and vacancy action plan.",
            "speaker_notes": "Close with a clear ask rather than another diagnostic point. The proposed roadmap sequences stabilization before modernization and optimization. This protects mission readiness while leadership validates budget and role-design assumptions. The decision today is to begin structured action, not to finalize every workforce move.",
            "appendix_backup_outputs": "executive_summary.csv; workforce_risk_matrix.csv; assumptions_and_limitations.csv",
        },
    ]
    pd.DataFrame(slide_rows).to_csv(OUT / "slide_content_plan.csv", index=False)

    appendix_rows = [
        {
            "appendix_item": "Data dictionary",
            "output_file": "data_dictionary.csv",
            "why_it_belongs_in_appendix": "Defines source and derived fields without consuming main-deck space.",
            "executive_question_it_answers": "What data fields were used and how should they be interpreted?",
        },
        {
            "appendix_item": "Missing value analysis",
            "output_file": "missing_values.csv",
            "why_it_belongs_in_appendix": "Supports data-quality confidence and flags the one actionable Employee ID issue.",
            "executive_question_it_answers": "Can leadership trust the analysis inputs?",
        },
        {
            "appendix_item": "Numeric summary statistics",
            "output_file": "summary_statistics.csv",
            "why_it_belongs_in_appendix": "Provides detailed distributions behind headline averages.",
            "executive_question_it_answers": "What are the underlying age, service, training, remote-work, and salary distributions?",
        },
        {
            "appendix_item": "Categorical summary statistics",
            "output_file": "summary_statistics_categorical.csv",
            "why_it_belongs_in_appendix": "Shows the full composition by office, branch, team, title, grade, and position status.",
            "executive_question_it_answers": "How is the workforce distributed across organizational and role categories?",
        },
        {
            "appendix_item": "Vacancy rate by branch chart",
            "output_file": "chart_vacancy_rate_by_branch.png",
            "why_it_belongs_in_appendix": "Useful branch detail, but not required in the main storyline once the risk matrix is shown.",
            "executive_question_it_answers": "Which branches have the highest vacancy rates?",
        },
        {
            "appendix_item": "Vacancy rate by GS grade chart",
            "output_file": "chart_vacancy_rate_by_gs_grade.png",
            "why_it_belongs_in_appendix": "Shows grade-level vacancy pressure as backup for staffing prioritization.",
            "executive_question_it_answers": "Which grades have the greatest vacancy pressure?",
        },
        {
            "appendix_item": "Authorized positions by branch chart",
            "output_file": "chart_authorized_positions_by_branch.png",
            "why_it_belongs_in_appendix": "Provides scale context for branch comparisons without crowding the main deck.",
            "executive_question_it_answers": "How large is each branch in authorized position terms?",
        },
        {
            "appendix_item": "Payroll detail",
            "output_file": "payroll_summary.csv",
            "why_it_belongs_in_appendix": "Contains segment-level payroll detail supporting financial exposure claims.",
            "executive_question_it_answers": "Where is payroll concentrated by office, branch, grade, title, and position status?",
        },
        {
            "appendix_item": "Retirement eligibility detail",
            "output_file": "retirement_eligibility_analysis.csv",
            "why_it_belongs_in_appendix": "Documents branch-level retirement categories and proxy assumptions.",
            "executive_question_it_answers": "Where is retirement exposure concentrated and how large is it?",
        },
        {
            "appendix_item": "Assumptions and limitations",
            "output_file": "assumptions_and_limitations.csv",
            "why_it_belongs_in_appendix": "Prevents overstatement and clarifies where estimates require validation.",
            "executive_question_it_answers": "What should leadership know before using these findings for decisions?",
        },
    ]
    pd.DataFrame(appendix_rows).to_csv(OUT / "appendix_map.csv", index=False)


if __name__ == "__main__":
    main()
