set -eox

pip install pytest cwltool pyyaml arvados-python-client

# For fixing bug in libraries
pip uninstall pycurl
export PYCURL_SSL_LIBRARY=openssl
pip install --compile  --no-cache-dir pycurl==7.44