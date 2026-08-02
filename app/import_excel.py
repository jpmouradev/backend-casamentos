from supabase import create_client
from google_sheets import client_google, creds_info, creds
from googleapiclient.discovery import build
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)
sheet_id = "1hcfcJmJ_tRHmUfYitXX5ANtx3k0GHSf-ycOP8gL6j94"

complete_sheet = client_google.open_by_key(sheet_id)
# sheet = complete_sheet.get_worksheet(0)
# data = pd.DataFrame(sheet.get_all_records())

# df = data.rename(columns={
#     "Convidado": "nome",
#     "Numero": "telefone",
#     "Nome Principal": "principal"
# })

# df["confirmacao"] = None
# df["evento_id"] = 1
# print(df.head())

# data = df.to_dict(orient="records")

# response = (
#     supabase
#     .table("pessoas")
#     .insert(data)
#     .execute()
# )


def configurar_dashboard(sheet: str):
    """
    Cria uma aba 'Gráfico' com um gráfico de pizza caso ela não exista.
    """

    sheets = build("sheets", "v4", credentials=creds)

    spreadsheet = sheets.spreadsheets().get(spreadsheetId=sheet).execute()

    for s in spreadsheet["sheets"]:
        if s["properties"]["title"] == "Gráfico":
            print("Dashboard já existe.")
            return

    requests = [{"addSheet": {"properties": {"title": "Gráfico"}}}]

    resposta = (
        sheets.spreadsheets()
        .batchUpdate(spreadsheetId=sheet, body={"requests": requests})
        .execute()
    )

    dashboard_sheet_id = resposta["replies"][0]["addSheet"]["properties"]["sheetId"]

    aba_principal = spreadsheet["sheets"][0]["properties"]["title"]

    aba_convidados = next(
        sheet["properties"]["title"]
        for sheet in spreadsheet["sheets"]
        if sheet["properties"]["title"] == "Convidados"
    )

    values = [
        ["Status", "Quantidade"],
        ["Sim", f"=COUNTIF('{aba_convidados}'!D:D;\"Sim\")"],
        ["Não", f"=COUNTIF('{aba_convidados}'!D:D;\"Não\")"],
        [
            "Sem resposta",
            f"=COUNTIFS('{aba_convidados}'!A2:A;\"<>\";'{aba_convidados}'!D2:D;\"\")",
        ],
    ]

    sheets.spreadsheets().values().update(
        spreadsheetId=sheet,
        range="Gráfico!A1:B4",
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()

    requests = [
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Confirmações de Presença",
                        "pieChart": {
                            "legendPosition": "RIGHT_LEGEND",
                            "domain": {
                                "sourceRange": {
                                    "sources": [
                                        {
                                            "sheetId": dashboard_sheet_id,
                                            "startRowIndex": 1,
                                            "endRowIndex": 4,
                                            "startColumnIndex": 0,
                                            "endColumnIndex": 1,
                                        }
                                    ]
                                }
                            },
                            "series": {
                                "sourceRange": {
                                    "sources": [
                                        {
                                            "sheetId": dashboard_sheet_id,
                                            "startRowIndex": 1,
                                            "endRowIndex": 4,
                                            "startColumnIndex": 1,
                                            "endColumnIndex": 2,
                                        }
                                    ]
                                }
                            },
                        },
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": dashboard_sheet_id,
                                "rowIndex": 0,
                                "columnIndex": 3,
                            }
                        }
                    },
                }
            }
        }
    ]

    sheets.spreadsheets().batchUpdate(
        spreadsheetId=sheet, body={"requests": requests}
    ).execute()

    print("Dashboard criado com sucesso.")


def configurar_presentes_recebidos(sheet: str):
    """
    Cria a aba 'Presentes Recebidos' caso não exista.
    """

    sheets = build("sheets", "v4", credentials=creds)

    spreadsheet = sheets.spreadsheets().get(spreadsheetId=sheet).execute()

    for s in spreadsheet["sheets"]:
        if s["properties"]["title"] == "Presentes Recebidos":
            print("Aba Presentes Recebidos já existe.")
            return

    requests = [{"addSheet": {"properties": {"title": "Presentes Recebidos"}}}]

    resposta = (
        sheets.spreadsheets()
        .batchUpdate(spreadsheetId=sheet, body={"requests": requests})
        .execute()
    )

    # Cabeçalho inicial
    headers = [["presente", "valor", "nome", "mensagem", "tipo_pagamento", "data"]]

    sheets.spreadsheets().values().update(
        spreadsheetId=sheet,
        range="Presentes Recebidos!A1:F1",
        valueInputOption="USER_ENTERED",
        body={"values": headers},
    ).execute()

    print("Aba Presentes Recebidos criada com sucesso.")


def configurar_cores_confirmacao(sheet: str):

    sheets = build("sheets", "v4", credentials=creds)

    spreadsheet = sheets.spreadsheets().get(spreadsheetId=sheet).execute()

    convidados_sheet_id = None

    for aba in spreadsheet["sheets"]:
        if aba["properties"]["title"] == "Convidados":
            convidados_sheet_id = aba["properties"]["sheetId"]
            break

    if convidados_sheet_id is None:
        print("Aba Convidados não encontrada.")
        return

    requests = [
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": convidados_sheet_id,
                            "startRowIndex": 1,  # ignora cabeçalho
                            "startColumnIndex": 3,  # coluna D
                            "endColumnIndex": 4,
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "Sim"}],
                        },
                        "format": {
                            "backgroundColor": {"red": 0.75, "green": 1, "blue": 0.75}
                        },
                    },
                },
                "index": 0,
            }
        },
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": convidados_sheet_id,
                            "startRowIndex": 1,
                            "startColumnIndex": 3,
                            "endColumnIndex": 4,
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "Não"}],
                        },
                        "format": {
                            "backgroundColor": {"red": 1, "green": 0.75, "blue": 0.75}
                        },
                    },
                },
                "index": 1,
            }
        },
    ]

    sheets.spreadsheets().batchUpdate(
        spreadsheetId=sheet, body={"requests": requests}
    ).execute()

    print("Formatação condicional criada.")


configurar_dashboard(sheet_id)
configurar_presentes_recebidos(sheet_id)
configurar_cores_confirmacao(sheet_id)
