from src.models import pedido_model
from src.services import notification_service
from src.config.settings import (
    STATUS_VALIDOS,
    DISCOUNT_THRESHOLD_HIGH, DISCOUNT_RATE_HIGH,
    DISCOUNT_THRESHOLD_MID, DISCOUNT_RATE_MID,
    DISCOUNT_THRESHOLD_LOW, DISCOUNT_RATE_LOW,
)


def criar(db, usuario_id: int, itens: list) -> dict:
    if not itens:
        raise ValueError("Pedido deve ter pelo menos 1 item")

    total = 0.0
    produtos_cache = {}
    for item in itens:
        produto = pedido_model.get_produto_for_order(db, item["produto_id"])
        if produto is None:
            raise ValueError(f"Produto {item['produto_id']} não encontrado")
        if produto["estoque"] < item["quantidade"]:
            raise ValueError(f"Estoque insuficiente para {produto['nome']}")
        produtos_cache[item["produto_id"]] = produto
        total += produto["preco"] * item["quantidade"]

    pedido_id = pedido_model.create(db, usuario_id, total)
    for item in itens:
        produto = produtos_cache[item["produto_id"]]
        pedido_model.add_item(db, pedido_id, item["produto_id"], item["quantidade"], produto["preco"])
        pedido_model.decrement_estoque(db, item["produto_id"], item["quantidade"])

    notification_service.on_order_created(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}


def listar_todos(db) -> list:
    return pedido_model.get_all_with_items(db)


def listar_por_usuario(db, usuario_id: int) -> list:
    return pedido_model.get_by_usuario(db, usuario_id)


def atualizar_status(db, pedido_id: int, novo_status: str) -> bool:
    if novo_status not in STATUS_VALIDOS:
        raise ValueError("Status inválido")
    result = pedido_model.update_status(db, pedido_id, novo_status)
    notification_service.on_order_status_changed(pedido_id, novo_status)
    return result


def relatorio_vendas(db) -> dict:
    counts = pedido_model.get_counts_by_status(db)
    faturamento = pedido_model.get_faturamento_bruto(db)
    total_pedidos = counts["total"]

    desconto = 0.0
    if faturamento > DISCOUNT_THRESHOLD_HIGH:
        desconto = faturamento * DISCOUNT_RATE_HIGH
    elif faturamento > DISCOUNT_THRESHOLD_MID:
        desconto = faturamento * DISCOUNT_RATE_MID
    elif faturamento > DISCOUNT_THRESHOLD_LOW:
        desconto = faturamento * DISCOUNT_RATE_LOW

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": counts["pendente"],
        "pedidos_aprovados": counts["aprovado"],
        "pedidos_cancelados": counts["cancelado"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
