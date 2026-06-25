import streamlit as st
from distance_calculation import get_distance
from voyage_calculations import calculate_sailing_days
from flat_rates import get_flat_rate
from port_fees import get_port_fee

def get_eca_reference_distance(port_name):
    if port_name == "Houston":
        return get_distance("Miami", "Houston")
    elif port_name == "Rotterdam":
        return get_distance("Falmouth, U.K.", "Rotterdam")
    elif port_name == "New York":
        return get_distance("Holyrood", "New York")
    return 0.0

def get_tonnage(ballast_port):
    if ballast_port in ["Houston", "Rotterdam"]:
        return 38000.0
    return 35000.0

st.set_page_config(page_title="TCE Calculator", layout="wide")
st.title("TCE Calculator")

st.write("This TCE Calculator lets you select a port opening in, a port ballasting to, and a port ladening to. You can also save calculations to make comparisons.")
st.write("Link to check bunker prices: https://minerva-fuel-prices.prd.mercuria.systems/")
st.write("Link to check flat rates: https://www.worldscale.co.uk/")
st.write("Link to check port costs: https://www.portlog.com/")
st.write("Link to check port distances: https://ptp.atobviac.com/")

PORT_OPTIONS = [
    "Botany Bay",
    "Dar-es-Salaam",
    "Durban",
    "Houston",
    "Jubail - Commercial Port",
    "Kwinana (Refinery)",
    "Luanda",
    "New York",
    "Rotterdam",
    "Singapore",
    "Sikka",
    "Ulsan",
]

# Fixed assumptions
FIXED_ASSUMPTIONS = {
    "ballast_speed": 12.5,
    "ballast_fuel_tpd": 17.0,
    "laden_speed": 13.0,
    "laden_fuel_tpd": 23.0,
    "port_days": 4.5,
    "load_port_fuel_tpd": 7.0,
    "discharge_port_fuel_tpd": 12.0,
    "commission": 0.0375,
    "co2_emission_factor": 3.2,
    "carbon_price": 100.0,
    "eu_fee_pct": 0.5
}

st.subheader("Voyage Assumptions")
st.markdown(
    f"""
    **Laden Speed:** {FIXED_ASSUMPTIONS['laden_speed']} kts |
    **Ballast Speed:** {FIXED_ASSUMPTIONS['ballast_speed']} kts |
    **Laden Fuel Consumption:** {FIXED_ASSUMPTIONS['laden_fuel_tpd']} tpd |
    **Ballast Fuel Consumption:** {FIXED_ASSUMPTIONS['ballast_fuel_tpd']} tpd |
    **Port Days:** {FIXED_ASSUMPTIONS['port_days']} |
    **Discharge Fuel Consumption:** {FIXED_ASSUMPTIONS['discharge_port_fuel_tpd']} tpd |
    **Load Fuel Consumption:** {FIXED_ASSUMPTIONS['load_port_fuel_tpd']} tpd |
    **Commission:** {FIXED_ASSUMPTIONS['commission']} |
    **CO2 Emission Factor:** {FIXED_ASSUMPTIONS['co2_emission_factor']} |
    **Carbon Price:** ${FIXED_ASSUMPTIONS['carbon_price']} |
    **EU Fee %:** {FIXED_ASSUMPTIONS['eu_fee_pct']}
    """
)

if "saved_tce_results" not in st.session_state:
    st.session_state["saved_tce_results"] = []

if "use_auto_wait_days" not in st.session_state:
    st.session_state["use_auto_wait_days"] = True

if "wait_days" not in st.session_state:
    st.session_state["wait_days"] = 0.0

st.subheader("Voyage Inputs")

col1, col2, col3 = st.columns(3)
with col1:
    open_port = st.selectbox(
        "Open Port",
        ["Select"] + PORT_OPTIONS,
        key="single_open_port"
    )

with col2:
    ballast_port = st.selectbox(
        "Port Ballasting To",
        ["Select"] + PORT_OPTIONS,
        key="single_ballast_port"
    )

