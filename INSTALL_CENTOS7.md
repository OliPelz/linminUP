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
$ for pkg in numpy watchdog h5py cython biopython simplemysql configargparse psutil mlpy ; do pip install $pkg; done 
```

now we need to install some additional packages which cannot be found / compiled with pip and needed for minUP
first install the CentOS gsl devel package
```
yum install gsl-devel
```
 
next we need to install mlpy (from Github and not from sourceforge because we need the latest version)
```
mkdir ~/src
cd $_
git clone https://github.com/lukauskas/mlpy.git
cd mlpy
python setup.py install
```
finally install ```pygsl``` version ```2.2.0``` from sourceforge
TODO

Create a bash script we will call instead of minUP.py (since we use a custom python 2.7.6 which is not the system python - otherwise skip this step)

Fix minUP.py shebang to work with our custom virtualenv python (command tested for minUP 0.63).
You are likely to skip this step if your virtualenv python is the same as the system python (which in my example is not). Dont forget to source your virtualenv before ```source /opt/minUP/.venv/bin/activate```if not done already
```bash
$ MYPY=$(echo `which python`)
$ sed -i "s~\\/usr\/bin\/python~$MYPY~g" /opt/minUP/minUP.py 
```

Now you can run it from anywhere as user minion
```bash
chmod +x /opt/minUP/minUP.py
export PATH=/opt/minUP:$PATH
cd 
minUP.py --help
```


As I dont want to use minUP.py as a server systemd or init script but want users to conveniently start/stop the script I wrap/put it in the following bash script

/opt/minUP/start_minUP.sh:
```bash
#!/bin/bash
Pidfile=/opt/minUP/minUP.pid

# read in pid file
if [ -f $Pidfile ]
   echo 'seems like the minUP process is already running. try script stop_minUP.sh'
   exit 1
fi

nohup minUP.py $@ &> /dev/null &
if [ $? eq 0]
then
  echo $! > $Pidfile
fi
```

stop_minUP.sh
```
#!/bin/bash
Pidfile=/opt/minUP/minUP.pid

if [ -f $Pidfile ] ; then
   echo "stopping minUP"
   kill -15 $Pid
   if [ $? eq 0 ]
   then
     echo "...done"
   else 
     echo "...error while trying to stop minUP"
     exit 0
   fi
   rm -f $Pidfile
   exit 0
else
   echo "Cannot stop minUP- no Pidfile found, process seems not to run"
   exit 1
fi
```

make executable
```
chmod +x /opt/minUP/start_minUP.sh
chmod +x /opt/minUP/stop_minUP.sh
```


example to use the scripts
in my example I can access a shared nfs mount both on the server minion is running and also locally under ```/mnt/data```
I have uploaded the minotour testdata into ```/mnt/data/minion-test-data-set```
so everything can be done locally:
```
$ echo "
[Defaults]
mysql-host=192.168.1.10
mysql-username=dykvandyke
mysql-password=xxxx
mysql-port=3306
align-ref-fasta=/mnt/data/minion-test-data-set/demo_data_set/reference
watch-dir=/home/mnt/data/minion-test-data-set/demo_data_set/downloads
minotour-username=dykvandyke
#minotour-sharing-usernames=
flowcell-owner=olip
#output-dir=
#run-number=
" > /mnt/data/minion.config
```
Now start the run locally using ssh
```
MINOUT=/mnt/data/minUP-`date +'%s'`
ssh minion@server mkdir $MINOUT
ssh minion@server /opt/minUP/start_minUP.sh -e $MINOUT -a /home/minion/minoTour-data/minup_posix.config
```

now finally run using a custom path config file and output dir 
```
/software/minUP/minUP.py -d  -a /home/minion/minoTour-data/minup_posix.config -e /home/minion/minoTour-output-today
```
