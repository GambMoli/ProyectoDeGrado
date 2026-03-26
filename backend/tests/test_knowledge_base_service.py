from pathlib import Path

from app.services.knowledge_base_service import KnowledgeBaseService

DATASETS_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "datasets"


def test_search_finds_biseccion_topic() -> None:
    service = KnowledgeBaseService(DATASETS_DIR)

    results = service.search("Explicame el metodo de biseccion", limit=3)

    assert results
    assert results[0].document.course == "metodos_numericos"
    assert results[0].document.topic == "biseccion"


def test_search_finds_continuidad_topic() -> None:
    service = KnowledgeBaseService(DATASETS_DIR)

    results = service.search("Que es la continuidad de funciones en calculo 1", limit=3)

    assert results
    assert results[0].document.course == "calculo_1"
    assert results[0].document.topic == "continuidad_de_funciones"
