from django.shortcuts import redirect
from django.urls import reverse

class RodanegociosProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        caminho = request.path

        # Libera a página de acesso
        if caminho.startswith("/acesso/"):
            return self.get_response(request)

        # Libera arquivos estáticos (CSS, JS, imagens)
        if caminho.startswith("/static/"):
            return self.get_response(request)

        # Se não tiver acesso, bloqueia tudo
        if not request.session.get("acesso_rodanegocios"):
            return redirect(reverse("core:acesso_rodanegocios"))

        return self.get_response(request)