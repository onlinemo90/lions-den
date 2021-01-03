import functools
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .zoos import zoos

def login_and_zoo_access_required(view_function):
	@functools.wraps(view_function)
	@login_required(login_url='login')
	def wrapper(*args, **kwargs):
		# Get request and zoo_id arguments
		request = kwargs['request'] if 'request' in kwargs else args[0]
		zoo_id = kwargs['zoo_id'] if 'zoo_id' in kwargs else args[1]
		
		# Check user permissions
		if zoo_id in zoos and (request.user.is_superuser or request.user.groups.filter(name=zoo_id).exists()):
			return view_function(*args, **kwargs)
		else:
			return redirect('home')
	
	return wrapper