from .models import *

alice: User = User.objects.create(userId="u1", email="alice@example.com", password="123")
bob: User = User.objects.create(userId="u2", email="bob@example.com", password="123")

FriendRequest.objects.create(from_user=alice, to_user=bob)

pending = bob.received_requests.filter(status=FriendRequestStatus.PENDING)

request = pending.first()
request.status = FriendRequestStatus.ACCEPTED
request.save()

alice.friends()  # → [bob]
bob.friends()    # → [alice]
