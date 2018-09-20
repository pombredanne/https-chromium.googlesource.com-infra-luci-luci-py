# Copyright 2015 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Windows specific utility functions."""

import ctypes
import logging
import os
import platform
import re
import string
import subprocess
import sys

from utils import tools

import gpu


## Private stuff.


_WIN32_CLIENT_NAMES = {
    u'5.0': u'2000',
    u'5.1': u'XP',
    u'5.2': u'XP',
    u'6.0': u'Vista',
    u'6.1': u'7',
    u'6.2': u'8',
    u'6.3': u'8.1',
    u'10.0': u'10',
}

_WIN32_SERVER_NAMES = {
    u'5.2': u'2003Server',
    u'6.0': u'2008Server',
    u'6.1': u'2008ServerR2',
    u'6.2': u'2012Server',
    u'6.3': u'2012ServerR2',
    u'10.0': u'2016Server',
}

# Defaults if missing.
_winreg = None
win32com = None


if sys.platform == 'cygwin':
  try:
    import cygwinreg as _winreg
  except ImportError:
    pass


if sys.platform == 'win32':
  # This file is imported on non-Windows so guard the Win32 setup code to only
  # run on Windows.
  from ctypes import wintypes
  import _winreg
  try:
    # win32com is included in pywin32, which is an optional package.
    import win32com
    import win32com.client
  except ImportError:
    pass

  ### Types.

  # The function prototype for EnumWindows.
  EnumWindowsProc = ctypes.WINFUNCTYPE(
      wintypes.BOOL, wintypes.HWND, ctypes.py_object)

  # https://msdn.microsoft.com/en-us/library/windows/desktop/aa379595.aspx
  class SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
      ('Sid', ctypes.c_void_p), # PSID
      ('Attributes', wintypes.DWORD),
    ]

  # https://msdn.microsoft.com/en-us/library/windows/desktop/bb394727.aspx
  class TOKEN_MANDATORY_LABEL(ctypes.Structure):
    _fields_ = [
      ('Label', SID_AND_ATTRIBUTES),
    ]

  # https://msdn.microsoft.com/en-us/library/windows/desktop/aa366770.aspx
  class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
      ('dwLength', wintypes.DWORD),
      ('dwMemoryLoad', wintypes.DWORD),
      ('dwTotalPhys', wintypes.DWORDLONG),
      ('dwAvailPhys', wintypes.DWORDLONG),
      ('dwTotalPageFile', wintypes.DWORDLONG),
      ('dwAvailPageFile', wintypes.DWORDLONG),
      ('dwTotalVirtual', wintypes.DWORDLONG),
      ('dwAvailVirtual', wintypes.DWORDLONG),
      ('dwAvailExtendedVirtual', wintypes.DWORDLONG),
    ]

  # Setup the Win32 functions needed below.
  advapi32 = ctypes.windll.advapi32
  # https://msdn.microsoft.com/en-us/library/windows/desktop/aa446657.aspx
  advapi32.GetSidSubAuthority.argtypes = (ctypes.c_void_p, wintypes.DWORD)
  advapi32.GetSidSubAuthority.restype = ctypes.POINTER(wintypes.DWORD)
  # https://msdn.microsoft.com/en-us/library/windows/desktop/aa446658.aspx
  advapi32.GetSidSubAuthorityCount.argtypes = (ctypes.c_void_p,) # PSID
  advapi32.GetSidSubAuthorityCount.restype = ctypes.POINTER(ctypes.c_ubyte)
  # https://msdn.microsoft.com/en-us/library/windows/desktop/aa446671.aspx
  advapi32.GetTokenInformation.argtypes = (
      wintypes.HANDLE, ctypes.c_long, # TOKEN_INFORMATION_CLASS
      ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD))
  advapi32.GetTokenInformation.restype = BOOL
  # https://msdn.microsoft.com/en-us/library/windows/desktop/aa379295.aspx
  advapi32.OpenProcessToken.argtypes = (
      wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE))
  advapi32.OpenProcessToken.restype = wintypes.BOOL

  # Setup the Win32 functions needed below.
  kernel32 = ctypes.windll.kernel32
  # https://msdn.microsoft.com/en-us/library/windows/desktop/ms724211.aspx
  kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
  kernel32.CloseHandle.restype = wintypes.BOOL
  # https://msdn.microsoft.com/en-us/library/windows/desktop/ms683179.aspx
  kernel32.GetCurrentProcess.argtypes = ()
  kernel32.GetCurrentProcess.restype = wintypes.HANDLE
  # https://msdn.microsoft.com/en-us/library/windows/desktop/aa364937.aspx
  kernel32.GetDiskFreeSpaceExW.argtypes = (
      wintypes.LPCWSTR, ctypes.POINTER(wintypes.ULARGE_INTEGER),
      ctypes.POINTER(wintypes.ULARGE_INTEGER),
      ctypes.POINTER(wintypes.ULARGE_INTEGER))
  kernel32.GetDiskFreeSpaceExW.restype = wintypes.BOOL
  # https://msdn.microsoft.com/en-us/library/windows/desktop/aa364939.aspx
  kernel32.GetDriveTypeW.argtypes = (wintypes.LPCWSTR,)
  kernel32.GetDriveTypeW.restype = wintypes.UINT
  # https://msdn.microsoft.com/en-us/library/windows/desktop/aa366589.aspx
  kernel32.GlobalMemoryStatusEx.argtypes = (ctypes.POINTER(MemoryStatusEx),)
  kernel32.GlobalMemoryStatusEx.retype = wintypes.BOOL
  # https://msdn.microsoft.com/en-us/library/windows/desktop/ee662307.aspx
  kernel32.QueryUnbiasedInterruptTime.argtypes = (
      ctypes.POINTER(wintypes.ULONGLONG),)
  kernel32.QueryUnbiasedInterruptTime.restype = wintypes.BOOL

  # Setup the Win32 functions needed below.
  user32 = ctypes.windll.user32
  # https://msdn.microsoft.com/en-us/library/windows/desktop/ms633497.aspx
  user32.EnumWindows.argtypes = (EnumWindowsProc, ctypes.py_object)
  user32.EnumWindows.restype = wintypes.BOOL
  # https://msdn.microsoft.com/en-us/library/windows/desktop/ms633582.aspx
  user32.GetClassNameW.argtypes = (wintypes.HWND wintypes.LPWSTR, ctypes.c_int)
  user32.GetClassNameW.restype = ctypes.c_int
  # https://msdn.microsoft.com/en-us/library/windows/desktop/ms633584.aspx
  user32.GetWindowLongW.argtypes = (wintypes.HWND, ctypes.c_int)
  user32.GetWindowLongW.restype = wintypes.LONG
  # https://msdn.microsoft.com/en-us/library/windows/desktop/ms633527.aspx
  user32.IsIconic.argtypes = (wintypes.HWND,)
  user32.IsIconic.restype = wintypes.BOOL
  # https://msdn.microsoft.com/en-us/library/windows/desktop/ms633530.aspx
  user32.IsWindowVisible.argtypes = (wintypes.HWND,)
  user32.IsWindowVisible.restype = wintypes.BOOL


