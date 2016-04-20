How to install and setup minUP.py on CentOS 7 with virtualenv
tested with python 2.7.6

```bash
$ useradd minion
$ passwd minion
$ yum update; yum -y install python-pip
$ pip install --upgrade pip
$ su - minion
$ MINUP_DEST=/opt/minUP
$ virtualenv /opt/minUP/.venv
$ echo "source /opt/minUP/.venv/bin/activate" >> ~/.bashrc
$ source /opt/minUP/.venv/bin/activate
```
Install Linux minup latest and ALL dependencies for minUP.py
```
$ cd /opt/minUP
$ git clone git@github.com:OliPelz/linminUP.git .
$ for pkg in numpy watchdog h5py cython biopython simplemysql configargparse ; do pip install $pkg; done 
```

Create a bash script we will call instead of minUP.py (since minUP.py expects running from its installation location)

```bash


```


