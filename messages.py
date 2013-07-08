"""ProtoRPC message definition for a CCDA document."""

from protorpc import message_types
from protorpc import messages


class Code(messages.Message):
  name = messages.StringField(1)
  code = messages.StringField(2)
  code_system = messages.StringField(3)
  code_system_name = messages.StringField(4)


class DateRange(messages.Message):
  start = message_types.DateTimeField(1)
  end = message_types.DateTimeField(2)


class Allergy(messages.Message):
  code = messages.MessageField(Code, 1)
  date_range = messages.MessageField(DateRange, 2)
  severity = messages.StringField(3)
  reaction = messages.MessageField(Code, 4)
  reaction_type = messages.MessageField(Code, 5)
  allergen = messages.MessageField(Code, 6)


class Address(messages.Message):
  # TODO: street.
  city = messages.StringField(1)
  state = messages.StringField(2)
  postal_code = messages.StringField(3)
  country = messages.StringField(4)


class Guardian(messages.Message):
  # TODO: name, phone.
  address = messages.MessageField(Address, 1)
  relationship = messages.StringField(2)


class Demographic(messages.Message):
  # TODO: name, phone.
  dob = message_types.DateTimeField(1)
  gender = messages.MessageField(Code, 2)
  marital_status = messages.MessageField(Code, 3)
  language = messages.StringField(4)
  race = messages.MessageField(Code, 5)
  ethnicity = messages.MessageField(Code, 6)
  religion = messages.MessageField(Code, 7)
  birthplace = messages.MessageField(Address, 8)


class Provider(messages.Message):
  organization = messages.StringField(1)
  address = messages.MessageField(Address, 2)
  # TODO: phone.


class Encounter(messages.Message):
  # TODO: implement me.
  pass


class Product(messages.Message):
  code = messages.MessageField(Code, 1)
  # TODO: translation, route, instructions, education_type.


class Immunization(messages.Message):
  date = message_types.DateTimeField(1)
  product = messages.MessageField(Product, 2)


class LabResult(messages.Message):
  date = message_types.DateTimeField(1)
  code = messages.MessageField(Code, 2)
  value = messages.IntegerField(3)
  unit = messages.StringField(4)
  # TODO: reference.


class Lab(messages.Message):
  code = messages.MessageField(Code, 1)
  result = messages.MessageField(LabResult, 2)


class Quantity(messages.Message):
  value = messages.StringField(1)
  unit = messages.StringField(2)


class Prescriber(messages.Message):
  organization = messages.StringField(1)
  person = messages.StringField(2)


class Medication(messages.Message):
  date_range = messages.MessageField(DateRange, 1)
  product = messages.MessageField(Product, 2)
  quantity = messages.MessageField(Quantity, 3)
  precondition = messages.MessageField(Code, 4)
  reason = messages.MessageField(Code, 5)
  route = messages.MessageField(Code, 6)
  vehicle = messages.MessageField(Code, 7)
  administration = messages.MessageField(Code, 8)
  prescriber = messages.MessageField(Prescriber, 9)


class Problem(messages.Message):
  code = messages.MessageField(Code, 1)
  status = messages.StringField(2)
  age = messages.IntegerField(3)
  date_range = messages.MessageField(DateRange, 4)


class Procedure(messages.Message):
  date = message_types.DateTimeField(1)
  code = messages.MessageField(Code, 2)
  specimen = messages.MessageField(Code, 3)
  device = messages.MessageField(Code, 4)
  performer = messages.MessageField(Provider, 5)


class VitalResult(messages.Message):
  code = messages.MessageField(Code, 1)
  value = messages.IntegerField(2)
  unit = messages.StringField(3)


class Vital(messages.Message):
  date = message_types.DateTimeField(1)
  results = messages.MessageField(VitalResult, 2, repeated=True)


class CcdaDocument(messages.Message):
  allergies = messages.MessageField(Allergy, 1, repeated=True)
  demographics = messages.MessageField(Demographic, 2)
  # TODO: encounters.
  immunizations = messages.MessageField(Immunization, 3, repeated=True)
  labs = messages.MessageField(Lab, 4, repeated=True)
  medications = messages.MessageField(Medication, 5, repeated=True)
  problems  = messages.MessageField(Problem, 6, repeated=True)
  procedures = messages.MessageField(Procedure, 7, repeated=True)
  vitals = messages.MessageField(Vital, 8, repeated=True)
