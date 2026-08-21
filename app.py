from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app(config=None):
    app = Flask(__name__)

    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)

    import personas.models  # noqa: F401
    import usuarios.models  # noqa: F401
    import roles.models     # noqa: F401
    import sistemas.models  # noqa: F401
    import permisos.models  # noqa: F401

    from personas import Blueprint_Personas
    app.register_blueprint(Blueprint_Personas, url_prefix="/personas")

    from usuarios import Blueprint_Usuarios
    app.register_blueprint(Blueprint_Usuarios, url_prefix="/usuarios")

    from roles import Blueprint_Roles
    app.register_blueprint(Blueprint_Roles, url_prefix="/roles")

    from sistemas import Blueprint_Sistemas
    app.register_blueprint(Blueprint_Sistemas, url_prefix="/sistemas")

    from permisos import Blueprint_Permisos
    app.register_blueprint(Blueprint_Permisos, url_prefix="/permisos")

    @app.route("/")
    def home():
        return "Hola Flask"

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
