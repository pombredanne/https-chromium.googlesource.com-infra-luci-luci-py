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

from api.platforms import common
from api.platforms import gpu


## Private stuff.


_WIN32_CLIENT_NAMES = {
    '5.0': '2000',
    '5.1': 'XP',
    '5.2': 'XP',
    '6.0': 'Vista',
    '6.1': '7',
    '6.2': '8',
    '6.3': '8.1',
    '10.0': '10',
    '11.0': '11',
}

_WIN32_SERVER_NAMES = {
    '5.2': '2003Server',
    '6.0': '2008Server',
    '6.1': '2008ServerR2',
    '6.2': '2012Server',
    '6.3': '2012ServerR2',
    '10.0': 'Server',
}


@tools.cached
def _get_mount_points():
  """Returns the list of 'fixed' drives in format 'X:\\'."""
  ctypes.windll.kernel32.GetDriveTypeW.argtypes = (ctypes.c_wchar_p,)
  ctypes.windll.kernel32.GetDriveTypeW.restype = ctypes.c_ulong
  DRIVE_FIXED = 3
  # https://msdn.microsoft.com/library/windows/desktop/aa364939.aspx
  return [
      '%s:\\' % letter for letter in string.ascii_lowercase
      if ctypes.windll.kernel32.GetDriveTypeW(letter + ':\\') == DRIVE_FIXED
  ]


def _get_disk_info(mount_point):
  """Returns total and free space on a mount point in Mb."""
  total_bytes = ctypes.c_ulonglong(0)
  free_bytes = ctypes.c_ulonglong(0)
  ctypes.windll.kernel32.GetDiskFreeSpaceExW(
      ctypes.c_wchar_p(mount_point), None, ctypes.pointer(total_bytes),
      ctypes.pointer(free_bytes))
  return {
      'free_mb': round(free_bytes.value / 1024. / 1024., 1),
      'size_mb': round(total_bytes.value / 1024. / 1024., 1),
  }


@tools.cached
def _get_win32com():
  """Returns an uninitialized WMI client."""
  try:
    import pythoncom
    from win32com import client  # pylint: disable=F0401
    return client, pythoncom
  except ImportError:
    # win32com is included in pywin32, which is an optional package that is
    # installed by Swarming devs. If you find yourself needing it to run without
    # pywin32, for example in cygwin, please send us a CL with the
    # implementation that doesn't use pywin32.
    return None, None


@tools.cached
def _get_wmi_wbem():
  """Returns a WMI client connected to localhost ready to do queries."""
  client, _ = _get_win32com()
  if not client:
    return None
  wmi_service = client.Dispatch('WbemScripting.SWbemLocator')
  return wmi_service.ConnectServer('.', 'root\\cimv2')


@tools.cached
def _get_wmi_wbem_for_storage():
  """
  Returns a WMI client connected to localhost ready to do queries for storage.
  """
  client, pythoncom = _get_win32com()
  if not client:
    return None
  wmi_service = client.Dispatch('WbemScripting.SWbemLocator')
  try:
    return wmi_service.ConnectServer('.', 'Root\\Microsoft\\Windows\\Storage')
  except pythoncom.com_error:
    return None


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
  out = subprocess.check_output(['cmd.exe', '/c', 'ver']).strip().decode()
  match = re.search(_CMD_RE, out, re.IGNORECASE)
  if not match:
    # Failed to start cmd.exe, that's really bad. Return a dummy value to not
    # crash.
    logging.error('Failed to run cmd.exe /c ver:\n%s', out)
    return '0.0', '0'

  os_version = match.group(1)
  build_number = match.group(2)
  major_build_number = build_number.split('.')[0]
  if os_version == '10.0' and int(major_build_number) >= 22000:
    os_version = '11.0'

  return os_version, build_number


def _is_topmost_window(hwnd):
  """Returns True if |hwnd| is a topmost window."""
  ctypes.windll.user32.GetWindowLongW.restype = ctypes.c_long  # LONG
  ctypes.windll.user32.GetWindowLongW.argtypes = [
      ctypes.c_void_p,  # HWND
      ctypes.c_int
  ]
  # -20 is GWL_EXSTYLE
  ex_styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
  # 8 is WS_EX_TOPMOST
  return bool(ex_styles & 8)


