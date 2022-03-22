#!/bin/bash

# ~/script/testnet3/restart_defid.sh
#
# Restart defid, rename debug.log.

~/.defi/defi-cli stop
sleep 5
mv ~/.defi/data/testnet3/debug.log ~/.defi/data/testnet3/$(date +%F-%H:%M)_debug.log
sleep 2
