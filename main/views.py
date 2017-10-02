from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import get_random_string
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger

from django.contrib.auth.models import Group

from .models import User2, Wyznanie, Komentarz, Answer
from .forms import FormaWyznanie, FormaKomentarz, FormAnswer

# Create your views here.


def swap(request):
    for wyznanie in Komentarz.objects.all():

        wyznanie.tresc = code_generate(Komentarz) + code_generate(Komentarz) + code_generate(Komentarz)
        wyznanie.save()
    return redirect('home')

# notification template, global
NOTIFICATION = 'main/notification.html'


def notification(request, template=NOTIFICATION, text=""):
    return render(request, template, {'text': text})


# ### ### ### ### ###

# API FUNCTIONALITY #

# ### ### ### ### ###


# Toggles favourite
@login_required(login_url='login')
def toggle_favourite(request, code):
    object_ = get_object_or_404(Wyznanie, code=code)
    # Checks if user already liked the post
    if request.user in object_.favourites.all():
        # if yes, remove the like
        object_.favourites.remove(request.user)
        faved = False  # set this to False if is not user favourite
    else:
        # else, add one
        object_.favourites.add(request.user)  # TYPE ERROR IF USER NOT LOGGED IN
        faved = True  # set this to True if is user favourite
    # Returns the current number of favourites
    return JsonResponse({
        'count': object_.favourites.count(),
        'faved': faved  # tells the front end that the user likes the object
    })


# Comments likes api
@login_required(login_url='login')
def likes_api(request, mdl, code, option):

    # c = comments w = wyznania (posts)
    if mdl is 'c':
        object_ = get_object_or_404(Komentarz, code=code)
        print(mdl)
    elif mdl is 'w':
        object_ = get_object_or_404(Wyznanie, code=code)
        print(mdl)
    elif mdl is 'a':
        object_ = get_object_or_404(Answer, code=code)
        print(mdl)
    else:
        return HttpResponse("WRONG MODEL " + str(mdl))

    status = 2
    buff = 0  # check if user was liking/disliking before
    # 1 = like 0 = dislike 2 = none

    if request.user in object_.likes.all():
        object_.likes.remove(request.user)
        buff = 1
    if request.user in object_.dislikes.all():
        object_.dislikes.remove(request.user)
        buff = 2
    if option is '1':
            status = 1  # user likes comment
            if buff != 1:
                object_.likes.add(request.user)
    elif option is '0':
            status = 0  # user dislikes comment
            if buff != 2:
                object_.dislikes.add(request.user)
    else:
        return HttpResponse("WRONG OPTION " + str(option))

    return JsonResponse({
        'count': object_.likes.count() - object_.dislikes.count(),
        'status': status
    })


