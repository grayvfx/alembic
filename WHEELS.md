### Building PyAlembic Python Wheels via Github Actions

This describes how to build the python alembic library for linux via Github Actions. For local build instructions, see the [main readme](https://github.com/alembic/alembic).


### Building

The Github Action is currently set to be triggered manually via workflow_dispatch, as the build process can take up to 40 minutes. At the time of writing this documentation (28 July 2021) this is only possible on the master/main branch. This is adjustable in the wheels.yml file described below.

Instructions for how to trigger a manual workflow on github are [here](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow).

The general process is as follows:
1) The workflow file here: .github/workflows/wheels.yml triggers the accompanying actions: .github/actions/build-manylinux/python*/
2) The Dockerfile is used to pull the correct base image
3) A shell script is used to build pyalembic inside the Docker container, based on the latest code in the branch, consisting of two stages:
   1) A setup.py file is run which compiles pyalembic, collects dependencies and creates a wheel. The alembic version number is currently defined
   within this file and CMakeLists.txt.
   2) The python auditwheel module is run to repackage and correctly link all dependencies in the wheel file
4) The .whl is exported as a build artifact which is found when clicking on the workflow on the Actions tab in the Github repository.


### Installing

Once you have downloaded the build artifact:

```bash
pip install alembic-*.whl
```

Substitute alembic-*.whl for the full name of the file.

