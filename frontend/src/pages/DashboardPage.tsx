import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Button,
  Chip,
} from '@mui/material';
import {
  BugReport as BugReportIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Error as ErrorIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material';
import { ProcessedIssue, SentryIssue } from '../types';
import { apiService } from '../services/api';
import { useWorkspace } from '../hooks/useWorkspace';

interface DashboardPageProps {
  onPageChange?: (page: string) => void;
}

const DashboardPage: React.FC<DashboardPageProps> = ({ onPageChange }) => {
  const [processedIssues, setProcessedIssues] = useState<ProcessedIssue[]>([]);
  const [sentryIssues, setSentryIssues] = useState<SentryIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyzingIssues, setAnalyzingIssues] = useState<Set<string>>(new Set());
  const [mounted, setMounted] = useState(false);
  const { workspace } = useWorkspace();

  useEffect(() => {
    // Задержка для предотвращения гидратации
    const timer = setTimeout(() => {
      setMounted(true);
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [workspace]); // eslint-disable-line react-hooks/exhaustive-deps

  const formatDate = (dateString: string | undefined): string => {
    if (!mounted || !dateString) return 'Unknown date';
    try {
      return new Date(dateString).toLocaleDateString('en-US');
    } catch {
      return 'Invalid date';
    }
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [processedData, sentryData] = await Promise.allSettled([
        apiService.getProcessedIssues(),
        workspace?.sentry_api_token ? apiService.getSentryIssues() : Promise.resolve([])
      ]);

      if (processedData.status === 'fulfilled') {
        setProcessedIssues(processedData.value);
      }

      if (sentryData.status === 'fulfilled') {
        setSentryIssues(sentryData.value);
      }

      if (processedData.status === 'rejected' && sentryData.status === 'rejected') {
        setError('Failed to load dashboard data');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeIssue = async (issueId: string) => {
    try {
      console.log('Analyzing issue with ID:', issueId);
      console.log('Full issue object for debugging:', sentryIssues.find(issue => issue.id === issueId));
      setAnalyzingIssues(prev => new Set(prev).add(issueId));
      
      const result = await apiService.analyzeIssue(issueId);
      console.log('Analysis result:', result);
      
      if (result.status === 'completed') {
        // Refresh the dashboard to show updated data
        await fetchDashboardData();
        console.log('Analysis completed:', result);
      } else if (result.status === 'analyzing') {
        console.log('Analysis started, please wait...');
        // You might want to show a notification here
      } else {
        console.error('Analysis failed');
      }
    } catch (err: any) {
      console.error('Failed to analyze issue:', err);
      console.error('Error details:', err.response?.data);
      setError(err.response?.data?.detail || 'Failed to analyze issue');
    } finally {
      setAnalyzingIssues(prev => {
        const newSet = new Set(prev);
        newSet.delete(issueId);
        return newSet;
      });
    }
  };

  const getStatusColor = (status: string | undefined) => {
    if (!status) return 'default';
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const stats = {
    totalProcessed: processedIssues?.length || 0,
    completed: processedIssues?.filter(issue => issue?.status === 'completed').length || 0,
    processing: processedIssues?.filter(issue => issue?.status === 'processing').length || 0,
    failed: processedIssues?.filter(issue => issue?.status === 'failed').length || 0,
    totalSentry: sentryIssues?.length || 0,
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
          <Button onClick={fetchDashboardData} sx={{ ml: 2 }}>
            Retry
          </Button>
        </Alert>
      )}

      {!workspace?.sentry_api_token && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Configure Sentry API token in workspace settings to load data
        </Alert>
      )}

      {/* Statistics Cards */}
      <Box display="flex" gap={3} flexWrap="wrap" sx={{ mb: 4 }}>
        <Box flex="1" minWidth="250px">
          <Card sx={{ 
            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
            color: 'white',
            border: 'none',
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="rgba(255,255,255,0.8)" gutterBottom variant="body2" sx={{ fontWeight: 500 }}>
                    Total Processed
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                    {stats.totalProcessed}
                  </Typography>
                </Box>
                <Box sx={{ 
                  backgroundColor: 'rgba(255,255,255,0.2)', 
                  borderRadius: '16px', 
                  p: 2,
                  backdropFilter: 'blur(10px)',
                }}>
                  <BugReportIcon sx={{ fontSize: 40 }} />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>

        <Box flex="1" minWidth="250px">
          <Card sx={{ 
            background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
            color: 'white',
            border: 'none',
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="rgba(255,255,255,0.8)" gutterBottom variant="body2" sx={{ fontWeight: 500 }}>
                    Completed
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                    {stats.completed}
                  </Typography>
                </Box>
                <Box sx={{ 
                  backgroundColor: 'rgba(255,255,255,0.2)', 
                  borderRadius: '16px', 
                  p: 2,
                  backdropFilter: 'blur(10px)',
                }}>
                  <CheckCircleIcon sx={{ fontSize: 40 }} />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>

        <Box flex="1" minWidth="250px">
          <Card sx={{ 
            background: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
            color: 'white',
            border: 'none',
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="rgba(255,255,255,0.8)" gutterBottom variant="body2" sx={{ fontWeight: 500 }}>
                    Processing
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                    {stats.processing}
                  </Typography>
                </Box>
                <Box sx={{ 
                  backgroundColor: 'rgba(255,255,255,0.2)', 
                  borderRadius: '16px', 
                  p: 2,
                  backdropFilter: 'blur(10px)',
                }}>
                  <ScheduleIcon sx={{ fontSize: 40 }} />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>

        <Box flex="1" minWidth="250px">
          <Card sx={{ 
            background: 'linear-gradient(135deg, #ef4444 0%, #f87171 100%)',
            color: 'white',
            border: 'none',
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="rgba(255,255,255,0.8)" gutterBottom variant="body2" sx={{ fontWeight: 500 }}>
                    Errors
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                    {stats.failed}
                  </Typography>
                </Box>
                <Box sx={{ 
                  backgroundColor: 'rgba(255,255,255,0.2)', 
                  borderRadius: '16px', 
                  p: 2,
                  backdropFilter: 'blur(10px)',
                }}>
                  <ErrorIcon sx={{ fontSize: 40 }} />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Recent Processed Issues */}
      <Box display="flex" gap={3} flexWrap="wrap">
        <Box flex="1" minWidth="400px">
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                📋 Recent Issues
              </Typography>
              {sentryIssues.length === 0 ? (
                <Box textAlign="center" py={4}>
                  <Typography color="textSecondary" sx={{ fontSize: '1.1rem' }}>
                    {workspace?.sentry_api_token ? 'No issues found' : 'Configure Sentry to view issues'}
                  </Typography>
                </Box>
              ) : (
                <Box>
                  {sentryIssues.slice(0, 5).filter(issue => issue && issue.id).map((issue) => (
                    <Box key={issue.id} sx={{ 
                      mb: 2, 
                      p: 3, 
                      border: '1px solid #e2e8f0', 
                      borderRadius: 3,
                      backgroundColor: '#fafafa',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        backgroundColor: '#f1f5f9',
                        transform: 'translateY(-1px)',
                        boxShadow: '0 4px 12px rgb(0 0 0 / 0.1)',
                      },
                    }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                        <Typography variant="subtitle2" noWrap sx={{ fontWeight: 600 }}>
                          {issue.title || 'No title'}
                        </Typography>
                        <Chip 
                          label={issue.level || 'unknown'} 
                          color="default"
                          size="small"
                          sx={{ fontWeight: 500 }}
                        />
                      </Box>
                      <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                        {issue.project_name || 'Unknown project'} • {formatDate(issue.last_seen)}
                      </Typography>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2" sx={{ color: '#64748b' }}>
                          Count: {issue.count || 0} • Users: {issue.userCount || 0}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Chip 
                            label={issue.status || 'unresolved'} 
                            size="small"
                            variant="outlined"
                            color="default"
                          />
                          <Button
                            variant="outlined"
                            size="small"
                            startIcon={analyzingIssues.has(issue.id) ? <CircularProgress size={16} /> : <PsychologyIcon />}
                            disabled={analyzingIssues.has(issue.id)}
                            sx={{ 
                              minWidth: 'auto',
                              px: 2,
                              borderColor: '#3b82f6',
                              color: '#3b82f6',
                              '&:hover': {
                                borderColor: '#2563eb',
                                backgroundColor: '#eff6ff'
                              },
                              '&:disabled': {
                                borderColor: '#d1d5db',
                                color: '#6b7280'
                              }
                            }}
                            onClick={() => handleAnalyzeIssue(issue.id)}
                          >
                            {analyzingIssues.has(issue.id) ? 'Analyzing...' : 'Analyze'}
                          </Button>
                        </Box>
                      </Box>
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>

        <Box flex="1" minWidth="400px">
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                🏢 Workspace Information
              </Typography>
              {workspace ? (
                <Box sx={{ 
                  p: 3, 
                  backgroundColor: '#f8fafc', 
                  borderRadius: 3,
                  border: '1px solid #e2e8f0',
                }}>
                  <Typography variant="body1" sx={{ mb: 2, fontWeight: 600, fontSize: '1.1rem' }}>
                    {workspace.name}
                  </Typography>
                  {workspace.description && (
                    <Typography variant="body2" sx={{ mb: 2, color: '#64748b' }}>
                      {workspace.description}
                    </Typography>
                  )}
                  
                  <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        Sentry Organization:
                      </Typography>
                      <Chip 
                        label={workspace.sentry_organization || 'Not configured'} 
                        size="small" 
                        color="default"
                        variant="outlined"
                      />
                    </Box>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        Sentry Token:
                      </Typography>
                      <Chip 
                        label={workspace.sentry_api_token ? 'Configured' : 'Not configured'} 
                        size="small" 
                        color="default"
                        variant="outlined"
                      />
                    </Box>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        OpenAI Key:
                      </Typography>
                      <Chip 
                        label={workspace.openai_api_key ? 'Configured' : 'Not configured'} 
                        size="small" 
                        color="default"
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                  
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 3, fontSize: '0.9rem' }}>
                    Created: {formatDate(workspace.created_at)}
                  </Typography>
                </Box>
              ) : (
                <Box textAlign="center" py={4}>
                  <Typography color="textSecondary">
                    Loading workspace...
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Recent Processed Issues Section */}
          <Card sx={{ mt: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  🔍 Recently Processed Issues
                </Typography>
                {onPageChange && (
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => onPageChange('analyses')}
                    sx={{ borderRadius: 2 }}
                  >
                    View All Analyses
                  </Button>
                )}
              </Box>
              {processedIssues.length === 0 ? (
                <Box textAlign="center" py={4}>
                  <Typography color="textSecondary" sx={{ fontSize: '1.1rem' }}>
                    No processed issues yet
                  </Typography>
                </Box>
              ) : (
                <Box>
                  {processedIssues.slice(0, 5).filter(issue => issue && issue.id).map((issue) => (
                    <Box key={issue.id} sx={{ 
                      mb: 2, 
                      p: 3, 
                      border: '1px solid #e2e8f0', 
                      borderRadius: 3,
                      backgroundColor: '#fafafa',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        backgroundColor: '#f1f5f9',
                        transform: 'translateY(-1px)',
                        boxShadow: '0 4px 12px rgb(0 0 0 / 0.1)',
                      },
                    }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                        <Typography variant="subtitle2" noWrap sx={{ fontWeight: 600 }}>
                          {issue.sentry_issue_data?.title || 'No title'}
                        </Typography>
                        <Chip 
                          label={issue.status || 'unknown'} 
                          color="default"
                          size="small"
                          sx={{ fontWeight: 500 }}
                        />
                      </Box>
                      <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                        {formatDate(issue.created_at)}
                      </Typography>
                      {issue.ai_analysis && (
                        <Typography variant="body2" sx={{ mt: 1, fontWeight: 500 }}>
                          Priority: <Chip label={issue.ai_analysis.priority || 'unknown'} size="small" variant="outlined" color="default" />
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default DashboardPage;
