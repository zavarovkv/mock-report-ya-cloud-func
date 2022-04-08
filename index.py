import base64
import random

from datetime import datetime, timedelta
from config import Config
from storage import save_to_storage


def handler(event, context):

    path = event['path']

    # Check access key in request header
    try:
        api_key = event['headers']['X-Api-Key']

    except Exception as e:
        return forbidden(event, context, str(e))

    if api_key != Config.API_KEY:
        return forbidden(event, context)

    # Routing
    if path == '/generate_report':
        return generate_report(event, context)
    
    elif path == '/get_report':
        return get_report(event, context)
    
    else:
        return bad_request(event, context)


def generate_report(event, context):

    if event['httpMethod'] != 'POST':
        return bad_request(event, context)
    
    try:
        params = event['params']
        
        start_date = datetime.strptime(params['start_date'], Config.DATE_FORMAT)
        end_date = datetime.strptime(params['end_date'], Config.DATE_FORMAT)
        curr_date = datetime.now()

    except Exception as e:
        return bad_request(event, context, str(e))

    delta = (end_date - start_date).total_seconds()

    if delta > Config.DATE_PERIOD_LIMIT:
        return bad_request(event, context, 'Too long period of dates. Should be less then 90 days.')

    # Prepare date's for encode to base64
    pre = '\t'.join(e.strftime(Config.DATE_FORMAT) for e in [start_date, end_date, curr_date])

    try:
        # And convert it
        encoded = base64.b64encode(bytes(pre, 'utf-8'))
        encoded = encoded.decode('ascii')
        
    except Exception as e:
        return bad_request(event, context, str(e))

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': {
            'report_id': encoded
        }
    }


def get_report(event, context):

    if event['httpMethod'] != 'GET':
        return bad_request(event, context)
    
    try:
        report_id = event['params']['report_id']

    except Exception as e:
        return bad_request(event, context, str(e))

    try:
        # Decode report_id into string
        decoded = report_id.encode('ascii')
        decoded = base64.b64decode(decoded)
        decoded = decoded.decode('ascii')

        # And decode string into dates
        [start_date, end_date, request_date] = decoded.split('\t')

        start_date = datetime.strptime(start_date, Config.DATE_FORMAT)
        end_date = datetime.strptime(end_date, Config.DATE_FORMAT)
        request_date = datetime.strptime(request_date, Config.DATE_FORMAT)

    except Exception as e:
        return bad_request(event, context, 'Incorrect report_id format')

    curr_date = datetime.now()

    # Define status
    delta = (curr_date - request_date).total_seconds()

    if delta < Config.DELAY_SECONDS:
        status = 'RUNNING'
    else:
        status = 'SUCCESS'

    report_link = None

    if status == 'SUCCESS':
        report_data = get_report_data(start_date, end_date)

        key_name = base64.b64encode(bytes(report_id, 'utf-8'))
        key_name = key_name.decode('ascii')

        report_link = save_to_storage(report_data, key_name)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': {
            'id': report_id,
            'status': status,
            'data': {
                'report_link': report_link
            }
        }
    }


def bad_request(event, context, e=''):
    return {
        'statusCode': 400,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': f'Bad request. {e}'
    }


def forbidden(event, context, e=''):
    return {
        'statusCode': 403,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': f'403 Forbidden. {e}'
    }


def get_report_data(start_date, end_date, size=1000) -> dict:
    report_dict = {}
    delta = timedelta(days=1)

    while start_date <= end_date:
        random.seed(start_date)
        report_dict[start_date.strftime(Config.DATE_FORMAT)] = int(random.random() * size)
        start_date += delta

    return report_dict
