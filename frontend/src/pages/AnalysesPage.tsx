import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Chip,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Tooltip,
  Stack,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Psychology as AnalysisIcon,
  BugReport as BugIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Schedule as ClockIcon,
  Code as CodeIcon,
  Build as FixIcon,
} from '@mui/icons-material';
import { useWorkspace } from '../hooks/useWorkspace';
import { apiService } from '../services/api';
import { ProcessedIssue } from '../types';

const AnalysesPage: React.FC = () => {
  const { workspace } = useWorkspace();
  const [analyses, setAnalyses] = useState<ProcessedIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState<ProcessedIssue | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setMounted(true);
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (workspace) {
      loadAnalyses();
    }
  }, [workspace]);

  const loadAnalyses = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getProcessedIssues();
      setAnalyses(data);
    } catch (err) {
      console.error('Failed to load analyses:', err);
      setError('Failed to load AI analyses');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (analysis: ProcessedIssue) => {
    setSelectedAnalysis(analysis);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
    setSelectedAnalysis(null);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckIcon color="success" />;
      case 'failed': return <ErrorIcon color="error" />;
      case 'analyzing': return <CircularProgress size={16} />;
      default: return <ClockIcon />;
    }
  };

  const formatDate = (dateString: string) => {
    if (!mounted || !dateString) return 'Unknown date';
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Invalid date';
    }
  };

  if (!workspace) {
    return (
      <Box p={3}>
        <Alert severity="warning">
          Please select a workspace to view AI analyses.
        </Alert>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error" action={
          <Button color="inherit" size="small" onClick={loadAnalyses}>
            Try Again
          </Button>
        }>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
            🧠 AI Analyses
          </Typography>
          <Typography variant="body1" color="textSecondary">
            View and manage AI-generated issue analyses
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadAnalyses}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Stats Cards */}
      <Box display="flex" gap={3} flexWrap="wrap" mb={4}>
        <Box flex="1" minWidth="250px">
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Box p={1.5} bgcolor="primary.main" borderRadius="50%" color="white">
                  <AnalysisIcon />
                </Box>
                <Box>
                  <Typography variant="h6" fontWeight={600}>
                    {analyses.length}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Total Analyses
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
        <Box flex="1" minWidth="250px">
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Box p={1.5} bgcolor="success.main" borderRadius="50%" color="white">
                  <CheckIcon />
                </Box>
                <Box>
                  <Typography variant="h6" fontWeight={600}>
                    {analyses.filter(a => a.status === 'completed').length}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Completed
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
        <Box flex="1" minWidth="250px">
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Box p={1.5} bgcolor="error.main" borderRadius="50%" color="white">
                  <ErrorIcon />
                </Box>
                <Box>
                  <Typography variant="h6" fontWeight={600}>
                    {analyses.filter(a => a.ai_analysis?.priority === 'critical').length}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Critical Issues
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
        <Box flex="1" minWidth="250px">
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Box p={1.5} bgcolor="warning.main" borderRadius="50%" color="white">
                  <ClockIcon />
                </Box>
                <Box>
                  <Typography variant="h6" fontWeight={600}>
                    {analyses.filter(a => a.status === 'processing').length}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    In Progress
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Analyses List */}
      {analyses.length === 0 ? (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <AnalysisIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No AI analyses found
          </Typography>
          <Typography variant="body2" color="textSecondary" mb={3}>
            Analyse some issues from the Issues page to see results here.
          </Typography>
        </Paper>
      ) : (
        <Box display="flex" gap={3} flexWrap="wrap">
          {analyses.map((analysis) => (
            <Box flex="1" minWidth="350px" maxWidth="400px" key={analysis.id}>
              <Card sx={{ 
                height: '100%',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: 3,
                },
              }}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Box display="flex" alignItems="center" gap={1}>
                      {getStatusIcon(analysis.status)}
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {analysis.sentry_issue_data?.title || 'Unknown Issue'}
                      </Typography>
                    </Box>
                    <IconButton 
                      size="small" 
                      onClick={() => handleViewDetails(analysis)}
                      sx={{ ml: 1 }}
                    >
                      <ViewIcon fontSize="small" />
                    </IconButton>
                  </Box>

                  <Typography variant="body2" color="textSecondary" mb={2} noWrap>
                    {analysis.ai_analysis?.summary || 'No summary available'}
                  </Typography>

                  <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                    <Chip 
                      label={analysis.status || 'unknown'}
                      size="small"
                      color="default"
                    />
                    {analysis.ai_analysis?.priority && (
                      <Chip 
                        label={analysis.ai_analysis.priority}
                        size="small"
                        color="default"
                      />
                    )}
                  </Box>

                  <Typography variant="caption" color="textSecondary">
                    Created: {formatDate(analysis.created_at)}
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          ))}
        </Box>
      )}

      {/* Details Dialog */}
      <Dialog 
        open={detailsOpen} 
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <AnalysisIcon color="primary" />
            <Box>
              <Typography variant="h6">
                AI Analysis Details
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {selectedAnalysis?.sentry_issue_data?.title}
              </Typography>
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {selectedAnalysis?.ai_analysis ? (
            <Stack spacing={3}>
              <Box>
                <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <BugIcon fontSize="small" color="primary" />
                  Summary
                </Typography>
                <Typography variant="body2">
                  {selectedAnalysis.ai_analysis.summary}
                </Typography>
              </Box>

              <Divider />

              <Box>
                <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ErrorIcon fontSize="small" color="error" />
                  Root Cause
                </Typography>
                <Typography variant="body2">
                  {selectedAnalysis.ai_analysis.root_cause}
                </Typography>
              </Box>

              <Divider />

              <Box>
                <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <FixIcon fontSize="small" color="success" />
                  Suggested Fix
                </Typography>
                <Typography variant="body2">
                  {selectedAnalysis.ai_analysis.suggested_fix}
                </Typography>
              </Box>

              {selectedAnalysis.ai_analysis.reproduction_steps && selectedAnalysis.ai_analysis.reproduction_steps.length > 0 && (
                <>
                  <Divider />
                  <Box>
                    <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
                      Steps to Reproduce
                    </Typography>
                    <List dense>
                      {selectedAnalysis.ai_analysis.reproduction_steps.map((step: string, index: number) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <Typography variant="body2" color="primary" fontWeight={600}>
                              {index + 1}.
                            </Typography>
                          </ListItemIcon>
                          <ListItemText primary={step} />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                </>
              )}

              <Divider />

              <Box display="flex" gap={2} flexWrap="wrap">
                <Box>
                  <Typography variant="caption" color="textSecondary">
                    Priority
                  </Typography>
                  <Box>
                    <Chip 
                      label={selectedAnalysis.ai_analysis.priority || 'Unknown'}
                      size="small"
                      color="default"
                    />
                  </Box>
                </Box>
                <Box>
                  <Typography variant="caption" color="textSecondary">
                    Estimated Effort
                  </Typography>
                  <Typography variant="body2">
                    {selectedAnalysis.ai_analysis.estimated_effort || 'Not specified'}
                  </Typography>
                </Box>
              </Box>
            </Stack>
          ) : (
            <Alert severity="info">
              No detailed analysis available for this issue.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AnalysesPage;
