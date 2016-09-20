from kubos import flash
import unittest
from mock import MagicMock
import subprocess

def test_bash_called_with_correct_args():
    subprocess.check_call = MagicMock(return_value = 0)
    flash.flash_mspdebug("", "")
    subprocess.check_call.assert_called_with(['/bin/bash', 'flash/mspdebug/flash.sh', 'bin/osx/mspdebug', 'prog '])

test_bash_called_with_correct_args()
