from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, time

# ============================
# EVENTO
# ============================
class Evento(models.Model):
    nome = models.CharField(max_length=255)
    data = models.DateField(default=timezone.now)
    local = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    inicio_ev = models.TimeField(default=time(8, 0))
    termino_ev = models.TimeField(default=time(18, 0))

    def __str__(self):
        return f"{self.nome} - {self.data:%d/%m/%Y}"
    
# ============================
# INTERESSE
# ============================
class Interesse(models.Model):
    CATEGORIAS = [
        ("PAIS", "País"),
        ("PRECO", "Faixa de Preço"),
        ("TIPO", "Tipo de Produto"),
        ("PERFIL", "Perfil Desejado"),
        ("REGIAO", "Região do Brasil"),
        ("OUTRO", "Outro"),
    ]

    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="OUTRO")
    nome = models.CharField(max_length=100, unique=True)
    
    class Meta:
        unique_together = ("categoria", "nome")  # Evita duplicação de interesses

    def __str__(self):
        return self.nome
    
# ============================
# EMPRESA
# ============================
class Empresa(models.Model):
    CHOISES_MODALIDADE = [
        ("COMPRADOR", "Comprador"),
        ("EXPOSITOR", "Expositor"),
    ]
    nome = models.CharField(max_length=255)
    interesses = models.ManyToManyField(Interesse, related_name="empresas", blank=True)
    site = models.CharField(max_length=255, blank=True)
    segmento = models.CharField(max_length=255, blank=True)
    modalidade = models.CharField(max_length=255, blank=True, choices=CHOISES_MODALIDADE, default="EXPOSITOR")

    def save(self, *args, **kwargs):
        if self.site:
            # Se o usuário não colocou http:// ou https://, adiciona automaticamente
            if not self.site.startswith(("http://", "https://")):
                self.site = "https://" + self.site
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
 
class PerfilComprador(models.Model):
    empresa = models.OneToOneField(Empresa, on_delete=models.CASCADE)

    rotulos_internacionais = models.IntegerField(null=True, blank=True)
    paises_que_trabalha = models.ManyToManyField(Interesse, related_name="compradores_paises", blank=True)
    preco_medio = models.ManyToManyField(Interesse, related_name="compradores_preco", blank=True)
    tipos_produto = models.ManyToManyField(Interesse, related_name="compradores_tipos", blank=True)
    regioes_interesse = models.ManyToManyField(Interesse, related_name="compradores_regioes", blank=True)

    def __str__(self):
        return f"Perfil do Comprador: {self.empresa.nome}"


class PerfilExpositor(models.Model):
    empresa = models.OneToOneField(Empresa, on_delete=models.CASCADE)

    pais_origem = models.ForeignKey(Interesse, on_delete=models.SET_NULL, null=True, related_name="expositores_pais")
    preco_faixa = models.ManyToManyField(Interesse, related_name="expositores_preco", blank=True)
    tipos_produto = models.ManyToManyField(Interesse, related_name="expositores_tipos", blank=True)
    regioes_brasil = models.ManyToManyField(Interesse, related_name="expositores_regioes", blank=True)
    perfil_comprador_desejado = models.ManyToManyField(Interesse, related_name="expositores_perfil", blank=True)

    def __str__(self):
        return f"Perfil do Expositor: {self.empresa.nome}"
    
# ============================
# REPRESENTANTE
# ============================
class Representante(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='representantes')
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.nome} ({self.empresa.nome})'


# ============================
# REUNIÃO
# ============================
class Reuniao(models.Model):
    DURACOES = [
        (15, "15 minutos"),
        (20, "20 minutos"),
        (30, "30 minutos"),
    ]
    nome = models.CharField(max_length=100)
    duracao = models.IntegerField(choices=DURACOES, default=20)
    inicio_ro = models.TimeField(default=timezone.now)
    fim_ro = models.TimeField(default=timezone.now)
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="reunioes"   
    )
    def __str__(self):
        return f"{self.nome} - {self.hora_inicio:%H:%M} - {self.hora_fim:%H:%M}"


# ============================
# MESA
# ============================
class Mesa(models.Model):
    numero = models.PositiveIntegerField()
    nome = models.CharField(max_length=100, blank=True, null=True)
    reuniao = models.ForeignKey(Reuniao, on_delete=models.CASCADE, related_name="mesas")

    class Meta:
        unique_together = ("numero", "reuniao")  # evita duplicação de mesas na mesma reuniao

    def __str__(self):
        return f"Mesa {self.numero} - {self.reuniao.nome}"

# ============================
# RESERVA
# ============================
class Reserva(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name="reservas")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    horario = models.TimeField(null=True, blank=True)  # opcional, se quiser registrar

    class Meta:
        unique_together = ('mesa', 'empresa')
    
    def __str__(self):
        return f"{self.empresa.nome} na Mesa {self.mesa.numero}"

    
