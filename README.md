## Install
### Docker
* sudo apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl
* curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
* sudo add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) \
    stable"
* sudo apt-key fingerprint 0EBFCD88
* sudo apt-get update
* sudo apt-get -y install docker-ce
* sudo docker run hello-world
* sudo apt-get install python-pip python-dev build-essential 
* sudo pip install --upgrade pip
 
## Workflow Steps

### Clone git repository
```
git clone git@dqa03:danny.lai/pressure_test_backend.git
```

### Branch to develop
```
git checkout develop
```

### Build image
```
docker build -t pressure_test_backend:0.1 .
```

### Create container
```
docker run -d -ti --name django -p 8000:8000 -v "$PWD"/pressure_test:/code/pressure_test pressure_test_backend:0.1 /bin/bash

```

### SSH to container
```
docker exec -ti django /bin/bash
```

### Activate virtual env
```
root@01739d768e32:/home/dqa# cd code
root@01739d768e32:/home/dqa/code# source env/bin/activate
(env) root@01739d768e32:/home/dqa/code#
```

### Happy coding
* You can enjoy your coding from these steps