with col3:
    laden_port = st.selectbox(
        "Port Ladening To",
        ["Select"] + PORT_OPTIONS,
        key="single_laden_port"
    )

rev1, rev2, rev3 = st.columns(3)
with rev1:
    tons = get_tonnage(ballast_port) if ballast_port != "Select" else 0.0
    tonnage = st.number_input("Tonnage", min_value=0.0, value = tons)
with rev2:
    ws_rate = st.number_input("WS Rate", min_value=0.0, value=100.0, step=1.0)
with rev3:
    rate = get_flat_rate(ballast_port, laden_port)
    flat_rate = st.number_input("Flat Rate", value = rate)

if st.session_state.get("use_auto_wait_days", True):
    if open_port != "Select" and ballast_port != "Select":
        try:
            auto_ballast_distance_nm = get_distance(open_port, ballast_port)
            auto_ballast_days = calculate_sailing_days(
                auto_ballast_distance_nm,
                FIXED_ASSUMPTIONS["ballast_speed"]
            )

            if ballast_port == "Singapore" and auto_ballast_days < 14:
                st.session_state["wait_days"] = 14 - auto_ballast_days
            else:
                st.session_state["wait_days"] = 0.0

        except Exception:
            st.session_state["wait_days"] = 0.0
    else:
        st.session_state["wait_days"] = 0.0

exp1, exp2, exp3, exp4, exp5 = st.columns(5)
with exp1:
    ballast_port_cost = st.number_input("Ballast Port Cost", min_value = 0.0, value = get_port_fee(ballast_port), step = 1000.0)
with exp2:
    laden_port_cost = st.number_input("Laden Port Cost", min_value = 0.0, value = get_port_fee(laden_port), step = 1000.0)
with exp3:
    bunker_cost = st.number_input("VLSFO Cost", min_value = 0.0, value = 850.0, step = 100.0)
with exp4:
    port_bunker_cost = st.number_input(" MGO Cost", min_value = 0.0, value = 1500.0, step = 100.0)
with exp5:
    wait_days = st.number_input("Wait Days", min_value=0.0, step=0.01, key="wait_days", disabled=st.session_state.get("use_auto_wait_days", True))
    st.checkbox("Use Auto Wait Days", key="use_auto_wait_days")
bunker_spread = port_bunker_cost - bunker_cost


