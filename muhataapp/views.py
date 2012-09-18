from muhataapp.models import AccountForm, Account, AdForm, Ad, Tag, MyAuthForm, EditAdForm
from muhataapp.utils import handle_uploaded_file

from django.shortcuts import HttpResponse, render_to_response, RequestContext, HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.template.defaultfilters import slugify
from django.views.decorators.cache import cache_page

from django.db.models import Count

from django.core.files.images import get_image_dimensions

import os

class MyException(Exception): pass

def home(request):
    vars = {}
    vars['ads'] = Ad.objects.order_by("-date")
    vars['tags'] = Tag.objects.order_by("-count")[:30]
    vars['acf'] = AccountForm()
    vars['auf'] = MyAuthForm()
    try:
        vars['flash_message'] = request.session['flash_msg']
        del request.session['flash_msg']
    except KeyError:
        pass

    return render_to_response('home.html', vars, context_instance=RequestContext(request))

def add_user_to_database(request):
    if request.POST:
        acf = AccountForm(request.POST)
        if acf.is_valid():
            username = acf.cleaned_data['username']
            password = acf.cleaned_data['password']
            email = acf.cleaned_data['email']
            #create accoutn:
            Account.objects.create_user(username,email = email, password = password)
            #login:
            user = authenticate(username=username, password=password)
            login(request,user)
            request.session['flash_msg'] = "Регистрацията е успешна."
            return HttpResponseRedirect("/dobavi-obqva/")
        else:
            request.session['flash_msg'] = "Неуспешна регистрация."
            return HttpResponseRedirect("/")
    else:
        raise MyException("Request is not POST, it is " + request.method )

def authenticate_and_login_user(request):
    if request.POST:
        vars = {}
        auf = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect("/dobavi-obqva/")
            else:
                raise MyException("This user has been deleted")
        else:
            request.session['flash_msg'] = "Неуспешен логин."
            return HttpResponseRedirect("/")
    else:
        raise MyException("Request is not POST, it is " + request.method )

def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")

def display_add_ad_page(request):
	if request.method == "GET":
		vars = {}
		try:
			vars['flash_message'] = request.session['flash_msg']
			del request.session['flash_msg']
		except KeyError:
			pass
		if request.user.is_authenticated():
			vars['adf'] = AdForm()
			vars['ads'] = Ad.objects.filter(author = request.user.id)
			return render_to_response('add_ad.html', vars, context_instance=RequestContext(request))
		else:   # redirect to frontpage and display message
			request.session['flash_msg'] = u"Само регистрирани потребители могат да добавят обяви"
			return HttpResponseRedirect("/")
	else:
		raise MyException("Only GET request allowed" + request.method)

def add_ad_to_database(request):
    if request.POST:
        vars = {}
        adf = AdForm(request.POST, request.FILES)
        if adf.is_valid():
            ad = Ad()
            if request.FILES:
                ad.has_pic = True
            else:
                ad.has_pic = False

            if ad.has_pic == True:
                w, h = get_image_dimensions( adf.cleaned_data['picture'] )
            	ad.picture_height = h
            	ad.picture_width = w

            ad.title = adf.cleaned_data['title']
            ad.content = adf.cleaned_data['content']
            ad.adult_content = adf.cleaned_data['adult_content']
            ad.author = request.user.id
            ad.save()

            if ad.has_pic == True:
                handle_uploaded_file( adf.cleaned_data['picture'] , ad.id)

            #increase or add tags:
            tags = request.POST['tags'].split()

            for tag in tags:
                tag, created = Tag.objects.get_or_create(name = tag)
                #associate tag and ad
                tag.ad.add(ad)

                if created == True:
                    #new tags already have count = 1
                    pass
                else:
                    tag.count += 1
                    tag.save()

            return HttpResponseRedirect("/obqva/" + str(ad.id) + "/")
        else:
            vars = {}
            vars['adf'] = adf
            return render_to_response('search_by_tag_results.html', vars, context_instance=RequestContext(request))
    else:
        raise MyException("Must be a POST request")

def add_slug(request, id):
    try:
        a = Ad.objects.get(id = id)
    except Ad.DoesNotExist:
        raise MyException("There is no add with this id")
    return HttpResponseRedirect(u"/obqva/" + id + "/" + a.slug + "/")

def display_ad(request, id, slug):
    vars = {}
    vars['acf'] = AccountForm()
    vars['auf'] = AuthenticationForm()
    try:
		a = Ad.objects.get(id = id)
    except Ad.DoesNotExist:
        raise MyException("There is no add with this id")

    if a.picture_width > 500:
        a.picture_height = ( a.picture_height * 500 ) / a.picture_width
        a.picture_width = 500
        a.save()

    vars['ad'] = a

    return render_to_response('ad.html', vars, context_instance=RequestContext(request))

