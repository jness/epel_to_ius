import subprocess

def run(options):
    '''takes a list containing shell command and options'''
    process = subprocess.Popen(options, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    return process
