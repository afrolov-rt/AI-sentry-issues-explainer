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
  const [showSentryToken, setShowSentryToken] = useState(false);
  const [showSentryDsn, setShowSentryDsn] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    sentry_api_token: '',
    sentry_organization: '',
    sentry_dsn: '',
  });

  useEffect(() => {
    if (workspace) {
      setFormData({
        name: workspace.name || '',
        description: workspace.description || '',
        sentry_api_token: workspace.sentry_auth_token || '',
        sentry_organization: workspace.sentry_org_slug || '',
        sentry_dsn: workspace.sentry_dsn || '',
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
      if (formData.sentry_api_token !== workspace?.sentry_auth_token) {
        updateData.sentry_api_token = formData.sentry_api_token;
      }
      if (formData.sentry_organization !== workspace?.sentry_org_slug) {
        updateData.sentry_organization = formData.sentry_organization;
      }
      if (formData.sentry_dsn !== workspace?.sentry_dsn) {
        updateData.sentry_dsn = formData.sentry_dsn;
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

            <Divider sx={{ my: 2 }} />

            <TextField
              label="Sentry DSN (Data Source Name)"
              type={showSentryDsn ? 'text' : 'password'}
              value={formData.sentry_dsn}
              onChange={handleInputChange('sentry_dsn')}
              fullWidth
              helperText="DSN for sending error events to your Sentry project (e.g., https://abc@o123.ingest.sentry.io/456)"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowSentryDsn(!showSentryDsn)}
                      edge="end"
                    >
                      {showSentryDsn ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button
                variant="outlined"
                onClick={testSentryConnection}
                disabled={loading || !formData.sentry_api_token || !formData.sentry_organization}
                startIcon={loading ? <CircularProgress size={20} /> : <SettingsIcon />}
              >
                Test Connection
              </Button>
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
