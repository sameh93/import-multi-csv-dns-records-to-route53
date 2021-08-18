# Import Multi csv dns records to AWS Route53

If you have exported infoblox csv file, this code can help you to import all the dns records inside a csv file to route53 all at once.

It skipps `NS` and `SOA` records.
It groups each of `A`, `TXT`, `MX` and `SRV` records together per zone `Name` value.

# Prerequisites:

- Python.
- AWS Access Key and Secret Access key with Route53 Admin permissions.
- Route53 hosted zone Id that you want to push the records to.
- Csv file that contains the dns records.

# Steps:

1. Export AWS Credentianls Keys on your shell.
2. Run python code

# Python command:
```
python import_records.py --file <PATH_TO_THE_FILE_NAME>.csv --domain <ROUTE53_DOMAIN_NAME> --zoneId <ROUTE53_HOSTED_ZONE_ID> -c "comment-for-the-import"
```

# Example:
1. You have a file called `example.csv` in the same directory of `import_records.py` 
2. DNS domain name is `example.com`
3. Route53 Zone Id `Z00200923BCJHIIBYO1AY` (Note: it's not available anymore, just for the elaboration)

```
python import_records.py --file example.csv --domain example.com --zoneId Z00200923BCJHIIBYO1AY -c "comment-for-the-import"
```

# Happy Migration :) 
