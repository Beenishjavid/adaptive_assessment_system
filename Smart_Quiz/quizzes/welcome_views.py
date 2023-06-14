from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def welcome(request):
    """Welcome page for unauthenticated users"""
    if request.user.is_authenticated:
        return redirect('home')
    
    context = {
        'title': 'Welcome to Smart Quiz System'
    }
    return render(request, 'quizzes/welcome.html', context)
