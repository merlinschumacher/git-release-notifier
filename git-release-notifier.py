import logging
from platform import release
import smtplib
from email.message import EmailMessage
import ssl
from typing import Tuple

import yaml
from git import cmd
from semver import VersionInfo

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
config = None


class Email():
    def __init__(self, server, port, username, password):
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    def send(self, subject, body, sender_address, recipients):
        msg = EmailMessage()
        msg['From'] = sender_address
        msg['To'] = recipients
        msg['Subject'] = subject
        msg.set_content(body)
        context=ssl.create_default_context()
        with smtplib.SMTP(self.server, self.port) as s:
            try:
                s.starttls(context=context)
                s.login(self.username, self.password)
                s.send_message(msg)
            except Exception as e:
                log.error("Could not send mail to {}".format(recipients))
                log.exception(e)


class Git():
    def lsremote(url):
        remote_tags = {}
        g = cmd.Git()
        remote_tags = g.ls_remote(
            "--tags", "--sort=v:refname", url).split("\n")

        remote_tags = remote_tags[-1].split('\t')

        if remote_tags[1]:
            remote_tags[1] = remote_tags[1].replace(
                "refs/tags/v", "").replace("^{}", "")
        return remote_tags[0], remote_tags[1]


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
                log.exception("Failed to load config file: %s",
                              self.config_file)
                raise e

    def save_config(self):
        with open(self.config_file, 'w') as f:
            try:
                yaml.dump(self.config, f)
                log.info("Wrote to config file: %s", self.config_file)
            except yaml.YAMLError as e:
                log.exception("Failed to load config file: %s",
                              self.config_file)
                raise e
        return


class ReleaseNotifier():
    def __init__(self):
        self.config = Config("config.yml")
        emailConfig = self.config()["settings"]["smtp"]
        self.repositories = self.config()["repositories"]
        self.email = Email(emailConfig['host'],
                        emailConfig['port'],
                        emailConfig['username'],
                        emailConfig['password'])

        for i, repo in enumerate(self.repositories):
            key = next(iter(repo))
            repo_data = repo[key]
            self.checkRepo(i, key, repo_data)

    def sendNotification(self, title, recipients, sender_address, last_version, new_version, url):

        subject = "[NEW RELEASE]: " + \
            title + " (" + new_version + ")"
        body = """The repository of {title} now contains a tag for {new_version}.

Click here to visit the site: {url}

The last version was {last_version}.

This mail was sent by git-release-notifier.py.
    """.format(title=title,
            new_version=new_version,
            last_version=last_version,
            url=url)
        self.email.send(subject, 
                        body, 
                        sender_address,
                        recipients)

    def checkRepo(self, i, key, repo_data):
        log.info(repo_data["title"] + " (" + repo_data["url"] + ")")
        _, new_version = Git.lsremote(repo_data["url"])

        last_version = repo_data.get("last_version", "0.0.0")
        
        last_version = VersionInfo.parse(last_version)
        new_version = VersionInfo.parse(new_version)

        if (VersionInfo.compare(new_version, last_version) > 0):
            log.info("New version found: %s", new_version)
         
            recipients = repo_data.get("recipients", [])
            sender_address = repo_data.get("sender_address")
            title = repo_data.get("title")
            url = repo_data.get("url")
            self.sendNotification(title, recipients, sender_address, str(last_version), str(new_version), url)

        self.repositories[i][key]["last_version"] = str(new_version)
        self.config.save_config()


if __name__ == "__main__":
    rn = ReleaseNotifier()
