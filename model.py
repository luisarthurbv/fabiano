from pydantic import BaseModel, ConfigDict

class Oferta(BaseModel):
    title: str
    avaliacao: str
    valor: str
    descricao: str
    numero: str
    endereco: str
