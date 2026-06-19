def format_sailing_time(distance_nm, speed_knots):
    if speed_knots <= 0:
        raise ValueError("Speed must be greater than zero.")

    total_hours = distance_nm / speed_knots

    days = int(total_hours // 24)
    hours = int(round(total_hours % 24))

    if hours == 24:
        days += 1
        hours = 0

    day_label = "day" if days == 1 else "days"
    hour_label = "hour" if hours == 1 else "hours"

    return f"{days} {day_label} {hours} {hour_label}"


def format_days_to_text(days_value):
    total_hours = days_value * 24
    days = int(total_hours // 24)
    hours = int(round(total_hours % 24))

    if hours == 24:
        days += 1
        hours = 0

    day_label = "day" if days == 1 else "days"
    hour_label = "hour" if hours == 1 else "hours"

    return f"{days} {day_label} {hours} {hour_label}"


def calculate_sailing_days(distance_nm, speed_knots):
    if speed_knots <= 0:
        raise ValueError("Speed must be greater than zero.")

    total_hours = distance_nm / speed_knots
    return total_hours / 24 * 1.1


def calculate_freight_revenue(tonnage, flat_rate, worldscale):
    return tonnage * flat_rate * (worldscale / 100)


def get_freight_revenue(use_lump_sum, lump_sum, tonnage, flat_rate, worldscale):
    if use_lump_sum:
        return lump_sum
    return calculate_freight_revenue(tonnage, flat_rate, worldscale)


def calculate_round_voyage_expense(
    laden_distance_nm,
    ballast_distance_nm,
    laden_speed_knots,
    ballast_speed_knots,
    laden_fuel_tpd,
    ballast_fuel_tpd,
    fuel_price,
    discharge_port_days,
    discharge_fuel_tpd,
    load_port_days,
    load_fuel_tpd,
    port_fuel_price,
    port_cost
):
    laden_days = calculate_sailing_days(laden_distance_nm, laden_speed_knots)
    ballast_days = calculate_sailing_days(ballast_distance_nm, ballast_speed_knots)

    laden_fuel_cost = laden_days * laden_fuel_tpd * fuel_price
    ballast_fuel_cost = ballast_days * ballast_fuel_tpd * fuel_price

    discharge_port_fuel_cost = discharge_port_days * discharge_fuel_tpd * port_fuel_price
    load_port_fuel_cost = load_port_days * load_fuel_tpd * port_fuel_price

    voyage_fuel_cost = laden_fuel_cost + ballast_fuel_cost
    port_fuel_cost = discharge_port_fuel_cost + load_port_fuel_cost

    total_expense = voyage_fuel_cost + port_fuel_cost + port_cost
    total_sailing_days = laden_days + ballast_days
    total_port_days = discharge_port_days + load_port_days
    total_days = total_sailing_days + total_port_days
    total_voyage_distance = laden_distance_nm + ballast_distance_nm

    return {
        "laden_days": laden_days,
        "ballast_days": ballast_days,
        "total_sailing_days": total_sailing_days,
        "discharge_port_days": discharge_port_days,
        "load_port_days": load_port_days,
        "total_port_days": total_port_days,
        "total_days": total_days,
        "total_voyage_distance": total_voyage_distance,
        "voyage_fuel_cost": voyage_fuel_cost,
        "port_fuel_cost": port_fuel_cost,
        "port_cost": port_cost,
        "total_expense": total_expense
    }


def calculate_tce(revenue, expenses, total_days):
    if total_days <= 0:
        raise ValueError("Total days must be greater than zero.")

    return (revenue - expenses) / total_days