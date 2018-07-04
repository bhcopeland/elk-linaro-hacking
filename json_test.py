from elasticsearch import Elasticsearch, helpers
import sys, json

es = Elasticsearch()

def load_json(directory):
    " Use a generator, no need to load all in memory"
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(filename,'r') as open_file:
                yield json.load(open_file)

helpers.bulk(es, load_json(sys.argv[1]), index='my-index', doc_type='my-type')