# HANDLES ANSWERING COMMENTS
class GetAnswerForm(View):
    # Return answer form
    def get(self, request, code):
        return HttpResponse(FormAnswer())

    def post(self, request, code):
        form = FormAnswer(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.id_komentarza = get_object_or_404(Komentarz, code=code)
            post.code = code_generate(Answer)
            post.save()
            code = get_object_or_404(Komentarz, code=code).id_wyznania.code
            return redirect('detail', code)
        return HttpResponse(form)

# ### ### ### ### ### #

# BASIC FUNCTIONALITY #

# ### ### ### ### ### #


def post_judge(request, code, option):
    object_ = get_object_or_404(Wyznanie, code=code)
    text = None
    if option is 3:
        # Move to home
        object_.is_accepted = True
        object_.is_rejected = False
        object_.is_hidden = False
        text = 'Przeniesiono na główną: ' + str(code)
    elif option is 2:
        # Move to queue
        object_.is_accepted = False
        object_.is_rejected = False
        object_.is_hidden = False
        text = 'Przeniesiono do poczekalni: ' + str(code)
    elif option is 1:
        # Move to staff_queue
        object_.is_accepted = False
        object_.is_rejected = False
        object_.is_hidden = True
        text = 'Przeniesiono do niezweryfikowanych: ' + str(code)
    elif option is 0:
        # Move to thrash
        object_.is_accepted = False
        object_.is_rejected = True
        object_.is_hidden = True
        text = 'Przeniesiono do kosza: ' + str(code)

    object_.save()
    return notification(request, NOTIFICATION, text)


class Home(View):
    template_name = 'main/main.html'  # sets the default template to index.html
    objects = Wyznanie.objects  # fetch database for posts

    # Displays posts, home page
    def get(self, request, *args, **kwargs):
        option = kwargs.get('data')

        if option == 'home':
            objects = self.objects.filter(is_hidden=False, is_accepted=True).order_by('-data')
        elif option == 'queue':
            objects = self.objects.filter(is_hidden=False, is_accepted=False, is_rejected=False).order_by('-data')
        elif option == 'bests':
            bests = self.objects.filter(is_hidden=False, is_accepted=True, is_rejected=False)
            objects = sorted(bests, key=lambda a: a.counter(), reverse=True)[:10]
        elif option == 'staff_queue':
            objects = Wyznanie.objects.filter(is_hidden=True, is_accepted=False, is_rejected=False).order_by('-data')
        elif option == 'staff_thrash':
            objects = Wyznanie.objects.filter(is_rejected=True).order_by('-data')

        paginator = Paginator(objects, 10, orphans=True)
        page = request.GET.get('page')

        try:
            objects = paginator.page(page)
        except PageNotAnInteger:
            objects = paginator.page(1)
        except EmptyPage:
            objects = paginator.page(paginator.num_pages)

        return render(request, self.template_name, {
            "wyznania": objects
        })


# only for staff, to accept/reject posts
def staff_queue(request):
    template_name = 'main/index.html'  # sets the default template to index.html
    objects = Wyznanie.objects.filter(is_hidden=True, is_accepted=False, is_rejected=False).order_by('-data')
    return render(request, template_name, {
        "wyznania": objects
    })


def staff_thrash(request):
    template_name = 'main/index.html'  # sets the default template to index.html

    objects = Wyznanie.objects.filter(is_rejected=True).order_by('-data')
    return render(request, template_name, {
        "wyznania": objects
    })


# ADD POST PAGE
class WyznanieCreate(View):

    form = FormaWyznanie
    template_name = 'main/dodaj_wyznanie.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form()})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            code = code_generate(Wyznanie)
            post.code = code
            post.save()
            text = 'Dodano wyznanie.'
            return notification(request, NOTIFICATION, text)
        return render(request, self.template_name, {'form': self.form(request.POST)})


# DETAILED VIEW OF A POST WITH COMMENTS
def wyznanie(request, code):
    # comments adding form
    form = FormaKomentarz()
    # gets user post by code from url or 404
    obj = get_object_or_404(Wyznanie, code=code)
    # gets comments for posts then sorts it descending by score
    comments = Komentarz.objects.filter(id_wyznania=obj)
    # python reversed sorting
    # sorts comments by score
    comments = sorted(comments, key=lambda a: a.counter(), reverse=True)

    # comment adding logic
    if request.method == "POST":
        form = FormaKomentarz(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.id_wyznania = obj
            post.code = code_generate(Komentarz)
            post.save()
            return notification(request, NOTIFICATION, text="Dodano komentarz.")
    return render(request, 'main/wyznanie.html', {
        "wyznanie": obj,  # user post
        "comments": comments,  # post comments
        "form": form,  # add comment form
    })


def code_generate(model):
    code = get_random_string()
    while True:
        if model.objects.filter(code=code).exists():
            code = get_random_string()
        else:
            break
    return code


# #### ### ### ### ### #

# ## AUTHENTICATION ## #

# #### ### ### ### ### #

# REGISTER PAGE
class AuthenticationUserRegister(View):

    template_name = 'main/authentication/rejestracja.html'
    form = UserCreationForm

    def get(self, request, *args, **kwargs):
        form = self.form()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            form.save()
            text = 'Pomyślnie stworzono konto.'
            return notification(request, NOTIFICATION, text=text)
        else:
            errors = []
            for e in form.errors:
                errors.append(form.errors[e].as_text())

        return render(request, self.template_name, {'form': self.form, 'errors': errors})


# LOGIN PAGE
class AuthenticationUserLogin(View):

    template_name = 'main/authentication/logowanie.html'
    form = AuthenticationForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('notification', 'Użytkownik jest już zalogowany!')
        return render(request, self.template_name, {'form': self.form()})

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            text = 'Zalogowano jako: ' + username
        else:
            text = 'Nieprawidłowe dane logowania!'
        return notification(request, NOTIFICATION, text=text)


# simple logout
def user_logout(request):
    logout(request)
    text = 'Pomyślnie wylogowano!'
    return notification(request, NOTIFICATION, text=text)


# ### ### ### ### #### #

# ### USER SECTION ### #

# ### ### ### ### #### #

@login_required(login_url='login')
def settings(request):
    return render(request, 'main/user_profile.html')


@login_required(login_url='login')
def change_password(request):
    form = PasswordChangeForm(request.user)
    if request.method == "POST":
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            text = 'Hasło zostało zmienione.'
            return notification(request, NOTIFICATION, text=text)
        form = PasswordChangeForm(request.POST)
    return render(request, 'main/user_changepassword.html', {
        "form": form
    })


# shows each user profile, without personal information
def user_profile(request, username):
    object_ = get_object_or_404(User2, username=username)

    return render(request, 'main/user_profile.html', {
        'user': object_,
        'banned': object_.is_banned(),
    })


# ban if not banned unban if banned and redirect to user profile
def user_profile_ban_toggle(request, username):
    if request.user.is_staff:
        user_ = get_object_or_404(User2, username=username)
        group_ = Group.objects.get(name='banned')
        if user_.is_banned():
            group_.user_set.remove(user_)
            text = 'Odblokowano'
        else:
            group_.user_set.add(user_)
            text = 'Zablokowano'
    text = text + ' konto użytkownika: ' + username
    return notification(request, NOTIFICATION, text=text)


# displays favourites of chosen user
def user_favorites(request, username):

    user = get_object_or_404(User2, username=username)
    objects = user.favourites.all()

    return render(request, 'main/user_items.html', {
        'text': 'Ulubione ',
        'objects': objects,
        'username': username,
    })


# displays posts of chosen user
# visible for staff users only
def user_posts(request, username):
    if request.user.is_staff:
        user = get_object_or_404(User2, username=username)
        objects = user.wyznanie_set.all()

        return render(request, 'main/user_items.html', {
            'text': 'Wyznania ',
            'objects': objects,
            'username': username,
        })
    text = 'Nie posiadasz uprawnień administratora!'
    return notification(request, NOTIFICATION, text=text)