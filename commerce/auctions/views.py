from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.forms.forms import Form
from django.forms.widgets import Textarea
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Category, Comment, Bid, Listing, User

#Forms models

class BidForm(Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2)
    
class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, max_length=500)

class ListingForm(Form):
    title=forms.CharField()
    description=forms.CharField(widget=forms.Textarea)
    image=forms.CharField()
    category=forms.CharField()
    bid_0=forms.DecimalField(max_digits=12, decimal_places=2, label="Initial bid")




def index(request):
    listings = Listing.objects.all()
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings" : listings,
        "categories" : categories 
    })


@login_required
def bid(request):
    if request.method == 'POST':
        b_form = BidForm(request.POST)
        # Can we make a lambda in render arguments?, lets try it 
        print(request.POST['o_bid'])
        if b_form.is_valid() and b_form.cleaned_data['amount'] > float(request.POST['o_bid']):
            listing = Listing.objects.get(pk=request.POST["listing"])
            b = Bid(
                amount=b_form.cleaned_data["amount"],
                author=request.user,
                listing= listing
            )
            b.save()
            listing.watchers.add(request.user)
            return render(request, "auctions/bid.html", {
                "bid" : b
            })
        else:
            return render(request, "auctions/bid.html", {
                "message" : "Oops! Your bid needs to be higher than the previous one."
            })

    return HttpResponseRedirect(reverse("index"))    


# Here we show all listings corresponding to a specific category
def category(request, category):
    c = Category.objects.get(name=category)
    listings=Listing.objects.filter(categories=c)
    return render(request, "auctions/category.html", {
        "listings" : listings
    })



@login_required
def create(request):
    form=ListingForm()
    if request.method == "POST":
        form=ListingForm(request.POST)
        if form.is_valid():
            # Assigning values to new listing object
            l = Listing(
                author= User.objects.get(pk=request.user.id),
                description = form.cleaned_data["description"],
                image = form.cleaned_data["image"],
                title = form.cleaned_data["title"]
            )
            l.save()

            #Saving category. Maybe try to apply regex to add more than 1?
            try:
                Category.objects.get(name=form.cleaned_data["category"]).listings.add(l)
            except:
                c = Category(
                    name = form.cleaned_data["category"]
                )
                c.save()
                c.listings.add(l)

            # Initializing Bid "floor".
            b = Bid(
                amount= form.cleaned_data["bid_0"],
                author= User.objects.get(pk=request.user.id),
                listing= l
            )
            b.save()

            return HttpResponseRedirect(reverse("listing", args=(l.id, )))
        else:
            return render(request, "auctions/create.html", {
                "form" : form
            })

    return render(request, "auctions/create.html", {
        "form" : form
    })


def listing(request, listing_id, message=False):
        b_form = BidForm()
        c_form = CommentForm()
        listing = Listing.objects.get(pk=listing_id)
        comments = Comment.objects.filter(listing=listing_id)
        
        # Save and redirect after making comments
        if request.method == 'POST':
            c_form = CommentForm(request.POST)
            if c_form.is_valid():
                c = Comment(
                    author = request.user,
                    listing =listing,
                    content = c_form.cleaned_data["content"]
                )
                c.save()
                return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
            else:
                return render(request, "auctions/listing.html", {
                    "listing" : listing,
                    "comments" : comments,
                    "c_form" : c_form,
                    "bid" : listing.bid.last().amount,
                    "message":message
                })


        return render(request, "auctions/listing.html", {
            "listing" : listing,
            "comments" : comments,
            "c_form" : c_form,
            "b_form" : b_form,
            "bid" : listing.bid.last().amount 
        })


@login_required
def watchlist(request):
    if request.method == 'POST':
        form=request.POST
        if form:
            l = Listing.objects.get(pk=form["listing"])
            if l in request.user.following.all():
                request.user.following.remove(l)
            else:
                request.user.following.add(l)
        return HttpResponseRedirect(reverse("listing", args=(l.id,)))
    #shows all listings for current user
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
