import mercadopago

from fastapi import APIRouter, HTTPException

from app.crud_google import GoogleConvidados

from app.schemas import (
    PesquisaResponse,
    ConviteResponse,
    ConviteSemNumeroResponse,
    ConviteCriancasResponse,
    ConfirmacaoRequest,
    ConfirmacaoCriancaRequest,
    ConfirmacaoSemTelefoneRequest,
    MensagemResponse,
    PresenteRequest,
    CriarPagamentoRequest,
)

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/pesquisar", response_model=list[PesquisaResponse])
def pesquisar(nome: str, sheet: str):

    google = GoogleConvidados(
        sheet,
        carregar_convidados=True,
    )

    return google.pesquisar(nome)


@router.get("/convite", response_model=ConviteResponse)
def buscar_convite(principal: str, sheet: str):

    google = GoogleConvidados(
        sheet,
        carregar_convidados=True,
    )

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


@router.get("/convite_sem_numero", response_model=ConviteSemNumeroResponse)
def buscar_convite_sem_numero(principal: str, sheet: str):

    google = GoogleConvidados(
        sheet,
        carregar_convidados=True,
    )

    pessoas = google.buscar_convite(principal)

    if not pessoas:
        raise HTTPException(status_code=404, detail="Convite não encontrado.")

    confirmado = google.convite_ja_confirmado(principal)

    return {
        "confirmado": confirmado,
        "pessoas": pessoas,
    }


@router.get("/convite_criancas_simples", response_model=ConviteCriancasResponse)
def buscar_convite_criancas_simples(principal: str, sheet: str):

    google = GoogleConvidados(
        sheet,
        carregar_convidados=True,
    )

    pessoas, criancas = google.buscar_convite_com_criancas(principal)

    if not pessoas:
        raise HTTPException(status_code=404, detail="Convite não encontrado.")

    confirmado = google.convite_ja_confirmado(principal)

    return {
        "confirmado": confirmado,
        "criancas": criancas,
        "pessoas": pessoas,
    }


@router.post("/confirmar", response_model=MensagemResponse)
def confirmar(
    dados: ConfirmacaoRequest,
):

    google = GoogleConvidados(
        dados.sheet,
        carregar_convidados=True,
    )

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


@router.post("/confirmar_sem_telefone", response_model=MensagemResponse)
def confirmar_sem_telefone(
    dados: ConfirmacaoSemTelefoneRequest,
):

    google = GoogleConvidados(
        dados.sheet,
        carregar_convidados=True,
    )

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


@router.post("/confirmar_com_criancas_simples", response_model=MensagemResponse)
def confirmar_com_criancas_simples(
    dados: ConfirmacaoCriancaRequest,
):

    google = GoogleConvidados(
        dados.sheet,
        carregar_convidados=True,
    )

    if google.convite_ja_confirmado(dados.principal):
        raise HTTPException(status_code=409, detail="Este convite já foi confirmado.")

    confirmacoes = [
        {
            "convidado": pessoa.convidado,
            "confirmacao": pessoa.confirmacao,
        }
        for pessoa in dados.pessoas
    ]

    google.salvar_confirmacoes_com_criancas(
        dados.principal, confirmacoes, dados.criancas
    )

    return {"sucesso": True, "mensagem": "Confirmação registrada com sucesso."}


@router.get("/presentes")
def presentes(sheet: str):

    google = GoogleConvidados(
        sheet,
        carregar_presentes=True,
    )

    return google.buscar_presentes()


@router.get("/dados")
def dados_noivos(sheet: str):

    google = GoogleConvidados(
        sheet,
        carregar_dados=True,
    )

    return google.buscar_dados_noivos()


@router.post("/presente")
def salvar_presente(dados: PresenteRequest):

    google = GoogleConvidados(
        dados.sheet,
        carregar_presentes_recebidos=True,
    )

    google.salvar_presente(
        presente=dados.presente,
        valor=dados.valor,
        nome=dados.nome,
        mensagem=dados.mensagem,
        tipo_pagamento=dados.tipo_pagamento,
    )

    return {"sucesso": True}


@router.post("/criar-pagamento")
def criar_pagamento(dados: CriarPagamentoRequest):

    try:
        google = GoogleConvidados(
            dados.sheet,
            carregar_dados=True,
        )

        access_token = google.buscar_mercado_pago_token()

        sdk = mercadopago.SDK(access_token)

        preference_data = {
            "items": [
                {
                    "title": dados.presente,
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": dados.valor,
                },
            ],
            "payment_methods": {
                "installments": 6,
                "default_installments": 1,
            },
        }

        preference_response = sdk.preference().create(preference_data)

        if preference_response.get("status") not in (200, 201):
            raise HTTPException(
                status_code=500, detail="Erro ao criar pagamento no Mercado Pago."
            )

        return {"link_pagamento": preference_response["response"]["init_point"]}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
