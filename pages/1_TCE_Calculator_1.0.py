import streamlit as st
from distance_calculation import (
    get_route_options,
    get_distance,
    get_distance_for_route,
    get_route_ports
)
from voyage_calculations import (
    get_freight_revenue,
    calculate_round_voyage_expense,
    calculate_tce,
    format_days_to_text
)

st.set_page_config(page_title="TCE Calculation", layout="wide")
st.title("TCE Calculation")

route_options = get_route_options()
dropdown_options = ["Select route"] + list(route_options.keys())
route_keys = ["route1", "route2", "route3", "route4"]

FIXED_ASSUMPTIONS = {
    "laden_speed": 13.0,
    "ballast_speed": 12.5,
    "laden_fuel_tpd": 23.0,
    "ballast_fuel_tpd": 23.0,
    # "fuel_price": 800.0,
    # "port_fuel_price": 1200.0,
    "discharge_port_days": 2.25,
    "discharge_fuel_tpd": 17.0,
    "load_port_days": 2.25,
    "load_fuel_tpd": 7.0,
    # "port_cost": 95000.0,
    "tonnage": 35000
}

st.subheader("Voyage Assumptions")
st.markdown(
    f"""
    **Laden Speed:** {FIXED_ASSUMPTIONS['laden_speed']} kts |
    **Ballast Speed:** {FIXED_ASSUMPTIONS['ballast_speed']} kts |
    **Laden Fuel:** {FIXED_ASSUMPTIONS['laden_fuel_tpd']} tpd |
    **Ballast Fuel:** {FIXED_ASSUMPTIONS['ballast_fuel_tpd']} tpd |
    **Discharge Port Days:** {FIXED_ASSUMPTIONS['discharge_port_days']} |
    **Discharge Fuel:** {FIXED_ASSUMPTIONS['discharge_fuel_tpd']} tpd |
    **Load Port Days:** {FIXED_ASSUMPTIONS['load_port_days']} |
    **Load Fuel:** {FIXED_ASSUMPTIONS['load_fuel_tpd']} tpd |
    **Tonnage:** {FIXED_ASSUMPTIONS['tonnage']} tons
    """
)

tab1, tab2, tab3 = st.tabs(["Voyage Revenue", "Voyage Expenses", "Voyage TCE"])

