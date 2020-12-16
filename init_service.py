import os

import model_server_config_pb2
import toml
from google.protobuf import text_format


class mi(object):
    def __init__(self):
        self.config = toml.load("./config.toml")
        self.model_list = self.config['models']['name']
        self.work_dirs = self.config['work']
        if not os.path.isdir(self.work_dirs['models']):
            os.makedirs(self.work_dirs['models'])
        if not os.path.isdir(self.work_dirs['tmp']):
            os.makedirs(self.work_dirs['tmp'])

    def gen_model_config_for_tfserving(self):
        mfl = model_server_config_pb2.ModelConfigList()
        for mn in self.model_list:
            mf = model_server_config_pb2.ModelConfig()
            mf.name = mn
            mf.base_path = os.path.join(self.work_dirs['models'], mn)
            mf.model_type = 1
            mfl.config.append(mf)
        c = model_server_config_pb2.ModelServerConfig()
        c.model_config_list.CopyFrom(mfl)
        cs = text_format.MessageToString(c)
        with open("./model_server_config", "w") as f:
            f.write(cs)


if __name__ == '__main__':
    mio = mi()
    mio.gen_model_config_for_tfserving()
