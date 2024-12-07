import streamlit as st
import random
import pandas as pd


def random_price(maturity, start_value_price, end_value_price):
    return round(random.uniform(start_value_price, end_value_price))


def random_coupon(maturity, start_value_coupon, end_value_coupon):
    return round(random.uniform(start_value_coupon, end_value_coupon), 1)


def gen_coupon_bonds(maturity, coupon_bonds):
    for year in range(1, maturity + 1):
        coupon_bonds.update({f"coupon_bond_{year}": []})
    return coupon_bonds


def initalize_coupon_bonds(maturity, coupon_bonds, price_list, coupon_list, max_maturity, fraction_list, to_replic_cf):
    if coupon_bonds.get(f"coupon_bond_{maturity + 1}") is None:
        start_value = to_replic_cf[maturity - 1]
    else:
        value = difference(maturity, coupon_bonds, price_list, coupon_list, max_maturity)
        start_value = -value + to_replic_cf[maturity - 1]

    coupon_bonds[f"coupon_bond_{maturity}"].append(start_value)
    calc_fractions(maturity, coupon_bonds, price_list, coupon_list, fraction_list, max_maturity)

    if maturity > 1:
        initalize_coupon_bonds(maturity - 1, coupon_bonds, price_list, coupon_list, max_maturity, fraction_list,
                               to_replic_cf)

    return coupon_bonds, fraction_list


def difference(maturity, coupon_bonds, price_list, coupon_list, max_maturity):
    if coupon_bonds.get(f"coupon_bond_{maturity + 1}") is not None:
        value = (
                list(reversed(coupon_bonds[f"coupon_bond_{maturity + 1}"]))[maturity] +
                difference(maturity + 1, coupon_bonds, price_list, coupon_list, max_maturity)
        )
        return value
    else:
        return 0


def calc_fractions(maturity, coupon_bonds, price_list, coupon_list, fraction_list, max_maturity):
    fraction = coupon_bonds[f"coupon_bond_{maturity}"][0] / (100 + coupon_list[maturity - 1])
    fraction_list.append(fraction)
    cashflows_coupon_bonds(maturity, coupon_bonds, price_list, coupon_list, fraction, max_maturity)


def cashflows_coupon_bonds(maturity, coupon_bonds, price_list, coupon_list, fraction, max_maturity):
    coupon = coupon_list[maturity - 1] * fraction
    price = -(price_list[maturity - 1] * fraction)

    for year in range(1, maturity):
        coupon_bonds[f"coupon_bond_{maturity}"].append(coupon)

    coupon_bonds[f"coupon_bond_{maturity}"].append(price)

    current_length = len(coupon_bonds[f"coupon_bond_{maturity}"])
    zeros_to_add = max_maturity + 1 - current_length
    for _ in range(zeros_to_add):
        coupon_bonds[f"coupon_bond_{maturity}"].insert(0, 0)


def reset_state():
    # Setze den Session-State auf Standardwerte
    st.session_state.clear()
    st.session_state['state'] = "start"
    st.rerun()


