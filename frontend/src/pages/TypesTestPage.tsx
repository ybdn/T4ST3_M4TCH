import React from 'react';

// Test d'import direct de FriendUser
import type { FriendUser } from '../types/match';

const TypesTestPage: React.FC = () => {
  // Test que le type existe
  const testUser: FriendUser = {
    user_id: 1,
    username: "test",
    gamertag: "TM_TEST",
    display_name: "Test User",
    avatar_url: "test.jpg"
  };

  console.log('FriendUser test:', testUser);

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl mb-4">🧪</div>
        <h1 className="text-2xl font-bold mb-2">Test Types FriendUser</h1>
        <p className="text-gray-400">Import et utilisation directe</p>
        <div className="mt-4 text-xs text-gray-500">
          <div>FriendUser type: ✅ Défini</div>
          <div>Test object: {testUser ? '✅ Créé' : '❌ Échec'}</div>
          <div>Gamertag: {testUser.gamertag}</div>
        </div>
      </div>
    </div>
  );
};

export default TypesTestPage;