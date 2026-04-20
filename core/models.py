from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, time
from localflavor.br.models import BRCNPJField
from django.contrib.auth.models import User

# ============================
# PERMISSÕES DE ACESSO
# ============================
class ConfiguracaoSistema(models.Model):
    chave = models.CharField(max_length=100, unique=True)
    valor = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.chave}: {self.valor}"
    
    def save(self, *args, **kwargs):
        self.chave = "senha_rodanegocios"
        super().save(*args, **kwargs)



class Meta:
    permissions = [
        ("acesso_rodanegocios", "Pode acessar o sistema Rodanegocios"),
    ]


class SolicitacaoAcesso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    justificativa = models.TextField()
    aprovado = models.BooleanField(default=False)
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Acesso de {self.usuario.username}"

# ============================
# INTERESSE
# ============================
class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["nome", "ordem"]  # Ordena por nome e depois por ordem

    def __str__(self):
        return self.nome
    
class Interesse(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
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
        ("VENDEDOR", "Vendedor"),
    ]
    nome = models.CharField(max_length=255)
    cnpj = BRCNPJField(unique=True, null=True, blank=True)
    endereco = models.ForeignKey("Endereco", on_delete=models.SET_NULL, null=True, blank=True)
    site = models.CharField(max_length=255, blank=True)
    segmento = models.CharField(max_length=255, blank=True)
    modalidade = models.CharField(max_length=255, blank=True, choices=CHOISES_MODALIDADE, default="VENDEDOR")
    interesses = models.ManyToManyField(Interesse, related_name="empresas", blank=True)

    def save(self, *args, **kwargs):
        if self.site:
            # Se o usuário não colocou http:// ou https://, adiciona automaticamente
            if not self.site.startswith(("http://", "https://")):
                self.site = "https://" + self.site
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
    
# ============================
# ENDEREÇO
# ============================
class Endereco(models.Model):
    rua = models.CharField(max_length=255, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    complemento = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=255, blank=True)
    cidade = models.CharField(max_length=255)
    estado = models.CharField(max_length=255)
    cep = models.CharField(max_length=20, blank=True)
    pais = models.CharField(max_length=255, default="Brasil")

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.cidade}/{self.estado}"
    
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
    participantes = models.ManyToManyField(
        Empresa, through='EmpresaEvento',
        related_name='eventos_participantes'
)

    def __str__(self):
        return f"{self.nome} - {self.data:%d/%m/%Y}"

# ===============================
# EMPRESA PARTICIPANTE DE EVENTO
# ===============================
class EmpresaEvento(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    participa = models.BooleanField(default=True)

    class Meta:
        unique_together = ('empresa', 'evento')

    def __str__(self):
        return f"{self.empresa.nome} — {self.evento.nome} ({'Participa' if self.participa else 'Não participa'})"
    

# ============================
# REPRESENTANTE
# ============================
class Representante(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='representantes')
    nome = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
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
    inicio_ro = models.TimeField(default=timezone.now)
    fim_ro = models.TimeField(default=timezone.now)
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="rodadas"   
    )
    def __str__(self):
        return f"{self.nome} - {self.inicio_ro:%H:%M} - {self.fim_ro:%H:%M}"


# ============================
# MESA
# ============================
class Mesa(models.Model):
    rodada = models.ForeignKey(Rodada, on_delete=models.CASCADE,
                               null=True, blank=True, related_name="mesas")
    numero = models.PositiveIntegerField()

    comprador = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="mesas_como_comprador",
        null=True,
        blank=True
    )

    vendedor = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="mesas_como_vendedor",
        null=True,
        blank=True
    )
    @property
    def status(self):
        if self.comprador and self.vendedor:
            return "completa"
        elif self.comprador or self.vendedor:
            return "vaga"
        return "vazia"
    
    def __str__(self):
        return f"Mesa {self.numero}"

