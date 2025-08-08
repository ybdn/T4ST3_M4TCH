import React, { useState, useEffect, Fragment } from 'react';
import { Transition } from '@headlessui/react';
import clsx from 'clsx';

// Définition des types de messages, en utilisant des chaînes de caractères simples
export type FeedbackType = 'success' | 'error' | 'warning' | 'info';

interface FeedbackMessage {
  id: string;
  message: string;
  type: FeedbackType;
  duration?: number;
}

interface UserFeedbackProps {
  message: FeedbackMessage | null;
  onClose: (id: string) => void;
}

const UserFeedback: React.FC<UserFeedbackProps> = ({ message, onClose }) => {
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (message) {
      setShow(true);
      const duration = message.duration || 4000;
      const timer = setTimeout(() => {
        handleClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [message]);

  const handleClose = () => {
    if (message) {
      setShow(false);
      // Laisser le temps à l'animation de se terminer avant de supprimer le message
      setTimeout(() => {
        onClose(message.id);
      }, 300); // Doit correspondre à la durée de la transition
    }
  };

  if (!message) {
    return null;
  }

  const alertStyles = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    warning: 'bg-yellow-500 text-white',
    info: 'bg-blue-500 text-white',
  };

  return (
    <div className="fixed top-5 left-1/2 -translate-x-1/2 z-50 w-full max-w-md px-4">
      <Transition
        show={show}
        as={Fragment}
        enter="transition ease-out duration-300"
        enterFrom="transform opacity-0 scale-95 -translate-y-10"
        enterTo="transform opacity-100 scale-100 translate-y-0"
        leave="transition ease-in duration-300"
        leaveFrom="transform opacity-100 scale-100 translate-y-0"
        leaveTo="transform opacity-0 scale-95 -translate-y-10"
      >
        <div
          className={clsx(
            'rounded-md shadow-lg p-4 flex items-center justify-between w-full',
            alertStyles[message.type]
          )}
        >
          <p className="text-sm font-medium">{message.message}</p>
          <button
            onClick={handleClose}
            className="ml-4 p-1 rounded-full hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white"
          >
            <svg
              className="h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </Transition>
    </div>
  );
};

// Hook pour gérer les messages de feedback
export const useUserFeedback = () => {
  const [messages, setMessages] = useState<FeedbackMessage[]>([]);

  const addMessage = (
    message: string,
    type: FeedbackType = 'info',
    duration?: number
  ) => {
    const id = Date.now().toString();
    const newMessage: FeedbackMessage = { id, message, type, duration };
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
    showInfo,
  };
};

export default UserFeedback;