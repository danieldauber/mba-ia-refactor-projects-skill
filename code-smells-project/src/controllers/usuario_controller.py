from werkzeug.security import generate_password_hash, check_password_hash
from src.models import usuario_model


def listar_todos(db) -> list:
    return usuario_model.get_all(db)


def buscar_por_id(db, usuario_id: int) -> dict:
    usuario = usuario_model.get_by_id(db, usuario_id)
    if usuario is None:
        raise ValueError("Usuário não encontrado")
    return usuario


def criar(db, dados: dict) -> dict:
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        raise ValueError("Nome, email e senha são obrigatórios")
    senha_hash = generate_password_hash(senha, method="pbkdf2:sha256")
    usuario_id = usuario_model.create(db, nome, email, senha_hash)
    return {"id": usuario_id}


def login(db, email: str, senha: str) -> dict:
    if not email or not senha:
        raise ValueError("Email e senha são obrigatórios")
    usuario = usuario_model.get_by_email(db, email)
    if usuario is None or not check_password_hash(usuario["senha"], senha):
        raise PermissionError("Email ou senha inválidos")
    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "tipo": usuario["tipo"],
    }
