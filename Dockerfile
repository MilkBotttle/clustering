FROM ubuntu:18.04
USER root
RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN pip3 install ansible
COPY ./ansible/playbooks /usr/share/ansible/playbooks
COPY run_ansible.sh /opt/run_ansible.sh
ENTRYPOINT /opt/run_ansible.sh

