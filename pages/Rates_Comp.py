import streamlit as st
from distance_calculation import get_distance
from voyage_calculations import calculate_sailing_days

st.set_page_config(page_title="Rates Comparison", layout="wide")
st.title("Rates Comparison")
st.write(
    "Each tab below represents the open port. Click through the tabs to see the different open ports and corresponding voyage options for comparison."
)

FIXED_RATE_ASSUMPTIONS = {
    "ballast_speed": 13.0,
    "ballast_fuel_tpd": 23.0,
    "fuel_price": 800.0,
    "laden_speed": 12.5,
    "laden_fuel_tpd": 23.0,
    "load_port_days": 2.25,
    "load_port_fuel_tpd": 7.0,
    "discharge_port_days": 2.25,
    "discharge_port_fuel_tpd": 17.0,
    "port_fuel_price": 1200.0,
    "port_cost": 63000.0,
    "comparison_speed": 13.0,
    "comparison_fuel_tpd": 23.0,
    "comparison_fuel_price": 800.0,
    "tonnage": 35000
}

st.subheader("Voyage Assumptions")
st.markdown(
    f"""
    **Laden Speed:** {FIXED_RATE_ASSUMPTIONS['laden_speed']} kts |
    **Ballast Speed:** {FIXED_RATE_ASSUMPTIONS['ballast_speed']} kts |
    **Laden Fuel:** {FIXED_RATE_ASSUMPTIONS['laden_fuel_tpd']} tpd |
    **Ballast Fuel:** {FIXED_RATE_ASSUMPTIONS['ballast_fuel_tpd']} tpd |
    **Discharge Port Days:** {FIXED_RATE_ASSUMPTIONS['discharge_port_days']} |
    **Discharge Fuel:** {FIXED_RATE_ASSUMPTIONS['discharge_port_fuel_tpd']} tpd |
    **Load Port Days:** {FIXED_RATE_ASSUMPTIONS['load_port_days']} |
    **Load Fuel:** {FIXED_RATE_ASSUMPTIONS['load_port_fuel_tpd']} tpd |
    **Bunker Price:** {FIXED_RATE_ASSUMPTIONS['fuel_price']} |
    **Tonnage:** {FIXED_RATE_ASSUMPTIONS['tonnage']}
    """
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Kwinana", "Botany Bay", "Sikka", "Dar es Salaam", "Durban"])


def render_rate_comparison_tab(
    open_port_label,
    comparison_match_terms,
    comparison_route_default_name,
    comparison_expense_to_port,
    alt_ballast_options,
    alt_laden_options,
    key_prefix
):
    comparison_routes = st.session_state.get("comparison_tce_routes", {})
    comparison_data = None
    comparison_route_name = comparison_route_default_name

    for route_key, route_value in comparison_routes.items():
        if all(term in route_key for term in comparison_match_terms):
            comparison_data = route_value
            comparison_route_name = route_key
            break

    st.subheader("Open Port Route")
    st.write(f"**Route Name:** {comparison_route_name}")

    comparison_tce = comparison_data["tce"] if comparison_data is not None else None

    if comparison_tce is not None:
        st.write(f"**Open Port Route TCE:** ${comparison_tce:,.2f}/day")
    else:
        st.info("Open Port Route TCE not yet available from the Voyage TCE page.") 

    st.subheader("Alternative Voyage Option")

    with st.expander("Alternative Route Inputs", expanded=True):
        ports_col1, ports_col2 = st.columns(2)
        with ports_col1:
            ballast_port = st.selectbox(
                "Port Ballasting To",
                ["Select"] + alt_ballast_options,
                key=f"{key_prefix}_ballast_port"
            )
        with ports_col2:
            laden_port = st.selectbox(
                "Port Ladening To",
                ["Select"] + alt_laden_options,
                key=f"{key_prefix}_laden_port"
            )

        revenue_col1, revenue_col2 = st.columns(2)
        with revenue_col1:
            ws_rate = st.number_input(
                "WS Rate",
                min_value=0.0,
                value=100.0,
                step=1.0,
                key=f"{key_prefix}_ws_rate"
            )
        with revenue_col2:
            flat_rate = st.number_input(
                "Flat Rate",
                min_value=0.0,
                value=20.0,
                step=0.5,
                key=f"{key_prefix}_flat_rate"
            )

    if st.button("Run Route Economics", key=f"{key_prefix}_route_economics"):
        try:
            if ballast_port == "Select" or laden_port == "Select":
                raise ValueError("Please select both ballast and laden ports.")

            ballast_speed = FIXED_RATE_ASSUMPTIONS["ballast_speed"]
            ballast_fuel_tpd = FIXED_RATE_ASSUMPTIONS["ballast_fuel_tpd"]
            fuel_price = FIXED_RATE_ASSUMPTIONS["fuel_price"]

            laden_speed = FIXED_RATE_ASSUMPTIONS["laden_speed"]
            laden_fuel_tpd = FIXED_RATE_ASSUMPTIONS["laden_fuel_tpd"]

            load_port_days = FIXED_RATE_ASSUMPTIONS["load_port_days"]
            load_port_fuel_tpd = FIXED_RATE_ASSUMPTIONS["load_port_fuel_tpd"]

            discharge_port_days = FIXED_RATE_ASSUMPTIONS["discharge_port_days"]
            discharge_port_fuel_tpd = FIXED_RATE_ASSUMPTIONS["discharge_port_fuel_tpd"]

            port_fuel_price = FIXED_RATE_ASSUMPTIONS["port_fuel_price"]
            port_cost = FIXED_RATE_ASSUMPTIONS["port_cost"]

            ballast_distance_nm = get_distance(open_port_label, ballast_port)
            laden_distance_nm = get_distance(ballast_port, laden_port)

            ballast_days = calculate_sailing_days(ballast_distance_nm, ballast_speed)
            laden_days = calculate_sailing_days(laden_distance_nm, laden_speed)

            ballast_bunker_cost = ballast_days * ballast_fuel_tpd * fuel_price
            laden_bunker_cost = laden_days * laden_fuel_tpd * fuel_price

            load_port_fuel_cost = load_port_days * load_port_fuel_tpd * port_fuel_price
            discharge_port_fuel_cost = discharge_port_days * discharge_port_fuel_tpd * port_fuel_price

            revenue = FIXED_RATE_ASSUMPTIONS['tonnage'] * flat_rate * (ws_rate / 100)

            total_sailing_days = ballast_days + laden_days
            total_port_days = load_port_days + discharge_port_days
            total_days = total_sailing_days + total_port_days

            total_expenses = (
                ballast_bunker_cost
                + laden_bunker_cost
                + load_port_fuel_cost
                + discharge_port_fuel_cost
                + port_cost
            )

            alternative_tce = (revenue - total_expenses) / total_days if total_days > 0 else 0.0

            st.session_state[f"{key_prefix}_route_result"] = {
                "comparison_route_name": comparison_route_name,
                "comparison_tce": comparison_tce,
                "ballast_port": ballast_port,
                "laden_port": laden_port,
                "ballast_distance_nm": ballast_distance_nm,
                "laden_distance_nm": laden_distance_nm,
                "revenue": revenue,
                "total_expenses": total_expenses,
                "total_days": total_days,
                "total_sailing_days": total_sailing_days,
                "total_port_days": total_port_days,
                "ballast_days": ballast_days,
                "laden_days": laden_days,
                "load_port_days": load_port_days,
                "discharge_port_days": discharge_port_days,
                "ballast_bunker_cost": ballast_bunker_cost,
                "laden_bunker_cost": laden_bunker_cost,
                "voyage_fuel_cost": ballast_bunker_cost + laden_bunker_cost,
                "load_port_fuel_cost": load_port_fuel_cost,
                "discharge_port_fuel_cost": discharge_port_fuel_cost,
                "alternative_tce": alternative_tce,
            }

            st.session_state.pop(f"{key_prefix}_route_error", None)

        except Exception as e:
            st.session_state[f"{key_prefix}_route_error"] = str(e)

    if f"{key_prefix}_route_error" in st.session_state:
        st.error(st.session_state[f"{key_prefix}_route_error"])

    route_result = st.session_state.get(f"{key_prefix}_route_result")

    if route_result is not None:
        required_keys = [
            "total_expenses",
            "total_days",
            "total_sailing_days",
            "total_port_days",
            "ballast_days",
            "laden_days",
            "load_port_days",
            "discharge_port_days",
            "alternative_tce",
            "voyage_fuel_cost",
            "load_port_fuel_cost",
            "discharge_port_fuel_cost",
        ]

        if not all(key in route_result for key in required_keys):
            st.session_state.pop(f"{key_prefix}_route_result", None)
            route_result = None

    if route_result is not None:
        st.subheader(f"{open_port_label} Comparison Output")
        st.write(f"**Open Port Route:** {route_result['comparison_route_name']}")

        if route_result["comparison_tce"] is not None:
            st.write(f"**Open Port Route TCE:** ${route_result['comparison_tce']:,.2f}/day")
        else:
            st.info("Open Port Route TCE not yet available from the Voyage TCE page.")

        tce_spread = None
        if route_result.get("comparison_tce") is not None:
            tce_spread = route_result["alternative_tce"] - route_result["comparison_tce"]

        st.write(f"**Alternative Route:** {route_result['ballast_port']} → {route_result['laden_port']}")
        st.write(f"**Alternative Route Revenue:** ${route_result['revenue']:,.2f}")
        st.write(f"**Alternative Route Expenses:** ${route_result['total_expenses']:,.2f}")
        st.write(f"**Alternative Route Total Days:** {route_result['total_days']:,.2f}")
        st.write(f"**Sailing Days:** {route_result['total_sailing_days']:,.2f}")
        st.write(f"**Port Days:** {route_result['total_port_days']:,.2f}")
        st.write(f"**Laden Days:** {route_result['laden_days']:,.2f}")
        st.write(f"**Ballast Days:** {route_result['ballast_days']:,.2f}")
        st.write(f"**Load Port Days:** {route_result['load_port_days']:,.2f}")
        st.write(f"**Discharge Port Days:** {route_result['discharge_port_days']:,.2f}")
        st.write(f"**Alternative Route TCE:** ${route_result['alternative_tce']:,.2f}/day")
        st.write(f"**Voyage Fuel Costs:** ${route_result['voyage_fuel_cost']:,.2f}")
        st.write(f"**Discharge Fuel Costs:** ${route_result['discharge_port_fuel_cost']:,.2f}")
        st.write(f"**Load Fuel Costs:** ${route_result['load_port_fuel_cost']:,.2f}")

        if tce_spread is not None:
            st.write(f"**TCE Spread (Alternative - Open Port Route):** ${tce_spread:,.2f}/day")
        else:
            st.write("**TCE Spread (Alternative - Open Port Route):** N/A")


with tab1:
    st.header("Kwinana")
    render_rate_comparison_tab(
        open_port_label="Kwinana (Refinery)",
        comparison_match_terms=["Singapore", "Kwinana"],
        comparison_route_default_name="TC7 Singapore → Kwinana (Refinery)",
        comparison_expense_to_port="Singapore",
        alt_ballast_options=["Sikka"],
        alt_laden_options=["Dar-es-Salaam"],
        key_prefix="kwinana"
    )

with tab2:
    st.header("Botany Bay")
    render_rate_comparison_tab(
        open_port_label="Botany Bay",
        comparison_match_terms=["Ulsan", "Botany"],
        comparison_route_default_name="TC22 Ulsan → Botany Bay",
        comparison_expense_to_port="Ulsan",
        alt_ballast_options=["Singapore"],
        alt_laden_options=["Ulsan"],
        key_prefix="botany"
    )

with tab3:
    st.header("Sikka")
    render_rate_comparison_tab(
        open_port_label="Sikka",
        comparison_match_terms=["Sikka", "Dar-es-Salaam"],
        comparison_route_default_name="TC17 Sikka → Dar-es-Salaam",
        comparison_expense_to_port="Dar-es-Salaam",
        alt_ballast_options=["Singapore"],
        alt_laden_options=["Kwinana (Refinery)"],
        key_prefix="sikka"
    )

with tab4:
    st.header("Dar es Salaam")
    render_rate_comparison_tab(
        open_port_label="Dar-es-Salaam",
        comparison_match_terms=["Sikka", "Dar-es-Salaam"],
        comparison_route_default_name="TC17 Sikka → Dar-es-Salaam",
        comparison_expense_to_port="Sikka",
        alt_ballast_options=["Singapore"],
        alt_laden_options=["Kwinana (Refinery)"],
        key_prefix="dar"
    )

with tab5:
    st.header("Durban")
    render_rate_comparison_tab(
        open_port_label="Durban",
        comparison_match_terms=["Sikka", "Dar-es-Salaam"],
        comparison_route_default_name="TC17 Sikka → Dar-es-Salaam",
        comparison_expense_to_port="Sikka",
        alt_ballast_options=["Houston"],
        alt_laden_options=["Amsterdam"],
        key_prefix="durban"
    )