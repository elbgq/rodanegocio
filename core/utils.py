import random
import colorsys
from .models import ConfiguracaoSistema

# Função para gerar uma cor única para cada vendedor
def cor_para_vendedor(vendedor_id):
    random.seed(vendedor_id)
    r = random.randint(80, 200)
    g = random.randint(80, 200)
    b = random.randint(80, 200)
    return {
        "solid": f"rgb({r}, {g}, {b})",
        "alpha": f"rgba({r}, {g}, {b}, 0.18)"  # fundo suave
    }


# Função para ler a senha do Rodanegocios
def get_senha_rodanegocios():
    obj, _ = ConfiguracaoSistema.objects.get_or_create(
        chave="senha_rodanegocios",
        defaults={"valor": "rodanegocios123"}  # senha inicial
    )
    return obj.valor

# Função utilitária para gravar a senha do Rodanegocios
def set_senha_rodanegocios(nova_senha):
    ConfiguracaoSistema.objects.update_or_create(
        chave="senha_rodanegocios",
        defaults={"valor": nova_senha}
    )


