#-----------------------------------------------------------------------------
#  Copyright (C) 2019 Alberto Sottile, Eric Larson
#
#  Distributed under the terms of the 3-clause BSD License.
#-----------------------------------------------------------------------------

import atexit
import shutil
import subprocess

GSETTINGS_ARGS = ['gsettings', 'get', 'org.gnome.desktop.interface']

def getInterface() -> str:
    if not shutil.which('gsettings'):
        msg = 'Unable to determine settings, gsettings is not available.'
        raise RuntimeError(msg)

    # Using the freedesktop specifications for checking dark mode
    if subprocess.check_output(GSETTINGS_ARGS + ['color-scheme']):
        return 'color-scheme'

    # Try older gtk-theme method
    if subprocess.check_output(GSETTINGS_ARGS + ['gtk-theme']):
        return 'gtk-theme'

    msg = 'Unable to determine settings'
    raise RuntimeError(msg)

def theme():
    try:
        interface = getInterface()
    except Exception:
        return 'Light'
    stdout = subprocess.check_output(GSETTINGS_ARGS + [interface]).decode()
    # we have a string, now remove start and end quote
    theme = stdout.lower().strip()[1:-1]
    if '-dark' in theme.lower():
        return 'Dark'
    else:
        return 'Light'

def isDark():
    return theme() == 'Dark'

def isLight():
    return theme() == 'Light'

# def listener(callback: typing.Callable[[str], None]) -> None:
def listener(callback):
    interface = getInterface()

    with subprocess.Popen(
        ['gsettings', 'monitor', 'org.gnome.desktop.interface', interface],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    ) as p:
        atexit.register(p.terminate)
        for line in p.stdout:
            callback('Dark' if '-dark' in line.strip().lower() else 'Light')
