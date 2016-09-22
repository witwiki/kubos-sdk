from kubos import flash
import unittest
from mock import MagicMock
import subprocess

subprocess.check_call = MagicMock(return_value = 0)

def test_bash_called_with_correct_args_mspdebug():
    flash.flash_mspdebug("", "")
    subprocess.check_call.assert_called_with(['/bin/bash', 'flash/mspdebug/flash.sh', 'bin/linux/mspdebug', 'prog '])

def test_bash_called_with_correct_args_dfu_util():
    flash.flash_dfu_util("", "")
    subprocess.check_call.assert_called_with(['/bin/bash', 'flash/dfu_util/flash.sh', 'bin/linux/dfu-util', ''])

def test_bash_called_with_correct_args_openocd():
    flash.flash_openocd("", "")
    subprocess.check_call.assert_called_with(['/bin/bash', 'flash/openocd/flash.sh', 'bin/linux/openocd', 'stm32f4_flash ', 'flash/openocd'])

test_bash_called_with_correct_args_mspdebug()
test_bash_called_with_correct_args_dfu_util()
test_bash_called_with_correct_args_openocd()



