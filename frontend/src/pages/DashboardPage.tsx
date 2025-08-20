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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  BugReport as BugReportIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Error as ErrorIcon,
  Psychology as PsychologyIcon,
  Close as CloseIcon,
  Code as CodeIcon,
  Build as FixIcon,
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
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [analyzingIssues, setAnalyzingIssues] = useState<Set<string>>(new Set());
  const [mounted, setMounted] = useState(false);
  const [generatingEvents, setGeneratingEvents] = useState(false);
  const [sentryStatus, setSentryStatus] = useState<any>(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState<ProcessedIssue | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const { workspace } = useWorkspace();

  useEffect(() => {
    const timer = setTimeout(() => {
      setMounted(true);
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [workspace]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    checkSentryStatus();
  }, []);

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
      setError(null);
      setSuccessMessage(null);
      setAnalyzingIssues(prev => new Set(prev).add(issueId));
      
      const result = await apiService.analyzeIssue(issueId);
      
      if (result.status === 'completed') {
        await fetchDashboardData();
      } else if (result.status === 'analyzing') {
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

  const checkSentryStatus = async () => {
    try {
      const publicStatus = await apiService.getSentryStatusPublic();
      setSentryStatus(publicStatus);
      
      try {
        const fullStatus = await apiService.getSentryStatus();
        setSentryStatus(fullStatus);
      } catch (err: any) {
      }
    } catch (err: any) {
      console.error('Failed to get any Sentry status:', err);
      setSentryStatus({ sentry_configured: false });
    }
  };

  const handleGenerateRandomEvents = async (eventType?: string, count: number = 3) => {
    setError(null);
    setSuccessMessage(null);
    
    if (!sentryStatus?.sentry_configured) {
      setError('Sentry DSN is not configured on the backend. Please check server configuration.');
      return;
    }

    setGeneratingEvents(true);
    
    try {
      const result = await apiService.generateRandomSentryEvent(eventType, count);
      
      if (result.success) {
        setSuccessMessage(`Successfully generated ${result.total_generated} Sentry events! Check your Sentry dashboard in a few moments.`);
        
        setTimeout(() => {
          fetchDashboardData();
          setSuccessMessage(null);
        }, 5000);
      } else {
        setError('Failed to generate events');
      }
    } catch (err: any) {
      console.error('Failed to generate Sentry events:', err);
      setError(err.response?.data?.detail || 'Failed to generate Sentry events');
    } finally {
      setGeneratingEvents(false);
    }
  };

  const handleViewIssueAnalysis = async (issueId: string) => {
    try {
      const existingAnalysis = processedIssues.find(
        (analysis) => analysis.sentry_issue_id === issueId
      );
      
      if (existingAnalysis) {
        setSelectedAnalysis(existingAnalysis);
        setDetailsOpen(true);
      } else {
        setError('No analysis found for this issue. Please analyze it first.');
      }
    } catch (err: any) {
      console.error('Failed to view analysis:', err);
      setError('Failed to load analysis');
    }
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
    setSelectedAnalysis(null);
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

      {successMessage && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {successMessage}
        </Alert>
      )}

      {!workspace?.sentry_api_token && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Configure Sentry API token in workspace settings to load data
        </Alert>
      )}

      {sentryStatus && !sentryStatus.sentry_configured && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
              Sentry Event Generation Not Available
            </Typography>
            <Typography variant="body2">
              Sentry DSN is not configured on the backend server. To generate test events:
            </Typography>
            <Typography variant="body2" component="ul" sx={{ mt: 1, ml: 2 }}>
              <li>Set the APP_SENTRY_DSN environment variable on the backend</li>
              <li>Restart the backend server</li>
            </Typography>
          </Box>
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
                  borderRadius: '50%', 
                  width: 70,
                  height: 70,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
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
                  borderRadius: '50%', 
                  width: 70,
                  height: 70,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
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
                  borderRadius: '50%', 
                  width: 70,
                  height: 70,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
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
                  borderRadius: '50%', 
                  width: 70,
                  height: 70,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
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
              <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  📋 Recent Issues
                </Typography>
                <Box display="flex" gap={1}>
                  <Button
                    variant="outlined"
                    size="small"
                    color="primary"
                    disabled={generatingEvents || !sentryStatus?.sentry_configured}
                    onClick={() => handleGenerateRandomEvents('error', 1)}
                    sx={{ minWidth: 'auto', px: 2 }}
                  >
                    {generatingEvents ? <CircularProgress size={16} /> : '�'} Error
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    color="warning"
                    disabled={generatingEvents || !sentryStatus?.sentry_configured}
                    onClick={() => handleGenerateRandomEvents('warning', 1)}
                    sx={{ minWidth: 'auto', px: 2 }}
                  >
                    {generatingEvents ? <CircularProgress size={16} /> : '⚠️'} Warning
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    color="secondary"
                    disabled={generatingEvents || !sentryStatus?.sentry_configured}
                    onClick={() => handleGenerateRandomEvents(undefined, 3)}
                    sx={{ minWidth: 'auto', px: 2 }}
                  >
                    {generatingEvents ? <CircularProgress size={16} /> : '🎲'} Random
                  </Button>
                </Box>
              </Box>
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
                      cursor: 'pointer',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        backgroundColor: '#f1f5f9',
                        transform: 'translateY(-1px)',
                        boxShadow: '0 4px 12px rgb(0 0 0 / 0.1)',
                      },
                    }}
                    onClick={() => handleViewIssueAnalysis(issue.id)}
                    >
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
                            onClick={(e) => {
                              e.stopPropagation();
                              handleAnalyzeIssue(issue.id);
                            }}
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

      {/* Analysis Details Dialog */}
      <Dialog 
        open={detailsOpen} 
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            Analysis Details
          </Typography>
          <IconButton onClick={handleCloseDetails} size="small">
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        
        {selectedAnalysis && (
          <DialogContent>
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedAnalysis.sentry_issue_data?.title || 'Unknown Issue'}
              </Typography>
              
              <Box display="flex" gap={1} mb={3}>
                <Chip 
                  label={selectedAnalysis.status || 'unknown'}
                  color={getStatusColor(selectedAnalysis.status)}
                  size="small"
                />
                {selectedAnalysis.ai_analysis?.priority && (
                  <Chip 
                    label={selectedAnalysis.ai_analysis.priority}
                    color="default"
                    size="small"
                  />
                )}
              </Box>

              {selectedAnalysis.ai_analysis && (
                <>
                  <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                    📋 Summary
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {selectedAnalysis.ai_analysis.summary || 'No summary available'}
                  </Typography>

                  <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                    🔍 Root Cause Analysis
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {selectedAnalysis.ai_analysis.root_cause || 'No root cause analysis available'}
                  </Typography>

                  {selectedAnalysis.ai_analysis.suggested_fix && (
                    <>
                      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                        🔧 Suggested Fix
                      </Typography>
                      <Typography variant="body1" paragraph>
                        {selectedAnalysis.ai_analysis.suggested_fix}
                      </Typography>
                    </>
                  )}
                </>
              )}

              <Divider sx={{ my: 3 }} />
              
              <Typography variant="body2" color="textSecondary">
                Created: {formatDate(selectedAnalysis.created_at)} • 
                Updated: {formatDate(selectedAnalysis.updated_at)}
              </Typography>
            </Box>
          </DialogContent>
        )}
        
        <DialogActions>
          <Button onClick={handleCloseDetails} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DashboardPage;
