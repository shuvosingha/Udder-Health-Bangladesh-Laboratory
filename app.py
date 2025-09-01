import streamlit as st
import pandas as pd
from datetime import datetime

# --- User Credentials ---
USERS = {
    "farmer1": {"password": "milk123", "role": "Farmer"},
    "admin1": {"password": "scc456", "role": "Admin1"},
    "admin2": {"password": "milk789", "role": "Admin2"},
    "admin3": {"password": "tbc321", "role": "Admin3"},
    "superadmin": {"password": "labmaster", "role": "SuperAdmin"}
}

# --- Role Permissions ---
ROLE_PERMISSIONS = {
    "Farmer": ["submit_data"],
    "Admin1": ["view_data", "add_scc"],
    "Admin2": ["view_data", "add_milk_comp"],
    "Admin3": ["view_data", "add_tbc"],
    "SuperAdmin": ["view_data", "add_scc", "add_milk_comp", "add_tbc", "download_data", "generate_cert"]
}

# --- Session State Setup ---
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()

# --- Sidebar Login ---
st.sidebar.title("🔐 Login")
if st.session_state.role is None:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")

    if login_btn:
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state.role = user["role"]
            st.session_state.username = username
            st.success(f"Welcome, {username} ({user['role']})")
        else:
            st.error("Invalid username or password")
else:
    st.sidebar.markdown(f"👤 Logged in as: `{st.session_state.username}` | Role: `{st.session_state.role}`")
    if st.sidebar.button("Logout"):
        st.session_state.role = None
        st.session_state.username = None

# --- App Title ---
st.title("🐄 Udder Health Bangladesh")

# --- Permissions ---
permissions = ROLE_PERMISSIONS.get(st.session_state.role, [])

# --- Farmer Submission ---
if "submit_data" in permissions:
    st.header("📥 Sample Submission Form")
    with st.form("farmer_form"):
        date = st.date_input("Date of Submission", value=datetime.today())
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
                "Date": date, "Farmer": farmer_name, "Farm": farm_name, "Location": location, "Mobile": mobile,
                "Milk Today": milk_today, "Lactating Total": lactating_total, "Lactating <3M": lactating_0_3,
                "Lactating 3–6M": lactating_3_6, "Lactating 6–9M": lactating_6_9, "Lactating >9M": lactating_9_plus,
                "Dry Cows": dry_cows, "Heifers": heifers, "Calves <1Y": calves,
                "Mastitis Now": mastitis_now, "Mastitis Last": mastitis_last, "Breed": breed,
                "Somatic Cell Count": None, "SCC Grade": None, "SCC Status": None,
                "Fat%": None, "Protein%": None, "Lactose%": None, "SNF": None, "Freezing Point": None, "Milk Comp Status": None,
                "TBC": None, "TBC Status": None
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([entry])], ignore_index=True)
            st.success("Submission successful!")

# --- Admin1: SCC Input ---
if "add_scc" in permissions:
    st.header("🧪 Somatic Cell Count Entry")
    for i, row in st.session_state.data.iterrows():
        st.subheader(f"{row['Farmer']} ({row['Date']})")
        scc = st.number_input(f"SCC for {row['Farmer']}", key=f"scc_{i}", min_value=0)
        if st.button(f"Save SCC for {row['Farmer']}", key=f"scc_btn_{i}"):
            st.session_state.data.at[i, "Somatic Cell Count"] = scc

# --- Admin2: Milk Composition Input ---
if "add_milk_comp" in permissions:
    st.header("🥛 Milk Composition Entry")
    for i, row in st.session_state.data.iterrows():
        st.subheader(f"{row['Farmer']} ({row['Date']})")
        fat = st.number_input("Fat %", key=f"fat_{i}")
        protein = st.number_input("Protein %", key=f"protein_{i}")
        lactose = st.number_input("Lactose %", key=f"lactose_{i}")
        snf = st.number_input("SNF", key=f"snf_{i}")
        fp = st.number_input("Freezing Point", key=f"fp_{i}")
        if st.button(f"Save Milk Comp for {row['Farmer']}", key=f"milk_btn_{i}"):
            st.session_state.data.at[i, "Fat%"] = fat
            st.session_state.data.at[i, "Protein%"] = protein
            st.session_state.data.at[i, "Lactose%"] = lactose
            st.session_state.data.at[i, "SNF"] = snf
            st.session_state.data.at[i, "Freezing Point"] = fp

