from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from .forms import LoginUserForm, RegisterUserForm, RegisterPosterForm, SignForPoster
from .models import Poster, User


def index(request):
    data = {'posters': Poster.objects.all()}
    return render(request, 'index.html', context=data)


class Posters(ListView):
    # data = {'posters': Poster.objects.all()}
    # return render(request, 'posters.html', context=data)
    model = Poster
    template_name = 'posters.html'
    context_object_name = 'posters'
    extra_context = {
        'posters': Poster.objects.all(),
    }


def poster(request, post_slug):
    post = get_object_or_404(Poster, slug=post_slug)
    if request.method == 'POST':
        form = SignForPoster(request.POST)
        if form.is_valid():
            try:
                # todo переделать обработчик исключений на проверку request.COOKIES['nickname']
                user = User.objects.get(nickname=request.COOKIES['nickname'])
                post.subscribers.add(user)
                return redirect('personal_account')
            except:
                return redirect('login_page')
    else:
        form = SignForPoster()
    context = {'post': post, 'form': form}
    return render(request, 'poster.html', context=context)


def personal_account(request):
    try:
        user = User.objects.get(nickname=request.COOKIES['nickname'])

        user_data = {
            'user': user,
            'events': user.events.all(),
            'subs': Poster.objects.filter(subscribers__nickname=request.COOKIES['nickname']),
        }
    except:
        return redirect('login_page')
    return render(request, 'personal_account.html', context=user_data)


def poster_redactor(request):
    if request.method == 'POST':
        form = RegisterPosterForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(nickname=request.COOKIES['nickname'])
                user.events.create(title=form.cleaned_data['title'],
                                   place=form.cleaned_data['place'],
                                   price=form.cleaned_data['price'],
                                   creator=request.COOKIES['nickname'],
                                   short_description=form.cleaned_data['short_description'],
                                   full_description=form.cleaned_data['full_description'],
                                   time_event=form.cleaned_data['time_event'])

                user.save()
                return redirect('posters')
            except:
                form.add_error(None, 'Не удалось создать обьявление')
    else:
        form = RegisterPosterForm()
    data = {'form': form}
    return render(request, 'poster_redactor.html', context=data)


def submit_application(request):
    # todo - страница с отправлением заявки модераторам
    # if request.method == 'POST':
    #     form = RegisterPosterForm(request.POST)
    #     if form.is_valid():
    #         try:
    #             user = User.objects.get(nickname=request.COOKIES['nickname'])
    #             user.events.create(title=form.cleaned_data['title'],
    #                                place=form.cleaned_data['place'],
    #                                price=form.cleaned_data['price'],
    #                                creator=request.COOKIES['nickname'],
    #                                short_description=form.cleaned_data['short_description'],
    #                                full_description=form.cleaned_data['full_description'],
    #                                time_event=form.cleaned_data['time_event'])
    #
    #             user.save()
    #             return redirect('posters')
    #         except:
    #             form.add_error(None, 'Не удалось создать обьявление')
    # else:
    #     form = RegisterPosterForm()
    # data = {'form': form}
    return render(request, 'submit_application.html', context=data)


def registration_page(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            try:
                if User.objects.filter(nickname=form.cleaned_data['nickname']):
                    raise Exception
                user = User(nickname=form.cleaned_data['nickname'],
                            password=form.cleaned_data['password'],
                            name=form.cleaned_data['name'],
                            surname=form.cleaned_data['surname'],
                            age=form.cleaned_data['age'],
                            hobby=form.cleaned_data['hobby'])
                user.save()
                rsp = redirect('login_page')
                rsp.set_cookie('nickname', form.cleaned_data['nickname'])
                return rsp
            except:
                form.add_error(None, 'Пользователь с таким ником уже существует')
    else:
        form = RegisterUserForm()
    data = {'form': form}
    return render(request, 'registration_page.html', context=data)


def login_page(request):
    if request.method == 'POST':
        form = LoginUserForm(request.POST)
        if form.is_valid():
            if not User.objects.filter(nickname=form.cleaned_data['nickname']):
                return redirect('registration_page')
            elif User.objects.filter(nickname=form.cleaned_data['nickname'])[0].password \
                    != form.cleaned_data['password']:
                form.add_error(None, 'Неправильно указан пароль')
            else:
                try:
                    User.objects.get(nickname=request.COOKIES['nickname'])
                    return redirect('index')
                except:
                    rsp = redirect('index')
                    rsp.set_cookie('nickname', form.cleaned_data['nickname'])
                    return rsp


    else:
        form = LoginUserForm()
    return render(request, 'login_page.html', context={'form': form})
