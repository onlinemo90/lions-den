from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .decorators import login_and_zoo_access_required
from .zoos import zoos
from .models import Species

@login_required
def zoos_index(request):
	#TODO: move this permission-check logic into a User model method
	if request.user.is_superuser:
		allowed_zoos = zoos.values()
	else:
		allowed_zoos = [zoos[user_group.name] for user_group in request.user.groups.all() if user_group.name in zoos]
	
	if len(allowed_zoos) == 1:
		return redirect(allowed_zoos[0].id + '/')
	return render(
		request=request,
		template_name='model_editor/zoos_index.html',
		context={'zoos' : allowed_zoos}
	)

@login_and_zoo_access_required
def zoo_home(request, zoo_id):
	all_species = Species.objects.using(zoo_id).all()
	return render(
		request=request,
		template_name='model_editor/zoo.html',
		context={'zoo': zoos[zoo_id], 'all_species' : all_species}
	)

@login_and_zoo_access_required
def species(request, zoo_id, species_id):
	species = Species.objects.using(zoo_id).filter(id=species_id).get()
	return render(
		request=request,
		template_name='model_editor/species.html',
		context={'zoo': zoos[zoo_id], 'species': species}
	)
