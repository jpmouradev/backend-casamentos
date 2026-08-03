import pandas as pd
import time

from app.google_sheets import client_google
from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal

CACHE_TTL = 60  # segundos

_planilha_cache = {}
_worksheet_cache = {}
_dataframe_cache = {}


class GoogleConvidados:

    def __init__(
        self,
        sheet_id: str,
        carregar_dados=False,
        carregar_convidados=False,
        carregar_presentes=False,
        carregar_presentes_recebidos=False,
    ):

        self.sheet_id = sheet_id

        self.planilha = self._obter_planilha()

        if carregar_dados:
            self.worksheet_dados = self._obter_worksheet("Dados")
            self.df_dados = self._obter_dataframe("Dados")

        if carregar_convidados:
            self.worksheet_convidados = self._obter_worksheet("Convidados")
            self.df = self._obter_dataframe("Convidados")

        if carregar_presentes:
            self.worksheet_presentes = self._obter_worksheet("Presentes")
            self.df_presentes = self._obter_dataframe("Presentes")
            self.df_presentes["preco"] = (
                self.df_presentes["preco"]
                .fillna("0")
                .astype(str)
                .str.strip()
                .str.replace(",", ".", regex=False)
                .apply(Decimal)
            )

        if carregar_presentes_recebidos:
            self.worksheet_presentes_recebidos = self._obter_worksheet(
                "Presentes Recebidos"
            )

    def _obter_planilha(self):

        cache = _planilha_cache.get(self.sheet_id)

        if cache:
            timestamp, planilha = cache

            if time.time() - timestamp < CACHE_TTL:
                return planilha

        planilha = client_google.open_by_key(self.sheet_id)

        _planilha_cache[self.sheet_id] = (
            time.time(),
            planilha,
        )

        return planilha

    def _obter_worksheet(self, nome):

        chave = (self.sheet_id, nome)

        cache = _worksheet_cache.get(chave)

        if cache:
            timestamp, worksheet = cache

            if time.time() - timestamp < CACHE_TTL:
                return worksheet

        worksheet = self.planilha.worksheet(nome)

        _worksheet_cache[chave] = (
            time.time(),
            worksheet,
        )

        return worksheet

    def _obter_dataframe(self, nome):

        chave = (self.sheet_id, nome)

        cache = _dataframe_cache.get(chave)

        if cache:
            timestamp, df = cache

            if time.time() - timestamp < CACHE_TTL:
                return df

        worksheet = self._obter_worksheet(nome)

        valores = worksheet.get_all_values()

        cabecalho = valores[0]
        linhas = valores[1:]

        df = pd.DataFrame(linhas, columns=cabecalho)

        if nome == "Presentes":
            df["preco"] = (
                df["preco"]
                .fillna("0")
                .astype(str)
                .str.strip()
                .replace("", "0")
                .str.replace(",", ".", regex=False)
                .astype(float)
            )

        _dataframe_cache[chave] = (
            time.time(),
            df,
        )

        return df

    def _limpar_cache(self, nome_aba):

        chave = (self.sheet_id, nome_aba)

        _dataframe_cache.pop(chave, None)

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

    def buscar_convite_com_criancas(self, principal: str):

        convidados = (
            self.df[self.df["nome_principal"] == principal]
            .sort_values("convidado")
            .to_dict(orient="records")
        )

        if not convidados:
            return {
                "convidados": [],
                "criancas": 0,
            }

        criancas = 0

        for convidado in convidados:
            valor = convidado.get("criancas")

            if pd.notna(valor) and str(valor).strip() != "":
                criancas = int(valor)
                break

        return convidados, criancas

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

        updates = []

        for item in confirmacoes:

            valor = "Sim" if item["confirmacao"] else "Não"

            for indice, linha in enumerate(registros, start=2):

                if (
                    linha["nome_principal"] == principal
                    and linha["convidado"] == item["convidado"]
                ):

                    updates.append(
                        {
                            "range": f"C{indice}",
                            "values": [[valor]],
                        }
                    )

                    break

        if updates:
            self.worksheet_convidados.batch_update(updates)

        self._limpar_cache("Convidados")

    def salvar_confirmacoes_com_criancas(
        self,
        principal: str,
        confirmacoes: list,
        confirmacao_crianca: int,
    ):

        registros = self.df.to_dict(orient="records")

        updates = []

        for item in confirmacoes:

            valor = "Sim" if item["confirmacao"] else "Não"

            for indice, linha in enumerate(registros, start=2):

                if (
                    linha["nome_principal"] == principal
                    and linha["convidado"] == item["convidado"]
                ):

                    updates.append(
                        {
                            "range": f"C{indice}",
                            "values": [[valor]],
                        }
                    )

                    break

        for indice, linha in enumerate(registros, start=2):

            if linha["nome_principal"] != principal:
                continue

            criancas = linha.get("criancas")

            if pd.notna(criancas) and str(criancas).strip():

                updates.append(
                    {
                        "range": f"E{indice}",
                        "values": [[confirmacao_crianca]],
                    }
                )

                break

        if updates:
            self.worksheet_convidados.batch_update(updates)

        self._limpar_cache("Convidados")

    def buscar_presentes(self):

        return self.df_presentes.to_dict(orient="records")

    def salvar_presente(
        self, presente: str, valor: float, nome: str, mensagem: str, tipo_pagamento: str
    ):
        data = datetime.now(ZoneInfo("America/Fortaleza")).strftime("%d/%m/%Y %H:%M")

        linha = [presente, valor, nome, mensagem, tipo_pagamento, data]

        self.worksheet_presentes_recebidos.append_row(
            linha, value_input_option="USER_ENTERED"
        )
        self._limpar_cache("Presentes Recebidos")

    def buscar_dados_noivos(self):

        return self.df_dados.iloc[0].to_dict()

    def buscar_mercado_pago_token(self):
        if self.df_dados.empty:
            raise ValueError("A aba Dados está vazia.")

        token = self.df_dados.iloc[0].get("mercado_pago_token")

        if not token or pd.isna(token):
            raise ValueError("mercado_pago_token não encontrado na aba Dados.")

        return str(token).strip()
