from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import UserManager


MEDIAWIKI_TABLE_PREFIX = getattr(settings, 'MEDIAWIKI_TABLE_PREFIX', '')
MEDIAWIKI_USER_FIELD = getattr(settings, 'MEDIAWIKI_USER_FIELD', 'mediawiki_user')
MEDIAWIKI_USER_FK_FIELD = getattr(settings, 'MEDIAWIKI_USER_FK_FIELD', 'mediawiki_user_id')


class MediaWikiEnabledUserManager(UserManager):

    def create_from_mediawiki_user(self, wiki_user):
        email = self.normalize_email(wiki_user.email)
        username = self.model.normalize_username(wiki_user.name)
        first, last = self.normalize_first_last(wiki_user)
        user = self.model(
            username=username,
            email=email,
            first_name=first,
            last_name=last,
        )
        setattr(user, MEDIAWIKI_TABLE_PREFIX, wiki_user)
        setattr(user, MEDIAWIKI_USER_FK_FIELD, wiki_user.id)
        user.save(using=self._db)
        return user

    @staticmethod
    def normalize_first_last(wiki_user):
        first, last = '', ''
        if wiki_user.real_name:
            parts = wiki_user.real_name.split(' ')
            first = parts[0]
            if len(parts) > 1:
                last = ' '.join(parts[1:])
        return first, last


class MediaWikiUser(models.Model):

    class Meta:
        db_table = MEDIAWIKI_TABLE_PREFIX+'user'
        managed = False

    id = models.AutoField(primary_key=True, db_column='user_id')
    name = models.BinaryField(max_length=255, db_column='user_name')
    real_name = models.CharField(max_length=255, db_column='user_real_name')
    email = models.CharField(max_length=255, db_column='user_email')

    touched = models.BinaryField(max_length=14, db_column='user_touched')
    token = models.BinaryField(max_length=32, db_column='user_token')

    email_authenticated = models.BinaryField(max_length=14, db_column='user_email_authenticated')
    email_token = models.BinaryField(max_length=32, db_column='user_email_token')
    email_token_expires = models.BinaryField(max_length=14, db_column='user_email_token_expires')

    registration = models.BinaryField(max_length=14, db_column='user_registration')

    editcount = models.PositiveIntegerField(db_column='user_editcount')

    def verify_session_and_cookie_values(self, session, user_id):
        return self.id == session[b'wsUserID'] == int(user_id)


class RecentChanges(models.Model):

    class Meta:
        db_table = MEDIAWIKI_TABLE_PREFIX+'recentchanges'
        managed = False
        ordering = ('-rc_timestamp',)

    id = models.AutoField(primary_key=True, db_column='rc_id')
    title = models.CharField(max_length=255, db_column='rc_title')
    user = models.ForeignKey(MediaWikiUser, db_column='rc_user')
    username = models.CharField(max_length=255, db_column='rc_user_text')
    rc_timestamp = models.BinaryField()

    @property
    def modified(self):
        ts = self.rc_timestamp
        return datetime(
            int(ts[:4]),
            int(ts[4:6]),
            int(ts[6:8]),
            int(ts[8:10]),
            int(ts[10:12]),
            int(ts[12:]),
        )
