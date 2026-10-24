from app.analyzer import analyze_profile, summarize_market

def test_allocation_percentages_sum_to_100():
    for profile in ("conservador", "moderado", "arrojado"):
        result = analyze_profile(profile, 1000)
        assert sum(result["distribuicao_ilustrativa_percentual"].values()) == 100

def test_moderate_allocation_amounts():
    result = analyze_profile("moderado", 50000)
    assert result["valores_ilustrativos"] == {
        "renda_fixa": 25000.0,
        "acoes": 20000.0,
        "fiis": 5000.0,
    }

def test_market_change():
    result = summarize_market([{
        "symbol": "TEST", "price": 110, "previous_close": 100, "currency": "BRL"
    }])
    assert result[0]["change_percent"] == 10.0
