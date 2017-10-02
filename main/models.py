from django.db import models
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import User, Group

# Create your models here.


class User2(User):
    class Meta:
        proxy = True

    def is_banned(self):
        return self in Group.objects.get(name='banned').user_set.all()


class Avatar(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    url = models.URLField()

    def __str__(self):
        return str(self.url)


class Wyznanie(models.Model):
    code = models.CharField(max_length=12, unique=True, primary_key=True)  # used as a slug field

    autor = models.ForeignKey(User)
    title = models.CharField(max_length=120)
    tresc = models.TextField()
    data = models.DateTimeField(default=datetime.now)

    is_hidden = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    favourites = models.ManyToManyField(User, blank=True, related_name='favourites')

    likes = models.ManyToManyField(User, blank=True, related_name='post_likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='post_dislikes')

    def __str__(self):
        return self.code + " : " + self.title

    def counter(self):
        return self.likes.count() - self.dislikes.count()

    def get3(self):
        data = sorted(self.komentarz_set.all(), key=lambda a: a.counter(), reverse=True)[:3]
        return data


class Komentarz(models.Model):
    code = models.CharField(max_length=12, unique=True)  # used as a slug field

    id_wyznania = models.ForeignKey(Wyznanie)
    autor = models.ForeignKey(User)

    tresc = models.TextField()
    data_dodania = models.DateTimeField(default=datetime.now)
    data_edycji= models.DateTimeField(default=datetime.now)

    is_hidden = models.BooleanField(default=False)

    likes = models.ManyToManyField(User, blank=True, related_name='comment_likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='comment_dislikes')

    def __str__(self):
        return '' + self.autor.username + ' : ' + self.tresc

    def counter(self):
        return self.likes.count() - self.dislikes.count()

    def get2(self):
        data = sorted(self.answer_set.all(), key=lambda a: a.counter(), reverse=True)[:2]
        return data


class Answer(models.Model):
    code = models.CharField(max_length=12, unique=True)  # used as a slug field

    id_komentarza = models.ForeignKey(Komentarz)
    autor = models.ForeignKey(User)

    tresc = models.TextField()
    data_dodania = models.DateTimeField(default=datetime.now)
    data_edycji= models.DateTimeField(default=datetime.now)

    is_hidden = models.BooleanField(default=False)

    likes = models.ManyToManyField(User, blank=True, related_name='comment_answer_likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='comment_answer_dislikes')

    def __str__(self):
        return 'answ: ' + self.id_komentarza.code + '' + self.autor.username + ' : ' + self.tresc

    def counter(self):
        return self.likes.count() - self.dislikes.count()
