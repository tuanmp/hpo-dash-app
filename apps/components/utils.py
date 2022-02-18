import os
import re
import shutil
import sys
from configparser import ConfigParser
from dash import html
import dash_bootstrap_components as dbc
from pandaclient.Client import _Curl
from pandaclient.openidc_utils import OpenIdConnect_Utils

# import sys
import ssl
import uuid
import json
import time
import glob
import base64
import datetime
try:
    from urllib import urlencode, unquote_plus
    from urlparse import urlparse
    from urllib2 import urlopen, Request, HTTPError
except ImportError:
    from urllib.parse import urlencode, unquote_plus, urlparse
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
try:
    baseURL = os.environ['PANDA_URL']
except Exception:
    baseURL = 'http://pandaserver.cern.ch:25080/server/panda'
try:
    baseURLSSL = os.environ['PANDA_URL_SSL']
except Exception:
    baseURLSSL = 'https://pandaserver.cern.ch/server/panda'

baseURLCSRVSSL = "https://pandacache.cern.ch/server/panda"


# import paramiko
# from pandaclient import PLogger, panda_jupyter

# tmpLog = PLogger.getPandaLogger()

siteOptions = ['ANALY_BNL_GPU_ARC', 'ANALY_OU_OSCER_GPU_TEST', 'ANALY_QMUL_GPU_TEST', "ANALY_MANC_GPU_TEST",
               "ANALY_MWT2_GPU", "ANALY_INFN-T1_GPU", "ANALY_SLAC_GPU", "ANALY_CERN-PTEST"]
searchAlgorithmOptions = ['hyperopt', 'skopt', 'bohb',
                          'ax', 'tune', 'random', 'bayesian', 'nevergrad']
