from django.shortcuts import redirect
from django.urls import reverse

class RodanegociosProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        caminho = request.path
        
        # Permite logout SEM interferência
        if caminho.startswith("/accounts/logout"):
            return self.get_response(request)
        
        # URLs liberadas SEM restrição
        urls_livres = [
           "/",
            "/accounts/login/",
            "/solicitar-acesso/",
            "/admin/login/",
        ]

        if caminho in urls_livres:
            return self.get_response(request)

        # ---------------------------
        # B) Arquivos estáticos e admin
        # ---------------------------
        if caminho.startswith("/static/") or caminho.startswith("/admin/"):
            return self.get_response(request)

        # ---------------------------
        # C) Exige login
        # ---------------------------
        if not request.user.is_authenticated:
            return redirect("/accounts/login/")

        # ---------------------------
        # D) Staff tem acesso total
        # ---------------------------
        if request.user.is_staff:
            return self.get_response(request)

        # ---------------------------
        # E) Rotas que exigem permissão
        # ---------------------------
        if caminho.startswith("/rodanegocios/"):
            if not request.user.has_perm("core.acesso_rodanegocios"):
                return redirect(reverse("core:acesso_negado"))

        # ---------------------------
        # F) Rotas normais (permitidas)
        # ---------------------------
        return self.get_response(request)
