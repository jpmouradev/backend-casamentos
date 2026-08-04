from typing import List, Optional
from pydantic import BaseModel


class PesquisaResponse(BaseModel):
    principal: str


class PessoaResponse(BaseModel):
    convidado: str
    numero: str
    nome_principal: str
    confirmacao: str


class PessoaSemNumeroResponse(BaseModel):
    convidado: str
    nome_principal: str
    confirmacao: str


class PessoaSimplesResponse(BaseModel):
    convidado: str
    nome_principal: str
    confirmacao: str


class ConviteResponse(BaseModel):
    confirmado: bool
    telefone: str
    pessoas: List[PessoaResponse]


class ConviteSemNumeroResponse(BaseModel):
    confirmado: bool
    pessoas: List[PessoaSemNumeroResponse]


class ConviteCriancasResponse(BaseModel):
    confirmado: bool
    criancas: int
    pessoas: List[PessoaSimplesResponse]


class ConfirmacaoPessoa(BaseModel):
    convidado: str
    confirmacao: bool


class ConfirmacaoRequest(BaseModel):
    principal: str
    telefone_final: str
    sheet: str
    pessoas: List[ConfirmacaoPessoa]


class ConfirmacaoSemTelefoneRequest(BaseModel):
    principal: str
    sheet: str
    pessoas: List[ConfirmacaoPessoa]


class ConfirmacaoCriancaRequest(BaseModel):
    principal: str
    criancas: int
    sheet: str
    pessoas: List[ConfirmacaoPessoa]


class MensagemResponse(BaseModel):
    sucesso: bool
    mensagem: str


class PresenteRequest(BaseModel):

    presente: str
    valor: float
    nome: Optional[str] = None
    mensagem: Optional[str] = None
    tipo_pagamento: str
    sheet: str


class CriarPagamentoRequest(BaseModel):
    presente: str
    valor: float
    sheet: str
