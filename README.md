# git-release-notifier - A git release/tag notification script

This script will send you an email, when a new release/tag is published on GitHub or any other given Git repo.

To configure it just look at the `config.yml.examlpe` file and modify it to your needs.

There is also a docker image available for this script. To run a container use the following command:

```
docker run -v $(pwd)/config.yml:/app/config.yml ghcr.io/merlinschumacher/git-release-notifier:main
```
