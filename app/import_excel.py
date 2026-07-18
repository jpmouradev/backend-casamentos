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
sheet_id = "1GjV9rnJ_LQfaN_Ac0GnOhUtiZ0CCW77j26l40yzV2Fo"

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

    sheets = build(
        "sheets",
        "v4",
        credentials=creds
    )

    spreadsheet = sheets.spreadsheets().get(
        spreadsheetId=sheet
    ).execute()

    for s in spreadsheet["sheets"]:
        if s["properties"]["title"] == "Gráfico":
            print("Dashboard já existe.")
            return

    requests = [
        {
            "addSheet": {
                "properties": {
                    "title": "Gráfico"
                }
            }
        }
    ]

    resposta = sheets.spreadsheets().batchUpdate(
        spreadsheetId=sheet,
        body={"requests": requests}
    ).execute()

    dashboard_sheet_id = resposta["replies"][0]["addSheet"]["properties"]["sheetId"]

    aba_principal = spreadsheet["sheets"][0]["properties"]["title"]

    values = [
        ["Status", "Quantidade"],
        ["Sim", f'=COUNTIF(\'{aba_principal}\'!D:D;"Sim")'],
        ["Não", f'=COUNTIF(\'{aba_principal}\'!D:D;"Não")'],
        ["Sem resposta", f'=COUNTIFS(\'{aba_principal}\'!A2:A;"<>";\'{aba_principal}\'!D2:D;"")']
    ]

    sheets.spreadsheets().values().update(
        spreadsheetId=sheet,
        range="Gráfico!A1:B4",
        valueInputOption="USER_ENTERED",
        body={
            "values": values
        }
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
                                    "sources": [{
                                        "sheetId": dashboard_sheet_id,
                                        "startRowIndex": 1,
                                        "endRowIndex": 4,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 1
                                    }]
                                }
                            },
                            "series": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId": dashboard_sheet_id,
                                        "startRowIndex": 1,
                                        "endRowIndex": 4,
                                        "startColumnIndex": 1,
                                        "endColumnIndex": 2
                                    }]
                                }
                            }
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": dashboard_sheet_id,
                                "rowIndex": 0,
                                "columnIndex": 3
                            }
                        }
                    }
                }
            }
        }
    ]

    sheets.spreadsheets().batchUpdate(
        spreadsheetId=sheet,
        body={"requests": requests}
    ).execute()

    print("Dashboard criado com sucesso.")

configurar_dashboard(sheet_id)