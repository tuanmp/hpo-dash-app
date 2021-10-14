import os
import re
import shutil
import sys
from configparser import ConfigParser

import paramiko
from pandaclient import PLogger, panda_jupyter

tmpLog = PLogger.getPandaLogger()

siteOptions = ['ANALY_BNL_GPU_ARC', 'ANALY_OU_OSCER_GPU_TEST', 'ANALY_QMUL_GPU_TEST', "ANALY_MANC_GPU_TEST",
               "ANALY_MWT2_GPU", "ANALY_INFN-T1_GPU", "ANALY_SLAC_GPU", "ANALY_CERN-PTEST"]
searchAlgorithmOptions = ['hyperopt', 'skopt', 'bohb',
                          'ax', 'tune', 'random', 'bayesian', 'nevergrad']
steeringExecTemp = 'run --rm -v "$(pwd)":/HPOiDDS gitlab-registry.cern.ch/zhangruihpc/steeringcontainer:0.0.4 /bin/bash -c "hpogrid generate --n_point=%NUM_POINTS --max_point=%MAX_POINTS --infile=/HPOiDDS/%IN --outfile=/HPOiDDS/%OUT -l='
taskAttributes = ("nParallelEvaluation", "maxPoints", "maxEvaluationJobs", "nPointsPerIteration",
                  "minUnevaluatedPoints", "steeringContainer", "steeringExec", "evaluationContainer",
                  "evaluationExec", "site", "evaluationInput", "evaluationTrainingData", "trainingDS",
                  "evaluationOutput", "outDS", "evaluationMeta",
                  "evaluationMetrics", "checkPointToSave", "checkPointToLoad", "checkPointInterval")
parameterDetails = {
    "nParallelEvalulations": "The number of hyperparameter points evaluated concurrently.",
    "maxEvaluationJobs": "The maximum number of evaluation jobs in the search. 2\u00D7(maxPoints) by default. The task is terminated when all hyperparameter points are evaluated or the number of evaluation jobs reaches maxEvaluationJobs",
    "maxPoints": "The maximum number of hyperparameter points to evaluate in the search.",
    "nPointsPerIteration": "In each iteration, ∂ number of new hyperparameter points equals nPointsPerIteration less the number of unevaluated points.",
    "minUnevaluatedPoints": "The next iteration is triggered to generate new hyperparameter points when the number of unevaluated points goes below minUnevaluatedPoints.",
    "checkPointInterval": "Frequency to check files for checkpointing in minute.",
    "checkPointToSave": "A comma-separated list of files and/or directories to be periodically saved to a tarball for checkpointing. These files and directories must be placed in the working directory. None by default.",
    "checkPointToLoad": "The name of the saved tarball for checkpointing. The tarball is given to the evaluation container when the training is resumed, if this option is specified. Otherwise, the tarball is automatically extracted in the working directories.",
    "evaluationContainer": "The container image for evaluation.",
    "evaluationExec": "Execution string to run evaluation in singularity.",
    "trainingDS": "Name of training dataset that has been uploaded to rucio.",
    "outDS": "Name of the output dataset from the search that will be uploaded to rucio. Maybe left blank, in which case, dataset name is one shown on the add-on bars.",
    "evaluationTrainingData": "Input filename for evaluation where a json-formatted list of training data filenames is placed. 'input_ds.json' by default. Can be omitted if the payload directly fetches the training data, e.g. using wget.",
    "evaluationInput": "Input filename for evaluation where a json-formatted hyperparameter point is placed. input.json by default",
    "evaluationOutput": "Output filename of evaluation. output.json by default.",
    "evaluationMetrics": "The name of metrics file produced by evaluation.",
    "evaluationMeta": "The name of metadata file produced by evaluation.",
    "steeringContainer": "The container image for steering run by docker.∂"
}


def splitCommaSepInput(input):
    if not isinstance(input, str):
        raise TypeError("Input must be a string")
    return re.split(",", re.sub("\s", input))


