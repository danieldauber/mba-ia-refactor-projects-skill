import logging

logger = logging.getLogger(__name__)


def on_order_created(pedido_id: int, usuario_id: int):
    logger.info(f"[EMAIL] Order {pedido_id} created for user {usuario_id}")
    logger.info(f"[SMS] Order received confirmation for user {usuario_id}")
    logger.info(f"[PUSH] New order {pedido_id} received by the system")


def on_order_status_changed(pedido_id: int, novo_status: str):
    logger.info(f"[NOTIFICATION] Order {pedido_id} status changed to {novo_status}")
