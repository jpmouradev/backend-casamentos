import pandas as pd

# ============================================================
# CONFIGURAÇÃO
# ============================================================

ARQUIVO = "presentes.xlsx"
ABA = 0

# Informe aqui as colunas
COL_NOME = 0
COL_PRECO = 1
COL_IMAGEM = 2
COL_LINK_CARTAO = 3
COL_DESCRICAO = None


# ============================================================

df = pd.read_excel(ARQUIVO, sheet_name=ABA)


def valor(linha, coluna, default=""):
    if coluna is None:
        return default

    if isinstance(coluna, int):
        v = linha.iloc[coluna]
    else:
        v = linha[coluna]

    if pd.isna(v):
        return default

    return str(v).strip()


def escapar(texto):
    return texto.replace("\\", "\\\\").replace('"', '\\"')


linhas = []

linhas.append("let gifts = [\n")

for _, linha in df.iterrows():

    nome = escapar(valor(linha, COL_NOME))
    descricao = escapar(valor(linha, COL_DESCRICAO))
    imagem = escapar(valor(linha, COL_IMAGEM))
    link_cartao = escapar(valor(linha, COL_LINK_CARTAO))

    preco = valor(linha, COL_PRECO)

    try:
        preco = f"{float(preco):.2f}"
    except:
        pass

    linhas.append("  {\n")
    linhas.append(f'    nome: "{nome}",\n')
    linhas.append(f'    descricao: "{descricao}",\n')
    linhas.append(f'    preco: "{preco}",\n')
    linhas.append(f'    imagem: "{imagem}",\n')
    linhas.append(f'    link_cartao: "{link_cartao}",\n')
    linhas.append("  },\n")

linhas.append("];")


with open("gifts.js", "w", encoding="utf-8") as f:
    f.writelines(linhas)

print("Arquivo gifts.js criado!")
