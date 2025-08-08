import React, { useState, useEffect } from 'react';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import Slide from '@mui/material/Slide';
import type { AlertColor } from '@mui/material/Alert';
import type { SlideProps } from '@mui/material/Slide';

interface FeedbackMessage {
  id: string;
  message: string;
  type: AlertColor;
  duration?: number;
}

interface UserFeedbackProps {
  message: FeedbackMessage | null;
  onClose: (id: string) => void;
}

function SlideTransition(props: SlideProps) {
  return <Slide {...props} direction="up" />;
}

const UserFeedback: React.FC<UserFeedbackProps> = ({ message, onClose }) => {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (message) {
      setOpen(true);
      
      // Auto-close après la durée spécifiée
      const duration = message.duration || 4000;
      const timer = setTimeout(() => {
        setOpen(false);
        setTimeout(() => onClose(message.id), 300); // Attendre la transition
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [message, onClose]);

  const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpen(false);
    setTimeout(() => onClose(message?.id || ''), 300);
  };

  if (!message) return null;

  return (
    <Snackbar
      open={open}
      autoHideDuration={message.duration || 4000}
      onClose={handleClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      TransitionComponent={SlideTransition}
      sx={{
        '& .MuiAlert-root': {
          minWidth: { xs: '90vw', sm: 400 },
          maxWidth: { xs: '90vw', sm: 600 }
        }
      }}
    >
      <Alert
        onClose={handleClose}
        severity={message.type}
        variant="filled"
        sx={{
          width: '100%',
          '& .MuiAlert-message': {
            fontSize: { xs: '0.875rem', sm: '1rem' }
          }
        }}
      >
        {message.message}
      </Alert>
    </Snackbar>
  );
};

// Hook pour gérer les messages de feedback
export const useUserFeedback = () => {
  const [messages, setMessages] = useState<FeedbackMessage[]>([]);

  const addMessage = (
    message: string,
    type: AlertColor = 'info',
    duration?: number
  ) => {
    const id = Date.now().toString();
    const newMessage: FeedbackMessage = {
      id,
      message,
      type,
      duration
    };
    
    setMessages(prev => [...prev, newMessage]);
    return id;
  };

  const removeMessage = (id: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== id));
  };

  const showSuccess = (message: string, duration?: number) => {
    return addMessage(message, 'success', duration);
  };

  const showError = (message: string, duration?: number) => {
    return addMessage(message, 'error', duration);
  };

  const showWarning = (message: string, duration?: number) => {
    return addMessage(message, 'warning', duration);
  };

  const showInfo = (message: string, duration?: number) => {
    return addMessage(message, 'info', duration);
  };

  return {
    messages,
    addMessage,
    removeMessage,
    showSuccess,
    showError,
    showWarning,
    showInfo
  };
};

export default UserFeedback;
