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

  def __init__(self, filename):
    """Constructor method."""
    self._f = open(filename, 'rb')

  def ReadHeader(self):
    """Reads the header record from the FIT file."""
    header = self._f.read(12)
    (self._header_size,
     self._protocol_version,
     self._profile_version,
     self._data_size,
     self._data_type)  = struct.unpack('<BBHII', header)
    
  def GetNextRecord(self):
    """Gets the next record in the file."""

    # Read the first byte to determine:
    #   1. Whether this is a definition or a data record, and
    #   2. What the local message type is
    data = self._f.read(1)
    record = struct.unpack('<B', data)
    record_type = record[0]

    # The seventh digit in the bit array defines this.
    if record_type & 64 == 64:
      # Pass the local record type (first four bits)
      self.GetDefinitionRecord(record_type & 15)
    else:
      # Pass the local record type (first four bits)
      self.GetDataRecord(record_type & 15)

  def GetDefinitionRecord(self, local_msg_type):
    """Fetches the definition record that defines the proceeding data record."""

    # The record header is always 5 bytes
    data = self._f.read(5)
    (reserved, arch, msg_no, num_fields) = struct.unpack('<BBHB', data)
    local_msg = {'arch': arch,
                 'msg_no': msg_no,
                 'num_fields': num_fields,
                 'fields': []}

    # Step through the field definitions. Each are 3 bytes.
    for i in range(num_fields):
      data = self._f.read(3)
      (def_num, field_size, base_type) = struct.unpack('<BBB', data)
      local_msg['fields'].append({'def_num': def_num, 'field_size': field_size})
    self.local_msg_types[local_msg_type] = local_msg

  def GetDataRecord(self, local_msg_type):
    """Fetches a data record."""

    print 'Data record found: local_msg_type=%d' % (local_msg_type)

    fields = self.local_msg_types[local_msg_type]['fields']
    if fields:
      total_bytes_read = 0
      for field in fields:
        total_bytes_read += field['field_size']
        data = self._f.read(field['field_size'])
        if field['field_size'] == 1:
          (field_data) = struct.unpack('<B', data)
        elif field['field_size'] == 2:
          (field_data) = struct.unpack('<H', data)
        elif field['field_size'] == 4:
          (field_data) = struct.unpack('<I', data)
        try:
          print '  %s: %d' % (self.field_defs[self.local_msg_types[local_msg_type]['msg_no']][field['def_num']], field_data[0])
        except KeyError:
          print '  %d: %d' % (field['def_num'], field_data[0])

  def ProcessDefinitionRecord(self):
    """Reads a definition message and returns a list of fields to be processed."""

  def Process(self):
    """Main entry for class."""
    self.ReadHeader()
    for i in range(200):
      self.GetNextRecord()
      print ''

if __name__ == '__main__':
  fit = Fit('/home/brooks/500.fit')
  fit.Process()
  
