import json
import os
from datetime import datetime
from bson.json_util import dumps, loads

from pymongo import MongoClient

from config import Config


client = MongoClient(Config.HOSTNAME, Config.PORT)
db = client[Config.DATABASE]


def get_attackers(vm_id):
    vm = db.virtual_machines.find_one(filter={"vm_id": vm_id})
    if not vm:
        return []

    vm_tags = vm.get("tags")
    if not vm_tags:
        return []

    fw_rules = db.firewall_rules.find({"dest_tag": {"$in": vm_tags}})
    source_tags = set()
    for rule in fw_rules:
        source_tags.add(rule.get("source_tag"))
    attackers = db.virtual_machines.find({"tags": {"$in": list(source_tags)}},
                                         projection={"vm_id": True, "_id": False})
    result = []
    for vm in loads(dumps(attackers)):  # attackers looks like [{"vm_id": "vm-12121"}, {"vm_id": "vm-13131"}]
        result.append(vm["vm_id"])

    return result


def count_objects(collection_name):
    collection = db[collection_name]
    return collection.count_documents({})


def get_average(collection_name, value):
    pipeline = [{"$group": {"_id": 1, "total": {"$avg": "${}".format(value)}}}]
    average = loads(dumps(db[collection_name].aggregate(pipeline)))[0].get("total")
    return average


def add_stat(duration):
    return db["stats"].insert_one({"duration": duration, "timestamp": datetime.utcnow()})


def get_stats():
    num_of_requests = count_objects("stats")
    if num_of_requests > 0:
        avg_time_in_ms = get_average("stats", "duration") * 1000
    else:
        avg_time_in_ms = 0

    result = {"vm_count": count_objects("virtual_machines"),
              "request_count": num_of_requests,
              "average_request_time": avg_time_in_ms
              }

    return result


def setup_db(json_file_path=Config.PATH_TO_INITIAL_DATA_SET,
             clear_stats=Config.CLEAR_STATS_EVERY_RELOAD,
             reload_db=Config.SETUP_NEW_CLOUD_ENV_EVERY_RELOAD):
    if clear_stats:
        db["stats"].delete_many({})

    if reload_db:
        db["virtual_machines"].delete_many({})
        db["firewall_rules"].delete_many({})

    if os.path.exists(json_file_path):
        with open(json_file_path) as json_file:
            try:
                data = json.load(json_file)
                vms = data.get("vms", [])
                fw_rules = data.get("fw_rules", [])
                if len(vms) > 0:
                    db["virtual_machines"].insert_many(vms)
                if len(fw_rules) > 0:
                    db["firewall_rules"].insert_many(fw_rules)
            except Exception as e:
                print("Error: {}".format(str(e)))
