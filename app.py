import streamlit as st
import io
import pandas as pd


st.set_page_config(page_title="Multi-Owner Revenue Calculator", layout="centered")

st.title("🛢️ Multi-Owner Oil & Gas Revenue Calculator")
st.markdown("As the **operator**, calculate your total royalty obligations, revenue, and profit across multiple mineral owners.")

# --- Global Inputs ---
st.subheader("📥 Global Inputs")

production_revenue = st.number_input("Gross Production Revenue ($)", min_value=0.0, value=100000.0, step=1000.0)
total_acres = st.number_input("Total Tract Acres", min_value=0.01, value=160.0)
estimated_costs = st.number_input("Estimated Drilling + Operating Costs ($)", min_value=0.0, value=50000.0, step=1000.0)

# --- Royalty Selection ---
st.markdown("### 🎯 Lease Royalty Options")

common_royalties = {
    "12.5% (1/8)": 12.5,
    "18.75% (3/16)": 18.75,
    "20% (1/5)": 20.0,
    "25% (1/4)": 25.0
}

use_custom = st.checkbox("Use custom royalty rate", value=False)

if use_custom:
    lease_royalty_percent = st.number_input("Enter custom royalty (%)", min_value=0.0, max_value=100.0, value=18.75)
else:
    selected_label = st.selectbox("Select Lease Royalty", list(common_royalties.keys()), index=1)
    lease_royalty_percent = common_royalties[selected_label]

royalty_decimal = lease_royalty_percent / 100
wi = 1 - royalty_decimal

# --- Mineral Owners ---
st.markdown("---")
st.subheader("➕ Mineral Owner Entries")

num_owners = st.number_input("How many mineral owners?", min_value=1, max_value=10, step=1, value=2)

owners = []
total_nri = 0
total_royalty_payment = 0

for i in range(int(num_owners)):
    st.markdown(f"### Owner {i + 1}")
    owner_name = st.text_input(f"Name of Owner {i + 1}", value=f"Owner {i + 1}", key=f"name_{i}")
    leased_acres = st.number_input(f"Leased Acres from {owner_name}", min_value=0.0, key=f"acres_{i}")

    mi = leased_acres / total_acres if total_acres > 0 else 0
    nri = mi * royalty_decimal
    royalty_payment = production_revenue * nri

    owners.append({
        "name": owner_name,
        "leased_acres": leased_acres,
        "mi": mi,
        "nri": nri,
        "royalty_payment": royalty_payment
    })

    total_nri += nri
    total_royalty_payment += royalty_payment

# --- Operator's Revenue and Profit ---
company_wi_revenue = production_revenue * wi
profit = company_wi_revenue - estimated_costs

# --- Output Summary ---
st.markdown("---")
st.subheader("📊 Results Summary")

st.write(f"💸 **Total Royalty Payments:** ${total_royalty_payment:,.2f}")
st.write(f"🏦 **Company's Working Interest Revenue (WI):** ${company_wi_revenue:,.2f}")
st.write(f"🛠️ **Estimated Costs:** ${estimated_costs:,.2f}")
st.write(f"✅ **Estimated Profit:** ${profit:,.2f}")

# --- Owner Breakdown ---
st.markdown("---")
st.subheader("📄 Mineral Owner Breakdown")

for owner in owners:
    st.markdown(f"**{owner['name']}**")
    st.write(f"- Leased Acres: {owner['leased_acres']}")
    st.write(f"- MI: {owner['mi'] * 100:.2f}%")
    st.write(f"- NRI: {owner['nri'] * 100:.4f}%")
    st.write(f"- Royalty Payment: ${owner['royalty_payment']:,.2f}")
    st.markdown("---")

# --- Notes ---
st.markdown("📘 _NRI = (Leased Acres / Total Acres) × Royalty %_  \n📘 _Total Royalty Payment = Sum of all owners' NRI × Revenue_")
# --- Export to CSV ---
st.markdown("### 📤 Export Owner Data")

# Create DataFrame
df = pd.DataFrame([
    {
        "Owner Name": owner['name'],
        "Leased Acres": owner['leased_acres'],
        "MI (%)": round(owner['mi'] * 100, 4),
        "NRI (%)": round(owner['nri'] * 100, 4),
        "Royalty Payment ($)": round(owner['royalty_payment'], 2)
    }
    for owner in owners
])

# Download button
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Download Owner Breakdown as CSV",
    data=csv,
    file_name='owner_breakdown.csv',
    mime='text/csv'
)
