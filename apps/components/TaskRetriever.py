import configparser
import os
import pandas as pd
import json
from urllib3 import PoolManager

class Retriever():
    def __init__(self, username=None):
        self.username = username
        self.base_url='https://bigpanda.cern.ch'
        self.headers={'Accept': 'application/json', 'Content-Type':'application/json'}
        pass

    # @property
    # def pandaConfigFile(self):
    #     return os.path.expanduser('~/.panda/panda_setup.cfg')

    # def get_username_from_conf(self):
    #     try:
    #         conf = configparser.ConfigParser()
    #         conf.read(self.pandaConfigFile)
    #         self.username = conf['main']["USERNAME"]
    #     except:
    #         pass

    # def renew_proxy(self, username, lxplusPassWord, gridPassword, host="lxplus7.cern.ch"):
    #     do_authentication(username=username, lxplusPassWord=lxplusPassWord,
    #                       gridPassword=gridPassword, host=host)
    #     self.get_username_from_conf()

    # def retrieve_all_taskId(self, username=None, **kwargs):
    #     return queryPandaMonUtils.query_tasks(username=username if username else self.username, verbose=False, **kwargs)[-1]

    def retrieve_task(self, **kwargs):
        assert ('taskID' in kwargs or 'username' in kwargs)
        http=PoolManager()
        fields={}
        if kwargs.get('taskID'):
            fields['jeditaskid']=kwargs.get('taskID')
        if kwargs.get('username'):
            fields['username']=kwargs.get('username')
        if kwargs.get('age'):
            fields['days']=kwargs.get('age')
        if kwargs.get('taskname'):
            fields['taskname']=kwargs.get('taskname')
        req = http.request(
            method="GET",
            headers=self.headers,
            url=self.base_url+"/tasks",
            fields=fields
        )
        return req.status, json.loads(req.data)

    def retrieve_jobs(self, taskID):
        http=PoolManager()
        fields={
            'jeditaskid': str(taskID)
        }
        req = http.request(
            method="GET",
            headers=self.headers,
            url=self.base_url+"/jobs",
            fields=fields
        )
        return req.status, json.loads(req.data)['jobs']


# class JobHandler:
#     def __init__(self, jobs=None):
#         self.jobs = jobs
#         self._df = self.set_job_df()

#     @property
#     def df(self):
#         return self._df

#     @df.setter
#     def df(self, Df):
#         if isinstance(Df, pd.DataFrame):
#             self._df = Df

#     def set_job_df(self):
#         try:
#             return pd.DataFrame(self.jobs)
#         except:
#             return pd.DataFrame()
