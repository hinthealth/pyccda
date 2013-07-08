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
  ENCOUNTER = '2.16.840.1.113883.10.20.22.4.49'
  IMMUNIZATION = '2.16.840.1.113883.10.20.22.2.2.1'
  IMMUNIZATION_PRODUCT = '2.16.840.1.113883.10.20.22.4.54'
  LAB = '2.16.840.1.113883.10.20.22.2.3.1'
  MEDICATION = '2.16.840.1.113883.10.20.22.4.16'
  PROBLEM = '2.16.840.1.113883.10.20.22.4.4'
  PROBLEM_STATUS = '2.16.840.1.113883.10.20.22.4.6'
  PROCEDURE = '2.16.840.1.113883.10.20.22.2.7.1'
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


# TODO: Add more fields to the CSV.
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

  def get_entries_by_template(self, root, parent=None):
    if parent is None:
      parent = self._doc
    nodes = [
        node.parentNode
        for node in parent.getElementsByTagName('templateId')
        if node.getAttribute('root') == root]
    return nodes

  @classmethod
  def get_date_from_effective_time(cls, entry):
    val = entry.getElementsByTagName('effectiveTime')[0].getAttribute('value')
    return cls.get_date_from_value(val)

  @classmethod
  def get_date_from_value(cls, val):
    if len(val) == len('YYYYMMDD'):
      datetime_format = '%Y%m%d'
    elif len(val) == len('YYYYMMDDHHMMSS'):
      datetime_format = '%Y%m%d%H%M%S'
    return datetime.datetime.strptime(val, datetime_format)

  @classmethod
  def get_date_range_from_node(cls, date_node):
    low_nodes = date_node.getElementsByTagName('low')
    low = low_nodes[0].getAttribute('value') if low_nodes else None
    high_nodes = date_node.getElementsByTagName('high')
    high = high_nodes[0].getAttribute('value') if high_nodes else None
    return {
        'start': cls.get_date_from_value(low) if low else None,
        'end': cls.get_date_from_value(high) if high else None,
    }

  @classmethod
  def get_quantity_message_from_node(cls, node):
    quantity = messages.Quantity()
    quantity.value = node.getAttribute('value')
    quantity.unit = node.getAttribute('unit')
    return quantity


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
    # TODO: Remove duplicate code.
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
    doc.immunizations = []
    entries = self._tree.get_entries_by_template(Root.IMMUNIZATION)
    for entry in entries:
      product_node = self._tree.get_entries_by_template(
          Root.IMMUNIZATION_PRODUCT, parent=entry)[0]
      immunization = messages.Immunization()
      immunization.date = CcdaTree.get_date_from_effective_time(entry)
      immunization.product = messages.Product()
      code_node = product_node.getElementsByTagName('code')[0]
      product_code = CcdaTree.get_code_from_node(code_node)
      immunization.product.code = messages.Code(**product_code)

    # Labs.
    doc.labs = []
    lab_parent = self._tree.get_entries_by_template(Root.LAB)[0]
    entries = lab_parent.getElementsByTagName('entry')
    for entry in entries:
      lab = messages.Lab()
      code_node = entry.getElementsByTagName('code')[0]
      lab_code = CcdaTree.get_code_from_node(code_node)
      lab.code = messages.Code(**lab_code)

      lab.result = messages.LabResult()
      component_node = entry.getElementsByTagName('component')[0]
      result_code_node = component_node.getElementsByTagName('code')[0]
      result_code = CcdaTree.get_code_from_node(result_code_node)
      lab.result.code = messages.Code(**result_code)

      doc.labs.append(lab)

    # Medications.
    doc.medications = []
    entries = self._tree.get_entries_by_template(Root.MEDICATION)
    for entry in entries:
      medication = messages.Medication()
      medication.product = messages.Product()

      date_node = entry.getElementsByTagName('effectiveTime')[0]
      date_range = CcdaTree.get_date_range_from_node(date_node)
      medication.date_range = messages.DateRange(**date_range)

      product_node = entry.getElementsByTagName('manufacturedProduct')[0]
      product_code_node = product_node.getElementsByTagName('code')[0]
      product_code = CcdaTree.get_code_from_node(product_code_node)
      medication.product.code = messages.Code(**product_code)

      quantity_nodes = entry.getElementsByTagName('doseQuantity')
      if quantity_nodes:
        node = quantity_nodes[0]
        medication.dose_quantity = CcdaTree.get_quantity_message_from_node(node)

      rate_nodes = entry.getElementsByTagName('rateQuantity')
      if rate_nodes:
        node = rate_nodes[0]
        medication.rate_quantity = CcdaTree.get_quantity_message_from_node(node)

      # TODO: precondition, reason, route, vehicle, administration, prescriber.
      doc.medications.append(medication)

    # Problems.
    doc.problems = []
    entries = self._tree.get_entries_by_template(Root.PROBLEM)
    for entry in entries:
      problem = messages.Problem()

      code_node = entry.getElementsByTagName('code')[0]
      problem_code = CcdaTree.get_code_from_node(code_node)
      problem.code = messages.Code(**problem_code)

      date_node = entry.getElementsByTagName('effectiveTime')[0]
      date_range = CcdaTree.get_date_range_from_node(date_node)
      problem.date_range = messages.DateRange(**date_range)

      status_nodes = self._tree.get_entries_by_template(Root.PROBLEM_STATUS,
                                                       parent=entry)
      if status_nodes:
        status_node = status_nodes[0]
        entry_node = status_node.getElementsByTagName('value')[0]
        problem.status = entry_node.getAttribute('displayName')

      # TODO: Implement problem.age.
      doc.problems.append(problem)

    # Procedures.
    doc.procedures = []
    procedure_parent = self._tree.get_entries_by_template(Root.PROCEDURE)[0]
    entries = procedure_parent.getElementsByTagName('entry')
    for entry in entries:
      procedure = messages.Procedure()
      code_node = entry.getElementsByTagName('code')[0]
      procedure_code = CcdaTree.get_code_from_node(code_node)
      procedure.code = messages.Code(**procedure_code)
      procedure.date = CcdaTree.get_date_from_effective_time(entry)

      # TODO: Implement specimen, performer, device.
      doc.procedures.append(procedure)

    # Vitals.
    doc.vitals = []
    entries = self._tree.get_entries_by_template(Root.VITAL)
    for entry in entries:
      vital = messages.Vital()
      vital.date = CcdaTree.get_date_from_effective_time(entry)
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
