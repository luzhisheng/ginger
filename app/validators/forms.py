from wtforms import Form, StringField, IntegerField
from wtforms.validators import DataRequired, length
from app.libs.enums import ClientTypeEnum


class ClientForm(Form):
	account = StringField(validators=[DataRequired(),
									  length(max=32, min=5)])
	secret = StringField(validators=[DataRequired()])
	type = IntegerField(validators=[DataRequired()])

	def validate_type(self, value):
		try:
			client = ClientTypeEnum(value.data)
		except ValueError as e:
			raise e


class UserEmailForm(ClientForm):
	pass