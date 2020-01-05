from app.libs.redprint import Redprint
from app.validators.forms import ClientForm
from flask import request, json
from app.libs.enums import ClientTypeEnum

api = Redprint('client')


@api.route('/register', methods=['POST'])
def create_client():
	data = request.json
	form = ClientForm(data=data)
	if form.validate():
		promise = {
			ClientTypeEnum.USER_EMAIL: __register_by_email,
		}


def __register_by_email():
	pass