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

export interface OcrResponse {
  success: boolean;
  ocr_text: string | null;
  error_message: string | null;
}

export interface ChatRequest {
  user_id?: string | null;
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

export type UserRole = "student" | "teacher";

export interface AuthUser {
  id: string;
  display_name: string;
  email: string;
  role: UserRole;
  is_anonymous: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: "bearer";
  user: AuthUser;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  display_name: string;
  email: string;
  password: string;
  role: UserRole;
  teacher_access_code?: string;
}

export interface ReportPeriod {
  start: string;
  end: string;
}

export interface ReportsOverview {
  period: ReportPeriod;
  active_students: number;
  total_queries: number;
  resolved_exercises: number;
  failed_exercises: number;
  ai_resolution_rate: number;
  avg_queries_per_active_student: number;
}

export interface StudentReportListItem {
  user_id: string;
  display_name: string;
  email: string | null;
  is_anonymous: boolean;
  conversation_count: number;
  message_count: number;
  exercise_count: number;
  last_activity_at: string | null;
}

export interface StudentReportSummary {
  user_id: string;
  display_name: string;
  email: string | null;
  is_anonymous: boolean;
  period: ReportPeriod;
  usage_frequency_days_per_week: number;
  total_queries: number;
  total_conversations: number;
  total_exercises: number;
  resolved_exercises: number;
  failed_exercises: number;
  ai_resolution_rate: number;
  activity_span_hours_estimate: number;
  first_activity_at: string | null;
  last_activity_at: string | null;
}

export interface StudentWeeklyActivityPoint {
  label: string;
  queries: number;
  exercises: number;
}

export interface StudentWeeklyActivity {
  user_id: string;
  period: ReportPeriod;
  series: StudentWeeklyActivityPoint[];
}

export interface TopicReportSummary {
  topic: "limit" | "derivative" | "integral" | "equation";
  label: string;
  questions_count: number;
  exercises_generated: number;
  active_students_ratio: number;
  interaction_level: "low" | "medium" | "high";
  questions_change_ratio: number | null;
  exercises_change_ratio: number | null;
}

export interface TopicTrendPoint {
  date: string;
  label: string;
  questions: number;
}

export interface TopicTrend {
  topic: "limit" | "derivative" | "integral" | "equation";
  label: string;
  period: ReportPeriod;
  series: TopicTrendPoint[];
}
