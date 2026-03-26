export type ProblemType =
  | "derivative"
  | "integral"
  | "limit"
  | "simplification"
  | "equation"
  | "unknown";

export type MessageRole = "user" | "assistant" | "system";
export type SourceType = "text" | "image";
export type ChatMode = "auto" | "exercise" | "theory";
export type MessageStatus = "received" | "solved" | "needs_clarification" | "error";
export type ExerciseStatus = "received" | "ocr_failed" | "parse_failed" | "solved" | "solver_failed";

export interface ExerciseResolution {
  sympy_input: string;
  final_result: string;
  steps: string[];
  explanation: string;
  explanation_source: string;
}

export interface Exercise {
  id: string;
  source_type: SourceType;
  raw_input: string;
  ocr_text: string | null;
  detected_problem_type: ProblemType | null;
  extracted_expression: string | null;
  variable: string | null;
  limit_point: string | null;
  parse_notes: string[];
  status: ExerciseStatus;
  error_message: string | null;
  resolution: ExerciseResolution | null;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  source_type: SourceType | null;
  status: MessageStatus;
  error_message: string | null;
  created_at: string;
  exercise: Exercise | null;
}

export interface ChatRequest {
  user_id: string;
  conversation_id?: string | null;
  mode?: ChatMode;
  message: string;
}

export interface ChatResponse {
  user_id: string;
  conversation_id: string;
  user_message: Message;
  assistant_message: Message;
}

export interface ConversationSummary {
  id: string;
  user_id: string;
  title: string;
  summary: string | null;
  created_at: string;
  updated_at: string;
  last_message_preview: string | null;
  message_count: number;
}

export interface ConversationDetail {
  id: string;
  user_id: string;
  title: string;
  summary: string | null;
  created_at: string;
  updated_at: string;
  messages: Message[];
}
