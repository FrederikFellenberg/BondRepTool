import streamlit as st
import random
import re


def random_price(maturity, start_value_price, end_value_price):
    return round(random.uniform(start_value_price, end_value_price))


def random_coupon(maturity, start_value_coupon, end_value_coupon):
    return round(random.uniform(start_value_coupon, end_value_coupon), 1)


def gen_coupon_bonds(maturity, coupon_bonds):
    for year in range(1, maturity + 1):
        coupon_bonds.update({f"coupon_bond_{year}": []})
    return coupon_bonds


def gen_zero_bond(maturity):
    zero_bond = [100]
    for _ in range(maturity):
        zero_bond.append(0)
    return zero_bond


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
        value = (list(reversed(coupon_bonds[f"coupon_bond_{maturity + 1}"]))[maturity]
                 + difference(maturity + 1, coupon_bonds, price_list, coupon_list, max_maturity))
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

    for _ in range(1, maturity):
        coupon_bonds[f"coupon_bond_{maturity}"].append(coupon)

    coupon_bonds[f"coupon_bond_{maturity}"].append(price)

    current_length = len(coupon_bonds[f"coupon_bond_{maturity}"])
    zeros_to_add = max_maturity + 1 - current_length
    for _ in range(zeros_to_add):
        coupon_bonds[f"coupon_bond_{maturity}"].insert(0, 0)


def main():
    st.title("Bond Replication Tool")

    maturity = st.number_input("Maturity in Years: ", min_value=1, step=1)
    start_value_price = st.slider("Lower Bound for Price: ", 1, 100, 85)
    end_value_price = st.slider("Upper Bound for Price: ", 1, 200, 115)
    start_value_coupon = st.slider("Lower Bound for Coupon: ", 0.0, 10.0, 1.0)
    end_value_coupon = st.slider("Upper Bound for Coupon: ", 0.0, 20.0, 10.0)

    generate_bonds = st.button("Generate Bonds")

    if generate_bonds:
        max_maturity = maturity
        price_list = []
        coupon_list = []
        fraction_list = []
        coupon_bonds = {}

        to_replic_cf = [0 for _ in range(max_maturity - 1)]
        to_replic_cf.append(100)

        for year in range(1, maturity + 1):
            price = random_price(maturity, start_value_price, end_value_price)
            coupon = random_coupon(maturity, start_value_coupon, end_value_coupon)
            price_list.append(price)
            coupon_list.append(coupon)

        st.write("Price List:", price_list)
        st.write("Coupon List:", coupon_list)

        coupon_bonds = gen_coupon_bonds(maturity, coupon_bonds)
        coupon_bonds, fraction_list = initalize_coupon_bonds(maturity, coupon_bonds, price_list, coupon_list,
                                                             max_maturity, fraction_list, to_replic_cf)

        st.write("Generated Coupon Bonds:", coupon_bonds)
        st.write("Fraction List:", fraction_list)


if __name__ == "__main__":
    main()