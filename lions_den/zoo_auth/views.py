from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages


def logout_view(request):
	logout(request)
	messages.info(request, 'You have been logged out')
	return redirect('login')
