import copy
import json

import yaml
from pandaclient import MiscUtils, PsubUtils

siteOptions = ['ANALY_BNL_GPU_ARC', 'ANALY_OU_OSCER_GPU_TEST', 'ANALY_QMUL_GPU_TEST',
               "ANALY_MANC_GPU_TEST", "ANALY_MWT2_GPU", "ANALY_INFN-T1_GPU", "ANALY_SLAC_GPU", "ANALY_CERN-PTEST"]
searchAlgorithmOptions = sorted(
    ['hyperopt', 'skopt', 'bohb', 'ax', 'tune', 'random', 'bayesian', 'nevergrad'])
steeringExecTemplate = 'run --rm -v "$(pwd)":/HPOiDDS #STEERINGCONTAINER /bin/bash -c "hpogrid generate --n_point=%NUM_POINTS --max_point=%MAX_POINTS --infile=/HPOiDDS/%IN --outfile=/HPOiDDS/%OUT -l=#METHOD"'


class JobConfig:
    def __init__(self):
        # general configurations
        self._nParallelEvaluation = 1
        self._maxPoints = 10
        self._maxEvaluationJobs = 2 * self._maxPoints
        # steering configurations
        self._nPointsPerIteration = 2
        self._minUnevaluatedPoints = 0
        self._steeringContainer = "gitlab-registry.cern.ch/zhangruihpc/steeringcontainer:0.0.4"
        self._searchAlgorithm = 'nevergrad'
        self._searchSpaceFile = ""
        # evaluation configurations
        self._evaluationContainer = "docker://gitlab-registry.cern.ch/zhangruihpc/evaluationcontainer:mlflow"
        self._evaluationExec = ""
        self._evaluationInput = 'input.json'  #
        self._evaluationTrainingData = "input_ds.json"
        self._evaluationOutput = "output.json"
        self._evaluationMeta = ""  #
        self._evaluationMetrics = "metrics.tgz"
        self._trainingDS = ""
        self._checkPointToSave = ""
        self._checkPointToLoad = ""  #
        self._checkPointInterval = 5
        self._site = siteOptions[:1]
        self._customOutDS = ""
        self._uuid = str(MiscUtils.wrappedUuidGen()).upper()
        pass

    @property
    def user(self):
        return PsubUtils.getNickname()

    @property
    def uuid(self):
        return self._uuid

    @property
    def outDS(self):
        return "user.{0}{1}.{2}/".format(self.user, ("." + self.customOutDS) if self.customOutDS else "", self.uuid)

    @property
    def searchAlgorithm(self):
        return self._searchAlgorithm

    @searchAlgorithm.setter
    def searchAlgorithm(self, val):
        self._searchAlgorithm = val

    @property
    def nParallelEvaluation(self):
        return self._nParallelEvaluation

    @nParallelEvaluation.setter
    def nParallelEvaluation(self, n):
        if isinstance(n, int) and n > 0:
            self._nParallelEvaluation = n
        else:
            raise ValueError(
                "{} is an invalid value of nParallelEvaluations".format(n))

    @property
    def maxPoints(self):
        return self._maxPoints

    @maxPoints.setter
    def maxPoints(self, n):
        if isinstance(n, int) and n > 0 and n <= self.maxEvaluationJobs:
            self._maxPoints = n
        else:
            raise ValueError("{} is an invalid value of maxPoints".format(n))

    @property
    def maxEvaluationJobs(self):
        return self._maxEvaluationJobs

    @maxEvaluationJobs.setter
    def maxEvaluationJobs(self, n):
        if isinstance(n, int) and n > 0 and n >= self.maxPoints:
            self._maxEvaluationJobs = n
        else:
            raise ValueError(
                "{} is an invalid value of maxEvaluationJobs".format(n))

    @property
    def nPointsPerIteration(self):
        return self._nPointsPerIteration

    @nPointsPerIteration.setter
    def nPointsPerIteration(self, n):
        if isinstance(n, int) and n > 0:
            self._nPointsPerIteration = n
        else:
            raise ValueError(
                "{} is an invalid value of nPointsPerIteration".format(n))

    @property
    def minUnevaluatedPoints(self):
        return self._minUnevaluatedPoints

    @minUnevaluatedPoints.setter
    def minUnevaluatedPoints(self, n):
        if isinstance(n, int) and n >= 0:
            self._minUnevaluatedPoints = n
        else:
            raise ValueError(
                "{} is an invalid value of minUnevaluatedPoints".format(n))

    @property
    def steeringContainer(self):
        return self._steeringContainer

    @steeringContainer.setter
    def steeringContainer(self, t):
        if isinstance(t, str):
            self._steeringContainer = t
        else:
            raise ValueError(
                "{} is an invalid value of steeringContainer".format(t))

    @property
    def steeringExec(self):
        return steeringExecTemplate.replace("#STEERINGCONTAINER", self.steeringContainer).replace("#METHOD", self.searchAlgorithm)

    @property
    def searchSpaceFile(self):
        return self._searchSpaceFile

    @searchSpaceFile.setter
    def searchSpaceFile(self, t):
        if isinstance(t, str) and t.endswith(".json"):
            self._searchSpaceFile = t
        else:
            raise ValueError(
                "{} is an invalid value for searchSpaceFile".format(t))

    @property
    def evaluationContainer(self):
        return self._evaluationContainer

    @evaluationContainer.setter
    def evaluationContainer(self, t):
        if isinstance(t, str):
            self._evaluationContainer = t
        else:
            raise ValueError(
                "{} is an invalid value of searchSpaceFile".format(t))

    @property
    def evaluationExec(self):
        return self._evaluationExec

    @evaluationExec.setter
    def evaluationExec(self, t):
        if isinstance(t, str) and len(t) > 0:
            self._evaluationExec = t
        else:
            raise ValueError(
                "{} is an invalid value of evaluationExec".format(t))

    @property
    def evaluationInput(self):
        return self._evaluationInput

    @evaluationInput.setter
    def evaluationInput(self, t):
        if isinstance(t, str) and t.endswith(".json"):
            self._evaluationInput = t
        else:
            raise ValueError(
                "{} is an invalid value of evaluationInput".format(t))

    @property
    def evaluationTrainingData(self):
        return self._evaluationTrainingData

    @evaluationTrainingData.setter
    def evaluationTrainingData(self, t):
        if isinstance(t, str) and t.endswith(".json"):
            self._evaluationTrainingData = t
        else:
            raise ValueError(
                "{} is an invalid value of evaluationTrainingData".format(t))

    @property
    def evaluationOutput(self):
        return self._evaluationOutput

    @evaluationOutput.setter
    def evaluationOutput(self, t):
        if isinstance(t, str) and t.endswith(".json"):
            self._evaluationOutput = t
        else:
            raise ValueError(
                "{} is an invalid value of evaluationOutput".format(t))

    @property
    def evaluationMeta(self):
        return self._evaluationMeta

    @evaluationMeta.setter
    def evaluationMeta(self, t):
        if isinstance(t, str):
            self._evaluationMeta = t
        else:
            raise ValueError(
                "{} is an invalid value of evaluationMeta".format(t))

    @property
    def evaluationMetrics(self):
        return self._evaluationMetrics

    @evaluationMetrics.setter
    def evaluationMetrics(self, t):
        if isinstance(t, str) and t.endswith(".tgz"):
            self._evaluationMetrics = t
        else:
            raise ValueError(
                "{} is an invalid value of evaluationMetrics".format(t))

    @property
    def trainingDS(self):
        return self._trainingDS

    @trainingDS.setter
    def trainingDS(self, t):
        if isinstance(t, str):
            self._trainingDS = t
        else:
            raise ValueError("{} is an invalid value of trainingDS".format(t))

    @property
    def customOutDS(self):
        return self._customOutDS

    @customOutDS.setter
    def customOutDS(self, t):
        if isinstance(t, str):
            self._customOutDS = t
        else:
            raise ValueError("{} is an invalid value of customOutDS".format(t))

    @property
    def checkPointToSave(self):
        return self._checkPointToSave

    @checkPointToSave.setter
    def checkPointToSave(self, t):
        if isinstance(t, str):
            self._checkPointToSave = t
        else:
            raise ValueError(
                "{} is an invalid value of checkPointToSave".format(t))

    @property
    def checkPointToLoad(self):
        return self._checkPointToLoad

    @checkPointToLoad.setter
    def checkPointToLoad(self, t):
        if isinstance(t, str):
            self._checkPointToLoad = t
        else:
            raise ValueError(
                "{} is an invalid value of checkPointToLoad".format(t))

    @property
    def checkPointInterval(self):
        return self._checkPointInterval

    @checkPointInterval.setter
    def checkPointInterval(self, n):
        if isinstance(n, int) and n > 0:
            self._checkPointInterval = n
        else:
            raise TypeError(
                "{} is an invalid value of checkPointInterval".format(n))

    @property
    def site(self):
        return self._site

    @site.setter
    def site(self, s):
        if isinstance(s, list) and all([(site in siteOptions) for site in s]):
            self._site = s
        else:
            raise TypeError("site must be a list")

    def to_json(self, name=None):
        config = self.to_dict()
        if isinstance(name, str) and name.endswith(".json") and name.replace(".json", ""):
            with open(name, "w") as f:
                output = {key: config[key] for key in config if key != "uuid"}
                json.dump(output, f, indent=4)
            return
        else:
            return json.dumps(config, sort_keys=False)

    def to_yaml(self, name=None):
        config = self.to_dict()
        if isinstance(name, str) and name.endswith(".yaml") and name.replace(".yaml", ""):
            with open(name, 'w') as f:
                output = {key: config[key] for key in config if key != "uuid"}
                yaml.dump(output, f)
            return
        else:
            return yaml.dump(config)

    def _to_dict(self):
        properties = {p.replace("_", ""): self.__dict__[
            p] for p in self.__dict__ if self.__dict__[p]}
        return properties

    def to_dict(self):
        return self._to_dict()

    def copy(self):
        return copy.deepcopy(self)
