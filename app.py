import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date


# --- SuperAdmin Credentials ---
USERNAME = "superadmin"
PASSWORD = "superpass"

# --- Session Setup ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()
if "categories" not in st.session_state:
    st.session_state.categories = {
        "Farm Name": [],
        "Location": [],
        "Farmer's Name": [],
        "Breed of Cows": []
    }

# --- Login ---
st.sidebar.title("🔐 SuperAdmin Login")
if not st.session_state.authenticated:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Logged in as SuperAdmin")
        else:
            st.error("❌ Invalid credentials")
    st.stop()
else:
    st.sidebar.markdown("👤 Logged in as: `SuperAdmin`")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.stop()

# --- Category Manager ---
st.sidebar.header("🗂️ Category Manager")
category = st.sidebar.selectbox("Select Category", list(st.session_state.categories.keys()))
new_value = st.sidebar.text_input("Add New Value")
if st.sidebar.button("➕ Add to Category"):
    if new_value and new_value not in st.session_state.categories[category]:
        st.session_state.categories[category].append(new_value)
        st.sidebar.success(f"Added '{new_value}' to {category}")
    elif new_value:
        st.sidebar.warning(f"'{new_value}' already exists in {category}")

# --- App Title ---
st.title("🐄 Udder Health Bangladesh — SuperAdmin Panel")

# --- Farmer Submission Form ---
st.header("📥 Submit Farmer Sample")
with st.form("farmer_form"):
    date_submitted = st.date_input("Date of Submission", value=date.today())
    farmer_name = st.selectbox("Farmer's Name", st.session_state.categories["Farmer's Name"])
    farm_name = st.selectbox("Farm Name", st.session_state.categories["Farm Name"])
    location = st.selectbox("Location", st.session_state.categories["Location"])
    mobile = st.text_input("Mobile Number")
    milk_today = st.number_input("Total Litres of Milk Today", min_value=0.0)
    lactating_total = st.number_input("Total Lactating Cows", min_value=0)
    lactating_0_3 = st.number_input("Lactating Cows <3 Months", min_value=0)
    lactating_3_6 = st.number_input("Lactating Cows 3–6 Months", min_value=0)
    lactating_6_9 = st.number_input("Lactating Cows 6–9 Months", min_value=0)
    lactating_9_plus = st.number_input("Lactating Cows >9 Months", min_value=0)
    dry_cows = st.number_input("Dry Cows", min_value=0)
    heifers = st.number_input("Heifers", min_value=0)
    calves = st.number_input("Calves <1 Year", min_value=0)
    mastitis_now = st.number_input("Clinical Mastitis Cases Now", min_value=0)
    mastitis_last = st.number_input("Clinical Mastitis Cases Last Month", min_value=0)
    breed = st.selectbox("Breed of Cows", st.session_state.categories["Breed of Cows"])
    submitted = st.form_submit_button("Submit")

    if submitted:
        entry = {
            "Date": date_submitted, "Farmer": farmer_name, "Farm": farm_name, "Location": location, "Mobile": mobile,
            "Milk Today": milk_today, "Lactating Total": lactating_total, "Lactating <3M": lactating_0_3,
            "Lactating 3–6M": lactating_3_6, "Lactating 6–9M": lactating_6_9, "Lactating >9M": lactating_9_plus,
            "Dry Cows": dry_cows, "Heifers": heifers, "Calves <1Y": calves,
            "Mastitis Now": mastitis_now, "Mastitis Last": mastitis_last, "Breed": breed,
            "Somatic Cell Count": None, "SCC Grade": None, "SCC Status": None, "SCC Entry Date": None,
            "Fat%": None, "Protein%": None, "Lactose%": None, "SNF": None, "Freezing Point": None,
            "Milk Comp Status": None, "Milk Composition Entry Date": None,
            "TBC": None, "TBC Status": None, "TBC Entry Date": None
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([entry])], ignore_index=True)
        st.success("✅ Submission successful!")

# --- Lab Input Section ---
st.header("🧪 Enter Lab Results")
for i, row in st.session_state.data.iterrows():
    st.subheader(f"{row['Farmer']} ({row['Date']})")
    scc = st.number_input("Somatic Cell Count", key=f"scc_{i}", min_value=0)
    fat = st.number_input("Fat %", key=f"fat_{i}")
    protein = st.number_input("Protein %", key=f"protein_{i}")
    lactose = st.number_input("Lactose %", key=f"lactose_{i}")
    snf = st.number_input("SNF", key=f"snf_{i}")
    fp = st.number_input("Freezing Point", key=f"fp_{i}")
    tbc = st.number_input("Total Bacterial Count (TBC)", key=f"tbc_{i}", min_value=0)
    if st.button(f"Save Lab Data for {row['Farmer']}", key=f"lab_btn_{i}"):
        today = date.today()
        st.session_state.data.at[i, "Somatic Cell Count"] = scc
        st.session_state.data.at[i, "SCC Entry Date"] = today
        st.session_state.data.at[i, "Fat%"] = fat
        st.session_state.data.at[i, "Protein%"] = protein
        st.session_state.data.at[i, "Lactose%"] = lactose
        st.session_state.data.at[i, "SNF"] = snf
        st.session_state.data.at[i, "Freezing Point"] = fp
        st.session_state.data.at[i, "Milk Composition Entry Date"] = today
        st.session_state.data.at[i, "TBC"] = tbc
        st.session_state.data.at[i, "TBC Entry Date"] = today
        st.success(f"✅ Lab data saved for {row['Farmer']}")

