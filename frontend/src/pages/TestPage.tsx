import React from 'react';
import type { FriendUser } from '../types/match';

const TestPage: React.FC = () => {
  // FriendUser is a type only; ensure no runtime reference
  
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl mb-4">Test FriendUser Import</h1>
        <p>Import Status: ✅ SUCCESS</p>
      </div>
    </div>
  );
};

export default TestPage;