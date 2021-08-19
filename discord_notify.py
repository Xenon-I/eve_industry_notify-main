import time
from discord_webhook import DiscordWebhook
import requests
import datetime
import redis


eve_seat_api_token = ''
eve_seat_host = ''
eve_corporation_id = ''
redis_host = ''
discord_web_hook_url = ''


def get_industry_jobs():
    headers = {
        'accept': 'application/json',
        'X-Token': eve_seat_api_token,
        'X-CSRF-TOKEN': '',
    }
    response = requests.get(
        eve_seat_host + 'api/v2/corporation/industry/' + eve_corporation_id + '?%24filter=status%20eq%20%27active%27', # Odata filter for get only active jobs
        headers=headers)
    response_json = response.json()
    if response_json['meta']['last_page'] == 1:
        return response_json['data']
    else:
        total_page = response_json['meta']['last_page']
        for page in range(2, total_page+1):
            response = requests.get(
                eve_seat_host + 'api/v2/corporation/industry/' + eve_corporation_id +
                '?%24filter=status%20eq%20%27active%27&page=' + str(page), headers=headers)
            response_json.extend(response.json()['data'])
        return response_json['data']


def check_redis(job_id):
    if rd.get(job_id) == b'done':
        return True
    else:
        return False


def set_redis(job_id):
    rd.set(job_id, 'done')


def notify_done_message(message):
    webhook = DiscordWebhook(url=discord_web_hook_url, content=message)
    webhook.execute()


if __name__ == "__main__":
    rd = redis.StrictRedis(host=redis_host, port=6379, db=5)

    data = get_industry_jobs()
    message_buff = ''
    for item in data:
        end_date = datetime.datetime.strptime(item['end_date'], '%Y-%m-%d %H:%M:%S')
        if end_date < datetime.datetime.now():
            if check_redis(item['job_id']):
                pass
            else:
                if item['facility_id'] == 1000000000000:
                    buff = '[some_structure]'
                elif item['facility_id'] == 1000000000000:
                    buff = '[some_structure]'
                else:
                    buff = '[some_structure]'
#                 message_buff += item['blueprint']['typeName'] + ' x ' + str(item['runs']) + ' job in ' + buff + ' is done.\n'
#                 set_redis(item['job_id'])
#                 if len(message_buff) > 1000:
#                     notify_done_message(message_buff)
#                     time.sleep(3)
#                     message_buff = ''
            message_buff.append(item['blueprint']['typeName'] + ' x ' + str(item['runs']) + ' job in ' + buff + ' is done.\n')
            set_redis(item['job_id'])

    if message_buff != '':
#         notify_done_message(message_buff)
        notify_done_message('\n'.join(list(set(message_buff))))
    else:
        exit(0)

