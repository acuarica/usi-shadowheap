#!/bin/sh



SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  TARGET="$(readlink "$SOURCE")"
  if [[ $SOURCE == /* ]]; then
    echo "SOURCE '$SOURCE' is an absolute symlink to '$TARGET'"
    SOURCE="$TARGET"
  else
    DIR="$( dirname "$SOURCE" )"
    echo "SOURCE '$SOURCE' is a relative symlink to '$TARGET' (relative to '$DIR')"
    SOURCE="$DIR/$TARGET" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
  fi
done
echo "SOURCE is '$SOURCE'"
RDIR="$( dirname "$SOURCE" )"
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
if [ "$DIR" != "$RDIR" ]; then
  echo "DIR '$RDIR' resolves to '$DIR'"
fi
echo "DIR is '$DIR'"


ROOT=$DIR

CLASS=$1
PACKAGE=ch.usi.inf.sape.frheap.heaptests.`echo $CLASS | tr '[A-Z]' '[a-z]'`
MAINCLASS=$PACKAGE.$CLASS

CP=$ROOT/bin/
AGENT=$ROOT/../fr-heapagent/build/libfrheapagent.jnilib
PROXYBCP=$ROOT/../fr-heapagent/build/


cd $ROOT/../fr-heapagent
make

cd -

if [ $? -ne 0 ]; then
	echo "Finished with errors"
	exit	
fi

#cd ../fr-heapagenttest

mkdir -p logs
mkdir -p db
rm db/*

kill_server () {
	if [ -f "$1" ]; then
		local PID=$(< "$1")
		[ -n "$PID" ] && kill -KILL $PID 2> /dev/null
		rm -f "$1"
	fi
}

SERVER_PID_FILE=server.pid

FR=$ROOT/../fr-instr
FRLIB=${FR}/lib

JARS=/Users/luigi/Downloads/jar/avrora-cvs-20091224.jar

#echo $FRLIB

java -cp ${FR}/bin:${FRLIB}/log4j-1.2.17.jar:${FRLIB}/asm-debug-all-4.0.jar:$FR/resources:$JARS \
	ch.usi.inf.sape.frheap.server.FrHeapInstrumentServer > logs/server-output.log &

# print pid to the server file
if [ -n "${SERVER_PID_FILE}" ]; then
	echo $! > ${SERVER_PID_FILE}
fi

sleep 1

EVENTSPERSAMPLE=500
XMS=32m
XMX=128m

JOPT="-Xms$XMS -Xmx$XMX"

#JDEBUG="-Xcheck:jni -Xdiag -verbose:jni -verbose:class"

java $JOPT -Xverify:none -agentpath:$AGENT=$EVENTSPERSAMPLE -Xbootclasspath/a:$PROXYBCP -cp $CP "$MAINCLASS"

#java -Xverify:none -agentpath:$AGENT=20000 -Xbootclasspath/a:$PROXYBCP -jar lib/dacapo-9.12-bach.jar avrora

kill_server $SERVER_PID_FILE

#cat db/tlog.*.log > db/tlog.log
#cat db/fr.*.log > db/fr.log
#cat $1
#| sort --numeric-sort --key=1 --field-separator=":" 

#./parsedb.py

exit

SUMMARY=csv/summary-$CLASS-$EVENTSPERSAMPLE-Xms$XMS-Xmx$XMX.txt

echo "# Config" > $SUMMARY
echo "#   Running class                 : $CLASS" >> $SUMMARY 
echo "#   Events per sample             : $EVENTSPERSAMPLE" >> $SUMMARY
echo "#   Initial Java heap size (-Xms) : $XMS" >> $SUMMARY
echo "#   Maximum Java heap size (-Xmx) : $XMX" >> $SUMMARY
echo "#" >> $SUMMARY

cat db/summary.txt >> $SUMMARY
