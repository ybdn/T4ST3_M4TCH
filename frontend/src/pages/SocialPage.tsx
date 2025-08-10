import React, { useState } from 'react';
import AppHeader from '../components/AppHeader';
import AppBottomNav from '../components/AppBottomNav';
import FriendsManager from '../components/FriendsManager';

interface SocialPageProps {
  onNavigate?: (section: string) => void;
}

const SocialPage: React.FC<SocialPageProps> = ({ onNavigate }) => {
  const [bottomNavValue, setBottomNavValue] = useState(0);

  const handleBottomNavChange = (_event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'profil'];
    onNavigate?.(sections[newValue]);
  };

  return (
    <div className="min-h-screen tm-auth-bg font-inter">
      <AppHeader title="Social" onBack={() => onNavigate?.('accueil')} />

      <div className="h-[calc(100vh-4rem)] overflow-y-auto pb-20">
        <div className="w-full max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <FriendsManager />
        </div>
      </div>

      <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />
    </div>
  );
};

export default SocialPage;


