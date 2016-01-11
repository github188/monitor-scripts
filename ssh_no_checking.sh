#!/bin/sh

# set as GIT_SSH ENV so that git could clone repo without ssh Hostkey confirmation
exec /usr/bin/ssh -o StrictHostKeyChecking=no "$@"