# --- Admin3: TBC Input ---
if "add_tbc" in permissions:
    st.header("🦠 Total Bacterial Count Entry")
    for i, row in st.session_state.data.iterrows():
        st.subheader(f"{row['Farmer']} ({row['Date']})")
        tbc = st.number_input("TBC", key=f"tbc_{i}", min_value=0)
        if st.button(f"Save TBC for {row['Farmer']}", key=f"tbc_btn_{i}"):
            st.session_state.data.at[i, "TBC"] = tbc


# --- Unified Data View for Admins ---
if st.session_state.role in ["Admin1", "Admin2", "Admin3", "SuperAdmin"]:
    st.header("📋 Full Submission Table")
    st.dataframe(st.session_state.data)

    st.markdown("---")

    # Role-specific input sections
    if st.session_state.role in ["Admin1", "SuperAdmin"]:
        st.subheader("🧪 Somatic Cell Count Entry")
        for i, row in st.session_state.data.iterrows():
            scc = st.number_input(f"SCC for {row['Farmer']} ({row['Date']})", key=f"scc_{i}", min_value=0)
            if st.button(f"Save SCC for {row['Farmer']}", key=f"scc_btn_{i}"):
                st.session_state.data.at[i, "Somatic Cell Count"] = scc

    if st.session_state.role in ["Admin2", "SuperAdmin"]:
        st.subheader("🥛 Milk Composition Entry")
        for i, row in st.session_state.data.iterrows():
            fat = st.number_input("Fat %", key=f"fat_{i}")
            protein = st.number_input("Protein %", key=f"protein_{i}")
            lactose = st.number_input("Lactose %", key=f"lactose_{i}")
            snf = st.number_input("SNF", key=f"snf_{i}")
            fp = st.number_input("Freezing Point", key=f"fp_{i}")
            if st.button(f"Save Milk Comp for {row['Farmer']}", key=f"milk_btn_{i}"):
                st.session_state.data.at[i, "Fat%"] = fat
                st.session_state.data.at[i, "Protein%"] = protein
                st.session_state.data.at[i, "Lactose%"] = lactose
                st.session_state.data.at[i, "SNF"] = snf
                st.session_state.data.at[i, "Freezing Point"] = fp

    if st.session_state.role in ["Admin3", "SuperAdmin"]:
        st.subheader("🦠 Total Bacterial Count Entry")
        for i, row in st.session_state.data.iterrows():
            tbc = st.number_input("TBC", key=f"tbc_{i}", min_value=0)
            if st.button(f"Save TBC for {row['Farmer']}", key=f"tbc_btn_{i}"):
                st.session_state.data.at[i, "TBC"] = tbc

# --- Data Analysis & Assessment ---
# --- Data Analysis & Assessment ---
if "view_data" in permissions or "download_data" in permissions:
    st.header("📈 Data Analysis & Assessment")

    if st.session_state.data.empty:
        st.info("No data available yet.")
    else:
        df = st.session_state.data.copy()

        # Define check_pending before using it
        def check_pending(row):
            pending = []
            if pd.isnull(row.get("Somatic Cell Count")):
                pending.append("Admin1: SCC")
            if any(pd.isnull(row.get(col)) for col in ["Fat%", "Protein%", "Lactose%", "SNF", "Freezing Point"]):
                pending.append("Admin2: Milk Comp")
            if pd.isnull(row.get("TBC")):
                pending.append("Admin3: TBC")
            return ", ".join(pending) if pending else "✅ All Inputs Done"

        df["Pending Inputs"] = df.apply(check_pending, axis=1)

        # Display status overview
        st.subheader("🧾 Submission Status Overview")
        st.dataframe(df[["Farmer", "Date", "Farm", "Pending Inputs"]])

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


# --- Pending Admin Input Tracker ---
def check_pending(row):
    pending = []
    if pd.isnull(row["Somatic Cell Count"]):
        pending.append("Admin1: SCC")
    if pd.isnull(row["Fat%"]) or pd.isnull(row["Protein%"]) or pd.isnull(row["Lactose%"]) or pd.isnull(row["SNF"]) or pd.isnull(row["Freezing Point"]):
        pending.append("Admin2: Milk Comp")
    if pd.isnull(row["TBC"]):
        pending.append("Admin3: TBC")
    return ", ".join(pending) if pending else "✅ All Inputs Done"

def check_pending(row):
    pending = []
    if pd.isnull(row.get("Somatic Cell Count")):
        pending.append("Admin1: SCC")
    if any(pd.isnull(row.get(col)) for col in ["Fat%", "Protein%", "Lactose%", "SNF", "Freezing Point"]):
        pending.append("Admin2: Milk Comp")
    if pd.isnull(row.get("TBC")):
        pending.append("Admin3: TBC")
    return ", ".join(pending) if pending else "✅ All Inputs Done"
