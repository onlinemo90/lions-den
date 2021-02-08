from io import BytesIO
import qrcode, base64
from .encryption import encrypt

BASE_URL = 'https://zooverse.org?'

def create_request_qrcode(zoo, request):
	request_str = '&'.join((f'{key}={value}' for key,value in request.items()))
	url = BASE_URL + encrypt(request_str, zoo.encryption_key)
	qrcode_string = BytesIO()
	qrcode.make(url).save(qrcode_string, 'png')
	return base64.b64encode(qrcode_string.getvalue()).decode()
