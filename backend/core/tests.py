from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import List, ListItem, VersusMatch, VersusParticipant, VersusRound, VersusVote
import json


class VersusMatchModelTests(TestCase):
    """Tests for VersusMatch model functionality"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='test123')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='test123')
        
        # Create test lists and items
        self.list1 = List.objects.create(
            name="Films User1", 
            category=List.Category.FILMS,
            owner=self.user1
        )
        self.list2 = List.objects.create(
            name="Films User2", 
            category=List.Category.FILMS,
            owner=self.user2
        )
        
        self.item1 = ListItem.objects.create(
            title="Inception",
            description="Science fiction film",
            list=self.list1,
            position=1
        )
        self.item2 = ListItem.objects.create(
            title="Matrix",
            description="Cyberpunk film", 
            list=self.list2,
            position=1
        )
    
    def test_create_versus_match(self):
        """Test creating a new versus match"""
        match = VersusMatch.objects.create(
            category=List.Category.FILMS,
            created_by=self.user1,
            max_rounds=5
        )
        
        self.assertEqual(match.status, VersusMatch.Status.WAITING)
        self.assertEqual(match.current_round, 1)
        self.assertFalse(match.completed)
        self.assertEqual(match.max_rounds, 5)
    
    def test_add_participants(self):
        """Test adding participants to a match"""
        match = VersusMatch.objects.create(
            category=List.Category.FILMS,
            created_by=self.user1
        )
        
        # Add participants
        participant1 = VersusParticipant.objects.create(match=match, user=self.user1)
        participant2 = VersusParticipant.objects.create(match=match, user=self.user2)
        
        self.assertEqual(match.participants.count(), 2)
        self.assertTrue(match.is_participant(self.user1))
        self.assertTrue(match.is_participant(self.user2))
        self.assertTrue(match.can_start())
    
    def test_create_round(self):
        """Test creating a round in a match"""
        match = VersusMatch.objects.create(
            category=List.Category.FILMS,
            created_by=self.user1
        )
        
        round_obj = VersusRound.objects.create(
            match=match,
            round_number=1,
            item1=self.item1,
            item2=self.item2
        )
        
        self.assertEqual(round_obj.status, VersusRound.Status.PENDING)
        self.assertEqual(round_obj.round_number, 1)
        self.assertIsNone(round_obj.winner_item)
    
    def test_vote_in_round(self):
        """Test voting in a round"""
        match = VersusMatch.objects.create(
            category=List.Category.FILMS,
            created_by=self.user1,
            status=VersusMatch.Status.ACTIVE
        )
        
        participant1 = VersusParticipant.objects.create(match=match, user=self.user1)
        participant2 = VersusParticipant.objects.create(match=match, user=self.user2)
        
        round_obj = VersusRound.objects.create(
            match=match,
            round_number=1,
            item1=self.item1,
            item2=self.item2,
            status=VersusRound.Status.ACTIVE
        )
        
        # Vote for item1
        vote1 = VersusVote.objects.create(
            round=round_obj,
            participant=participant1,
            chosen_item=self.item1
        )
        
        vote2 = VersusVote.objects.create(
            round=round_obj,
            participant=participant2,
            chosen_item=self.item1
        )
        
        self.assertEqual(round_obj.votes.count(), 2)
        self.assertEqual(round_obj.votes.filter(chosen_item=self.item1).count(), 2)
    
    def test_mark_round_completed(self):
        """Test marking a round as completed"""
        match = VersusMatch.objects.create(
            category=List.Category.FILMS,
            created_by=self.user1
        )
        
        round_obj = VersusRound.objects.create(
            match=match,
            round_number=1,
            item1=self.item1,
            item2=self.item2
        )
        
        round_obj.mark_completed(self.item1)
        round_obj.refresh_from_db()
        
        self.assertEqual(round_obj.status, VersusRound.Status.COMPLETED)
        self.assertEqual(round_obj.winner_item, self.item1)
        self.assertIsNotNone(round_obj.completed_at)
    
    def test_mark_match_completed(self):
        """Test marking a match as completed"""
        match = VersusMatch.objects.create(
            category=List.Category.FILMS,
            created_by=self.user1
        )
        
        match.mark_completed()
        match.refresh_from_db()
        
        self.assertEqual(match.status, VersusMatch.Status.COMPLETED)
        self.assertTrue(match.completed)
        self.assertIsNotNone(match.completed_at)


class VersusMatchAPITests(APITestCase):
    """Tests for versus match API endpoints"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='test123')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='test123')
        self.user3 = User.objects.create_user(username='user3', email='user3@test.com', password='test123')
        
        # Create test lists and items
        self.list1 = List.objects.create(
            name="Films User1", 
            category=List.Category.FILMS,
            owner=self.user1
        )
        
        self.item1 = ListItem.objects.create(
            title="Inception",
            description="Science fiction film",
            list=self.list1,
            position=1
        )
        self.item2 = ListItem.objects.create(
            title="Matrix",
            description="Cyberpunk film", 
            list=self.list1,
            position=2
        )
        
        # Create a test match
        self.match = VersusMatch.objects.create(
            category=List.Category.FILMS,
            created_by=self.user1,
            status=VersusMatch.Status.ACTIVE
        )
        
        # Add participants
        self.participant1 = VersusParticipant.objects.create(match=self.match, user=self.user1, score=5)
        self.participant2 = VersusParticipant.objects.create(match=self.match, user=self.user2, score=3)
        
        # Create a round
        self.round1 = VersusRound.objects.create(
            match=self.match,
            round_number=1,
            item1=self.item1,
            item2=self.item2,
            status=VersusRound.Status.ACTIVE
        )
        
        # Add votes
        VersusVote.objects.create(
            round=self.round1,
            participant=self.participant1,
            chosen_item=self.item1
        )
    
    def get_jwt_token(self, user):
        """Get JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def test_get_match_state_as_participant(self):
        """Test getting match state as a participant"""
        # Use user2 who hasn't voted yet
        token = self.get_jwt_token(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('get_versus_match_state', kwargs={'match_id': self.match.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Check basic match information
        self.assertEqual(data['id'], self.match.id)
        self.assertEqual(data['category'], 'FILMS')
        self.assertEqual(data['status'], 'ACTIVE')
        self.assertEqual(data['current_round'], 1)
        self.assertFalse(data['completed'])
        self.assertTrue(data['is_participant'])
        self.assertTrue(data['can_vote'])  # user2 hasn't voted yet
        
        # Check participants
        self.assertEqual(len(data['participants']), 2)
        participant_usernames = [p['username'] for p in data['participants']]
        self.assertIn('user1', participant_usernames)
        self.assertIn('user2', participant_usernames)
        
        # Check current round data
        self.assertIsNotNone(data['current_round_data'])
        round_data = data['current_round_data']
        self.assertEqual(round_data['round_number'], 1)
        self.assertEqual(round_data['status'], 'ACTIVE')
        self.assertIsNotNone(round_data['item1'])
        self.assertIsNotNone(round_data['item2'])
        self.assertEqual(round_data['item1']['title'], 'Inception')
        self.assertEqual(round_data['item2']['title'], 'Matrix')
        
        # Check votes count
        self.assertIsNotNone(round_data['votes_count'])
        self.assertEqual(round_data['votes_count']['item1'], 1)
        self.assertEqual(round_data['votes_count']['item2'], 0)
        self.assertEqual(round_data['votes_count']['total'], 1)
        
        # Check user vote (user2 hasn't voted yet)
        self.assertIsNone(round_data['user_vote'])
    
    def test_get_match_state_as_participant_who_already_voted(self):
        """Test getting match state as a participant who already voted"""
        # Use user1 who has already voted
        token = self.get_jwt_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('get_versus_match_state', kwargs={'match_id': self.match.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Check basic match information
        self.assertTrue(data['is_participant'])
        self.assertFalse(data['can_vote'])  # user1 has already voted
        
        # Check current round data
        round_data = data['current_round_data']
        
        # Check user vote (user1 voted for item1)
        self.assertEqual(round_data['user_vote'], self.item1.id)
    
    def test_get_match_state_as_non_participant(self):
        """Test getting match state as a non-participant (filtered view)"""
        token = self.get_jwt_token(self.user3)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('get_versus_match_state', kwargs={'match_id': self.match.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Check basic match information
        self.assertEqual(data['id'], self.match.id)
        self.assertFalse(data['is_participant'])
        self.assertFalse(data['can_vote'])
        
        # Check filtered participants (should only show username and score)
        self.assertEqual(len(data['participants']), 2)
        for participant in data['participants']:
            self.assertIn('username', participant)
            self.assertIn('score', participant)
            # Sensitive data should be filtered out for non-participants
            self.assertNotIn('user_id', participant)
            self.assertNotIn('joined_at', participant)
        
        # Check current round data (user_vote should be filtered out)
        if data.get('current_round_data'):
            round_data = data['current_round_data']
            self.assertNotIn('user_vote', round_data)
    
    def test_get_match_state_nonexistent_match(self):
        """Test getting state of non-existent match"""
        token = self.get_jwt_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('get_versus_match_state', kwargs={'match_id': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertIn('error', data)
    
    def test_get_match_state_unauthenticated(self):
        """Test getting match state without authentication"""
        url = reverse('get_versus_match_state', kwargs={'match_id': self.match.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_completed_match_state(self):
        """Test getting state of a completed match"""
        # Mark match as completed
        self.match.mark_completed()
        
        token = self.get_jwt_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('get_versus_match_state', kwargs={'match_id': self.match.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['status'], 'COMPLETED')
        self.assertTrue(data['completed'])
        self.assertFalse(data['can_vote'])
        self.assertIsNotNone(data['completed_at'])
        # No current round data for completed matches
        self.assertIsNone(data['current_round_data'])
    
    def test_match_progression_workflow(self):
        """Test the complete workflow of match progression"""
        token = self.get_jwt_token(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Initial state - user2 can vote
        url = reverse('get_versus_match_state', kwargs={'match_id': self.match.id})
        response = self.client.get(url)
        data = response.json()
        
        self.assertTrue(data['can_vote'])
        self.assertEqual(data['current_round'], 1)
        
        # After user2 votes, they shouldn't be able to vote again
        VersusVote.objects.create(
            round=self.round1,
            participant=self.participant2,
            chosen_item=self.item2
        )
        
        # Check state after vote
        response = self.client.get(url)
        data = response.json()
        
        # user2 should no longer be able to vote in this round
        self.assertFalse(data['can_vote'])
        
        # Vote counts should be updated
        round_data = data['current_round_data']
        self.assertEqual(round_data['votes_count']['item1'], 1)
        self.assertEqual(round_data['votes_count']['item2'], 1)
        self.assertEqual(round_data['votes_count']['total'], 2)


# Create your tests here.
