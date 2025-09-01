import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- SuperAdmin Credentials ---
USERNAME = "superadmin"
PASSWORD = "superpass"

# --- Session Setup ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()

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

# --- App Title ---
st.title("🐄 Udder Health Bangladesh — SuperAdmin Panel")

# --- Farmer Submission Form ---
st.header("📥 Submit Farmer Sample")
with st.form("farmer_form"):
    date_submitted = st.date_input("Date of Submission", value=date.today())
    farmer_name = st.text_input("Farmer's Name")
    farm_name = st.text_input("Farm Name")
    location = st.text_input("Location")
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
    breed = st.text_input("Breed of Cows")
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

# --- Data Analysis & Certification ---
st.header("📈 Data Analysis & Certification")
df = st.session_state.data.copy()


# SCC Assessment
df["SCC Grade"] = df["Somatic Cell Count"].apply(lambda x: (
    "Super Quality" if x <= 200000 else
    "Excellent" if x <= 400000 else
    "Very Good" if x <= 600000 else
    "Good" if x <= 800000 else
    "Fair" if pd.notnull(x) else None
))
df["SCC Status"] = df["Somatic Cell Count"].apply(lambda x: "Normal" if pd.notnull(x) and x <= 800000 else "High" if pd.notnull(x) else None)

# Milk Composition Assessment
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

# TBC Assessment
df["TBC Status"] = df["TBC"].apply(lambda x: "Normal" if pd.notnull(x) and x <= 100000 else "High" if pd.notnull(x) else None)

# Pending Input Tracker
def check_pending(row):
    pending = []
    if pd.isnull(row["Somatic Cell Count"]): pending.append("SCC")
    if any(pd.isnull(row[col]) for col in ["Fat%", "Protein%", "Lactose%", "SNF", "Freezing Point"]): pending.append("Milk Comp")
    if pd.isnull(row["TBC"]): pending.append("TBC")
    return ", ".join(pending) if pending else "✅ All Inputs Done"
df["Pending Inputs"] = df.apply(check_pending, axis=1)

# Days Since Submission
df["Days Since Submission"] = (pd.to_datetime(date.today()) - pd.to_datetime(df["Date"])).dt.days

# Display Summary
st.subheader("🧾 Submission Status Overview")
st.dataframe(df[[
    "Farmer", "Date", "Farm", "Days Since Submission", "Pending Inputs",
    "SCC Grade", "SCC Status", "Milk Comp Status", "TBC Status"
]])

# --- Dashboard Summary ---
st.header("📊 Lab Workflow Dashboard")

total_samples = len(df)
pending_scc = df["Somatic Cell Count"].isna().sum()
pending_milk = df[["Fat%", "Protein%", "Lactose%", "SNF", "Freezing Point"]].isna().any(axis=1).sum()
pending_tbc = df["TBC"].isna().sum()
overdue = df[(df["Days Since Submission"] > 3) & (df["Pending Inputs"] != "✅ All Inputs Done")].shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("🧑‍🌾 Total Submissions", total_samples)
col2.metric("🟡 Pending SCC", pending_scc)
col3.metric("🟣 Pending Milk Comp", pending_milk)

col4, col5 = st.columns(2)
col4.metric("🔵 Pending TBC", pending_tbc)
col5.metric("🔴 Overdue Samples (>3 days)", overdue)

# Certification Generator
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

# CSV Download
st.subheader("📥 Export Data")
st.download_button(
    label="Download Full Dataset as CSV",
    data=df.to_csv(index=False),
    file_name="udder_health_data.csv",
    mime="text/csv"
)

