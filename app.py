import streamlit as st
import pandas as pd
from datetime import datetime

# --- User Credentials ---
USERS = {
    "admin1": {"password": "admin1pass", "role": "Admin1"},
    "admin2": {"password": "admin2pass", "role": "Admin2"},
    "superadmin": {"password": "superpass", "role": "SuperAdmin"}
}

# --- Session Setup ---
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

# --- Shared Data View ---
if st.session_state.role in ["Admin1", "Admin2", "SuperAdmin"]:
    st.subheader("📄 All Submissions")
    st.dataframe(st.session_state.data)

# --- Admin1 & SuperAdmin: Farmer Submission + SCC + Milk Composition ---
if st.session_state.role in ["Admin1", "SuperAdmin"]:
    st.subheader("📥 Submit Farmer Sample")
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

    st.subheader("🧪 SCC & Milk Composition Entry")
    for i, row in st.session_state.data.iterrows():
        scc = st.number_input(f"SCC for {row['Farmer']}", key=f"scc_{i}", min_value=0)
        fat = st.number_input("Fat %", key=f"fat_{i}")
        protein = st.number_input("Protein %", key=f"protein_{i}")
        lactose = st.number_input("Lactose %", key=f"lactose_{i}")
        snf = st.number_input("SNF", key=f"snf_{i}")
        fp = st.number_input("Freezing Point", key=f"fp_{i}")
        if st.button(f"Save Lab Data for {row['Farmer']}", key=f"lab_btn_{i}"):
            st.session_state.data.at[i, "Somatic Cell Count"] = scc
            st.session_state.data.at[i, "Fat%"] = fat
            st.session_state.data.at[i, "Protein%"] = protein
            st.session_state.data.at[i, "Lactose%"] = lactose
            st.session_state.data.at[i, "SNF"] = snf
            st.session_state.data.at[i, "Freezing Point"] = fp
            st.success(f"Lab data saved for {row['Farmer']}")

# --- Admin2 & SuperAdmin: TBC Input ---
if st.session_state.role in ["Admin2", "SuperAdmin"]:
    st.subheader("🦠 Total Bacterial Count Entry")
    for i, row in st.session_state.data.iterrows():
        tbc = st.number_input("TBC", key=f"tbc_{i}", min_value=0)
        if st.button(f"Save TBC for {row['Farmer']}", key=f"tbc_btn_{i}"):
            st.session_state.data.at[i, "TBC"] = tbc
            st.success(f"TBC saved for {row['Farmer']}")

# --- Data Analysis & Assessment ---
if st.session_state.role in ["Admin1", "Admin2", "SuperAdmin"]:
    st.header("📈 Data Analysis & Assessment")
    if st.session_state.data.empty:
        st.info("No data available yet.")
    else:
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
            if any(pd.isnull(row[col]) for col in ["Fat%", "Protein%", "Lact