def _get_window_class(hwnd):
  """Returns the class name of |hwnd|."""
  ctypes.windll.user32.GetClassNameW.restype = ctypes.c_int
  ctypes.windll.user32.GetClassNameW.argtypes = [
      ctypes.c_void_p,  # HWND
      ctypes.c_wchar_p,
      ctypes.c_int
  ]
  name = ctypes.create_unicode_buffer(257)
  name_len = ctypes.windll.user32.GetClassNameW(hwnd, name, len(name))
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
    - '5.1', '6.1', '10.0', etc. There is no way to distinguish between some
      versions of Windows because they share the same major version number.
      Examples of this are Windows 7 and Server 2008 with 6.1, and Windows 10
      and Windows 11 with 10.0.
  """

  return _get_os_numbers()[0]


@tools.cached
def get_client_versions():
  """Gets the client versions (or client equivalent for server).

  Returns:
    A list of client versions (or client equivalent for server).
    E.g. '10' for Windows 10 and Windows Server 2016.
  """
  version_nubmer = get_os_version_number()
  if version_nubmer in _WIN32_CLIENT_NAMES:
    return [_WIN32_CLIENT_NAMES[version_nubmer]]
  return []


@tools.cached
def get_os_version_names():
  """Returns the marketing/user-friendly names of the OS.

  The return value contains the base marketing name, e.g. Vista, 10, or
  2008Server. For Windows Server starting with 2016, this value is always
  "Server".

  For versions released before Windows 10, the return value also contains the
  name with the service pack, e.g. 7-SP1 or 2012ServerR2-SP0.

  For Windows 10 and Windows Server starting with 2016, the return value
  includes "10-" or "Server-" followed by one or more parts of the build number.
  E.g. for Windows 10 with build number 18362.207, the return value includes
  10-18362, 10-18362.207. For Windows Server 2019 with build number 17763.557,
  the return value includes Server-17763, Server-17763.557.
  """
  # Python keeps a local map in platform.py and it is updated at newer python
  # release. Since our python release is a bit old, do not rely on it.
  is_server = sys.getwindowsversion().product_type != 1
  lookup = _WIN32_SERVER_NAMES if is_server else _WIN32_CLIENT_NAMES
  version_number, build_number = _get_os_numbers()
  marketing_name = lookup.get(version_number, version_number)
  if version_number in ('10.0', '11.0'):
    rv = [marketing_name]
    # Windows 10 doesn't have service packs, the build number now is the
    # reference number. More discussion in
    # https://docs.google.com/document/d/1iF1tbc1oedCQ9J6aL7sHeuaayY3bs52fuvKxvLLZ0ig
    if '.' in build_number:
      major_version = build_number.split('.')[0]
      rv.append('%s-%s' % (marketing_name, major_version))
    rv.append('%s-%s' % (marketing_name, build_number))
    rv.sort()
    return rv
  service_pack = platform.win32_ver()[2] or 'SP0'
  return [marketing_name, '%s-%s' % (marketing_name, service_pack)]


def get_startup_dir():
  # Do not use environment variables since it wouldn't work reliably on cygwin.
  # TODO(maruel): Stop hardcoding the values and use the proper function
  # described below. Postponed to a later CL since I'll have to spend quality
  # time on Windows to ensure it works well.
  # https://msdn.microsoft.com/library/windows/desktop/bb762494.aspx
  # CSIDL_STARTUP = 7
  # https://msdn.microsoft.com/library/windows/desktop/bb762180.aspx
  # shell.SHGetFolderLocation(NULL, CSIDL_STARTUP, NULL, NULL, string)
  if get_os_version_number() == '5.1':
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
def get_visual_studio_versions():
  """Retrieves all installed Visual Studio versions.

  The returned version list is sorted such that the first element is the highest
  version number.

  Returns:
    A list of Visual Studio version strings.
  """
  import winreg

  try:
    k = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        'SOFTWARE\\Wow6432Node\\Microsoft\\VSCommon')
  # pylint: disable=undefined-variable
  except WindowsError:
    return None

  try:
    versions = []
    for i in range(winreg.QueryInfoKey(k)[0]):
      sub_key = winreg.EnumKey(k, i)
      if re.match(r'\d+\.\d+', sub_key):
        versions.append(sub_key)
    return sorted(versions, key=float, reverse=True)
  finally:
    k.Close()


@tools.cached
def get_cpuinfo():
  # Ironically, the data returned by WMI is mostly worthless.
  # Another option is IsProcessorFeaturePresent().
  # https://msdn.microsoft.com/en-us/library/windows/desktop/ms724482.aspx
  import winreg
  k = winreg.OpenKey(
      winreg.HKEY_LOCAL_MACHINE,
      'HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0')
  try:
    identifier, _ = winreg.QueryValueEx(k, 'Identifier')
    match = re.match(r'^.+ Family (\d+) Model (\d+) Stepping (\d+)$',
                     identifier)
    name, _ = winreg.QueryValueEx(k, 'ProcessorNameString')
    vendor, _ = winreg.QueryValueEx(k, 'VendorIdentifier')
    return {
        'model':
        [int(match.group(1)),
         int(match.group(2)),
         int(match.group(3))],
        'name': name,
        'vendor': vendor,
    }
  finally:
    k.Close()


def get_cpu_type_with_wmi():
  # Get CPU architecture type using WMI.
  # This is a fallback for when platform.machine() returns None.
  # References:
  # https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-processor#properties
  # https://source.winehq.org/source/include/winnt.h#L680
  # https://github.com/puppetlabs/facter/blob/2.x/lib/facter/hardwaremodel.rb#L28
  wbem = _get_wmi_wbem()
  if not wbem:
    return None
  _, pythoncom = _get_win32com()
  try:
    q = 'SELECT Architecture, Level, AddressWidth FROM Win32_Processor'
    for cpu in wbem.ExecQuery(q):

      def intel_arch():
        arch_level = min(cpu.Level, 6)
        return 'i%d86' % arch_level  # e.g. i386, i686

      if cpu.Architecture == 10:  # PROCESSOR_ARCHITECTURE_IA32_ON_WIN64
        return 'i686'
      if cpu.Architecture == 9:  # PROCESSOR_ARCHITECTURE_AMD64
        if cpu.AddressWidth == 32:
          return intel_arch()
        return 'amd64'
      if cpu.Architecture == 0:  # PROCESSOR_ARCHITECTURE_INTEL
        return intel_arch()
  except pythoncom.com_error as e:
    # This generally happens when this is called as the host is shutting down.
    logging.error('get_cpu_type_with_wmi(): %s', e)
  # Unknown or exception.
  return None


def get_gpu():
  """Returns video device as listed by WMI.

  Not cached as the GPU driver may change underneat.
  """
  wbem = _get_wmi_wbem()
  if not wbem:
    return None, None

  _, pythoncom = _get_win32com()
  dimensions = set()
  state = set()
  # https://msdn.microsoft.com/library/aa394512.aspx
  try:
    for device in wbem.ExecQuery('SELECT * FROM Win32_VideoController'):
      # The string looks like:
      #  PCI\VEN_15AD&DEV_0405&SUBSYS_040515AD&REV_00\3&2B8E0B4B&0&78
      pnp_string = device.PNPDeviceID
      ven_id = 'UNKNOWN'
      dev_id = 'UNKNOWN'
      match = re.search(r'VEN_([0-9A-F]{4})', pnp_string)
      if match:
        ven_id = match.group(1).lower()
      match = re.search(r'DEV_([0-9A-F]{4})', pnp_string)
      if match:
        dev_id = match.group(1).lower()

      dev_name = device.VideoProcessor or ''
      version = device.DriverVersion or ''
      ven_name, dev_name = gpu.ids_to_names(ven_id, 'Unknown', dev_id, dev_name)

      dimensions.add(ven_id)
      dimensions.add('%s:%s' % (ven_id, dev_id))
      if version:
        dimensions.add('%s:%s-%s' % (ven_id, dev_id, version))
        state.add('%s %s %s' % (ven_name, dev_name, version))
      else:
        state.add('%s %s' % (ven_name, dev_name))
  except pythoncom.com_error as e:
    # This generally happens when this is called as the host is shutting down.
    logging.error('get_gpu(): %s', e)
  return sorted(dimensions), sorted(state)


@tools.cached
def get_integrity_level():
  """Returns the integrity level of the current process as a string.

  TODO(maruel): It'd be nice to make it work on cygwin. The problem is that
  ctypes.windll is unaccessible and it is not known to the author how to use
  stdcall convention through ctypes.cdll.
  """
  if get_os_version_number() == '5.1':
    # Integrity level is Vista+.
    return None

  mapping = {
      0x0000: 'untrusted',
      0x1000: 'low',
      0x2000: 'medium',
      0x2100: 'medium high',
      0x3000: 'high',
      0x4000: 'system',
      0x5000: 'protected process',
  }

  # This was specifically written this way to work on cygwin except for the
  # windll part. If someone can come up with a way to do stdcall on cygwin, that
  # would be appreciated.
  BOOL = ctypes.c_long
  DWORD = ctypes.c_ulong
  HANDLE = ctypes.c_void_p

  class SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('Sid', ctypes.c_void_p),
        ('Attributes', DWORD),
    ]

  class TOKEN_MANDATORY_LABEL(ctypes.Structure):
    _fields_ = [
        ('Label', SID_AND_ATTRIBUTES),
    ]

  TOKEN_READ = DWORD(0x20008)
  # Use the same casing as in the C declaration:
  # https://msdn.microsoft.com/library/windows/desktop/aa379626.aspx
  TokenIntegrityLevel = ctypes.c_int(25)
  ERROR_INSUFFICIENT_BUFFER = 122

  # All the functions used locally. First open the process' token, then query
  # the SID to know its integrity level.
  ctypes.windll.kernel32.GetLastError.argtypes = ()
  ctypes.windll.kernel32.GetLastError.restype = DWORD
  ctypes.windll.kernel32.GetCurrentProcess.argtypes = ()
  ctypes.windll.kernel32.GetCurrentProcess.restype = ctypes.c_void_p
  ctypes.windll.advapi32.OpenProcessToken.argtypes = (HANDLE, DWORD,
                                                      ctypes.POINTER(HANDLE))
  ctypes.windll.advapi32.OpenProcessToken.restype = BOOL
  ctypes.windll.advapi32.GetTokenInformation.argtypes = (HANDLE, ctypes.c_long,
                                                         ctypes.c_void_p, DWORD,
                                                         ctypes.POINTER(DWORD))
  ctypes.windll.advapi32.GetTokenInformation.restype = BOOL
  ctypes.windll.advapi32.GetSidSubAuthorityCount.argtypes = [ctypes.c_void_p]
  ctypes.windll.advapi32.GetSidSubAuthorityCount.restype = ctypes.POINTER(
      ctypes.c_ubyte)
  ctypes.windll.advapi32.GetSidSubAuthority.argtypes = (ctypes.c_void_p, DWORD)
  ctypes.windll.advapi32.GetSidSubAuthority.restype = ctypes.POINTER(DWORD)

  # First open the current process token, query it, then close everything.
  token = ctypes.c_void_p()
  proc_handle = ctypes.windll.kernel32.GetCurrentProcess()
  if not ctypes.windll.advapi32.OpenProcessToken(proc_handle, TOKEN_READ,
                                                 ctypes.byref(token)):
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
    if ctypes.windll.advapi32.GetTokenInformation(token, TokenIntegrityLevel,
                                                  ctypes.c_void_p(), info_size,
                                                  ctypes.byref(info_size)):
      logging.error('GetTokenInformation() failed expectation')
      return None
    if info_size.value == 0:
      logging.error('GetTokenInformation() returned size 0')
      return None
    if ctypes.windll.kernel32.GetLastError() != ERROR_INSUFFICIENT_BUFFER:
      logging.error('GetTokenInformation(): Unknown error: %d',
                    ctypes.windll.kernel32.GetLastError())
      return None
    token_info = TOKEN_MANDATORY_LABEL()
    ctypes.resize(token_info, info_size.value)
    if not ctypes.windll.advapi32.GetTokenInformation(
        token, TokenIntegrityLevel, ctypes.byref(token_info), info_size,
        ctypes.byref(info_size)):
      logging.error(
          'GetTokenInformation(): Unknown error with buffer size %d: %d',
          info_size.value,
          ctypes.windll.kernel32.GetLastError())
      return None
    p_sid_size = ctypes.windll.advapi32.GetSidSubAuthorityCount(
        token_info.Label.Sid)
    res = ctypes.windll.advapi32.GetSidSubAuthority(
        token_info.Label.Sid, p_sid_size.contents.value - 1)
    value = res.contents.value
    return mapping.get(value) or '0x%04x' % value
  finally:
    ctypes.windll.kernel32.CloseHandle(token)


@tools.cached
def get_physical_ram():
  """Returns the amount of installed RAM in Mb, rounded to the nearest number.
  """

  # https://msdn.microsoft.com/library/windows/desktop/aa366589.aspx
  class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ('dwLength', ctypes.c_ulong),
        ('dwMemoryLoad', ctypes.c_ulong),
        ('dwTotalPhys', ctypes.c_ulonglong),
        ('dwAvailPhys', ctypes.c_ulonglong),
        ('dwTotalPageFile', ctypes.c_ulonglong),
        ('dwAvailPageFile', ctypes.c_ulonglong),
        ('dwTotalVirtual', ctypes.c_ulonglong),
        ('dwAvailVirtual', ctypes.c_ulonglong),
        ('dwAvailExtendedVirtual', ctypes.c_ulonglong),
    ]
  stat = MemoryStatusEx()
  stat.dwLength = ctypes.sizeof(MemoryStatusEx)  # pylint: disable=W0201
  ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
  return int(round(stat.dwTotalPhys / 1024. / 1024.))


def get_uptime():
  """Return uptime for Windows 7 and later.

  Excludes sleep time.
  """
  val = ctypes.c_ulonglong(0)
  if ctypes.windll.kernel32.QueryUnbiasedInterruptTime(ctypes.byref(val)) != 0:
    return val.value / 10000000.
  return 0.


def get_reboot_required():
  """Returns True if the system should be rebooted to apply updates.

  This is not guaranteed to notice all conditions that could require reboot.
  """
  # Based on https://stackoverflow.com/a/45717438
  k = None
  import winreg
  try:
    k = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\'
        'Auto Update\\RebootRequired')
    _, num_values, _ = winreg.QueryInfoKey(k)
    return num_values > 0
  except WindowsError:  # pylint: disable=undefined-variable
    # This error very likely means the RebootRequired key does not exist,
    # meaning reboot is not required.
    return False
  finally:
    if k:
      k.Close()


@tools.cached
def get_ssd():
  """Returns a list of SSD disks."""
  wbem = _get_wmi_wbem_for_storage()
  if not wbem:
    return ()
  # https://docs.microsoft.com/en-us/previous-versions/windows/desktop/stormgmt/msft-physicaldisk
  try:
    return sorted(
      d.DeviceId for d in wbem.ExecQuery('SELECT * FROM MSFT_PhysicalDisk')
      if d.MediaType == 4
    )
  except AttributeError:
    return ()


def list_top_windows():
  """Returns a list of the class names of topmost windows.

  Windows owned by the shell are ignored.
  """
  # The function prototype of EnumWindowsProc.
  window_enum_proc_prototype = ctypes.WINFUNCTYPE(
      ctypes.c_long,  # BOOL
      ctypes.c_void_p,  # HWND
      ctypes.c_void_p)  # LPARAM

  # Set up various user32 functions that are needed.
  ctypes.windll.user32.EnumWindows.restype = ctypes.c_long  # BOOL
  ctypes.windll.user32.EnumWindows.argtypes = [
      window_enum_proc_prototype,
      ctypes.py_object
  ]
  ctypes.windll.user32.IsWindowVisible.restype = ctypes.c_long  # BOOL
  ctypes.windll.user32.IsWindowVisible.argtypes = [ctypes.c_void_p]  # HWND
  ctypes.windll.user32.IsIconic.restype = ctypes.c_long  # BOOL
  ctypes.windll.user32.IsIconic.argtypes = [ctypes.c_void_p]  # HWND

  out = []

  def on_window(hwnd, lparam):  # pylint: disable=unused-argument
    """Evaluates |hwnd| to determine whether or not it is a topmost window.

    In case |hwnd| is a topmost window, its class name is added to the
    collection of topmost window class names to return.
    """
    # Dig deeper into visible, non-iconified, topmost windows.
    if (ctypes.windll.user32.IsWindowVisible(hwnd) and
        not ctypes.windll.user32.IsIconic(hwnd) and
        _is_topmost_window(hwnd)):
      # Fetch the class name and make sure it's not owned by the Windows shell.
      class_name = _get_window_class(hwnd)
      if (class_name and
          class_name not in ['Button', 'Shell_TrayWnd',
                             'Shell_SecondaryTrayWnd']):
        out.append(class_name)
    return 1

  ctypes.windll.user32.EnumWindows(window_enum_proc_prototype(on_window), None)
  return out


@tools.cached
def get_computer_system_info():
  """Return a named tuple, which lists the following params from the WMI class
  Win32_ComputerSystemProduct:

  name, vendor, version, uuid
  """
  wbem = _get_wmi_wbem()
  if not wbem:
    return None

  info = None
  # https://msdn.microsoft.com/en-us/library/aa394105
  for device in wbem.ExecQuery('SELECT * FROM Win32_ComputerSystemProduct'):
    info = common.ComputerSystemInfo(
        name=device.Name,
        vendor=device.Vendor,
        version=device.Version,
        serial=device.IdentifyingNumber)
  return info
