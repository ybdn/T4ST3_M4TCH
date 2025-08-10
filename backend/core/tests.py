from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import List, ListItem, VersusMatch, VersusRound, VersusChoice


class VersusMatchTestCase(APITestCase):
    """Tests pour la fonctionnalité versus match"""
    
    def setUp(self):
        """Configuration des tests"""
        # Créer des utilisateurs de test
        self.user1 = User.objects.create_user(
            username='player1',
            email='player1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='player2', 
            email='player2@test.com',
            password='testpass123'
        )
        
        # Créer des listes et éléments de test
        self.list1 = List.objects.create(
            name='Films Player 1',
            category='FILMS',
            owner=self.user1
        )
        self.list2 = List.objects.create(
            name='Films Player 2',
            category='FILMS',
            owner=self.user2
        )
        
        # Créer des éléments de test
        self.item1 = ListItem.objects.create(
            title='Film A',
            description='Premier film',
            list=self.list1,
            position=1
        )
        self.item2 = ListItem.objects.create(
            title='Film B',
            description='Deuxième film',
            list=self.list2,
            position=1
        )
        
        # Créer un match de test
        self.match = VersusMatch.objects.create(
            player1=self.user1,
            player2=self.user2,
            category='FILMS',
            status=VersusMatch.Status.ACTIVE
        )
        
        # Créer un round de test
        self.round = VersusRound.objects.create(
            match=self.match,
            round_number=1,
            item1=self.item1,
            item2=self.item2,
            status=VersusRound.Status.ACTIVE
        )
        
        # Client API
        self.client = APIClient()
    
    def test_submit_valid_choice(self):
        """Test de soumission d'un choix valide"""
        # S'authentifier en tant que player1
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('submit_versus_choice', kwargs={'match_id': self.match.id})
        data = {'chosen_item_id': self.item1.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['choice_submitted'])
        self.assertFalse(response.data['round_completed'])
        self.assertTrue(response.data['waiting_for_other_player'])
        
        # Vérifier que le choix a été créé
        choice = VersusChoice.objects.get(round=self.round, player=self.user1)
        self.assertEqual(choice.chosen_item, self.item1)
    
    def test_submit_double_choice_error(self):
        """Test d'erreur de double soumission"""
        # Créer un choix existant
        VersusChoice.objects.create(
            round=self.round,
            player=self.user1,
            chosen_item=self.item1
        )
        
        # S'authentifier et essayer de soumettre un autre choix
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('submit_versus_choice', kwargs={'match_id': self.match.id})
        data = {'chosen_item_id': self.item2.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('déjà fait votre choix', response.data['error'])
    
    def test_submit_invalid_item_error(self):
        """Test d'erreur avec un élément invalide"""
        # Créer un autre élément qui ne fait pas partie du round
        invalid_item = ListItem.objects.create(
            title='Film C',
            description='Film non valide',
            list=self.list1,
            position=2
        )
        
        # S'authentifier et essayer de soumettre ce choix
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('submit_versus_choice', kwargs={'match_id': self.match.id})
        data = {'chosen_item_id': invalid_item.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ne fait pas partie de ce round', response.data['error'])
    
    def test_unauthorized_player_error(self):
        """Test d'erreur pour un joueur non autorisé"""
        # Créer un troisième utilisateur
        user3 = User.objects.create_user(
            username='player3',
            email='player3@test.com',
            password='testpass123'
        )
        
        # S'authentifier en tant que player3
        self.client.force_authenticate(user=user3)
        
        url = reverse('submit_versus_choice', kwargs={'match_id': self.match.id})
        data = {'chosen_item_id': self.item1.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('ne participez pas', response.data['error'])
    
    def test_complete_round_both_liked_same(self):
        """Test de complétion de round avec like/like"""
        # Premier choix (player1 choisit item1)
        self.client.force_authenticate(user=self.user1)
        url = reverse('submit_versus_choice', kwargs={'match_id': self.match.id})
        data = {'chosen_item_id': self.item1.id}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Deuxième choix (player2 choisit aussi item1 - same choice)
        self.client.force_authenticate(user=self.user2)
        data = {'chosen_item_id': self.item1.id}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['choice_submitted'])
        self.assertTrue(response.data['round_completed'])
        self.assertTrue(response.data['both_liked_same'])
        
        # Vérifier que les scores ont été mis à jour
        self.match.refresh_from_db()
        self.assertEqual(self.match.player1_score, 1)
        self.assertEqual(self.match.player2_score, 1)
        self.assertEqual(self.match.current_round, 2)
    
    def test_complete_round_different_choices(self):
        """Test de complétion de round avec choix différents"""
        # Premier choix (player1 choisit item1)
        self.client.force_authenticate(user=self.user1)
        url = reverse('submit_versus_choice', kwargs={'match_id': self.match.id})
        data = {'chosen_item_id': self.item1.id}
        response = self.client.post(url, data, format='json')
        
        # Deuxième choix (player2 choisit item2)
        self.client.force_authenticate(user=self.user2)
        data = {'chosen_item_id': self.item2.id}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['choice_submitted'])
        self.assertTrue(response.data['round_completed'])
        self.assertFalse(response.data['both_liked_same'])
        
        # Vérifier que les scores n'ont pas changé
        self.match.refresh_from_db()
        self.assertEqual(self.match.player1_score, 0)
        self.assertEqual(self.match.player2_score, 0)
        self.assertEqual(self.match.current_round, 2)
    
    def test_match_not_found_error(self):
        """Test d'erreur pour un match inexistant"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('submit_versus_choice', kwargs={'match_id': 9999})
        data = {'chosen_item_id': self.item1.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Match non trouvé', response.data['error'])
    
    def test_inactive_match_error(self):
        """Test d'erreur pour un match inactif"""
        # Changer le statut du match
        self.match.status = VersusMatch.Status.COMPLETED
        self.match.save()
        
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('submit_versus_choice', kwargs={'match_id': self.match.id})
        data = {'chosen_item_id': self.item1.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('non actif', response.data['error'])


class VersusModelTestCase(TestCase):
    """Tests pour les modèles versus"""
    
    def setUp(self):
        """Configuration des tests"""
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com')
        
        self.list1 = List.objects.create(name='List 1', category='FILMS', owner=self.user1)
        self.item1 = ListItem.objects.create(title='Item 1', list=self.list1, position=1)
        self.item2 = ListItem.objects.create(title='Item 2', list=self.list1, position=2)
    
    def test_versus_match_model(self):
        """Test du modèle VersusMatch"""
        match = VersusMatch.objects.create(
            player1=self.user1,
            player2=self.user2,
            category='FILMS'
        )
        
        self.assertEqual(str(match), f"{self.user1.username} vs {self.user2.username} (Films)")
        self.assertTrue(match.is_player(self.user1))
        self.assertTrue(match.is_player(self.user2))
        self.assertEqual(match.get_players(), [self.user1, self.user2])
    
    def test_versus_round_model(self):
        """Test du modèle VersusRound"""
        match = VersusMatch.objects.create(
            player1=self.user1,
            player2=self.user2,
            category='FILMS'
        )
        
        round_obj = VersusRound.objects.create(
            match=match,
            round_number=1,
            item1=self.item1,
            item2=self.item2
        )
        
        self.assertEqual(str(round_obj), f"Round 1 - {self.item1.title} vs {self.item2.title}")
        self.assertEqual(round_obj.get_items(), [self.item1, self.item2])
        self.assertFalse(round_obj.has_player_chosen(self.user1))
        self.assertFalse(round_obj.is_complete())
    
    def test_versus_choice_model(self):
        """Test du modèle VersusChoice"""
        match = VersusMatch.objects.create(
            player1=self.user1,
            player2=self.user2,
            category='FILMS'
        )
        
        round_obj = VersusRound.objects.create(
            match=match,
            round_number=1,
            item1=self.item1,
            item2=self.item2
        )
        
        choice = VersusChoice.objects.create(
            round=round_obj,
            player=self.user1,
            chosen_item=self.item1
        )
        
        self.assertEqual(str(choice), f"{self.user1.username} choisit {self.item1.title}")
        self.assertTrue(round_obj.has_player_chosen(self.user1))
        self.assertFalse(round_obj.is_complete())  # Besoin du deuxième choix
