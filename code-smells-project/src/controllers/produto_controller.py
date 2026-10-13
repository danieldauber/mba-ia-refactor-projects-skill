from typing import Optional
from src.models import produto_model
from src.config.settings import CATEGORIAS_VALIDAS


def listar_todos(db) -> list:
    return produto_model.get_all(db)


def buscar_por_id(db, produto_id: int) -> dict:
    produto = produto_model.get_by_id(db, produto_id)
    if produto is None:
        raise ValueError("Produto não encontrado")
    return produto


def buscar(db, termo: str, categoria: Optional[str], preco_min: Optional[float], preco_max: Optional[float]) -> list:
    return produto_model.search(db, termo, categoria, preco_min, preco_max)


def criar(db, dados: dict) -> dict:
    _validar(dados)
    produto_id = produto_model.create(
        db,
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return {"id": produto_id}


def atualizar(db, produto_id: int, dados: dict) -> bool:
    existing = produto_model.get_by_id(db, produto_id)
    if existing is None:
        raise ValueError("Produto não encontrado")
    _validar(dados)
    return produto_model.update(
        db,
        produto_id,
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )


def deletar(db, produto_id: int) -> bool:
    existing = produto_model.get_by_id(db, produto_id)
    if existing is None:
        raise ValueError("Produto não encontrado")
    return produto_model.delete(db, produto_id)


def _validar(dados: dict):
    if not dados:
        raise ValueError("Dados inválidos")
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            raise ValueError(f"{campo.capitalize()} é obrigatório")
    if dados["preco"] < 0:
        raise ValueError("Preço não pode ser negativo")
    if dados["estoque"] < 0:
        raise ValueError("Estoque não pode ser negativo")
    nome = dados["nome"]
    if len(nome) < 2:
        raise ValueError("Nome muito curto")
    if len(nome) > 200:
        raise ValueError("Nome muito longo")
    categoria = dados.get("categoria", "geral")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError(f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}")