@tools.cached
def _get_mount_points():
  """Returns the list of 'fixed' drives in format 'X:\\'."""
  DRIVE_FIXED = 3
  # https://msdn.microsoft.com/library/windows/desktop/aa364939.aspx
  return [
    u'%s:\\' % letter
    for letter in string.lowercase
    if kernel32.GetDriveTypeW(letter + ':\\') == DRIVE_FIXED
  ]


def _get_disk_info(mount_point):
  """Returns total and free space on a mount point in Mb."""
  total_bytes = wintypes.ULARGE_INTEGER(0)
  free_bytes = wintypes.ULARGE_INTEGER(0)
  kernel32.GetDiskFreeSpaceExW(
      mount_point, None, ctypes.byref(total_bytes), ctypes.byref(free_bytes))
  return {
    u'free_mb': round(free_bytes.value / 1024. / 1024., 1),
    u'size_mb': round(total_bytes.value / 1024. / 1024., 1),
  }


@tools.cached
def _get_win32com():
  """Returns an uninitialized WMI client."""
  try:
    from win32com import client  # pylint: disable=F0401
    return client
  except ImportError:
    # win32com is included in pywin32, which is an optional package that is
    # installed by Swarming devs. If you find yourself needing it to run without
    # pywin32, for example in cygwin, please send us a CL with the
    # implementation that doesn't use pywin32.
    return None


