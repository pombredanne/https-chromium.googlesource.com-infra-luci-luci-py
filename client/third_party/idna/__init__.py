# Emulate the bare minimum for idna for the Swarming bot.
# In practice, we do not need it, and it's very large.
# See https://pypi.org/project/idna/

from encodings import idna

def encode(host, uts46=False):
  # Used by urllib3
  return idna.ToAscii(host)

def decode(host):
  # Used by cryptography/hazmat/backends/openssl/x509.py
  return idna.ToUnicode(host)
