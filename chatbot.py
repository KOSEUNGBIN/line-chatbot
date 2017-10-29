
import logging
import json
import config
import datetime

from linebot import (
    api, webhook
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)


from watson_developer_cloud import (
    ConversationV1, WatsonException
)

# logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# line
line_bot = api.LineBotApi(config.line_access_token)
handler = webhook.WebhookHandler(config.line_channel_secret)
parser = webhook.WebhookParser(config.line_channel_secret)

# watson
conversation = ConversationV1(
  username = config.watson_username,
  password = config.watson_password,
  version = datetime.datetime.today().strftime('%Y-%m-%d')
)

def main(event, context):

    response = {
        "headers": {"status": 'success'},
        "statusCode": 200,
        "body": ""
    }

    if 'body' in event:
        try:
            # webhook parsing
            signature = event['headers']['X-Line-Signature']
            response_body = parser.parse(event['body'] , signature)

            logger.info(response_body)

            # message 개수 단위로 watson conversion api 에 요청
            # watson conversion api 결과를 Line api를 통해, Cients에게 전송
            for value in response_body:
                responseFromWatson = request_message_to_watson(value)
                logger.info(responseFromWatson['context']['system']['branch_exited_reason'])
                if responseFromWatson['context']['system']['branch_exited_reason'] != 'completed':
                    raise InvalidSignatureError
                logger.info(' reply token : ' + value.reply_token)

                value.message.text = responseFromWatson['output']['text'][0]
                logger.info(' value.message.text : ' + str(value.message.text))

                responseFromLine = handle_message(value)
                logger.info(responseFromLine)

        except InvalidSignatureError as error:
            response['headers']['status'] = "fail"
            response['statusCode'] = error.status_code
            response['body'] = error.message

            logger.error(error.status_code)
            logger.error(error.message)
            logger.error(error.message)
        except LineBotApiError as error:
            response['headers']['status'] = "fail"
            response['statusCode'] = error.status_code
            response['body'] = error.message

            logger.error(error.status_code)
            logger.error(error.message)
            logger.error(error.message)

    return response

# request message to Line api
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    return line_bot.reply_message(event.reply_token, TextSendMessage(text=event.message.text))

# request questions to Watson conversion api
def request_message_to_watson(message):

    watsonResponse = None
    try:
        watsonResponse = conversation.message(
            workspace_id=config.watson_workspace_id,
            message_input={
                'text': str(message)
            }
        )

        watsonResponse = json.dumps(watsonResponse, indent=2)
        watsonResponse = json.loads(watsonResponse)

        logger.info(watsonResponse)
    except WatsonException as error:
        logger.error(str(error))



    return  watsonResponse
