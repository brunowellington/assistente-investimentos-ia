# Assistente de Investimentos com IA

MVP educacional que recebe dados de um investidor por HTTP, valida o perfil informado, consulta cotações de mercado, calcula indicadores simples em Python e gera um relatório textual. A automação pode ser orquestrada pelo **n8n** e enviada por e-mail quando as credenciais forem configuradas.

> **Aviso importante:** projeto demonstrativo e educacional. Não é consultoria financeira, não prevê rentabilidade e não deve ser usado como recomendação real de compra ou venda. Os resultados dependem da qualidade e atualidade das fontes. Não envie dados pessoais ou financeiros sensíveis para ambientes de teste.

## Funcionalidades

- Webhook HTTP com validação de entrada.
- Perfis `conservador`, `moderado` e `arrojado`.
- Consulta opcional de cotações via Yahoo Finance (`yfinance`).
- Análise descritiva e relatório em JSON.
- Geração opcional de texto com um LLM (OpenAI ou Gemini).
- Modelo de e-mail HTML.
- Registro de auditoria em JSON Lines.
- Workflow de exemplo para importar no n8n.

## Arquitetura

```text
Cliente / formulário
        |
        v
Webhook n8n (ou API FastAPI)
        |
        v
Validação e análise Python
        |
        +------> API de mercado (opcional)
        |
        +------> LLM (opcional; texto explicativo)
        |
        v
Relatório JSON + log de auditoria
        |
        v
E-mail (configuração opcional no n8n)
```

## Estrutura

```text
assistente-investimentos-ia/
├── app/
│   ├── main.py
│   ├── analyzer.py
│   ├── market_data.py
│   ├── report.py
│   └── audit.py
├── n8n/
│   └── workflow-exemplo.json
├── examples/
│   └── request.json
├── tests/
│   └── test_analyzer.py
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

## 1. Executar localmente

Requisitos: Python 3.11 ou superior.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

A API estará em `http://127.0.0.1:8000`. Documentação interativa: `http://127.0.0.1:8000/docs`.

Teste:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d @examples/request.json
```

## 2. Exemplo de entrada

```json
{
  "nome": "Marinaldo",
  "perfil": "moderado",
  "capital": 50000,
  "email": "cliente@example.com",
  "ativos": ["PETR4.SA", "VALE3.SA"]
}
```

Use somente dados fictícios durante os testes. O campo `ativos` é opcional e contém símbolos de mercado para consulta demonstrativa.

## 3. Configuração de IA (opcional)

Copie `.env.example` para `.env` e configure **apenas um** provedor:

- OpenAI: `LLM_PROVIDER=openai` e `OPENAI_API_KEY=...`
- Gemini: `LLM_PROVIDER=gemini` e `GEMINI_API_KEY=...`
- Sem LLM: `LLM_PROVIDER=none`

A IA é usada somente para redigir uma explicação baseada nos dados calculados. Ela não deve inventar cotações nem substituir validação humana. Nunca coloque chaves de API no GitHub.

## 4. n8n

O arquivo `n8n/workflow-exemplo.json` é um ponto de partida para importar no n8n. Configure o webhook e a URL da API de análise (por padrão `http://host.docker.internal:8000/analyze` quando o n8n roda em Docker no mesmo computador). Em Linux, `host.docker.internal` pode exigir configuração extra; em produção, use uma URL privada alcançável pela instância n8n.

Fluxo sugerido:
1. **Webhook** (`POST /investimentos`) recebe o JSON.
2. **HTTP Request** encaminha o corpo para `/analyze`.
3. **Respond to Webhook** devolve o resultado.
4. Para e-mail, acrescente um nó Gmail/SMTP e mapeie `email`, `nome` e `relatorio_html` do retorno. Configure OAuth/credenciais diretamente no n8n; não as armazene no workflow exportado.

## 5. Testes

```bash
pytest -q
```

## 6. Docker

```bash
docker build -t assistente-investimentos-ia .
docker run --rm -p 8000:8000 --env-file .env assistente-investimentos-ia
```

## Segurança e limitações

- Valida os dados recebidos e limita o tamanho do capital.
- Não armazena chaves no código.
- O log local pode conter dados pessoais: mantenha-o fora do Git e aplique política de retenção.
- HTTPS, autenticação do webhook, limitação de requisições e gestão segura de segredos são necessários antes de publicar.
- Cotações externas podem estar atrasadas, indisponíveis ou sujeitas a limites.
- A distribuição por classe de ativo é apenas um exemplo didático, não uma carteira recomendada para uma pessoa real.
