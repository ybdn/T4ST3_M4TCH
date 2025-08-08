import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Field, Label, Input, Description, Button } from '@headlessui/react';
import { Transition } from '@headlessui/react';
import clsx from 'clsx';


const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError("Échec de la connexion. Vérifiez vos identifiants.");
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen tm-auth-bg flex items-center justify-center py-4 px-4 sm:px-6 lg:px-8 font-inter overflow-y-auto">
      <Transition
        appear={true}
        show={true}
        enter="transition-all duration-700 ease-out"
        enterFrom="opacity-0 scale-95 translate-y-8"
        enterTo="opacity-100 scale-100 translate-y-0"
      >
        <div className="phi-container w-full phi-gap">
          {/* Header épuré avec proportions dorées */}
          <div className="text-center">
            <h1 className="phi-title font-bold font-cinzel text-white">
              T4ST3 M4TCH
            </h1>
            <h2 className="phi-subtitle font-semibold text-tm-text">Connexion</h2>
          </div>

          {/* Message d'erreur avec effet de verre */}
          <Transition
            show={!!error}
            enter="transition-all duration-300 ease-out"
            enterFrom="opacity-0 scale-95 translate-y-2"
            enterTo="opacity-100 scale-100 translate-y-0"
            leave="transition-all duration-200 ease-in"
            leaveFrom="opacity-100 scale-100 translate-y-0"
            leaveTo="opacity-0 scale-95 translate-y-2"
          >
            <div className="tm-glass border border-tm-primary/40 text-tm-primary p-3 rounded-xl text-sm text-center" style={{
              boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 12px rgba(225, 29, 72, 0.15)'
            }}>
              {error}
            </div>
          </Transition>

          {/* Formulaire principal avec effet de verre */}
          <div className="tm-glass-card phi-card rounded-xl">
            <form onSubmit={handleSubmit} className="phi-gap">
              <Field>
                <Label className="phi-label font-medium text-tm-text">Nom d'utilisateur</Label>
                <Description className="phi-description text-tm-text-muted">Votre identifiant unique sur la plateforme.</Description>
                <Input
                  type="text"
                  autoComplete="username"
                  required
                  autoFocus
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className={clsx(
                    'phi-input block w-full rounded-xl tm-glass-input text-sm text-tm-text placeholder:text-tm-text-muted',
                    'focus:outline-none data-focus:ring-2 data-focus:ring-tm-primary data-focus:border-white/40 transition-all duration-200 data-focus:bg-white/12'
                  )}
                  placeholder="Votre nom d'utilisateur"
                />
              </Field>

              <Field>
                <Label className="phi-label font-medium text-tm-text">Mot de passe</Label>
                <Description className="phi-description text-tm-text-muted">Ne partagez jamais votre mot de passe.</Description>
                <Input
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={clsx(
                    'phi-input block w-full rounded-xl tm-glass-input text-sm text-tm-text placeholder:text-tm-text-muted',
                    'focus:outline-none data-focus:ring-2 data-focus:ring-tm-primary data-focus:border-white/40 transition-all duration-200 data-focus:bg-white/12'
                  )}
                  placeholder="Votre mot de passe"
                />
              </Field>

              <Button
                type="submit"
                className="w-full tm-glass-button phi-button inline-flex items-center justify-center gap-2 rounded-xl focus:not-data-focus:outline-none data-focus:outline-2 data-focus:outline-white/50"
              >
                Se connecter
              </Button>
            </form>
          </div>

          {/* Lien vers inscription avec effet de verre */}
          <div className="tm-glass phi-small-card rounded-xl text-sm text-center" style={{
            boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 12px rgba(255, 255, 255, 0.05)'
          }}>
            <p className="text-tm-text-muted">
              Vous n'avez pas de compte ?{' '}
              <Link 
                to="/register" 
                className="font-medium text-tm-primary hover:text-tm-primary/80 transition-colors duration-200"
              >
                Inscrivez-vous
              </Link>
            </p>
          </div>
        </div>
      </Transition>
    </div>
  );
};

export default LoginPage;
