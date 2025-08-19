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
} from '@mui/icons-material';
import { ProcessedIssue, SentryIssue } from '../types';
import { apiService } from '../services/api';
import { useWorkspace } from '../hooks/useWorkspace';

const DashboardPage: React.FC = () => {
  const [processedIssues, setProcessedIssues] = useState<ProcessedIssue[]>([]);
  const [sentryIssues, setSentryIssues] = useState<SentryIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { workspace } = useWorkspace();

  useEffect(() => {
    fetchDashboardData();
  }, [workspace]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [processedData, sentryData] = await Promise.allSettled([
        apiService.getProcessedIssues(),
        workspace?.sentry_auth_token ? apiService.getSentryIssues() : Promise.resolve([])
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const stats = {
    totalProcessed: processedIssues.length,
    completed: processedIssues.filter(issue => issue.status === 'completed').length,
    processing: processedIssues.filter(issue => issue.status === 'processing').length,
    failed: processedIssues.filter(issue => issue.status === 'failed').length,
    totalSentry: sentryIssues.length,
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

      {!workspace?.sentry_auth_token && (
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
                📋 Recent Processed Issues
              </Typography>
              {processedIssues.length === 0 ? (
                <Box textAlign="center" py={4}>
                  <Typography color="textSecondary" sx={{ fontSize: '1.1rem' }}>
                    No processed issues yet
                  </Typography>
                </Box>
              ) : (
                <Box>
                  {processedIssues.slice(0, 5).map((issue) => (
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
                          {issue.sentry_issue_data.title}
                        </Typography>
                        <Chip 
                          label={issue.status} 
                          color={getStatusColor(issue.status) as any}
                          size="small"
                          sx={{ fontWeight: 500 }}
                        />
                      </Box>
                      <Typography variant="body2" color="textSecondary">
                        {new Date(issue.created_at).toLocaleDateString('en-US')}
                      </Typography>
                      {issue.ai_analysis && (
                        <Typography variant="body2" sx={{ mt: 1, fontWeight: 500 }}>
                          Priority: <Chip label={issue.ai_analysis.priority} size="small" variant="outlined" />
                        </Typography>
                      )}
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
                        label={workspace.sentry_org_slug || 'Not configured'} 
                        size="small" 
                        color={workspace.sentry_org_slug ? 'success' : 'default'}
                        variant="outlined"
                      />
                    </Box>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        Sentry Token:
                      </Typography>
                      <Chip 
                        label={workspace.sentry_auth_token ? 'Configured' : 'Not configured'} 
                        size="small" 
                        color={workspace.sentry_auth_token ? 'success' : 'warning'}
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
                        color={workspace.openai_api_key ? 'success' : 'warning'}
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                  
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 3, fontSize: '0.9rem' }}>
                    Created: {new Date(workspace.created_at).toLocaleDateString('en-US')}
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
        </Box>
      </Box>
    </Box>
  );
};

export default DashboardPage;
