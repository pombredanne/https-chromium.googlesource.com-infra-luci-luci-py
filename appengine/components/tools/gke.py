#!/usr/bin/env python
# Copyright 2014 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Wrapper around GKE (Google Container Engine) SDK tools to simplify working
with container deployments."""

__version__ = '1.0'

import collections
import json
import logging
import optparse
import os
import subprocess
import sys

# In case gke.py was run via symlink, find the original file since it's where
# third_party libs are. Handle a chain of symlinks too.
SCRIPT_PATH = os.path.abspath(__file__)
IS_SYMLINKED = False
while True:
  try:
    SCRIPT_PATH = os.path.abspath(
        os.path.join(os.path.dirname(SCRIPT_PATH), os.readlink(SCRIPT_PATH)))
    IS_SYMLINKED = True
  except OSError:
    break

ROOT_DIR = os.path.dirname(os.path.dirname(SCRIPT_PATH))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, '..', 'third_party_local'))

import colorama
from depot_tools import subcommand

def run_command(cmd):
  logging.info('Running command: %s', cmd)
  return subprocess.call(
      cmd,
      stdin=sys.stdin,
      stdout=sys.stdout,
      stderr=sys.stderr)

def check_output(cmd, cwd=None):
  logging.info('Running command (cwd=%r): %s', cwd, cmd)
  return subprocess.check_output(cmd, cwd=cwd)


class Configuration(object):
  """Cluster is the configuration for a single GKE application.
  """

  # Config is the configuration schema.
  Config = collections.namedtuple('Config', (
      'clusters',
  ))
  Cluster = collections.namedtuple('Cluster', (
      'key', 'name', 'zone'))

  def __init__(self, config):
    self.config = config
    self.clusters = {c.key: c for c in config.clusters}

  @classmethod
  def write_template(cls, path):
    # Generate a template config and write it.
    cfg = cls.Config(
      clusters=[
        cls.Cluster(
          key='cluster-key',
          name='cluster-name',
          zone='cluster-zone',
        )._asdict(),
      ],
    )
    with open(path, 'w') as fd:
      json.dump(cfg._asdict(), fd, indent=2, sort_keys=True)

  @classmethod
  def load(cls, path):
    if not os.path.isfile(path):
      cls.write_template(path)
      raise ValueError('Missing configuration path. A template was generated '
                       'at: %r' % (path,))

    with open(path, 'r') as fd:
      d = json.load(fd)

    # Load the JSON into our namedtuple schema.
    cfg = cls.Config(**d)
    cfg = cfg._replace(clusters=[cls.Cluster(**v) for v in cfg.clusters])

    return cls(cfg)


class Application(object):
  """Cluster is the configuration for a single GKE application.

  This includes the application's name, project, deployment parameters.

  An application consists of:
  - A path to its root Dockerfile.
  - Deployment cluster parameters (project, zone, etc.), loaded from JSON.
  """

  def __init__(self, project, dockerfile_path, config, cluster_key):
    self.project = project
    self.dockerfile_path = dockerfile_path
    self.cfg = config
    self.cluster = config.clusters[cluster_key]

  @property
  def name(self):
    return self.cluster.name
  @property
  def zone(self):
    return self.cluster.zone

  @property
  def kubectl_context(self):
    """Returns the name of the "kubectl" context for this Application.

    This name is a "gcloud" implementation detail, and may change in the future.
    Knowing the name, we can check for credential provisioning locally, reducing
    the common case overhead of individual "kubectl" invocations.
    """
    return 'gke_%s_%s_%s' % (self.project, self.zone, self.name)


class Kubectl(object):
  """Wrapper around the "kubectl" tool.
  """

  def __init__(self, app, needs_refresh):
    self.app = app
    self._needs_refresh = needs_refresh

  @property
  def executable(self):
    return 'kubectl'

  def run(self, *cmd):
    args = [
        self.executable,
        '--context', self.ensure_app_context(),
    ]
    args.extend(*cmd)
    return run_command(args)

  def check_output(self, *cmd, **kwargs):
    context = kwargs.pop('context', self.app.kubectl_context)
    args = [
        self.executable,
        '--context', context,
    ]
    args.extend(cmd)
    return check_output(args, **kwargs)

  def _has_app_context(self):
    # If this command returns non-zero and has non-empty output, we know that
    # the context is available.
    stdout = self.check_output(
        'config',
        'view',
        '--output', 'jsonpath=\'{.users[?(@.name == "%s")].name}\'' % (
            self.app.kubectl_context,),
        context='',
    )
    stdout = stdout.strip()
    return stdout and stdout != "''"

  def ensure_app_context(self):
    """Sets the current "kubectl" context to point to the current application.

    Kubectl can contain multiple context configurations. We want to explicitly
    specify the context each time we execute a command.

    Worst-case, we need to use "gcloud" to provision the context, which includes
    round-trips from remote services. Best-case, we're already provisioned with
    the context and can just use it.

    Returns (str): The name of the Kubernetes context, suitable for passing
      to the "--context" command-line parameter.
    """
    if self._needs_refresh or not self._has_app_context():
      check_output([
          'gcloud',
          '--project', self.app.project,
          'container',
          'clusters',
          'get-credentials',
          self.app.name,
          '--zone', self.app.zone,
      ])
      self._needs_refresh = False
      if not self._has_app_context():
        raise Exception('Kubernetes context missing after provisioning.')
    return self.app.kubectl_context


def CMDkubectl(parser, args):
  """Runs a Kubernetes command in the context of the configured Application.
  """
  parser.add_app_options()
  kctl, _, args = parser.parse_args(args)
  return kctl.run(args)


class OptionParser(optparse.OptionParser):
  """OptionParser with some canned options."""

  def __init__(self, app_dir, **kwargs):
    optparse.OptionParser.__init__(
        self,
        version=__version__,
        description=sys.modules['__main__'].__doc__,
        **kwargs)
    self.app_dir = app_dir

  def add_app_options(self):
    self.add_option(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase logging verbosity. Can be specified multiple times.')
    self.add_option(
        '-r', '--force-refresh',
        action='store_true',
        help='Forcefully refresh GKE authentication.')

    self.add_option(
        '-A', '--app-dir',
        help='Path to the GKE application directory, which contains its '
             'Dockerfile.')
    self.add_option(
        '-P', '--project',
        help='Name of the cloud project to work with.')
    self.add_option(
        '-C', '--config',
        help='Path to the cluster configuration JSON file.')
    self.add_option(
        '-K', '--cluster-key',
        help='Key of the cluster within the config to work with.')

  def parse_args(self, *args, **kwargs):
    options, args = optparse.OptionParser.parse_args(self, *args, **kwargs)

    if not options.project:
      raise ValueError('A project is required (--project).')
    if not options.config:
      raise ValueError('A config path is required (--config).')

    if options.verbose == 0:
      logging.getLogger().setLevel(logging.WARNING)
    elif options.verbose == 1:
      logging.getLogger().setLevel(logging.INFO)
    else:
      logging.getLogger().setLevel(logging.DEBUG)

    config = Configuration.load(options.config)
    if not options.cluster_key or options.cluster_key not in config.clusters:
      raise ValueError(
          'A cluster key is required (--cluster-key), one of: %s' % (
            ', '.join(sorted(config.clusters.keys())),)
      )

    app_dir = self.app_dir or options.app_dir
    if not app_dir:
      raise ValueError('No "app_dir" specified, and could not probe one.')

    dockerfile_path = os.path.join(app_dir, 'Dockerfile')
    if not os.path.isfile(dockerfile_path):
      raise ValueError('No Dockerfile in "app_dir": %r' % (app_dir,))

    app = Application(
        options.project,
        dockerfile_path,
        config,
        options.cluster_key)
    kctl = Kubectl(app, options.force_refresh)
    return kctl, options, args


def find_app_dir(search_dir):
  """Locates GKE app root directory (or returns None if not found).

  Starts by examining search_dir, then its parent, and so on, until it discovers
  git repository root or filesystem root.

  A directory is a suspect for an app root if it has a Dockerfile in it.

  A root directory is denoted either by presence of '.git' subdir, or 'ROOT'
  file.
  """
  def is_root(p):
    return (
        os.path.isdir(os.path.join(p, '.git')) or
        os.path.isfile(os.path.join(p, 'ROOT')) or
        os.path.dirname(p) == p)

  def is_app_dir(p):
    return os.path.isfile(os.path.join(p, 'Dockerfile'))

  while not is_root(search_dir):
    parent = os.path.dirname(search_dir)
    if is_app_dir(search_dir):
      return search_dir
    search_dir = parent
  return None


def main(args):
  # gke.py may be symlinked into app's directory or its subdirectory (to avoid
  # typing --app-dir all the time). If linked into subdirectory, discover root
  # by locating app.yaml. It is used for Python GAE apps and one-module Go apps
  # that have all YAMLs in app root dir.
  app_dir = None
  if IS_SYMLINKED:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = find_app_dir(script_dir)

  # If not symlinked into an app directory, try to discover app root starting
  # from cwd.
  app_dir = app_dir or find_app_dir(os.getcwd())

  colorama.init()
  dispatcher = subcommand.CommandDispatcher(__name__)
  try:
    return dispatcher.execute(OptionParser(app_dir), args)
  except KeyboardInterrupt:
    # Don't dump stack traces on Ctrl+C, it's expected flow in some commands.
    print >> sys.stderr, '\nInterrupted'
    return 1


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  sys.exit(main(sys.argv[1:]))
