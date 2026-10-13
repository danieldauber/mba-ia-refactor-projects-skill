from flask import Blueprint, request, jsonify
from src.controllers import produto_controller
from database import get_db

produtos_bp = Blueprint("produtos", __name__)


@produtos_bp.route("/produtos", methods=["GET"])
def listar():
    produtos = produto_controller.listar_todos(get_db())
    return jsonify({"dados": produtos, "sucesso": True}), 200


@produtos_bp.route("/produtos/busca", methods=["GET"])
def buscar():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria") or None
    preco_min = request.args.get("preco_min")
    preco_max = request.args.get("preco_max")
    preco_min = float(preco_min) if preco_min else None
    preco_max = float(preco_max) if preco_max else None
    resultados = produto_controller.buscar(get_db(), termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


@produtos_bp.route("/produtos/<int:id>", methods=["GET"])
def buscar_por_id(id):
    try:
        produto = produto_controller.buscar_por_id(get_db(), id)
        return jsonify({"dados": produto, "sucesso": True}), 200
    except ValueError as e:
        return jsonify({"erro": str(e), "sucesso": False}), 404


@produtos_bp.route("/produtos", methods=["POST"])
def criar():
    try:
        dados = request.get_json()
        resultado = produto_controller.criar(get_db(), dados or {})
        return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Produto criado"}), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@produtos_bp.route("/produtos/<int:id>", methods=["PUT"])
def atualizar(id):
    try:
        dados = request.get_json()
        produto_controller.atualizar(get_db(), id, dados or {})
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200
    except ValueError as e:
        status = 404 if "não encontrado" in str(e) else 400
        return jsonify({"erro": str(e)}), status


@produtos_bp.route("/produtos/<int:id>", methods=["DELETE"])
def deletar(id):
    try:
        produto_controller.deletar(get_db(), id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404
