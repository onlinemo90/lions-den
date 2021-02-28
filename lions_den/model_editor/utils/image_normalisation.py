import io
import base64
import functools

from PIL import Image


def _open_image(img_file):
	"""
	Camera orientation is stored in the image metadata (EXIF data).
	PIL's Image.open() does not account for this, causing silent image rotation.
	
	Apply Image.transpose to ensure 0th row of pixels is at the visual
	top of the image, and 0th column is the visual left-hand side.
	Return the original image if unable to determine the orientation.

	As per CIPA DC-008-2012, the orientation field contains an integer,
	1 through 8. Other values are reserved.
	"""
	img = Image.open(img_file)
	exif_orientation_tag = 0x0112
	exif_transpose_sequences = [  # Val  0th row  0th col
		[],  # 0    (reserved)
		[],  # 1   top      left
		[Image.FLIP_LEFT_RIGHT],  # 2   top      right
		[Image.ROTATE_180],  # 3   bottom   right
		[Image.FLIP_TOP_BOTTOM],  # 4   bottom   left
		[Image.FLIP_LEFT_RIGHT, Image.ROTATE_90],  # 5   left     top
		[Image.ROTATE_270],  # 6   right    top
		[Image.FLIP_TOP_BOTTOM, Image.ROTATE_90],  # 7   right    bottom
		[Image.ROTATE_90],  # 8   left     bottom
	]
	
	try:
		seq = exif_transpose_sequences[img._getexif()[exif_orientation_tag]]
	except:
		return img
	else:
		return functools.reduce(type(img).transpose, seq, img)


def normalised_html_image_str(img_file, model):
	img = _open_image(img_file)
	width, height = img.size
	x_min, x_max, y_min, y_max = 0, width, 0, height
	aspect_ratio = model.image.field.size[0] / model.image.field.size[1]
	
	# Crop
	if width / height < aspect_ratio:  # image too tall
		new_width, new_height = width, round(width / aspect_ratio)
		y_min = round((height - new_height) // 2)
		y_max = y_min + new_height
	elif width / height > aspect_ratio:  # image too wide
		new_width, new_height = height * aspect_ratio, height
		x_min = round((width - new_width) // 2)
		x_max = x_min + new_width
	img = img.crop((x_min, y_min, x_max, y_max))
	
	# Scale
	img = img.resize(model.image.field.size, Image.ANTIALIAS)
	
	# Output
	output = io.BytesIO()
	img.save(output, format=model.image.field.format)
	base64_img_str = base64.b64encode(output.getvalue()).decode()
	return f'data:image/{model.image.field.format};base64,{base64_img_str}'