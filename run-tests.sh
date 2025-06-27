#!/bin/bash
set -e

OAREPO_VERSION=${OAREPO_VERSION:-12}
PYTHON="${PYTHON:-python3.12}"
VENV=".venv"

export PIP_EXTRA_INDEX_URL=https://gitlab.cesnet.cz/api/v4/projects/1408/packages/pypi/simple
export UV_EXTRA_INDEX_URL=https://gitlab.cesnet.cz/api/v4/projects/1408/packages/pypi/simple

test_scripts() {
  local folder="$1/*"
  for entry in $folder
  do
    if [[ "$entry" == *.py ]]
    then
      module="$(echo "$entry" | sed -e 's|^\./||' -e 's|/|.|g' -e 's|\.py$||')"
      echo $module
      python -c "import $module"
    fi
  done
}

"${PYTHON}" -m venv $VENV
. $VENV/bin/activate
pip install -U setuptools pip wheel
pip install -e .
pip install "oarepo[tests,rdm]==${OAREPO_VERSION}.*" #correct version
pip install deepmerge

test_scripts "./pytest_oarepo"

pip install oarepo-requests
test_scripts "./pytest_oarepo/requests"

pip install oarepo-communities
test_scripts "./pytest_oarepo/communities"

pip install oarepo-vocabularies
test_scripts "./pytest_oarepo/vocabularies"