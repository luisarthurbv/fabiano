from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class Oferta(BaseModel):
    uf: str
    cidade: str
    title: str
    avaliacao: Decimal
    valor: Decimal
    desconto: Decimal
    descricao: str
    numero: str
    endereco: str
    endereco_normalizado: str
    link: str