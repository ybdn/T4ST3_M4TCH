import React, { Component, ErrorInfo, ReactNode } from 'react';

// Icônes SVG pour remplacer celles de MUI
const ErrorIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const RefreshIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h5M20 20v-5h-5M4 4l1.5 1.5A9 9 0 0120.5 15M20 20l-1.5-1.5A9 9 0 003.5 9" />
  </svg>
);

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-tm-surface flex items-center justify-center p-4">
          <div className="bg-tm-surface-light rounded-lg shadow-lg p-8 text-center max-w-lg w-full">
            <ErrorIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
            
            <h1 className="text-2xl font-bold text-tm-text-primary mb-2">
              Oups ! Quelque chose s'est mal passé
            </h1>
            
            <p className="text-tm-text-secondary mb-6">
              Une erreur inattendue s'est produite. Nous nous excusons pour ce désagrément.
            </p>

            <div className="bg-red-900/20 border border-red-500/30 rounded-md p-4 mb-6 text-left">
              <p className="text-red-400 font-semibold">
                Erreur : {this.state.error?.message || 'Erreur inconnue'}
              </p>
              {import.meta.env.DEV && this.state.errorInfo && (
                <details className="mt-2">
                  <summary className="text-sm text-tm-text-secondary cursor-pointer">Détails techniques</summary>
                  <pre className="text-xs text-tm-text-secondary overflow-auto mt-2 p-2 bg-black/20 rounded">
                    {this.state.errorInfo.componentStack}
                  </pre>
                </details>
              )}
            </div>

            <div className="flex gap-4 justify-center">
              <button
                className="flex items-center gap-2 bg-primary text-white font-semibold px-6 py-2 rounded-md hover:bg-primary/80 transition-colors"
                onClick={this.handleReset}
              >
                <RefreshIcon className="h-5 w-5" />
                Réessayer
              </button>
              
              <button
                className="bg-tm-surface text-tm-text-primary font-semibold px-6 py-2 rounded-md hover:bg-tm-surface/80 border border-tm-border transition-colors"
                onClick={() => window.location.reload()}
              >
                Recharger la page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;