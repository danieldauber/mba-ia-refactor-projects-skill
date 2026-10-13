from flask import Blueprint, request, jsonify
from src.controllers import pedido_controller
from database import get_db

pedidos_bp = Blueprint("pedidos", __name__)


@pedidos_bp.route("/pedidos", methods=["POST"])
def criar():
    try:
        dados = request.get_json() or {}
        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])
        if not usuario_id:
            return jsonify({"erro": "Usuario ID é obrigatório"}), 400
        resultado = pedido_controller.criar(get_db(), usuario_id, itens)
        return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201
    except ValueError as e:
        return jsonify({"erro": str(e), "sucesso": False}), 400


@pedidos_bp.route("/pedidos", methods=["GET"])
def listar_todos():
    pedidos = pedido_controller.listar_todos(get_db())
    return jsonify({"dados": pedidos, "sucesso": True}), 200


@pedidos_bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_por_usuario(usuario_id):
    pedidos = pedido_controller.listar_por_usuario(get_db(), usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


@pedidos_bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status(pedido_id):
    try:
        dados = request.get_json() or {}
        novo_status = dados.get("status", "")
        pedido_controller.atualizar_status(get_db(), pedido_id, novo_status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@pedidos_bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    relatorio = pedido_controller.relatorio_vendas(get_db())
    return jsonify({"dados": relatorio, "sucesso": True}), 200
