import re
import zlib
import phpserialize
from django.db import connections
from django.conf import settings
from django.contrib.auth import get_user as get_django_user_from_request
from django.contrib.auth import get_user_model as get_django_user_model
from django.contrib.auth import login

from .models import MediaWikiUser

MEDIAWIKI_COOKIE_PREFIX = getattr(settings, 'MEDIAWIKI_COOKIE_PREFIX', 'mediawiki')
MEDIAWIKI_DB_ALIAS = getattr(settings, 'MEDIAWIKI_DB_ALIAS', 'mediawiki')
connection = connections[MEDIAWIKI_DB_ALIAS]


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
    with connection.cursor() as c:
        c.execute("select value from objectcache where keyname = %s", (
            'mediawiki:session:'+session_id,
        ))
        compressed = c.fetchone()[0]
        serialized = zlib.decompress(compressed, -15)
        return unserialize_session(serialized)


def get_session_from_request(request):
    session_id = request.COOKIES.get(MEDIAWIKI_COOKIE_PREFIX+'_session')
    print('session_id: {}'.format(session_id))
    if session_id:
        return get_session(session_id)


def get_user(user_id):
    try:
        return MediaWikiUser.objects.\
            using(MEDIAWIKI_DB_ALIAS).\
            get(pk=user_id)
    except MediaWikiUser.DoesNotExist:
        return None


def get_mediawiki_user_from_request(request):
    session = get_session_from_request(request)
    if session and session.get(b'wsUserID'):
        user = get_user(session[b'wsUserID'])
        if user:
            user_id = request.COOKIES.get(MEDIAWIKI_COOKIE_PREFIX+'UserID')
            user_name = request.COOKIES.get(MEDIAWIKI_COOKIE_PREFIX+'UserName')
            if user.verify_session_and_cookie_values(session, user_id, user_name):
                return user


def get_or_create_django_user(request):
    from django.contrib.auth.models import AnonymousUser

    wiki_user = get_mediawiki_user_from_request(request)
    if wiki_user:

        django_user = get_django_user_from_request(request)
        if django_user.is_authenticated:

            if wiki_user.id == django_user.mediawiki_user_id:
                # wiki session and django sessions match
                django_user.mediawiki_user = wiki_user
                return django_user
            else:
                # sessions mismatch, invalidate django session
                request.session.flush()

        else:

            DjangoUser = get_django_user_model()
            try:
                django_user = DjangoUser.objects.get(mediawiki_user_id=wiki_user.id)
            except DjangoUser.DoesNotExist:
                django_user = DjangoUser.objects.create_from_mediawiki_user(wiki_user)
            login(request, django_user)
            django_user.mediawiki_user = wiki_user
            return django_user

    return AnonymousUser()
