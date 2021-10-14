import copy
import json
import os
import re

import yaml
from pandaclient import (Client, MiscUtils, PandaToolsPkgInfo, PLogger,
                         PsubUtils, panda_jupyter)

from .JobConfigurations import JobConfig
from .utils import taskAttributes

tmpLog = PLogger.getPandaLogger()


class Phpo:
    def __init__(self):
        self.JobConfig = JobConfig()
        self.HyperParameters = {}
        self._alrbArgs = None
        self._architecture = ""
        self._segmentSpecFile = None
        self._workingGroup = None
        self._noSubmit = None
        self._voms = None
        self._intrSrv = False
        self._official = False
        pass

    @property
    def SearchSpace(self):
        return {element.name: element.search_space_element for element in self.HyperParameters.values()}

    @property
    def execStrTemplate(self):
        return 'phpo'

    def _setup(self):
        panda_jupyter.setup()
        return

    @property
    def ExecStr(self):
        config = self.JobConfig
        execStr = self.execStrTemplate
        for att in taskAttributes:
            val = getattr(config, att)
            if att in ["evaluationExec", 'evaluationContainer', 'steeringExec']:
                if not val:
                    tmpLog.error(
                        '--{0} is not specified. Setting to a dummy value.'.format(att.replace("_", "")))
            if val == None or val == "":
                continue
            if att == "outDS":
                if not PsubUtils.checkOutDsName(outDS=val, official=self._official, nickName=PsubUtils.getNickname(), verbose=True):
                    tmpLog.exception("Invalid outDS name: %s" % val)
            if att == "site":
                val = ",".join(val)
            if isinstance(val, bool):
                if val:
                    execStr += ' --{0}'.format(att)
            else:
                execStr += " --{0}={1}".format(att, val)
        return execStr

    def _makeSandbox(self, verbose=False):
        # create tmp dir
        curDir = os.getcwd()
        tmpDir = os.path.join(curDir, MiscUtils.wrappedUuidGen())
        os.makedirs(tmpDir)

        # sandbox
        if verbose:
            tmpLog.debug("=== making sandbox ===")
        archiveName = 'jobO.%s.tar' % MiscUtils.wrappedUuidGen()
        archiveFullName = os.path.join(tmpDir, archiveName)
        extensions = ['json', 'py', 'sh', 'yaml']
        find_opt = ' -o '.join(['-name "*.{0}"'.format(e) for e in extensions])
        tmpOut = MiscUtils.commands_get_output(
            'find . {0} | tar cvfz {1} --files-from - '.format(find_opt, archiveFullName))

        if verbose:
            print(tmpOut + '\n')
            tmpLog.debug("=== checking sandbox ===")
            tmpOut = MiscUtils.commands_get_output(
                'tar tvfz {0}'.format(archiveFullName))
            print(tmpOut + '\n')
            tmpLog.debug("=== uploading sandbox===")
        os.chdir(tmpDir)
        status, out = Client.putFile(
            archiveName, verbose, useCacheSrv=True, reuseSandbox=True)
        os.chdir(curDir)
        if out.startswith('NewFileName:'):
            # found the same input sandbox to reuse
            archiveName = out.split(':')[-1]
        elif out != 'True':
            # failed
            # print(out)
            tmpLog.error("Failed with %s" % status)
        matchURL = re.search("(http.*://[^/]+)/", Client.baseURLCSRVSSL)
        sourceURL = matchURL.group(1)

        return tmpDir, archiveName, sourceURL

    def taskParams(self, archiveName, sourceURL, noEmail=True):
        config = self.JobConfig
        taskParamMap = {}
        taskParamMap['noInput'] = True
        taskParamMap['nEventsPerJob'] = 1
        taskParamMap['nEvents'] = config.nParallelEvaluation
        taskParamMap['maxNumJobs'] = config.maxEvaluationJobs
        taskParamMap['totNumJobs'] = config.maxPoints
        taskParamMap['taskName'] = config.outDS
        taskParamMap['vo'] = 'atlas'
        taskParamMap['architecture'] = self._architecture
        taskParamMap['hpoWorkflow'] = True
        taskParamMap['transUses'] = ''
        taskParamMap['transHome'] = ''
        taskParamMap['transPath'] = 'http://pandaserver.cern.ch:25080/trf/user/runHPO-00-00-01'
        taskParamMap['processingType'] = 'panda-client-{0}-jedi-hpo'.format(
            PandaToolsPkgInfo.release_version)
        taskParamMap['prodSourceLabel'] = 'user'
        taskParamMap['useLocalIO'] = 1
        taskParamMap['cliParams'] = self.ExecStr
        taskParamMap['skipScout'] = True
        taskParamMap['coreCount'] = 1
        taskParamMap['container_name'] = config.evaluationContainer
        if noEmail:
            taskParamMap['noEmail'] = True
        if self._workingGroup is not None:
            taskParamMap['workingGroup'] = self._workingGroup
        if len(config.site) == 1:
            taskParamMap['site'] = config.site[0]
        else:
            taskParamMap['includedSite'] = config.site
        taskParamMap['multiStepExec'] = {'preprocess': {'command': '${TRF}',
                                                        'args': '--preprocess ${TRF_ARGS}'},
                                         'postprocess': {'command': '${TRF}',
                                                         'args': '--postprocess ${TRF_ARGS}'},
                                         'containerOptions': {'containerExec':
                                                              'while [ ! -f __payload_in_sync_file__ ]; do sleep 5; done; '
                                                              'echo "=== cat exec script ==="; '
                                                              'cat __run_main_exec.sh; '
                                                              'echo; '
                                                              'echo "=== exec script ==="; '
                                                              '/bin/sh __run_main_exec.sh; '
                                                              'REAL_MAIN_RET_CODE=$?; '
                                                              'touch __payload_out_sync_file__; '
                                                              'exit $REAL_MAIN_RET_CODE ',
                                                              'containerImage': config.evaluationContainer}
                                         }
        if config.checkPointToSave:
            taskParamMap['multiStepExec']['coprocess'] = {'command': '${TRF}',
                                                          'args': '--coprocess ${TRF_ARGS}'}
        if self._alrbArgs:
            taskParamMap['multiStepExec']['containerOptions']['execArgs'] = self._alrbArgs

        logDatasetName = re.sub('/$', '.log/', config.outDS)

        taskParamMap['log'] = {'dataset': logDatasetName,
                               'container': logDatasetName,
                               'type': 'template',
                               'param_type': 'log',
                               'value': '{0}.$JEDITASKID.${{SN}}.log.tgz'.format(logDatasetName[:-1])
                               }
        taskParamMap['hpoRequestData'] = {'sandbox': None,
                                          'executable': 'docker',
                                          'arguments': config.steeringExec,
                                          'output_json': 'output.json',
                                          'max_points': config.maxPoints,
                                          'num_points_per_generation': config.nPointsPerIteration,
                                          }
        if config.minUnevaluatedPoints:
            taskParamMap['hpoRequestData']['min_unevaluated_points'] = config.minUnevaluatedPoints
        if config.searchSpaceFile:
            with open(config.searchSpaceFile, mode='r') as json_file:
                optSpace = json.load(json_file)
                if optSpace:
                    taskParamMap['hpoRequestData']['opt_space'] = optSpace
                else:
                    tmpLog.warning(
                        "%s empty, switching to internal search space." % config.searchSpaceFile)
        else:
            taskParamMap['hpoRequestData']['opt_space'] = self.SearchSpace
            if not taskParamMap['hpoRequestData']['opt_space']:
                tmpLog.warning(
                    "Empty search space. Job will not run. Define a valid search space by using method 'define_searchSpace' or specifying a non-empty external search space.")

        taskParamMap['jobParameters'] = [
            {'type': 'constant',
             'value': '-o {0} -j "" --inSampleFile {1}'.format(config.evaluationOutput,
                                                               config.evaluationInput)
             },
            {'type': 'constant',
             'value': '-a {0} --sourceURL {1}'.format(archiveName, sourceURL)
             },
        ]
        taskParamMap['jobParameters'] += [
            {'type': 'constant',
             'value': '-p "',
             'padding': False,
             },
        ]
        taskParamMap['jobParameters'] += PsubUtils.convertParamStrToJediParam(config.evaluationExec, {}, '',
                                                                              True, False,
                                                                              includeIO=False)
        taskParamMap['jobParameters'] += [
            {'type': 'constant',
             'value': '"',
             },
        ]
        if config.checkPointToSave:
            taskParamMap['jobParameters'] += [
                {'type': 'constant',
                 'value': '--checkPointToSave {0}'.format(config.checkPointToSave)
                 },
            ]
            if config.checkPointInterval:
                taskParamMap['jobParameters'] += [
                    {'type': 'constant',
                     'value': '--checkPointInterval {0}'.format(config.checkPointInterval)
                     },
                ]
        if config.checkPointToLoad:
            taskParamMap['jobParameters'] += [
                {'type': 'constant',
                 'value': '--checkPointToLoad {0}'.format(config.checkPointToLoad)
                 },
            ]
        if config.trainingDS:
            taskParamMap['jobParameters'] += [
                {'type': 'constant',
                 'value': '--writeInputToTxt IN_DATA:{0}'.format(config.evaluationTrainingData)
                 },
                {'type': 'template',
                 'param_type': 'input',
                 'value': '-i "${IN_DATA/T}"',
                 'dataset': config.trainingDS,
                 'attributes': 'nosplit,repeat',
                 },
                {'type': 'constant',
                 'value': '--inMap "{\'IN_DATA\': ${IN_DATA/T}}"'
                 },
            ]
        if config.evaluationMeta:
            taskParamMap['jobParameters'] += [
                {'type': 'constant',
                 'value': '--outMetaFile={0}'.format(config.evaluationMeta),
                 },
            ]
        if self._segmentSpecFile:
            taskParamMap['segmentedWork'] = True
            with open(self._segmentSpecFile) as f:
                # read segments
                segments = json.load(f)
                # search space
                if 'opt_space' in taskParamMap['hpoRequestData'] and \
                        isinstance(taskParamMap['hpoRequestData']['opt_space'], dict):
                    space = taskParamMap['hpoRequestData']['opt_space']
                    taskParamMap['hpoRequestData']['opt_space'] = []
                else:
                    space = None
                # set model ID to each segment
                for i in range(len(segments)):
                    segments[i].update({'id': i})
                    # make clone of search space if needed
                    if space is not None:
                        new_space = dict()
                        new_space['model_id'] = i
                        new_space['search_space'] = copy.deepcopy(space)
                        taskParamMap['hpoRequestData']['opt_space'].append(
                            new_space)
                taskParamMap['segmentSpecs'] = segments

            taskParamMap['jobParameters'] += [
                {'type': 'constant',
                 'value': '--segmentID=${SEGMENT_ID}',
                 },
            ]
        if config.evaluationMetrics is not None:
            lfn = '$JEDITASKID.metrics.${SN}.tgz'
            if self._segmentSpecFile is not None:
                lfn = '${MIDDLENAME}.' + lfn
            taskParamMap['jobParameters'] += [
                {'type': 'template',
                 'param_type': 'output',
                 'value': lfn,
                 'dataset': config.outDS,
                 'hidden': True,
                 },
                {'type': 'constant',
                 'value': '--outMetricsFile=${{OUTPUT0}}^{0}'.format(config.evaluationMetrics),
                 },
            ]

        return taskParamMap

    def submit(self, verbose=False, checkOnly=False, python3=False, noEmail=True, dumpJson=None, loadJson=None, dumpYaml=None):
        panda_jupyter.setup()
        # check grid-proxy
        PsubUtils.check_proxy(verbose, self._voms)
        config = self.JobConfig
        if self._intrSrv:
            Client.useIntrServer()

        tmpDir, archiveName, sourceURL = self._makeSandbox(verbose=verbose)
        taskParamMap = self.taskParams(
            archiveName=archiveName, sourceURL=sourceURL, noEmail=noEmail)

        if checkOnly:
            if verbose:
                tmpLog.debug("==== taskParams ====")
                print(yaml.dump(taskParamMap))
            return

        tmpLog.info("submit {0}".format(config.outDS))
        tmpStat, tmpOut = Client.insertTaskParams(taskParamMap, verbose, True)
        # result
        taskID = None
        exitCode = None
        if tmpStat != 0:
            tmpStr = "task submission failed with {0}".format(tmpStat)
            tmpLog.error(tmpStr)
            exitCode = 1
        if tmpOut[0] in [0, 3]:
            tmpStr = tmpOut[1]
            tmpLog.info(tmpStr)
            os.remove(tmpDir)
            try:
                m = re.search('jediTaskID=(\d+)', tmpStr)
                taskID = int(m.group(1))
            except Exception:
                pass
        else:
            tmpStr = "task submission failed. {0}".format(tmpOut[1])
            tmpLog.error(tmpStr)
            exitCode = 1

        dumpItem = config._to_dict()
        dumpItem['returnCode'] = exitCode
        dumpItem['returnOut'] = tmpStr
        dumpItem['jediTaskID'] = taskID

        # dump
        if dumpJson:
            with open(dumpJson, 'w') as f:
                json.dump(dumpItem, f)
        if dumpYaml:
            with open(dumpYaml, 'w') as f:
                yaml.dump(dumpItem, f)
        return

    def saveSearchSpace(self, name: str):
        search_space = {
            element.name: element.search_space_element for element in self.HyperParameters.values()}
        if name and name.endswith(".json") and name.replace(".json", ""):
            with open(name, "w") as f:
                json.dump(search_space, f, indent=4)
        elif name and name.endswith(".yaml") and name.replace(".yaml", ""):
            with open(name, "w") as f:
                yaml.dump(search_space, f)
        return

    def saveConfig(self, name: str):
        if name and name.endswith(".json") and name.replace(".json", ""):
            self.JobConfig.to_json(name=name)
        elif name and name.endswith(".yaml") and name.replace(".yaml", ""):
            self.JobConfig.to_yaml(name=name)
        return

    @staticmethod
    def check_proxy(verbose=False, vomsRole=None, refresh_info=False, generate_new=True):
        return PsubUtils.check_proxy(verbose, vomsRole, refresh_info=refresh_info, generate_new=generate_new)
