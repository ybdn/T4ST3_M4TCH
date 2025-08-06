import React from 'react';
import Dashboard from './components/Dashboard';

function App() {
  const handleNavigate = (section: string) => {
    console.log(`Navigation vers: ${section}`);
    // TODO: Implémenter la navigation entre les sections
  };

  return <Dashboard onNavigate={handleNavigate} />;
}

export default App;
