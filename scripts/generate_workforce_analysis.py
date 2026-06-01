from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "Guidehouse_Public_Health_Case_Study_Data_Set.xlsx"
OUT = ROOT / "analysis_output"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def money(series: pd.Series) -> pd.Series:
    return series.round(2)


def retirement_status(row: pd.Series) -> str:
    if not row["is_occupied"]:
        return "Not applicable - vacant"

    age = row["Age"]
    service = row["Years of Service"]

    # Federal retirement proxy using available fields only. Exact MRA needs DOB.
    if (age >= 62 and service >= 5) or (age >= 60 and service >= 20) or (age >= 57 and service >= 30):
        return "Currently eligible"
    if age >= 55 and service >= 25:
        return "Near-term eligible / high risk"
    if age >= 50 and service >= 20:
        return "Medium-term eligibility watch"
    return "Longer-term workforce"


def write_csv(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False)


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str, filename: str, xlabel: str = "", ylabel: str = "") -> None:
    plot_df = df.copy()
    fig_h = max(4.8, min(9.5, 0.32 * len(plot_df) + 2.5))
    fig, ax = plt.subplots(figsize=(10.5, fig_h))
    ax.barh(plot_df[x].astype(str), plot_df[y], color="#2F5597")
    ax.invert_yaxis()
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel or y)
    ax.set_ylabel(ylabel or "")
    ax.grid(axis="x", alpha=0.25)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    max_val = plot_df[y].max() if len(plot_df) else 0
    for i, value in enumerate(plot_df[y]):
        label = f"{value:,.1f}%" if "rate" in y.lower() or "percent" in y.lower() else f"{value:,.0f}"
        ax.text(value + max(max_val * 0.01, 0.1), i, label, va="center", fontsize=9)
    plt.tight_layout()
    fig.savefig(OUT / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


def stacked_bar_chart(
    df: pd.DataFrame,
    index_col: str,
    category_col: str,
    value_col: str,
    title: str,
    filename: str,
) -> None:
    pivot = df.pivot_table(index=index_col, columns=category_col, values=value_col, aggfunc="sum", fill_value=0)
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=True).index]
    fig_h = max(5.2, min(10, 0.34 * len(pivot) + 2.5))
    fig, ax = plt.subplots(figsize=(11, fig_h))
    colors = ["#2F5597", "#70AD47", "#FFC000", "#C00000", "#7F7F7F"]
    pivot.plot(kind="barh", stacked=True, ax=ax, color=colors[: len(pivot.columns)])
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold")
    ax.set_xlabel("Positions")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.25)
    ax.legend(title="", loc="lower right")
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    fig.savefig(OUT / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)

    workforce = pd.read_excel(INPUT, sheet_name="DPHA_Workforce_Data")
    payscale = pd.read_excel(INPUT, sheet_name="GS_Payscale")

    df = workforce.copy()
    df["grade_num"] = df["GS Paygrade"].astype(str).str.extract(r"(\d+)").astype(int)
    df["step_num"] = df["GS Paygrade Step"].astype(int)

    pay_long = payscale.melt(id_vars="Grade", var_name="step_label", value_name="annual_salary")
    pay_long["step_num"] = pay_long["step_label"].str.extract(r"(\d+)").astype(int)
    pay_long = pay_long.rename(columns={"Grade": "grade_num"})
    df = df.merge(pay_long[["grade_num", "step_num", "annual_salary"]], on=["grade_num", "step_num"], how="left")

    df["is_occupied"] = df["Occupied or Vacant Position"].eq("Occupied")
    df["is_vacant"] = df["Occupied or Vacant Position"].eq("Vacant")
    df["actual_payroll"] = np.where(df["is_occupied"], df["annual_salary"], 0)
    df["vacant_authorized_payroll"] = np.where(df["is_vacant"], df["annual_salary"], 0)
    df["authorized_payroll"] = df["annual_salary"]
    df["retirement_eligibility_status"] = df.apply(retirement_status, axis=1)
    df["age_band"] = pd.cut(
        df["Age"].where(df["is_occupied"]),
        bins=[0, 29, 39, 49, 54, 59, 64, 200],
        labels=["Under 30", "30-39", "40-49", "50-54", "55-59", "60-64", "65+"],
        right=True,
    )
    df["service_band"] = pd.cut(
        df["Years of Service"].where(df["is_occupied"]),
        bins=[-1, 4, 9, 14, 19, 24, 29, 200],
        labels=["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30+"],
    )

    # 1. Data dictionary
    descriptions = {
        "Position / Job ID#": "Unique identifier for each authorized position; one duplicate position ID appears in source.",
        "Employee ID#": "Employee identifier for occupied positions; '-' indicates vacant position.",
        "Position Title": "Role or job title assigned to the position.",
        "Office": "Office or organizational unit owning the position.",
        "DPHA Branch": "Branch within Public Health Advancement; '-' indicates central office / not branch-assigned.",
        "DPHA Team": "Team within a branch; '-' indicates central office / not team-assigned.",
        "GS Paygrade": "General Schedule grade for the position.",
        "GS Paygrade Step": "General Schedule step for the position.",
        "Occupied or Vacant Position": "Position status in the workforce roster.",
        "Age": "Employee age; zero for vacant positions.",
        "Years of Service": "Employee years of service; zero for vacant positions.",
        "Training Hours (Prior Year)": "Prior-year training hours; zero for vacant positions.",
        "Average Remote Workdays Per Month": "Average monthly remote workdays; zero for vacant positions.",
        "annual_salary": "Derived annual salary from GS grade and step using GS_Payscale tab.",
        "actual_payroll": "Derived payroll cost for occupied positions only.",
        "authorized_payroll": "Derived annual salary for all authorized positions, occupied and vacant.",
        "vacant_authorized_payroll": "Derived salary value of currently vacant positions.",
        "retirement_eligibility_status": "Derived retirement risk band using age and years-of-service proxy rules.",
    }
    dictionary_rows = []
    for col in list(workforce.columns) + [
        "annual_salary",
        "actual_payroll",
        "authorized_payroll",
        "vacant_authorized_payroll",
        "retirement_eligibility_status",
    ]:
        source = df[col] if col in df.columns else workforce[col]
        dictionary_rows.append(
            {
                "field_name": col,
                "source_or_derived": "Source" if col in workforce.columns else "Derived",
                "data_type": str(source.dtype),
                "description": descriptions.get(col, ""),
                "non_null_count": int(source.notna().sum()),
                "unique_values": int(source.nunique(dropna=False)),
                "sample_values": "; ".join(map(str, source.dropna().astype(str).unique()[:5])),
                "missing_or_structural_note": (
                    "'-' is structural not-applicable for vacant or central-office records"
                    if col in ["Employee ID#", "DPHA Branch", "DPHA Team"]
                    else "Zeros in employee-specific measures are structural for vacant positions"
                    if col in ["Age", "Years of Service", "Training Hours (Prior Year)", "Average Remote Workdays Per Month"]
                    else ""
                ),
            }
        )
    write_csv(pd.DataFrame(dictionary_rows), "data_dictionary.csv")

    # 2. Summary statistics
    numeric_cols = [
        "Age",
        "Years of Service",
        "Training Hours (Prior Year)",
        "Average Remote Workdays Per Month",
        "annual_salary",
    ]
    summary_rows = []
    for population, frame in {
        "All authorized positions": df,
        "Occupied positions only": df[df["is_occupied"]],
        "Vacant positions only": df[df["is_vacant"]],
    }.items():
        for col in numeric_cols:
            s = frame[col].dropna()
            summary_rows.append(
                {
                    "population": population,
                    "metric": col,
                    "count": int(s.count()),
                    "mean": s.mean(),
                    "median": s.median(),
                    "std_dev": s.std(),
                    "min": s.min(),
                    "p25": s.quantile(0.25),
                    "p75": s.quantile(0.75),
                    "max": s.max(),
                }
            )
    write_csv(pd.DataFrame(summary_rows).round(2), "summary_statistics.csv")

    categorical_rows = []
    for col in ["Office", "DPHA Branch", "DPHA Team", "Position Title", "GS Paygrade", "Occupied or Vacant Position"]:
        counts = df[col].value_counts(dropna=False)
        for value, count in counts.items():
            categorical_rows.append(
                {
                    "field_name": col,
                    "value": value,
                    "count": int(count),
                    "percent_of_positions": round(count / len(df) * 100, 2),
                }
            )
    write_csv(pd.DataFrame(categorical_rows), "summary_statistics_categorical.csv")

    # 3. Missing value analysis
    missing_rows = []
    structural_rules = {
        "Employee ID#": df["is_vacant"] & df["Employee ID#"].eq(" -"),
        "DPHA Branch": df["DPHA Branch"].eq(" -"),
        "DPHA Team": df["DPHA Team"].eq(" -"),
        "Age": df["is_vacant"] & df["Age"].eq(0),
        "Years of Service": df["is_vacant"] & df["Years of Service"].eq(0),
        "Training Hours (Prior Year)": df["is_vacant"] & df["Training Hours (Prior Year)"].eq(0),
        "Average Remote Workdays Per Month": df["is_vacant"] & df["Average Remote Workdays Per Month"].eq(0),
    }
    for col in workforce.columns:
        raw_null = df[col].isna()
        blank = df[col].astype(str).str.strip().eq("")
        placeholder = df[col].astype(str).str.strip().isin(["-", "NA", "N/A", "None", "nan"])
        structural = structural_rules.get(col, pd.Series(False, index=df.index))
        actionable = (raw_null | blank | placeholder) & ~structural
        missing_rows.append(
            {
                "field_name": col,
                "raw_null_count": int(raw_null.sum()),
                "blank_count": int(blank.sum()),
                "placeholder_dash_count": int(placeholder.sum()),
                "structural_not_applicable_count": int(structural.sum()),
                "actionable_missing_count": int(actionable.sum()),
                "actionable_missing_percent": round(actionable.mean() * 100, 2),
                "quality_note": "No actionable missingness after structural values are separated"
                if actionable.sum() == 0
                else "Investigate source completeness",
            }
        )
    write_csv(pd.DataFrame(missing_rows), "missing_values.csv")

    # 4. Workforce demographics summary
    demo_frames = []
    for field in ["age_band", "service_band", "GS Paygrade", "DPHA Branch", "Position Title"]:
        temp = (
            df[df["is_occupied"]]
            .groupby(field, observed=False)
            .agg(
                occupied_headcount=("Position / Job ID#", "count"),
                avg_age=("Age", "mean"),
                avg_years_of_service=("Years of Service", "mean"),
                avg_training_hours=("Training Hours (Prior Year)", "mean"),
                avg_remote_workdays=("Average Remote Workdays Per Month", "mean"),
                total_actual_payroll=("actual_payroll", "sum"),
            )
            .reset_index()
            .rename(columns={field: "segment_value"})
        )
        temp.insert(0, "segment_type", field)
        demo_frames.append(temp)
    demographics = pd.concat(demo_frames, ignore_index=True)
    demographics["headcount_percent"] = demographics["occupied_headcount"] / df["is_occupied"].sum() * 100
    write_csv(demographics.round(2), "workforce_demographics_summary.csv")

    # 5. Payroll summary
    payroll_frames = []
    for field in ["Office", "DPHA Branch", "GS Paygrade", "Position Title", "Occupied or Vacant Position"]:
        temp = (
            df.groupby(field, dropna=False)
            .agg(
                authorized_positions=("Position / Job ID#", "count"),
                occupied_positions=("is_occupied", "sum"),
                vacant_positions=("is_vacant", "sum"),
                authorized_payroll=("authorized_payroll", "sum"),
                actual_payroll=("actual_payroll", "sum"),
                vacant_authorized_payroll=("vacant_authorized_payroll", "sum"),
                avg_authorized_salary=("authorized_payroll", "mean"),
            )
            .reset_index()
            .rename(columns={field: "segment_value"})
        )
        temp.insert(0, "segment_type", field)
        payroll_frames.append(temp)
    payroll = pd.concat(payroll_frames, ignore_index=True)
    payroll["vacancy_rate"] = payroll["vacant_positions"] / payroll["authorized_positions"] * 100
    write_csv(payroll.round(2), "payroll_summary.csv")

    # 6. Retirement eligibility analysis
    retirement = (
        df.groupby(["DPHA Branch", "retirement_eligibility_status"], dropna=False)
        .agg(
            positions=("Position / Job ID#", "count"),
            avg_age=("Age", "mean"),
            avg_years_of_service=("Years of Service", "mean"),
            actual_payroll=("actual_payroll", "sum"),
        )
        .reset_index()
    )
    retirement["percent_of_occupied_headcount"] = np.where(
        retirement["retirement_eligibility_status"].eq("Not applicable - vacant"),
        np.nan,
        retirement["positions"] / df["is_occupied"].sum() * 100,
    )
    write_csv(retirement.round(2), "retirement_eligibility_analysis.csv")

    # 7. Vacancy analysis
    vacancy_frames = []
    for field in ["Office", "DPHA Branch", "DPHA Team", "GS Paygrade", "Position Title"]:
        temp = (
            df.groupby(field, dropna=False)
            .agg(
                authorized_positions=("Position / Job ID#", "count"),
                occupied_positions=("is_occupied", "sum"),
                vacant_positions=("is_vacant", "sum"),
                vacant_authorized_payroll=("vacant_authorized_payroll", "sum"),
                avg_vacant_salary=("vacant_authorized_payroll", lambda s: s[s > 0].mean()),
            )
            .reset_index()
            .rename(columns={field: "segment_value"})
        )
        temp.insert(0, "segment_type", field)
        temp["vacancy_rate"] = temp["vacant_positions"] / temp["authorized_positions"] * 100
        vacancy_frames.append(temp)
    vacancy = pd.concat(vacancy_frames, ignore_index=True).sort_values(
        ["segment_type", "vacant_positions", "vacancy_rate"], ascending=[True, False, False]
    )
    write_csv(vacancy.round(2), "vacancy_analysis.csv")

    # Executive CSV with a few board-style KPIs.
    occupied = df[df["is_occupied"]]
    exec_summary = pd.DataFrame(
        [
            {"metric": "Authorized positions", "value": len(df)},
            {"metric": "Occupied positions", "value": int(df["is_occupied"].sum())},
            {"metric": "Vacant positions", "value": int(df["is_vacant"].sum())},
            {"metric": "Vacancy rate", "value": round(df["is_vacant"].mean() * 100, 2)},
            {"metric": "Actual occupied payroll", "value": round(df["actual_payroll"].sum(), 2)},
            {"metric": "Authorized payroll incl. vacancies", "value": round(df["authorized_payroll"].sum(), 2)},
            {"metric": "Vacant authorized payroll", "value": round(df["vacant_authorized_payroll"].sum(), 2)},
            {"metric": "Average occupied age", "value": round(occupied["Age"].mean(), 2)},
            {"metric": "Average occupied years of service", "value": round(occupied["Years of Service"].mean(), 2)},
            {
                "metric": "Current retirement eligible headcount",
                "value": int(occupied["retirement_eligibility_status"].eq("Currently eligible").sum()),
            },
            {
                "metric": "Current retirement eligible share of occupied",
                "value": round(occupied["retirement_eligibility_status"].eq("Currently eligible").mean() * 100, 2),
            },
        ]
    )
    write_csv(exec_summary, "executive_summary.csv")

    # Charts
    charts_dir_note = OUT / "charts_manifest.csv"
    branch_headcount = (
        df.groupby("DPHA Branch")
        .agg(authorized_positions=("Position / Job ID#", "count"))
        .reset_index()
        .sort_values("authorized_positions", ascending=True)
    )
    bar_chart(
        branch_headcount,
        "DPHA Branch",
        "authorized_positions",
        "Authorized Positions by Branch",
        "chart_authorized_positions_by_branch.png",
        xlabel="Authorized positions",
    )

    age_dist = occupied.groupby("age_band", observed=False).size().reset_index(name="occupied_headcount")
    bar_chart(
        age_dist,
        "age_band",
        "occupied_headcount",
        "Occupied Headcount by Age Band",
        "chart_occupied_headcount_by_age_band.png",
        xlabel="Occupied headcount",
    )

    grade_payroll = (
        df.groupby("GS Paygrade")
        .agg(actual_payroll=("actual_payroll", "sum"))
        .reset_index()
        .sort_values("actual_payroll", ascending=True)
    )
    bar_chart(
        grade_payroll,
        "GS Paygrade",
        "actual_payroll",
        "Actual Payroll by GS Grade",
        "chart_actual_payroll_by_gs_grade.png",
        xlabel="Actual payroll ($)",
    )

    branch_payroll = (
        df.groupby("DPHA Branch")
        .agg(actual_payroll=("actual_payroll", "sum"))
        .reset_index()
        .sort_values("actual_payroll", ascending=True)
    )
    bar_chart(
        branch_payroll,
        "DPHA Branch",
        "actual_payroll",
        "Actual Payroll by Branch",
        "chart_actual_payroll_by_branch.png",
        xlabel="Actual payroll ($)",
    )

    retire_chart = (
        df[df["is_occupied"]]
        .groupby(["DPHA Branch", "retirement_eligibility_status"])
        .size()
        .reset_index(name="positions")
    )
    stacked_bar_chart(
        retire_chart,
        "DPHA Branch",
        "retirement_eligibility_status",
        "positions",
        "Retirement Eligibility by Branch",
        "chart_retirement_eligibility_by_branch.png",
    )

    vac_branch = (
        df.groupby("DPHA Branch")
        .agg(authorized_positions=("Position / Job ID#", "count"), vacant_positions=("is_vacant", "sum"))
        .reset_index()
    )
    vac_branch["vacancy_rate"] = vac_branch["vacant_positions"] / vac_branch["authorized_positions"] * 100
    vac_branch = vac_branch.sort_values("vacancy_rate", ascending=True)
    bar_chart(
        vac_branch,
        "DPHA Branch",
        "vacancy_rate",
        "Vacancy Rate by Branch",
        "chart_vacancy_rate_by_branch.png",
        xlabel="Vacancy rate (%)",
    )

    vac_grade = (
        df.groupby("GS Paygrade")
        .agg(authorized_positions=("Position / Job ID#", "count"), vacant_positions=("is_vacant", "sum"))
        .reset_index()
    )
    vac_grade["vacancy_rate"] = vac_grade["vacant_positions"] / vac_grade["authorized_positions"] * 100
    vac_grade = vac_grade.sort_values("vacancy_rate", ascending=True)
    bar_chart(
        vac_grade,
        "GS Paygrade",
        "vacancy_rate",
        "Vacancy Rate by GS Grade",
        "chart_vacancy_rate_by_gs_grade.png",
        xlabel="Vacancy rate (%)",
    )

    manifest = pd.DataFrame(
        [
            {"chart_file": path.name, "path": str(path)}
            for path in sorted(OUT.glob("chart_*.png"))
        ]
    )
    manifest.to_csv(charts_dir_note, index=False)


if __name__ == "__main__":
    main()
