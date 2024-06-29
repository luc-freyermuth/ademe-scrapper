import requests
import math
import csv
import time
from functools import reduce

'/inventories?page=1&itemsPerPage=10&publication.status[]=valide&publication.status[]=a-traiter&publication.status[]=refuse'

ADEME_BILANS_API_URL = 'https://bilans-ges.ademe.fr/api'
PAGE_SIZE = 50

def get_bilans_page(page, page_size):
    return requests.get(ADEME_BILANS_API_URL + f'/inventories?page={page}&itemsPerPage={page_size}&publication.status[]=valide&publication.status[]=a-traiter&publication.status[]=refuse').json()

def get_bilans_page_count(page_size):
    return math.ceil(get_bilans_page(1, page_size)['hydra:totalItems'] / page_size)

def get_bilans_page_content(page, page_size):
    return get_bilans_page(page, page_size)['hydra:member']

def get_bilan_details(id):
    return requests.get(ADEME_BILANS_API_URL + f'inventories/{id}').json()

def optional_chain(root, keys):
    result = root
    for k in keys.split('.'):
        if isinstance(result, dict):
            result = result.get(k, None)
        else:
            result = getattr(result, k, None)
        if result is None:
            break
    return result

page_count = get_bilans_page_count(PAGE_SIZE)

data = []

for page in range(1, page_count):
    print(f'Page {page}')
    page_content = get_bilans_page_content(page, PAGE_SIZE)
    for details in page_content:
        # the information i needed, you could simply combine all the dicts and throw them in the csv
        data.append({
            'id': details['id'],
            'link': f'https://bilans-ges.ademe.fr/bilans/consultation/{details['id']}/fiche-identite',
            'name': details['inventoryEntity']['companyName'],
            'year': details['identitySheet']['reportingYear'],
            'naf_code': optional_chain(details, 'identitySheet.APECode.id'),
            'naf_code_label': optional_chain(details, 'identitySheet.APECode.label'),
            'min_employees': optional_chain(details, 'inventoryEntity.peopleCount.min'),
            'max_employees': optional_chain(details, 'inventoryEntity.peopleCount.max'),
            'structure_type': optional_chain(details, 'entity.structureType.label'),
            'departement': optional_chain(details, 'entity.department.id'),
            'CA_keuros': details['identitySheet']['turnover']
        })
    time.sleep(2)

with open("database.csv", "w", newline="") as f:
    w = csv.DictWriter(f, data[0].keys())
    w.writeheader()
    for d in data:
        w.writerow(d)