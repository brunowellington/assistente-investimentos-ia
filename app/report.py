import html
import os

def generate_ai_summary(payload: dict) -> str | None:
    provider = os.getenv("LLM_PROVIDER", "none").lower()
    facts = (
        f"Nome: {payload['nome']}; perfil declarado: {payload['perfil']}; "
        f"capital informado: R$ {payload['capital']:.2f}; "
        f"distribuição ilustrativa: {payload['analise']['distribuicao_ilustrativa_percentual']}; "
        f"cotações consultadas: {payload.get('mercado', [])}."
    )
    instruction = (
        "Escreva um resumo claro em português para um protótipo educacional de "
        "assistente financeiro. Descreva os dados fornecidos sem sugerir compra "
        "ou venda de ativos, sem prometer retorno e sem inventar informações. "
        "Inclua que não é aconselhamento financeiro. Dados: " + facts
    )
    try:
        if provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": instruction}],
                temperature=0.2,
            )
            return response.choices[0].message.content
        if provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
            return model.generate_content(instruction).text
    except Exception:
        return "Não foi possível gerar o resumo com IA. Consulte os dados estruturados do relatório."
    return None

def make_report_html(name: str, profile: str, analysis: dict, market: list[dict], ai_summary: str | None) -> str:
    safe_name = html.escape(name)
    safe_profile = html.escape(profile)
    rows = "".join(
        f"<tr><td>{html.escape(str(q.get('symbol', '-')))}</td>"
        f"<td>{html.escape(str(q.get('price', q.get('error', 'indisponível'))))}</td>"
        f"<td>{html.escape(str(q.get('change_percent', '-')))}</td></tr>"
        for q in market
    ) or "<tr><td colspan='3'>Nenhuma cotação consultada.</td></tr>"
    summary = html.escape(ai_summary or "Resumo de IA desativado; consulte os dados estruturados.")
    allocation = analysis["distribuicao_ilustrativa_percentual"]
    return f"""<!doctype html><html lang="pt-BR"><meta charset="utf-8">
    <body style="font-family:Arial,sans-serif;color:#202938;max-width:720px;margin:auto">
    <h1>Relatório demonstrativo de investimentos</h1>
    <p>Olá, {safe_name}. Este relatório é um exemplo educacional.</p>
    <h2>Perfil informado: {safe_profile}</h2>
    <ul><li>Renda fixa: {allocation['renda_fixa']}%</li>
    <li>Ações: {allocation['acoes']}%</li><li>FIIs: {allocation['fiis']}%</li></ul>
    <h2>Dados de mercado</h2><table border="1" cellpadding="8" cellspacing="0">
    <tr><th>Ativo</th><th>Preço</th><th>Variação (%)</th></tr>{rows}</table>
    <h2>Resumo</h2><p>{summary}</p>
    <hr><p><strong>Aviso:</strong> conteúdo exclusivamente educacional, não constitui
    recomendação de investimento, oferta, promessa de rentabilidade ou aconselhamento financeiro.
    Verifique fontes, custos, riscos e adequação antes de qualquer decisão.</p></body></html>"""
