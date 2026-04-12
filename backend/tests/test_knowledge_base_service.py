from pathlib import Path

import pytest

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


def test_search_finds_gauss_seidel_topic() -> None:
    service = KnowledgeBaseService(DATASETS_DIR)

    results = service.search("Explicame gauss seidel para sistemas lineales", limit=3)

    assert results
    assert results[0].document.course == "metodos_numericos"
    assert results[0].document.topic == "gauss_seidel"


@pytest.mark.parametrize(
    ("query", "expected_topic"),
    [
        ("Que es crank nicolson", "crank_nicolson"),
        ("Explicame fft", "transformada_rapida_de_fourier"),
        ("Busco info sobre programacion lineal", "programacion_lineal"),
        ("Como funciona la busqueda por incrementos", "busqueda_por_incrementos"),
    ],
)
def test_search_finds_recent_chapra_topics(query: str, expected_topic: str) -> None:
    service = KnowledgeBaseService(DATASETS_DIR)

    results = service.search(query, limit=3)

    assert results
    assert results[0].document.course == "metodos_numericos"
    assert results[0].document.topic == expected_topic
