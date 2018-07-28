from django.shortcuts import render, redirect
from .models import Gig
# Create your views here.


def home(request):
    gigs = Gig.objects.filter(status=True)

    return render(request,'home.html',{"gigs":gigs})


def gig_detail(request, id):
    try:
        gig = Gig.objects.get(id=id)
    except Gig.DoesNotExist:
        return redirect('/')
    return render(request, 'gig_detail.html', {"gig": gig})


def create_gig(request):
    return render(request, 'create_gig.html',{})


def my_gigs(request):
    return render(request, 'my_gigs.html', {})



