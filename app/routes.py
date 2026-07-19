from fastapi import APIRouter, HTTPException

from app.crud_google import GoogleConvidados

from app.schemas import (
    PesquisaResponse,
    ConviteResponse,
    ConfirmacaoRequest,
    MensagemResponse,
    PresenteRequest,
)

router = APIRouter()


@router.get("/pesquisar", response_model=list[PesquisaResponse])
def pesquisar(nome: str, sheet: str):

    google = GoogleConvidados(sheet)

    return google.pesquisar(nome)


@router.get("/convite", response_model=ConviteResponse)
def buscar_convite(principal: str, sheet: str):

    google = GoogleConvidados(sheet)

    pessoas = google.buscar_convite(principal)

    if not pessoas:
        raise HTTPException(status_code=404, detail="Convite não encontrado.")

    telefone = str(pessoas[0]["numero"])

    telefone_mascarado = telefone[:-4] + "XXXX"

    confirmado = google.convite_ja_confirmado(principal)

    return {
        "telefone": telefone_mascarado,
        "confirmado": confirmado,
        "pessoas": pessoas,
    }


@router.post("/confirmar", response_model=MensagemResponse)
def confirmar(
    dados: ConfirmacaoRequest,
):

    google = GoogleConvidados(dados.sheet)

    if not google.validar_telefone(
        dados.principal,
        dados.telefone_final,
    ):
        raise HTTPException(status_code=401, detail="Telefone inválido.")

    if google.convite_ja_confirmado(dados.principal):
        raise HTTPException(status_code=409, detail="Este convite já foi confirmado.")

    confirmacoes = [
        {
            "convidado": pessoa.convidado,
            "confirmacao": pessoa.confirmacao,
        }
        for pessoa in dados.pessoas
    ]

    google.salvar_confirmacoes(
        dados.principal,
        confirmacoes,
    )

    return {"sucesso": True, "mensagem": "Confirmação registrada com sucesso."}


@router.get("/presentes")
def presentes(sheet: str):

    google = GoogleConvidados(sheet)

    return google.buscar_presentes()


@router.get("/dados")
def dados_noivos(sheet: str):

    google = GoogleConvidados(sheet)

    return google.buscar_dados_noivos()


@router.post("/presente")
def salvar_presente(dados: PresenteRequest):

    google = GoogleConvidados(dados.sheet)

    google.salvar_presente(
        presente=dados.presente,
        valor=dados.valor,
        nome=dados.nome,
        mensagem=dados.mensagem,
        tipo_pagamento=dados.tipo_pagamento,
    )

    return {"sucesso": True}
