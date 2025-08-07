from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from .serializers import RegisterSerializer, ListSerializer
from .models import List
from .permissions import IsOwnerOrReadOnly

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Returns a simple JSON response to indicate that the API is running.
    """
    return Response(
        {"status": "ok", "message": "API is running"},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })


class ListViewSet(viewsets.ModelViewSet):
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        # Un utilisateur ne peut voir que ses propres listes
        return List.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        # Automatiquement définir le propriétaire comme l'utilisateur courant
        serializer.save(owner=self.request.user)