#!/bin/bash

var=$(mmcli --list-modems)
char=${var:41:2}

mmcli -m $char -d
mmcli -m $char -e

dhclient wwan0 -r # release

sleep 3
mmcli -m $char --simple-disconnect
sleep 5 

mmcli -m $char --simple-connect='apn=emmb,ip-type=ipv4v6'
sleep 5

dhclient wwan0
ip r d default dev wwan0
