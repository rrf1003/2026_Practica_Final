from flask import Flask, request
from proxy.proxy_subject import ProxySubject
from ui.mediator import UIMediator

# 1. Configuración de Flask
# Indicamos que busque los templates html dentro de la carpeta 'ui/templates'
app = Flask(__name__, template_folder="ui/templates")

# 2. Inicialización del Sistema (Composition Root)
# Creamos el Sujeto Real (Proxy) que tiene acceso a DB, Repo y Métricas
subject = ProxySubject()

# Creamos el Mediador que conectará la Vista con el Sujeto
mediator = UIMediator(subject)

# 3. Definición de Rutas
@app.route("/", methods=["GET"])
def index():
    """Ruta principal: Muestra el formulario y el historial."""
    return mediator.show_index()

@app.route("/analyze", methods=["POST"])
def analyze():
    """Ruta de acción: Procesa el formulario de análisis."""
    # Pasamos request.form (diccionario inmutable) al mediador
    return mediator.handle_analyze(request.form)

if __name__ == "__main__":
    # Ejecutamos en modo debug para desarrollo
    app.run(debug=True, port=5000)