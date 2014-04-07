#!/bin/bash

#Use this to reset the servos
device1=$(~/smc_linux/SmcCmd -l | grep "18v7" -m 1 | awk -F'#' '{print $2'})
device2=$(~/smc_linux/SmcCmd -l | grep "18v7" -m 2 | tail -n1 | awk -F'#' '{print$2}')
~/smc_linux/SmcCmd -d "$device1" --resume
~/smc_linux/SmcCmd -d "$device2" --resume

