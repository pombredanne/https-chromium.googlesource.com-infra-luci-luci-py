use_relative_paths = True

vars = {
  "external_github": "https://chromium.googlesource.com/external/github.com",
}

deps = {
  'appengine/swarming/ui2/nodejs/': {
    'packages': [
      {
        'package': 'infra/nodejs/nodejs/${{platform}}',
        'version': 'node_version:10.15.3',
      }
    ],
    'dep_type': 'cipd',
    'condition': 'checkout_linux or checkout_mac',
  },
  'appengine/third_party/nose2':
    '{external_github}/nose-devs/nose2.git@' +
    'aaf48fb854b3aa5dde974271fe6e7ca398a0996a',
}
