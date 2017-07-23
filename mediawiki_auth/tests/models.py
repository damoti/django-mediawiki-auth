from django.db import models
from django.contrib.auth.models import AbstractUser
from mediawiki_auth.models import MediaWikiEnabledUserManager


class User(AbstractUser):
    mediawiki_user_id = models.PositiveIntegerField(unique=True, db_index=True)
    objects = MediaWikiEnabledUserManager()
