from .models import Profile


def save_avatar(backend, user, response, *args, **kwargs):
    try:
        profile = Profile.objects.get(user_id=user.id)
    except Profile.DoesNotExist:
        profile = Profile(user_id=user.id)
    if backend.name == 'facebook':
        profile.avatar = 'https://graph.facebook.com/%s/picture?type=large' % response['id']

    profile.save()


def save_profile1(backend, user, response, *args, **kwargs):
    if backend.name == 'facebook':
        profile = Profile(user_id=user.id)
        if profile is None:
            profile = Profile(user_id=user.id)
        profile.avatar = 'https://graph.facebook.com/%s/picture?type=large' % response['id']
        profile.email = response.get('email')
        profile.first_name = response.get('first_name')
        profile.last_name = response.get('last_name')
        profile.link = response.get('link')
        profile.locale = response.get('locale')
        profile.timezone = response.get('timezone')
        profile.gender = response.get('gender')
        profile.link = response.get('link')
        profile.timezone = response.get('timezone')
        profile.save()


def save_profile(backend, user, response, *args, **kwargs):
    try:
        profile = Profile.objects.get(user_id=user.id)
    except Profile.DoesNotExist:
        profile = Profile(user_id=user.id)
    if backend.name == 'facebook':
        profile.avatar = 'https://graph.facebook.com/%s/picture?type=large' % response['id']
        profile.email = response.get('email')
        profile.first_name = response.get('first_name')
        profile.last_name = response.get('last_name')
        profile.link = response.get('link')
        profile.locale = response.get('locale')
        profile.timezone = response.get('timezone')
        profile.gender = response.get('gender')
        profile.link = response.get('link')
        profile.timezone = response.get('timezone')
    profile.save()
