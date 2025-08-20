import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
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
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Pagination,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  BugReport as BugIcon,
  Psychology as AnalyzeIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { useWorkspace } from '../hooks/useWorkspace';
import { apiService } from '../services/api';
import { SentryIssue } from '../types';

const IssuesPage: React.FC = () => {
  const { workspace } = useWorkspace();
  const [issues, setIssues] = useState<SentryIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedIssue, setSelectedIssue] = useState<SentryIssue | null>(null);
  const [analyzeDialogOpen, setAnalyzeDialogOpen] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [projects, setProjects] = useState<any[]>([]);
  const [mounted, setMounted] = useState(false);
  
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('is:unresolved');
  const [levelFilter, setLevelFilter] = useState<string>('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const timer = setTimeout(() => {
      setMounted(true);
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    loadIssues();
    loadProjects();
  }, [workspace, selectedProject, statusFilter, levelFilter, page]);

  const loadProjects = async () => {
    try {
      if (!workspace?.sentry_api_token) return;
      const projectsData = await apiService.getSentryProjects();
      setProjects(projectsData);
    } catch (err) {
      console.error('Failed to load projects:', err);
    }
  };

  const loadIssues = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!workspace?.sentry_api_token) {
        setError('Sentry API token not configured. Please update workspace settings.');
        return;
      }

      let query = statusFilter;
      if (levelFilter) {
        query += ` level:${levelFilter}`;
      }

      const issuesData = await apiService.getSentryIssues(selectedProject, query);
      setIssues(issuesData);
      
      setTotalPages(Math.ceil(issuesData.length / 25));
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load issues');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async (issue: SentryIssue) => {
    try {
      setAnalyzing(true);
      setSelectedIssue(issue);
      setAnalyzeDialogOpen(true);

      await apiService.analyzeIssue(issue.id);
      
      await loadIssues();
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze issue');
    } finally {
      setAnalyzing(false);
      setAnalyzeDialogOpen(false);
    }
  };

  const getStatusChip = (status: string) => {
    return <Chip size="small" color="default" label={status || 'Unknown'} />;
  };

  const getLevelChip = (level: string) => {
    return <Chip size="small" color="default" label={level || 'Unknown'} />;
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
          No workspace found. Please create a workspace first.
        </Alert>
      </Box>
    );
  }

  if (!workspace.sentry_api_token) {
    return (
      <Box p={3}>
        <Alert severity="warning">
          Sentry API token not configured. Please update workspace settings.
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          <BugIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
          Sentry Issues
        </Typography>
        
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadIssues}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <FilterIcon />
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Project</InputLabel>
            <Select
              value={selectedProject}
              label="Project"
              onChange={(e) => setSelectedProject(e.target.value)}
            >
              <MenuItem value="">All Projects</MenuItem>
              {projects.map((project) => (
                <MenuItem key={project.id} value={project.id}>
                  {project.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              label="Status"
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="is:unresolved">Unresolved</MenuItem>
              <MenuItem value="is:resolved">Resolved</MenuItem>
              <MenuItem value="is:ignored">Ignored</MenuItem>
              <MenuItem value="">All</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Level</InputLabel>
            <Select
              value={levelFilter}
              label="Level"
              onChange={(e) => setLevelFilter(e.target.value)}
            >
              <MenuItem value="">All Levels</MenuItem>
              <MenuItem value="error">Error</MenuItem>
              <MenuItem value="warning">Warning</MenuItem>
              <MenuItem value="info">Info</MenuItem>
              <MenuItem value="debug">Debug</MenuItem>
            </Select>
          </FormControl>
        </Stack>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Issue</TableCell>
                  <TableCell>Level</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Project</TableCell>
                  <TableCell>Events</TableCell>
                  <TableCell>Users</TableCell>
                  <TableCell>Last Seen</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {issues.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No issues found
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  issues.map((issue) => (
                    <TableRow key={issue.id} hover>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {issue.title}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {issue.culprit}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{getLevelChip(issue.level)}</TableCell>
                      <TableCell>{getStatusChip(issue.status)}</TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {issue.project_name || 'Unknown'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {issue.count?.toLocaleString() || 0}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {issue.userCount?.toLocaleString() || 0}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {formatDate(issue.last_seen)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1}>
                          <Tooltip title="View in Sentry">
                            <IconButton
                              size="small"
                              onClick={() => window.open(issue.permalink, '_blank')}
                            >
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Analyze with AI">
                            <IconButton
                              size="small"
                              onClick={() => handleAnalyze(issue)}
                              disabled={analyzing}
                            >
                              <AnalyzeIcon />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={3}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(event, value) => setPage(value)}
                color="primary"
              />
            </Box>
          )}
        </>
      )}

      {/* Analyze Dialog */}
      <Dialog 
        open={analyzeDialogOpen} 
        onClose={() => setAnalyzeDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Analyzing Issue</DialogTitle>
        <DialogContent>
          <Box display="flex" alignItems="center" gap={2}>
            <CircularProgress size={24} />
            <Typography>
              AI is analyzing the issue "{selectedIssue?.title}"...
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAnalyzeDialogOpen(false)} disabled={analyzing}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default IssuesPage;
