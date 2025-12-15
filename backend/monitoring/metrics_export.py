# metrics_export.py
import json
from datetime import datetime
from pathlib import Path
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.parser import text_string_to_metric_families

def save_metrics_to_json(metrics_text: str, filename: str = "prometheus_metrics.json"):
    """Сохраняет метрики Prometheus в JSON файл"""
    
    metrics_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": []
    }
    
    # Парсим метрики из текстового формата Prometheus
    for family in text_string_to_metric_families(metrics_text):
        for sample in family.samples:
            metrics_data["metrics"].append({
                "name": sample.name,
                "labels": dict(sample.labels),
                "value": float(sample.value),
                "type": family.type
            })
    
    # Сохраняем в файл
    filepath = Path(filename)
    filepath.write_text(json.dumps(metrics_data, indent=2))
    
    return metrics_data