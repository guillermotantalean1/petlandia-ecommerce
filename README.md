# Petlandia E-commerce

Petlandia es una tienda en línea de productos para mascotas con un propósito social: un porcentaje de todas las compras se destina a albergues de rescate animal.

## Características Principales

- Catálogo de productos para mascotas
- Carrito de compras
- Panel de administración para gestionar productos
- Sistema de autenticación para administradores
- Diseño responsive y amigable

## Tecnologías Utilizadas

- Python (Flask)
- HTML5
- CSS3
- JavaScript
- SQLite

## Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/your-username/petlandia-ecommerce.git
cd petlandia-ecommerce
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Iniciar la aplicación:
```bash
python app.py
```

5. Abrir el navegador en `http://localhost:5000`

## Estructura del Proyecto

```
petlandia-ecommerce/
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   ├── templates/
│   ├── models/
│   └── routes/
├── instance/
├── venv/
├── requirements.txt
├── config.py
└── app.py
```

## Contribución

Este es un proyecto educativo para un curso universitario.

## Licencia

MIT License
