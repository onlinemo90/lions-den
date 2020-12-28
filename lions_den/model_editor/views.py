from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .decorators import login_and_zoo_access_required
from .zoos import zoos
from .models import Species

@login_required
def zoos_index(request):
	allowed_zoos = [zoos[zoo_id] for zoo_id in zoos if request.user.has_perm('zoo:' + zoo_id + ':access')]
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
