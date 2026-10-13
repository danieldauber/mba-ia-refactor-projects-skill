import os

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
DB_PATH = os.environ.get("DB_PATH", "loja.db")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

DISCOUNT_THRESHOLD_HIGH = 10000
DISCOUNT_RATE_HIGH = 0.10
DISCOUNT_THRESHOLD_MID = 5000
DISCOUNT_RATE_MID = 0.05
DISCOUNT_THRESHOLD_LOW = 1000
DISCOUNT_RATE_LOW = 0.02

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
