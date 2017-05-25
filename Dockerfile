FROM vivotekdqa/pressure_test_env:0.1

WORKDIR /home/dqa
RUN mkdir data
COPY . data/

WORKDIR /home/dqa/data
RUN ansible-playbook setup_of_python_modules.yml -i hosts

WORKDIR /home/dqa/