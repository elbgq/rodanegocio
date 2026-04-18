from django.shortcuts import redirect
from django.urls import reverse


class RodanegociosProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        caminho = request.path
        
        # ---------------------------
        # A) Libera a página de acesso (senha)
        # ---------------------------
        if caminho.startswith("/acesso/"):
            return self.get_response(request)

        # ---------------------------
        # B) Arquivos estáticos e admin
        # ---------------------------
        if caminho.startswith("/static/") or caminho.startswith("/admin/"):
            return self.get_response(request)

        # ---------------------------
        # C) Se não tem sessão, redireciona para /acesso/
        # ---------------------------
        if not request.session.get("acesso_rodanegocios"):
            return redirect("/acesso/")

        # ---------------------------
        # D) Staff tem acesso total
        # ---------------------------
        if request.user.is_staff:
            return self.get_response(request)

        # ---------------------------
        # E) Proteção específica para /rodanegocios/
        # ---------------------------
        if caminho.startswith("/rodanegocios/"):
            # Aqui você pode colocar regras extras se quiser
            pass

        # ---------------------------
        # F) Demais rotas liberadas
        # ---------------------------
        return self.get_response(request)
