from core.models import Empresa, Rodada, Mesa
from django.db import transaction
from datetime import timedelta, datetime
from core.utils import empresas_tem_relacao

#====================================
# Esta função calcula a afinidade entre duas pessoas com base nos interesses que elas
# têm em comum.
#====================================
def calcular_afinidade(a, b):
    interesses_a = set(a.interesses.values_list("id", flat=True))
    interesses_b = set(b.interesses.values_list("id", flat=True))
    return len(interesses_a.intersection(interesses_b))

#====================================
# Esta função implementa uma lógica de matching otimizado entre compradores e vendedores,
# respeitando limites e evitando repetições dentro da mesma rodada.
#=====================================
def gerar_pares_para_rodada(compradores, vendedores_disponiveis, qtd_mesas):
    matriz = []

    #Criação da matriz de afinidades e calcula a afinidade entre eles
    for c in compradores:
        for e in vendedores_disponiveis:
            
            # Trava de ralacionamento entre comprador e vendedor
            if empresas_tem_relacao(c.id, e.id):
                continue  # ignora este par
            
            score = calcular_afinidade(c, e)
            matriz.append((c, e, score))
            
    # Ordenação pela maior afinidade. A matriz está priorizando os melhores matches.
    matriz.sort(key=lambda x: x[2], reverse=True)

    # Preparação para montar os pares, garantindo que cada vendedor seja usado apenas uma vez
    # por rodada, mas permitindo que compradores possam repetir entre rodadas.
    pares = []
    usados_compradores = set()
    usados_vendedores = set()

    # Construção dos pares. Se já atingiu o número de mesas, para tudo.
    for c, e, score in matriz:
        if len(pares) >= qtd_mesas:
            break
        
        # Evitar repetição de vendedores dentro da mesma rodada, mas permitir
        # que eles possam participar de rodadas futuras.
        if e.id in usados_vendedores:
            continue

        # Evitar repetição de compradores dentro da mesma rodada, mas permitir que
        # eles possam participar de rodadas futuras.
        if c.id in usados_compradores:
            continue
        
        # Marca comprador e vendedor como usados. O vendedor não pode ser usado novamente
        # nesta rodada, mas o comprador pode ser usado em rodadas futuras.
        pares.append((c, e))
        usados_compradores.add(c.id)
        usados_vendedores.add(e.id)
        
    # Retorna os pares formados e os vendedores usados para que possam ser removidos da
    # lista de disponíveis para as próximas rodadas.
    return pares, usados_vendedores

#=====================================
# Essa é a função mais completa do fluxo, porque ela cria todas as rodadas, controla
# horários, pausas, mesas e garante que todos os vendedores sejam atendidos ao longo do evento.
#=====================================
def gerar_todas_as_rodadas(
    evento,
    qtd_mesas,
    duracao_minutos,
    inicio_rodadas,
    intervalo_minutos,
    pausa_cada,
    pausa_duracao
):
    # Carrega compradores e vendedores do evento
    compradores = list(Empresa.objects.filter(
        modalidade="COMPRADOR",
        empresaevento__evento=evento,
        empresaevento__participa=True
    ))

    vendedores = list(Empresa.objects.filter(
        modalidade="VENDEDOR",
        empresaevento__evento=evento,
        empresaevento__participa=True
    ))

    # Cria um conjunto com IDs dos vendedores restantes para garantir que cada vendedor
    # seja atendido apenas uma vez por rodada, mas possa participar de rodadas futuras.
    vendedores_restantes = set(e.id for e in vendedores)
    
    # Configura variáveis iniciais para controle de rodadas e horários
    rodadas_criadas = []
    numero_rodada = 1
    # início customizado para a primeira rodada
    horario_atual = datetime.combine(evento.data, datetime.strptime(inicio_rodadas, "%H:%M").time())
 
    # Loop principal: continua enquanto houver vendedores não atendidos. O loop garante
    # que cada vendedor seja atendido em pelo menos uma rodada, mas permite que compradores
    # possam repetir entre rodadas.
    while vendedores_restantes:
        # Seleciona apenas vendedores ainda disponíveis
        vendedores_disponiveis = [
            e for e in vendedores if e.id in vendedores_restantes
        ]

        # Gera os pares da rodada atual, garantindo que cada vendedor seja usado apenas
        # uma vez por rodada, mas permitindo que compradores possam repetir entre rodadas.
        pares, usados_vendedores = gerar_pares_para_rodada(
            compradores,
            vendedores_disponiveis,
            qtd_mesas
        )

        # Se não houver pares possíveis, encerra.
        if not pares:
            break
        
        # Calcula horário de início e fim da rodada.
        inicio = horario_atual.time()
        fim_dt = horario_atual + timedelta(minutes=duracao_minutos)
        fim = fim_dt.time()

        # Cria a rodada no banco de dados e as mesas correspondentes aos pares formados.
        # Cada vendedor é marcado como usado para esta rodada, mas pode ser usado em
        # rodadas futuras. Cada comprador pode ser usado em múltiplas rodadas, mas não
        # pode repetir dentro da mesma rodada.
        rodada = Rodada.objects.create(
            evento=evento,
            nome=f"Rodada {numero_rodada}",
            duracao=duracao_minutos,
            inicio_ro=inicio,
            fim_ro=fim
        )

        # Cria as mesas da rodada com os pares formados. Cada mesa representa um encontro
        # entre um comprador e um vendedor.
        for i, (comprador, vendedor) in enumerate(pares, start=1):
            Mesa.objects.create(
                rodada=rodada,
                numero=i,
                comprador=comprador,
                vendedor=vendedor
            )

        # Armazena a rodada criada para referência futura e incrementa o número da rodada.
        rodadas_criadas.append(rodada)
        numero_rodada += 1

        # Atualiza horário para próxima rodada
        horario_atual = fim_dt + timedelta(minutes=intervalo_minutos)
 
        # Pausa programada
        if pausa_cada > 0 and (numero_rodada - 1) % pausa_cada == 0:
            horario_atual += timedelta(minutes=pausa_duracao)
        
        # Remove vendedores que já foram usados nesta rodada, mas permite que compradores
        # possam repetir entre rodadas.
        vendedores_restantes -= usados_vendedores

    # Retorna todas as rodadas criadas para que possam ser exibidas ou processadas
    # posteriormente.
    return rodadas_criadas

# Resumo: "É um algoritmo guloso + organizador de agenda, muito bem estruturado."


