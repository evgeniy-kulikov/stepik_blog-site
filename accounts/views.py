from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Изменение пароля
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin

from .forms import SignUpForm, LoginForm, UpdateUserForm, UpdateProfileForm


# Изменение пароля
# Переопределяем встроенный класс PasswordChangeView
class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'registration/change_password.html'
    success_message = "Ваш пароль успешно изменен"
    success_url = reverse_lazy('users-profile')


# @login_required
# def profile(request):
#     return render(request, 'registration/profile.html')

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен')
            return redirect(to='accounts:users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'accounts/profile.html', {'user_form': user_form, 'profile_form': profile_form})


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login")

    # Через метод initial мы можем передать словарь
    # с ключами - именами полей и значениями - начальными значениями полей формы.
    initial = None  # принимает {'key': 'value'}

    template_name = 'accounts/signup.html'

    def dispatch(self, request, *args, **kwargs):
        # перенаправит на домашнюю страницу,
        # если пользователь попытается получить доступ к странице регистрации после авторизации
        if request.user.is_authenticated:
            return redirect(to='/')

        return super(SignUpView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Создан аккаунт для {username}')

            # return redirect(to='/')
            return redirect(to='login')  # редирект на страницу логина после регистрации

        return render(request, self.template_name, {'form': form})

# # Простой вариант
# class SignUpView(generic.CreateView):
#     # form_class = UserCreationForm  # встроенный класс из auth.forms
#     form_class = SignUpForm  # переопределили UserCreationForm из встроенного класса auth.forms
#     success_url = reverse_lazy("login")  # Перенаправление на login-страницу при успешной регистрации
#     template_name = "accounts/signup.html"


class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # Установим время истечения сеанса равным 0 секундам.
            # Таким образом, он автоматически закроет сеанс после закрытия браузера.
            # И обновим данные.
            self.request.session.set_expiry(0)
            self.request.session.modified = True

        # В противном случае сеанс браузера будет таким же как время сеанса cookie "SESSION_COOKIE_AGE",
        # определенное в settings.py
        return super(CustomLoginView, self).form_valid(form)


# Для Django 5.0 и выше
def logout_view(request):
    logout(request)
    # return HttpResponseRedirect(redirect_to=reverse('blog:post_list'))
    return HttpResponseRedirect("/")

    # На Django 5.0 и выше  удалили выход из системы по запросу GET
    # return HttpResponseRedirect(redirect_to=reverse('logout'))
