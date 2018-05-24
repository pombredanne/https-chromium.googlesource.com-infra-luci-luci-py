# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Utility functions for google.protobuf.field_mask_pb2.FieldMask.

Supports advanced field mask semantics:
- Refer to fields and map keys using . literals:
  - Supported map key types: string, integer types, bool.
  - Floating point (including double and float), enum, and bytes keys are not
    supported by protobuf or this implementation.
  - Fields: 'publisher.name' means field name of field publisher
  - string map keys: 'metadata.year' means string key 'year' of map field
    metadata
  - integer map keys (e.g. int32): 'year_ratings.0' means integer key 0 of a map
    field year_ratings
  - bool map keys: 'access_text.true' means boolean key true of a map field
    access_text
- String map keys that cannot be represented as an unquoted string literal,
  must be quoted using backticks: metadata.`year.published`, metadata.`17`,
  metadata.``. Backtick can be escaped with ``: a.`b``c` means map key "b`c"
  of map field a.
- Refer to all map keys using a * literal: "topics.*.archived" means field
  "archived" of all map values of map field "topic".
- Refer to all elements of a repeated field using a * literal: authors.*.name
- Refer to all fields of a message using * literal: publisher.*.
- Prohibit addressing a single element in repeated fields: authors.0.name

FieldMask.paths string grammar:
  path = segment {'.' segment}
  segment = literal | '*' | quoted_string;
  literal = string | integer | bool
  string = (letter | '_') {letter | '_' | digit}
  integer = ['-'] digit {digit};
  bool = 'true' | 'false';
  quoted_string = '`' { utf8-no-backtick | '``' } '`'

