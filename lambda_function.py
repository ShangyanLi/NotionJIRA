from dotenv import dotenv_values
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from sys import exit
from tqdm.autonotebook import tqdm

# Initial requests setup, handling possible HTTP 429 rate limited errors from Notion.
config = dotenv_values('.env')
token = config.get('NOTION_TOKEN')
db_id = config.get('NOTION_DATABASE_ID')
id_prop = config.get('NOTION_ID_PROP', 'Ticket ID')
if token is None or db_id is None:
    print('You must pass in both NOTION_TOKEN and NOTION_DATABASE_ID as env variables.')
    exit(1)

base_url = 'https://api.notion.com/v1'
headers = {'Authorization': f'Bearer {token}', 'Notion-Version': '2021-05-13'}
retry_strategy = Retry(
    total=10,
    status_forcelist=[429],
    allowed_methods=['GET', 'PATCH', 'POST'],
    backoff_factor=0.5
)
adapter = HTTPAdapter(max_retries=retry_strategy)
s = requests.session()
s.headers.update(headers)
s.mount('https://', adapter)
s.mount('http://', adapter)


def has_ticket_id_prop() -> bool:
    r = s.get(f'{base_url}/databases/{db_id}')
    if not r.status_code // 100 == 2:
        print(f'Error: Unexpected response {r}\n{r.text}')
        exit(1)
    props = r.json()['properties']
    return id_prop in props.keys() and props[id_prop]['type'] == 'number'


def get_latest_ticket_id() -> int:
    results = s.post(f'{base_url}/databases/{db_id}/query', json={
        'page_size': 1,
        'filter': {
            'property': id_prop,
            'number': {
                'is_not_empty': True
            }
        },
        'sorts': [
            {
                'property': id_prop,
                'direction': 'descending',
            }
        ]
    }).json()['results']
    # Since we start IDs with 1, 0 indicates no ticket has its ID set yet.
    return results[0]['properties'][id_prop]['number'] if results else 0


def get_tickets_from_db() -> ([str], int):
    tickets = []
    latest_id = get_latest_ticket_id()

    sort_json = {
        'sorts': [
            {
                'timestamp': 'created_time',
                'direction': 'ascending'
            }
        ],
        'filter': {
            'or': [
                {
                    'property': id_prop,
                    'number': {
                        'greater_than': latest_id
                    }
                },
                {
                    'property': id_prop,
                    'number': {
                        'is_empty': True
                    }
                }
            ]
        }
    }

    def get_page_of_tickets(cursor: str = None) -> None:
        data_json = sort_json if cursor is None else {**sort_json, 'start_cursor': cursor}
        r = s.post(f'{base_url}/databases/{db_id}/query', json=data_json).json()
        # We only need the page id's. Returned results are already sorted by Notion.
        tickets.extend([p['id'] for p in r['results']])
        print('Retrieved a page. ', end='')
        print(f'next page cursor is {r["next_cursor"]}...' if r['next_cursor'] is not None else '')
        if r['has_more']:
            get_page_of_tickets(r['next_cursor'])

    get_page_of_tickets()
    print(f'Done. Retrieved {len(tickets)} new ticket(s).\n')
    return tickets, latest_id


def update_ticket_ids(tickets: [str], latest_id: int) -> None:
    if not tickets:
        print('No tickets to update, exiting.')
        return

    ticket_id = latest_id
    errors = []
    print(f'Adding auto-incrementing "Ticket ID" property to {len(tickets)} ticket(s)...')
    for page_id in tqdm(tickets):
        ticket_id += 1
        r = s.patch(f'{base_url}/pages/{page_id}', json={
            'properties': {
                'Ticket ID': ticket_id
            }
        })
        if r.status_code != 200:
            errors.append(page_id)
    if errors:
        print(f'The following page ID(s) could not be updated: {", ".join(errors)}')


def main(event, context):
    if not has_ticket_id_prop():
        print(f'Property "{id_prop}" does not exist in database or its type is not Number.')
        exit(1)
    update_ticket_ids(*get_tickets_from_db())


if __name__ == '__main__':
    main('', '')
