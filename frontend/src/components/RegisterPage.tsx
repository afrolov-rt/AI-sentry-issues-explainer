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
import { RegisterRequest } from '../types';

interface RegisterPageProps {
  onSwitchToLogin: () => void;
}

const RegisterPage: React.FC<RegisterPageProps> = ({ onSwitchToLogin }) => {
  const { register, loading, error, clearError } = useAuth();
  const [formData, setFormData] = useState<RegisterRequest>({
    email: '',
    username: '',
    password: '',
  });
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    if (name === 'confirmPassword') {
      setConfirmPassword(value);
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value,
      }));
    }
    
    if (error) {
      clearError();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.email || !formData.username || !formData.password || !confirmPassword) {
      return;
    }

    if (formData.password !== confirmPassword) {
      return;
    }

    try {
      await register(formData);
    } catch (error) {
    }
  };

  const isFormValid = formData.email && 
                     formData.username && 
                     formData.password && 
                     confirmPassword &&
                     formData.password === confirmPassword;

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
          mt: 6,
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
              Sign Up
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {formData.password && confirmPassword && formData.password !== confirmPassword && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Passwords do not match
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email"
              name="email"
              autoComplete="email"
              autoFocus
              value={formData.email}
              onChange={handleChange}
              disabled={loading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
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
              autoComplete="new-password"
              value={formData.password}
              onChange={handleChange}
              disabled={loading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="confirmPassword"
              label="Confirm Password"
              type="password"
              id="confirmPassword"
              autoComplete="new-password"
              value={confirmPassword}
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
              disabled={loading || !isFormValid}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Sign Up'}
            </Button>
            
            <Box textAlign="center">
              <Button
                variant="text"
                onClick={(e) => {
                  e.preventDefault();
                  onSwitchToLogin();
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
                Already have an account? Sign In
              </Button>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default RegisterPage;
