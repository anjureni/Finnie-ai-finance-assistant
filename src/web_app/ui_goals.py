# src/web_app/ui_goals.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import json
import os

GOALS_PATH = os.path.join("data", "goals.json")

CATEGORIES = [
    "Retirement",
    "Education",
    "House",
    "Emergency Fund",
    "Vacation",
    "Other",
]


# -----------------------------
# Persistence helpers
# -----------------------------
def _ensure_data_dir():
    os.makedirs("data", exist_ok=True)


def _load_goals_from_disk():
    _ensure_data_dir()
    if not os.path.exists(GOALS_PATH):
        return []
    try:
        with open(GOALS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_goals_to_disk(goals):
    _ensure_data_dir()
    with open(GOALS_PATH, "w", encoding="utf-8") as f:
        json.dump(goals, f, indent=2)


def _init_goal_state():
    if "goals" not in st.session_state:
        goals = _load_goals_from_disk()

        if not goals:
            goals = [
                {
                    "name": "Emergency Fund",
                    "category": "Emergency Fund",
                    "target_amount": 10000.0,
                    "current_amount": 1500.0,
                    "monthly_contribution": 300.0,
                    "years": 2,
                    "annual_return_pct": 4.0,
                    "created_on": str(date.today()),
                }
            ]
            _save_goals_to_disk(goals)

        st.session_state["goals"] = goals


# -----------------------------
# Math helpers
# -----------------------------
def _future_value_schedule(current_amount, monthly_contribution, years, annual_return_pct):
    months = int(years * 12)
    r_m = (annual_return_pct / 100.0) / 12.0

    bal = float(current_amount)
    rows = []
    for m in range(0, months + 1):
        rows.append({"Month": m, "Balance": bal})
        bal = bal * (1.0 + r_m) + float(monthly_contribution)

    return pd.DataFrame(rows)


def _required_monthly_contribution(current_amount, target_amount, years, annual_return_pct):
    n = int(years * 12)
    r = (annual_return_pct / 100.0) / 12.0

    pv = float(current_amount)
    fv = float(target_amount)

    if n <= 0:
        return None

    if abs(r) < 1e-9:
        return max(0.0, (fv - pv) / n)

    growth = (1.0 + r) ** n
    pmt = (fv - pv * growth) * r / (growth - 1.0)
    return max(0.0, float(pmt))


def _plot_growth(df, target_amount, title):
    if df is None or df.empty:
        st.info("No projection to plot.")
        return

    fig, ax = plt.subplots()
    ax.plot(df["Month"], df["Balance"])
    ax.axhline(y=float(target_amount), linestyle="--")
    ax.set_title(title)
    ax.set_xlabel("Month")
    ax.set_ylabel("Balance ($)")
    st.pyplot(fig)


# -----------------------------
# UI
# -----------------------------
def render_goals_tab():
    st.subheader("🎯 Goal Planner")
    st.caption("Create, edit, and track goals with projections (education only).")

    _init_goal_state()
    goals = st.session_state["goals"]

    # ======================================================
    # 1) YOUR GOALS (full width)
    # ======================================================
    st.markdown("## ✅ Your Goals")

    filter_cat = st.selectbox(
        "Filter by category",
        options=["All"] + CATEGORIES,
        index=0,
        key="goal_cat_filter",
    )

    view_goals = goals
    if filter_cat != "All":
        view_goals = [g for g in goals if g.get("category") == filter_cat]

    if not view_goals:
        st.info("No goals found. Create one below.")
    else:
        df = pd.DataFrame(view_goals)
        # order columns so it shows nicely
        cols = [
            "name",
            "category",
            "target_amount",
            "current_amount",
            "monthly_contribution",
            "years",
            "annual_return_pct",
            "created_on",
        ]
        df = df[cols]

        # ✅ full width table + better formatting
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    # Delete goal
    st.markdown("### 🗑️ Delete a Goal")
    if goals:
        names = [g["name"] for g in goals]
        del_name = st.selectbox("Choose goal to delete", options=names, key="del_goal_name")
        if st.button("Delete Goal", use_container_width=True, key="btn_delete_goal"):
            st.session_state["goals"] = [g for g in goals if g["name"] != del_name]
            _save_goals_to_disk(st.session_state["goals"])
            st.rerun()
    else:
        st.info("No goals to delete.")

    st.divider()

    # ======================================================
    # 2) CREATE NEW GOAL (stacked below)
    # ======================================================
    st.markdown("## ➕ Create New Goal")

    with st.form("goal_form", clear_on_submit=True):
        name = st.text_input("Goal Name (e.g., House Down Payment)")
        category = st.selectbox("Category", options=CATEGORIES, index=0)

        c1, c2 = st.columns(2)
        with c1:
            target_amount = st.number_input("Target Amount ($)", min_value=0.0, value=20000.0, step=500.0)
            years = st.number_input("Time Horizon (years)", min_value=1, value=3, step=1)
        with c2:
            current_amount = st.number_input("Current Saved ($)", min_value=0.0, value=0.0, step=100.0)
            annual_return_pct = st.number_input("Expected Annual Return (%)", min_value=0.0, value=6.0, step=0.5)

        mode = st.radio(
            "Planning mode",
            ["I know my monthly contribution", "Calculate required monthly contribution"],
        )

        monthly_contribution = 0.0
        if mode == "I know my monthly contribution":
            monthly_contribution = st.number_input(
                "Monthly Contribution ($)", min_value=0.0, value=300.0, step=50.0
            )

        submitted = st.form_submit_button("Create Goal", use_container_width=True)

    if submitted:
        if not name.strip():
            st.warning("Please enter a goal name.")
        else:
            if mode == "Calculate required monthly contribution":
                monthly_contribution = _required_monthly_contribution(
                    current_amount=current_amount,
                    target_amount=target_amount,
                    years=int(years),
                    annual_return_pct=annual_return_pct,
                )
                st.success(f"Required monthly contribution ≈ **${monthly_contribution:,.2f}**")

            new_goal = {
                "name": name.strip(),
                "category": category,
                "target_amount": float(target_amount),
                "current_amount": float(current_amount),
                "monthly_contribution": float(monthly_contribution),
                "years": int(years),
                "annual_return_pct": float(annual_return_pct),
                "created_on": str(date.today()),
            }
            st.session_state["goals"].append(new_goal)
            _save_goals_to_disk(st.session_state["goals"])
            st.success("Goal created ✅")
            st.rerun()

    st.divider()

    # ======================================================
    # 3) EDIT GOAL (update monthly/target directly)
    # ======================================================
    st.markdown("## ✏️ Edit Goal")

    if not st.session_state["goals"]:
        st.info("Create a goal first to edit it.")
        st.caption("⚠️ Educational use only. Not financial advice.")
        return

    names = [g["name"] for g in st.session_state["goals"]]
    selected_edit = st.selectbox("Select a goal to edit", options=names, key="edit_goal_select")

    g = next(x for x in st.session_state["goals"] if x["name"] == selected_edit)

    with st.form("edit_goal_form"):
        category_e = st.selectbox("Category", options=CATEGORIES, index=CATEGORIES.index(g.get("category", "Other")))
        target_e = st.number_input("Target Amount ($)", min_value=0.0, value=float(g["target_amount"]), step=500.0)
        current_e = st.number_input("Current Saved ($)", min_value=0.0, value=float(g["current_amount"]), step=100.0)

        c1, c2, c3 = st.columns(3)
        with c1:
            years_e = st.number_input("Time Horizon (years)", min_value=1, value=int(g["years"]), step=1)
        with c2:
            return_e = st.number_input(
                "Expected Annual Return (%)", min_value=0.0, value=float(g["annual_return_pct"]), step=0.5
            )
        with c3:
            monthly_e = st.number_input(
                "Monthly Contribution ($)", min_value=0.0, value=float(g["monthly_contribution"]), step=50.0
            )

        recalc = st.checkbox("Recalculate required monthly contribution", value=False)
        save_btn = st.form_submit_button("Save Changes", use_container_width=True)

    if save_btn:
        if recalc:
            monthly_e = _required_monthly_contribution(
                current_amount=current_e,
                target_amount=target_e,
                years=int(years_e),
                annual_return_pct=return_e,
            )
            st.info(f"Recalculated monthly contribution ≈ **${monthly_e:,.2f}**")

        # update in place
        for i, item in enumerate(st.session_state["goals"]):
            if item["name"] == selected_edit:
                st.session_state["goals"][i] = {
                    **item,
                    "category": category_e,
                    "target_amount": float(target_e),
                    "current_amount": float(current_e),
                    "monthly_contribution": float(monthly_e),
                    "years": int(years_e),
                    "annual_return_pct": float(return_e),
                }
                break

        _save_goals_to_disk(st.session_state["goals"])
        st.success("Goal updated ✅")
        st.rerun()

    st.divider()

    # ======================================================
    # 4) GROWTH OVER TIME
    # ======================================================
    st.markdown("## 📈 Growth Over Time")

    names2 = [g["name"] for g in st.session_state["goals"]]
    selected = st.selectbox("Select a goal to visualize", names2, key="goal_select")

    g2 = next(x for x in st.session_state["goals"] if x["name"] == selected)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Target", f"${g2['target_amount']:,.2f}")
    c2.metric("Current", f"${g2['current_amount']:,.2f}")
    c3.metric("Monthly", f"${g2['monthly_contribution']:,.2f}")
    c4.metric("Return", f"{g2['annual_return_pct']:.1f}%")

    proj = _future_value_schedule(
        current_amount=g2["current_amount"],
        monthly_contribution=g2["monthly_contribution"],
        years=g2["years"],
        annual_return_pct=g2["annual_return_pct"],
    )

    colA, colB = st.columns([1.1, 0.9], gap="large")
    with colA:
        _plot_growth(proj, g2["target_amount"], f"{g2['name']} — Growth Projection")

    with colB:
        st.markdown("#### Projection Table (last 12 months)")
        st.dataframe(proj.tail(12), use_container_width=True, hide_index=True)

        final_balance = float(proj["Balance"].iloc[-1])
        gap = float(g2["target_amount"] - final_balance)
        if gap <= 0:
            st.success(f"On track ✅ Projected final balance: **${final_balance:,.2f}**")
        else:
            st.warning(f"Projected final balance: **${final_balance:,.2f}** (short by **${gap:,.2f}**)")

    st.divider()
    st.caption("⚠️ Educational use only. Not financial advice.")
