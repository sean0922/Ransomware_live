import pycountry


def country_code_to_name(code: str) -> str:
    if code is None:
        return ""
    code = str(code).strip()
    if not code:
        return ""

    c = pycountry.countries.get(alpha_2=code.upper())
    if c:
        return c.name

    c = pycountry.countries.get(alpha_3=code.upper())
    if c:
        return c.name

    if code.isdigit():
        c = pycountry.countries.get(numeric=code.zfill(3))
        if c:
            return c.name

    return code
