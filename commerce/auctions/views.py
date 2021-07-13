from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.forms.forms import Form
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Comment, Bid, Listing, User

class ListingForm(Form):
    title=forms.CharField()
    description=forms.CharField(widget=forms.Textarea)
    image=forms.CharField()
    bid_0=forms.DecimalField(max_digits=12, decimal_places=2)




def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings" : listings 
    })


@login_required
def create(request):
    form=ListingForm()
    if request.method == "POST":
        form=ListingForm(request.POST)
        if form.is_valid():
            l = Listing(
                author= User.objects.get(pk=request.user.id),
                description= form.cleaned_data["description"],
                image= form.cleaned_data["image"],
                title= form.cleaned_data["title"]
            )
            l.save()
            b = Bid(
                amount= form.cleaned_data["bid_0"],
                author= User.objects.get(pk=request.user.id),
                listing= l
            )
            return HttpResponseRedirect(reverse("listing", args=(l.id, )))

    return render(request, "auctions/create.html", {
        "form" : form
    })

def listing(request, listing_id):
    if request.user.is_authenticated:
        listing = Listing.objects.get(pk=listing_id)
        comments = Comment.objects.filter(listing=listing_id)
        return render(request, "auctions/listing.html", {
            "listing" : listing,
            "comments" : comments
        })


@login_required
def watchlist(request):
    listings = Listing.objects.filter(watchers=request.user)
    return render(request, "auctions/watchlist.html", {
        "listings" : listings
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
