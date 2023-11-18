from fastapi import FastAPI
import os
from routes import router
import subprocess


def setup_condor_config():
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


def create_app():
    setup_condor_config()

    app = FastAPI()
    app.include_router(router)
    return app
