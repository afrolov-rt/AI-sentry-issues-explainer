import { useState, useEffect } from 'react';
import { Workspace, CreateWorkspaceRequest, UpdateWorkspaceRequest } from '../types';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const useWorkspace = () => {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();

  const fetchCurrentWorkspace = async () => {
    if (!isAuthenticated) return;
    
    try {
      setLoading(true);
      setError(null);
      const workspaceData = await apiService.getCurrentWorkspace();
      setWorkspace(workspaceData);
    } catch (err: any) {
      let errorMessage = 'Failed to fetch workspace';
      
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map((error: any) => error.msg || error).join(', ');
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const createWorkspace = async (workspaceData: CreateWorkspaceRequest): Promise<Workspace> => {
    try {
      setLoading(true);
      setError(null);
      const newWorkspace = await apiService.createWorkspace(workspaceData);
      setWorkspace(newWorkspace);
      return newWorkspace;
    } catch (err: any) {
      let errorMessage = 'Failed to create workspace';
      
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map((error: any) => error.msg || error).join(', ');
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateWorkspace = async (workspaceData: UpdateWorkspaceRequest): Promise<Workspace> => {
    try {
      setLoading(true);
      setError(null);
      const updatedWorkspace = await apiService.updateWorkspace(workspaceData);
      setWorkspace(updatedWorkspace);
      return updatedWorkspace;
    } catch (err: any) {
      let errorMessage = 'Failed to update workspace';
      
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map((error: any) => error.msg || error).join(', ');
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => {
    setError(null);
  };

  const refreshWorkspace = async () => {
    await fetchCurrentWorkspace();
  };

  useEffect(() => {
    fetchCurrentWorkspace();
  }, [isAuthenticated]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    workspace,
    loading,
    error,
    createWorkspace,
    updateWorkspace,
    fetchCurrentWorkspace,
    refreshWorkspace,
    clearError,
  };
};
