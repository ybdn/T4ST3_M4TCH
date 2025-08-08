import React from 'react';

interface MusicIconProps {
  size?: number;
  color?: string;
  className?: string;
}

const MusicIcon: React.FC<MusicIconProps> = ({ size = 32, color = 'white', className }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Musical note with artistic details */}
      <g stroke={color} strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
        {/* Vinyl record */}
        <circle cx="16" cy="16" r="12" />
        <circle cx="16" cy="16" r="8" strokeWidth="1" opacity="0.7" />
        <circle cx="16" cy="16" r="4" strokeWidth="1" opacity="0.5" />
        <circle cx="16" cy="16" r="1.5" fill={color} />
        
        {/* Musical notes floating around */}
        <g strokeWidth="1.2" fill={color}>
          {/* Note 1 */}
          <circle cx="6" cy="8" r="1.2" />
          <path d="M7.2 8v-4" />
          <path d="M7.2 4c0 0 2 0 3 1" />
          
          {/* Note 2 */}
          <circle cx="24" cy="10" r="1" />
          <path d="M25 10v-5" />
          <path d="M25 5c0 0 2 0 2.5 1.5" />
          
          {/* Note 3 */}
          <circle cx="26" cy="22" r="1" />
          <path d="M27 22v-4" />
          
          {/* Note 4 */}
          <circle cx="8" cy="26" r="1" />
          <path d="M9 26v-3" />
        </g>
        
        {/* Sound waves */}
        <path d="M2 16c0-2 1-4 2-4" strokeWidth="1" opacity="0.6" />
        <path d="M1 16c0-3 2-6 3-6" strokeWidth="1" opacity="0.4" />
        <path d="M30 16c0-2-1-4-2-4" strokeWidth="1" opacity="0.6" />
        <path d="M31 16c0-3-2-6-3-6" strokeWidth="1" opacity="0.4" />
        
        <path d="M2 16c0 2 1 4 2 4" strokeWidth="1" opacity="0.6" />
        <path d="M1 16c0 3 2 6 3 6" strokeWidth="1" opacity="0.4" />
        <path d="M30 16c0 2-1 4-2 4" strokeWidth="1" opacity="0.6" />
        <path d="M31 16c0 3-2 6-3 6" strokeWidth="1" opacity="0.4" />
        
        {/* Stylized treble clef in center */}
        <path d="M14 12c0 0 2-1 3 0s1 2 0 3s-2 1-2 2v3" strokeWidth="1.2" opacity="0.8" />
      </g>
    </svg>
  );
};

export default MusicIcon;