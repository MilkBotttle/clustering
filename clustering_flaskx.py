import configparser
import docker
import json
import os
from flask import Flask
from flask_restx import Resource, Api
# from ansible.playbook import PlayBook
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible import context

app = Flask(__name__)
api = Api(app)
docker_client = docker.from_env()

BASEPATH="/var/lib/clustering"

def execute_playbook(playbook_path, options):
    playbook_path = "./ansible/playbooks/hello.yaml"
    inventory_path = "hosts"

    context.CLIARGS = ImmutableDict(tags={}, listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
                    module_path=None, forks=100, remote_user='xxx', private_key_file=None,
                    ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=False,
                    become_method='sudo', become_user='root', verbosity=True, check=False, start_at_task=None)

    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=['inventory'])
    import pdb;pdb.set_trace()
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    executor = PlaybookExecutor(
                playbooks=[playbook_path], inventory=inventory, variable_manager=variable_manager, loader=loader, passwords={})

    results = executor.run()
    return results

def create_clustering_record(path):
    if not os.path.isdir(path):
        os.mkdir(path)

def gen_ansible_cfg(path):
    config = configparser.ConfigParser()
    config['defaults']['log_path']="%s/ansible.log" % (path)
    config['ssh_connection']['ssh_args'] = "-o StrictHostKeyChecking=no"
    with open(path, 'w') as configfile:
        config.write(configfile)

def create_file(path, text):
    with open(path, "wt") as text_file:
        print(text, file=text_file)

@api.route('/<string:cluster_type>/<uuid>')
class Clustering(Resource):
    def get(self, cluster_type, uuid):
        path="%/%s/%s/state" % (BASEPATH, cluster_type, uuid)
        with open(path, r) as json_file:
            state = json.load(path)
        return state

    def post(self, cluster_type, uuid):
        path = "%s/%s/%s" % (BASEPATH, cluster_type, uuid)
        data = api.payload
        create_clustering_record(path)
        # Create ansible cfg
        gen_ansible_cfg(path)
        # Create inventory
        hosts = data['hosts']
        create_file("%s/hosts" % path, hosts)

        # Run container
        container_name = "%s-%s" % (cluster_type, uuid)
        environment={"TYPE": cluster_type,
                     "TAGS": "create"}
        docker_client.containers.run(
            image='clustering',
            name=container_name,
            volumes={path: {'bind': '/etc/ansible', 'mode': 'rw'}},
            environment=environment,
            network_mod='host',
            detach=True)
        return {}


if __name__ == '__main__':
    app.run(debug=True)
