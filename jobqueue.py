#!/usr/bin/python3

import xmlrpc.client
import argparse
from elasticsearch import Elasticsearch, TransportError
from datetime import datetime

index_mappings = {
  "settings": {
      "index.mapping.ignore_malformed": True,
      "dynamic": False
   },
}

def main():
    es = Elasticsearch([
    {'host': 'localhost', 'port': 9999},
    ])
    index_name = "jobqueue"
    doc_type = "json-comments"
    es.indices.create(index=index_name, ignore=400, body=index_mappings)

    parser = argparse.ArgumentParser(description='Get a LAVA server job queue')

    parser.add_argument("-s", "--server", type=str,
                        help="LAVA server to get the info from")
    parser.add_argument("-t", "--token", type=str,
                        help="User authentication token")
    parser.add_argument("-u", "--username", type=str,
                        help="Username to use for query")
    options = parser.parse_args()

    server = xmlrpc.client.ServerProxy("https://%s:%s@%s/RPC2" % (options.username, options.token, options.server))

    jobs = server.scheduler.pending_jobs_by_device_type()
    for k, v in jobs.items():
        doc = { 
          'device': {
            'type': k,
	    'status': v,
          },
        'timestamp': datetime.now() 
}
        #jobs.update(doc)
        print(doc)
        es.index(index=index_name, doc_type=doc_type, body=doc)

if __name__ == '__main__':
    main()
