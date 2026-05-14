from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.utils.security import expires_in_hours, hash_password, verify_password


class TestHashPassword:
    class TestNormal:
        def test_produce_formato_pbkdf2_sha256(self) -> None:
            hashed = hash_password("MiClave123!")
            parts = hashed.split("$")
            assert parts[0] == "pbkdf2_sha256"
            assert len(parts) == 4

        def test_hash_resultante_es_string(self) -> None:
            assert isinstance(hash_password("MiClave123!"), str)

        def test_iteraciones_por_defecto_en_hash(self) -> None:
            _, iterations, _, _ = hash_password("MiClave123!").split("$")
            assert iterations == "390000"

    class TestLimite: 
        def test_dos_llamadas_producen_hashes_distintos(self) -> None:
            assert hash_password("MiClave123!") != hash_password("MiClave123!")

        def test_password_vacio_produce_hash_valido(self) -> None:
            assert hash_password("").startswith("pbkdf2_sha256$")

        def test_password_muy_largo_produce_hash(self) -> None:
            assert hash_password("A" * 1000).startswith("pbkdf2_sha256$")

        def test_iteraciones_personalizadas_quedan_en_hash(self) -> None:
            _, iterations, _, _ = hash_password("clave", iterations=100).split("$")
            assert iterations == "100"

    class TestError:
        def test_password_con_caracteres_unicode_no_lanza_excepcion(self) -> None:
            assert hash_password("Clavé_ñ_123!").startswith("pbkdf2_sha256$")


class TestVerifyPassword:
    class TestNormal:
        def test_verifica_password_correcto(self) -> None:
            hashed = hash_password("Correcto123!")
            assert verify_password("Correcto123!", hashed) is True

        def test_rechaza_password_incorrecto(self) -> None:
            hashed = hash_password("Correcto123!")
            assert verify_password("Incorrecto999!", hashed) is False

        def test_verifica_password_con_caracteres_especiales(self) -> None:
            hashed = hash_password("P@$$w0rd!#")
            assert verify_password("P@$$w0rd!#", hashed) is True

    class TestLimite:
        def test_es_sensible_a_mayusculas(self) -> None:
            assert verify_password("password1!", hash_password("Password1!")) is False

        def test_rechaza_password_vacio_contra_hash_real(self) -> None:
            assert verify_password("", hash_password("AlgunaClave1!")) is False

        def test_verifica_password_vacio_hasheado(self) -> None:
            assert verify_password("", hash_password("")) is True

    class TestError:
        def test_retorna_false_para_hash_none(self) -> None:
            assert verify_password("cualquier", None) is False

        def test_retorna_false_para_hash_vacio(self) -> None:
            assert verify_password("cualquier", "") is False

        def test_retorna_false_para_hash_malformado(self) -> None:
            assert verify_password("cualquier", "estono$esunhash") is False

        def test_retorna_false_para_algoritmo_desconocido(self) -> None:
            assert verify_password("cualquier", "md5$1000$salt$digest") is False


class TestExpiresInHours:
    class TestNormal:
        def test_retorna_datetime_en_el_futuro(self) -> None:
            assert expires_in_hours(1) > datetime.now(timezone.utc)

        def test_agrega_horas_correctas(self) -> None:
            before = datetime.now(timezone.utc)
            future = expires_in_hours(5)
            after = datetime.now(timezone.utc)
            assert before + timedelta(hours=5) <= future <= after + timedelta(hours=5)

        def test_retorna_datetime_con_timezone_utc(self) -> None:
            assert expires_in_hours(1).tzinfo is not None

    class TestLimite:
        def test_cero_horas_retorna_tiempo_cercano_a_ahora(self) -> None:
            before = datetime.now(timezone.utc)
            result = expires_in_hours(0)
            after = datetime.now(timezone.utc)
            assert before <= result <= after

        def test_valor_grande_de_horas(self) -> None:
            assert expires_in_hours(8760) > datetime.now(timezone.utc) + timedelta(days=364)

    class TestError:
        def test_horas_negativas_retorna_fecha_en_el_pasado(self) -> None:
            assert expires_in_hours(-1) < datetime.now(timezone.utc)
