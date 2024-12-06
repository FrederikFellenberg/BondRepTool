import random

maturity = int(input("Maturity: "))
def random_metrics(maturity):
    price = random.uniform(0.5,1.5)
    coupon = random.uniform(0,0.15)
    return price, coupon


def gen_bond_properties(maturity):
    price_list = []
    coupon_list = []
    for year in range(1, maturity+1):
        price, coupon = random_metrics(year)
        price_list.append(price)
        coupon_list.append(coupon)
    return price_list, coupon_list


def gen_coupon_bonds(maturity):
    coupon_bonds = {}
    for year in range(1, maturity+1):
        coupon_bonds.update({f"coupon_bond_{year}": []})

    return coupon_bonds


def gen_zero_bond(maturity):
    zero_bond = [100]
    for year in range(maturity):
        zero_bond.append(0)

    return zero_bond


def initalize_coupon_bonds(maturity, coupon_bonds, price_list, coupon_list, max_maturity):
    if coupon_bonds.get(f"coupon_bond_{maturity + 1}") is None:
        start_value = 1
    else:
        value = difference(maturity, coupon_bonds, price_list, coupon_list, max_maturity)
        start_value = -value

    coupon_bonds[f"coupon_bond_{maturity}"].append(start_value)

    calc_fractions(maturity, coupon_bonds, price_list, coupon_list)

    if maturity > 1:
        initalize_coupon_bonds(maturity - 1, coupon_bonds, price_list, coupon_list, max_maturity)


def difference(maturity, coupon_bonds, price_list, coupon_list, max_maturity):
    if coupon_bonds.get(f"coupon_bond_{maturity + 1}") is not None:
        value = ((list(reversed(coupon_bonds[f"coupon_bond_{maturity + 1}"]))[maturity]) +
                  difference(maturity + 1, coupon_bonds, price_list, coupon_list, max_maturity))
        return value
    else:
        return 0

def calc_fractions(maturity, coupon_bonds, price_list, coupon_list):
    fraction = coupon_bonds[f"coupon_bond_{maturity}"][0] / (1 + coupon_list[maturity - 1])
    cashflows_coupon_bonds(maturity, coupon_bonds, price_list, coupon_list, fraction)


def cashflows_coupon_bonds(maturity, coupon_bonds, price_list, coupon_list, fraction):
    coupon = coupon_list[maturity - 1] * fraction
    price = -(price_list[maturity - 1] * fraction)

    for year in range(1, maturity):
        coupon_bonds[f"coupon_bond_{maturity}"].append(coupon)

    coupon_bonds[f"coupon_bond_{maturity}"].append(price)


coupon_bonds = gen_coupon_bonds(maturity)
price_list, coupon_list = ([1, 0.98, 1.02], [0.05, 0.04, 0.07])
initalize_coupon_bonds(maturity, coupon_bonds, price_list, coupon_list, maturity)
print(coupon_bonds)