# -------------------------------
# TAB 1: VOYAGE REVENUE
# -------------------------------
with tab1:
    st.header("Voyage Revenue")
    st.write("Select up to 4 routes and enter WorldScale.")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        route1 = st.selectbox("Route 1", dropdown_options, key="route1")
        ws1 = st.number_input("Worldscale", min_value=0.0, value=100.0, step=1.0, key="ws1")
        flat_rate1 = st.number_input("Flat Rate", min_value=0.0, value=20.0, step=0.5, key="flat1")

    with col2:
        route2 = st.selectbox("Route 2", dropdown_options, key="route2")
        ws2 = st.number_input("Worldscale", min_value=0.0, value=100.0, step=1.0, key="ws2")
        flat_rate2 = st.number_input("Flat Rate", min_value=0.0, value=20.0, step=0.5, key="flat2")

    with col3:
        route3 = st.selectbox("Route 3", dropdown_options, key="route3")
        ws3 = st.number_input("Worldscale", min_value=0.0, value=100.0, step=1.0, key="ws3")
        flat_rate3 = st.number_input("Flat Rate", min_value=0.0, value=20.0, step=0.5, key="flat3")

    with col4:
        route4 = st.selectbox("Route 4", dropdown_options, key="route4")
        ws4 = st.number_input("Worldscale", min_value=0.0, value=100.0, step=1.0, key="ws4")
        flat_rate4 = st.number_input("Flat Rate", min_value=0.0, value=20.0, step=0.5, key="flat4")
        use_lump_sum4 = st.checkbox("Use Lump Sum", key="use_lump_sum4")
        lump_sum4 = st.number_input("Lump Sum", min_value=0.0, value=0.0, step=10000.0, key="lump_sum4")

    selected_routes = [
        {
            "route": route1,
            "tonnage": FIXED_ASSUMPTIONS["tonnage"],
            "ws": ws1,
            "flat_rate": flat_rate1,
            "use_lump_sum": False,
            "lump_sum": 0.0,
        },
        {
            "route": route2,
            "tonnage": FIXED_ASSUMPTIONS["tonnage"],
            "ws": ws2,
            "flat_rate": flat_rate2,
            "use_lump_sum": False,
            "lump_sum": 0.0,
        },
        {
            "route": route3,
            "tonnage": FIXED_ASSUMPTIONS["tonnage"],
            "ws": ws3,
            "flat_rate": flat_rate3,
            "use_lump_sum": False,
            "lump_sum": 0.0,
        },
        {
            "route": route4,
            "tonnage": FIXED_ASSUMPTIONS["tonnage"],
            "ws": ws4,
            "flat_rate": flat_rate4,
            "use_lump_sum": use_lump_sum4,
            "lump_sum": lump_sum4,
        },
    ]   

    if st.button("Calculate Voyage Revenue"):
        result_cols = st.columns(4)

        for i, route_data in enumerate(selected_routes):
            with result_cols[i]:
                st.subheader(f"Route {i+1}")
                route_name = route_data["route"]

                if route_name == "Select route":
                    st.info("No route selected.")
                    continue

                try:
                    result = get_distance_for_route(route_name)

                    freight_revenue = get_freight_revenue(
                        route_data["use_lump_sum"],
                        route_data["lump_sum"],
                        route_data["tonnage"],
                        route_data["flat_rate"],
                        route_data["ws"]
                    )

                    st.write(f"**Load Port:** {result['departure']}")
                    st.write(f"**Discharge Port:** {result['arrival']}")
                    st.markdown(
                        f"""
                        <div style="font-size:16px; margin-top:10px;">
                            <strong>Freight Revenue:</strong> ${freight_revenue:,.2f}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                except Exception as e:
                    st.exception(e)

# -------------------------------
# TAB 2: VOYAGE EXPENSES
# -------------------------------
with tab2:
    st.header("Voyage Expenses")
    st.write("This tab calculates voyage fuel costs and port fuel costs.")

    expense_inputs_col1, expense_inputs_col2, expense_inputs_col3, expense_inputs_col4 = st.columns(4)

    for i, col in enumerate([expense_inputs_col1, expense_inputs_col2, expense_inputs_col3, expense_inputs_col4]):
        with col:
            route_name = st.session_state.get(route_keys[i], "Select route")
            st.subheader(f"Route {i+1}")
            st.write(f"**Selected Route:** {route_name}")

            st.number_input("Fuel Price ($/ton)", min_value=0.0, value=800.0, step=10.0, key=f"fuel_price_{i+1}")
            st.number_input("Port Fuel Price ($/ton)", min_value=0.0, value=1200.0, step=10.0, key=f"port_fuel_price_{i+1}")
            st.number_input("Port Cost", min_value=0.0, value=80000.0, step=10000.0, key=f"port_cost_{i+1}")

    if st.button("Calculate Voyage Expenses"):
        result_cols = st.columns(4)

        for i, col in enumerate(result_cols):
            with col:
                route_name = st.session_state.get(route_keys[i], "Select route")
                st.subheader(f"Route {i+1}")

                if route_name == "Select route":
                    st.info("No route selected.")
                    continue

                try:
                    load_port, discharge_port = get_route_ports(route_name)

                    laden_distance_nm = get_distance(load_port, discharge_port)
                    ballast_distance_nm = get_distance(discharge_port, load_port)

                    fuel_price = st.session_state.get(f"fuel_price_{i+1}", 800.0)
                    port_fuel_price = st.session_state.get(f"port_fuel_price_{i+1}", 1200.0)
                    port_cost = st.session_state.get(f"port_cost_{i+1}", 80000)

                    laden_speed = FIXED_ASSUMPTIONS["laden_speed"]
                    ballast_speed = FIXED_ASSUMPTIONS["ballast_speed"]
                    laden_fuel_tpd = FIXED_ASSUMPTIONS["laden_fuel_tpd"]
                    ballast_fuel_tpd = FIXED_ASSUMPTIONS["ballast_fuel_tpd"]
                    discharge_port_days = FIXED_ASSUMPTIONS["discharge_port_days"]
                    discharge_fuel_tpd = FIXED_ASSUMPTIONS["discharge_fuel_tpd"]
                    load_port_days = FIXED_ASSUMPTIONS["load_port_days"]
                    load_fuel_tpd = FIXED_ASSUMPTIONS["load_fuel_tpd"]

                    expense_result = calculate_round_voyage_expense(
                        laden_distance_nm,
                        ballast_distance_nm,
                        laden_speed,
                        ballast_speed,
                        laden_fuel_tpd,
                        ballast_fuel_tpd,
                        fuel_price,
                        discharge_port_days,
                        discharge_fuel_tpd,
                        load_port_days,
                        load_fuel_tpd,
                        port_fuel_price,
                        port_cost
                    )

                    st.write(f"**Route:** {load_port} → {discharge_port}")
                    st.markdown(
                        f"""
                        <div style="font-size:16px; margin-top:10px;">
                            <strong>Voyage Fuel Cost:</strong> ${expense_result['voyage_fuel_cost']:,.2f}
                        </div>
                        <div style="font-size:16px; margin-top:6px;">
                            <strong>Port Fuel Cost:</strong> ${expense_result['port_fuel_cost']:,.2f}
                        </div>
                        <div style="font-size:16px; margin-top:6px;">
                            <strong>Port Cost:</strong> ${expense_result['port_cost']:,.2f}
                        </div>
                        <div style="font-size:16px; margin-top:6px;">
                            <strong>Total Expense:</strong> ${expense_result['total_expense']:,.2f}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.exception(e)

# -------------------------------
# TAB 3: VOYAGE TCE
# -------------------------------
with tab3:
    st.header("Voyage TCE")
    st.write("TCE = (Revenue - Expenses) / Total Days")

    if st.button("Calculate Voyage TCE"):
        result_cols = st.columns(4)

        for i, col in enumerate(result_cols):
            with col:
                route_name = st.session_state.get(route_keys[i], "Select route")
                st.subheader(f"Route {i+1}")
                st.write(f"**Selected Route:** {route_name}")

                if route_name == "Select route":
                    st.info("No route selected.")
                    continue

                try:
                    load_port, discharge_port = get_route_ports(route_name)

                    laden_distance_nm = get_distance(load_port, discharge_port)
                    ballast_distance_nm = get_distance(discharge_port, load_port)

                    fuel_price = st.session_state.get(f"fuel_price_{i+1}", 800.0)
                    port_fuel_price = st.session_state.get(f"port_fuel_price_{i+1}", 1200.0)
                    port_cost = st.session_state.get(f"port_cost_{i+1}", 80000)

                    laden_speed = FIXED_ASSUMPTIONS["laden_speed"]
                    ballast_speed = FIXED_ASSUMPTIONS["ballast_speed"]
                    laden_fuel_tpd = FIXED_ASSUMPTIONS["laden_fuel_tpd"]
                    ballast_fuel_tpd = FIXED_ASSUMPTIONS["ballast_fuel_tpd"]
                    discharge_port_days = FIXED_ASSUMPTIONS["discharge_port_days"]
                    discharge_fuel_tpd = FIXED_ASSUMPTIONS["discharge_fuel_tpd"]
                    load_port_days = FIXED_ASSUMPTIONS["load_port_days"]
                    load_fuel_tpd = FIXED_ASSUMPTIONS["load_fuel_tpd"]

                    tonnage = FIXED_ASSUMPTIONS["tonnage"]
                    ws = st.session_state.get(f"ws{i+1}", 100.0)
                    flat_rate = st.session_state.get(f"flat{i+1}", 20.0)
                    use_lump_sum = st.session_state.get(f"use_lump_sum{i+1}", False)
                    lump_sum = st.session_state.get(f"lump_sum{i+1}", 0.0)

                    revenue = get_freight_revenue(
                        use_lump_sum,
                        lump_sum,
                        tonnage,
                        flat_rate,
                        ws
                    )

                    expense_result = calculate_round_voyage_expense(
                        laden_distance_nm,
                        ballast_distance_nm,
                        laden_speed,
                        ballast_speed,
                        laden_fuel_tpd,
                        ballast_fuel_tpd,
                        fuel_price,
                        discharge_port_days,
                        discharge_fuel_tpd,
                        load_port_days,
                        load_fuel_tpd,
                        port_fuel_price,
                        port_cost
                    )

                    tce_value = calculate_tce(
                        revenue,
                        expense_result["total_expense"],
                        expense_result["total_days"]
                    )

                    total_voyage_duration_text = format_days_to_text(expense_result["total_sailing_days"])

                    if "comparison_tce_routes" not in st.session_state:
                        st.session_state["comparison_tce_routes"] = {}

                    st.session_state["comparison_tce_routes"][route_name] = {
                        "tce": tce_value,
                        "route_name": route_name,
                        "route_display": f"{load_port} → {discharge_port}",
                        "revenue": revenue,
                        "expenses": expense_result["total_expense"],
                        "voyage_fuel_cost": expense_result["voyage_fuel_cost"],
                        "port_fuel_cost": expense_result["port_fuel_cost"],
                        "port_cost": expense_result["port_cost"],
                        "total_days": expense_result["total_days"],
                        "total_port_days": expense_result["total_port_days"],
                        "total_voyage_distance": expense_result["total_voyage_distance"],
                        "total_voyage_duration_text": total_voyage_duration_text,
                    }

                    st.write(f"**Route:** {load_port} → {discharge_port}")
                    st.markdown(
                        f"""
                        <div style="font-size:16px; margin-top:10px;">
                            <strong>Total Voyage Distance:</strong> {expense_result['total_voyage_distance']:,.0f} nm
                        </div>
                        <div style="font-size:16px; margin-top:6px;">
                            <strong>Total Voyage Duration:</strong> {total_voyage_duration_text}
                        </div>
                        <div style="font-size:16px; margin-top:6px;">
                            <strong>Total Port Days:</strong> {expense_result['total_port_days']:,.2f}
                        </div>
                        <div style="font-size:16px; margin-top:6px;">
                            <strong>Total Days:</strong> {expense_result['total_days']:,.2f}
                        </div>
                        <div style="font-size:16px; margin-top:6px;">
                            <strong>Revenue:</strong> ${revenue:,.2f}
                        </div>
                        <div style="font-size:16px; margin-top:6px;">
                            <strong>Expenses:</strong> ${expense_result['total_expense']:,.2f}
                        </div>
                        <div style="font-size:16px; margin-top:6px;">
                            <strong>TCE:</strong> ${tce_value:,.2f}/day
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                except Exception as e:
                    st.exception(e)