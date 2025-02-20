# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: safeEntry.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fsafeEntry.proto\x12\tsafeEntry\"\x07\n\x05\x45mpty\"\x89\x01\n\x07Request\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04nric\x18\x02 \x01(\t\x12\x10\n\x08location\x18\x03 \x01(\t\x12\x0f\n\x07\x63heckin\x18\x04 \x01(\t\x12\x10\n\x08\x63heckout\x18\x05 \x01(\t\x12\x13\n\x0bgroupnumber\x18\x06 \x01(\x05\x12\n\n\x02id\x18\x07 \x01(\t\x12\x0c\n\x04\x66lag\x18\x08 \x01(\x05\"\x18\n\x05Reply\x12\x0f\n\x07message\x18\x01 \x01(\t\"D\n\x0c\x44\x65layedReply\x12\x0f\n\x07message\x18\x01 \x01(\t\x12#\n\x07request\x18\x02 \x03(\x0b\x32\x12.safeEntry.Request2\x83\x04\n\tSafeEntry\x12\x31\n\x07\x43heckIn\x12\x12.safeEntry.Request\x1a\x10.safeEntry.Reply\"\x00\x12\x32\n\x08\x43heckOut\x12\x12.safeEntry.Request\x1a\x10.safeEntry.Reply\"\x00\x12\x38\n\x0cGroupCheckIn\x12\x12.safeEntry.Request\x1a\x10.safeEntry.Reply\"\x00(\x01\x12\x37\n\rGroupCheckOut\x12\x12.safeEntry.Request\x1a\x10.safeEntry.Reply\"\x00\x12:\n\x0eHistoryListing\x12\x12.safeEntry.Request\x1a\x10.safeEntry.Reply\"\x00\x30\x01\x12\x35\n\tListCases\x12\x10.safeEntry.Reply\x1a\x10.safeEntry.Reply\"\x00(\x01\x30\x01\x12\x37\n\x0f\x44\x65\x63lareAffected\x12\x10.safeEntry.Reply\x1a\x10.safeEntry.Reply\"\x00\x12\x33\n\x0bGetNotified\x12\x10.safeEntry.Reply\x1a\x10.safeEntry.Reply\"\x00\x12;\n\x11LogInNotification\x12\x10.safeEntry.Reply\x1a\x10.safeEntry.Reply\"\x00\x30\x01\x62\x06proto3')



_EMPTY = DESCRIPTOR.message_types_by_name['Empty']
_REQUEST = DESCRIPTOR.message_types_by_name['Request']
_REPLY = DESCRIPTOR.message_types_by_name['Reply']
_DELAYEDREPLY = DESCRIPTOR.message_types_by_name['DelayedReply']
Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), {
  'DESCRIPTOR' : _EMPTY,
  '__module__' : 'safeEntry_pb2'
  # @@protoc_insertion_point(class_scope:safeEntry.Empty)
  })
_sym_db.RegisterMessage(Empty)

Request = _reflection.GeneratedProtocolMessageType('Request', (_message.Message,), {
  'DESCRIPTOR' : _REQUEST,
  '__module__' : 'safeEntry_pb2'
  # @@protoc_insertion_point(class_scope:safeEntry.Request)
  })
_sym_db.RegisterMessage(Request)

Reply = _reflection.GeneratedProtocolMessageType('Reply', (_message.Message,), {
  'DESCRIPTOR' : _REPLY,
  '__module__' : 'safeEntry_pb2'
  # @@protoc_insertion_point(class_scope:safeEntry.Reply)
  })
_sym_db.RegisterMessage(Reply)

DelayedReply = _reflection.GeneratedProtocolMessageType('DelayedReply', (_message.Message,), {
  'DESCRIPTOR' : _DELAYEDREPLY,
  '__module__' : 'safeEntry_pb2'
  # @@protoc_insertion_point(class_scope:safeEntry.DelayedReply)
  })
_sym_db.RegisterMessage(DelayedReply)

_SAFEENTRY = DESCRIPTOR.services_by_name['SafeEntry']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _EMPTY._serialized_start=30
  _EMPTY._serialized_end=37
  _REQUEST._serialized_start=40
  _REQUEST._serialized_end=177
  _REPLY._serialized_start=179
  _REPLY._serialized_end=203
  _DELAYEDREPLY._serialized_start=205
  _DELAYEDREPLY._serialized_end=273
  _SAFEENTRY._serialized_start=276
  _SAFEENTRY._serialized_end=791
# @@protoc_insertion_point(module_scope)
