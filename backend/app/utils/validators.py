from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def round_decimal(value, places="0.01") -> Decimal:
    if value is None:
        raise ValueError("Invalid numeric value: 'None'")

    try:
        rounded_value = Decimal(value)
    except InvalidOperation as e:
        raise ValueError(f"Invalid numeric value: {value}") from e

    return rounded_value.quantize(Decimal(places), rounding=ROUND_HALF_UP)
