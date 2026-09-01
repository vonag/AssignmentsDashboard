import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os

st.set_page_config(page_title="Assignment Dashboard", page_icon="📚", layout="wide")

DATA_FILE = "assignments.csv"
COLUMNS = ["Class", "Assignment", "Due Date", "Status", "Notes"]

CLASS_COLORS = [
    "#4C6EF5", "#12B886", "#F59F00", "#E64980",
    "#7048E8", "#15AABF", "#FA5252", "#82C91E",
]


def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["Due Date"])
        df["Due Date"] = df["Due Date"].dt.date
        return df
    return pd.DataFrame(columns=COLUMNS)


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


def urgency_flag(row, today):
    if row["Status"] == "Done":
        return "✅"
    due = row["Due Date"]
    if pd.isna(due):
        return "⬜"
    days_left = (due - today).days
    if days_left < 0:
        return "🔴"
    if days_left <= 2:
        return "🟠"
    if days_left <= 6:
        return "🟡"
    return "🟢"


if "df" not in st.session_state:
    st.session_state.df = load_data()

st.markdown(
    """<style>
    .stApp { background-color: #FDEEF4; }
    </style>""",
    unsafe_allow_html=True,
)

st.title("Assignments")
st.caption("One card per class, sorted by due date, color-coded so you can see what needs attention at a glance.")

# --- Sidebar: add + backup ---
with st.sidebar:
    st.header("Add an assignment")

    existing_classes = sorted(st.session_state.df["Class"].dropna().unique().tolist())
    class_choice = st.selectbox("Class", existing_classes + ["+ New class"] if existing_classes else ["+ New class"])
    new_class_name = ""
    if class_choice == "+ New class":
        new_class_name = st.text_input("New class name")

    with st.form("add_form", clear_on_submit=True):
        new_assignment = st.text_input("Assignment")
        new_due = st.date_input("Due date", value=date.today() + timedelta(days=7))
        new_notes = st.text_input("Notes (optional)")
        submitted = st.form_submit_button("Add")
        if submitted:
            final_class = new_class_name.strip() if class_choice == "+ New class" else class_choice
            if final_class and new_assignment:
                new_row = pd.DataFrame([{
                    "Class": final_class,
                    "Assignment": new_assignment,
                    "Due Date": new_due,
                    "Status": "Not started",
                    "Notes": new_notes,
                }])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df)
                st.rerun()
            else:
                st.warning("Need a class and an assignment name.")

    st.divider()
    st.markdown("**Color key**")
    st.markdown("🔴 Overdue &nbsp; 🟠 Due ≤2 days &nbsp; 🟡 Due ≤6 days &nbsp; 🟢 Later &nbsp; ✅ Done")

    st.divider()
    st.download_button(
        "⬇️ Download backup (CSV)",
        data=st.session_state.df.to_csv(index=False),
        file_name="assignments_backup.csv",
        mime="text/csv",
    )
    uploaded = st.file_uploader("⬆️ Restore from backup", type="csv")
    if uploaded is not None:
        restored = pd.read_csv(uploaded, parse_dates=["Due Date"])
        restored["Due Date"] = restored["Due Date"].dt.date
        st.session_state.df = restored
        save_data(st.session_state.df)
        st.rerun()

today = date.today()
df = st.session_state.df.copy()

# --- Top banners: overdue / due soon, across all classes ---
if not df.empty:
    df["_days_left"] = df["Due Date"].apply(lambda d: (d - today).days if pd.notna(d) else None)
    overdue = df[(df["_days_left"] < 0) & (df["Status"] != "Done")]
    soon = df[(df["_days_left"] >= 0) & (df["_days_left"] <= 2) & (df["Status"] != "Done")]
    if not overdue.empty:
        st.error("🔴 Overdue: " + ", ".join(f"{r.Assignment} ({r.Class})" for r in overdue.itertuples()))
    if not soon.empty:
        st.warning("🟠 Due within 2 days: " + ", ".join(f"{r.Assignment} ({r.Class})" for r in soon.itertuples()))

    total = len(df)
    done = len(df[df["Status"] == "Done"])
    st.progress(done / total if total else 0, text=f"{done} of {total} assignments done overall")

st.divider()

if df.empty:
    st.info("No assignments yet — add your first one from the sidebar.")
else:
    classes = sorted(df["Class"].dropna().unique().tolist())
    updated_frames = []

    for i, cls in enumerate(classes):
        color = CLASS_COLORS[i % len(CLASS_COLORS)]
        class_df = df[df["Class"] == cls].sort_values("Due Date").copy()
        class_df["Flag"] = class_df.apply(lambda r: urgency_flag(r, today), axis=1)

        n_pending = len(class_df[class_df["Status"] != "Done"])
        next_due = class_df[class_df["Status"] != "Done"]["Due Date"].min()
        next_due_str = f" · next due {next_due.strftime('%b %-d')}" if pd.notna(next_due) else ""

        st.markdown(
            f"""<div style="border-left: 6px solid {color}; padding-left: 12px; margin-bottom: 4px;">
            <h4 style="margin-bottom:0;">{cls}</h4>
            <span style="color: gray;">{n_pending} pending{next_due_str}</span>
            </div>""",
            unsafe_allow_html=True,
        )

        display_cols = ["Flag", "Assignment", "Due Date", "Status", "Notes"]
        edited = st.data_editor(
            class_df[display_cols],
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            disabled=["Flag"],
            column_config={
                "Flag": st.column_config.TextColumn("", width="small"),
                "Due Date": st.column_config.DateColumn("Due Date", format="MMM D, YYYY"),
                "Status": st.column_config.SelectboxColumn("Status", options=["Not started", "In progress", "Done"]),
            },
            key=f"editor_{cls}",
        )
        edited = edited.drop(columns=["Flag"], errors="ignore")
        edited["Class"] = cls
        updated_frames.append(edited[COLUMNS])
        st.markdown("&nbsp;", unsafe_allow_html=True)

    st.session_state.df = pd.concat(updated_frames, ignore_index=True)
    save_data(st.session_state.df)
