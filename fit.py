#!/usr/bin/env python

import struct

class Fit:
  """Main class definition."""

  local_msg_types = {}
  msg_types = {
    0: 'File ID',
    1: 'Capabilities',
    2: 'Device Settings',
    20: 'Record',
    21: 'Event',
    23: 'Device Info',
    49: 'File Creator'}

  field_defs = {
    0: { 0: 'Type',
         1: 'Manufacturer',
         2: 'Product',
         3: 'Serial Number',
         4: 'Time Created',
         5: 'Number',
       },
    20: { 0: 'Latitude',
          1: 'Longitude',
          2: 'Altitude',
          3: 'Heart Rate',
          4: 'Cadence',
          5: 'Distance',
          6: 'Speed',
          7: 'Power',
          8: 'Compressed Speed/Distance',
          9: 'Grade',
          10: 'Resistance',
          11: 'Time from Course',
          12: 'Cycle Length',
          13: 'Temperature',
          253: 'Timestamp',
        },
    21: { 0: 'Event',
          1: 'Event Type',
          2: 'Data16',
          3: 'Data',
          4: 'Event Group',
          253: 'Timestamp',
        },
    23: { 0: 'Device Index',
          1: 'Device Type',
          2: 'Manufacturer',
          3: 'Serial Number',
          4: 'Product',
          5: 'Software Version',
          6: 'Hardware Version',
          7: 'Cumulative Operating Time',
          8: 'Unknown (8)',
          10: 'Battery Voltage',
          11: 'Battery Status',
          253: 'Timestamp',
        },
    49: { 0: 'Software Version',
          1: 'Hardware Version'
        }
  }

  def __init__(self, filename=None):
    """Constructor method."""
    self._header = {}
    self._local_messages = []
    self._records = []

    # Load a file, if given
    if filename:
      self.LoadFromFile(filename)

  def LoadFromFile(self, filename):
    """Loads data from a FIT file."""
    self._f = open(filename, 'rb')
    self._file_struct = {}

  def AddRecord(self, record):
    """Adds a record to the fit data structure."""
    self._records.append(record)

  @staticmethod
  def ConvertSemicirclesToDegrees(semicircles):
    """Converts semicircles to degrees."""
    degrees = semicircles * 180 / 2147483648
    return degrees

  def ReadHeader(self):
    """Reads the header record from the FIT file.
       The header is a mere 12 bytes and contains:
         - Length of the header (1 byte)
         - File protocol version (1 byte)
         - Profile version (2 bytes)
         - Size of data records section (4 bytes)
         - Data type (must be ascii text 'FIT') (4 bytes)
    """
    header = self._f.read(12)
    (self._header['header_size'],
     self._header['protocol_version'],
     self._header['profile_version'],
     self._header['data_size'],
     self._header['data_type'])  = struct.unpack('<BBHII', header)

    # Set a varible to keep track of file reading
    self._data_remaining = self._data_size

  def GetNextRecord(self):
    """Gets the next record in the file.
       Records can be either definition records or data records.
    """

    # Read the first byte to determine:
    #   1. Whether this is a definition or a data record, and
    #   2. What the local message type is
    data = self._f.read(1)
    self._data_remaining -= 1
    record = struct.unpack('<B', data)
    record_type = record[0]

    # The seventh digit in the bit array defines record type.
    if record_type & 64 == 64:
      # Pass the local record type (first four bits)
      self.GetDefinitionRecord(record_type & 15)
      return Record.DEFINITION
    else:
      # Pass the local record type (first four bits)
      self.GetDataRecord(record_type & 15)
      return Record.DATA

  def GetDefinitionRecord(self, local_msg_type):
    """Fetches the definition record that defines the proceeding data record."""

    # The record header always starts with 5 bytes of information:
    # - Reserved (1 byte)
    # - Architecture (1 byte)
    # - Global Message Number (2 bytes)
    # - Number of fields (1 byte)
    data = self._f.read(5)
    self._data_remaining -= 5
    (reserved, arch, msg_no, num_fields) = struct.unpack('<BBHB', data)
    fields = []
    
    # Step through the field definitions. Each is 3 bytes.
    for i in range(num_fields):
      data = self._f.read(3)
      self._data_remaining -= 3
      (def_num, field_size, base_type) = struct.unpack('<BBB', data)
      field = Field(def_num, field_size, base_type)
      fields.append(field)

    message = Message(Message.LOCAL, msg_no=msg_no, fields=fields)

    self.AddMessage(message)

    record = Record(Record.DEFINITION,
                    arch=arch,
                    msg_no=msg_no,
                    num_fields=num_fields,
                    fields=fields)

    self.AddRecord(record)

  def GetDataRecord(self, local_msg_type):
    """Fetches a data record."""

    data = {}
    fields = self.local_msg_types[local_msg_type]['fields']
    if fields:
      for field in fields:
        raw_data = self._f.read(field['field_size'])
        self._data_remaining -= field['field_size']
        if field['field_size'] == 1:
          (field_data) = struct.unpack('<B', raw_data)
        elif field['field_size'] == 2:
          (field_data) = struct.unpack('<H', raw_data)
        elif field['field_size'] == 4:
          (field_data) = struct.unpack('<I', raw_data)
        data[field['def_num']] = field_data[0]
        try:
          print '  %s: %d' % (self.field_defs[self.local_msg_types[local_msg_type]['msg_no']][field['def_num']], field_data[0])
        except KeyError:
          print '  %d: %d' % (field['def_num'], field_data[0])
      return data
    return None

  def ProcessDefinitionRecord(self):
    """Reads a definition message and returns a list of fields to be processed."""

  def Process(self):
    """Main entry for class."""
    self.ReadHeader()
    while self._data_remaining > 0:
      self.GetNextRecord()
      print ''


class Record(object):
  """Represents a FIT file record."""

  DEFINITION = 1
  DATA = 2

  def __init__(self, type,
               arch=None,
               msg_no=None,
               num_fields=None
               fields=[]):
    """Constructor."""
    self._type = type


class Field(object):
  """Represents a field in a Record."""

  def __init__(self, def_num, field_size, base_type):
    """Default constructor."""
    self._def_num = def_num
    self._field_size = field_size
    self._base_type = base_type


class Message(object):
  """Represents a message (local or global)."""

  GLOBAL = 1
  LOCAL = 2

  def __init__(self, type, fields=None):
    """Default constructor."""
    self._type = type
    self._fields = fields

