#!/bin/bash
# use mounted ansible.cfg and inventory at /etc/ansible

ansible-playbooks /usr/share/ansible/playbooks/$TYPE.yaml --tags $TAGS