# --- Data Analysis & Dashboard ---
st.header("📈 Data Analysis & Certification")
df = st.session_state.data.copy()

if df.empty or "Somatic Cell Count" not in df.columns:
    st.info("📭 No data available to analyze. Please submit farmer samples first.")
else:
    # --- Assessments ---
    df["SCC Grade"] = df["Somatic Cell Count"].apply(lambda x: (
        "Super Quality" if x <= 200000 else
        "Excellent" if x <= 400000 else
        "Very Good" if x <= 600000 else
        "Good" if x <= 800000 else
        "Fair" if pd.notnull(x) else None
    ))
    df["SCC Status"] = df["Somatic Cell Count"].apply(lambda x: "Normal" if pd.notnull(x) and x <= 800000 else "High" if pd.notnull(x) else None)

    def assess_milk(row):
        if pd.isnull(row["Fat%"]): return None
        return "Normal" if (
            3 <= row["Fat%"] <= 5 and
            3.2 <= row["Protein%"] <= 3.8 and
            4.4 <= row["Lactose%"] <= 4.6 and
            row["SNF"] >= 8.0 and
            -0.565 <= row["Freezing Point"] <= -0.532
        ) else "Abnormal"
    df["Milk Comp Status"] = df.apply(assess_milk, axis=1)
    df["TBC Status"] = df["TBC"].apply(lambda x: "Normal" if pd.notnull(x) and x <= 100000 else "High" if pd.notnull(x) else None)

    # --- Pending Tracker & Aging ---
    def check_pending(row):
        pending = []
        if pd.isnull(row["Somatic Cell Count"]): pending.append("SCC")
        if any(pd.isnull(row[col]) for col in ["Fat%", "Protein%", "Lactose%", "SNF", "Freezing Point"]): pending.append("Milk Comp")
        if pd.isnull(row["TBC"]): pending.append("TBC")
        return ", ".join(pending) if pending else "✅ All Inputs Done"
    df["Pending Inputs"] = df.apply(check_pending, axis=1)
    df["Days Since Submission"] = (pd.to_datetime(date.today()) - pd.to_datetime(df["Date"])).dt.days

    # --- Certification Generator ---
    st.subheader("📄 Generate Certifications")
    cert_type = st.selectbox("Select Certification Type", ["Somatic Cell Count", "Milk Composition", "TBC"])
    for i, row in df.iterrows():
        st.markdown(f"**Farmer:** {row['Farmer']} | **Date:** {row['Date']}")
        if cert_type == "Somatic Cell Count":
            st.write(f"""
            Somatic Cell Count: {row['Somatic Cell Count']}
            Grade: {row['SCC Grade']}
            Status: {row['SCC Status']}
            Entry Date: {row['SCC Entry Date']}
            """)
        elif cert_type == "Milk Composition":
            st.write(f"""
            Fat: {row['Fat%']}%
            Protein: {row['Protein%']}%
            Lactose: {row['Lactose%']}%
            SNF: {row['SNF']}
            Freezing Point: {row['Freezing Point']}
            Status: {row['Milk Comp Status']}
            Entry Date: {row['Milk Composition Entry Date']}
            """)
        elif cert_type == "TBC":
            st.write(f"""
            Total Bacterial Count (TBC): {row['TBC']}
            Status: {row['TBC Status']}
            Entry Date: {row['TBC Entry Date']}
            """)

    # --- CSV Export ---
    st.subheader("📥 Export Data")
    st.download_button(
        label="Download Full Dataset as CSV",
        data=df.to_csv(index=False),
        file_name="udder_health_data.csv",
        mime="text/csv"
    )

from fpdf import FPDF
import io

