import React from 'react';

interface FilmIconProps {
  size?: number;
  color?: string;
  className?: string;
}

const FilmIcon: React.FC<FilmIconProps> = ({ size = 32, color = 'white', className }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Film reel with artistic details */}
      <g stroke={color} strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
        {/* Main film strip */}
        <rect x="4" y="8" width="24" height="16" />
        
        {/* Film perforations - left side */}
        <rect x="4" y="10" width="2" height="1.5" fill={color} />
        <rect x="4" y="13" width="2" height="1.5" fill={color} />
        <rect x="4" y="16" width="2" height="1.5" fill={color} />
        <rect x="4" y="19" width="2" height="1.5" fill={color} />
        <rect x="4" y="22" width="2" height="1.5" fill={color} />
        
        {/* Film perforations - right side */}
        <rect x="26" y="10" width="2" height="1.5" fill={color} />
        <rect x="26" y="13" width="2" height="1.5" fill={color} />
        <rect x="26" y="16" width="2" height="1.5" fill={color} />
        <rect x="26" y="19" width="2" height="1.5" fill={color} />
        <rect x="26" y="22" width="2" height="1.5" fill={color} />
        
        {/* Film frames */}
        <rect x="8" y="10" width="4" height="3" />
        <rect x="14" y="10" width="4" height="3" />
        <rect x="20" y="10" width="4" height="3" />
        
        <rect x="8" y="19" width="4" height="3" />
        <rect x="14" y="19" width="4" height="3" />
        <rect x="20" y="19" width="4" height="3" />
        
        {/* Central artistic element - camera lens */}
        <circle cx="16" cy="16" r="3" />
        <circle cx="16" cy="16" r="1.5" fill={color} />
        
        {/* Decorative film curves */}
        <path d="M4 6c4 0 6 2 6 2s2-2 6-2s4 2 4 2s2-2 6-2" />
        <path d="M4 26c4 0 6-2 6-2s2 2 6 2s4-2 4-2s2 2 6 2" />
      </g>
    </svg>
  );
};

export default FilmIcon;