import boto3
from boto3.dynamodb.conditions import Attr

aws_access_key_id="ASIAXRPYQJ5RGT2HEIQE"
aws_secret_access_key="YD/pzIHu2UIwiFTkaun+AP21mbHvRoBDcTgMCKgT"
aws_session_token="FwoGZXIvYXdzEK3//////////wEaDHuICJ0m2l8ZXhVxJCLNASdZ581Q09qNmj+ysC5Uf6r2W6FZFU68clKcPFKYdPBMNEPSJGTc07p96yLB80T6ioILItOP97nudq2YlZRXcypowr4Qer2okMXj3allHR1FBTdmFFpYBAqQwk1UevCvSho+yvcctH0Ykp3oKTTiixy6zeXJttJPtOyaD5+ou/CZp/PfReD/ZD5W793FbwNwveQdJTSAPVL6lzHtwTyScGbhg96142xwXb9aoojbirFbiFzeL5MZB5cJ8zmNiKmdKYFdsdQxSczf++aYGkEo7IXOoQYyLUBhyqBMR4vWyEd9eH2e2zUfgNg5/BbBHnazbYYuDbyxG0FmR5tV/kFGL+2cGg=="

# creating a resource
dynamodb = boto3.resource( 'dynamodb',
                        aws_access_key_id=aws_access_key_id, 
                        aws_secret_access_key=aws_secret_access_key, 
                        aws_session_token=aws_session_token,
                        region_name='us-east-1') 

login = dynamodb.Table('login')
music = dynamodb.Table('music')
subscribe = dynamodb.Table('subscription')

def confirm_login(email,password):
    query_params = {
    'KeyConditionExpression': 'email = :val1 and password = :val2',
    'ExpressionAttributeValues': {
        ':val1': email,
        ':val2': password
        }
    }
    
    response = login.query(**query_params)
    
    if not response['Items']:
        return False

    else:
        return response['Items'][0]['username']

def email_exists(email):
    # Query the table for items with a specific email address
    response = login.query(
        KeyConditionExpression='email = :email',
        ExpressionAttributeValues={
            ':email': email
        }
    )
    
    if response['Count'] == 1: #email already exists
        return True
    else: #email does not exist
        return False

def register(email, username, password):
    
    # check for duplicity
    if email_exists(email) == False:
        user = {
            "email" : email,
            "password" : password,
            "username" : username
        }
        login.put_item(Item=user)
        return True
    else:
        return False
    
def get_subscribed_music(email):
    
    query_params = {
    'KeyConditionExpression': 'email = :val1',
    'ExpressionAttributeValues': {
        ':val1': email,
        }
    }
    
    response = subscribe.query(**query_params)
    
    data_to_return = []
    list_of_songs = response['Items']
    for song in list_of_songs:
        data_to_return.append(get_music(title=song['title'], artist=song['artist'])[0])
    
    return data_to_return
                   
def get_music(title,artist):
    query_params = {
    'KeyConditionExpression': 'artist = :val1 and title = :val2',
    'ExpressionAttributeValues': {
        ':val1': artist,
        ':val2': title
        }
    }
    response = music.query(**query_params)
    
    if not response['Items']:
        return False

    else:
        return response['Items']

def get_query(title,artist,year):
    
    filter_expression = None
    
    if len(title) != 0:
            filter_expression = Attr('title').eq(title)
    if len(artist) != 0:
        if filter_expression is None:
            filter_expression = Attr('artist').eq(artist)
        else:
            filter_expression = filter_expression &  Attr('artist').eq(artist) 
    if len(year) != 0:
        if filter_expression is None:
            filter_expression = Attr('year').eq(year)
        else:
            filter_expression = filter_expression & Attr('year').eq(year)  

    if filter_expression is None:
        return False
    
    # Define the expression attribute names
    expression_attribute_names = {'#t': 'title', '#a': 'artist', '#y': 'year', "#w" : 'web_url', "#i" : 'img_url'}

    # Define the projection expression
    projection_expression = "#t, #a, #y, #w, #i"

    # Scan the table with the defined filter expression, expression attribute names, and projection expression
    response = music.scan(FilterExpression=filter_expression, ExpressionAttributeNames=expression_attribute_names, ProjectionExpression=projection_expression)
    
    
    print("Response Item : " + str(response['Items']))
    return response['Items']

def remove_subscription(email, title, artist):
    conditional_expression = 'artist = :artist'
    
    expression_attribute_values = {
        ':artist' : artist
    }
    
    response = subscribe.delete_item(
        Key={'email': email, 'title' : title},
        ConditionExpression=conditional_expression,
        ExpressionAttributeValues=expression_attribute_values
    )
    
    if 'Attributes' in response:
        return True
    else:
        return False
    

def susbcribe_song(email, title, artist):
    subs= {
        "email" : email,
        "title" : title,
        "artist" : artist
    }
    subscribe.put_item(Item=subs)
    return True