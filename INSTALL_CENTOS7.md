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
Install Linux minup latest and ALL dependencies for minUP.py. Dont forget to source your virtualenv before ```source /opt/minUP/.venv/bin/activate``` if not done already.

```
$ cd /opt/minUP
$ git clone git@github.com:OliPelz/linminUP.git .
$ for pkg in numpy watchdog h5py cython biopython simplemysql configargparse psutil ; do pip install $pkg; done 
```

Create a bash script we will call instead of minUP.py (since we use a custom python 2.7.6 which is not the system python - otherwise skip this step)

Fix minUP.py shebang to work with our custom virtualenv python (command tested for minUP 0.63).
You are likely to skip this step if your virtualenv python is the same as the system python (which in my example is not). Dont forget to source your virtualenv before ```source /opt/minUP/.venv/bin/activate```if not done already
```bash
$ MYPY=$(echo `which python`)
$ sed -i "s~\\/usr\/bin\/python~$MYPY~g" /software/minUP/minUP.py 
```

Now you can run it from anywhere as user minion
```bash
chmod +x /software/minUP/minUP.py
export PATH=/software/minUP:$PATH
cd 
minUP.py --help
```
