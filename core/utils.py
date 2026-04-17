import random
import colorsys


def cor_para_vendedor(vendedor_id):
    random.seed(vendedor_id)
    r = random.randint(80, 200)
    g = random.randint(80, 200)
    b = random.randint(80, 200)
    return {
        "solid": f"rgb({r}, {g}, {b})",
        "alpha": f"rgba({r}, {g}, {b}, 0.18)"  # fundo suave
    }

'''
# Paleta mais variada (HSV → RGB)
def cor_para_vendedor(vendedor_id):
    random.seed(vendedor_id)

    # Gera um hue entre 0 e 1
    hue = (vendedor_id * 0.61803398875) % 1  # número áureo para espaçar bem

    # Converte HSV → RGB
    r, g, b = colorsys.hsv_to_rgb(hue, 0.55, 0.95)

    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)

    return {
        "solid": f"rgb({r}, {g}, {b})",
        "alpha": f"rgba({r}, {g}, {b}, 0.20)"
    }

# Paleta pré-definida (cores “corporativas”)
PALETA = [
    (244, 67, 54),
    (33, 150, 243),
    (76, 175, 80),
    (255, 193, 7),
    (156, 39, 176),
    (255, 87, 34),
    (63, 81, 181),
    (0, 150, 136),
    (205, 220, 57),
    (121, 85, 72),
]

# Paleta pastel (mais suave)
def cor_para_vendedor(vendedor_id):
    idx = vendedor_id % len(PALETA)
    r, g, b = PALETA[idx]
    return {
        "solid": f"rgb({r}, {g}, {b})",
        "alpha": f"rgba({r}, {g}, {b}, 0.20)"
    }


def cor_para_vendedor(vendedor_id):
    random.seed(vendedor_id)
    r = random.randint(120, 200)
    g = random.randint(120, 200)
    b = random.randint(120, 200)
    return {
        "solid": f"rgb({r}, {g}, {b})",
        "alpha": f"rgba({r}, {g}, {b}, 0.25)"
    }
'''
