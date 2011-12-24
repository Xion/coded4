'''
Utility functions.
'''
from subprocess import Popen, PIPE


def exec_command(cmd, workdir=None):
    ''' Executes given shell command and returns its stdout as string.
    @param workdir: Working directory for the command
    '''
    cmd_out = Popen(cmd, shell=True, cwd=workdir, stdout=PIPE).stdout
    return cmd_out.read()