#!/bin/bash
Pidfile=/software/minUP/minUP.pid

# read in pid file
if [ -f $Pidfile ]
then
   echo 'seems like the minUP process is already running. try script stop_minUP.sh'
   exit 1
fi

nohup /software/minUP/minUP.py $@ # &> /dev/null &
RETVAL=$?
[ $RETVAL -eq 0 ] && echo $! > $Pidfile

