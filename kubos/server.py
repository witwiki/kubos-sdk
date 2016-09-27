# Kubos SDK
# Copyright (C) 2016 Kubos Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Interact with the debug (gdb) server.

    Example:
        kubos server <start, stop, restart, status>
   
    Attributes:
        server_running (str): Running.
        server_stopped (str): Stopped.

"""

import os
import psutil
import subprocess
import sys
import time

from options import parser
from pkg_resources import resource_filename
from utils import container, project, target

server_running = 'Running'
server_stopped = 'Stopped'

def addOptions(parser):
    """Add an argument to the argument parser.

    Args:
        parser (argparse.ArgumentParser): The argument parser to add an argument to.

    """
    parser.add_argument('action', nargs='?', help='Interact directly with the gdb server. Options: start, stop, restart or status')


def execCommand(args, following_args):
    """Interact with the gdb for remote debugging. 
   
    Args:
        args (argparse.Namespace): Command line arguments.
    
    """
    if args.action == 'start':
        start_server()
    elif args.action == 'status':
        print_server_status()
    elif args.action == 'stop':
        stop_server()
    elif args.action == 'restart':
        restart_server()


def start_server():
    """Start a board specific debugger service.

    Raises: 
        sys.stderr.

    """
    current_target = target.get_current_target()
    flash_dir, lib_dir, exe_dir = get_dirs()
    project.add_ld_library_path(lib_dir)
    if not current_target:
        print >>sys.stderr, 'Set a target hardware device and build your project before debugging'
        sys.exit(1)
    if current_target.startswith('stm32') or current_target.startswith('na'):
        flash_script = os.path.join(flash_dir, 'openocd', 'flash.sh')
        util_exe = os.path.join(exe_dir, 'openocd')
        proc = subprocess.Popen(['/bin/bash', flash_script, util_exe, '', lib_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif current_target.startswith('msp430'):
        flash_script = os.path.join(flash_dir, 'mspdebug', 'flash.sh')
        util_exe = os.path.join(exe_dir, 'mspdebug')
        proc = subprocess.Popen(['/bin/bash', flash_script, util_exe, 'gdb 3333'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #catch failed server starts
    time.sleep(0.5)
    status = get_server_status()
    if status == server_stopped:
        print >>sys.stderr, 'GDB server failed to start... Ensure your target device is connected'
        sys.exit(1)
    elif status == server_running:
        print 'Server successfully Started'


def get_server_status():
    """Determine the current status of the debugger service.

    Returns:
        server_running (str): Status for running service.
        server_stopped (str): Status for stopped service.

    """
    flash_util = get_flash_util()
    process = get_server_process(flash_util)
    if process:
        return server_running
    else:
        return server_stopped


def print_server_status():
    """Print the current status of the debugger service.

    """
    print 'Kubos GDB Server status: %s' % get_server_status()


def stop_server():
    """Stop a board specific debugger service.

    """
    flash_util = get_flash_util()
    process = get_server_process(flash_util)
    if process:
        process.terminate()
        print 'Server Shut Down...'
    else:
        print 'Server is not running... Nothing to do'


def restart_server():
    """Restart the debugger utility.

    """
    stop_server()
    start_server()


def get_server_process(util_name):
    """Retrieve a process by name.

    Args:
        util_name (str): The process name.

    Returns:
        proc (psutil.Process): The process for success, none for failure.

    """
    full_list = psutil.process_iter()
    for proc in full_list:
        try:
            if proc.name() == util_name:
                return proc
        except psutil.ZombieProcess:
            pass
    return None


def get_flash_util():
    """Determine the appropriate flash utility based on the current target.

    Returns:
        flash_util (str): Board specific flash utility name.

    Raises: 
        sys.stderr.

    """
    current_target = target.get_current_target()
    if not current_target:
        print >>sys.stderr, 'No Target is currently set. Cannot start the gdb server'
        sys.exit(1)
    if current_target.startswith('stm32') or current_target.startswith('na'):
        flash_util = 'openocd'
    elif current_target.startswith('msp430'):
        flash_util = 'mspdebug'
    return flash_util


def get_dirs():
    """Create an OS specific path to the kubos-sdk flash, library, and binary directories.

    Returns:
        flash_dir (path): OS specific path to the kubos-sdk flash directory.
        lib_dir (path): OS specific path to the kubos-sdk flash libraries.
        bin_dir (path): OS specific path to the kubos-sdk flash executables.

    """
    kubos_dir = resource_filename(__name__, '')
    flash_dir = os.path.join(kubos_dir, 'flash')
    if sys.platform.startswith('linux'):
        bin_dir = os.path.join(kubos_dir, 'bin', 'linux')
        lib_dir = os.path.join(kubos_dir, 'lib', 'linux')
    elif sys.platform.startswith('darwin'):
        bin_dir = os.path.join(kubos_dir, 'bin', 'osx')
        lib_dir = os.path.join(kubos_dir, 'lib', 'osx')
    return flash_dir, lib_dir, bin_dir

