from ast import IsNot
import yaml
import logging
from git import cmd 
from semver import VersionInfo
import re

log = logging.getLogger(__name__)
config = None


def lsremote(url):
    remote_tags = {}
    g = cmd.Git()
    remote_tags = g.ls_remote("--tags", "--sort=v:refname",url).split("\n")
    
    remote_tags = remote_tags[-1].split('\t')
    
    if remote_tags[1]:
        remote_tags[1] = remote_tags[1].replace("refs/tags/v", "").replace("^{}", "")
    else:
        return None
    return remote_tags



class Config():
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def __call__(self):
        return self.config

    def load_config(self):
        with open(self.config_file, 'r') as f:
            try:
                log.info("Loaded config file: %s", self.config_file)
                return yaml.load(f, Loader=yaml.FullLoader)
            except yaml.YAMLError as e:
                log.exception("Failed to load config file: %s", self.config_file)
                raise e




if __name__ == "__main__":
    config =  Config("config.yml")
    for repo in config()["repositories"]:
        key = next(iter(repo))
        repo_data = repo[key]
        print(repo_data["title"])
        print(repo_data["url"])
        tag = lsremote(repo_data["url"])
        if (tag[0]):
            print(VersionInfo.parse(tag[1]))