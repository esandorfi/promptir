"""LLM inference endpoints."""

import time
from fastapi import APIRouter, HTTPException, Depends
from openai import OpenAI, OpenAIError

from ..config import Settings, get_settings
from ..schemas import InferenceRequest, InferenceResponse, ModelsResponse

router = APIRouter()

# Cost per 1M tokens (input/output) for common models
MODEL_COSTS = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-4": (30.00, 60.00),
    "gpt-3.5-turbo": (0.50, 1.50),
    "claude-3-5-sonnet-20241022": (3.00, 15.00),
    "claude-3-5-haiku-20241022": (0.25, 1.25),
    "claude-3-opus-20240229": (15.00, 75.00),
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float | None:
    """Estimate cost for a model and token counts."""
    if model not in MODEL_COSTS:
        # Try partial match
        for key in MODEL_COSTS:
            if key in model:
                model = key
                break
        else:
            return None

    input_cost, output_cost = MODEL_COSTS[model]
    return (input_tokens * input_cost + output_tokens * output_cost) / 1_000_000


@router.get("/api/infer/models", response_model=ModelsResponse)
def list_models(settings: Settings = Depends(get_settings)) -> ModelsResponse:
    """List available models."""
    return ModelsResponse(models=settings.available_models)


@router.post("/api/infer", response_model=InferenceResponse)
def run_inference(
    request: InferenceRequest, settings: Settings = Depends(get_settings)
) -> InferenceResponse:
    """Run LLM inference using OpenAI-compatible API."""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY or PROMPTIR_OPENAI_API_KEY not configured",
        )

    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    start = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    except OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"LLM API error: {str(e)}")

    latency_ms = int((time.perf_counter() - start) * 1000)

    usage = response.usage
    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = usage.completion_tokens if usage else 0

    content = response.choices[0].message.content or ""

    return InferenceResponse(
        content=content,
        model=response.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost_estimate=estimate_cost(request.model, input_tokens, output_tokens),
    )