def main():
    st.title("Bond Replication Tool")

    if "state" not in st.session_state:
        st.session_state['state'] = "start"
    if "price_list" not in st.session_state:
        st.session_state['price_list'] = []
    if "coupon_list" not in st.session_state:
        st.session_state['coupon_list'] = []

    # Sidebar Einstellungen
    st.sidebar.header("Settings")
    maturity = st.sidebar.number_input("Maturity in Years", min_value=1, value=3, step=1)
    advanced_settings = st.sidebar.checkbox("Show Advanced Settings")
    start_value_price, end_value_price = 85, 115
    start_value_coupon, end_value_coupon = 1.0, 10.0

    if advanced_settings:
        st.sidebar.subheader("Advanced Price Settings")
        start_value_price = st.sidebar.slider("Lower Bound for Price", 1, 100, start_value_price, step=1)
        end_value_price = st.sidebar.slider("Upper Bound for Price", 1, 200, end_value_price, step=1)
        st.sidebar.subheader("Advanced Coupon Settings")
        start_value_coupon = st.sidebar.slider("Lower Bound for Coupon", 0.0, 10.0, start_value_coupon, step=0.1)
        end_value_coupon = st.sidebar.slider("Upper Bound for Coupon", 0.0, 20.0, end_value_coupon, step=0.1)

    col1, col2 = st.columns(2)

    if col1.button("Generate Bonds", key="generate"):
        st.session_state['state'] = "generate"
        st.session_state['price_list'] = [random_price(maturity, start_value_price, end_value_price) for _ in
                                          range(maturity)]
        st.session_state['coupon_list'] = [random_coupon(maturity, start_value_coupon, end_value_coupon) for _ in
                                           range(maturity)]

    if col2.button("Initialize Bonds", key="initialize"):
        # Wenn auf "Initialize Bonds" geklickt wird, wird der Zustand auf "initialize" gesetzt
        st.session_state["state"] = "initialize"

    # Wenn der Zustand "initialize" ist, zeigt die Eingabefelder an
    if st.session_state["state"] == "initialize":
        # Zeige die Eingabefelder mit den aktuellen Werten aus session_state
        prices_input = st.text_input("Prices (comma separated):")
        coupons_input = st.text_input("Coupons (comma separated):")

        # Wenn der Benutzer auf "Apply" klickt, speichere die Eingabewerte in session_state
        if st.button("Apply", key="apply"):
            try:
                # Verarbeite die Eingaben als Listen von Floats
                price_list = [float(p) for p in prices_input.split(",")]
                coupon_list = [float(c) for c in coupons_input.split(",")]

                if len(price_list) == maturity and len(coupon_list) == maturity:
                    st.session_state["price_list"] = price_list
                    st.session_state["coupon_list"] = coupon_list
                    st.session_state["state"] = "generate"
                else:
                    st.error("Lists must be of length equal to maturity.")
            except ValueError:
                st.error("Invalid inputs, please ensure all values are numeric and separated by commas.")

    if st.session_state['state'] == "generate":
        st.subheader("Generated Bonds")
        bonds_df = pd.DataFrame({
            "Year": range(1, maturity + 1),
            "Price": st.session_state['price_list'],
            "Coupon": st.session_state['coupon_list']
        })
        st.dataframe(bonds_df)

        st.session_state['cashflow_input'] = st.text_input("Cash Flow Sequence (comma separated)", "")

        col1, col2 = st.columns(2)
        if col1.button("Show Results", key="results"):
            st.session_state['state'] = "result"
            cashflow_input = st.session_state['cashflow_input']
            if not cashflow_input or len(cashflow_input.split(",")) != maturity:
                to_replic_cf = [0 for _ in range(maturity - 1)]  # Define default cash flow sequence if none provided
                to_replic_cf.append(100)
                st.info("Proceeding with default Cash Flow Sequence.")
            else:
                to_replic_cf = [float(value) for value in cashflow_input.split(",")]

        if col2.button("Reset", key="result_generate"):
            reset_state()

    if st.session_state['state'] == "result":
        try:
            st.session_state['coupon_bonds'] = {}
            st.session_state['fraction_list'] = []
            # Generiere Coupon Bonds
            st.session_state['coupon_bonds'] = gen_coupon_bonds(maturity, st.session_state['coupon_bonds'])
            coupon_bonds, fraction_list = initalize_coupon_bonds(
                maturity, st.session_state['coupon_bonds'], st.session_state['price_list'],
                st.session_state['coupon_list'], maturity, st.session_state['fraction_list'], to_replic_cf
            )

            # Dynamische Header erstellen
            header = ["Maturity", "Fraction"] + [f"Cashflow t={year}" for year in range(maturity + 1)]

            # Initialisiere Daten für die Tabelle
            table_data = []
            for year in reversed(range(1, maturity + 1)):
                fraction = list(reversed(fraction_list))[year - 1]
                cashflows = list(reversed(coupon_bonds[f"coupon_bond_{year}"]))
                row = [year, round(fraction, 4)] + [round(cf, 2) for cf in cashflows]
                table_data.append(row)

            # Berechne NPV-Zeile
            npv_list = [sum(values) for values in zip(*coupon_bonds.values())]
            npv_row = ["Diff.", ""] + [round(npv, 2) for npv in list(reversed(npv_list))]

            # DataFrame erstellen
            results_df = pd.DataFrame(table_data, columns=header)
            results_df.loc[len(results_df)] = npv_row  # NPV-Zeile hinzufügen

            # Tabelle anzeigen
            st.subheader("Results")
            st.dataframe(results_df)

            st.session_state['state'] = "generate"
        except NameError:
            st.error("Please provide a valid cash flow sequence.")


if __name__ == "__main__":
    main()