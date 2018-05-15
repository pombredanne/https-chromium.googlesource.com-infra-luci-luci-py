# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Utility functions for google.protobuf.field_mask_pb2.FieldMask."""

import contextlib

from google import protobuf
from google.protobuf import descriptor


def trim_message(msg, field_mask):
  """Clears msg fields that are not in the field_mask.

  This is a noop if field_mask is empty.

  This supports advanced field mask semantics:
  - Refer to fields and map keys using . literals:
    - Supported map key types: string, integer types, bool.
    - Floating point (including double and float), enum, and bytes keys are not
      supported by protobuf or this spec.
    - Fields: publisher.name
    - string keys: metadata.year
    - integer keys (e.g. int32): year_ratings.0
    - bool keys: access_text.true
  - String map keys that cannot be represented as an unquoted string literal,
    must be quoted using backticks: metadata.`year.published`, metadata.`17`,
    metadata.``, metatadata.`hi``bye`
  - Refer to all map keys using a * literal: topics.*.archived
  - Refer to all elements of a repeated field using a * literal: authors.*.name
  - Refer to all fields of a message using * literal: publisher.*.
  - Prohibit addressing a single element in repeated fields: authors.0.name

  TODO(nodir): replace spec above with a link to a spec when it is avialble.

  Args:
    msg: a google.protobuf.message.Message instance.
    field_mask: a google.protobuf.field_mask_pb2.FieldMask instance.
  """
  paths = [parse_path(p, msg.DESCRIPTOR) for p in field_mask.paths]
  _trim_message(msg, parse_field_tree(paths))


def _trim_message(message, field_tree):
  """Clears a protobuf message according to a field mask.

  field_tree must be in dict format. See parse_field_tree.
  """

  # Path to the current field value.
  path = []

  @contextlib.contextmanager
  def with_comp(comp):
    path.append(comp)
    try:
      yield
    finally:
      path.pop()

  include = lambda: must_include(field_tree, tuple(path))

  def trim_msg(msg):
    for f, v in msg.ListFields():
      with with_comp(f.name):
        incl = include()
        if incl == INCLUDE_RECURSIVELY:
          continue

        if incl == EXCLUDE:
          msg.ClearField(f.name)
          continue

        if not f.message_type:
          # The field is a scalar, but the field mask does not specify to
          # include it entirely. Skip it because scalars do not have subfields.
          msg.ClearField(f.name)
          continue

        # Trim the field value.
        if f.message_type.GetOptions().map_entry:
          for mk, mv in v.items():
            with with_comp(mk):
              incl = include()
              if incl == INCLUDE_RECURSIVELY:
                continue

              if incl == EXCLUDE:
                v.pop(mk)
                continue

              if isinstance(mv, protobuf.Message):
                trim_msg(mv)

        elif f.label == descriptor.FieldDescriptor.LABEL_REPEATED:
          with with_comp(STAR):
            for rv in v:
              trim_msg(rv)
        else:
          trim_msg(v)

  trim_msg(message)


STAR = object()

# Token types.
_STAR, _PERIOD, _LITERAL, _QUOTED_STRING = xrange(4)


def _tokenize(path):
  """Transforms path to an iterator of (token_type, string) tuples.

  Raises:
    ValueError if a quoted string is not closed.
  """
  if not isinstance(path, basestring):
    raise ValueError('path is not a basestring')

  i = 0
  while i < len(path):
    if path[i] == '`':
      # This is a quoted string.

      i += 1  # Swallow backtick.

      quoted_string = []  # Parsed quoted string as list of string parts.
      while True:
        next_backtick = path.find('`', i)
        if next_backtick == -1:
          raise ValueError('a quoted string is not closed')

        quoted_string.append(path[i:next_backtick])
        i = next_backtick + 1  # Swallow the discovered backtick.

        escaped_backtick = i < len(path) and path[i] == '`'
        if not escaped_backtick:
          break
        quoted_string.append('`')
        i += 1  # Swallow second backtick.

      yield (_QUOTED_STRING, ''.join(quoted_string))
    elif path[i] == '*':
      i += 1
      yield (_STAR, '*')
    elif path[i] == '.':
      i += 1
      yield (_PERIOD, '.')
    else:
      start = i
      while i < len(path):
        if path[i] in ('.', '*', '`'):
          break
        i += 1
      yield (_LITERAL, path[start:i])