def generate_scc_certificate(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Background image
    pdf.image("letterpad_scc.png", x=0, y=0, w=210)

    # Extract values
    test_date = pd.to_datetime(row["Date"]).strftime("%-d %B %Y")
    next_test_date = (pd.to_datetime(row["Date"]) + pd.Timedelta(days=30)).strftime("%-d %B %Y")
    farm_name = row["Farm"]
    location = row["Location"]
    farmer_name = row["Farmer"]
    lactating_cows = int(row["Lactating Total"])
    scc_value = int(row["Somatic Cell Count"])
    scc_grade = row["SCC Grade"]

    # Certificate text
    pdf.set_xy(20, 40)
    pdf.multi_cell(0, 10, f"""This is to certify that bulk milk sample tested on {test_date} from {farm_name} located at {location} owned by Mr. {farmer_name} for somatic cell count (SCC) using Ekomilk Horizon UNLIMITED milk analyzer (EKOMILK, Bulgaria).

The test result for SCC obtained from bulk milk of {lactating_cows} lactating cows was {scc_value:,} cells/mL of milk.
The milk quality was “{scc_grade}” according to the test results.

Milk Quality Categorization — Somatic Cell Count (cells/mL of milk):
☐ Super quality < 200,000
☐ Excellent 200,000 to < 400,000
☐ Very good 400,000 to < 600,000
☐ Good 600,000 to < 800,000
█ Fair ≥ 800,000

This test is valid for one month.
Next suggested test date: {next_test_date}.
""")

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer
    
# Inside your SCC certification loop
if cert_type == "Somatic Cell Count":
    st.write(f"""
    Somatic Cell Count: {row['Somatic Cell Count']}
    Grade: {row['SCC Grade']}
    Status: {row['SCC Status']}
    Entry Date: {row['SCC Entry Date']}
    """)

    # PDF download button
    pdf_buffer = generate_scc_certificate(row)
    st.download_button(
        label="📄 Download SCC Certificate as PDF",
        data=pdf_buffer.getvalue(),
        file_name=f"scc_certificate_{row['Farmer'].replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

    # --- Interactive Dashboard ---
    st.header("📊 Lab Analytics Dashboard")
    tab1, tab2, tab3 = st.tabs(["🔍 Filter & Summary", "📊 Descriptive Stats", "📦 Box Plots"])

    with tab1:
        st.subheader("🔍 Filter Panel")
        min_date = df["Date"].min()
        max_date = df["Date"].max()
        start_date, end_date = st.date_input("Select Date Range", value=(min_date, max_date))
        farm_filter = st.selectbox("Farm Name", ["All"] + sorted(df["Farm"].dropna().unique()))
        breed_filter = st.selectbox("Breed of Cows", ["All"] + sorted(df["Breed"].dropna().unique()))
        year_filter = st.selectbox("Year", ["All"] + sorted(df["Date"].dt.year.dropna().astype(str).unique()))
        month_filter = st.selectbox("Month", ["All"] + sorted(df["Date"].dt.month.dropna().astype(str).unique()))

        filtered_df = df.copy()
        filtered_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(start_date)) & (filtered_df["Date"] <= pd.to_datetime(end_date))]
        if farm_filter != "All":
            filtered_df = filtered_df[filtered_df["Farm"] == farm_filter]
        if breed_filter != "All":
            filtered_df = filtered_df[filtered_df["Breed"] == breed_filter]
        if year_filter != "All":
            filtered_df = filtered_df[filtered_df["Date"].dt.year.astype(str) == year_filter]
        if month_filter != "All":
            filtered_df = filtered_df[filtered_df["Date"].dt.month.astype(str) == month_filter]

        st.subheader("📈 Sample Summary")
        total_samples = len(filtered_df)
        pending_scc = filtered_df["Somatic Cell Count"].isna().sum()
        pending_milk = filtered_df[["Fat%", "Protein%", "Lactose%", "SNF", "Freezing Point"]].isna().any(axis=1).sum()
        pending_tbc = filtered_df["TBC"].isna().sum()
        overdue = filtered_df[(filtered_df["Days Since Submission"] > 3) & (filtered_df["Pending Inputs"] != "✅ All Inputs Done")].shape[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("🧑‍🌾 Total Samples", total_samples)
        col2.metric("🟡 Pending SCC", pending_scc)
        col3.metric("🟣 Pending Milk Comp", pending_milk)

        col4, col5 = st.columns(2)
        col4.metric("🔵 Pending TBC", pending_tbc)
        col5.metric("🔴 Overdue Samples (>3 days)", overdue)

    with tab2:
        st.subheader("📊 Descriptive Statistics")

        def describe_column(col):
            valid = filtered_df[col].dropna()
            if valid.empty:
                return "No data available"
            return {
                "Mean": round(valid.mean(), 2),
                "Q1": round(valid.quantile(0.25), 2),
                "Median": round(valid.median(), 2),
                "Q3": round(valid.quantile(0.75), 2),
                "Count": len(valid)
            }

        metrics = {
            "Somatic Cell Count": describe_column("Somatic Cell Count"),
            "Fat%": describe_column("Fat%"),
            "Protein%": describe_column("Protein%"),
            "Lactose%": describe_column("Lactose%"),
            "SNF": describe_column("SNF"),
            "Freezing Point": describe_column("Freezing Point"),
            "TBC": describe_column("TBC")
        }

        for test, stats in metrics.items():
            st.markdown(f"**{test}**")
            if isinstance(stats, str):
                st.write(stats)
            else:
                st.write(stats)

    with tab3:
        st.subheader("📦 Box Plot Visualizations")
        box_cols = ["Somatic Cell Count", "Fat%", "Protein%", "Lactose%", "SNF", "Freezing Point", "TBC"]
        for col in box_cols:
            if filtered_df[col].dropna().empty:
                st.write(f"📭 No data for {col}")
                continue
            fig, ax = plt.subplots()
            sns.boxplot(y=filtered_df[col], ax=ax)
            ax.set_title(f"{col} Distribution")
            st.pyplot(fig)
