from core.models import Empresa, Rodada, Mesa
from django.db import transaction
from datetime import timedelta, datetime


def calcular_afinidade(a, b):
    interesses_a = set(a.interesses.values_list("id", flat=True))
    interesses_b = set(b.interesses.values_list("id", flat=True))
    return len(interesses_a.intersection(interesses_b))


def gerar_pares_para_rodada(compradores, expositores_disponiveis, qtd_mesas):
    matriz = []

    for c in compradores:
        for e in expositores_disponiveis:
            score = calcular_afinidade(c, e)
            matriz.append((c, e, score))

    matriz.sort(key=lambda x: x[2], reverse=True)

    pares = []
    usados_compradores = set()
    usados_expositores = set()

    for c, e, score in matriz:
        if len(pares) >= qtd_mesas:
            break

        if e.id in usados_expositores:
            continue

        # comprador pode repetir entre rodadas
        if c.id in usados_compradores:
            continue

        pares.append((c, e))
        usados_compradores.add(c.id)
        usados_expositores.add(e.id)

    return pares, usados_expositores


def gerar_todas_as_rodadas(
    evento,
    qtd_mesas,
    duracao_minutos,
    inicio_rodadas,
    intervalo_minutos,
    pausa_cada,
    pausa_duracao
):

    compradores = list(Empresa.objects.filter(modalidade="COMPRADOR"))
    expositores = list(Empresa.objects.filter(modalidade="EXPOSITOR"))

    expositores_restantes = set(e.id for e in expositores)
    rodadas_criadas = []

    numero_rodada = 1
    
    # início customizado para a primeira rodada
    horario_atual = datetime.combine(evento.data, datetime.strptime(inicio_rodadas, "%H:%M").time())


    while expositores_restantes:
        expositores_disponiveis = [
            e for e in expositores if e.id in expositores_restantes
        ]

        pares, usados_expositores = gerar_pares_para_rodada(
            compradores,
            expositores_disponiveis,
            qtd_mesas
        )

        if not pares:
            break
        
        # Calcula horário de início e fim
        inicio = horario_atual.time()
        fim_dt = horario_atual + timedelta(minutes=duracao_minutos)
        fim = fim_dt.time()

        rodada = Rodada.objects.create(
            evento=evento,
            nome=f"Rodada {numero_rodada}",
            duracao=duracao_minutos,
            inicio_ro=inicio,
            fim_ro=fim
        )

        for i, (comprador, expositor) in enumerate(pares, start=1):
            Mesa.objects.create(
                rodada=rodada,
                numero=i,
                comprador=comprador,
                expositor=expositor
            )

        rodadas_criadas.append(rodada)
        numero_rodada += 1

        # Atualiza horário para próxima rodada
        horario_atual = fim_dt + timedelta(minutes=intervalo_minutos)

        # Pausa programada
        if pausa_cada > 0 and (numero_rodada - 1) % pausa_cada == 0:
            horario_atual += timedelta(minutes=pausa_duracao)
            
        expositores_restantes -= usados_expositores

    return rodadas_criadas