_INTEGER_FIELD_TYPES = {
    descriptor.FieldDescriptor.TYPE_INT64,
    descriptor.FieldDescriptor.TYPE_INT32,
    descriptor.FieldDescriptor.TYPE_UINT32,
    descriptor.FieldDescriptor.TYPE_UINT64,
    descriptor.FieldDescriptor.TYPE_FIXED64,
    descriptor.FieldDescriptor.TYPE_FIXED32,
    descriptor.FieldDescriptor.TYPE_SFIXED64,
    descriptor.FieldDescriptor.TYPE_SFIXED32,
}


class _ParseContext(object):
  def __init__(self, desc):
    self.i = 0
    self.desc = desc
    self.repeated = False  # next segment is expected to be repeated
    self.map = False
    self._field_path = []  # full path of the urrent field

  def advance_to_field(self, field):
    self.desc = field.message_type
    self.map = field.message_type and field.message_type.GetOptions().map_entry
    self.repeated = field.label == descriptor.FieldDescriptor.LABEL_REPEATED
    self._field_path.append(field.name)

  @property
  def field_path(self):
    return '.'.join(self._field_path)


def parse_path(path, desc):
  """Parses a field path as a tuple of segments.

  Grammar:
    path = segment {'.' segment}
    segment = literal | '*' | quoted_string;
    literal = string | integer | bool
    string = (letter | '_') {letter | '_' | digit}
    integer = ['-'] digit {digit};
    bool = 'true' | 'false';
    quoted_string = '`' { utf8-no-backtick | '``' } '`'

  Args:
    path: a field path.
    desc: a google.protobuf.descriptor.Descriptor of the target message.

  Returns:
    A tuple of segments. A star is returned as STAR object.

  Raises:
    ValueError if path is invalid.
  """
  tokens = list(_tokenize(path))

  # Context
  ctx = _ParseContext(desc)
  eof = lambda: ctx.i >= len(tokens)

  def peek():
    if ctx.i == len(tokens):
      raise ValueError('unexpected end')
    return tokens[ctx.i]

  def read():
    tok = peek()
    ctx.i += 1
    return tok

  def read_path():
    segs = [parse_segment()]
    while not eof():
      tok_type, tok = read()
      if tok_type != _PERIOD:
        raise ValueError('unexpected token "%s"; expected a period' % tok)
      segs.append(parse_segment())
    return tuple(segs)

  def parse_segment():
    tok_type, tok = peek()
    assert tok
    if tok_type == _PERIOD:
      raise ValueError('a segment cannot start with a period')

    if ctx.map:
      key_type = ctx.desc.fields_by_name['key'].type
      if tok_type == _STAR:
        read()
        seg = STAR
      elif key_type == descriptor.FieldDescriptor.TYPE_BOOL:
        seg = read_bool()
      elif key_type in _INTEGER_FIELD_TYPES:
        seg = read_integer()
      elif key_type == descriptor.FieldDescriptor.TYPE_STRING:
        if tok_type == _QUOTED_STRING:
          read()
          seg = tok
        elif tok_type == _LITERAL:
          seg = read_string()
        else:
          raise ValueError('unexpected token "%s"; expected a string' % tok)
      else:
        raise ValueError(
            'unsupported key type of field "%s"' % ctx.field_path)

      ctx.advance_to_field(ctx.desc.fields_by_name['value'])
      return seg

    if ctx.repeated:
      if tok_type != _STAR:
        raise ValueError('a repeated field can be followed only by a star')
      read()
      ctx.repeated = False
      return STAR

    if ctx.desc is None:
      raise ValueError(
          '%s is not a message field, cannot have subfields' % ctx.field_path)

    field_name = read_string()
    field = ctx.desc.fields_by_name.get(field_name)
    if field is None:
      prefix = ctx.field_path
      full_name = '%s.%s' % (prefix, field_name) if prefix else field_name
      raise ValueError('field "%s" does not exist' % full_name)
    ctx.advance_to_field(field)
    return field_name

  def read_bool():
    tok_type, tok = read()
    if tok_type == _LITERAL and tok in ('true', 'false'):
      return tok == 'true'
    raise ValueError(
        'invalid segment "%s" for a map field %s with a boolean key' %
        (tok, ctx.field_path))

  def read_integer():
    tok_type, tok = read()
    if tok_type != _LITERAL:
      raise ValueError('unexpected token "%s"; expected an integer' % tok)
    try:
      return int(tok)
    except ValueError:
      raise ValueError(
          'invalid segment "%s" for a map field %s with an integer key' %
          (tok, ctx.field_path))

  def read_string():
    tok_type, tok = read()
    if tok_type != _LITERAL:
      raise ValueError(
          'unexpected token "%s"; expected an unquoted string literal' % tok)

    first, rem = tok[0], tok[1:]
    if first == '_' or first.isalpha():
      if not rem or all(c == '_' or c.isalnum() for c in rem):
        return tok
    raise ValueError('invalid unquoted string "%s"' % tok)

  return read_path()


