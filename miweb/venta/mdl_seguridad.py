# Middleware
class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response # Se inicia cuando se carga el servidor

    def __call__(self, request):
        print("Antes de la vista")
        response = self.get_response(request)
        print("Después de la vista")

        return response