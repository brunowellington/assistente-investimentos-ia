import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.analyzer import analyze_profile, summarize_market
from app.audit import log_event
from app.market_data import fetch_quotes
from app.report import generate_ai_summary, make_report_html

load_dotenv()

class InvestorRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    perfil: str
    capital: float = Field(gt=0, le=100_000_000)
    email: EmailStr
    ativos: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("perfil")
    @classmethod
    def validate_profile(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in {"conservador", "moderado", "arrojado"}:
            raise ValueError("perfil deve ser conservador, moderado ou arrojado")
        return value

    @field_validator("ativos")
    @classmethod
    def validate_symbols(cls, values: list[str]) -> list[str]:
        cleaned = []
        for value in values:
            symbol = value.strip().upper()
            if not symbol or len(symbol) > 20 or not all(c.isalnum() or c in ".-^=" for c in symbol):
                raise ValueError("Símbolo de ativo inválido.")
            cleaned.append(symbol)
        return cleaned

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Assistente de Investimentos com IA",
    description="MVP educacional para análise demonstrativa e geração de relatório.",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
def root():
    return {"projeto": app.title, "status": "online", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(request: InvestorRequest):
    try:
        analysis = analyze_profile(request.perfil, request.capital)
        quotes_raw = []
        if os.getenv("ENABLE_MARKET_DATA", "false").lower() == "true":
            quotes_raw = fetch_quotes(request.ativos)
        market = summarize_market(quotes_raw)
        base = {
            "nome": request.nome,
            "perfil": request.perfil,
            "capital": request.capital,
            "analise": analysis,
            "mercado": market,
        }
        ai_summary = generate_ai_summary(base)
        report_html = make_report_html(request.nome, request.perfil, analysis, quotes_raw, ai_summary)
        audit_id = log_event("analysis_completed", {
            "perfil": request.perfil,
            "capital": request.capital,
            "symbols": request.ativos,
            "market_data_enabled": os.getenv("ENABLE_MARKET_DATA", "false").lower() == "true",
        })
        return {
            "status": "success",
            "audit_id": audit_id,
            "nome": request.nome,
            "email": str(request.email),
            "perfil": request.perfil,
            "capital": request.capital,
            "analise": analysis,
            "mercado": market,
            "resumo_ia": ai_summary,
            "relatorio_html": report_html,
            "aviso": "Demonstração educacional; não é recomendação financeira.",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        log_event("analysis_failed", {"error_type": type(exc).__name__})
        raise HTTPException(status_code=500, detail="Falha interna ao processar a análise.") from exc
