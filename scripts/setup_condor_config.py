import os
import subprocess
# This script is run as part of the container startup process
# It is responsible for writing the condor_config file
# It expects the following environment variables to be set:
# CONDOR_HOST
# SCHEDD_HOST
# COLLECTOR_HOST
# POOL_PASSWORD (optional)


required_env_vars = ["CONDOR_HOST", "SCHEDD_HOST", "COLLECTOR_HOST"]
if not all(env_var in os.environ for env_var in required_env_vars):
    raise ValueError(
        f"Missing one or more of the following environment variables: {required_env_vars}"
    )

with open("/etc/condor/condor_config", "w") as f:
    for env_var in required_env_vars:
        f.write(f"{env_var} = {os.environ[env_var]}\n")
    f.write("SEC_PASSWORD_FILE = /etc/condor/password\n")
    f.write("SEC_CLIENT_AUTHENTICATION_METHODS = PASSWORD\n")

# use subprocess to condor_store_cred if pool_password is set
if "POOL_PASSWORD" in os.environ:
    subprocess.run(["condor_store_cred", "add", "-f", "/etc/condor/password", "-p", os.environ["POOL_PASSWORD"]])

