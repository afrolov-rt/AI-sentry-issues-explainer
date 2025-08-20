import React, { useState } from 'react';
import { 
  Container, 
  Paper, 
  TextField, 
  Button, 
  Typography, 
  Box, 
  Alert,
  CircularProgress,
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { LoginRequest } from '../types';

interface LoginPageProps {
  onSwitchToRegister: () => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onSwitchToRegister }) => {
  const { login, loading, error, clearError } = useAuth();
  const [formData, setFormData] = useState<LoginRequest>({
    username: '',
    password: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    if (error) {
      clearError();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password) {
      return;
    }

    try {
      await login(formData);
    } catch (error) {
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          margin: 0,
          padding: 3,
        }}
      >
        <Paper elevation={0} sx={{ 
          padding: 4, 
          width: '100%', 
          maxWidth: '400px',
          mt: 8,
          borderRadius: 4,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        }}>
          <Box textAlign="center" sx={{ mb: 4 }}>
            <Typography component="h1" variant="h4" sx={{ 
              fontWeight: 700, 
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 1,
            }}>
              🚀 AI Sentry Issues Explainer
            </Typography>
            <Typography component="h2" variant="h5" sx={{ fontWeight: 600, color: '#475569' }}>
              Sign In
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus
              value={formData.username}
              onChange={handleChange}
              disabled={loading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
              disabled={loading}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ 
                mt: 3, 
                mb: 2, 
                py: 1.5,
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                fontWeight: 600,
                fontSize: '1.1rem',
              }}
              disabled={loading || !formData.username || !formData.password}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
            </Button>
            
            <Box textAlign="center">
              <Button
                variant="text"
                onClick={(e) => {
                  e.preventDefault();
                  onSwitchToRegister();
                }}
                disabled={loading}
                sx={{
                  textTransform: 'none',
                  fontWeight: 500,
                  color: '#6366f1',
                  '&:hover': {
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                  },
                }}
              >
                Don't have an account? Sign Up
              </Button>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;
