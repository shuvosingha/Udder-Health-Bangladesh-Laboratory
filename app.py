# app.py

import streamlit as st
import pandas as pd
from datetime import datetime

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
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()

# --- Sidebar Login ---
st.sidebar.title("🔐 Role Login")
role = st.sidebar.selectbox("Select your role", list(ROLE_PERMISSIONS.keys()))
st.session_state.role = role
permissions = ROLE_PERMISSIONS[role]

# --- App Title ---
st.title("🐄 Udder Health Bangladesh")

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
        if scc <= 200000:
            grade = "Super Quality"
        elif scc <= 400000:
            grade = "Excellent"
        elif scc <= 600000:
            grade = "Very Good"
        elif scc <= 800000:
            grade = "Good"
        else:
            grade = "Fair"
        status = "Normal" if scc <= 800000 else "High"
        if st.button(f"Save SCC for {row['Farmer']}", key=f"scc_btn_{i}"):
            st.session_state.data.at[i, "Somatic Cell Count"] = scc
            st.session_state.data.at[i, "SCC Grade"] = grade
            st.session_state.data.at[i, "SCC Status"] = status
            st.success(f"SCC saved for {row['Farmer']}")

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
        status = "Normal" if (3 <= fat <= 5 and 3.2 <= protein <= 3.8 and 4.4 <= lactose <= 4.6 and snf >= 8.0 and -0.565 <= fp <= -0.532) else "Abnormal"
        if st.button(f"Save Milk Comp for {row['Farmer']}", key=f"milk_btn_{i}"):
            st.session_state.data.at[i, "Fat%"] = fat
            st.session_state.data.at[i, "Protein%"] = protein
            st.session_state.data.at[i, "Lactose%"] = lactose
            st.session_state.data.at[i, "SNF"] = snf
            st.session_state.data.at[i, "Freezing Point"] = fp
            st.session_state.data.at[i, "Milk Comp Status"] = status
            st.success(f"Milk composition saved for {row['Farmer']}")

# --- Admin3: TBC Input ---
if "add_tbc" in permissions:
    st.header("🦠 Total Bacterial Count Entry")
    for i, row in st.session_state.data.iterrows():
        st.subheader(f"{row['Farmer']} ({row['Date']})")
        tbc = st.number_input("TBC", key=f"tbc_{i}", min_value=0)
        status = "Normal" if tbc <= 100000 else "High"
        if st.button(f"Save TBC for {row['Farmer']}", key=f"tbc_btn_{i}"):
            st.session_state.data.at[i, "TBC"] = tbc
            st.session_state.data.at[i, "TBC Status"] = status
            st.success(f"TBC saved for {row['Farmer']}")

# --- SuperAdmin: Full Access ---
if "download_data" in permissions:
    st.header("📊 Full Data Overview")
    st.dataframe(st.session_state.data)
    st.download_button("Download CSV", st.session_state.data.to_csv(index=False), "udder_health_data.csv")

if "generate_cert" in permissions:
    st.subheader("📄 Generate Certifications")
    cert_type = st.selectbox("Select Certification Type", ["Somatic Cell Count", "Milk Composition", "TBC"])
    for i, row in st.session_state.data.iterrows():
        st.markdown(f"**Farmer:** {row['Farmer']} | **Date:** {row['Date']}")
        if cert_type == "Somatic Cell Count":
            st.write(f"SCC: {row['Somatic Cell Count']} | Grade: {row['SCC Grade']} | Status: {row['SCC Status']}")
        elif cert_type == "Milk Composition":
            st.write(f"Fat: {row['Fat%']} | Protein: {row['Protein%']} | Lactose: {row['Lactose%']} | SNF: {row['SNF']} | FP: {row['Freezing Point']} | Status: {row['Milk Comp Status']}")
        elif cert_type == "TBC":
            st.write(f"TBC: {row['TBC']} |
