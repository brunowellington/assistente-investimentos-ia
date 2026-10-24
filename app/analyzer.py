from typing import Any

ALLOCATIONS = {
    "conservador": {"renda_fixa": 80, "acoes": 10, "fiis": 10},
    "moderado": {"renda_fixa": 50, "acoes": 40, "fiis": 10},
    "arrojado": {"renda_fixa": 20, "acoes": 60, "fiis": 20},
}

def analyze_profile(perfil: str, capital: float) -> dict[str, Any]:
    """Gera uma divisão ilustrativa para demonstração, não uma recomendação."""
    perfil = perfil.lower().strip()
    if perfil not in ALLOCATIONS:
        raise ValueError("Perfil deve ser conservador, moderado ou arrojado.")
    allocation = ALLOCATIONS[perfil]
    amounts = {key: round(capital * percent / 100, 2)
               for key, percent in allocation.items()}
    return {
        "perfil": perfil,
        "distribuicao_ilustrativa_percentual": allocation,
        "valores_ilustrativos": amounts,
        "observacao": (
            "Exemplo educacional de alocação. Não constitui recomendação "
            "personalizada nem considera objetivos, prazo, liquidez, impostos "
            "ou tolerância detalhada a perdas."
        ),
    }

def summarize_market(quotes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normaliza cotações e calcula variação percentual quando possível."""
    output = []
    for quote in quotes:
        previous = quote.get("previous_close")
        current = quote.get("price")
        change_pct = None
        if isinstance(previous, (int, float)) and previous:
            if isinstance(current, (int, float)):
                change_pct = round((current - previous) / previous * 100, 2)
        output.append({
            "symbol": quote.get("symbol"),
            "price": current,
            "previous_close": previous,
            "change_percent": change_pct,
            "currency": quote.get("currency"),
            "source": quote.get("source", "unknown"),
        })
    return output
