from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm, ThoughtForm, UpdateUserForm, UpdateProfileForm
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Thought, Profile
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random

# Create your views here.
def homepage(request):
    phrases =  [
        "A sanctuary for your ideas.",
        "A haven for your musings.",
        "A refuge for your reflections.",
        "A retreat for your contemplations.",
        "A dwelling for your notions.",
        "An abode for your inspirations.",
        "A haven for your imagination.",
        "A sanctuary for your insights.",
        "A harbor for your introspections.",
        "A space for your inner dialogue."
        "A shelter for your ideas.",
        "A haven for your ponderings.",
        "A nook for your reflections.",
        "A retreat for your meditations.",
        "A nest for your notions.",
        "An asylum for your inspirations.",
        "A sanctum for your imagination.",
        "A repository for your insights.",
        "A domain for your contemplations."
    ]
    motivational_quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Believe you can and you're halfway there. - Theodore Roosevelt",
        "It does not matter how slowly you go as long as you do not stop. - Confucius",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
        "Your limitation—it's only your imagination.",
        "Push yourself, because no one else is going to do it for you.",
        "Great things never come from comfort zones.",
        "Dream it. Wish it. Do it.",
        "The harder you work for something, the greater you'll feel when you achieve it."
        "Success is not the key to happiness. Happiness is the key to success. If you love what you are doing, you will be successful. - Albert Schweitzer",
        "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
        "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt",
        "The way to get started is to quit talking and begin doing. - Walt Disney",
        "It's not whether you get knocked down, it's whether you get up. - Vince Lombardi",
        "The only person you are destined to become is the person you decide to be. - Ralph Waldo Emerson",
        "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson",
        "Hardships often prepare ordinary people for an extraordinary destiny. - C.S. Lewis",
        "Opportunities don't happen, you create them. - Chris Grosser",
        "The only way to achieve the impossible is to believe it is possible. - Charles Kingsleigh"
    ]
    quote = random.choice(motivational_quotes)
    thought = random.choice(phrases)
    context= {"thought": thought,
              "quote": quote
              }
    return render(request, "journal/index.html", context)


def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            current_user = form.save(commit=False)
            form.save()
            send_mail("Welcome to Thoughts!", "Congratulations on creating your account",
                      settings.DEFAULT_FROM_EMAIL, [current_user.email], )
            profile = Profile.objects.create(user=current_user)
            messages.success(request, "User created!")
            return redirect("my-login")
    context = {"RegistrationForm": form}
    return render(request, "journal/register.html", context)


def my_login(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                messages.success(request, "Login successful!")
                return redirect("dashboard")

    context = {"LoginForm": form}
    return render(request, "journal/my-login.html", context)


def user_logout(request):
    auth.logout(request)
    messages.success(request, "Logout successful!")
    return redirect("")


@login_required(login_url="my-login")
def dashboard(request):
    profile_pic = Profile.objects.get(user=request.user)
    context = {"profilePic": profile_pic}
    return render(request, "journal/dashboard.html", context)


@login_required(login_url="my-login")
def create_thought(request):
    form = ThoughtForm()

    if request.method == "POST":
        form = ThoughtForm(request.POST)
        if form.is_valid():
            thought = form.save(commit=False)
            thought.user = request.user
            thought.save()
            messages.success(request, "Thought created!")
            return redirect("my-thoughts")
    context = {"CreateThoughtForm": form}
    return render(request, "journal/create-thought.html", context)


@login_required(login_url="my-login")
def my_thoughts(request):
    current_user = request.user.id
    thought = Thought.objects.all().filter(user=current_user).order_by("-date_posted")

    context = {"AllThoughts": thought}
    return render(request, "journal/my-thoughts.html", context)


@login_required(login_url="my-login")
def update_thought(request, pk):
    try:
        thought = Thought.objects.get(id=pk, user=request.user)
    except:
        return redirect("my-thoughts")
    form = ThoughtForm(instance=thought)
    if request.method == "POST":
        form = ThoughtForm(request.POST, instance=thought)
        if form.is_valid():
            form.save()
            messages.success(request, "Thought updated!")
            return redirect("my-thoughts")
    context = {"UpdateThought": form}
    return render(request, "journal/update-thought.html", context)


@login_required(login_url="my-login")
def delete_thought(request, pk):
    try:
        thought = Thought.objects.get(id=pk, user=request.user)
    except:
        return redirect("my-thoughts")
    if request.method == "POST":
        thought.delete()
        messages.success(request, "Thought deleted!")
        return redirect("my-thoughts")

    return render(request, "journal/delete-thought.html")


@login_required(login_url="my-login")
def profile_management(request):
    form = UpdateUserForm(instance=request.user)

    profile = Profile.objects.get(user=request.user)

    form_2 = UpdateProfileForm(instance=profile)

    if request.method == "POST":
        form = UpdateUserForm(request.POST, instance=request.user)
        form_2 = UpdateProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Updated profile!")
            return redirect("dashboard")

        if form_2.is_valid():
            form_2.save()
            messages.success(request, "Updated picture!")
            return redirect("dashboard")
    context = {"UserUpdateForm": form,
               "ProfileUpdateForm": form_2}
    return render(request, "journal/profile-management.html", context)


@login_required(login_url="my-login")
def delete_account(request):
    if request.method == "POST":
        deleteUser = User.objects.get(username=request.user)
        deleteUser.delete()
        messages.success(request, "Account deleted!")
        return redirect("")
    return render(request, "journal/delete-account.html")
