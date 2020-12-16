import os
import shutil

import toml
from apscheduler.schedulers.blocking import BlockingScheduler
from boto3.session import Session
from glob2 import glob


class ml(object):
    def __init__(self, model_name):
        self.model_name = model_name
        self.config = toml.load("./config.toml")
        self.work_dirs = self.config['work']
        self.interval = self.config['daemon']['interval']
        self.s3_access_key_id = os.environ[self.config['envs']['ak']]
        self.s3_secret_access_key = os.environ[self.config['envs']['sk']]

        self.s3_bucket = os.environ[self.config['envs']['bucket']]
        self.s3_region = os.environ[self.config['envs']['region']]
        self.s3_key = os.environ[self.config['envs']['key_template']].replace("{model_name}", self.model_name)

        self.local_name = os.path.join(self.work_dirs['tmp'], self.model_name + ".zip")
        self.model_base = os.path.join(self.work_dirs['models'], self.model_name)
        self.tmp_dir = os.path.join(self.work_dirs['tmp'], self.model_name)
        self.zip_dir_name = self.work_dirs['zip_dir']

        self.session = Session(aws_access_key_id=self.s3_access_key_id, aws_secret_access_key=self.s3_secret_access_key)
        self.s3_client = self.session.client(service_name='s3', region_name=self.s3_region)

    def get_last_modified_ts(self):
        r = self.s3_client.head_object(Bucket=self.s3_bucket, Key=self.s3_key)
        return int(r['LastModified'].timestamp())

    def need_update_model(self):
        remote_modified_ts = self.get_last_modified_ts()
        if not os.path.isdir(self.model_base):
            return True, int(remote_modified_ts)
        ms = glob(os.path.join(self.model_base, "*"))
        local_modified_ts = 0
        for item in ms:
            try:
                local_modified_ts = max(int(item.split("/")[-1]), local_modified_ts)
            except Exception as e:
                print(e)
        if remote_modified_ts > local_modified_ts:
            return True, remote_modified_ts
        return False, 0

    def update_model(self, model_version):
        if os.path.isfile(self.local_name):
            os.remove(self.local_name)
        self.s3_client.download_file(Bucket=self.s3_bucket, Key=self.s3_key, Filename=self.local_name)
        if not os.path.isdir(self.model_base):
            os.mkdir(self.model_base)

        if os.path.isdir(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        os.mkdir(self.tmp_dir)

        zip_cmd = "unzip -o -d " + self.tmp_dir + " " + self.local_name
        os.system(zip_cmd)
        shutil.copytree(os.path.join(self.tmp_dir, self.zip_dir_name),
                        os.path.join(self.model_base, str(model_version)))

        shutil.rmtree(self.tmp_dir)
        if os.path.isfile(self.local_name):
            os.remove(self.local_name)

    def do(self):
        try:
            flag, v = mlo.need_update_model()
            if flag:
                mlo.update_model(v)
                print("update_model: %s || %s" % (self.model_name, str(v)))
        except Exception as e:
            print(e)


if __name__ == '__main__':
    cfg = toml.load("./config.toml")
    scheduler = BlockingScheduler()
    for mn in toml.load("./config.toml")['models']['name']:
        mlo = ml(mn)
        mlo.do()
        scheduler.add_job(mlo.do, 'interval', seconds=mlo.interval)
    scheduler.start()
