import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  User,
  Workspace,
  SentryIssue,
  ProcessedIssue,
  AuthTokens,
  LoginRequest,
  RegisterRequest,
  CreateWorkspaceRequest,
  UpdateWorkspaceRequest,
  ProcessIssueRequest,
} from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

  constructor() {
    this.api = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add token to requests
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle token expiration
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(credentials: LoginRequest): Promise<AuthTokens> {
    const response: AxiosResponse<AuthTokens> = await this.api.post('/auth/login', credentials);
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<AuthTokens> {
    const response: AxiosResponse<AuthTokens> = await this.api.post('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/auth/me');
    return response.data;
  }

  // Workspace endpoints
  async createWorkspace(workspaceData: CreateWorkspaceRequest): Promise<Workspace> {
    const response: AxiosResponse<Workspace> = await this.api.post('/workspaces/', workspaceData);
    return response.data;
  }

  async getCurrentWorkspace(): Promise<Workspace> {
    const response: AxiosResponse<Workspace> = await this.api.get('/workspaces/current');
    return response.data;
  }

  async updateWorkspace(workspaceData: UpdateWorkspaceRequest): Promise<Workspace> {
    const response: AxiosResponse<Workspace> = await this.api.put('/workspaces/current', workspaceData);
    return response.data;
  }

  async testSentryConnection(testData: { sentry_api_token: string; sentry_organization: string }): Promise<any> {
    const response: AxiosResponse<any> = await this.api.post('/workspaces/test-sentry', testData);
    return response.data;
  }

  // Sentry endpoints
  async getSentryProjects(): Promise<any[]> {
    const response: AxiosResponse<any[]> = await this.api.get('/issues/sentry/projects');
    return response.data;
  }

  async getSentryIssues(projectId?: string, status?: string): Promise<SentryIssue[]> {
    const params = new URLSearchParams();
    if (projectId) params.append('project_id', projectId);
    if (status) params.append('status', status);
    
    const response: AxiosResponse<SentryIssue[]> = await this.api.get(`/issues/sentry/issues?${params}`);
    return response.data;
  }

  // Issues processing endpoints
  async processIssue(issueData: ProcessIssueRequest): Promise<ProcessedIssue> {
    const response: AxiosResponse<ProcessedIssue> = await this.api.post('/issues/process', issueData);
    return response.data;
  }

  async getProcessedIssues(): Promise<ProcessedIssue[]> {
    const response: AxiosResponse<ProcessedIssue[]> = await this.api.get('/issues/processed');
    return response.data;
  }

  async getProcessedIssue(issueId: string): Promise<ProcessedIssue> {
    const response: AxiosResponse<ProcessedIssue> = await this.api.get(`/issues/processed/${issueId}`);
    return response.data;
  }

  async deleteProcessedIssue(issueId: string): Promise<void> {
    await this.api.delete(`/issues/processed/${issueId}`);
  }

  // Settings endpoints
  async getSettings(): Promise<any> {
    const response: AxiosResponse<any> = await this.api.get('/settings/');
    return response.data;
  }

  async updateSettings(settings: any): Promise<any> {
    const response: AxiosResponse<any> = await this.api.put('/settings/', settings);
    return response.data;
  }

  // Debug endpoints (if in development)
  async getDebugInfo(): Promise<any> {
    const response: AxiosResponse<any> = await this.api.get('/debug/info');
    return response.data;
  }

  async healthCheck(): Promise<any> {
    const response: AxiosResponse<any> = await this.api.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
