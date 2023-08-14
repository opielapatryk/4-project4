from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import Post, User

class CreateNewPostForm(forms.Form):
    post = forms.CharField(max_length=128,widget=forms.Textarea(attrs={'placeholder': 'How are you? :)'}))

def index(request):
    if request.method == 'POST':
        form = CreateNewPostForm(request.POST)
        if form.is_valid():
            post = form.cleaned_data['post']
            user = User.objects.get(username=request.user)
            new_post = Post(user=user, post=post)
            new_post.save()
            return HttpResponseRedirect(reverse("index"))

    return render(request, "network/index.html",{
        'posts':Post.objects.all(),
        'form': CreateNewPostForm()
        })

def profile_view(request, user_id):
    creator = User.objects.get(id=user_id)
    follow = ''
    # if you dont follow
    if request.user.is_authenticated:
        if creator.followers.filter(id=request.user.id):
            follow = 'Unfollow'
        else:
            # If you follow
            follow = 'Follow'

    return render(request, 'network/profile.html',{
        'creator': creator,
        'creator_id': user_id,
        'follow': follow,
        'posts': Post.objects.filter(user=creator)
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
