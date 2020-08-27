import pytz

from django.utils import timezone

class TimezoneMiddleware(object):
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    # Check if they are authenticated so we know we have their tz info
    if request.user.is_authenticated:
      # Getting the user's timezone and activate it
      tz = request.user.timezone
      timezone.activate(tz)
    # Otherwise deactivate and the default time zone will be used instead
    else:
      timezone.deactivate()
    response = self.get_response(request)
    return response