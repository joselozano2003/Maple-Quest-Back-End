from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from .models import *
from .serializers import *
from .s3_utils import S3ImageUploader
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
    
    @action(detail=False, methods=['get'])
    def friends(self, request):
        """
        Get current user's list of friends (accepted friend requests)
        """
        friends = request.user.friends()
        serializer = UserProfileSerializer(friends, many=True)
        return Response({
            'friends': serializer.data,
            'count': friends.count()
        })
    
    @action(detail=False, methods=['post'])
    def generate_upload_url(self, request):
        """
        Generate a presigned URL for uploading images to S3
        """
        filename = request.data.get('filename')
        if not filename:
            return Response({
                'error': 'filename is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        s3_uploader = S3ImageUploader()
        file_key = s3_uploader.generate_unique_filename(filename, request.user.user_id)
        presigned_url = s3_uploader.generate_presigned_url(file_key)
        
        if not presigned_url:
            return Response({
                'error': 'Failed to generate upload URL'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        public_url = s3_uploader.get_public_url(file_key)
        
        return Response({
            'upload_url': presigned_url,
            'public_url': public_url,
            'file_key': file_key,
            'expires_in': 3600  # 1 hour
        })


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
    
    @action(detail=False, methods=['post'])
    def add_friend(self, request):
        """
        Send a friend request to a user by their email or phone number
        """
        email = request.data.get('email')
        phone_no = request.data.get('phone_no')
        
        if not email and not phone_no:
            return Response({
                'error': 'Either email or phone_no is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find the user by email or phone
        try:
            if email:
                to_user = User.objects.get(email=email)
            else:
                to_user = User.objects.get(phone_no=phone_no)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found with the provided email or phone number'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if trying to add themselves
        if to_user.user_id == request.user.user_id:
            return Response({
                'error': 'You cannot send a friend request to yourself'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if friend request already exists
        existing_request = FriendRequest.objects.filter(
            models.Q(from_user=request.user, to_user=to_user) |
            models.Q(from_user=to_user, to_user=request.user)
        ).first()
        
        if existing_request:
            if existing_request.status == FriendRequestStatus.PENDING:
                return Response({
                    'message': 'Friend request already sent',
                    'friend_request': FriendRequestSerializer(existing_request).data
                }, status=status.HTTP_200_OK)
            elif existing_request.status == FriendRequestStatus.ACCEPTED:
                return Response({
                    'message': 'You are already friends with this user'
                }, status=status.HTTP_200_OK)
            elif existing_request.status == FriendRequestStatus.REJECTED:
                # Update the rejected request to pending
                existing_request.status = FriendRequestStatus.PENDING
                existing_request.from_user = request.user
                existing_request.to_user = to_user
                existing_request.save()
                return Response({
                    'message': 'Friend request sent successfully',
                    'friend_request': FriendRequestSerializer(existing_request).data
                }, status=status.HTTP_201_CREATED)
        
        # Create new friend request
        friend_request = FriendRequest.objects.create(
            from_user=request.user,
            to_user=to_user,
            status=FriendRequestStatus.PENDING
        )
        
        return Response({
            'message': 'Friend request sent successfully',
            'friend_request': FriendRequestSerializer(friend_request).data
        }, status=status.HTTP_201_CREATED)


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    
    def get_permissions(self):
        """
        Allow unauthenticated access for GET requests (list, retrieve, and images),
        require authentication for create, update, delete, and visit
        """
        if self.action in ['list', 'retrieve', 'images']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Generate unique location_id when creating a location
        """
        # Generate unique location_id
        location_id = str(uuid.uuid4())[:10]
        while Location.objects.filter(location_id=location_id).exists():
            location_id = str(uuid.uuid4())[:10]
        
        serializer.save(location_id=location_id)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def images(self, request, pk=None):
        """
        Get all images for a specific location from all users' visits
        """
        location = self.get_object()
        
        # Get all visits to this location
        visits = Visit.objects.filter(location=location)
        
        # Get all images from these visits
        images = Image.objects.filter(visit__in=visits).order_by('-id')
        
        serializer = ImageSerializer(images, many=True)
        return Response({
            'location_id': location.location_id,
            'location_name': location.name,
            'total_images': images.count(),
            'images': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def visit(self, request, pk=None):
        """
        Mark a location as visited by the authenticated user with optional images
        """
        location = self.get_object()
        user = request.user
        
        # Check if user has already visited this location
        existing_visit = Visit.objects.filter(user=user, location=location).first()
        if existing_visit:
            # If already visited, still allow adding new images
            images_data = request.data.get('images', [])
            created_images = []
            
            for image_data in images_data:
                if 'image_url' in image_data:
                    image = Image.objects.create(
                        visit=existing_visit,
                        image_url=image_data['image_url'],
                        description=image_data.get('description', ''),
                        likes=0
                    )
                    created_images.append(ImageSerializer(image).data)
            
            return Response({
                'message': 'Location already visited, images added' if created_images else 'Location already visited',
                'visit': VisitSerializer(existing_visit).data,
                'images': created_images,
                'points_earned': 0,  # No points for revisiting
                'total_points': user.points
            }, status=status.HTTP_200_OK)
        
        # Create new visit
        visit_data = {
            'user': user,
            'location': location,
            'note': request.data.get('note', '')  # Optional note from request
        }
        
        visit = Visit.objects.create(**visit_data)
        
        # Add images if provided
        images_data = request.data.get('images', [])
        created_images = []
        
        for image_data in images_data:
            if 'image_url' in image_data:
                image = Image.objects.create(
                    visit=visit,
                    image_url=image_data['image_url'],
                    description=image_data.get('description', ''),
                    likes=0
                )
                created_images.append(ImageSerializer(image).data)
        
        # Award points to user
        user.points += location.points
        user.save()
        
        return Response({
            'message': 'Location visited successfully',
            'visit': VisitSerializer(visit).data,
            'images': created_images,
            'points_earned': location.points,
            'total_points': user.points
        }, status=status.HTTP_201_CREATED)


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