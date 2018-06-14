#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2017, Wayne Witzel III <wayne@riotousliving.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: tower_credential_type
author: "WWT Team"
version_added: "2.7"
short_description: create, update, or destroy Ansible Tower Credential Type.
description:
    - Create, update, or destroy Ansible Tower Credential Type. See
      U(https://www.ansible.com/tower) for an overview.
options:
    name:
      description:
        - Name of Custom Credential type
      required: True
    description:
      description:
        - Enter an arbitrary description as appropriate (optional)
    state:
      description:
        - Desired state of the resource.
      default: "present"
      choices: ["present", "absent"]
    kind:
      description:
        - Kind of Custom Credential
      choices: ['ssh','vault','net','scm','cloud','insights']
      required: True
    inputs:
      description:
        - specify an input schema which defines a set of ordered fields for that type.
    injectors:
      description:
        - enter environment variables or extra variables that specify the values a credential type can inject.
extends_documentation_fragment: tower
'''


EXAMPLES = '''
- name: Add custom credential type
  tower_credential_type:
    name: Custom Credentials
    description: Credential Type Description
    kind: cloud
    state: present
    tower_config_file: "~/tower_cli.cfg"
    inputs:
      fields:
        - type: string
          id: username
          label: Username
        - type: string
          id: password
          label: Password
          secret: true
        - type: string
          id: url
          label: Base URL
      required:
        - username
        - password
        - url
    injectors:
      env:
        CUSTOM_USERNAME: "{{'{{'}}username{{'}}'}}"
        CUSTOM_PASSWORD: "{{'{{'}}password{{'}}'}}"
        CUSTOM_URL: "{{'{{'}}url{{'}}'}}"
'''

from ansible.module_utils.ansible_tower import tower_argument_spec, tower_auth_config, tower_check_mode, HAS_TOWER_CLI

try:
    import tower_cli
    import tower_cli.utils.exceptions as exc

    from tower_cli.conf import settings
except ImportError:
    pass


def main():
    argument_spec = tower_argument_spec()
    argument_spec.update(dict(
        name=dict(required=True),
        description=dict(),
        state=dict(choices=['present', 'absent'], default='present'),
        kind=dict(required=True, choices=['ssh', 'vault', 'net', 'scm', 'cloud', 'insights']),
        inputs=dict(type='dict'),
        injectors=dict(type='dict'),
    ))

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    if not HAS_TOWER_CLI:
        module.fail_json(msg='ansible-tower-cli required for this module')

    name = module.params.get('name')
    state = module.params.get('state')
    json_output = {'credential_type': name, 'state': state}

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        tower_check_mode(module)
        ct = tower_cli.get_resource('credential_type')

        params = module.params.copy()
        params['create_on_missing'] = True
        try:
            if state == 'present':
                result = ct.modify(**params)
                json_output['id'] = result['id']
            elif state == 'absent':
                result = ct.delete(**params)
        except (exc.ConnectionError, exc.BadRequest, exc.NotFound) as excinfo:
            module.fail_json(msg='Failed to update job template: {0}'.format(excinfo), changed=False)

    json_output['changed'] = result['changed']
    module.exit_json(**json_output)


from ansible.module_utils.basic import AnsibleModule
if __name__ == '__main__':
    main()
