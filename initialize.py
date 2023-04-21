import boto3
import json
import os
import requests
from io import BytesIO
from botocore.exceptions import ClientError

# getting credentials from cres files
resource_creds = json.load(open('resources.json', 'r'))

# creating a resource
dynamodb = boto3.resource( 'dynamodb',
                        aws_access_key_id=resource_creds['aws_access_key_id'],
                        aws_secret_access_key=resource_creds['aws_secret_access_key'],
                        aws_session_token=resource_creds['aws_session_token'],
                        region_name='us-east-1') 

# cleanup 
for tablename in ['login', 'music', 'subscription']:
    table = dynamodb.Table(tablename)
    
    # delete the table
    try:
        table.delete()
        
        # Wait for the table to be deleted
        table.wait_until_not_exists()
    except ClientError:
        print("{} does not exist in database. Moving Forward.".format(tablename))

with open('a1.json', 'r') as f: #reading the file to update the music table 
    data = json.load(f)
    
with open('users.json', 'r') as u: #reading the file to update the users table 
    users = json.load(u)

with open('subscription.json', 'r') as u: #reading the file to update the users table 
    subscriptions = json.load(u)
#--------------------------------------------------------------------------------
# creating the music table from python
table_name = 'music'
table = dynamodb.create_table(
    TableName=table_name,
    KeySchema=[
        {
            'AttributeName': 'title',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'artist',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'title',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'artist',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait for the table to be created
table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

print(f"Table '{table_name}' has been created successfully.")


artists = [] # to avoid duplicacy
songs = data['songs']

#creating a resource object for an s3 bucket
s3_bucket = boto3.resource( 's3',
                        aws_access_key_id=resource_creds['aws_access_key_id'],
                        aws_secret_access_key=resource_creds['aws_secret_access_key'],
                        aws_session_token=resource_creds['aws_session_token'],
                        region_name='us-east-1') 

table = dynamodb.Table(table_name) #readin the music table


# cleanup
# clearing the bucket before adding the images
s3_images_bucket = s3_bucket.Bucket('images-artist')
s3_images_bucket.objects.delete()


for song in songs:
    table.put_item(Item=song) 
    print('Data Inserted : ' + song['artist'] + " - " + song['title'])
    
    artist = song['artist']
    
    if artist not in artists:
        url = song['img_url']
        response = requests.get(url) 
        filename = artist + ".jpg"
        file_content = BytesIO(response.content)
        artists.append(artist)
        
        try:
            response = s3_images_bucket.upload_fileobj(file_content, filename)
            print('Image Inserted in S3 : ' + song['artist'])
        except Exception as e:
            print(str(e))
                
#--------------------------------------------------------------------------------

table_name = 'login'
table = dynamodb.create_table(
    TableName=table_name,
    KeySchema=[
        {
            'AttributeName': 'email',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'password',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'password',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# # Wait for the table to be created
table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

print(f"Table '{table_name}' has been created successfully.")

table = dynamodb.Table(table_name)

# for login
for user in users["users"]:
    table.put_item(Item=user)
    print('User inserted in database : ' + user['username'])

#--------------------------------------------------------------------------------

table_name = 'subscription'
table = dynamodb.Table(table_name)
table = dynamodb.create_table(
    TableName=table_name,
    KeySchema=[
        {
            'AttributeName': 'email',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'title',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'title',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait for the table to be created
table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

print(f"Table '{table_name}' has been created successfully.")

# for subscription
for subscription in subscriptions['subscriptions']:
    table.put_item(Item=subscription)
    print('Susbcription inserted in database : ' + subscription['email'] + " : " + subscription['title'])



