import React from 'react';

interface BookIconProps {
  size?: number;
  color?: string;
  className?: string;
}

const BookIcon: React.FC<BookIconProps> = ({ size = 32, color = 'white', className }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Book with artistic details */}
      <g stroke={color} strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
        {/* Main book */}
        <path d="M6 4h16c1 0 2 1 2 2v20c0 1-1 2-2 2H6" />
        <path d="M6 4c-1 0-2 1-2 2v20c0 1 1 2 2 2" />
        
        {/* Book spine */}
        <line x1="6" y1="4" x2="6" y2="28" strokeWidth="2" />
        
        {/* Pages effect */}
        <path d="M8 6h12" strokeWidth="0.8" opacity="0.7" />
        <path d="M8 9h10" strokeWidth="0.8" opacity="0.7" />
        <path d="M8 12h12" strokeWidth="0.8" opacity="0.7" />
        <path d="M8 15h8" strokeWidth="0.8" opacity="0.7" />
        <path d="M8 18h11" strokeWidth="0.8" opacity="0.7" />
        <path d="M8 21h9" strokeWidth="0.8" opacity="0.7" />
        <path d="M8 24h7" strokeWidth="0.8" opacity="0.7" />
        
        {/* Bookmark */}
        <path d="M18 4v8l2-1.5L22 12V4" fill={color} />
        
        {/* Decorative corner */}
        <path d="M22 6l-2 2" strokeWidth="1" opacity="0.8" />
        <circle cx="21" cy="7" r="0.5" fill={color} />
        
        {/* Reading glasses resting on book */}
        <g strokeWidth="1" opacity="0.6">
          <circle cx="12" cy="14" r="2.5" />
          <circle cx="18" cy="14" r="2.5" />
          <path d="M14.5 14h1" />
          <path d="M9.5 14l-1-0.5" />
          <path d="M20.5 14l1-0.5" />
        </g>
        
        {/* Magical sparkles */}
        <g fill={color} opacity="0.7">
          <circle cx="26" cy="8" r="0.5" />
          <circle cx="28" cy="12" r="0.3" />
          <circle cx="25" cy="16" r="0.4" />
          <path d="M27 20l0.5-1.5L29 19l-1.5 0.5L27 20z" />
        </g>
      </g>
    </svg>
  );
};

export default BookIcon;