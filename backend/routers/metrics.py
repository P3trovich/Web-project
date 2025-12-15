from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from monitoring.metrics_export import save_metrics_to_json

router = APIRouter()

@router.get("/metrics")
async def metrics():
    """Эндпоинт для Prometheus"""
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )

@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@router.get("/metrics/export")
def export_metrics():
    """Сохраняет текущие метрики в JSON файл и возвращает их"""
    # Получаем метрики в текстовом формате
    metrics_text = generate_latest().decode('utf-8')
    
    # Сохраняем в файл
    saved_data = save_metrics_to_json(metrics_text)
    
    return saved_data