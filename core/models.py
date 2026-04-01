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
# EMPRESA
# ============================
class Empresa(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    site = models.CharField(max_length=255, blank=True)
    segmento = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if self.site:
            # Se o usuário não colocou http:// ou https://, adiciona automaticamente
            if not self.site.startswith(("http://", "https://")):
                self.site = "https://" + self.site
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
 
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
# RODADA
# ============================
class Rodada(models.Model):
    DURACOES = [
        (15, "15 minutos"),
        (20, "20 minutos"),
        (30, "30 minutos"),
    ]
    nome = models.CharField(max_length=100)
    duracao = models.IntegerField(choices=DURACOES, default=20)
    # data = models.DateField(default=timezone.now)
    inicio_ro = models.TimeField(default=timezone.now)
    fim_ro = models.TimeField(default=timezone.now)
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="rodadas"   
    )
    def __str__(self):
        return f"{self.nome} - {self.hora_inicio:%H:%M} - {self.hora_fim:%H:%M}"


# ============================
# MESA
# ============================
class Mesa(models.Model):
    numero = models.PositiveIntegerField()
    nome = models.CharField(max_length=100, blank=True, null=True)
    rodada = models.ForeignKey(Rodada, on_delete=models.CASCADE, related_name="mesas")

    class Meta:
        unique_together = ("numero", "rodada")  # evita duplicação de mesas na mesma rodada

    def __str__(self):
        return f"Mesa {self.numero} - {self.rodada.nome}"

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

    
