import React, { useState, useEffect, Fragment, useCallback } from "react";
import { Transition } from "@headlessui/react";
import clsx from "clsx";

// Définition des types de messages, en utilisant des chaînes de caractères simples
export type FeedbackType = "success" | "error" | "warning" | "info";

export interface FeedbackMessage {
  id: string;
  message: string;
  type: FeedbackType;
  duration?: number;
}

interface UserFeedbackProps {
  messages: FeedbackMessage[];
  onClose: (id: string) => void;
  maxVisible?: number;
  defaultDurationMs?: number;
}

const alertStyles = {
  success: "bg-green-500 text-white",
  error: "bg-red-500 text-white",
  warning: "bg-yellow-500 text-white",
  info: "bg-blue-500 text-white",
};

const ToastItem: React.FC<{
  data: FeedbackMessage;
  onClose: (id: string) => void;
  duration: number;
  index: number;
  total: number;
}> = ({ data, onClose, duration }) => {
  const [show, setShow] = useState(true);
  const handleClose = useCallback(() => {
    setShow(false);
    setTimeout(() => onClose(data.id), 250);
  }, [data.id, onClose]);
  useEffect(() => {
    const t = setTimeout(() => handleClose(), duration);
    return () => clearTimeout(t);
  }, [handleClose, duration]);
  return (
    <Transition
      show={show}
      as={Fragment}
      enter="transition ease-out duration-300"
      enterFrom="transform opacity-0 translate-y-2 scale-95"
      enterTo="transform opacity-100 translate-y-0 scale-100"
      leave="transition ease-in duration-250"
      leaveFrom="transform opacity-100 translate-y-0 scale-100"
      leaveTo="transform opacity-0 -translate-y-2 scale-95"
    >
      <div
        className={clsx(
          "rounded-md shadow-lg p-4 flex items-center justify-between w-full",
          alertStyles[data.type]
        )}
      >
        <p className="text-sm font-medium pr-2 flex-1">{data.message}</p>
        <button
          onClick={handleClose}
          className="ml-2 p-1 rounded-full hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white"
        >
          <svg
            className="h-4 w-4"
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
  );
};

const UserFeedback: React.FC<UserFeedbackProps> = ({
  messages,
  onClose,
  maxVisible = 4,
  defaultDurationMs = 4000,
}) => {
  if (!messages.length) return null;
  const visible = messages.slice(-maxVisible); // dernières
  return (
    <div className="fixed top-5 left-1/2 -translate-x-1/2 z-50 w-full max-w-md px-4 space-y-3 flex flex-col">
      {visible.map((m) => (
        <ToastItem
          key={m.id}
          data={m}
          onClose={onClose}
          duration={m.duration || defaultDurationMs}
          index={0}
          total={visible.length}
        />
      ))}
    </div>
  );
};

// Hook pour gérer les messages de feedback
export const useUserFeedback = () => {
  const [messages, setMessages] = useState<FeedbackMessage[]>([]);
  const MAX_QUEUE = 30;

  const addMessage = (
    message: string,
    type: FeedbackType = "info",
    duration?: number
  ) => {
    setMessages((prev) => {
      const last = prev[prev.length - 1];
      if (last && last.message === message && last.type === type) {
        return prev; // dédup basique
      }
      const id = Date.now().toString();
      const next = [...prev, { id, message, type, duration }];
      if (next.length > MAX_QUEUE) return next.slice(next.length - MAX_QUEUE);
      return next;
    });
    return Date.now().toString();
  };

  const removeMessage = (id: string) =>
    setMessages((prev) => prev.filter((m) => m.id !== id));

  const showSuccess = (message: string, duration?: number) => {
    return addMessage(message, "success", duration);
  };

  const showError = (message: string, duration?: number) => {
    return addMessage(message, "error", duration);
  };

  const showWarning = (message: string, duration?: number) => {
    return addMessage(message, "warning", duration);
  };

  const showInfo = (message: string, duration?: number) => {
    return addMessage(message, "info", duration);
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
