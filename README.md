# Condor Metrics
### Prometheus metrics about the state of condor queue including
* Idle queue
* Idle jobs

# Local Install on MacOS
* Install [Homebrew](https://brew.sh/)
* Use the install script here [install_conda_and_htcondor.sh](scripts%2Finstall_conda_and_htcondor.sh)

### Set up the following env variables 
These will  point to condor collector and socks proxy
* SOCKS_PROXY_PORT
* SOCKS_PROXY
* COLLECTOR_HOST



# Docker

## Colima
* brew install colima
* docker client from rancher desktopt
* set --export --prepend PATH "/Users/<username>/.rd/bin"
* ln -s /Users/bsadkhin/.colima/docker.sock /var/run/docker.sock

## Podman
* brew install podman-compose
* brew install podman
# PYCHARM
* Use `localhost/condor_metrics:test` with colima
* go to Help | Find Action | Registry
* disable python.use.targets.api
* recreate the interpreter from scratch
* build and use this image ` docker build . -t localhost/condor_metrics:test`

# VSCODE
* Setting: Dev › Containers: Docker Path
* Path: `/opt/homebrew/bin/podman`
* Setting: Dev › Containers: Docker Compose Path
* Path: `/opt/homebrew/bin/podman-compose`
