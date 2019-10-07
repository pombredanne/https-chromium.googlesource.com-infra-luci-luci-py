use_relative_paths = True

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
    'https://github.com/nose-devs/nose2.git@' +
    '7b2e31e5e77ae78744bfa48caa7bad6a13ed870a',
}
