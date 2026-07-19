import pandas as pd

from app.google_sheets import client_google
from datetime import datetime


class GoogleConvidados:

    def __init__(self, sheet_id: str):

        planilha = client_google.open_by_key(sheet_id)
        self.worksheet_convidados = planilha.worksheet("Convidados")
        self.worksheet_presentes = planilha.worksheet("Presentes")
        self.worksheet_presentes_recebidos = planilha.worksheet("Presentes Recebidos")

        dados = self.worksheet_convidados.get_all_records()
        presentes = self.worksheet_presentes.get_all_records()
        self.df = pd.DataFrame(dados)
        self.df_presentes = pd.DataFrame(presentes)

    def pesquisar(self, pesquisa: str):

        pesquisa = pesquisa.lower().strip()

        df = self.df[self.df["convidado"].str.lower().str.contains(pesquisa, na=False)]

        principals = (
            df["nome_principal"].dropna().drop_duplicates().sort_values().tolist()
        )

        return [{"principal": principal} for principal in principals]

    def buscar_convite(self, principal: str):

        convidados = (
            self.df[self.df["nome_principal"] == principal]
            .sort_values("convidado")
            .to_dict(orient="records")
        )

        return convidados

    def validar_telefone(self, principal: str, final: str):

        convite = self.df[self.df["nome_principal"] == principal]

        if convite.empty:
            return False

        numero = "".join(filter(str.isdigit, str(convite.iloc[0]["numero"])))

        return numero.endswith(final)

    def convite_ja_confirmado(self, principal: str):

        convite = self.df[self.df["nome_principal"] == principal]

        if convite.empty:
            return False

        return any(
            pd.notna(confirmacao) and str(confirmacao).strip() != ""
            for confirmacao in convite["confirmacao"]
        )

    def salvar_confirmacoes(self, principal: str, confirmacoes: list):

        registros = self.df.to_dict(orient="records")

        for item in confirmacoes:

            valor = "Sim" if item["confirmacao"] else "Não"

            for indice, linha in enumerate(registros, start=2):

                if (
                    linha["nome_principal"] == principal
                    and linha["convidado"] == item["convidado"]
                ):

                    self.worksheet_convidados.update_cell(indice, 4, valor)

                    break

    def buscar_presentes(self):

        return self.df_presentes.to_dict(orient="records")

    def salvar_presente(
        self, presente: str, valor: float, nome: str, mensagem: str, tipo_pagamento: str
    ):

        data = datetime.now().strftime("%d/%m/%Y %H:%M")

        linha = [presente, valor, nome, mensagem, tipo_pagamento, data]

        self.worksheet_presentes_recebidos.append_row(
            linha, value_input_option="USER_ENTERED"
        )
