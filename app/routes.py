from fastapi import APIRouter, HTTPException

from app import crud
from app.supabase_client import supabase

from app.schemas import (
    PesquisaResponse,
    ConviteResponse,
    ConfirmacaoRequest,
    MensagemResponse,
    EstatisticasResponse,
)


router = APIRouter()


@router.get(
    "/pesquisar",
    response_model=list[PesquisaResponse]
)
def pesquisar(nome: str, evento: str):
    evento_id = crud.buscar_evento_id(supabase, evento)
    resultado = crud.pesquisar_convidados(
        supabase,
        evento_id,
        nome,
    )

    return resultado


@router.get(
    "/convite",
    response_model=ConviteResponse
)
def buscar_convite(
    principal: str, evento: str
):
    evento_id = crud.buscar_evento_id(supabase, evento)
    pessoas = crud.buscar_convite(
        supabase,
        evento_id,
        principal,
    )

    if not pessoas:
        raise HTTPException(
            status_code=404,
            detail="Convite não encontrado."
        )

    telefone = pessoas[0]["telefone"]

    telefone_mascarado = (
        telefone[:-4] + "XXXX"
    )

    confirmado = any(
        pessoa["confirmacao"] is not None
        for pessoa in pessoas
    )

    return {
        "principal": principal,
        "telefone": telefone_mascarado,
        "confirmado": confirmado,
        "pessoas": pessoas
    }


@router.post(
    "/confirmar",
    response_model=MensagemResponse
)
def confirmar(
    dados: ConfirmacaoRequest
):
    evento_id = buscar_evento_id(supabase, dados.evento)
    valido = crud.validar_telefone(
        supabase,
        evento_id,
        dados.principal,
        dados.telefone_final,
    )

    if not valido:
        raise HTTPException(
            status_code=401,
            detail="Telefone inválido."
        )


    if crud.convite_ja_confirmado(
        supabase,
        dados.principal,
        tag,
    ):
        raise HTTPException(
            status_code=409,
            detail="Este convite já foi confirmado."
        )


    confirmacoes = [
        {
            "id": pessoa.id,
            "confirmacao": pessoa.confirmacao
        }
        for pessoa in dados.pessoas
    ]


    crud.salvar_confirmacoes(
        supabase,
        evento_id,
        dados.principal,
        confirmacoes,
    )


    return {
        "sucesso": True,
        "mensagem": "Confirmação registrada com sucesso."
    }


@router.get(
    "/estatisticas",
    response_model=EstatisticasResponse
)
def estatisticas(evento: str):
    evento_id = crud.buscar_evento_id(supabase, evento)
    return crud.estatisticas(supabase, evento_id)