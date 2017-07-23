INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'mediawiki_auth',
    'mediawiki_auth.tests',
)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'mediawiki_auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test_app',
        'HOST': '127.0.0.1',
        'PORT': 5433,
        'USER': 'postgres',
    },
    'mediawiki': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'USER': 'root',
        'PASSWORD': 'password',
        'NAME': 'mediawiki',
    }
}
AUTH_USER_MODEL = 'mediawiki_auth.DjangoUser'
ROOT_URLCONF = 'mediawiki_auth.tests.urls'
STATIC_URL = '/static/'
SECRET_KEY = 'test-key'
DEBUG = True
