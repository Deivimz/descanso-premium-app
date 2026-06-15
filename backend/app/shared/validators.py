import re

def is_valid_rut(rut: str) -> bool:
    """
    Valida un RUT chileno usando el algoritmo de Módulo 11.
    Acepta formatos: '12.345.678-9', '12345678-9', '123456789'
    El cuerpo puede tener de 6 a 8 dígitos (RUT van desde 1.000.000 hasta 99.999.999).
    """
    if not rut:
        return False

    # Eliminar puntos, guiones y espacios; convertir a mayúsculas
    rut_clean = rut.replace(".", "").replace("-", "").replace(" ", "").upper()

    # El cuerpo puede tener 6, 7 u 8 dígitos + 1 dígito verificador (0-9 o K)
    # Total: 7, 8 o 9 caracteres
    if not re.match(r"^\d{6,8}[0-9K]$", rut_clean):
        return False

    body = rut_clean[:-1]
    dv = rut_clean[-1]

    # Algoritmo Módulo 11
    suma = 0
    multiplo = 2
    for digit in reversed(body):
        suma += int(digit) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1

    remainder = suma % 11
    expected_dv_value = 11 - remainder

    if expected_dv_value == 11:
        expected_dv = "0"
    elif expected_dv_value == 10:
        expected_dv = "K"
    else:
        expected_dv = str(expected_dv_value)

    return dv == expected_dv
