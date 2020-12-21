from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
def logout_view(request):
	logout(request)
	messages.info(request, 'You have been logged out')
	return redirect('login')