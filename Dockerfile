FROM htcondor/base:lts

# Update and install necessary packages
RUN yum -y update && yum upgrade -y
RUN yum install -y wget which

# Install Miniconda # Remove the Miniconda installer after installation
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
&& bash ~/miniconda.sh -b -p /miniconda && rm ~/miniconda.sh

# Create a new conda environment with Python 3.11.5
RUN /miniconda/bin/conda create -y -n py3115 python=3.11.5

# Activate the new environment without a subshell
ENV PATH=/miniconda/envs/py3115/bin:$PATH
ENV PYTHONPATH=/miniconda/envs/py3115/lib/python3.11/site-packages


COPY . /app
WORKDIR /app

# Install your Python dependencies
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry update

ARG VCS_REF=no_git_commit_passed_to_build
RUN chmod +x "scripts/entrypoint.sh"
ENTRYPOINT ["scripts/entrypoint.sh"]