@tools.cached
def _get_wmi_wbem():
  """Returns a WMI client connected to localhost ready to do queries."""
  client = _get_win32com()
  if not client:
    return None
  wmi_service = client.Dispatch('WbemScripting.SWbemLocator')
  return wmi_service.ConnectServer('.', 'root\\cimv2')


# Regexp for _get_os_numbers()
_CMD_RE = r'\[version (\d+\.\d+)\.(\d+(?:\.\d+|))\]'


@tools.cached
def _get_os_numbers():
  """Returns the normalized OS version and build numbers as strings.

  Actively work around AppCompat version lie shim.

  Returns:
    - 5.1, 6.1, etc. There is no way to distinguish between Windows 7
      and Windows Server 2008R2 since they both report 6.1.
    - build number, like '10240'. Mostly relevant on Windows 10.
  """
  # Windows is lying to us until python adds to its manifest:
  #   <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
  # and it doesn't.
  # So ask nicely to cmd.exe instead, which will always happily report the right
  # version. Here's some sample output:
  # - XP: Microsoft Windows XP [Version 5.1.2600]
  # - Win10: Microsoft Windows [Version 10.0.10240]
  # - Win7 or Win2K8R2: Microsoft Windows [Version 6.1.7601]
  # - Win1709: Microsoft Windows [Version 10.0.16299.19]
  #
  # Some locale (like fr_CA) use a lower case 'version'.
  out = subprocess.check_output(['cmd.exe', '/c', 'ver']).strip()
  match = re.search(_CMD_RE, out, re.IGNORECASE)
  if not match:
    # Failed to start cmd.exe, that's really bad. Return a dummy value to not
    # crash.
    logging.error('Failed to run cmd.exe /c ver:\n%s', out)
    return '0.0', '0'
  return match.group(1), match.group(2)


def _is_topmost_window(hwnd):
  """Returns True if |hwnd| is a topmost window."""
  # -20 is GWL_EXSTYLE
  ex_styles = user32.GetWindowLongW(hwnd, -20)
  # 8 is WS_EX_TOPMOST
  return bool(ex_styles & 8)


def _get_window_class(hwnd):
  """Returns the class name of |hwnd|."""
  name = ctypes.create_unicode_buffer(257)
  name_len = user32.GetClassNameW(hwnd, name, len(name))
  if name_len <= 0 or name_len >= len(name):
    raise ctypes.WinError(descr='GetClassNameW failed; %s' %
                          ctypes.FormatError())
  return name.value


## Public API.


def from_cygwin_path(path):
  """Converts an absolute cygwin path to a standard Windows path."""
  if not path.startswith('/cygdrive/'):
    logging.error('%s is not a cygwin path', path)
    return None

  # Remove the cygwin path identifier.
  path = path[len('/cygdrive/'):]

  # Add : after the drive letter.
  path = path[:1] + ':' + path[1:]
  return path.replace('/', '\\')


def to_cygwin_path(path):
  """Converts an absolute standard Windows path to a cygwin path."""
  if len(path) < 2 or path[1] != ':':
    # TODO(maruel): Accept \\?\ and \??\ if necessary.
    logging.error('%s is not a win32 path', path)
    return None
  return '/cygdrive/%s/%s' % (path[0].lower(), path[3:].replace('\\', '/'))


@tools.cached
def get_os_version_number():
  """Returns the normalized OS version number as a string.

  Returns:
    - '5.1', '6.1', '10.0', etc. There is no way to distinguish between Windows
      7 and Windows Server 2008R2 since they both report 6.1.
  """
  return _get_os_numbers()[0]


@tools.cached
def get_os_version_names():
  """Returns the marketing name of the OS, without and with the service pack.

  On Windows 10, use the build number since there will be no service pack.
  """
  # Python keeps a local map in platform.py and it is updated at newer python
  # release. Since our python release is a bit old, do not rely on it.
  is_server = sys.getwindowsversion().product_type == 3
  lookup = _WIN32_SERVER_NAMES if is_server else _WIN32_CLIENT_NAMES
  version_number, build_number = _get_os_numbers()
  marketing_name = lookup.get(version_number, version_number)
  if version_number == u'10.0':
    # Windows 10 doesn't have service packs, the build number now is the
    # reference number.
    return marketing_name, u'%s-%s' % (marketing_name, build_number)
  service_pack = platform.win32_ver()[2] or u'SP0'
  return marketing_name, u'%s-%s' % (marketing_name, service_pack)


