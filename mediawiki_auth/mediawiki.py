import re
import zlib
import phpserialize
from django.db import connections
from django.conf import settings
from django.contrib.auth import get_user as get_django_user_from_request
from django.contrib.auth import get_user_model as get_django_user_model
from django.contrib.auth import login

from .models import (
    MediaWikiUser,
    MEDIAWIKI_USER_FK_FIELD,
    MEDIAWIKI_USER_FIELD,
    MEDIAWIKI_TABLE_PREFIX,
    MEDIAWIKI_DB_ALIAS
)

MEDIAWIKI_COOKIE_PREFIX = getattr(settings, 'MEDIAWIKI_COOKIE_PREFIX', 'mediawiki')


def unserialize_session(val):
    session = {}
    groups = re.split(b"([a-zA-Z0-9_]+)\|", val)
    if len(groups) > 2:
        groups = groups[1:]
        groups = zip(*([iter(groups)] * 2))
    for key, php_value in groups:
        session[key] = phpserialize.loads(php_value)
    return session


def get_session(session_id):
    with connections[MEDIAWIKI_DB_ALIAS].cursor() as c:
        c.execute("select value from {}objectcache where keyname = %s".format(MEDIAWIKI_TABLE_PREFIX), (
            'mediawiki:session:'+session_id,
        ))
        result = c.fetchone()
        if result and result[0]:
            serialized = zlib.decompress(result[0], -15)
            return unserialize_session(serialized)


def get_session_from_request(request):
    session_id = request.COOKIES.get(MEDIAWIKI_COOKIE_PREFIX+'_session')
    if session_id:
        return get_session(session_id)


def get_user(user_id):
    try:
        return MediaWikiUser.objects.get(pk=user_id)
    except (MediaWikiUser.DoesNotExist, MediaWikiUser.MultipleObjectsReturned):
        return None


def get_mediawiki_user_from_request(request):
    session = get_session_from_request(request)
    if session and session.get(b'wsUserID'):
        user = get_user(session[b'wsUserID'])
        if user:
            user_id = request.COOKIES.get(MEDIAWIKI_COOKIE_PREFIX+'UserID')
            if user.verify_session_and_cookie_values(session, user_id):
                return user


def get_django_user_from_mediawiki_user(wiki_user):
    User = get_django_user_model()
    try:
        return User.objects.get(**{MEDIAWIKI_USER_FK_FIELD: wiki_user.id})
    except (User.DoesNotExist, User.MultipleObjectsReturned):
        return None


def get_or_create_django_user_from_mediawiki_user(wiki_user):
    DjangoUser = get_django_user_model()
    try:
        return DjangoUser.objects.get(**{MEDIAWIKI_USER_FK_FIELD: wiki_user.id}), False
    except DjangoUser.DoesNotExist:
        return DjangoUser.objects.create_from_mediawiki_user(wiki_user), True


def get_or_create_django_user(request):
    from django.contrib.auth.models import AnonymousUser

    wiki_user = get_mediawiki_user_from_request(request)
    if wiki_user:

        django_user = get_django_user_from_request(request)
        if django_user.is_authenticated:

            if wiki_user.id == getattr(django_user, MEDIAWIKI_USER_FK_FIELD):
                # wiki session and django sessions match
                setattr(django_user, MEDIAWIKI_USER_FIELD, wiki_user)
                return django_user
            else:
                # sessions mismatch, invalidate django session
                request.session.flush()

        else:

            django_user, _ = get_or_create_django_user_from_mediawiki_user(wiki_user)
            login(request, django_user)
            setattr(django_user, MEDIAWIKI_USER_FIELD, wiki_user)
            return django_user

    return AnonymousUser()
