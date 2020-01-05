from app.libs.redprint import Redprint

api = Redprint('book')


@api.route('/get')
def get_user():
	return "i am qiye"