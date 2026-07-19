from supabase import Client


def pesquisar_convidados(supabase: Client, evento_id: int, pesquisa: str):
    """
    Procura por qualquer convidado e retorna apenas
    um resultado por principal.
    """

    response = (
        supabase.table("pessoas")
        .select("principal")
        .eq("evento_id", evento_id)
        .ilike("nome", f"%{pesquisa}%")
        .execute()
    )

    principals = {item["principal"] for item in response.data if item["principal"]}

    return [{"principal": principal} for principal in sorted(principals)]


def buscar_convite(supabase: Client, evento_id: int, principal: str):
    """
    Retorna todas as pessoas pertencentes ao convite.
    """

    response = (
        supabase.table("pessoas")
        .select("*")
        .eq("evento_id", evento_id)
        .eq("principal", principal)
        .order("nome")
        .execute()
    )

    return response.data


def validar_telefone(supabase: Client, evento_id: int, principal: str, final: str):

    response = (
        supabase.table("pessoas")
        .select("telefone")
        .eq("evento_id", evento_id)
        .eq("principal", principal)
        .limit(1)
        .execute()
    )

    if not response.data:
        return False

    telefone = "".join(filter(str.isdigit, str(response.data[0]["telefone"])))

    return telefone.endswith(final)


def salvar_confirmacoes(
    supabase: Client, evento_id: int, principal: str, confirmacoes: list
):

    for item in confirmacoes:

        (
            supabase.table("pessoas")
            .update({"confirmacao": item["confirmacao"]})
            .eq("evento_id", evento_id)
            .eq("id", item["id"])
            .eq("principal", principal)
            .execute()
        )


def estatisticas(supabase: Client, evento_id: int):

    response = (
        supabase.table("pessoas")
        .select("confirmacao")
        .eq("evento_id", evento_id)
        .execute()
    )

    pessoas = response.data

    total = len(pessoas)

    confirmados = sum(1 for p in pessoas if p["confirmacao"] is True)

    recusados = sum(1 for p in pessoas if p["confirmacao"] is False)

    pendentes = sum(1 for p in pessoas if p["confirmacao"] is None)

    return {
        "total": total,
        "confirmados": confirmados,
        "recusados": recusados,
        "pendentes": pendentes,
    }


def convite_ja_confirmado(supabase: Client, evento_id: int, principal: str):

    response = (
        supabase.table("pessoas")
        .select("confirmacao")
        .eq("evento_id", evento_id)
        .eq("principal", principal)
        .execute()
    )

    return any(pessoa["confirmacao"] is not None for pessoa in response.data)


def buscar_evento_id(supabase: Client, tag: str) -> int:
    """
    Retorna o ID do evento a partir da tag.
    Ex.: 'joao-maria' -> 1
    """

    response = supabase.table("eventos").select("id").eq("tag", tag).limit(1).execute()

    if not response.data:
        raise ValueError(f"Evento '{tag}' não encontrado.")

    return response.data[0]["id"]