def tag_search(request):
    """
    Search by tag relevance. Ads that match more tags are placed at the top.
    """
    if request.POST:
        vars = {}
        tags = request.POST['tags']
        tags = tags.split()
        vars['acf'] = AccountForm()
        vars['auf'] = AuthenticationForm()
        vars['tags'] = []
        vars['results'] = []
        res_ads = {}
        res = {}

        for tag in tags:
            try:
                t = Tag.objects.get(name = tag)
            except Tag.DoesNotExist:
                raise MyException("Tag '{0}' not found".format(tag))

            vars['tags'].append(t)

            ads = Ad.objects.filter(tag__name = tag)

            for ad in ads:
                if ad.id in res:
                    res[ad.id] += 1
                else:
                    res[ad.id] = 1
                    res_ads[ad.id] = ad

        #sort the dict by values
        from operator import itemgetter
        res_new = sorted(res.items(), key=itemgetter(1), reverse=True)

        for r in res_new:
            vars['results'].append( res_ads[ r[0] ] )

        return render_to_response('search_by_tag_results.html', vars, context_instance=RequestContext(request))
    else:
        raise MyException("request method is not POST")

def return_suggestions(request):
    tags = Tag.objects.order_by("-count")

    response = ""
    for tag in tags:
        response += tag.name + " "
    response = response[:-1]

    return HttpResponse(response, mimetype='application/javascript')

def report_ad(request, id):
	try:
		a = Ad.objects.get(id = id)
	except Ad.DoesNotExist:
		raise MyException("Ad not found")

	a.reported += 1
	a.save()
	return HttpResponse("")

def delete_ad(request, id):
	try:
		a = Ad.objects.get(id = id)
	except Ad.DoesNotExist:
		raise MyException("Ad not found")

	if request.user.id == a.author:
		a.delete()
		return HttpResponseRedirect("/dobavi-obqva/")
	else:
		raise MyException("You are not the author of this ad!")

def display_edit_ad(request, id):
	try:
		a = Ad.objects.get(id = id)
	except Ad.DoesNotExist:
		raise MyException("Ad not found")

	if request.user.id == a.author:
		vars = {}
		vars['adf'] = AdForm(instance = a)

		tags = Tag.objects.filter(ad = id)
		response = ""
		for tag in tags:
			response += tag.name + " "
		response = response[:-1]

		vars['tags'] = response
		vars['ad'] = a
		# if data is not correctly populated the "change ad" view will return a
		# flash message.
		try:
			vars['flash_message'] = request.session['flash_msg']
			del request.session['flash_msg']
		except KeyError:
			pass

		return render_to_response('edit_ad.html', vars, context_instance=RequestContext(request))
	else:
		raise MyException("You are not the author of this ad!")

def change_ad(request, id):
	if request.POST:
		try:
			a = Ad.objects.get(id = id)
		except Ad.DoesNotExist:
			raise MyException("Ad not found")
		if request.user.id == a.author:
			f = AdForm(request.POST, request.FILES, instance  = a)
			if f.is_valid():
				a.title = f.cleaned_data['title']
				a.content = f.cleaned_data['content']
				a.adult_content = f.cleaned_data['adult_content']

				if request.FILES:
					a.picture = str(id) + ".jpg"
					a.has_pic = True
					handle_uploaded_file( f.cleaned_data['picture'] , id)
					w, h = get_image_dimensions( f.cleaned_data['picture'] )
					a.picture_height = h
					a.picture_width = w
				else:
					a.has_pic = False

				a.save()

				org_tags = Tag.objects.filter(ad = id)
				tags = request.POST['tags'].split()

				# if tag was removed - delete or decrease count
				for ot in org_tags:
					if ot.name not in tags:
						if ot.count == 1:
							ot.delete()
						else:
							ot.count -= 1
							ot.save()

							#remove assoc. between tag and ad
							ot.ad.remove(a)


				# if tags was introduced - add on increase count
				org_tags = org_tags.values_list("name",flat=True)
				for t in tags:
					if t not in org_tags:
						ntag, created = Tag.objects.get_or_create(name = t)

						#assoc. tag and ad
						ntag.ad.add(a)

						if created == False:
							ntag.count += 1

						ntag.save()

				return HttpResponseRedirect("/obqva/" + id)
			else:
				request.session['flash_msg'] = "Невалидно попълнени данни"
				vars = {}
				vars['adf'] = f
				return render_to_response('edit_ad.html', vars, context_instance=RequestContext(request))
		else:
			raise MyException("You are not the author of this ad!")
	else:
		raise MyException("Not a POST request")

def delete_pic(request, id):

	try:
		a = Ad.objects.get(id = id)
	except Ad.DoesNotExist:
		return HttpResponse("Ad not found")

	if request.user.id == a.author:
		os.remove( 'C:/projects/muhata/muhataapp/static/user_data/' + str(id) + '.jpg' )
		os.remove( 'C:/projects/muhata/muhataapp/static/user_data/' + str(id) + '_thumb.jpg' )
		a.has_pic = False
		a.save()
		return HttpResponse("Снимката е изтрита")
	else:
		return HttpResponse("You cannot delete this")

