from __future__ import annotations


def build_practice_prompt(*, exercise_text: str, hint: str) -> str:
    return (
        "Vamos con un ejercicio para practicar.\n\n"
        f"Ejercicio:\n{exercise_text}\n\n"
        "Intentalo por tu cuenta primero. Puedes escribirme solo el resultado o contarme el procedimiento.\n\n"
        f"Pista:\n{hint}"
    )


def build_correct_feedback(
    *,
    exercise_text: str,
    student_answer: str,
    expected_answer: str,
) -> str:
    return (
        f"Si, ese resultado esta correcto: {expected_answer}. "
        "Coincide con la respuesta esperada y la idea del ejercicio esta bien aplicada. "
        "Si quieres, ahora revisamos el procedimiento paso a paso o te propongo uno un poco mas retador."
    )


def fallback_incorrect_feedback(
    *,
    student_answer: str,
    expected_answer: str,
    hint: str,
    attempts: int,
) -> str:
    if attempts <= 1:
        return (
            "No coincide todavia con la respuesta esperada. "
            f"Revisa tu expresion y usa esta pista: {hint}"
        )
    return (
        "Aun hay un detalle por corregir. "
        f"La referencia esperada es {expected_answer}. "
        "Comparala con tu resultado y ajusta el paso donde te desviaste."
    )


def fallback_practice_context_explanation(
    *,
    exercise_text: str,
    expected_answer: str,
    hint: str,
) -> str:
    return (
        f"Vamos a desarrollar este ejercicio: {exercise_text} "
        f"La referencia correcta es {expected_answer}. "
        f"La idea clave para resolverlo es: {hint}"
    ).strip()
