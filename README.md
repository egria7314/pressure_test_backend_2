**Install**
=============
### Docker
```
sudo apt-get -y install apt-transport-https ca-certificates curl
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-key fingerprint 0EBFCD88
sudo apt-get update
sudo apt-get -y install docker-ce
sudo docker run hello-world
sudo apt-get install python-pip python-dev build-essential 
sudo pip install --upgrade pip
sudo groupadd docker
sudo usermod -aG docker $USER
```

### Docker-compose
```
sudo pip install docker-compose
```

**Prepare**
============= 

### Clone git repository
```
git clone git@dqa03:danny.lai/pressure_test_backend.git
```

### Branch to *develop*
```
git checkout develop
```

**Workflow Steps**
=============

### Add .env file
* 如果要串連壓力測試container與ＥＬＫ(log system)平台,　請注意此步驟.
* 與docker-compose檔案同一層的目錄, 新增一個檔案並命名為.env, 然後貼上下面的內容： 

```
DOCK_HOST=172.19.16.51 　# 自己電腦的ＩＰ
ELK_HOST=172.19.16.104   # log system的ＩＰ
```

### Rebuild dockerfile 
* If you change a Dockerfile or the contents of its build directory, run to rebuild it.

```
sudo docker-compose build
```

### Start service
```
sudo docker-compose up
```

### Delete old container

* If your container name is already exist, you should remove old one. 
```
sudo docker-compose stop 
sudo docker-compose rm 
``` 
or
```
sudo docker-compose down
```

**Work inside container**
=============

### Connect to container
```
sudo docker exec -ti "your-container-name" /bin/bash
```
* use __docker ps__ to see container's name
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

**Unit test**
=============

### Run unittest inside container
```
sudo docker-compose -f docker-compose.yml -f docker-compose.test.yml up
```

**Delete Docker**
=============
```
https://stackoverflow.com/questions/31313497/how-to-remove-docker-installed-using-wget
```