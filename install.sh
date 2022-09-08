pip install -y pytest cwltool pyyaml arvados-python-client

# For fixing bug in libraries
pip uninstall pycurl
export PYCURL_SSL_LIBRARY=nss
pip install --compile --install-option="--with-nss" --no-cache-dir pycurl==7.44