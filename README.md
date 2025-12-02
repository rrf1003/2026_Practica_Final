# 📊 Repo Analyzer - Analizador de Calidad de Software

Aplicación web desarrollada en **Python/Flask** que permite analizar repositorios de GitHub para evaluar la calidad de su código mediante métricas estáticas.

El proyecto ha sido diseñado siguiendo estrictamente principios de **Ingeniería del Software**, implementando múltiples **Patrones de Diseño** para garantizar desacoplamiento, mantenibilidad y escalabilidad.

---

## 🏗️ Arquitectura y Patrones de Diseño

El núcleo del proyecto se basa en la separación de responsabilidades:

1.  **Singleton (`ConfigSingleton`):** Centralización de la configuración (rutas de BD, caché, parámetros).
2.  **Strategy (`metrics/*.py`):** Implementación polimórfica de algoritmos de análisis. Permite añadir nuevas métricas (como LCOM o Cohesión) sin modificar el código existente (*Open/Closed Principle*).
    * *Estrategias:* LOC, TODOs, Imports, Funciones (AST), Duplicación (Shingles), Mantenibilidad (MI Index).
3.  **Facade (`MetricsFacade`):** Simplifica la complejidad del subsistema de métricas, ofreciendo una interfaz única de cálculo (`compute_all`).
4.  **Proxy (`ProxySubject`):** Intermediario inteligente que gestiona la caché. Si un repositorio ya ha sido analizado, recupera los datos de SQLite en lugar de recalcular, optimizando el rendimiento.
5.  **Mediator (`UIMediator`):** Desacopla totalmente la vista (Flask) de la lógica de negocio. Coordina los componentes de UI (`Input`, `Options`, `Output`, `History`).

---

## ⚙️ Requisitos Previos

* **Python 3.10** o superior.
* **Git** instalado en el sistema (necesario para clonar repositorios externos).

---

## 🚀 Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar la aplicación en tu entorno local:

### 1. Clonar el proyecto e instalar dependencias

Se recomienda usar un entorno virtual:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Instalar librerías
pip install -r requirements.txt
```

### 2. Ejecutar la aplicación

Lanza el servidor web de Flask:
**python app.py**

La aplicación estará disponible en: **http://127.0.0.1:5000**
La primera vez que analices un repositorio, se creará automáticamente la carpeta repo_cache/ y la base de datos analysis_v2.db.

### 3. Ejecutar los Tests

Desde la raíz del proyecto, ejecuta:
**pytest**

Si quieres ver qué porcentaje del código está cubierto por los tests:
**pytest --cov=metrics**

### Estructura del Proyecto
2026_Practica_Final/
├── app.py                      # Punto de entrada (Flask)
├── config.py                   # Singleton de Configuración
├── pytest.ini                  # Configuración de los tests
├── requirements.txt            # Dependencias
├── README.md                   # Documentación
├── analysis_v2.db              # Bases de Datos
│
├── pics/
│
├── metrics/                    # Lógica de Negocio (Patrón Strategy)
│   ├── base.py                 # Interfaz abstracta
│   ├── duplication.py          # Detecta la duplicación de código
│   ├── facade.py               # Patrón Facade
│   ├── functions.py            # Análisis AST (Complejidad, Nesting)
│   ├── imports.py              # Numero de imports
│   ├── lines.py                # Lineas totales del fichero
│   ├── maintainability.py      # Índice de Mantenibilidad
│
├── proxy/                      # Patrón Proxy (Caché)
│   ├── proxy_subject.py        # Lógica de Caché vs Cálculo Real
│   └── subject_interface.py    # Interfaz común para el RealSubject y el Proxy.
│
├── repo/                  # Capa de Persistencia
│   ├── db_manager.py      # Gestión SQLite
│   └── repo_manager.py    # Gestión Git y Filesystem (Windows-safe)
│
├── ui/                    # Capa de Presentación (Patrón Mediator)
│   ├── mediator.py        # Coordinador UI
│   └── templates/         # Vistas HTML (Jinja2)
│
└── tests/                 # Tests Unitarios
    ├── conftest.py        # Fixtures y datos de prueba
    └── test_metrics.py    # Batería de pruebas