if st.button("Calculate TCE"):
    try:
        if open_port == "Select" or ballast_port == "Select" or laden_port == "Select":
            raise ValueError("Please select Open Port, Ballast Port, and Laden Port.")

        ballast_distance_nm = get_distance(open_port, ballast_port)
        laden_distance_nm = get_distance(ballast_port, laden_port)

        ballast_days = calculate_sailing_days(ballast_distance_nm, FIXED_ASSUMPTIONS["ballast_speed"])
        laden_days = calculate_sailing_days(laden_distance_nm, FIXED_ASSUMPTIONS["laden_speed"])

        ballast_emissions_cost = 0.0
        laden_emissions_cost = 0.0

        # If laden port is Rotterdam: 50% fee on ballast + laden legs
        if ballast_port == "Rotterdam":
            ballast_emissions_cost = (
                ballast_days
                * FIXED_ASSUMPTIONS["ballast_fuel_tpd"]
                * FIXED_ASSUMPTIONS["co2_emission_factor"]
                * FIXED_ASSUMPTIONS["carbon_price"]
                * FIXED_ASSUMPTIONS["eu_fee_pct"]
            )

            laden_emissions_cost = (
                laden_days
                * FIXED_ASSUMPTIONS["laden_fuel_tpd"]
                * FIXED_ASSUMPTIONS["co2_emission_factor"]
                * FIXED_ASSUMPTIONS["carbon_price"]
                * FIXED_ASSUMPTIONS["eu_fee_pct"]
            )

        # If ballast port is Rotterdam: 50% fee on laden leg only
        elif laden_port == "Rotterdam":
            laden_emissions_cost = (
                laden_days
                * FIXED_ASSUMPTIONS["laden_fuel_tpd"]
                * FIXED_ASSUMPTIONS["co2_emission_factor"]
                * FIXED_ASSUMPTIONS["carbon_price"]
                * FIXED_ASSUMPTIONS["eu_fee_pct"]
            )

        emissions_cost = ballast_emissions_cost + laden_emissions_cost

        ballast_bunker_cost = ballast_days * FIXED_ASSUMPTIONS["ballast_fuel_tpd"] * bunker_cost
        laden_bunker_cost = laden_days * FIXED_ASSUMPTIONS["laden_fuel_tpd"] * bunker_cost

        ballast_eca_distance_nm = 0.0
        laden_eca_distance_nm = 0.0
        ballast_eca_days = 0.0
        laden_eca_days = 0.0

        if ballast_port == "Houston":
            ballast_eca_distance_nm = get_eca_reference_distance("Houston") * 1.5
            ballast_eca_days = calculate_sailing_days(ballast_eca_distance_nm, FIXED_ASSUMPTIONS["ballast_speed"])
        elif ballast_port == "Rotterdam":
            ballast_eca_distance_nm = get_eca_reference_distance("Rotterdam") * 2
            ballast_eca_days = calculate_sailing_days(ballast_eca_distance_nm, FIXED_ASSUMPTIONS["ballast_speed"])
        elif ballast_port == "New York":
            ballast_eca_distance_nm = get_eca_reference_distance("New York")
            ballast_eca_days = calculate_sailing_days(ballast_eca_distance_nm, FIXED_ASSUMPTIONS["ballast_speed"])

        if laden_port == "Houston":
            laden_eca_distance_nm = get_eca_reference_distance("Houston")
            laden_eca_days = calculate_sailing_days(laden_eca_distance_nm, FIXED_ASSUMPTIONS["laden_speed"])
        elif laden_port == "Rotterdam":
            laden_eca_distance_nm = get_eca_reference_distance("Rotterdam")
            laden_eca_days = calculate_sailing_days(laden_eca_distance_nm, FIXED_ASSUMPTIONS["laden_speed"])
        elif laden_port == "New York":
            laden_eca_distance_nm = get_eca_reference_distance("New York")
            laden_eca_days = calculate_sailing_days(laden_eca_distance_nm, FIXED_ASSUMPTIONS["laden_speed"])

        ballast_eca_premium = ballast_eca_days * FIXED_ASSUMPTIONS['ballast_fuel_tpd'] * bunker_spread
        laden_eca_premium = laden_eca_days * FIXED_ASSUMPTIONS['laden_fuel_tpd'] * bunker_spread
        eca_premium = ballast_eca_premium + laden_eca_premium


        load_port_fuel_cost = (
            FIXED_ASSUMPTIONS["port_days"] / 2
            * FIXED_ASSUMPTIONS["load_port_fuel_tpd"]
            * port_bunker_cost
        )

        discharge_port_fuel_cost = (
            FIXED_ASSUMPTIONS["port_days"] /2
            * FIXED_ASSUMPTIONS["discharge_port_fuel_tpd"]
            * port_bunker_cost
        )

        revenue = tonnage * flat_rate * (ws_rate / 100)

        commission_costs = FIXED_ASSUMPTIONS['commission'] * revenue

        net_income = revenue - commission_costs

        total_sailing_days = ballast_days + laden_days

        wait_days = st.session_state.get("wait_days", 0.0)

        total_days = total_sailing_days + FIXED_ASSUMPTIONS["port_days"] + wait_days

        voyage_fuel_cost = ballast_bunker_cost + laden_bunker_cost
        port_fuel_cost = load_port_fuel_cost + discharge_port_fuel_cost

        bunker_costs = voyage_fuel_cost + port_fuel_cost + eca_premium

        port_costs = ballast_port_cost + laden_port_cost

        total_expenses = (
            bunker_costs
            + port_costs
            + emissions_cost
        )

        tce = (net_income - total_expenses) / total_days if total_days > 0 else 0.0

        result = {
            "open_port": open_port,
            "ballast_port": ballast_port,
            "laden_port": laden_port,
            "ballast_distance_nm": ballast_distance_nm,
            "laden_distance_nm": laden_distance_nm,
            "ballast_days": ballast_days,
            "laden_days": laden_days,
            "total_sailing_days": total_sailing_days,
            "port_days": FIXED_ASSUMPTIONS["port_days"],
            "total_days": total_days,
            "revenue": revenue,
            "net_income": net_income,
            "bunker_costs": bunker_costs,
            "port_costs": port_costs,
            "ballast_eca_days": ballast_eca_days,
            "laden_eca_days": laden_eca_days,
            "ballast_eca_premium": ballast_eca_premium,
            "laden_eca_premium": laden_eca_premium,
            "eca_premium": eca_premium,
            "total_expenses": total_expenses,
            "tce": tce,
            "ballast_emissions_cost": ballast_emissions_cost,
            "laden_emissions_cost": laden_emissions_cost,
            "emissions_cost": emissions_cost,
            "wait_days": wait_days
        }

        st.session_state["saved_tce_results"].append(result)

    except Exception as e:
        st.exception(e)

