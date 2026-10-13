from flask import Blueprint, request, jsonify
from src.controllers import usuario_controller
from database import get_db

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/usuarios", methods=["GET"])
def listar():
    usuarios = usuario_controller.listar_todos(get_db())
    return jsonify({"dados": usuarios, "sucesso": True}), 200


@usuarios_bp.route("/usuarios/<int:id>", methods=["GET"])
def buscar(id):
    try:
        usuario = usuario_controller.buscar_por_id(get_db(), id)
        return jsonify({"dados": usuario, "sucesso": True}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404


@usuarios_bp.route("/usuarios", methods=["POST"])
def criar():
    try:
        dados = request.get_json()
        resultado = usuario_controller.criar(get_db(), dados or {})
        return jsonify({"dados": resultado, "sucesso": True}), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@usuarios_bp.route("/login", methods=["POST"])
def login():
    try:
        dados = request.get_json() or {}
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        usuario = usuario_controller.login(get_db(), email, senha)
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except PermissionError as e:
        return jsonify({"erro": str(e), "sucesso": False}), 401
