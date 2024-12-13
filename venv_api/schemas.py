from pydantic import BaseModel, EmailStr
from typing import List, Optional


# Schema para Cliente
class ClienteCreateSchema(BaseModel):
    nome: Optional[str]
    idade: Optional[int]
    telefone: Optional[str]
    email: Optional[EmailStr]
    cpf: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "nome": "Arthur Farias",
                "idade": 27,
                "telefone": "83987388484",
                "email": "arthurfarias10@hotmail.com",
                "cpf": "01598142437"
            }
        }


# View Schema para visualização de um cliente
class ClienteViewSchema(ClienteCreateSchema):
    id: Optional[int]

# Schema para a listagem de clientes


class ListagemClientesSchema(BaseModel):
    clientes: List[ClienteViewSchema] = []

    class Config:
        orm_mode = True


# Schema para remoção de cliente
class ClienteDelSchema(BaseModel):
    message: Optional[str]
    nome: Optional[str]

# Schema para erros


class ErrorSchema(BaseModel):
    message: Optional[str]

# Schema para busca de cliente


class ClienteBuscaSchema(BaseModel):
    nome: Optional[str]
    email: Optional[EmailStr]
    cpf: Optional[str]
    idade: Optional[int]
    telefone: Optional[str]

# Schema para Comentário


class ComentarioCreateSchema(BaseModel):
    cliente_cpf: str  # Alterado de cliente_nome para cliente_cpf
    texto: str  # Tornado obrigatório
    arquivo: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "cliente_cpf": "01598142437",
                "texto": "Ótimo atendimento!",
                "arquivo": "comentario.txt"
            }
        }
        