def copy_panda_cfg():
    pandaPath = os.path.join(os.environ["HOME"], ".panda")
    if not os.path.isdir(pandaPath):
        os.makedirs(pandaPath)
    if not os.path.isfile(os.path.join(pandaPath, "panda_setup.cfg")):
        dst = os.path.join(pandaPath, "panda_setup.cfg")
        if 'eos/user/' in os.environ.get('HOME'):
            src = os.path.join(os.environ.get('HOME'),
                               '.local/etc/panda/panda_setup.example.cfg')
        else:
            src = f"{sys.exec_prefix}/etc/panda/panda_setup.example.cfg"
        config = ConfigParser()
        config.read(src)
        config.set(section='main', option='PANDA_AUTH',
                   value='x509_no_grid')
        config.set(section='main',
                   option='panda_use_native_httplib', value='1')
        with open(dst, 'w') as f:
            config.write(f)
    return


def get_panda_config(config_path=None):
    if config_path is not None and not config_path.endswith('panda_setup.cfg'):
        tmpLog.warning(
            'The given config file is invalid. Switching to default.')
    if not config_path or not config_path.endswith('panda_setup.cfg'):
        config_path = os.path.join(
            os.environ["HOME"], ".panda/panda_setup.cfg")
    if not os.path.isfile(config_path):
        copy_panda_cfg(config_path)
    config = ConfigParser()
    return config.read(config_path)


def create_ssh_client(username, password, host="lxplus7.cern.ch"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(policy=paramiko.AutoAddPolicy)
    ssh.load_system_host_keys()
    try:
        ssh.connect(host, username=username, password=password)
        return ssh
    except:
        print("ERROR: Unable to connect to host!")
        return None


def do_authentication(username, host, lxplusPassword, gridPassword):
    ssh = create_ssh_client(username, lxplusPassword, host)
    if ssh is None:
        tmpLog.error("Cannot login with your lxplus credentials.")
        return
    tmpLog.info("Logged in lxplus. Checking grid credentials.")
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
        "setupATLAS && lsetup rucio")
    ssh_stdin.write("y\n")
    ssh_stdin.flush()
    if 'Requested:  rucio ... \n' not in ssh_stdout.readlines():
        tmpLog.error("setupATLAS and lsetup rucio failed.")
        return
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
        "voms-proxy-init -voms atlas\n")
    try:
        ssh_stdin.write("{}\n".format(gridPassword))
        ssh_stdin.flush()
        lines = ssh_stdout.readlines()
    except:
        lines = []
    src = ""
    for line in lines:
        match = re.findall("Created proxy in (/tmp/\w+)", line)
        if match:
            src = match[0]
    if not src:
        tmpLog.error(
            "Unable to obtain voms proxy. The grid password is likely wrong.")
        return
    tmpLog.info("Obtained grid proxy. Checking bigPanda username.")
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
        "voms-proxy-info --all --e\n")
    name = ""
    for line in ssh_stdout.readlines():
        if line.startswith('subject'):
            subj = line.split(':', 1)[-1].lstrip()
            user_dn = re.sub(r'(/CN=\d+)+$', '', subj.replace('/CN=proxy', ''))
            name = user_dn.split('=')[-1]
            name = re.sub('[ |_]\d+', '', name)
            name = re.sub("[()']", '', name.replace("\n", ""))
            break
    filename = os.path.basename(src)
    sftp = ssh.open_sftp()
    pandaPath = os.path.join(os.environ["HOME"], ".panda")
    if not os.path.isdir(pandaPath):
        os.makedirs(pandaPath)
    tmpLog.info('Transfering x509 proxy.')
    sftp.get(src, os.path.join(pandaPath, filename))
    if not os.path.isfile(os.path.join(pandaPath, "panda_setup.cfg")):
        copy_panda_cfg()
        config = get_panda_config(os.path.join(pandaPath, "panda_setup.cfg"))
        config.set('main', 'PANDA_NICKNAME', username)
        config.set('main', 'X509_USER_PROXY',
                   os.path.join(pandaPath, filename))
        config.set('main', 'USERNAME', name)
        with open(os.path.join(pandaPath, "panda_setup.cfg"), 'w') as f:
            config.write(f)
    panda_jupyter.setup()
    tmpLog.info(
        f"Authentication successful! x509 proxy saved to {os.path.join(pandaPath, filename)}")
    ssh.close()
    sftp.close()
    return
