from typing import List
from typing import Optional

from pydantic import BaseModel


class PesquisaResponse(BaseModel):
    principal: str


class PessoaResponse(BaseModel):
    id: int
    nome: str
    telefone: str
    principal: str
    confirmacao: Optional[bool] = None


class ConviteResponse(BaseModel):
    principal: str
    telefone: str
    confirmado: bool
    pessoas: List[PessoaResponse]


class ConfirmacaoPessoa(BaseModel):
    id: int
    nome: str
    confirmacao: bool


class ConfirmacaoRequest(BaseModel):
    principal: str
    telefone_final: str
    sheet: str
    evento: str
    pessoas: List[ConfirmacaoPessoa]


class MensagemResponse(BaseModel):
    sucesso: bool
    mensagem: str


class EstatisticasResponse(BaseModel):
    total: int
    confirmados: int
    recusados: int
    pendentes: int