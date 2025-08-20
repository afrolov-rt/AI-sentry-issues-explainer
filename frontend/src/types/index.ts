export interface User {
  id: string;
  email: string;
  username: string;
  workspace_id: string;
  created_at: string;
  is_active: boolean;
}

export interface Workspace {
  id: string;
  name: string;
  description?: string;
  sentry_organization?: string;
  sentry_api_token?: string;
  sentry_test_dsn?: string;
  openai_api_key?: string;
  created_at: string;
  updated_at: string;
}

export interface SentryIssue {
  id: string;
  title: string;
  status: 'unresolved' | 'resolved' | 'ignored';
  level: 'error' | 'warning' | 'info' | 'debug';
  platform: string;
  culprit?: string;
  message: string;
  first_seen: string;
  last_seen: string;
  count: number;
  userCount: number;
  permalink: string;
  project_id: string;
  project_name: string;
  tags: Record<string, string>;
  metadata: Record<string, any>;
}

export interface ProcessedIssue {
  id: string;
  workspace_id: string;
  sentry_issue_id: string;
  sentry_issue_data: SentryIssue;
  ai_analysis?: AIAnalysis;
  technical_specification?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface AIAnalysis {
  summary: string;
  root_cause: string;
  impact_assessment: string;
  reproduction_steps: string[];
  suggested_fix: string;
  estimated_effort: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  tags: string[];
  similar_issues?: string[];
  confidence_score: number;
  token_usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface CreateWorkspaceRequest {
  name: string;
  description?: string;
}

export interface UpdateWorkspaceRequest {
  name?: string;
  description?: string;
  sentry_organization?: string;
  sentry_api_token?: string;
  openai_api_key?: string;
}

export interface ProcessIssueRequest {
  sentry_issue_id: string;
  generate_specification?: boolean;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  code?: string;
}