def _remove_trailing_stars(paths):
  ret = set()
  for p in paths:
    assert isinstance(p, tuple), p
    if p[-1] == STAR:
      p = p[:-1]
    ret.add(p)
  return ret


def normalize_paths(paths):
  """Normalizes field paths. Retusn a new set of paths.

  paths must be parsed, see parse_path.

  Removes trailing stars, e.g. convertes 'a.*' to 'a'.

  Removes paths that have a segment prefix already present in paths,
  e.g. removes ('a', 'b') from [('a', 'b'), ('a',)].
  """
  paths = _remove_trailing_stars(paths)

  present = set(paths)
  ret = set()
  for p in paths:
    redundant = False
    for i in xrange(len(p)):
      if p[:i] in present:
        redundant = True
        break
    if not redundant:
      ret.add(p)

  return ret


def parse_field_tree(paths):
  """Parses a field path list to a tree of fields.

  paths must be parsed, see parse_path.

  Each node represents a field and in turn is represented by a dict where each
  dict key is a child key and dict value is a child node. For example, parses
  [('a',), ('b', 'c')] as {'a': {}, 'b': {'c': {}}}.

  Normalizes field_paths using normalize_paths, so omits trailing stars and
  removes redundant paths, e.g. parses [('a',), ('a', 'b')] as {'a': {}}.
  """
  assert isinstance(paths, (list, tuple)), type(paths)
  paths = normalize_paths(paths)

  root = {}
  for p in paths:
    cur = root
    for c in p:
      cur = cur.setdefault(c, {})
  return root


EXCLUDE = 0
INCLUDE_PARTIALLY = 1
INCLUDE_RECURSIVELY = 2


def must_include(field_tree, path):
  """Tells if a field value at the given path must be included in the response.

  Does not normalize field paths, see normalize_paths.

  Args:
    field_tree: a dict of fields, see parse_field_tree.
    path: a tuple of path segments.

  Returns:
    EXCLUDE if the field value must not be included.
    INCLUDE_PARTIALLY if the field value must be included. If it is message
      field, some of its subfields might be excluded.
    INCLUDE_RECURSIVELY if the field value must be included entirely.
  """
  assert isinstance(path, tuple), path
  assert path

  def q(n, i):
    if len(n) == 0:
      # n is a leaf.
      return INCLUDE_RECURSIVELY

    if i == len(path):
      # n is an intermediate node and we've exhausted path.
      # Some of the value's subfields are included, so include this value
      # partially.
      return INCLUDE_PARTIALLY

    # Find children that match current segment.
    comp = path[i]
    children = [n.get(comp)]
    if comp != STAR:
      children.append(n.get(STAR))
    children = [c for c in children if c is not None]
    if not children:
      # Nothing matched.
      return EXCLUDE
    return max(q(c, i + 1) for c in children)

  return q(field_tree, 0)
