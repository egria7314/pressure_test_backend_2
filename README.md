## Install
### Docker
* sudo apt-get -y install apt-transport-https ca-certificates curl
* curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
* sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
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

### Build image and also create container
```
docker-compose run -d web
```

### Start service
```
docker-compose up
```

## Add code to container
### SSH to container
```
docker exec -ti "your-container-name" /bin/bash
```
* use *docker ps* to see container's name
* ex: pressuretestbackend_web_1

### Activate virtual env
```
root@01739d768e32:/home/dqa# cd code
root@01739d768e32:/home/dqa/code# source env/bin/activate
(env) root@01739d768e32:/home/dqa/code#
```

### Change to project working directory
```
(env) root@01739d768e32:/home/dqa/code# cd ../data
(env) root@01739d768e32:/home/dqa/data# cd pressure_test/
(env) root@01739d768e32:/home/dqa/data/pressure_test# 
```

### Delete old container

* If your container name is already exist, you should remove old one. 
```
docker-compose stop 
docker-compose rm 
``` 