steeringExecTemp = 'run --rm -v "$(pwd)":/HPOiDDS gitlab-registry.cern.ch/zhangruihpc/steeringcontainer:0.0.4 /bin/bash -c "hpogrid generate --n_point=%NUM_POINTS --max_point=%MAX_POINTS --infile=/HPOiDDS/%IN --outfile=/HPOiDDS/%OUT -l='
taskAttributes = ("nParallelEvaluation", "maxPoints", "maxEvaluationJobs", "nPointsPerIteration",
                  "minUnevaluatedPoints", "steeringContainer", "steeringExec", "evaluationContainer",
                  "evaluationExec", "sites", "evaluationInput", "evaluationTrainingData", "trainingDS",
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

def make_options_from_list(l):
    assert isinstance(l, list), "Input must be a list."
    return [{'label': i, 'value': i} for i in l]

def check_set(att, value, obj):
    try:
        setattr(obj, att, value)
        return True, None
    except Exception as e:
        return False, e

def splitCommaSepInput(input):
    if not isinstance(input, str):
        raise TypeError("Input must be a string")
    return re.split(",", re.sub("\s", input))


full_width_style = {'width': '100%'}
info_button_style = {'font-size': '11px', 'font-weight': 'bold', 'height': '20px', 'padding': '0 6px'}

def info_button(**kwargs):
    return dbc.Button('i', size='sm', color='success', outline=False, style=info_button_style, **kwargs)

def label_with_info_button(label, **kwargs):
	return html.Div(
		[
			label,
			info_button(**kwargs)
		]
	)

def get_index(container):
    index=0
    while index in container:
        index += 1
    return index

def getMethod(optMethod):
    if "uniform" in optMethod:
        return "Uniform"
    if "normal" in optMethod:
        return "Normal"
    if "categorical" in optMethod:
        return "Categorical"
    else:
        return None

def getDType(instance):
    if isinstance(instance, int):
        return "Int"
    if isinstance(instance, float):
        return "Float"
    if isinstance(instance, str):
        return "Text"
    if isinstance(instance, bool):
        return "Boolean"
    return None

def decode_id_token(id_token):
    try:
        enc = id_token.split('.')[1]
        enc += '=' * (-len(enc) % 4)
        dec = json.loads(base64.urlsafe_b64decode(enc.encode()))
        return dec
    except Exception as e:
        print(e)
        return None
        

class my_OpenIdConnect_Utils(OpenIdConnect_Utils):
    def __init__(self, auth_config_url, token_dir=None, log_stream=None, verbose=False):
        self.auth_config_url = auth_config_url
        if token_dir is None:
            token_dir = os.environ['PANDA_CONFIG_ROOT']
        self.token_dir = os.path.expanduser(token_dir)
        if not os.path.exists(self.token_dir):
            os.makedirs(self.token_dir, exist_ok=True)
        self.log_stream = log_stream
        self.verbose = verbose

    def check_token(self, data={}):
        if self.verbose:
            self.log_stream.debug("Checking token")
        try:
            dec = decode_id_token(data['id_token'])
            exp_time = datetime.datetime.utcfromtimestamp(dec['exp'])
            delta = exp_time - datetime.datetime.utcnow()
            if self.verbose:
                        self.log_stream.debug('token expiration time : {0} UTC'.\
                                              format(exp_time.strftime("%Y-%m-%d %H:%M:%S")))
            # check expiration time
            if delta < datetime.timedelta(minutes=5):
                # return refresh token
                if 'refresh_token' in data:
                    if self.verbose:
                        self.log_stream.debug('to refresh token')
                    return False, data, dec
            else:
                # return valid token
                if self.verbose:
                    self.log_stream.debug('valid token is available')
                return True, data, dec
        except Exception as e:
            self.log_stream.error('failed to decode cached token with {0}'.format(e))
        if self.verbose:
            self.log_stream.debug('cached token unavailable')
        return False, {}, None
      
    def fetch_page(self, url):
        # path = os.path.join(self.token_dir, CACHE_PREFIX + str(uuid.uuid5(uuid.NAMESPACE_URL, str(url))))
        # if os.path.exists(path) and \
        #         datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(path)) < \
        #         datetime.timedelta(hours=1):
        #     try:
        #         with open(path) as f:
        #             return True, json.load(f)
        #     except Exception as e:
        #         self.log_stream.debug('cached {0} is corrupted: {1}'.format(os.path.basename(url), str(e)))
        if self.verbose:
            self.log_stream.debug('fetching {0}'.format(url))
        try:
            context = ssl._create_unverified_context()
            conn = urlopen(url, context=context)
            text = conn.read().decode()
            if self.verbose:
                self.log_stream.debug(text)
            # with open(path, 'w') as f:
            #     f.write(text)
            # with open(path) as f:
            return True, json.loads(text)
        except HTTPError as e:
            return False, 'code={0}. reason={1}. description={2}'.format(e.code, e.reason, e.read())
        except Exception as e:
            return False, str(e)

    def refresh_token(self, token_endpoint, client_id, client_secret, refresh_token_string):
        if self.verbose:
            self.log_stream.debug('refreshing token')
        data = {'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token_string}
        rdata = urlencode(data).encode()
        req = Request(token_endpoint, rdata)
        req.add_header('content-type', 'application/x-www-form-urlencoded')
        try:
            conn = urlopen(req)
            text = conn.read()
            if self.verbose:
                self.log_stream.debug(text)
            # id_token = json.loads(text)['id_token']
            # with open(self.get_token_path(), 'w') as f:
            #     f.write(text)
            return True, json.loads(text)
        except HTTPError as e:
            return False, 'code={0}. reason={1}. description={2}'.format(e.code, e.reason, e.read())
        except Exception as e:
            return False, str(e)


    def run_device_authorization_flow(self, data):
        self.log_stream.info('Getting custom token id')
        s, o, dec = self.check_token(data)
        if s:
            # still valid
            print('still valid')
            return True, o, False
        refresh_token_string = o.get('refresh_token')
        # get auth config
        s, o = self.fetch_page(self.auth_config_url)
        if not s:
            print('cannot fetch oage')
            return False, "Failed to get Auth configuration: " + o, False
        auth_config = o
        # get endpoint config
        s, o = self.fetch_page(auth_config['oidc_config_url'])
        if not s:
            return False, "Failed to get endpoint configuration: " + o, False
        endpoint_config = o
        # refresh token
        if refresh_token_string is not None:
            s, o = self.refresh_token(endpoint_config['token_endpoint'], auth_config['client_id'],
                                 auth_config['client_secret'], refresh_token_string)
            # refreshed
            if s:
                print('token refreshed')
                return True, o, False
            else:
                if self.verbose:
                    self.log_stream.debug('failed to refresh token: {0}'.format(o))
        # get device code
        s, o = self.get_device_code(endpoint_config['device_authorization_endpoint'], auth_config['client_id'],
                                    auth_config['audience'])
        if not s:
            print('cannot get device code')
            return False, 'Failed to get device code: ' + o, False
        # get ID token
        # self.log_stream.info(("Please go to {0} and sign in. "
        #                  "Waiting until authentication is completed").format(o['verification_uri_complete']))
        if 'interval' in o:
            interval = o['interval']
        else:
            o['interval'] = 5
        o['token_endpoint'] = endpoint_config['token_endpoint']
        o['client_id'] = auth_config['client_id']
        o['client_secret'] = auth_config['client_secret']
        for key, value in endpoint_config.items():
            o[key]=value
        for key, value in auth_config.items():
            o[key]=value
        # s, o = self.get_id_token(endpoint_config['token_endpoint'], auth_config['client_id'],
        #                          auth_config['client_secret'], o['device_code'], interval, o['expires_in'])
        # if not s:
        #     return False, "Failed to get ID token: " + o
        # self.log_stream.info('All set')
        return True, o, True

    def run_refresh_token_flow(self, refresh_token_string=None):
        s, o = self.fetch_page(self.auth_config_url)
        if not s:
            self.log_stream.error(f"Cannot fetch from authorization config url {self.auth_config_url}\n output {o}")
            return False, "Failed to get Auth configuration: " + o
        auth_config = o
        # get endpoint config
        s, o = self.fetch_page(auth_config['oidc_config_url'])
        if not s:
            self.log_stream.error(f"Cannot fetch from OIDC config url {auth_config['oidc_config_url']}\n output {o}")
            return False, "Failed to get endpoint configuration: " + o
        endpoint_config = o
        # refresh token
        if refresh_token_string is not None:
            s, o = self.refresh_token(endpoint_config['token_endpoint'], auth_config['client_id'],
                                 auth_config['client_secret'], refresh_token_string)
            # refreshed
            if s:
                print('token refreshed')
                return True, o
            else:
                if self.verbose:
                    self.log_stream.debug('failed to refresh token: {0}'.format(o))
                return False, o
        return False, o              

    def get_id_token(self, token_endpoint, client_id, client_secret, device_code, interval, expires_in):

        if self.verbose:
            self.log_stream.debug('getting ID token')
        startTime = datetime.datetime.utcnow()
        data = {'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                'device_code': device_code}
        rdata = urlencode(data).encode()
        req = Request(token_endpoint, rdata)
        req.add_header('content-type', 'application/x-www-form-urlencoded')
        while datetime.datetime.utcnow() - startTime < datetime.timedelta(seconds=expires_in):
            try:
                conn = urlopen(req)
                text = conn.read().decode()
                if self.verbose:
                    self.log_stream.info(text)
                id_token = json.loads(text)['id_token']
                # with open(self.get_token_path(), 'w') as f:
                #     f.write(text)
                return True, json.loads(text)
            except HTTPError as e:
                text = e.read()
                try:
                    description = json.loads(text)
                    # pending
                    if description['error'] == "authorization_pending":
                        time.sleep(interval + 1)
                        continue
                except Exception:
                    pass
                return False, 'code={0}. reason={1}. description={2}'.format(e.code, e.reason, text)
            except Exception as e:
                return False, str(e)

class my_Curl(_Curl):
    def __init__(self):
        super().__init__()

    def get_oidc(self, tmp_log, verbose=False):
        parsed = urlparse(baseURLSSL)
        if parsed.port:
            auth_url = '{0}://{1}:{2}/auth/{3}_auth_config.json'.format(parsed.scheme, parsed.hostname, parsed.port,
                                                                        self.authVO)
        else:
            auth_url = '{0}://{1}/auth/{3}_auth_config.json'.format(parsed.scheme, parsed.hostname, parsed.port,
                                                                    self.authVO)
        oidc = my_OpenIdConnect_Utils(auth_url, log_stream=tmp_log, verbose=verbose)
        return oidc

    

# def copy_panda_cfg():
#     pandaPath = os.path.join(os.environ["HOME"], ".panda")
#     if not os.path.isdir(pandaPath):
#         os.makedirs(pandaPath)
#     if not os.path.isfile(os.path.join(pandaPath, "panda_setup.cfg")):
#         dst = os.path.join(pandaPath, "panda_setup.cfg")
#         if 'eos/user/' in os.environ.get('HOME'):
#             src = os.path.join(os.environ.get('HOME'),
#                                '.local/etc/panda/panda_setup.example.cfg')
#         else:
#             src = f"{sys.exec_prefix}/etc/panda/panda_setup.example.cfg"
#         config = ConfigParser()
#         config.read(src)
#         config.set(section='main', option='PANDA_AUTH',
#                    value='x509_no_grid')
#         config.set(section='main',
#                    option='panda_use_native_httplib', value='1')
#         with open(dst, 'w') as f:
#             config.write(f)
#     return


# def get_panda_config(config_path=None):
#     if config_path is not None and not config_path.endswith('panda_setup.cfg'):
#         tmpLog.warning(
#             'The given config file is invalid. Switching to default.')
#     if not config_path or not config_path.endswith('panda_setup.cfg'):
#         config_path = os.path.join(
#             os.environ["HOME"], ".panda/panda_setup.cfg")
#     if not os.path.isfile(config_path):
#         copy_panda_cfg(config_path)
#     config = ConfigParser()
#     return config.read(config_path)


# def create_ssh_client(username, password, host="lxplus7.cern.ch"):
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(policy=paramiko.AutoAddPolicy)
#     ssh.load_system_host_keys()
#     try:
#         ssh.connect(host, username=username, password=password)
#         return ssh
#     except:
#         print("ERROR: Unable to connect to host!")
#         return None


# def do_authentication(username, host, lxplusPassword, gridPassword):
#     ssh = create_ssh_client(username, lxplusPassword, host)
#     if ssh is None:
#         tmpLog.error("Cannot login with your lxplus credentials.")
#         return
#     tmpLog.info("Logged in lxplus. Checking grid credentials.")
#     ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
#         "setupATLAS && lsetup rucio")
#     ssh_stdin.write("y\n")
#     ssh_stdin.flush()
#     if 'Requested:  rucio ... \n' not in ssh_stdout.readlines():
#         tmpLog.error("setupATLAS and lsetup rucio failed.")
#         return
#     ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
#         "voms-proxy-init -voms atlas\n")
#     try:
#         ssh_stdin.write("{}\n".format(gridPassword))
#         ssh_stdin.flush()
#         lines = ssh_stdout.readlines()
#     except:
#         lines = []
#     src = ""
#     for line in lines:
#         match = re.findall("Created proxy in (/tmp/\w+)", line)
#         if match:
#             src = match[0]
#     if not src:
#         tmpLog.error(
#             "Unable to obtain voms proxy. The grid password is likely wrong.")
#         return
#     tmpLog.info("Obtained grid proxy. Checking bigPanda username.")
#     ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
#         "voms-proxy-info --all --e\n")
#     name = ""
#     for line in ssh_stdout.readlines():
#         if line.startswith('subject'):
#             subj = line.split(':', 1)[-1].lstrip()
#             user_dn = re.sub(r'(/CN=\d+)+$', '', subj.replace('/CN=proxy', ''))
#             name = user_dn.split('=')[-1]
#             name = re.sub('[ |_]\d+', '', name)
#             name = re.sub("[()']", '', name.replace("\n", ""))
#             break
#     filename = os.path.basename(src)
#     sftp = ssh.open_sftp()
#     pandaPath = os.path.join(os.environ["HOME"], ".panda")
#     if not os.path.isdir(pandaPath):
#         os.makedirs(pandaPath)
#     tmpLog.info('Transfering x509 proxy.')
#     sftp.get(src, os.path.join(pandaPath, filename))
#     if not os.path.isfile(os.path.join(pandaPath, "panda_setup.cfg")):
#         copy_panda_cfg()
#         config = get_panda_config(os.path.join(pandaPath, "panda_setup.cfg"))
#         config.set('main', 'PANDA_NICKNAME', username)
#         config.set('main', 'X509_USER_PROXY',
#                    os.path.join(pandaPath, filename))
#         config.set('main', 'USERNAME', name)
#         with open(os.path.join(pandaPath, "panda_setup.cfg"), 'w') as f:
#             config.write(f)
#     panda_jupyter.setup()
#     tmpLog.info(
#         f"Authentication successful! x509 proxy saved to {os.path.join(pandaPath, filename)}")
#     ssh.close()
#     sftp.close()
#     return
