import xmlrpc.client
username = "ben.copeland"
token = "xxx"
hostname = "lkft.validation.linaro.org"  # lkft.validation.linaro.org
server = xmlrpc.client.ServerProxy("https://%s:%s@%s/RPC2" % (username, token, hostname))
#print(server.system.listMethods())

print(server.results.get_testjob_suites_list_yaml('176271'))

foo = (server.results.results.get_testcase_results_yaml('176271', '356892', '2_kselftest-vsyscall-mode-native'))

import json

print(json.dumps(foo, indent=1))

# str = "https://lkft.validation.linaro.org/scheduler/job/308924"
# print(str.rsplit('/', 1)[-1])
