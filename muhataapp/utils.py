from models import Tag
from PIL import Image
from os import remove
from django.conf import settings


def handle_uploaded_file(f,id):
	path = 'C:/projects/muhata/muhataapp/static/user_data/' + str(id) + '.jpg'
	path2 = 'C:/projects/muhata/muhataapp/static/user_data/' + str(id) + '_thumb.jpg'
	destination = open(path, 'wb+')

	#less than 2.5 mb
	if f.size > 2621440:
		raise Http404

	for chunk in f.chunks():
		destination.write(chunk)
	destination.close()

	img_org = Image.open(path)

	width_org, height_org = img_org.size

	if width_org > height_org:
		new_w = 120
		new_h = ( 120 * height_org ) / width_org
	else:
		new_h = 120
		new_w = ( 120 * width_org ) / height_org

	img_anti = img_org.resize((new_w, new_h), Image.ANTIALIAS)
	img_anti.save(path2)




