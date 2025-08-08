import { useState, useCallback } from 'react';

interface ErrorState {
  message: string;
  details?: string;
  code?: string;
}

export const useErrorHandler = () => {
  const [error, setError] = useState<ErrorState | null>(null);

  const handleError = useCallback((error: any, context?: string) => {
    console.error(`Error in ${context || 'unknown context'}:`, error);
    
    let errorMessage = 'Une erreur inattendue s\'est produite';
    let errorDetails: string | undefined;
    let errorCode: string | undefined;

    if (error instanceof Error) {
      errorMessage = error.message;
    } else if (typeof error === 'string') {
      errorMessage = error;
    } else if (error?.response?.data?.error) {
      errorMessage = error.response.data.error;
      errorCode = error.response.status?.toString();
    } else if (error?.response?.data?.detail) {
      errorMessage = error.response.data.detail;
      errorCode = error.response.status?.toString();
    } else if (error?.message) {
      errorMessage = error.message;
    }

    // Messages d'erreur personnalisés pour les cas courants
    if (error?.response?.status === 401) {
      errorMessage = 'Session expirée. Veuillez vous reconnecter.';
      errorCode = '401';
    } else if (error?.response?.status === 403) {
      errorMessage = 'Accès refusé. Vous n\'avez pas les permissions nécessaires.';
      errorCode = '403';
    } else if (error?.response?.status === 404) {
      errorMessage = 'Ressource introuvable.';
      errorCode = '404';
    } else if (error?.response?.status === 500) {
      errorMessage = 'Erreur serveur. Veuillez réessayer plus tard.';
      errorCode = '500';
    } else if (error?.code === 'NETWORK_ERROR') {
      errorMessage = 'Erreur de connexion. Vérifiez votre connexion internet.';
      errorCode = 'NETWORK_ERROR';
    }

    setError({
      message: errorMessage,
      details: errorDetails,
      code: errorCode
    });
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const handleAsyncError = useCallback(async <T>(
    asyncFn: () => Promise<T>,
    context?: string
  ): Promise<T | null> => {
    try {
      clearError();
      return await asyncFn();
    } catch (err) {
      handleError(err, context);
      return null;
    }
  }, [handleError, clearError]);

  return {
    error,
    handleError,
    clearError,
    handleAsyncError
  };
};