TODO(nodir): replace spec above with a link to a spec when it is available.
"""

import contextlib

from google import protobuf
from google.protobuf import descriptor

__all__ = [
    'EXCLUDE',
    'INCLUDE_ENTIRELY',
    'INCLUDE_PARTIALLY',
    'STAR',
    'Tree',
]


# Used in a parsed path to represent a star segment.
# See parse_segment_tree.
STAR = object()

EXCLUDE = 0
INCLUDE_PARTIALLY = 1
INCLUDE_ENTIRELY = 2


class Tree(object):
  """A tree representation of a field mask. It serves as a tree node too.

  Each node represents a segment of a paths string, e.g. 'bar' in 'foo.bar.qux'.
  A Field mask with paths ['a', 'b.c'] is parsed as
    <root>
      a
      b
        c

  Attrs:
    descriptor: a descriptor of the message of the field this node represents.
      If the field is not a message type, it is None and it may not have
      children.
    repeated: True means that the segment represents a repeated field and not
      one of the field elements. Such tree can only have one child and it must
      have a STAR segment.
    children: a dict that maps a segment to its node, e.g. children of the root
      of the example above has keys 'a' and 'b', and values are Tree objects. A
      segment can be of type str, int, bool or it can be the value of
      field_masks.STAR for '*' segments.
  """

  def __init__(self, descriptor=None, repeated=False, children=None):
    """Initializes a new tree.

    The arguments initialize attributes of the same names, see Tree docstring.
    """
    self.descriptor = descriptor
    self.repeated = repeated
    self.children = children or {}

  def trim(self, message):
    """Clears msg fields that are not in the tree.

    If self is empty, this is a noop.
    The message must be a google.protobuf.message.Message.
    Uses self.include to decide what to trim.

    Fails if self.repeated is true.
    """
    assert not self.repeated
    # Path to the current field value.
    seg_stack = []

    @contextlib.contextmanager
    def with_seg(seg):
      """Returns a context manager that adds/removes a segment.

      The context manager adds/removes the segment to the stack of segments on
      enter/exit. Yields a boolean indicating whether the segment must be
      included. See include_field() docstring for possible values.
      See parse_segment_tree for possible values of seg.
      """
      seg_stack.append(seg)
      try:
        yield self.include(tuple(seg_stack))
      finally:
        seg_stack.pop()

    def trim_msg(msg):
      for f, v in msg.ListFields():
        with with_seg(f.name) as incl:
          if incl == INCLUDE_ENTIRELY:
            continue

          if incl == EXCLUDE:
            msg.ClearField(f.name)
            continue

          assert incl == INCLUDE_PARTIALLY

          if not f.message_type:
            # The field is scalar, but the field mask does not specify to
            # include it entirely. Skip it because scalars do not have
            # subfields. Note that parse_segment_tree would fail on such a mask
            # because a scalar field cannot be followed by other fields.
            msg.ClearField(f.name)
            continue

          # Trim the field value.
          if f.message_type.GetOptions().map_entry:
            for mk, mv in v.items():
              with with_seg(mk) as incl:
                if incl == INCLUDE_ENTIRELY:
                  pass
                elif incl == EXCLUDE:
                  v.pop(mk)
                elif isinstance(mv, protobuf.message.Message):
                  trim_msg(mv)
                else:
                  # The field is scalar, see the comment above.
                  v.pop(mk)
          elif f.label == descriptor.FieldDescriptor.LABEL_REPEATED:
            with with_seg(STAR):
              for rv in v:
                trim_msg(rv)
          else:
            trim_msg(v)

    trim_msg(message)

  def include(self, path):
    """Tells if a field value at the given path must be included.

    Args:
      path: a path string or a tuple of segments.

    Returns:
      EXCLUDE if the field value must be excluded.
      INCLUDE_PARTIALLY if some subfields of the field value must be included.
      INCLUDE_ENTIRELY if the field value must be included entirely.

    Raises:
      ValueError: path is a string and it is invalid according to
        self.descriptor and self.repeated.
    """
    assert path
    if not isinstance(path, tuple):
      path = _parse_path(path, self.descriptor, self.repeated)

    def include(node, i):
      """Tells if field path[i] must be included according to the node."""
      if not node.children:
        # node is a leaf.
        return INCLUDE_ENTIRELY

      if i == len(path):
        # n is an intermediate node and we've exhausted path.
        # Some of the value's subfields are included, so include this value
        # partially.
        return INCLUDE_PARTIALLY

      # Find children that match current segment.
      seg = path[i]
      children = [node.children.get(seg)]
      if seg != STAR:
        # node might have a star child
        # e.g. node = {'a': {'b': {}}, STAR: {'c': {}}}
        # If seg is 'x', we should check the star child.
        children.append(node.children.get(STAR))
      children = [c for c in children if c is not None]
      if not children:
        # Nothing matched.
        return EXCLUDE
      return max(include(c, i + 1) for c in children)

    return include(self, 0)

  @classmethod
  def from_field_mask(cls, field_mask, desc):
    """Parses a field mask to a Tree.

    Removes trailing stars, e.g. parses ['a.*'] to {'a': {}}.
    Removes redundant paths, e.g. parses ['a', 'a.b'] as {'a': {}}.

    Args:
      field_mask: a google.protobuf.field_mask_pb2.FieldMask instance.
      desc: a google.protobuf.descriptor.Descriptor for the target message.

    Raises:
      ValueError if a field path is invalid.
    """
    parsed_paths = []
    for p in field_mask.paths:
      try:
        parsed_paths.append(_parse_path(p, desc))
      except ValueError as ex:
        raise ValueError('invalid path "%s": %s' % (p, ex))

    parsed_paths = _normalize_paths(parsed_paths)

    root = cls(desc)
    for p in parsed_paths:
      node = root
      for seg in p:
        child = node.children.get(seg)
        if not child:
          if node.descriptor.GetOptions().map_entry:
            child = cls(node.descriptor.fields_by_name['value'].message_type)
          elif node.repeated:
            child = cls(node.descriptor)
          else:
            field = node.descriptor.fields_by_name[seg]
            repeated = field.label == descriptor.FieldDescriptor.LABEL_REPEATED
            child = cls(field.message_type, repeated=repeated)
          node.children[seg] = child
        node = child
    return root

  def __eq__(self, other):
    """Returns True if other is equivalent to self."""
    return (
        self.descriptor == other.descriptor and
        self.repeated == other.repeated and
        self.children == other.children)

  def __ne__(self, other):
    """Returns False if other is equivalent to self."""
    return not (self == other)

  def __repr__(self):
    """Returns a string representation of the Tree."""
    return 'Tree(%r, %r, %r)' % (self.descriptor, self.repeated, self.children)


def _normalize_paths(paths):
  """Normalizes field paths. Returns a new set of paths.

  paths must be parsed, see _parse_path.

  Removes trailing stars, e.g. convertes ('a', STAR) to ('a',).

  Removes paths that have a segment prefix already present in paths,
  e.g. removes ('a', 'b') from [('a', 'b'), ('a',)].
  """
  paths = _remove_trailing_stars(paths)
  return {
      p for p in paths
      if not any(p[:i] in paths for i in xrange(len(p)))
  }


def _remove_trailing_stars(paths):
  ret = set()
  for p in paths:
    assert isinstance(p, tuple), p
    if p[-1] == STAR:
      p = p[:-1]
    ret.add(p)
  return ret


# Token types.
_STAR, _PERIOD, _LITERAL, _STRING, _INTEGER, _UNKNOWN, _EOF = xrange(7)


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
_SUPPORTED_MAP_KEY_TYPES = _INTEGER_FIELD_TYPES | {
    descriptor.FieldDescriptor.TYPE_STRING,
    descriptor.FieldDescriptor.TYPE_BOOL,
}


def _parse_path(path, desc, repeated=False):
  """Parses a field path to a tuple of segments.

  See grammar in the module docstring.

  Args:
    path: a field path.
    desc: a google.protobuf.descriptor.Descriptor of the target message.
    repeated: True means that desc is a repeated field. For example,
      the target field is a repeated message field and path starts with an
      index. In such case, path must start with a star.

  Returns:
    A tuple of segments. A star is returned as STAR object.

  Raises:
    ValueError if path is invalid.
  """
  tokens = list(_tokenize(path))
  ctx = _ParseContext(desc, repeated)
  peek = lambda: tokens[ctx.i]

  def read():
    tok = peek()
    ctx.i += 1
    return tok

  def read_path():
    segs = []
    while True:
      seg, must_be_last = read_segment()
      segs.append(seg)

      tok_type, tok = read()
      if tok_type == _EOF:
        break
      if must_be_last:
        raise ValueError('unexpected token "%s"; expected end of string' % tok)
      if tok_type != _PERIOD:
        raise ValueError('unexpected token "%s"; expected a period' % tok)
    return tuple(segs)

  def read_segment():
    """Returns (segment, must_be_last) tuple."""
    tok_type, tok = peek()
    assert tok
    if tok_type == _PERIOD:
      raise ValueError('a segment cannot start with a period')
    if tok_type == _EOF:
      raise ValueError('unexpected end')

    is_map_key = ctx.desc and ctx.desc.GetOptions().map_entry
    if ctx.repeated and not is_map_key:
      if tok_type != _STAR:
        raise ValueError('unexpected token "%s", expected a star' % tok)
      read()  # Swallow star.
      ctx.repeated = False
      return STAR, False

    if ctx.desc is None:
      raise ValueError(
          'scalar field "%s" cannot have subfields' % ctx.field_path)

    if is_map_key:
      key_type = ctx.desc.fields_by_name['key'].type
      if key_type not in _SUPPORTED_MAP_KEY_TYPES:
        raise ValueError(
            'unsupported key type of field "%s"' % ctx.field_path)
      if tok_type == _STAR:
        read()  # Swallow star.
        seg = STAR
      elif key_type == descriptor.FieldDescriptor.TYPE_BOOL:
        seg = read_bool()
      elif key_type in _INTEGER_FIELD_TYPES:
        seg = read_integer()
      else:
        assert key_type == descriptor.FieldDescriptor.TYPE_STRING
        seg = read_string()

      ctx.advance_to_field(ctx.desc.fields_by_name['value'])
      return seg, False

    if tok_type == _STAR:
      # Include all fields.
      read()  # Swallow star.
       # A STAR field cannot be followed by subfields.
      return STAR, True

    if tok_type != _LITERAL:
      raise ValueError(
          'unexpected token "%s"; expected a field name' % tok)
    read()  # Swallow field name.
    field_name = tok

    field = ctx.desc.fields_by_name.get(field_name)
    if field is None:
      prefix = ctx.field_path
      full_name = '%s.%s' % (prefix, field_name) if prefix else field_name
      raise ValueError('field "%s" does not exist' % full_name)
    ctx.advance_to_field(field)
    return field_name, False

  def read_bool():
    tok_type, tok = read()
    if tok_type != _LITERAL or tok not in ('true', 'false'):
      raise ValueError(
          'unexpected token "%s", expected true or false' % tok)
    return tok == 'true'

  def read_integer():
    tok_type, tok = read()
    if tok_type != _INTEGER:
      raise ValueError('unexpected token "%s"; expected an integer' % tok)
    return int(tok)

  def read_string():
    tok_type, tok = read()
    if tok_type not in (_LITERAL, _STRING):
      raise ValueError('unexpected token "%s"; expected a string' % tok)
    return tok

  return read_path()


class _ParseContext(object):
  """Context of parsing in _parse_path."""

  def __init__(self, desc, repeated):
    self.i = 0
    self.desc = desc
    self.repeated = repeated
    self._field_path = []  # full path of the current field

  def advance_to_field(self, field):
    """Advances the context to the next message field.

    Args:
      field: a google.protobuf.descriptor.FieldDescriptor to move to.
    """
    self.desc = field.message_type
    self.repeated = field.label == descriptor.FieldDescriptor.LABEL_REPEATED
    self._field_path.append(field.name)

  @property
  def field_path(self):
    return '.'.join(self._field_path)


def _tokenize(path):
  """Transforms path to an iterator of (token_type, string) tuples.

  Raises:
    ValueError if a quoted string is not closed.
  """
  assert isinstance(path, basestring), path

  i = 0

  while i < len(path):
    start = i
    c = path[i]
    i += 1
    if c == '`':
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

      yield (_STRING, ''.join(quoted_string))
    elif c == '*':
      yield (_STAR, c)
    elif c == '.':
      yield (_PERIOD, c)
    elif c == '-' or c.isdigit():
      while i < len(path) and path[i].isdigit():
        i += 1
      yield (_INTEGER, path[start:i])
    elif c == '_' or c.isalpha():
      while i < len(path) and (path[i].isalnum() or path[i] == '_'):
        i += 1
      yield (_LITERAL, path[start:i])
    else:
      yield (_UNKNOWN, c)
  yield (_EOF, '<eof>')
