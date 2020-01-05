from app.libs.redprint import Redprint
from app.validators.forms import ClientForm
from flask import request, json
from app.libs.enums import ClientTypeEnum
from app.models.user import User

api = Redprint('client')


@api.route('/register', methods=['POST'])
def create_client():
	data = request.json
	form = ClientForm(data=data)
	if form.validate():
		promise = {
			ClientTypeEnum.USER_EMAIL: __register_user_by_email,
		}


def __register_user_by_email(form):
	# User.register_by_email(,form.account.data, form.secret.data)
	pass