#!/bin/sh

APP_SERVER="pythonsh.duapp.com"
#APP_SERVER="s.qww.pw"

for i in "$@"; do
    for f in $(find "$i" -type f); do
        echo $f
        curl --data-binary @"$f" "http://$APP_SERVER/sync/$f"
    done
done
