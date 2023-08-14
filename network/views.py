from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import Post, User
from django.core.paginator import Paginator



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

    posts_list = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html",{
        'form': CreateNewPostForm(),
        'posts_list':posts_list,
        'page_obj': page_obj
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

    posts_list = Post.objects.filter(user=creator).order_by('-timestamp')
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'network/profile.html',{
        'creator': creator,
        'creator_id': user_id,
        'follow': follow,
        'posts_list':posts_list,
        'page_obj': page_obj
    })

def following_view(request):
    if request.user.is_authenticated:
        # Get users that the current user follows
        current_user = User.objects.get(id=request.user.id)
        user_following = current_user.following.all()
        
        # Get posts from users that the current user follows
        posts_list = Post.objects.filter(user__in=user_following).order_by('-timestamp')
        paginator = Paginator(posts_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'network/following.html', {
            'posts_list':posts_list,
            'page_obj': page_obj
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
