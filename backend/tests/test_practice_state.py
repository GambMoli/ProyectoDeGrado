from __future__ import annotations

from types import SimpleNamespace

from app.services.practice.state import keywords_from_references, snapshot_practice_context


def _make_reference(*tags: str) -> object:
    return SimpleNamespace(document=SimpleNamespace(tags=list(tags)))


class TestSnapshotPracticeContext:
    class TestNormal:
        def test_status_siempre_es_completed(self) -> None:
            assert snapshot_practice_context({"topic": "integral"})["status"] == "completed"

        def test_incluye_campos_del_contexto(self) -> None:
            ctx = {
                "topic": "derivative",
                "problem_type": "derivative",
                "expected_answer": "2*x",
                "hint": "Usa la regla de la potencia",
            }
            snap = snapshot_practice_context(ctx, last_outcome="correct")
            assert snap["topic"] == "derivative"
            assert snap["expected_answer"] == "2*x"
            assert snap["last_outcome"] == "correct"

        def test_keywords_y_history_son_listas(self) -> None:
            snap = snapshot_practice_context({"keywords": ["limite"]})
            assert isinstance(snap["keywords"], list)
            assert isinstance(snap["practice_history"], list)

        def test_last_outcome_por_defecto_es_completed(self) -> None:
            assert snapshot_practice_context({"topic": "limit"})["last_outcome"] == "completed"

    class TestLimite:
        def test_attempts_override_tiene_prioridad(self) -> None:
            assert snapshot_practice_context({"attempts": 1}, attempts=7)["attempts"] == 7

        def test_usa_attempts_del_contexto_si_no_hay_override(self) -> None:
            assert snapshot_practice_context({"attempts": 3})["attempts"] == 3

        def test_keywords_none_retorna_lista_vacia(self) -> None:
            assert snapshot_practice_context({"keywords": None})["keywords"] == []

        def test_history_none_retorna_lista_vacia(self) -> None:
            assert snapshot_practice_context({"practice_history": None})["practice_history"] == []

    class TestError:
        def test_contexto_vacio_no_lanza_excepcion(self) -> None:
            snap = snapshot_practice_context({})
            assert snap["status"] == "completed"
            assert snap["attempts"] == 0
            assert snap["keywords"] == []


class TestKeywordsFromReferences:
    class TestNormal:
        def test_retorna_keywords_de_referencias(self) -> None:
            result = keywords_from_references([_make_reference("integral", "derivada")])
            assert "integral" in result and "derivada" in result

        def test_preserva_orden_de_insercion(self) -> None:
            assert keywords_from_references([_make_reference("integral", "derivada", "limite")]) == [
                "integral", "derivada", "limite"
            ]

        def test_combina_tags_de_multiples_referencias(self) -> None:
            result = keywords_from_references([_make_reference("integral"), _make_reference("derivada")])
            assert "integral" in result and "derivada" in result

    class TestLimite:
        def test_deduplica_keywords_repetidos(self) -> None:
            refs = [_make_reference("integral", "derivada"), _make_reference("integral")]
            assert keywords_from_references(refs).count("integral") == 1

        def test_limita_resultado_a_seis_items(self) -> None:
            assert len(keywords_from_references([_make_reference("a", "b", "c", "d", "e", "f", "g")])) == 6

        def test_referencia_sin_tags_no_aporta_keywords(self) -> None:
            assert keywords_from_references([_make_reference(), _make_reference("derivada")]) == ["derivada"]

    class TestError:
        def test_lista_vacia_retorna_lista_vacia(self) -> None:
            assert keywords_from_references([]) == []
