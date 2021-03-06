import unittest
import time
from utils import restart_rabbitmq,start_rabbitmq,stop_rabbitmq,metax_on,metax_off,restart_httpd,delete_file
import ida.ida as ida
import metax.metax as metax
from config.config import load_config_variables

from ida.ida_accounts_initialise import initialize_test_account
from pprint import pprint



# loading configuration variables
conf = load_config_variables()
user = conf['IDA_USER']
password = conf['IDA_PASS']
host = conf['IDA_HOST']



class UnitTestMain(unittest.TestCase):

    """
    Main class intializing the unittest environment:
    - setting up the variables
    - Initializing the test data
    """


    @classmethod
    def setUpClass(self):

        print("-----" * 20)
        print("\t\tInitialize IDA test accounts")
        print("-----" * 20)

        initialize_test_account(user, password, host)
        metax_on()

        print("-----" * 20)
        print("\t\tIDA - Metax tests")
        print("-----" * 20)
        print("\t1. Freeze file")
        print("\t2. Unfreeze file")
        print("\t3. Delete file")
        print("-----" * 20)
        print("-----" * 20)
        # instead of setting a signal handler for ctrl+c,
        # call teardown class to make sure everything is clean


    @classmethod
    def tearDownClass(cls):
        metax_off()
        # flush all the test files 
        pname = ["A", "B", "B"]
        for project in pname:
            metax.flush_project('Project_'+project)
        print("Flush test files from metax")

    def setUp(self):
        self.OK = [200,201,202,203]
        self.FAIL = [400,401,404]


    def tearDown(self):
        pass

class TestIDAMetax(UnitTestMain):
    """
    - IdaAppTests class performing all the test cases
    """
    @classmethod
    def setUpClass(self):
        super(TestIDAMetax, self).setUpClass()

    #@unittest.skip("reason for skipping")
    def testFreezeFile(self):


        data = {
            "project": "Project_A",
            "pathname": "/2017-10/Experiment_3/test01.dat"
        }
        user = 'PSO_Project_A'
        status, res = ida.freeze_file(user, data)
        self.assertIn(status, self.OK, 'freeze fails')
        pid = res["pid"]
        time.sleep(15)

        # Retrieve frozen nodes associated with Action
        status, node = ida.get_frozen_node_action(user, pid)
        self.assertIn(status, self.OK, 'check if node is empty')
        id = node[-1]["node"]

        #Looking for a file in metax
        #status = metax.get_file(id)
        #self.assertIn(status, self.OK, 'Not found in metax')


    #@unittest.skip("reason here")
    def testUnFreezeFile(self):

        data = {
            "project": "Project_A",
            "pathname": "/2017-10/Experiment_5/test02.dat"
        }

        user = 'PSO_Project_A'
        status, res = ida.freeze_file(user, data)
        self.assertIn(status, self.OK, 'freeze fails')


        pid = res["pid"]
        node = res["node"]


        time.sleep(25)
        # Retrieve set of actions
        
        data1 = {
            "status": "completed",
            "project": "Project_A"
        }

        status, actions = ida.get_actions(user, data1)
        self.assertIn(status, self.OK, 'actions retrieval fails')


        pid = actions["user" == "PSO_Project_A"]["pid"]
        nodeID = actions["user" == "PSO_Project_A"]["node"]

        # Retrieve action details of frozen file
        status, actions = ida.get_specific_actions(user, data1, pid)
        self.assertIn(status, self.OK, 'actions retrieval fails')

        # Unfreeze file
        data2 = {
            "node": nodeID,
            "project": "Project_A",
            "pathname": "/2017-10/Experiment_5/test02.dat"
        }
        status, res = ida.unfreeze_file(user, data)
        self.assertIn(status, self.OK, 'file unfreeze fails')
        
        


    #@unittest.skip("skipping..")
    def testDeleteFile(self):
        """
                Delete test case:
                - freezes the file
                - Delete the frozen file
                """
        
        #User C freeze experiment 6/test02.dat
        data = {
            "project": "Project_A",
            "pathname": "/2017-10/Experiment_4/test03.dat"
        }

        user = 'PSO_Project_A'
        status, res = ida.freeze_file(user, data)
        self.assertIn(status, self.OK, 'freeze fails')
        
        time.sleep(15)
        
        #Delete frozen folder
        nodeId = res['node']
        data = {
            "node": nodeId,
            "project": "Project_A",
            "pathname": "/2017-10/Experiment_4/test03.dat"
        }
        status = ida.delete_file(user, data)
        self.assertIn(status, self.OK, 'delete fails')
        
    

if __name__ == '__main__':
    unittest.main(verbosity = 2)
