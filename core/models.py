from django.db import models
from django.core.exceptions import ValidationError


class Empresa(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    site = models.URLField(blank=True)
    segmento = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.nome


class Representante(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='representantes')
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.nome} ({self.empresa.nome})'


class Evento(models.Model):
    nome = models.CharField(max_length=255)
    data = models.DateField()
    local = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class SlotHorario(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='slots')
    inicio = models.DateTimeField()
    fim = models.DateTimeField()

    def __str__(self):
        return f'{self.evento.nome} - {self.inicio:%H:%M} às {self.fim:%H:%M}'


class Reuniao(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    )

    slot = models.ForeignKey(SlotHorario, on_delete=models.CASCADE, related_name='reunioes')
    empresa_a = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='reunioes_como_a')
    empresa_b = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='reunioes_como_b')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')

    class Meta:
        unique_together = (
            ('slot', 'empresa_a', 'empresa_b'),
        )

    def __str__(self):
        return f'{self.empresa_a} x {self.empresa_b} em {self.slot}'

    # - Uma empresa não pode ter duas reuniões no mesmo slot
    def clean(self):
        if self.empresa_a == self.empresa_b:
            raise ValidationError('Uma reunião precisa de duas empresas diferentes.')

        # - Uma empresa não pode ter duas reuniões no mesmo horário
        conflito = Reuniao.objects.filter(slot=self.slot).filter(
            models.Q(empresa_a=self.empresa_a) |
            models.Q(empresa_b=self.empresa_a) |
            models.Q(empresa_a=self.empresa_b) |
            models.Q(empresa_b=self.empresa_b)
        )
        if self.pk:
            conflito = conflito.exclude(pk=self.pk)

        if conflito.exists():
            raise ValidationError('Uma das empresas já possui reunião neste horário.')
