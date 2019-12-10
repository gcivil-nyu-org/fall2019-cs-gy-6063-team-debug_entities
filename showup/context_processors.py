from .models import Request


def get_requests(request):
    try:
        # User is logged in.
        requests = Request.objects.filter(requestee=request.user.squad).count()
    except AttributeError:
        # User is not logged in.
        requests = 0
    return {"requests": requests}
