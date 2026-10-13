from typing import Optional


def _serialize(row, include_senha: bool = False) -> dict:
    data = {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }
    if include_senha:
        data["senha"] = row["senha"]
    return data


def get_all(db) -> list:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios")
    return [_serialize(row) for row in cursor.fetchall()]


def get_by_id(db, usuario_id: int) -> "Optional[dict]":
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    row = cursor.fetchone()
    return _serialize(row) if row else None


def get_by_email(db, email: str) -> "Optional[dict]":
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()
    return _serialize(row, include_senha=True) if row else None


def create(db, nome: str, email: str, senha_hash: str, tipo: str = "cliente") -> int:
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid
