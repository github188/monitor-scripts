#!/bin/bash
BASEDIR=$(dirname $0)
cd $BASEDIR
./recomand_rpc_client $@ 2>&1| grep -q success && echo status=success || echo status=failed
