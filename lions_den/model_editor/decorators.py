import functools
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# noinspection PyUnresolvedReferences
from zoo_auth.models import Zoo

def login_and_zoo_access_required(view_function):
	@functools.wraps(view_function)
	@login_required(login_url='login')
	def wrapper(*args, **kwargs):
		# Get request and zoo_id arguments
		request = kwargs['request'] if 'request' in kwargs else args[0]
		zoo_id = kwargs['zoo_id'] if 'zoo_id' in kwargs else args[1]
		
		# Check user permissions
		if request.user.zoos.filter(id=zoo_id).exists() or request.user.is_superadmin:
			return view_function(*args, **kwargs)
		else:
			return redirect('home')
	
	return wrapper