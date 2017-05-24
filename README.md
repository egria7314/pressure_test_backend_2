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

### Build image
```
docker build -t pressure_test_backend:0.1 .
```

### Create container and sharing folder
```
docker run -d -ti --name django -p 8000:8000 -v "$PWD":/code/pressure_test pressure_test_backend:0.1 /bin/bash

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

### Run server
```
(env) root@01739d768e32:/home/dqa/code# cd pressure_test/pressure_test
(env) root@01739d768e32:/home/dqa/code/pressure_test/pressure_test# python manage.py runserver 0.0.0.0:8000
```

### Develop your code

* After develop or create files on your local host,
* you can repeat steps from *build image* to *run server*

### Delete old container

* If your container name is already exist, you should remove old one. 
```
docker stop django
docker rm django
``` 