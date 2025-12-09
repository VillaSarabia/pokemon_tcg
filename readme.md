# Pokemon TCG - Sistema de Gestión de Cartas Pokémon

Sistema profesional de e-commerce para la venta de cartas Pokémon TCG, desarrollado con Django.

## Características Principales

### 🎨 Diseño y Experiencia de Usuario
- Diseño responsivo con paleta de colores Pokémon oficial
- Menú hamburguesa con animaciones CSS3
- Layout moderno con Flexbox/Grid CSS
- Templates reutilizables con herencia de Django

### 🔐 Seguridad y Autenticación
- Sistema de login/registro con validación
- Panel de administración protegido
- Sesiones independientes por usuario
- Protección CSRF en todos los formularios
- Decoradores de permisos (@login_required, @staff_member_required)

### 🛍️ Funcionalidades Cliente
- Catálogo completo de cartas con filtros avanzados
- Sistema de carrito persistente
- 4 métodos de pago diferentes
- Historial de pedidos
- Wishlist/favoritos
- Reseñas y valoraciones

### 📊 Panel de Administración
- Dashboard con estadísticas de ventas
- Gestión completa de inventario
- Sistema de alertas de stock bajo
- Templates CRUD reutilizables
- Gestión de pedidos

## Requisitos del Sistema

- Python 3.8+
- Django 4.2+
- Pillow 9.5+
- SQLite3 (producción: PostgreSQL/MySQL)