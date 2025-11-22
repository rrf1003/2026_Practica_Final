# Repo Analyzer - Analizador de Calidad de Código

Aplicación web en Flask diseñada para analizar repositorios de GitHub y calcular métricas de calidad de código (Líneas, Complejidad Ciclomática, Duplicación, Mantenibilidad) aplicando patrones de diseño de software avanzados.

> **Estado del proyecto:** 🚧 En desarrollo (Fase de configuración e infraestructura).

## 📋 Características del Diseño

El proyecto sigue una arquitectura estricta basada en patrones de diseño, tal como se define en los diagramas de arquitectura:

* **Singleton (`config.py`):** Para la gestión centralizada de configuración y rutas.
* **Strategy (`metrics/`):** Polimorfismo para los algoritmos de cálculo de métricas.
* **Facade (`metrics/facade.py`):** Simplificación del subsistema de análisis.
* **Proxy (`proxy/`):** Intermediario para caché y optimización de peticiones repetidas.
* **Mediator (`ui/`):** Desacoplamiento entre la lógica de negocio y los componentes de la interfaz de usuario.

## 🚀 Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto en tu entorno local.

### 1. Requisitos Previos
* **Python 3.10** o superior.
* **Git** instalado en el sistema.

### 2. Clonar el repositorio

```bash
git clone [https://github.com/rrf1003/2026_Practica_Final.git](https://github.com/TU_USUARIO/2026_Practica_Final.git)
cd 2026_Practica_Final

## 📂 Estructura del Proyecto

La estructura de archivos ha sido diseñada para asegurar la separación de responsabilidades:

```text
repo_analyzer/
├── app.py                 # Punto de entrada de la aplicación Flask
├── config.py              # Configuración global (Singleton)
├── requirements.txt       # Dependencias del proyecto
├── .gitignore             # Exclusiones de Git (seguridad y limpieza)
├── pics/                  # Recursos gráficos y diagramas
├── metrics/               # Estrategias de análisis (Lógica de negocio)
├── repo/                  # Gestión de persistencia (Git y SQLite)
├── proxy/                 # Patrón Proxy (Caché)
├── ui/                    # Capa de presentación (Mediator y Templates)
└── tests/                 # Tests unitarios (Pytest)