def get_startup_dir():
  # Do not use environment variables since it wouldn't work reliably on cygwin.
  # TODO(maruel): Stop hardcoding the values and use the proper function
  # described below. Postponed to a later CL since I'll have to spend quality
  # time on Windows to ensure it works well.
  # https://msdn.microsoft.com/library/windows/desktop/bb762494.aspx
  # CSIDL_STARTUP = 7
  # https://msdn.microsoft.com/library/windows/desktop/bb762180.aspx
  # shell.SHGetFolderLocation(NULL, CSIDL_STARTUP, NULL, NULL, string)
  if get_os_version_number() == u'5.1':
    startup = 'Start Menu\\Programs\\Startup'
  else:
    # Vista+
    startup = (
        'AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup')

  # On cygwin 1.5, which is still used on some bots, '~' points inside
  # c:\\cygwin\\home so use USERPROFILE.
  return '%s\\%s\\' % (
    os.environ.get('USERPROFILE', 'DUMMY, ONLY USED IN TESTS'), startup)


def get_disks_info():
  """Returns disk infos on all mount point in Mb."""
  if sys.platform != 'win32':
    return {}
  return {p: _get_disk_info(p) for p in _get_mount_points()}


@tools.cached
def get_audio():
  """Returns audio device as listed by WMI."""
  wbem = _get_wmi_wbem()
  if not wbem:
    return None
  # https://msdn.microsoft.com/library/aa394463.aspx
  return [
    device.Name
    for device in wbem.ExecQuery('SELECT * FROM Win32_SoundDevice')
    if device.Status == 'OK'
  ]


@tools.cached
def get_cpuinfo():
  """Returns CPU information."""
  if not _winreg:
    return {}
  # Ironically, the data returned by WMI is mostly worthless.
  # Another option is IsProcessorFeaturePresent().
  # https://msdn.microsoft.com/en-us/library/windows/desktop/ms724482.aspx
  k = _winreg.OpenKey(
      _winreg.HKEY_LOCAL_MACHINE,
      'HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0')
  try:
    identifier, _ = _winreg.QueryValueEx(k, 'Identifier')
    match = re.match(
        ur'^.+ Family (\d+) Model (\d+) Stepping (\d+)$', identifier)
    name, _ = _winreg.QueryValueEx(k, 'ProcessorNameString')
    vendor, _ = _winreg.QueryValueEx(k, 'VendorIdentifier')
    return {
      u'model': [
        int(match.group(1)), int(match.group(2)), int(match.group(3))
      ],
      u'name': name,
      u'vendor': vendor,
    }
  finally:
    k.Close()


def get_gpu():
  """Returns video device as listed by WMI.

  Not cached as the GPU driver may change underneat.
  """
  wbem = _get_wmi_wbem()
  if not wbem:
    return None, None

  client = _get_win32com()
  dimensions = set()
  state = set()
  # https://msdn.microsoft.com/library/aa394512.aspx
  try:
    for device in wbem.ExecQuery('SELECT * FROM Win32_VideoController'):
      # The string looks like:
      #  PCI\VEN_15AD&DEV_0405&SUBSYS_040515AD&REV_00\3&2B8E0B4B&0&78
      pnp_string = device.PNPDeviceID
      ven_id = u'UNKNOWN'
      dev_id = u'UNKNOWN'
      match = re.search(r'VEN_([0-9A-F]{4})', pnp_string)
      if match:
        ven_id = match.group(1).lower()
      match = re.search(r'DEV_([0-9A-F]{4})', pnp_string)
      if match:
        dev_id = match.group(1).lower()

      dev_name = device.VideoProcessor or u''
      version = device.DriverVersion or u''
      ven_name, dev_name = gpu.ids_to_names(ven_id, u'', dev_id, dev_name)

      dimensions.add(unicode(ven_id))
      dimensions.add(u'%s:%s' % (ven_id, dev_id))
      if version:
        dimensions.add(u'%s:%s-%s' % (ven_id, dev_id, version))
        state.add(u'%s %s %s' % (ven_name, dev_name, version))
      else:
        state.add(u'%s %s' % (ven_name, dev_name))
  except client.com_error as e:
    # This generally happens when this is called as the host is shutting down.
    logging.error('get_gpu(): %s', e)
  return sorted(dimensions), sorted(state)


