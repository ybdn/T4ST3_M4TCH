#!/usr/bin/env python3
"""
Script de vérification des endpoints clés - Pré-Bêta T4ST3_M4TCH
Usage: python verify_endpoints.py [base_url]
"""

import sys
import requests
import json
from datetime import datetime


class EndpointVerifier:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.auth_token = None
        self.results = []
        
    def log_result(self, endpoint, status, message, details=None):
        """Enregistre le résultat d'un test d'endpoint"""
        result = {
            'endpoint': endpoint,
            'status': '✅' if status == 'PASS' else '❌' if status == 'FAIL' else '⚠️',
            'result': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.results.append(result)
        print(f"{result['status']} {endpoint}: {message}")
        
    def test_health_check(self):
        """Test de l'endpoint health check"""
        try:
            response = self.session.get(f"{self.base_url}/api/health/")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    self.log_result('/api/health/', 'PASS', 'Health check OK')
                else:
                    self.log_result('/api/health/', 'FAIL', f'Réponse inattendue: {data}')
            else:
                self.log_result('/api/health/', 'FAIL', f'Status {response.status_code}')
        except Exception as e:
            self.log_result('/api/health/', 'FAIL', f'Erreur: {str(e)}')
    
    def test_registration(self):
        """Test de l'endpoint d'inscription"""
        try:
            test_user = {
                'username': f'testuser_{int(datetime.now().timestamp())}',
                'email': f'test_{int(datetime.now().timestamp())}@example.com',
                'password': 'testpass123!',
                'password2': 'testpass123!'
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/register/",
                json=test_user
            )
            
            if response.status_code == 201:
                data = response.json()
                self.log_result('/api/auth/register/', 'PASS', 'Inscription OK', 
                              {'user_created': data.get('username')})
            else:
                self.log_result('/api/auth/register/', 'FAIL', 
                              f'Status {response.status_code}: {response.text[:100]}')
        except Exception as e:
            self.log_result('/api/auth/register/', 'FAIL', f'Erreur: {str(e)}')
    
    def test_login_and_get_token(self):
        """Test de connexion et récupération du token"""
        try:
            # Créer un utilisateur test d'abord
            test_user = {
                'username': f'logintest_{int(datetime.now().timestamp())}',
                'email': f'login_{int(datetime.now().timestamp())}@example.com',
                'password': 'logintest123!',
                'password2': 'logintest123!'
            }
            
            reg_response = self.session.post(
                f"{self.base_url}/api/auth/register/",
                json=test_user
            )
            
            if reg_response.status_code != 201:
                self.log_result('/api/auth/token/', 'SKIP', 'Impossible de créer l\'utilisateur test')
                return
                
            # Tenter la connexion
            login_data = {
                'username': test_user['username'],
                'password': test_user['password']
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/token/",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access' in data and 'refresh' in data:
                    self.auth_token = data['access']
                    self.log_result('/api/auth/token/', 'PASS', 'Connexion JWT OK')
                else:
                    self.log_result('/api/auth/token/', 'FAIL', 'Tokens manquants dans la réponse')
            else:
                self.log_result('/api/auth/token/', 'FAIL', 
                              f'Status {response.status_code}: {response.text[:100]}')
        except Exception as e:
            self.log_result('/api/auth/token/', 'FAIL', f'Erreur: {str(e)}')
    
    def test_user_profile(self):
        """Test de récupération du profil utilisateur"""
        if not self.auth_token:
            self.log_result('/api/users/me/', 'SKIP', 'Aucun token d\'authentification')
            return
            
        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            response = self.session.get(f"{self.base_url}/api/users/me/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'username' in data and 'email' in data:
                    self.log_result('/api/users/me/', 'PASS', 'Profil utilisateur OK')
                else:
                    self.log_result('/api/users/me/', 'FAIL', 'Données de profil incomplètes')
            else:
                self.log_result('/api/users/me/', 'FAIL', f'Status {response.status_code}')
        except Exception as e:
            self.log_result('/api/users/me/', 'FAIL', f'Erreur: {str(e)}')
    
    def test_lists_endpoint(self):
        """Test de l'endpoint des listes"""
        if not self.auth_token:
            self.log_result('/api/lists/', 'SKIP', 'Aucun token d\'authentification')
            return
            
        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            response = self.session.get(f"{self.base_url}/api/lists/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= 4:
                    categories = [item.get('category') for item in data]
                    expected_categories = ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']
                    if all(cat in categories for cat in expected_categories):
                        self.log_result('/api/lists/', 'PASS', 
                                      f'Listes auto-créées OK ({len(data)} listes)')
                    else:
                        self.log_result('/api/lists/', 'WARN', 
                                      f'Catégories manquantes: {set(expected_categories) - set(categories)}')
                else:
                    self.log_result('/api/lists/', 'FAIL', f'Données de listes inattendues: {len(data) if isinstance(data, list) else type(data)}')
            else:
                self.log_result('/api/lists/', 'FAIL', f'Status {response.status_code}')
        except Exception as e:
            self.log_result('/api/lists/', 'FAIL', f'Erreur: {str(e)}')
    
    def test_external_search(self):
        """Test de recherche externe (sans clés API)"""
        if not self.auth_token:
            self.log_result('/api/search/external/', 'SKIP', 'Aucun token d\'authentification')
            return
            
        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            params = {'query': 'test', 'type': 'movie'}
            response = self.session.get(
                f"{self.base_url}/api/search/external/",
                headers=headers,
                params=params
            )
            
            # Accepter 200 (clés configurées) ou 400/503 (clés manquantes)
            if response.status_code in [200, 400, 503]:
                if response.status_code == 200:
                    self.log_result('/api/search/external/', 'PASS', 'Recherche externe OK (APIs configurées)')
                else:
                    self.log_result('/api/search/external/', 'WARN', 
                                  f'Endpoint fonctionnel mais APIs non configurées (Status {response.status_code})')
            else:
                self.log_result('/api/search/external/', 'FAIL', f'Status inattendu {response.status_code}')
        except Exception as e:
            self.log_result('/api/search/external/', 'FAIL', f'Erreur: {str(e)}')
    
    def test_trending_external(self):
        """Test de contenu tendance externe"""
        if not self.auth_token:
            self.log_result('/api/trending/external/', 'SKIP', 'Aucun token d\'authentification')
            return
            
        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            params = {'type': 'movie'}
            response = self.session.get(
                f"{self.base_url}/api/trending/external/",
                headers=headers,
                params=params
            )
            
            if response.status_code in [200, 400, 503]:
                if response.status_code == 200:
                    self.log_result('/api/trending/external/', 'PASS', 'Tendances externes OK')
                else:
                    self.log_result('/api/trending/external/', 'WARN', 
                                  f'Endpoint fonctionnel mais APIs non configurées (Status {response.status_code})')
            else:
                self.log_result('/api/trending/external/', 'FAIL', f'Status inattendu {response.status_code}')
        except Exception as e:
            self.log_result('/api/trending/external/', 'FAIL', f'Erreur: {str(e)}')
    
    def run_all_tests(self):
        """Exécute tous les tests d'endpoints"""
        print(f"🔍 Vérification des endpoints - {self.base_url}")
        print("=" * 60)
        
        # Tests dans l'ordre logique
        self.test_health_check()
        self.test_registration()
        self.test_login_and_get_token()
        self.test_user_profile()
        self.test_lists_endpoint()
        self.test_external_search()
        self.test_trending_external()
        
        # Résumé
        print("\n" + "=" * 60)
        total = len(self.results)
        passed = sum(1 for r in self.results if r['result'] == 'PASS')
        failed = sum(1 for r in self.results if r['result'] == 'FAIL')
        warned = sum(1 for r in self.results if r['result'] == 'WARN')
        skipped = sum(1 for r in self.results if r['result'] == 'SKIP')
        
        print(f"📊 RÉSUMÉ: {passed}✅ {failed}❌ {warned}⚠️ {skipped}⏭️ sur {total} tests")
        
        if failed == 0:
            print("🎉 Tous les endpoints critiques fonctionnent !")
        else:
            print("⚠️ Des endpoints critiques nécessitent une attention")
            
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'warned': warned,
            'skipped': skipped,
            'results': self.results
        }


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print("🚀 Vérification Endpoints Pré-Bêta T4ST3_M4TCH")
    print(f"🌐 URL de base: {base_url}")
    print()
    
    verifier = EndpointVerifier(base_url)
    summary = verifier.run_all_tests()
    
    # Sauvegarder les résultats en JSON
    with open('/tmp/endpoint_verification.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'base_url': base_url,
            'summary': summary
        }, f, indent=2)
    
    print(f"\n📄 Résultats détaillés sauvés dans: /tmp/endpoint_verification.json")
    
    # Code de sortie basé sur les échecs
    return 1 if summary['failed'] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())