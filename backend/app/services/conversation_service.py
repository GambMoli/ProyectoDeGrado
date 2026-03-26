from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.conversation import Conversation
from app.models.exercise import Exercise
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.chat import ChatRequest, ChatResponse, ExerciseOut, ExerciseResolutionOut, MessageOut
from app.schemas.conversation import ConversationDetail, ConversationSummary
from app.schemas.enums import ChatMode, ExerciseStatus, MessageRole, MessageStatus, SourceType
from app.services.explanation_service import ExplanationService
from app.services.math_parser_service import MathParserError, MathParserService
from app.services.ocr_service import OCRService
from app.services.practice_service import PracticeService
from app.services.sympy_solver_service import SolverError, SymPySolverService
from app.services.topic_explanation_service import TopicExplanationService
from app.services.tutor_agent_service import TutorAgentService


class ConversationService:
    def __init__(
        self,
        *,
        repository: ConversationRepository,
        parser_service: MathParserService,
        solver_service: SymPySolverService,
        explanation_service: ExplanationService,
        ocr_service: OCRService,
        practice_service: PracticeService,
        tutor_agent_service: TutorAgentService,
        topic_explanation_service: TopicExplanationService,
    ) -> None:
        self.repository = repository
        self.parser_service = parser_service
        self.solver_service = solver_service
        self.explanation_service = explanation_service
        self.ocr_service = ocr_service
        self.practice_service = practice_service
        self.tutor_agent_service = tutor_agent_service
        self.topic_explanation_service = topic_explanation_service
        self.settings = get_settings()

    def process_text_message(self, *, db: Session, payload: ChatRequest) -> ChatResponse:
        try:
            user = self.repository.get_or_create_user(db, payload.user_id)
            conversation = self.repository.get_or_create_conversation(
                db,
                user_id=user.id,
                conversation_id=payload.conversation_id,
                title_hint=payload.message,
            )
            user_message = self.repository.create_message(
                db,
                conversation_id=conversation.id,
                role=MessageRole.USER.value,
                content=payload.message,
                source_type=SourceType.TEXT.value,
                status=MessageStatus.RECEIVED.value,
            )

            conversation_context = self._build_recent_context(
                conversation=conversation,
                current_message_id=user_message.id,
            )
            if payload.mode == ChatMode.THEORY:
                decision_action = "answer_theory"
            elif payload.mode == ChatMode.EXERCISE:
                decision_action = "solve_exercise"
            else:
                decision = self.tutor_agent_service.decide(
                    message=payload.message,
                    conversation_context=conversation_context,
                    agent_state=conversation.agent_state,
                )
                decision_action = decision.action

            if decision_action == "generate_practice":
                response = self._generate_practice(
                    db=db,
                    user_id=user.id,
                    conversation=conversation,
                    user_message=user_message,
                    raw_input=payload.message,
                )
            elif decision_action == "grade_practice":
                response = self._grade_practice(
                    db=db,
                    user_id=user.id,
                    conversation=conversation,
                    user_message=user_message,
                    raw_input=payload.message,
                )
            elif decision_action in {"answer_theory", "ask_clarification"}:
                response = self._answer_theory(
                    db=db,
                    user_id=user.id,
                    conversation=conversation,
                    user_message=user_message,
                    raw_input=payload.message,
                    conversation_context=conversation_context,
                )
            else:
                response = self._solve_and_respond(
                    db=db,
                    user_id=user.id,
                    conversation=conversation,
                    user_message=user_message,
                    source_type=SourceType.TEXT,
                    raw_input=payload.message,
                    ocr_text=None,
                )
            db.commit()
            return response
        except LookupError as exc:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except HTTPException:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    def process_image_message(
        self,
        *,
        db: Session,
        image_bytes: bytes,
        filename: str,
        content_type: str,
        user_id: str | None,
        conversation_id: str | None,
        prompt: str | None,
    ) -> ChatResponse:
        if len(image_bytes) > self.settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"La imagen supera el maximo de {self.settings.max_upload_size_mb} MB.",
            )

        try:
            user = self.repository.get_or_create_user(db, user_id)
            conversation = self.repository.get_or_create_conversation(
                db,
                user_id=user.id,
                conversation_id=conversation_id,
                title_hint=prompt or filename,
            )
            message_content = prompt.strip() if prompt else f"Imagen subida: {filename}"
            user_message = self.repository.create_message(
                db,
                conversation_id=conversation.id,
                role=MessageRole.USER.value,
                content=message_content,
                source_type=SourceType.IMAGE.value,
                status=MessageStatus.RECEIVED.value,
            )
            exercise = self.repository.create_exercise(
                db,
                conversation_id=conversation.id,
                user_message_id=user_message.id,
                source_type=SourceType.IMAGE.value,
                raw_input=prompt.strip() if prompt else message_content,
            )
            user_message.submitted_exercise = exercise

            ocr_result = self.ocr_service.extract_text(
                image_bytes=image_bytes,
                filename=filename,
                content_type=content_type,
            )
            exercise.ocr_text = ocr_result.text or ocr_result.raw_text

            if not ocr_result.success or not ocr_result.text:
                assistant_message = self.repository.create_message(
                    db,
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT.value,
                    content=ocr_result.error_message
                    or "No pude extraer el ejercicio de la imagen. Intenta con otra foto o escribe el ejercicio manualmente.",
                    source_type=SourceType.IMAGE.value,
                    status=MessageStatus.NEEDS_CLARIFICATION.value,
                    error_message=ocr_result.error_message,
                )
                exercise.status = ExerciseStatus.OCR_FAILED.value
                exercise.error_message = (
                    ocr_result.error_message
                    or "No se pudo extraer texto matematico desde la imagen."
                )
                exercise.assistant_message = assistant_message
                self.repository.touch_conversation(
                    db,
                    conversation,
                    summary=assistant_message.content,
                    title_hint=prompt or filename,
                )
                db.commit()
                return ChatResponse(
                    user_id=user.id,
                    conversation_id=conversation.id,
                    user_message=self._build_message_out(user_message),
                    assistant_message=self._build_message_out(assistant_message),
                )

            combined_input = "\n".join(
                part for part in [prompt, ocr_result.text] if part and part.strip()
            )
            exercise.raw_input = combined_input
            response = self._solve_and_respond(
                db=db,
                user_id=user.id,
                conversation=conversation,
                user_message=user_message,
                source_type=SourceType.IMAGE,
                raw_input=combined_input,
                ocr_text=ocr_result.text,
                existing_exercise=exercise,
            )
            db.commit()
            return response
        except LookupError as exc:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except HTTPException:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

    def list_conversations(self, *, db: Session, user_id: str | None) -> list[ConversationSummary]:
        conversations = self.repository.list_conversations(db, user_id)
        return [self._build_conversation_summary(item) for item in conversations]

    def get_conversation(
        self,
        *,
        db: Session,
        conversation_id: str,
        user_id: str | None,
    ) -> ConversationDetail:
        conversation = self.repository.get_conversation(db, conversation_id, user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontro la conversacion solicitada.",
            )
        return self._build_conversation_detail(conversation)

    def count_knowledge_documents(self) -> int:
        return self.topic_explanation_service.knowledge_base_service.count_documents()

    def _answer_theory(
        self,
        *,
        db: Session,
        user_id: str,
        conversation: Conversation,
        user_message: Message,
        raw_input: str,
        conversation_context: list[str],
    ) -> ChatResponse:
        result = self.topic_explanation_service.answer(
            raw_input,
            conversation_context=conversation_context,
        )
        status_value = (
            MessageStatus.NEEDS_CLARIFICATION.value
            if result.source == "knowledge_fallback"
            else MessageStatus.SOLVED.value
        )
        assistant_message = self.repository.create_message(
            db,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content=result.text,
            source_type=SourceType.TEXT.value,
            status=status_value,
            error_message=None if status_value == MessageStatus.SOLVED.value else result.text,
        )
        summary = result.references[0].document.topic.replace("_", " ") if result.references else raw_input
        self.repository.touch_conversation(
            db,
            conversation,
            summary=summary,
            title_hint=raw_input,
        )
        return ChatResponse(
            user_id=user_id,
            conversation_id=conversation.id,
            user_message=self._build_message_out(user_message),
            assistant_message=self._build_message_out(assistant_message),
        )

    def _generate_practice(
        self,
        *,
        db: Session,
        user_id: str,
        conversation: Conversation,
        user_message: Message,
        raw_input: str,
    ) -> ChatResponse:
        generated = self.practice_service.generate_practice(
            request_text=raw_input,
            current_state=conversation.agent_state,
        )
        assistant_message = self.repository.create_message(
            db,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content=generated.text,
            source_type=SourceType.TEXT.value,
            status=MessageStatus.SOLVED.value,
        )
        self.repository.touch_conversation(
            db,
            conversation,
            summary="practica guiada",
            title_hint=raw_input,
            agent_state=generated.state,
        )
        return ChatResponse(
            user_id=user_id,
            conversation_id=conversation.id,
            user_message=self._build_message_out(user_message),
            assistant_message=self._build_message_out(assistant_message),
        )

    def _grade_practice(
        self,
        *,
        db: Session,
        user_id: str,
        conversation: Conversation,
        user_message: Message,
        raw_input: str,
    ) -> ChatResponse:
        pending_practice = dict(conversation.agent_state or {}).get("pending_practice")
        if not pending_practice:
            return self._answer_theory(
                db=db,
                user_id=user_id,
                conversation=conversation,
                user_message=user_message,
                raw_input=raw_input,
                conversation_context=self._build_recent_context(
                    conversation=conversation,
                    current_message_id=user_message.id,
                ),
            )

        graded = self.practice_service.grade_attempt(
            pending_practice=pending_practice,
            student_message=raw_input,
        )
        assistant_message = self.repository.create_message(
            db,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content=graded.text,
            source_type=SourceType.TEXT.value,
            status=MessageStatus.SOLVED.value if graded.is_correct else MessageStatus.NEEDS_CLARIFICATION.value,
            error_message=None if graded.is_correct else graded.text,
        )
        self.repository.touch_conversation(
            db,
            conversation,
            summary="practica corregida" if graded.is_correct else "practica en curso",
            title_hint=raw_input,
            agent_state=graded.next_state,
        )
        return ChatResponse(
            user_id=user_id,
            conversation_id=conversation.id,
            user_message=self._build_message_out(user_message),
            assistant_message=self._build_message_out(assistant_message),
        )

    def _solve_and_respond(
        self,
        *,
        db: Session,
        user_id: str,
        conversation: Conversation,
        user_message: Message,
        source_type: SourceType,
        raw_input: str,
        ocr_text: str | None,
        existing_exercise: Exercise | None = None,
    ) -> ChatResponse:
        exercise = existing_exercise
        if exercise:
            user_message.submitted_exercise = exercise

        try:
            parsed = self.parser_service.parse(raw_input)
        except MathParserError as exc:
            if (
                source_type == SourceType.TEXT
                and exc.code in {"no_clear_exercise", "invalid_expression"}
            ):
                return self._answer_theory(
                    db=db,
                    user_id=user_id,
                    conversation=conversation,
                    user_message=user_message,
                    raw_input=raw_input,
                    conversation_context=self._build_recent_context(
                        conversation=conversation,
                        current_message_id=user_message.id,
                    ),
                )

            exercise = exercise or self.repository.create_exercise(
                db,
                conversation_id=conversation.id,
                user_message_id=user_message.id,
                source_type=source_type.value,
                raw_input=raw_input,
                ocr_text=ocr_text,
            )
            user_message.submitted_exercise = exercise
            exercise.status = ExerciseStatus.PARSE_FAILED.value
            exercise.error_message = exc.user_message
            assistant_message = self.repository.create_message(
                db,
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT.value,
                content=exc.user_message,
                source_type=source_type.value,
                status=MessageStatus.NEEDS_CLARIFICATION.value,
                error_message=exc.user_message,
            )
            exercise.assistant_message = assistant_message
            self.repository.touch_conversation(
                db,
                conversation,
                summary=assistant_message.content,
                title_hint=raw_input,
            )
            return ChatResponse(
                user_id=user_id,
                conversation_id=conversation.id,
                user_message=self._build_message_out(user_message),
                assistant_message=self._build_message_out(assistant_message),
            )

        exercise = exercise or self.repository.create_exercise(
            db,
            conversation_id=conversation.id,
            user_message_id=user_message.id,
            source_type=source_type.value,
            raw_input=raw_input,
            ocr_text=ocr_text,
        )
        user_message.submitted_exercise = exercise
        exercise.detected_problem_type = parsed.problem_type.value
        exercise.extracted_expression = parsed.expression
        exercise.variable = parsed.variable
        exercise.limit_point = parsed.limit_point
        exercise.parse_notes = parsed.notes

        try:
            solved = self.solver_service.solve(parsed)
        except SolverError as exc:
            exercise.status = ExerciseStatus.SOLVER_FAILED.value
            exercise.error_message = exc.user_message
            assistant_message = self.repository.create_message(
                db,
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT.value,
                content=exc.user_message,
                source_type=source_type.value,
                status=MessageStatus.ERROR.value,
                error_message=exc.user_message,
            )
            exercise.assistant_message = assistant_message
            self.repository.touch_conversation(
                db,
                conversation,
                summary=assistant_message.content,
                title_hint=parsed.expression,
            )
            return ChatResponse(
                user_id=user_id,
                conversation_id=conversation.id,
                user_message=self._build_message_out(user_message),
                assistant_message=self._build_message_out(assistant_message),
            )

        explanation = self.explanation_service.generate(parsed=parsed, solved=solved)
        assistant_message = self.repository.create_message(
            db,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content=explanation.text,
            source_type=source_type.value,
            status=MessageStatus.SOLVED.value,
        )
        exercise.status = ExerciseStatus.SOLVED.value
        exercise.assistant_message = assistant_message
        exercise.error_message = None
        solved_record = self.repository.create_solved_exercise(
            db,
            exercise_id=exercise.id,
            sympy_input=solved.sympy_input,
            final_result=solved.final_result,
            steps=solved.steps,
            explanation_text=explanation.text,
            explanation_source=explanation.source,
        )
        exercise.solved_exercise = solved_record
        self.repository.touch_conversation(
            db,
            conversation,
            summary=solved.final_result,
            title_hint=parsed.expression,
        )
        return ChatResponse(
            user_id=user_id,
            conversation_id=conversation.id,
            user_message=self._build_message_out(user_message),
            assistant_message=self._build_message_out(assistant_message),
        )

    def _build_conversation_summary(self, conversation: Conversation) -> ConversationSummary:
        last_message = conversation.messages[-1] if conversation.messages else None
        return ConversationSummary(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            summary=conversation.summary,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            last_message_preview=last_message.content[:160] if last_message else None,
            message_count=len(conversation.messages),
        )

    def _build_conversation_detail(self, conversation: Conversation) -> ConversationDetail:
        return ConversationDetail(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            summary=conversation.summary,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[self._build_message_out(message) for message in conversation.messages],
        )

    def _build_message_out(self, message: Message) -> MessageOut:
        exercise = message.resolved_exercise or message.submitted_exercise
        return MessageOut(
            id=message.id,
            role=message.role,
            content=message.content,
            source_type=message.source_type,
            status=message.status,
            error_message=message.error_message,
            created_at=message.created_at,
            exercise=self._build_exercise_out(exercise),
        )

    @staticmethod
    def _build_recent_context(
        *,
        conversation: Conversation,
        current_message_id: str,
        limit: int = 4,
    ) -> list[str]:
        recent_messages = [
            message
            for message in conversation.messages
            if message.id != current_message_id
        ][-limit:]
        return [
            f"{message.role}: {message.content.strip()}"
            for message in recent_messages
            if message.content and message.content.strip()
        ]

    @staticmethod
    def _build_exercise_out(exercise: Exercise | None) -> ExerciseOut | None:
        if not exercise:
            return None

        resolution = None
        if exercise.solved_exercise:
            resolution = ExerciseResolutionOut(
                sympy_input=exercise.solved_exercise.sympy_input,
                final_result=exercise.solved_exercise.final_result,
                steps=exercise.solved_exercise.steps_json,
                explanation=exercise.solved_exercise.explanation_text,
                explanation_source=exercise.solved_exercise.explanation_source,
            )

        return ExerciseOut(
            id=exercise.id,
            source_type=exercise.source_type,
            raw_input=exercise.raw_input,
            ocr_text=exercise.ocr_text,
            detected_problem_type=exercise.detected_problem_type,
            extracted_expression=exercise.extracted_expression,
            variable=exercise.variable,
            limit_point=exercise.limit_point,
            parse_notes=exercise.parse_notes or [],
            status=exercise.status,
            error_message=exercise.error_message,
            resolution=resolution,
        )
