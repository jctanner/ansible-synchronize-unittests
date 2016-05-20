#!/usr/bin/env python

'''
(Epdb) pprint(DeepDiff(self.final_task_vars, out_task_vars), indent=2)
{ 'dic_item_added': set([u"root['ansible_python_interpreter']"]),
  'dic_item_removed': set([ u"root['hostvars']['127.0.0.1']",
			    u"root['hostvars']['::1']",
			    u"root['hostvars']['localhost']"]),
  'iterable_item_added': { u"root['hostvars']['el6host']['groups']['all'][1]": u'::1',
			   u"root['hostvars']['el6host']['groups']['ungrouped'][1]": u'::1',
			   u"root['vars']['hostvars']['el6host']['groups']['all'][1]": u'::1',
			   u"root['vars']['hostvars']['el6host']['groups']['ungrouped'][1]": u'::1'}}
'''

import json
import os
import sys
import yaml

from deepdiff import DeepDiff
from pprint import pprint
from ansible.plugins.action.synchronize import ActionModule
from ansible.playbook.play_context import MAGIC_VARIABLE_MAPPING

# Getting the incoming and outgoing task vars

'''
import copy
safe_vars = {}
for k,v in task_vars.iteritems():
    if k not in ['vars', 'hostvars']:
        safe_vars[k] = copy.deepcopy(v)
    else:    
        sdata = str(v)
        newv = eval(sdata)
        safe_vars[k] = newv

import json
with open('task_vars.json', 'wb') as f:
    f.write(json.dumps(safe_vars, indent=2))
'''




class TaskMock(object):
    args = {'src': u'/tmp/deleteme', 'dest': '/tmp/deleteme'}
    async = None

class StdinMock(object):
    shell = None

class ConnectionMock(object):
    ismock = True
    #transport = 'ssh'
    transport = None
    _new_stdin = StdinMock()

class PlayContextMock(object):
    shell = None
    private_key_file = None
    become = False
    check_mode = False
    no_log = None
    diff = None

class ModuleLoaderMock(object):
    def find_plugin(self, module_name, mod_type):
        pass

class SharedLoaderMock(object):
    module_loader = ModuleLoaderMock()    

class SynchronizeTester(object):
    task = TaskMock()
    connection = ConnectionMock()
    play_context = PlayContextMock()
    loader = None
    templar = None
    shared_loader_obj = SharedLoaderMock()

    final_task_vars = None
    execute_called = False

    def _execute_module(self, module_name, task_vars=None):
        self.execute_called = True
        self.final_task_vars = task_vars
        #print("MOCKED EXECUTE MODULE!!!")
        #pprint(task_vars)
        return {}
    
    def runtest(self, fixturepath='fixtures/basic'):

	metapath = os.path.join(fixturepath, 'meta.yaml')
	with open(metapath, 'rb') as f:
	    fdata = f.read()
	test_meta = yaml.load(fdata)

	# load inital task vars
	invarspath = os.path.join(fixturepath, 
		test_meta.get('fixtures', {}).get('taskvars_in', 'taskvars_in.json'))
        with open(invarspath, 'rb') as f:
            fdata = f.read()
        in_task_vars = json.loads(fdata)

	# load expected final task vars
	outvarspath = os.path.join(fixturepath, 
		test_meta.get('fixtures', {}).get('taskvars_out', 'taskvars_out.json'))
        with open(outvarspath, 'rb') as f:
            fdata = f.read()
        out_task_vars = json.loads(fdata)

	# fixup the connection
	for k,v in test_meta['connection'].iteritems():
            setattr(self.connection, k, v)

	# fixup the hostvars
	for k,v in test_meta['hostvars'].iteritems():
            in_task_vars['hostvars'][k] = v

	# initalize and run the module
        SAM = ActionModule(self.task, self.connection, self.play_context, 
                           self.loader, self.templar, self.shared_loader_obj)
        SAM._execute_module = self._execute_module
        result = SAM.run(task_vars=in_task_vars)

	# run assertions
	for check in test_meta['asserts']:
            value = eval(check)
            assert value, check


        import epdb; epdb.st()



if __name__ == "__main__":
    SynchronizeTester().runtest()
