from typing import Optional


def get_faturamento_bruto(db) -> float:
    cursor = db.cursor()
    cursor.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos")
    return cursor.fetchone()[0]


def get_counts_by_status(db) -> dict:
    cursor = db.cursor()
    result = {}
    for status in ("pendente", "aprovado", "cancelado"):
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", (status,))
        result[status] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    result["total"] = cursor.fetchone()[0]
    return result


def get_all_with_items(db) -> list:
    cursor = db.cursor()
    cursor.execute("""
        SELECT
            p.id, p.usuario_id, p.status, p.total, p.criado_em,
            ip.produto_id, ip.quantidade, ip.preco_unitario,
            pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = ip.produto_id
        ORDER BY p.id
    """)
    return _group_pedidos(cursor.fetchall())


def get_by_usuario(db, usuario_id: int) -> list:
    cursor = db.cursor()
    cursor.execute("""
        SELECT
            p.id, p.usuario_id, p.status, p.total, p.criado_em,
            ip.produto_id, ip.quantidade, ip.preco_unitario,
            pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = ip.produto_id
        WHERE p.usuario_id = ?
        ORDER BY p.id
    """, (usuario_id,))
    return _group_pedidos(cursor.fetchall())


def create(db, usuario_id: int, total: float) -> int:
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    db.commit()
    return cursor.lastrowid


def add_item(db, pedido_id: int, produto_id: int, quantidade: int, preco_unitario: float):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
        (pedido_id, produto_id, quantidade, preco_unitario),
    )
    db.commit()


def decrement_estoque(db, produto_id: int, quantidade: int):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        (quantidade, produto_id),
    )
    db.commit()


def get_produto_for_order(db, produto_id: int) -> "Optional[dict]":
    cursor = db.cursor()
    cursor.execute("SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (produto_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def update_status(db, pedido_id: int, novo_status: str) -> bool:
    cursor = db.cursor()
    cursor.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()
    return True


def _group_pedidos(rows) -> list:
    pedidos = {}
    for row in rows:
        pid = row["id"]
        if pid not in pedidos:
            pedidos[pid] = {
                "id": pid,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
        if row["produto_id"]:
            pedidos[pid]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] if row["produto_nome"] else "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())
