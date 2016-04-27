#!/bin/bash
Pidfile=/software/minUP/minUP.pid

if [ -f $Pidfile ]
then
   echo "stopping minUP"
   Pid=`cat $Pidfile`
   kill -9 $Pid
   RETVAL=$?
   if [ $RETVAL -eq 0 ]
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

