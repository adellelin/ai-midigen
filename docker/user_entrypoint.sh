#!/bin/bash
echo "Resolving user:"
if [ -z $ASUSER ]
then
    echo "  Running as root"
    exec "$@"
else
    adduser -uid $ASUSER --gecos "" --disabled-login user
    su -c "$@" user
fi

# example
# docker run -it -rm -v /home/mdp181/output/train_4bar_guitar_rock/:/output -e ASUSER=`id -u` midigen:latest python