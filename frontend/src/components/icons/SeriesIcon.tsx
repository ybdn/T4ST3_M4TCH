import React from 'react';

interface SeriesIconProps {
  size?: number;
  color?: string;
  className?: string;
}

const SeriesIcon: React.FC<SeriesIconProps> = ({ size = 32, color = 'white', className }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* TV/Series icon with artistic flair */}
      <g stroke={color} strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
        {/* TV screen */}
        <rect x="3" y="6" width="26" height="18" />
        <rect x="5" y="8" width="22" height="14" />
        
        {/* TV stand */}
        <path d="M12 24v3" />
        <path d="M20 24v3" />
        <path d="M8 27h16" />
        
        {/* Screen content - play button */}
        <polygon points="13,12 13,20 19,16" fill={color} />
        
        {/* Vintage TV details */}
        <circle cx="26" cy="9" r="1" fill={color} />
        <circle cx="26" cy="12" r="0.5" fill={color} />
        <circle cx="26" cy="15" r="0.5" fill={color} />
        
        {/* Signal waves */}
        <path d="M28 8c1 1 1 3 0 4" strokeWidth="1" />
        <path d="M29 6c2 2 2 6 0 8" strokeWidth="1" />
        
        {/* Decorative antenna */}
        <path d="M8 6l-2-3" />
        <path d="M12 6l2-4" />
        <circle cx="6" cy="3" r="0.5" fill={color} />
        <circle cx="14" cy="2" r="0.5" fill={color} />
        
        {/* Screen scanlines effect */}
        <line x1="6" y1="10" x2="26" y2="10" strokeWidth="0.5" opacity="0.6" />
        <line x1="6" y1="14" x2="26" y2="14" strokeWidth="0.5" opacity="0.6" />
        <line x1="6" y1="18" x2="26" y2="18" strokeWidth="0.5" opacity="0.6" />
      </g>
    </svg>
  );
};

export default SeriesIcon;