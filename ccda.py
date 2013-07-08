"""A basic CCDA library for Python.

  Usage:
    import pyccda
    ccda = pyccda.CcdaDocument(<File pointer to a CCDA XML file.>)
    ccda.to_message()  # Returns CCDA represented as a ProtoRPC message.
    ccda.to_csv()  # Returns CCDA represented as a CSV.
"""

from xml.dom import minidom
import cStringIO
import csv
import datetime
import messages


class Root(object):
  """The "root" attribute of templateId elements."""
  ALLERGY = '2.16.840.1.113883.10.20.22.4.7'
  MEDICATION = '2.16.840.1.113883.10.20.22.4.16'
  IMMUNIZATION = '2.16.840.1.113883.10.20.22.2.2.1'
  PROBLEM = '2.16.840.1.113883.10.20.22.4.4'
  PROCEDURE = '2.16.840.1.113883.10.20.22.4.14'
  ENCOUNTER = '2.16.840.1.113883.10.20.22.4.49'
  VITAL = '2.16.840.1.113883.10.20.22.2.4.1'


class Field(object):
  """A field of a CSV or BigQuery table representation of a CCDA."""

  def __init__(self, name, type='STRING', mode='NULLABLE'):
    self.name = name
    self.type = type
    self.mode = mode

  def to_json(self):
    return {
      'name': self.name,
      'type': self.type,
      'mode': self.mode,
    }


CSV_FIELDS = [
    Field('birthplace_city'),
    Field('birthplace_state'),
    Field('birthplace_postal_code'),
    Field('birthplace_country'),
    Field('dob', type='INTEGER'),
    Field('marital_status'),
    Field('gender'),
    Field('race'),
    Field('ethnicity'),
    Field('religion'),
]


class CcdaTree(object):
  """A CCDA document represented as a tree of nodes."""

  def __init__(self, fp):
    self._doc = minidom.parse(fp)

  @classmethod
  def get_code_from_node(cls, node):
    return {
        'code': node.getAttribute('code') if node else None,
        'code_system': node.getAttribute('codeSystem') if node else None,
        'name': node.getAttribute('displayName') if node else None,
    }

  def _get_element_by_tag_name(self, tag_name):
    nodes = self._doc.getElementsByTagName(tag_name)
    return nodes[0] if nodes else None

  def _get_code_from_tag_name(self, tag_name):
    node = self._get_element_by_tag_name(tag_name)
    return CcdaTree.get_code_from_node(node)

  def _get_value_of_child_by_tag_name(self, parent_node, tag_name):
    return parent_node.getElementsByTagName(tag_name)[0].firstChild.nodeValue

  def get_dob(self):
    val = self._get_element_by_tag_name('birthTime').getAttribute('value')
    return datetime.datetime.strptime(val, '%Y%M%d')

  def get_gender(self):
    return self._get_code_from_tag_name('administrativeGenderCode')

  def get_marital_status(self):
    return self._get_code_from_tag_name('maritalStatusCode')

  def get_language(self):
    return self._get_element_by_tag_name('languageCode').getAttribute('code')

  def get_race(self):
    return self._get_code_from_tag_name('raceCode')

  def get_ethnicity(self):
    return self._get_code_from_tag_name('ethnicGroupCode')

  def get_religion(self):
    return self._get_code_from_tag_name('religiousAffiliationCode')

  def get_birthplace(self):
    node = self._get_element_by_tag_name('birthplace')
    if not node:
      return {
          'city': None,
          'state': None,
          'postal_code': None,
          'country': None,
      }
    addr_node = node.getElementsByTagName('addr')[0]
    _get_val = self._get_value_of_child_by_tag_name
    return {
        'city': _get_val(addr_node, 'city'),
        'state': _get_val(addr_node, 'state'),
        'postal_code': _get_val(addr_node, 'postalCode'),
        'country': _get_val(addr_node, 'country'),
    }

  def get_entries_by_template(self, root):
    nodes = [
        node.parentNode
        for node in self._doc.getElementsByTagName('templateId')
        if node.getAttribute('root') == root]
    return nodes


class CcdaDocument(object):
  """A CCDA document that can be represented in various ways."""

  def __init__(self, fp):
    self._tree = CcdaTree(fp)

  def to_csv(self):
    """Converts the CCDA document to a CSV file."""
    message = self.to_message()
    row = {
        'birthplace_city': message.demographics.birthplace.city,
        'birthplace_country': message.demographics.birthplace.country,
        'birthplace_postal_code': message.demographics.birthplace.postal_code,
        'birthplace_state': message.demographics.birthplace.state,
        'dob': message.demographics.dob,
        'ethnicity': message.demographics.ethnicity.code,
        'gender': message.demographics.gender.code,
        'marital_status': message.demographics.marital_status.name,
        'race': message.demographics.race.code,
        'religion': message.demographics.ethnicity.code,
    }
    fp = cStringIO.StringIO()
    writer = csv.DictWriter(fp, [field.name for field in CSV_FIELDS])
    writer.writeheader()
    writer.writerow(row)
    fp.seek(0)
    return fp.read()

  def to_message(self):
    """Converts the CCDA document to a ProtoRPC message."""
    doc = messages.CcdaDocument()

    # Allergies.
    # TODO: Implement allergies.
    doc.allergies = [messages.Allergy()]

    # Demographics.
    doc.demographics = messages.Demographic()
    doc.demographics.dob = self._tree.get_dob()
    doc.demographics.gender = messages.Code(**self._tree.get_gender())
    doc.demographics.marital_status = messages.Code(
        **self._tree.get_marital_status())
    doc.demographics.language = self._tree.get_language()
    doc.demographics.race = messages.Code(
        **self._tree.get_race())
    doc.demographics.ethnicity = messages.Code(
        **self._tree.get_ethnicity())
    doc.demographics.religion = messages.Code(
        **self._tree.get_religion())
    doc.demographics.birthplace = messages.Address(
        **self._tree.get_birthplace())

    # Immunizations.
    # TODO: Implement immuniations.
    doc.immunizations = []
    entries = self._tree.get_entries_by_template(Root.IMMUNIZATION)
    for entry in entries:
      immunization = messages.Immunization()
      doc.immunizations.append(immunization)

    # Labs.
    # TODO: Implement labs.
    doc.labs = []

    # Medications.
    # TODO: Implement medications.
    doc.medications = []

    # Problems.
    # TODO: Implement problems.
    doc.problems = []

    # Procedures.
    # TODO: Implement procedures.
    doc.procedures = []

    # Vitals.
    doc.vitals = []
    entries = self._tree.get_entries_by_template(Root.VITAL)
    for entry in entries:
      vital = messages.Vital()
      val = entry.getElementsByTagName('effectiveTime')[0].getAttribute('value')
      if len(val) == len('YYYYMMDD'):
        datetime_format = '%Y%m%d'
      elif len(val) == len('YYYYMMDDHHMMSS'):
        datetime_format = '%Y%m%d%H%M%S'
      vital.date = datetime.datetime.strptime(val, datetime_format)
      vital.results = []
      result_entries = entry.getElementsByTagName('component')
      for result_entry in result_entries:
        vital_result = messages.VitalResult()
        code_node = result_entry.getElementsByTagName('code')[0]
        value_node = result_entry.getElementsByTagName('value')[0]
        vital_result_code = CcdaTree.get_code_from_node(code_node)
        vital_result.code = messages.Code(**vital_result_code)
        vital_result.value = long(float(value_node.getAttribute('value')))
        vital_result.unit = value_node.getAttribute('unit')
        vital.results.append(vital_result)
      doc.vitals.append(vital)

    return doc
