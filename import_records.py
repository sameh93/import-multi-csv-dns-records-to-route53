import csv
import json
import boto3
import argparse

parser = argparse.ArgumentParser(description='CSV Route53 Importer')
parser.add_argument('--file', action='store', dest='file', required=True,
                    help='The CSV file to import')
parser.add_argument('--domain', action='store', dest='domain', required=True,
                    help='The domain name')
parser.add_argument('--zoneId', action='store', dest='zoneId', required=True,
                    help='The Hosted Zone ID')
parser.add_argument('-c', action='store', dest='comment', required=True,
                    help='Comment to associate with the batch update')
parser.add_argument('-d', action='store_true', dest='debugMode', default=False,
                    help='Debug mode. Will not make call to Route53 API')

args = parser.parse_args()

# Parsing the csv file to remove the ' Record' from each Record value 
class DnsRecord:
    def __init__(self, domainName, type, name, value, ttl):
        self.type = type.replace(" Record", "")
        self.name = name
        self.value = value
        self.ttl = ttl

        if (self.name == ""):
            self.name = domainName

        if (not(self.name.endswith(domainName))):
            self.name = self.name + "." + domainName

        self.changeAction = 'UPSERT'
        self.resourceRecords = [
            {'Value': self.value}
        ]

route53Client = boto3.client("route53")

if (not(args.domain.endswith("."))):
    domainName = args.domain + "."  #As it must end with `.`

print("Importing " + args.file + " Into Route53 Zone Id: " + args.zoneId)

file = open(args.file)
csv = csv.reader(file)

r53ChangeBatch = {
    "Comment": args.comment,
    "Changes": []
}

aRec = {}
txtRec = {}
mxRec = {}
srcRec = {}

for row in csv:
    if (row[0] == "Name"):
        continue

    record = DnsRecord(domainName, row[1], row[0], row[2], 1800)

    # Skipping NS and SOA records as they are part of the old DNS server
    if (record.type == "NS" or record.type == "SOA"): 
        continue

    # Grouping all A, TXT, MX and SRV records per zone name
    if (record.type == "A"):
        found = False
        for key in aRec.keys():
            if record.name == key:
                found = True

        if found == True:
            aRec[record.name].append({"Value": record.value})
        else:    
            aRec[record.name] = [{"Value": record.value}]
        
        continue

    if (record.type == "TXT"):
        if (not(record.value.startswith("\""))):
            record.value = "\"" + record.value
        if (not(record.value.endswith("\""))):
            record.value = record.value + "\""

        found = False
        for key in txtRec.keys():
            if record.name == key:
                found = True

        if found == True:
            txtRec[record.name].append({"Value": record.value})
        else:    
            txtRec[record.name] = [{"Value": record.value}]
    
        continue

    if (record.type == "MX"):
        found = False
        for key in mxRec.keys():
            if record.name == key:
                found = True

        if found == True:
            mxRec[record.name].append({"Value": record.value})
        else:    
            mxRec[record.name] = [{"Value": record.value}]

        continue

    if (record.type == "SRV"):
        found = False
        for key in srcRec.keys():
            if record.name == key:
                found = True

        if found == True:
            srcRec[record.name].append({"Value": record.value})
        else:    
            srcRec[record.name] = [{"Value": record.value}]

        continue
    
    # If not any of (A, TXT, MX and SRV) then push the record with its type directly
    # Mainly used for CNAME type
    r53ChangeBatch["Changes"].append(
        {
            "Action": record.changeAction,
            "ResourceRecordSet": {
                "Name": record.name,
                "Type": record.type,
                "TTL": record.ttl,
                "ResourceRecords": [
                    {"Value": record.value}
                ]
            }
        }
    )

# Pushing Group Records
if(bool(aRec)):
    for key in aRec.keys():
        r53ChangeBatch["Changes"].append(
        {
            "Action": record.changeAction,
            "ResourceRecordSet": {
                "Name": key,
                "Type": "A",
                "TTL": 300,
                "ResourceRecords": aRec[key]
            }
        }
    )

if(bool(txtRec)):
    for key in txtRec.keys():
        r53ChangeBatch["Changes"].append(
        {
            "Action": record.changeAction,
            "ResourceRecordSet": {
                "Name": key,
                "Type": "TXT",
                "TTL": 300,
                "ResourceRecords": txtRec[key]
            }
        }
    )

if(bool(mxRec)):
    for key in mxRec.keys():
        r53ChangeBatch["Changes"].append(
        {
            "Action": record.changeAction,
            "ResourceRecordSet": {
                "Name": key,
                "Type": "MX",
                "TTL": 300,
                "ResourceRecords": mxRec[key]
            }
        }
    )

if(bool(srcRec)):
    for key in srcRec.keys():
        r53ChangeBatch["Changes"].append(
        {
            "Action": record.changeAction,
            "ResourceRecordSet": {
                "Name": key,
                "Type": "SRV",
                "TTL": 300,
                "ResourceRecords": srcRec[key]
            }
        }
    )

if (not(args.debugMode)):
    route53Client.change_resource_record_sets(
        HostedZoneId=args.zoneId,
        ChangeBatch=r53ChangeBatch)
else:
    print("Error in DebugMode")

print("************************")
print("All csv records have been pushed to Route53 Zone Id: "+args.zoneId)
