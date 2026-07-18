import gspread
import os
import pandas as pd

from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from app.google_sheets import client_google, creds_info


def salvar_confirmacoes_google(
    sheet: str,
    principal: str,
    confirmacoes: list
):
    """
    Atualiza a coluna 'Confirmacao' da planilha.

    Estrutura esperada:
    Convidado | Numero | Nome Principal | Confirmacao
    """

    planilha = client_google.open_by_key(sheet)
    sheet = planilha.get_worksheet(0)

    registros = sheet.get_all_records()

    for item in confirmacoes:
        valor = "Sim" if item["confirmacao"] else "Não"
        for indice, linha in enumerate(registros, start=2):

            if (
                linha["Nome Principal"] == principal
                and linha["Convidado"] == item["nome"]
            ):

                sheet.update_cell(
                    indice,
                    4,
                    valor
                )

                break
