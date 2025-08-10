from typing import Optional, List, Dict
from django.contrib.auth.models import User
from core.models import UserProfile, UserPreference, Friendship


def ensure_profile(user: User, fixed_gamertag: Optional[str] = None) -> UserProfile:
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if fixed_gamertag and profile.gamertag != fixed_gamertag:
        profile.gamertag = fixed_gamertag
        profile.save()
    return profile


def create_fake_user(username: str, password: str = "password123", email: str = "") -> User:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email}
    )
    if created:
        user.set_password(password)
        user.save()
    ensure_profile(user)
    return user


def add_likes(user: User, items: List[Dict]):
    for item in items:
        UserPreference.objects.update_or_create(
            user=user,
            external_id=item["external_id"],
            source=item["source"],
            defaults={
                "content_type": item["content_type"],
                "action": "liked",
                "title": item["title"],
                "metadata": item.get("metadata", {}),
            },
        )


def ensure_friend(user1: User, user2: User):
    friendship = (
        Friendship.objects.filter(requester=user1, addressee=user2).first()
        or Friendship.objects.filter(requester=user2, addressee=user1).first()
    )
    if friendship:
        if friendship.status != Friendship.Status.ACCEPTED:
            friendship.status = Friendship.Status.ACCEPTED
            friendship.save()
    else:
        Friendship.objects.create(
            requester=user1,
            addressee=user2,
            status=Friendship.Status.ACCEPTED,
        )


def main(target_gamertag: str = "TM_YPCA"):
    # Trouver l'utilisateur cible par gamertag, sinon fallback par username 'ybdn'
    target_profile = UserProfile.objects.filter(gamertag=target_gamertag).first()
    if not target_profile:
        owner = User.objects.filter(username="ybdn").first()
        if not owner:
            owner = User.objects.create_user("ybdn", "", "password123")
        target_profile = ensure_profile(owner, target_gamertag)
    me = target_profile.user

    # Contenu d'exemple (IDs plausibles)
    items_movies = [
        {
            "external_id": "603",
            "source": "tmdb",
            "content_type": "FILMS",
            "title": "The Matrix",
            "metadata": {"genre_ids": [28, 878], "popularity": 98},
        },
        {
            "external_id": "27205",
            "source": "tmdb",
            "content_type": "FILMS",
            "title": "Inception",
            "metadata": {"genre_ids": [28, 878, 53], "popularity": 92},
        },
    ]
    items_series = [
        {
            "external_id": "1399",
            "source": "tmdb",
            "content_type": "SERIES",
            "title": "Game of Thrones",
            "metadata": {"genre_ids": [10765, 18], "popularity": 95},
        }
    ]
    items_music = [
        {
            "external_id": "spotify_001",
            "source": "spotify",
            "content_type": "MUSIQUE",
            "title": "Bohemian Rhapsody - Queen",
            "metadata": {"genres": ["rock"]},
        }
    ]
    items_books = [
        {
            "external_id": "zyTCAlFPjgYC",
            "source": "google_books",
            "content_type": "LIVRES",
            "title": "Harry Potter",
            "metadata": {"authors": ["J.K. Rowling"]},
        }
    ]

    # Création de faux utilisateurs
    alice = create_fake_user("alice")
    bob = create_fake_user("bob")
    claire = create_fake_user("claire")

    # Ajout de likes (variés) pour chacun
    add_likes(alice, items_movies + items_series)
    add_likes(bob, items_movies + items_music)
    add_likes(claire, items_series + items_books)

    # Amitiés acceptées avec l'utilisateur cible
    ensure_friend(me, alice)
    ensure_friend(me, bob)
    ensure_friend(me, claire)

    print("Seeded users:", [u.username for u in [alice, bob, claire]])
    print("Gamertags:", alice.profile.gamertag, bob.profile.gamertag, claire.profile.gamertag)


if __name__ == "__main__":
    main()


