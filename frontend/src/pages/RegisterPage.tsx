import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  Link as MuiLink,
  Avatar,
  Alert,
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const RegisterPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    if (password !== password2) {
      setError('Les mots de passe ne correspondent pas.');
      return;
    }
    try {
      await register(username, email, password);
      navigate('/'); // Redirection vers le Dashboard après inscription
    } catch (err: any) {
      if (err.response && err.response.data) {
        // Essayer d'afficher un message d'erreur plus spécifique du backend
        const errorData = err.response.data;
        const firstErrorKey = Object.keys(errorData)[0];
        const errorMessage = errorData[firstErrorKey][0];
        setError(errorMessage || "Échec de l'inscription. Veuillez réessayer.");
      } else {
        setError("Échec de l'inscription. Une erreur inconnue est survenue.");
      }
      console.error(err);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
          <LockOutlinedIcon />
        </Avatar>
        <Typography component="h1" variant="h5">
          Inscription
        </Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 3 }}>
          {error && <Alert severity="error" sx={{ width: '100%', mb: 2 }}>{error}</Alert>}
          <Grid container spacing={2}>
            <Grid xs={12}>
              <TextField
                required
                fullWidth
                id="username"
                label="Nom d'utilisateur"
                name="username"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </Grid>
            <Grid xs={12}>
              <TextField
                required
                fullWidth
                id="email"
                label="Adresse Email"
                name="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </Grid>
            <Grid xs={12}>
              <TextField
                required
                fullWidth
                name="password"
                label="Mot de passe"
                type="password"
                id="password"
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </Grid>
            <Grid xs={12}>
              <TextField
                required
                fullWidth
                name="password2"
                label="Confirmer le mot de passe"
                type="password"
                id="password2"
                autoComplete="new-password"
                value={password2}
                onChange={(e) => setPassword2(e.target.value)}
              />
            </Grid>
          </Grid>
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            S'inscrire
          </Button>
          <Grid container justifyContent="flex-end">
            <Grid item>
              <MuiLink component={Link} to="/login" variant="body2">
                Déjà un compte ? Connectez-vous
              </MuiLink>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Container>
  );
};

export default RegisterPage;
