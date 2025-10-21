from .models import User, FriendRequest, FriendRequestStatus


def send_friend_request(from_user: User, to_user: User):
    if from_user == to_user:
        raise ValueError("You can not send a friend request to yourself.")

    request, created = FriendRequest.objects.get_or_create(
        from_user=from_user,
        to_user=to_user,
        defaults={'status': FriendRequestStatus.PENDING}
    )
    return request, created


def accept_friend_request(request: FriendRequest) -> None:
    request.status = FriendRequestStatus.ACCEPTED
    request.save()
