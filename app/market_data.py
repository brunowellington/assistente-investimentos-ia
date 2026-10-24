from typing import Any

def fetch_quotes(symbols: list[str]) -> list[dict[str, Any]]:
    """Consulta dados públicos via yfinance. Pode falhar ou retornar dados atrasados."""
    if not symbols:
        return []
    try:
        import yfinance as yf
    except ImportError:
        return [{"symbol": s, "error": "Instale yfinance para consultar o mercado."}
                for s in symbols]

    results = []
    for symbol in symbols[:10]:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price = info.get("lastPrice")
            previous = info.get("previousClose")
            currency = info.get("currency")
            results.append({
                "symbol": symbol,
                "price": float(price) if price is not None else None,
                "previous_close": float(previous) if previous is not None else None,
                "currency": currency,
                "source": "Yahoo Finance via yfinance",
                "disclaimer": "Pode haver atraso, indisponibilidade ou inconsistência.",
            })
        except Exception as exc:
            results.append({"symbol": symbol, "error": f"Consulta indisponível: {type(exc).__name__}"})
    return results
