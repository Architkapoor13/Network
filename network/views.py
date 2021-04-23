from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
import json
import operator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.views.decorators.csrf import csrf_exempt

from .models import User
from .models import *


def index(request):
    allpost = Posts.objects.all()
    allpost = allpost.order_by("-timestamp").all()
    pagination = Paginator(allpost, 10)
    pagenumber = request.GET.get('page')
    if request.user.is_authenticated:
        userlikedposts = User.objects.get(username=request.user.username).likes.all()
    else:
        userlikedposts = []
    currentpage = 1
    if request.method == 'GET':
        currentpage = pagenumber
        if pagenumber == None:
            currentpage = 1
        page_posts = pagination.get_page(pagenumber)
        return render(request, "network/index.html", {
            'pageposts': page_posts,
            'currentpage': int(currentpage),
            'userlikedposts': userlikedposts
        })
    else:
        wantedpagenumber = request.POST["wantedpagenumber"]
        return redirect(f"/?page={wantedpagenumber}")

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


@csrf_exempt
def posts(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        postdata = data.get("data")
        newpost = Posts(user=request.user, postdata=postdata)
        newpost.save()
        print("new post created!")
        return JsonResponse({
            'message': "new post posted!"
        })
    else:
        return JsonResponse({'message': "Post method required!"})


def allposts(request):
    if request.method != "GET":
        return JsonResponse({"message": "Get method required"})

    allpost = Posts.objects.all()
    allpost = allpost.order_by("-timestamp").all()
    return JsonResponse([post.serialize() for post in allpost], safe=False)


def profile(request, username, pnumber):
    if request.method == 'POST':
        wantedpagenumber = request.POST["wantedpagenumber"]
        return redirect(f"/profile/{username}/page={wantedpagenumber}")
    requesteduser = User.objects.get(username=username)
    followerscount = requesteduser.followers.count()
    followingcount = requesteduser.following.count()
    classname = "btn btn-primary"
    followbtncontent = "Follow"
    if request.user.is_authenticated:
        userlikedposts = User.objects.get(username=request.user.username).likes.all()
    else:
        userlikedposts = []
    if request.user in requesteduser.followers.all():
        classname = "btn btn-danger"
        followbtncontent = "Un-follow"
    page_posts = Posts.objects.filter(user=requesteduser)
    page_posts = page_posts.order_by('-timestamp').all()
    pagination = Paginator(page_posts, 10)
    posts = pagination.page(pnumber)
    return render(request, "network/profile.html", {
        "followerscount": followerscount,
        "followingcount": followingcount,
        "requesteduser": requesteduser,
        "followbtnclass": classname,
        "followbtncontent": followbtncontent,
        "pageposts": posts,
        "currentpage": int(pnumber),
        "userlikedposts": userlikedposts
    })


def profileposts(request, profilename):
    if request.method != 'GET':
        return JsonResponse({"message": "GET method required"})
    profileuser = User.objects.get(username=profilename)
    posts = Posts.objects.filter(user=profileuser)
    posts.order_by("-timestamp").all()
    return JsonResponse([post.serialize() for post in posts], safe=False)


def followtoggle(request, username):
    if request.method != "GET":
        return JsonResponse({"message": "GET method required"})
    if not request.user.is_authenticated:
        return JsonResponse({"message": "You need to login first"})
    usertofollow = User.objects.get(username=username)
    currentuser = User.objects.get(username=request.user.username)
    if usertofollow in currentuser.following.all():
        currentuser.following.remove(usertofollow)
        usertofollow.followers.remove(currentuser)
        currentuser.save()
        usertofollow.save()
        print(f"unfollowed {usertofollow.username}")
        return JsonResponse({"message": "user unfollowed"})
    else:
        currentuser.following.add(usertofollow)
        usertofollow.followers.add(currentuser)
        currentuser.save()
        usertofollow.save()
        print(f"followed {usertofollow.username}")
        return JsonResponse({"message": "user followed"})


def followingposts(request, pnumber):
    if not request.user.is_authenticated:
        return HttpResponse("Login First to complete this action")
    following = User.objects.get(username=request.user.username).following.all()
    print("before filtering out the posts")
    posts = Posts.objects.filter(user__in=following.all()).order_by('-timestamp')
    pagination = Paginator(posts, 10)
    page_posts = pagination.page(pnumber)
    if request.user.is_authenticated:
        userlikedposts = User.objects.get(username=request.user.username).likes.all()
    else:
        userlikedposts = []
    return render(request, 'network/followingposts.html', {
        "pageposts": page_posts,
        "currentpage": pnumber,
        "userlikedposts": userlikedposts
    })


def followingpostsapi(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "Login first complete this action"})
    if request.method != 'GET':
        return JsonResponse({"message": "GET method required"})

    posts = []
    following = User.objects.get(username=request.user.username).following.all()
    for follower in following:
        fposts = Posts.objects.filter(user=follower).order_by('-timestamp')
        for post in fposts:
            posts.append(post.serialize())

    newlist = sorted(posts, key=operator.itemgetter('time'), reverse=True)
    return JsonResponse(newlist, safe=False)


@csrf_exempt
def editpost(request, postid):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "Login first to complete this event!"})
    if request.method != 'POST':
        return JsonResponse({"message": "POST method required!"})
    data = json.loads(request.body)
    newdata = data.get('newdata')
    post = Posts.objects.get(id=postid)
    print(newdata)
    if post.user != request.user:
        return JsonResponse({"message": "Error editing the post"})
    post.postdata = newdata
    post.save()
    print("post edited")
    return JsonResponse({"message": "post edited!"})


def likes(request, postid):
    if request.method != 'GET':
        return JsonResponse({"message": "GET method required"})
    if not request.user.is_authenticated:
        return JsonResponse({"message": "Login first to complete this event"})
    post = Posts.objects.get(id=postid)
    currentuser = User.objects.get(username=request.user.username)
    if currentuser in post.likes.all():
        post.likes.remove(request.user)
        currentuser.postsliked.remove(post)
        post.save()
        currentuser.save()
        print("post unliked")
        return JsonResponse({"message": "post un-liked"})
    else:
        post.likes.add(currentuser)
        currentuser.postsliked.add(post)
        post.save()
        currentuser.save()
        print("post liked")
        return JsonResponse({"message": "post liked"})



