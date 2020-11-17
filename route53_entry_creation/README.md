# Introduction

The script automates the process of creating/modifying the AWS Route 53 entries via a python script in which Boto3(Amazon Web Services SDK for Python) has been used.The motive to reduce the time and effort compared to when Route 53 entries are created through AWS console(Connect with VPN(if applicable) -> Login into AWS Console ->Select R53 service -> Switch to desired hosted zone -> Create entry)

![Boto3](https://user-images.githubusercontent.com/50901044/98013545-812e1600-1e20-11eb-9603-caed48a5e6ae.jpg)



For more info refer, https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html

## Prerequisites

* Python should be installed in the system (v2.7).
* To perform operations on AWS Route53, if you are using an EC2 machine to host the script make sure the required AWS role is attached to that EC2 or if you are using this script in local then make sure the IAM user has necessary permissions.

## Example to run the script:

* Execute command as,

```python
python create_route53_entry.py
```

## How it Works?
* Script prompts for following user inputs:
    - Action : Here you need to enter which action you want to perform in R53. There are 3 choices available for the same:
            1) Create: Creates a new resource record set
            2) Delete: Deletes an existing resource record set.
            3) Upsert: If a resource record set doesn't already exist, Route 53 creates it. If a resource record set does exist, Route 53 updates it with the values in the request.
    - HostedZoneId : Enter the ID of the hosted zone that contains the resource record sets that you want to change
    - Name : Here you need specify the name of the record that you want to create, update, or delete. Make sure to mention full URL with domain name (eg. test1.mycompany.com)
    - Value : Here you need to specify the current or new DNS record value.
    - Type : Enter the DNS record type (CNAME/A).
  
<img width="685" alt="Screenshot " src="https://user-images.githubusercontent.com/50901044/98010591-e253ea80-1e1c-11eb-82d9-0b8adbe439f2.png">

    


