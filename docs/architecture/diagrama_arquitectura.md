# Diagrama de Arquitectura

## Visión general

```
┌─────────────────────────────────────────┐
│               Cliente                   │
│  (curl / Postman / frontend / tests)    │
└───────────────────┬─────────────────────┘
                    │ HTTP / JSON
                    ▼
┌─────────────────────────────────────────┐
│            Flask  (app.py)              │
│         Application Factory             │
│         create_app(config)              │
└──┬────┬────┬────┬────┬──────────────────┘
   │    │    │    │    │   Blueprints registrados
   ▼    ▼    ▼    ▼    ▼
┌──────────────────────────────────────────────────┐
│               Módulos del sistema                │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ personas │  │ usuarios │  │ sistemas │       │
│  │/personas │  │/usuarios │  │/sistemas │       │
│  └──────────┘  └──────────┘  └──────────┘       │
│                                                  │
│  ┌──────────┐  ┌──────────┐                     │
│  │  roles   │  │ permisos │                     │
│  │  /roles  │  │/permisos │                     │
│  └──────────┘  └──────────┘                     │
│                                                  │
│  Cada módulo contiene:                           │
│    __init__.py  ·  models.py  ·  validators.py   │
│    repository.py  ·  routes.py                   │
└──────────────────────┬───────────────────────────┘
                       │ ORM
                       ▼
┌─────────────────────────────────────────┐
│       Flask-SQLAlchemy  (ORM)           │
│       Flask-Migrate  (migraciones)      │
└───────────────────┬─────────────────────┘
                    │ SQL
                    ▼
┌─────────────────────────────────────────┐
│   PostgreSQL  (producción)              │
│   SQLite en memoria  (pruebas)          │
│                                         │
│   Tablas: personas · usuarios · roles   │
│           sistemas · permisos           │
│           usuario_roles · rol_permisos  │
└─────────────────────────────────────────┘
```

## Flujo RBAC

```
Sistema → Permiso → Rol → Usuario ← Persona
              └──────────────┘
         (herencia de permisos vía roles)
```

## Descripción de capas

| Capa | Componente | Responsabilidad |
|------|-----------|----------------|
| HTTP | Blueprint + routes.py | Recibe la petición, valida el ID, delega al repositorio, devuelve JSON |
| Validación | validators.py | Verifica campos obligatorios, longitudes y formatos antes de persistir |
| Negocio | repository.py | CRUD sobre la base de datos; maneja duplicados y dependencias |
| Modelo | models.py | Define la tabla SQLAlchemy y el método `to_dict()` |
| Persistencia | Flask-SQLAlchemy | ORM que abstrae las consultas SQL |
| Base de datos | PostgreSQL / SQLite | Almacenamiento relacional |