@tools.cached
def get_integrity_level():
  """Returns the integrity level of the current process as a string."""
  if get_os_version_number() == u'5.1' or sys.platform != 'win32':
    # Integrity level is Vista+; can't access Win32 on cygwin.
    return None

  mapping = {
    0x0000: u'untrusted',
    0x1000: u'low',
    0x2000: u'medium',
    0x2100: u'medium high',
    0x3000: u'high',
    0x4000: u'system',
    0x5000: u'protected process',
  }

  TOKEN_READ = DWORD(0x20008)
  # Use the same casing as in the C declaration:
  # https://msdn.microsoft.com/library/windows/desktop/aa379626.aspx
  TokenIntegrityLevel = ctypes.c_int(25)
  ERROR_INSUFFICIENT_BUFFER = 122

  # First open the process' token, then query the SID to know its integrity
  # level.

  # First open the current process token, query it, then close everything.
  token = ctypes.c_void_p()
  proc_handle = kernel32.GetCurrentProcess()
  if not advapi32.OpenProcessToken(
      proc_handle, TOKEN_READ, ctypes.byref(token)):
    logging.error('Failed to get process\' token')
    return None
  if token.value == 0:
    logging.error('Got a NULL token')
    return None
  try:
    # The size of the structure is dynamic because the TOKEN_MANDATORY_LABEL
    # used will have the SID appened right after the TOKEN_MANDATORY_LABEL in
    # the heap allocated memory block, with .Label.Sid pointing to it.
    info_size = DWORD()
    if advapi32.GetTokenInformation(
        token, TokenIntegrityLevel, ctypes.c_void_p(), info_size,
        ctypes.byref(info_size)):
      logging.error('GetTokenInformation() failed expectation')
      return None
    if info_size.value == 0:
      logging.error('GetTokenInformation() returned size 0')
      return None
    err = ctypes.GetLastError()
    if err != ERROR_INSUFFICIENT_BUFFER:
      logging.error('GetTokenInformation(): Unknown error: %d', err)
      return None
    token_info = TOKEN_MANDATORY_LABEL()
    ctypes.resize(token_info, info_size.value)
    if not advapi32.GetTokenInformation(
        token, TokenIntegrityLevel, ctypes.byref(token_info), info_size,
        ctypes.byref(info_size)):
      logging.error(
          'GetTokenInformation(): Unknown error with buffer size %d: %d',
          info_size.value, ctypes.GetLastError())
      return None
    p_sid_size = advapi32.GetSidSubAuthorityCount(token_info.Label.Sid)
    res = advapi32.GetSidSubAuthority(
        token_info.Label.Sid, p_sid_size.contents.value - 1)
    value = res.contents.value
    return mapping.get(value) or u'0x%04x' % value
  finally:
    kernel32.CloseHandle(token)


@tools.cached
def get_physical_ram():
  """Returns the amount of installed RAM in Mb, rounded to the nearest number.
  """
  if sys.platform != 'win32':
    return None
  stat = MemoryStatusEx()
  stat.dwLength = ctypes.sizeof(MemoryStatusEx)  # pylint: disable=W0201
  kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
  return int(round(stat.dwTotalPhys / 1024. / 1024.))


def get_uptime():
  """Return uptime for Windows 7 and later.

  Excludes sleep time.
  """
  if sys.platform != 'win32':
    return 0
  val = wintypes.ULONGLONG(0)
  if kernel32.QueryUnbiasedInterruptTime(ctypes.byref(val)) != 0:
    return val.value / 10000000.
  return 0.


def list_top_windows():
  """Returns a list of the class names of topmost windows.

  Windows owned by the shell are ignored.
  """
  if sys.platform != 'win32':
    return []
  IGNORED = ('Button', 'Shell_TrayWnd', 'Shell_SecondaryTrayWnd')

  out = []

  def on_window(hwnd, lparam):  # pylint: disable=unused-argument
    """Evaluates |hwnd| to determine whether or not it is a topmost window.

    In case |hwnd| is a topmost window, its class name is added to the
    collection of topmost window class names to return.
    """
    # Dig deeper into visible, non-iconified, topmost windows.
    if (user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd) and
        _is_topmost_window(hwnd)):
      # Fetch the class name and make sure it's not owned by the Windows shell.
      class_name = _get_window_class(hwnd)
      if class_name and class_name not in IGNORED:
        out.append(class_name)
    return 1

  user32.EnumWindows(window_enum_proc_prototype(on_window), None)
  return sorted(out)
