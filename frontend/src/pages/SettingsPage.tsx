import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  Alert,
  Divider,
  CircularProgress,
  InputAdornment,
  IconButton,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Save as SaveIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useWorkspace } from '../hooks/useWorkspace';
import { apiService } from '../services/api';

const SettingsPage: React.FC = () => {
  const { workspace, refreshWorkspace } = useWorkspace();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);
  const [testingOpenAI, setTestingOpenAI] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);
  const [openaiTestResult, setOpenaiTestResult] = useState<string | null>(null);
  const [showSentryToken, setShowSentryToken] = useState(false);
  const [showOpenAIKey, setShowOpenAIKey] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    sentry_api_token: '',
    sentry_organization: '',
    openai_api_key: '',
  });

  useEffect(() => {
    if (workspace) {
      setFormData({
        name: workspace.name || '',
        description: workspace.description || '',
        sentry_api_token: workspace.sentry_api_token || '',
        sentry_organization: workspace.sentry_organization || '',
        openai_api_key: workspace.openai_api_key || '',
      });
    }
  }, [workspace]);

  const handleInputChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
    // Clear messages when user starts typing
    if (error) setError(null);
    if (success) setSuccess(null);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const updateData: any = {};
      
      // Only include fields that have changed
      if (formData.name !== workspace?.name) {
        updateData.name = formData.name;
      }
      if (formData.description !== workspace?.description) {
        updateData.description = formData.description;
      }
      if (formData.sentry_api_token !== workspace?.sentry_api_token) {
        updateData.sentry_api_token = formData.sentry_api_token;
      }
      if (formData.sentry_organization !== workspace?.sentry_organization) {
        updateData.sentry_organization = formData.sentry_organization;
      }
      if (formData.openai_api_key !== workspace?.openai_api_key) {
        updateData.openai_api_key = formData.openai_api_key;
      }

      if (Object.keys(updateData).length === 0) {
        setError('No changes to save');
        return;
      }

      await apiService.updateWorkspace(updateData);
      await refreshWorkspace();
      setSuccess('Settings saved successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleTestOpenAI = async () => {
    if (!formData.openai_api_key.trim()) {
      setOpenaiTestResult('Please enter an OpenAI API key first');
      return;
    }

    try {
      setTestingOpenAI(true);
      setOpenaiTestResult(null);

      const result = await apiService.testOpenAIConnection({
        openai_api_key: formData.openai_api_key
      });

      if (result.connected) {
        setOpenaiTestResult(`✅ ${result.message}`);
      } else {
        setOpenaiTestResult(`❌ ${result.message}`);
      }
    } catch (err: any) {
      setOpenaiTestResult(`❌ Connection failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setTestingOpenAI(false);
    }
  };

  const handleTestSentry = async () => {
    if (!formData.sentry_api_token.trim() || !formData.sentry_organization.trim()) {
      setTestResult('Please enter both Sentry API token and organization slug');
      return;
    }

    try {
      setTesting(true);
      setTestResult(null);

      const result = await apiService.testSentryConnection({
        sentry_api_token: formData.sentry_api_token,
        sentry_organization: formData.sentry_organization
      });

      if (result.connected) {
        setTestResult(`✅ ${result.message}`);
      } else {
        setTestResult(`❌ ${result.message}`);
      }
    } catch (err: any) {
      setTestResult(`❌ Connection failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setTesting(false);
    }
  };

  const testSentryConnection = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      if (!formData.sentry_api_token || !formData.sentry_organization) {
        setError('Please fill in Sentry API token and organization first');
        return;
      }

      const result = await apiService.testSentryConnection({
        sentry_api_token: formData.sentry_api_token,
        sentry_organization: formData.sentry_organization,
      });

      if (result.connected) {
        setSuccess(result.message + (result.projects_count ? ` Found ${result.projects_count} projects.` : ''));
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to test connection');
    } finally {
      setLoading(false);
    }
  };

  if (!workspace) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        ⚙️ Workspace Settings
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}

      {/* General Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
            📝 General Settings
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              label="Workspace Name"
              value={formData.name}
              onChange={handleInputChange('name')}
              fullWidth
              required
              helperText="A descriptive name for your workspace"
            />
            
            <TextField
              label="Description"
              value={formData.description}
              onChange={handleInputChange('description')}
              fullWidth
              multiline
              rows={3}
              helperText="Optional description of your workspace"
            />
          </Box>
        </CardContent>
      </Card>

      {/* OpenAI Integration */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
            🤖 OpenAI Integration
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              label="OpenAI API Key"
              type={showOpenAIKey ? 'text' : 'password'}
              value={formData.openai_api_key}
              onChange={handleInputChange('openai_api_key')}
              fullWidth
              helperText="Your OpenAI API key for AI analysis of issues"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowOpenAIKey(!showOpenAIKey)}
                      edge="end"
                    >
                      {showOpenAIKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Button
                variant="outlined"
                onClick={handleTestOpenAI}
                disabled={testingOpenAI || !formData.openai_api_key.trim()}
                sx={{ minWidth: 120 }}
              >
                {testingOpenAI ? (
                  <>
                    <CircularProgress size={16} sx={{ mr: 1 }} />
                    Testing...
                  </>
                ) : (
                  'Test OpenAI'
                )}
              </Button>
              
              {openaiTestResult && (
                <Typography
                  variant="body2"
                  sx={{
                    color: openaiTestResult.includes('✅') ? 'success.main' : 'error.main',
                    flex: 1
                  }}
                >
                  {openaiTestResult}
                </Typography>
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Sentry Integration */}
      <Card>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
            🔗 Sentry Integration
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              label="Sentry API Token"
              type={showSentryToken ? 'text' : 'password'}
              value={formData.sentry_api_token}
              onChange={handleInputChange('sentry_api_token')}
              fullWidth
              helperText="Your Sentry API token for accessing issues"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowSentryToken(!showSentryToken)}
                      edge="end"
                    >
                      {showSentryToken ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            
            <TextField
              label="Sentry Organization Slug"
              value={formData.sentry_organization}
              onChange={handleInputChange('sentry_organization')}
              fullWidth
              helperText="Your Sentry organization identifier"
            />

            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Button
                variant="outlined"
                onClick={handleTestSentry}
                disabled={testing || !formData.sentry_api_token.trim() || !formData.sentry_organization.trim()}
                sx={{ minWidth: 120 }}
              >
                {testing ? (
                  <>
                    <CircularProgress size={16} sx={{ mr: 1 }} />
                    Testing...
                  </>
                ) : (
                  'Test Sentry'
                )}
              </Button>
              
              {testResult && (
                <Typography
                  variant="body2"
                  sx={{
                    color: testResult.includes('✅') ? 'success.main' : 'error.main',
                    flex: 1
                  }}
                >
                  {testResult}
                </Typography>
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Save Button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
        <Button
          variant="contained"
          onClick={handleSave}
          disabled={saving}
          startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
          size="large"
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};

export default SettingsPage;
