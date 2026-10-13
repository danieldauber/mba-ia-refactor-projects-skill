import logging
from flask import Flask, jsonify
from flask_cors import CORS

from src.config.settings import SECRET_KEY, DEBUG
from src.views.produto_routes import produtos_bp
from src.views.usuario_routes import usuarios_bp
from src.views.pedido_routes import pedidos_bp
from src.middlewares.error_handler import register_error_handlers
import database

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DEBUG"] = DEBUG

CORS(app)
database.init_app(app)
register_error_handlers(app)

app.register_blueprint(produtos_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(pedidos_bp)


@app.route("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


@app.route("/health")
def health_check():
    db = database.get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    produtos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    usuarios = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    pedidos = cursor.fetchone()[0]
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
        "versao": "1.0.0",
    }), 200


if __name__ == "__main__":
    with app.app_context():
        db = database.get_db()
        database.init_db(db)
        database.seed_db(db)

    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)

    app.run(host="0.0.0.0", port=5000, debug=DEBUG)
