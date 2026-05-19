from __future__ import division

import re
import textwrap
import time

import wpa_pyfi.subprocess_compat as subprocess
from wpa_pyfi.utils import db2dbm
from wpa_pyfi.exceptions import InterfaceError

_bssid_re = re.compile(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$')


class Cell(object):
    """
    Presents a Python interface to the output of iwlist.
    """

    def __init__(self):
        self.ssid = None
        self.bitrates = []
        self.address = None
        self.channel = None
        self.encrypted = False
        self.encryption_type = None
        self.frequency = None
        self.mode = None
        self.quality = None
        self.signal = None
        self.noise = None

    def __repr__(self):
        return 'Cell(ssid={ssid})'.format(**vars(self))

    @classmethod
    def all(cls, interface, scan_method='iwlist'):
        """
        Returns a list of all cells.

        scan_method:
          'iwlist'  — use /sbin/iwlist (default; may conflict with wpa_supplicant)
          'wpa_cli' — ask wpa_supplicant to scan via wpa_cli (safe to call while connected)
        """
        if scan_method == 'wpa_cli':
            return cls._all_via_wpa_cli(interface)
        try:
            iwlist_scan = subprocess.check_output(['/sbin/iwlist', interface, 'scan'],
                                                  stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise InterfaceError(e.output.strip())
        else:
            iwlist_scan = iwlist_scan.decode('utf-8')
        cells = map(Cell.from_string, cells_re.split(iwlist_scan)[1:])

        return cells

    @classmethod
    def _all_via_wpa_cli(cls, interface):
        """Scan via wpa_cli so the request goes through wpa_supplicant's driver path."""
        try:
            subprocess.check_output(['wpa_cli', '-i', interface, 'scan'],
                                    stderr=subprocess.STDOUT)
            time.sleep(2)
            output = subprocess.check_output(['wpa_cli', '-i', interface, 'scan_results'],
                                             stderr=subprocess.STDOUT).decode('utf-8')
        except subprocess.CalledProcessError:
            return []

        cells = []
        for line in output.splitlines():
            parts = line.split('\t')
            if len(parts) < 5:
                continue
            if not _bssid_re.match(parts[0]):
                continue  # skip header / status lines
            try:
                cell = Cell()
                cell.address = parts[0]
                cell.signal = int(parts[2])
                flags = parts[3]
                cell.ssid = parts[4] if parts[4] else None
                cell.encrypted = '[WPA' in flags or '[WEP' in flags
                if '[WPA2' in flags:
                    cell.encryption_type = 'wpa2'
                elif '[WPA' in flags:
                    cell.encryption_type = 'wpa'
                elif '[WEP' in flags:
                    cell.encryption_type = 'wep'
                cells.append(cell)
            except (ValueError, IndexError):
                continue
        return cells

    @classmethod
    def from_string(cls, cell_string):
        """
        Parses the output of iwlist scan for one cell and returns a Cell
        object for it.
        """
        return normalize(cell_string)

    @classmethod
    def where(cls, interface, fn):
        """
        Runs a filter over the output of :meth:`all` and the returns
        a list of cells that match that filter.
        """
        return list(filter(fn, cls.all(interface)))


cells_re = re.compile(r'Cell \d+ - ')
quality_re_dict = {'dBm': re.compile(r'Quality[=:](?P<quality>\d+/\d+).*Signal level[=:](?P<siglevel>-\d+) dBm?(.*Noise level[=:](?P<noiselevel>-\d+) dBm)?'),
                   'relative': re.compile(r'Quality[=:](?P<quality>\d+/\d+).*Signal level[=:](?P<siglevel>\d+/\d+)'),
                   'absolute': re.compile(r'Quality[=:](?P<quality>\d+).*Signal level[=:](?P<siglevel>\d+)')}
frequency_re = re.compile(r'^(?P<frequency>[\d\.]+ .Hz)(?:[\s\(]+Channel\s+(?P<channel>\d+)[\s\)]+)?$')


identity = lambda x: x

key_translations = {
    'encryption key': 'encrypted',
    'essid': 'ssid',
}


def normalize_key(key):
    key = key.strip().lower()

    key = key_translations.get(key, key)

    return key.replace(' ', '')

normalize_value = {
    'ssid': lambda v: v.strip('"'),
    'encrypted': lambda v: v == 'on',
    'address': identity,
    'mode': identity,
    'channel': int,
}


def split_on_colon(string):
    key, _, value = map(lambda s: s.strip(), string.partition(':'))

    return key, value


def normalize(cell_block):
    # The cell blocks come in with every line except the first indented at
    # least 20 spaces.  This removes the first 20 spaces off of those lines.
    lines = textwrap.dedent(' ' * 20 + cell_block).splitlines()
    cell = Cell()

    while lines:
        line = lines.pop(0)

        if line.startswith('Quality'):
            for re_name, quality_re in quality_re_dict.items():
                match_result = quality_re.search(line)
                if match_result is not None:
                    groups = match_result.groupdict()
                    cell.quality = groups['quality']
                    signal = groups['siglevel']
                    noise = groups.get('noiselevel')
                    if re_name == 'relative':
                        actual, total = map(int, signal.split('/'))
                        cell.signal = db2dbm(int((actual / total) * 100))
                    elif re_name == 'absolute':
                        cell.quality = cell.quality + '/100'
                        cell.signal = db2dbm(int(signal))
                    else:
                        cell.signal = int(signal)
                    if noise is not None:
                        cell.noise = int(noise)
                    break

        elif line.startswith('Bit Rates'):
            values = split_on_colon(line)[1].split('; ')

            # consume next line of bit rates, because they are split on
            # different lines, sometimes...
            if lines:
                while lines[0].startswith(' ' * 10):
                    values += lines.pop(0).strip().split('; ')

            cell.bitrates.extend(values)
        elif ':' in line:
            key, value = split_on_colon(line)
            key = normalize_key(key)

            if key == 'ie':
                if 'Unknown' in value:
                    continue

                # consume remaining block
                values = [value]
                while lines and lines[0].startswith(' ' * 4):
                    values.append(lines.pop(0).strip())

                if 'WPA2' in value:
                    cell.encryption_type = 'wpa2'
                elif 'WPA' in value:
                    cell.encryption_type = 'wpa'
            if key == 'frequency':
                matches = frequency_re.search(value)
                cell.frequency = matches.group('frequency')
                if matches.group('channel'):
                    cell.channel = int(matches.group('channel'))
            elif key in normalize_value:
                setattr(cell, key, normalize_value[key](value))

    # It seems that encryption types other than WEP need to specify their
    # existence.
    if cell.encrypted and not cell.encryption_type:
        cell.encryption_type = 'wep'

    return cell
