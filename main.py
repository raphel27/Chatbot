import requests as requests
from iexfinance.stocks import Stock
import re
import random

url = "https://api.telegram.org/bot1078830395:AAGsi7i_dxc3T7iqQQYQVBYjHGDT8M92zOU/"


# create chat ID
def get_chat_id(update):
    chat_id = update["message"]["chat"]["id"]
    return chat_id


# get message
def get_message_text(update):
    message_text = update["message"]["text"]
    return message_text


# get last up date
def last_update(req):
    response = requests.get(req + "getUpdates")
    response = response.json()
    result = response["result"]
    total_updates = len(result) - 1
    return result[total_updates]


# send back
def send_message(chat_id, message_text):
    params = {"chat_id": chat_id, "text": message_text}
    response = requests.post(url + "sendMessage", data=params)
    return response


def interpret(message):
    msg = message.lower()
    if 'hi' in msg:
        return 'id'
    if 'who' in msg:
        return 'self'
    if 'google' in msg:
        if 'latest' in msg:
            return 'ask_pric_goo'
        if 'open' in msg:
            return 'ask_hi_goo'
        else:
            return 'cp2'
    if 'apple' in msg:
        if 'latest' in msg:
            return 'ask_pric_app'
        if 'open' in msg:
            return 'ask_hi_app'
        else:
            return 'cp1'
    if 'thank' in msg:
        return 'end'
    return 'none'


a = Stock("AAPL", token="pk_20eee9b7062744679cd544d3c3170f6d")
APP = a.get_quote()
b = Stock("GOOGL", token="pk_20eee9b7062744679cd544d3c3170f6d")
GOO = a.get_quote()

WORK = 0
OTHER = 1
KEEPASK = 2
FINISH = 3

policy_rules = {
    (WORK, 'id'): (WORK, "How can I help you?", None),
    (WORK, "self"): (WORK, "I'm a stock bot which means I can give you some information about stock", None),
    (WORK, "cp2"): (WORK, "What information do you want to know about Google's stock?", None),
    (WORK, "cp1"): (WORK, "What information do you want to know about Apple's stock?", None),
    (WORK, "ask_pric_app"): (WORK, "Currently the price of Apple's stock is" + " " + str(APP['latestPrice']), KEEPASK),
    (WORK, "ask_hi_app"): (WORK, "The open price of Apple's stock is" + " " + str(APP['open']), KEEPASK),
    (WORK, "ask_pric_goo"): (WORK, "Currently the price of Google's stock is" + " " + str(GOO['latestPrice']), KEEPASK),
    (WORK, "ask_hi_goo"): (WORK, "The open price of Google's stock is" + " " + str(GOO['open']), KEEPASK),
    (WORK, "end"): (FINISH, "Glad I can help you!", None)
}


def match_rule(rules, message):
    for pattern, responses in rules.items():
        match = re.search(pattern, message)
        if match is not None:
            response = random.choice(responses)
            var = match.group(1) if '{0}' in response else None
            return response, var
    return "default", None


rules = {'if (.*)': ["Do you really think it's likely that {0}", 'Do you wish that {0}', 'What do you think about {0}',
                     'Really--if {0}'], 'do you think (.*)': ['if {0}? Absolutely.', 'No chance'],
         'I want (.*)': ['What would it mean if you got {0}', 'Why do you want {0}',
                         "What's stopping you from getting {0}"],
         'do you remember (.*)': ['Did you think I would forget {0}', "Why haven't you been able to forget {0}",
                                  'What about {0}', 'Yes .. and?']}


def replace_pronouns(message):
    message = message.lower()
    if 'me' in message:
        return re.sub('me', 'you', message)
    if 'i' in message:
        return re.sub('i', 'you', message)
    elif 'my' in message:
        return re.sub('my', 'your', message)
    elif 'your' in message:
        return re.sub('your', 'my', message)
    elif 'you' in message:
        return re.sub('you', 'me', message)

    return message


def chitchat_response(message):
    response, phrase = match_rule(rules, message)
    if response == "default":
        return None
    if '{0}' in response:
        phrase = replace_pronouns(message)
        response = response.format(phrase)
    return response


def responses(state, pending, message):
    response = chitchat_response(message)
    if response is not None:
        return state, None

    new_state, response, pending_state = policy_rules[(state, interpret(message))]
    if pending is not None:
        new_state, response, pending_state = policy_rules[pending]
    return new_state, pending, response


def send_messages(question):
    state = WORK
    pending = None
    state, pending, response = responses(state, pending, question)
    return response


# main for reply
def main():
    update_id = last_update(url)["update_id"]
    while True:
        update = last_update(url)
        if update_id == update["update_id"]:
            question = get_message_text(update)
            answer = send_messages(question)
            send_message(get_chat_id(update), answer)
            update_id += 1


main()
