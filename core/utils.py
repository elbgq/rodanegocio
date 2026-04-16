import random

def cor_para_vendedor(vendedor_id):
    random.seed(vendedor_id)
    r = random.randint(80, 200)
    g = random.randint(80, 200)
    b = random.randint(80, 200)
    return {
        "solid": f"rgb({r}, {g}, {b})",
        "alpha": f"rgba({r}, {g}, {b}, 0.18)"  # fundo suave
    }