if st.button("Clear Saved Calculations"):
    st.session_state["saved_tce_results"] = []

st.subheader("Saved TCE Calculations")

saved_results = st.session_state.get("saved_tce_results", [])

if not saved_results:
    st.info("No saved calculations yet.")
else:
    result_cols = st.columns(min(len(saved_results), 3))

    for idx, result in enumerate(saved_results):
        col = result_cols[idx % len(result_cols)]
        with col:
            wait_days_style = ""
            if result.get("wait_days", 0) > 5:
                wait_days_style = "color:red; font-weight:bold;"
            st.markdown(
                f"""
                <div style="padding:12px; border:1px solid #ddd; border-radius:8px; margin-bottom:12px;">
                    <div>Open Port: {result['open_port']}</div>
                    <div>Ballast Port: {result['ballast_port']}</div>
                    <div>Laden Port: {result['laden_port']}</div>
                    <div>Sailing Days: {result['total_sailing_days']:,.2f}</div>
                    <div>Ballast ECA Days: {result['ballast_eca_days']:,.2f}</div>
                    <div>Laden ECA Days: {result['laden_eca_days']:,.2f}</div>
                    <div style="{wait_days_style}">Wait Days: {result['wait_days']:,.2f}</div>
                    <div><strong><u>Total Days: {result['total_days']:,.2f}</u></strong></div>
                    <div>Revenue: ${result['revenue']:,.2f}</div>
                    <div><strong><u>Net Income: ${result['net_income']:,.2f}</u></strong></div>
                    <div>Bunker Costs: ${result['bunker_costs']:,.2f}</div>
                    <div>Port Costs: ${result['port_costs']:,.2f}</div>
                    <div>Ballast ECA Premium: ${result['ballast_eca_premium']:,.2f}</div>
                    <div>Laden ECA Premium: ${result['laden_eca_premium']:,.2f}</div>
                    <div>ECA Premium: ${result['eca_premium']:,.2f}</div>
                    <div>Ballast Emissions Cost: ${result['ballast_emissions_cost']:,.2f}</div>
                    <div>Laden Emissions Cost: ${result['laden_emissions_cost']:,.2f}</div>
                    <div>Emissions Cost: ${result['emissions_cost']:,.2f}</div>
                    <div><strong><u>Total Expenses: ${result['total_expenses']:,.2f}</u></strong></div>
                    <div><strong><u>TCE: ${result['tce']:,.2f}/day</u></strong></div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Delete This Result", key=f"delete_saved_tce_{idx}"):
                st.session_state["saved_tce_results"].pop(idx)
                st.rerun()