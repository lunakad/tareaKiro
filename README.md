# Person & User Management API (RBAC)

API REST construida con Flask que implementa gestión de personas, usuarios y control de acceso basado en roles (RBAC).

---

## Objetivo del proyecto

Proveer una API REST que permita administrar personas, usuarios y un modelo completo de RBAC (Role-Based Access Control): sistemas, permisos, roles y sus asignaciones. El proyecto aplica el patrón Application Factory de Flask con separación en módulos, repositorios y validadores.

---

## RBAC — Control de acceso basado en roles

El sistema implementa RBAC siguiendo esta jerarquía:

```
Persona → Usuario → Roles → Permisos → Sistemas
```

1. Se registra una **Persona** con sus datos de identidad.
2. Se crea un **Usuario** asociado a esa Persona.
3. Se crean **Sistemas** (aplicaciones o módulos).
4. Se crean **Permisos** dentro de cada Sistema.
5. Se crean **Roles** y se les asignan Permisos.
6. Se asignan Roles al Usuario.

El Usuario hereda todos los Permisos de sus Roles.

---

## Tecnologías utilizadas

| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Python | 3.12 | Lenguaje principal |
| Flask | 3.1.3 | Framework web |
| Flask-SQLAlchemy | 3.1.1 | ORM |
| Flask-Migrate | 4.1.0 | Migraciones de base de datos |
| bcrypt | ≥ 4.1 | Hash de contraseñas |
| PostgreSQL | — | Base de datos en producción |
| SQLite | — | Base de datos en desarrollo y pruebas |
| pytest | — | Framework de pruebas |
| hypothesis | ≥ 6.100 | Pruebas basadas en propiedades |

---

## Estructura del proyecto

```
tareaKiro/
│
├── app.py                   # Application Factory, db, migrate, blueprints
├── exceptions.py            # DuplicateError, DatabaseError, NotFoundError
├── utils.py                 # parse_id()
├── validators_base.py       # check_required, check_str_len, check_str_max
├── repo_base.py             # commit_or_raise()
├── requirements.txt         # Dependencias del proyecto
│
├── personas/                # CRUD de personas
│   ├── __init__.py
│   ├── models.py
│   ├── validators.py
│   ├── repository.py
│   └── routes.py
│
├── usuarios/                # CRUD de usuarios + asignación de roles
│   ├── __init__.py
│   ├── models.py
│   ├── validators.py
│   ├── repository.py
│   └── routes.py
│
├── sistemas/                # CRUD de sistemas
│   ├── __init__.py
│   ├── models.py
│   ├── validators.py
│   ├── repository.py
│   └── routes.py
│
├── roles/                   # CRUD de roles + asignación de permisos
│   ├── __init__.py
│   ├── models.py
│   ├── validators.py
│   ├── repository.py
│   └── routes.py
│
├── permisos/                # CRUD de permisos
│   ├── __init__.py
│   ├── models.py
│   ├── validators.py
│   ├── repository.py
│   └── routes.py
│
├── docs/
│   └── architecture/
│       └── diagrama_arquitectura.md   # Diagrama de capas
│
├── migrations/              # Migraciones Flask-Migrate
│
└── tests/
    ├── conftest.py
    ├── integration/
    │   └── test_flujo_rbac.py         # Prueba de integración RBAC
    ├── test_personas_routes.py
    ├── test_personas_validators.py
    ├── test_personas_pbt.py
    ├── test_usuarios_routes.py
    ├── test_usuarios_validators.py
    ├── test_usuarios_pbt.py
    ├── test_roles_routes.py
    ├── test_roles_validators.py
    ├── test_sistemas_routes.py
    ├── test_sistemas_validators.py
    ├── test_permisos_routes.py
    └── test_permisos_validators.py
```

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd tareaKiro

# 2. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar la base de datos (PostgreSQL)
export DATABASE_URL="postgresql://usuario:password@localhost:5432/nombre_bd"

# 5. Inicializar migraciones
flask db upgrade
```

---

## Ejecución

```bash
# Desarrollo (SQLite por defecto)
python app.py

# Producción (requiere DATABASE_URL configurado)
flask run
```

La API queda disponible en `http://localhost:5000`.

Endpoints principales:

| Recurso | Prefijo |
|---------|---------|
| Personas | `/personas` |
| Usuarios | `/usuarios` |
| Sistemas | `/sistemas` |
| Roles | `/roles` |
| Permisos | `/permisos` |

---

## Ejecución de pruebas

```bash
# Todas las pruebas
python -m pytest tests/ -v

# Solo pruebas unitarias de validadores
python -m pytest tests/ -v -k "validators"

# Solo pruebas de integración
python -m pytest tests/integration/ -v
```

Las pruebas utilizan SQLite en memoria; no requieren una instancia de PostgreSQL activa.

**Tipos de pruebas incluidas:**

- **Unitarias** — validadores con property-based testing (hypothesis): verifican que los validadores rechacen correctamente datos fuera de rango, formatos inválidos y campos obligatorios ausentes.
- **Integración** — pruebas de rutas REST con el cliente de pruebas de Flask: verifican todos los endpoints con sus códigos de respuesta esperados.
- **Integración RBAC** — `tests/integration/test_flujo_rbac.py`: verifica el flujo completo Persona → Usuario → Sistema → Rol → Permiso → asignaciones → verificación de acceso.

---

## Documentación de especificación

| Documento | Descripción |
|-----------|-------------|
| `.kiro/specs/person-user-management/requirements.md` | Requerimientos funcionales del sistema |
| `.kiro/specs/person-user-management/design.md` | Diseño técnico, modelos y arquitectura |
| `.kiro/specs/person-user-management/tasks.md` | Lista de tareas de implementación |

---

## Arquitectura

La aplicación sigue el patrón **Application Factory** de Flask con **Blueprints** por módulo.

```
Cliente
   ↓  HTTP/JSON
Flask (create_app)
   ↓  Blueprints
Módulos: personas · usuarios · sistemas · roles · permisos
   ↓  ORM
Flask-SQLAlchemy / Flask-Migrate
   ↓  SQL
PostgreSQL (producción) / SQLite (pruebas)
```

Cada módulo encapsula su modelo, validador, repositorio y rutas. Los archivos compartidos (`exceptions.py`, `utils.py`, `validators_base.py`, `repo_base.py`) evitan duplicación de lógica común.

El diagrama detallado se encuentra en [`docs/architecture/diagrama_arquitectura.md`](docs/architecture/diagrama_arquitectura.md).
