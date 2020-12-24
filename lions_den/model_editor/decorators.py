from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .zoos import zoos

def login_and_zoo_access_required(func):
	@login_required(login_url='login')
	def wrapper(*args, **kwargs):
		# Get request and zoo_id arguments
		request = kwargs['request'] if 'request' in kwargs else args[0]
		zoo_id = kwargs['zoo_id'] if 'zoo_id' in kwargs else args[1]
		
		# Check user permissions
		zoo_access_permission = 'zoo:' + zoo_id + ':access'
		if zoo_id in zoos and request.user.has_perm(zoo_access_permission):
			return func(*args, **kwargs)
		else:
			return redirect('home')
	
	return wrapper