from supabase import create_client
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("url")
key = os.getenv("key")

supabase = create_client(url, key)

# df = pd.read_excel("convidados.xlsx")

# df.columns = [
#     "nome",
#     "telefone",
#     "principal"
# ]

# df["confirmacao"] = None

# data = df.to_dict(orient="records")

# response = (
#     supabase
#     .table("pessoas")
#     .insert(data)
#     .execute()
# )

# print(response)


response = (
        supabase
        .table("pessoas")
        .select("confirmacao")
        .eq("principal", "Kalynka")
        .execute()
    )
print(any(
        pessoa["confirmacao"] is not None
        for pessoa in response.data
    ))