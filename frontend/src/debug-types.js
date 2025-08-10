// Test JavaScript simple pour vérifier les exports
try {
  const matchTypes = require('./types/match.ts');
  console.log('Types exports:', Object.keys(matchTypes));
  console.log('FriendUser présent:', 'FriendUser' in matchTypes);
} catch (error) {
  console.error('Erreur:', error.message);
}