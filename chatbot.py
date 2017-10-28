import logging
from botocore.vendored import requests
import json
import config
import base64
import hashlib
import hmac

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lineChatbot(event, context):
    print(event)

    if 'body' in event:
        body = json.loads(event['body'])
        replyToken = body['events'][0]['replyToken']
        message = body['events'][0]['message']

        logger.info(' reply token : ' + replyToken)

        params = {"replyToken": str(replyToken), "messages": [message]}
        headers = {"Content-type": "application/json",
                   "Authorization": "Bearer " + config.access_token}
        res = requests.post(url="https://api.line.me/v2/bot/message/reply", headers=headers, data=json.dumps(params))

        print('success')
        res.json()
        print(res.status_code)
        res.raise_for_status()

        res.connection.close()

    return {
        "headers": {"status": 'success'},
        "statusCode": 200,
        "body": ""
    }