from elasticsearch import Elasticsearch, TransportError
import requests
import xmlrpc.client
import simplejson as json
import yaml

index_mappings = {
  "settings": {
      "index.mapping.ignore_malformed": True,
      "dynamic": False
   },
   "mappings": {
   # testjobs
            "url": { "null_value": "null", "type": "text"  },
            "external_url": { "null_value": "null", "type": "text"  },
            "definition": { "null_value": "null", "type": "text"  },
            "name": { "null_value": "null", "type": "text"  },
            "build": { "null_value": "null", "type": "text"  },
            "environment": { "null_value": "null", "type": "text"  },
            "created_at": { "null_value": "null", "type": "text"  },
            "submitted_at": { "null_value": "null", "type": "text"  },
            "fetched_at": { "null_value": "null", "type": "text"  },
            "submitted": { "null_value": "null", "type": "text"  },
            "fetched": { "null_value": "null", "type": "text"  },
            "fetch_attempts": { "null_value": "null", "type": "text"  },
            "last_fetch_attempt": { "type":   "date", "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis" },
            "failure": { "null_value": "null", "type": "text"  },
            "can_resubmit": { "null_value": "null", "type": "text"  },
            "resubmitted_count": { "null_value": "null", "type": "text"  },
            "job_id": { "null_value": "null", "type": "text"  },
            "job_status": { "null_value": "null", "type": "text"  },
            "backend": { "null_value": "null", "type": "text"  },
            "testrun": { "null_value": "null", "type": "text"  },
            "target": { "null_value": "null", "type": "text"  },
            "target_build": { "null_value": "null", "type": "text"  },
            "parent_job": { "null_value": "null", "type": "text"  },
            "id": { "null_value": "null", "type": "text"  },
            "job": { "null_value": "null", "type": "text"  },
            "name": { "null_value": "null", "type": "text"  },
    #testruns (with dup fields removed)
            # "id": { "null_value": "null", "type": "text"  },
            # "tests_file": { "null_value": "null", "type": "text"  },
            # "metrics_file": { "null_value": "null", "type": "text"  },
            # "metadata_file": { "null_value": "null", "type": "text"  },
            # "log_file": { "null_value": "null", "type": "text"  },
            # "tests": { "null_value": "null", "type": "text"  },
            # "metrics": { "null_value": "null", "type": "text"  },
            # "completed": { "null_value": "null", "type": "text"  },
            # "datetime": { "type":   "date", "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis" },
            # "build_url": { "null_value": "null", "type": "text"  },
            # "job_status": { "null_value": "null", "type": "text"  },
            # "job_url": { "null_value": "null", "type": "text"  },
            # "resubmit_url": { "null_value": "null", "type": "text"  },
            # "data_processed": { "null_value": "null", "type": "text"  },
            # "status_recorded": { "null_value": "null", "type": "text"  },
            # "environment": { "null_value": "null", "type": "text"  },

   }
}

# default_mappings = {
#             "url": "https://qa-reports.linaro.org/api/testjobs/873176/",
#             "external_url": "https://validation.linaro.org/scheduler/job/1884786",
#             "definition": "https://qa-reports.linaro.org/api/testjobs/873176/definition/",
#             "name": "RPB OE boot dragonboard-410c morty 151",
#             "build": "53a0291",
#             "environment": "dragonboard-410c",
#             "created_at": "2018-06-29T08:48:40.814075Z",
#             "submitted_at": "2018-06-29T08:48:41.355514Z",
#             "fetched_at": "nul",
#             "submitted": "nul",
#             "fetched": "nul",
#             "fetch_attempts": 0,
#             "last_fetch_attempt": "2018-06-29T09:17:02.930161Z",
#             "failure": "nul",
#             "can_resubmit": "nul",
#             "resubmitted_count": 0,
#             "job_id": "1884786",
#             "job_status": "nul",
#             "backend": "https://qa-reports.linaro.org/api/backends/1/",
#             "testrun": "nul",
#             "target": "https://qa-reports.linaro.org/api/projects/74/",
#             "target_build": "https://qa-reports.linaro.org/api/builds/4802/",
#             "parent_job": "nul",
#    }

def get_all_results(url, results=[]):
    data = requests.get(url).json()
    if data['next']:
        return get_all_results(data['next'], results)
    else:
        return results+data['results']

### Elasticsearch
es = Elasticsearch()
index_name = "testjobs"
doc_type = "json-comments"
es.indices.create(index=index_name, ignore=400, body=index_mappings)

# multiple processes
# workers = 10
# manager = mp.Manager()
# q = manager.Queue(workers)
# pools = []

### qa-reports
#project_slug = "linux-mainline-oe"
project_slug = "linux-next-oe"
builds_to_check = 400
base_url = "https://qa-reports.linaro.org/api/"

project_url = "{}projects/?slug={}".format(base_url, project_slug)
projects = requests.get(project_url).json()
assert projects['count'] == 1
builds = requests.get(projects['results'][0]['builds']).json()

#### LAVA
username = "ben.copeland"
token = "xx"
hostname = "lkft.validation.linaro.org"  # lkft.validation.linaro.org
server = xmlrpc.client.ServerProxy("https://%s:%s@%s/RPC2" % (username, token, hostname))


for i in range(builds_to_check):
    testjobs = get_all_results(builds['results'][i]['testjobs'])
    # testruns = get_all_results(builds['results'][i]['testruns'])
    for job in testjobs:
        if job['job_status'] == 'Complete':
            if "lkft.validation.linaro.org" in job['external_url']:
                lava_job_id = job['external_url'].rsplit('/', 1)[-1]
                lava = server.results.get_testjob_suites_list_yaml(lava_job_id)
                print(server.results.get_testjob_metadata(lava_job_id))
                lava_info = json.dumps(yaml.load(lava), sort_keys=True)
                lava_json = json.loads(lava_info) # converts the json string to a dict.

                lavad = { 'lava' : lava_json[0]['name'] }
                job.update(lavad)
                job_json = json.dumps(job) # recovers json from the dict.
                print(json.dumps(job, indent=2))
        else:
            # Save without lava data
            job_json = json.dumps(job)
        es.index(index=index_name, doc_type=doc_type, body=job_json)


#es.index(index=index_name, doc_type=doc_type, body=testjobs_strip[0])
