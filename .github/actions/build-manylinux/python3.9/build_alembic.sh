#!/bin/bash

# Debugging options
set -e -x

# Build Alembic
cd /github/workspace/  # Default location of packages in docker action
python3.9 setup.py bdist_wheel
python3.9 -m pip show alembic

# Bundle external shared libraries into the wheels
find . -type f -iname "*-linux*.whl" -execdir sh -c "auditwheel repair '{}' -w ./ --plat '${PLAT}' || { echo 'Repairing wheels failed.'; auditwheel show '{}'; exit 1; }" \;

# Install our wheel
WHEEL=$(find . -type f -iname "*-manylinux*.whl")
echo "Successfully built wheel, running a test pip install: $WHEEL"
python3.9 -m pip install --force-reinstall "$WHEEL"

python3.9 -m pip show alembic

echo "$PYTHONPATH"

# make sure python has access to the alembic libraries
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.9/site-packages

# Run tests before releasing build
cd ./python/PyAlembic/Tests
python3.9 -m unittest discover