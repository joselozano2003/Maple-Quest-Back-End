from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from .models import *
from .serializers import *
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
import uuid


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow users to edit their own profile.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in ['GET']:
            return True
        
        # Write permissions only to the owner of the profile
        return obj.user_id == request.user.user_id


class IsOwner(BasePermission):
    """
    Custom permission to only allow users to access their own data.
    """
    def has_object_permission(self, request, view, obj):
        # Only allow access if the user owns this object
        return obj.user_id == request.user.user_id


def get_tokens_for_user(user):
    """Generate JWT tokens for our custom User model"""
    # User model now has all required Django authentication attributes
    refresh = RefreshToken.for_user(user)
    
    # Add custom claims
    refresh['user_id'] = user.user_id
    refresh['email'] = user.email
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def health_check(request):
    """
    Health check endpoint that verifies database connectivity
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }, status=503)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        # Generate unique user_id
        user_id = str(uuid.uuid4())[:15]
        while User.objects.filter(user_id=user_id).exists():
            user_id = str(uuid.uuid4())[:15]
        
        serializer.validated_data['user_id'] = user_id
        user = serializer.save()
        
        # Generate JWT tokens
        tokens = get_tokens_for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': tokens,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user with email and password
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                # Generate JWT tokens
                tokens = get_tokens_for_user(user)
                
                return Response({
                    'user': UserProfileSerializer(user).data,
                    'tokens': tokens,
                    'message': 'Login successful'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Get or update current user profile
    """
    user = request.user
    
    if request.method == 'GET':
        return Response(UserProfileSerializer(user).data)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Required for router, but filtered in get_queryset()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        """
        Users can only see their own profile
        """
        return User.objects.filter(user_id=self.request.user.user_id)
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action in ['list', 'retrieve']:
            return UserProfileSerializer
        return UserSerializer
    
    def perform_create(self, serializer):
        """
        Prevent creation through this endpoint - use registration instead
        """
        raise PermissionDenied("Use /auth/register/ to create new users")
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's profile - same as /auth/profile/
        """
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()  # Required for router, but filtered in get_queryset()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Users can only see friend requests they sent or received
        """
        return FriendRequest.objects.filter(
            models.Q(from_user=self.request.user) | 
            models.Q(to_user=self.request.user)
        )
    
    def perform_create(self, serializer):
        """
        Set the from_user to the current user
        """
        serializer.save(from_user=self.request.user)

    # detail=True -> the URL includes the pk of the object
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        friend_request: FriendRequest = self.get_object()
        
        # Only the recipient can accept a friend request
        if friend_request.to_user.user_id != request.user.user_id:
            raise PermissionDenied("You can only accept friend requests sent to you")
            
        friend_request.status = FriendRequestStatus.ACCEPTED
        friend_request.save()

        return Response({'status': 'accepted'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        friend_request: FriendRequest = self.get_object()
        
        # Only the recipient can reject a friend request
        if friend_request.to_user.user_id != request.user.user_id:
            raise PermissionDenied("You can only reject friend requests sent to you")
            
        friend_request.status = FriendRequestStatus.REJECTED
        friend_request.save()

        return Response({'status': 'rejected'}, status=status.HTTP_200_OK)


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.all()  # Required for router, but filtered in get_queryset()
    serializer_class = VisitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Users can only see their own visits
        """
        return Visit.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Set the user to the current user when creating a visit
        """
        serializer.save(user=self.request.user)


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()  # Required for router, but filtered in get_queryset()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Users can only see images from their own visits
        """
        return Image.objects.filter(visit__user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Ensure the visit belongs to the current user
        """
        visit = serializer.validated_data['visit']
        if visit.user.user_id != self.request.user.user_id:
            raise PermissionDenied("You can only add images to your own visits")
        serializer.save()