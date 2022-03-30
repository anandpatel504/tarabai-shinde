from dotenv import load_dotenv
import requests
import os
import json

'''
Return : records    : Rows of the navgurkul database in Notion
                    : {properties : field : {}}
'''
def get_navgurkul_records(DB_ID):
    all_records_resp = requests.post( f'https://api.notion.com/v1/databases/{DB_ID}/query', headers={ 'Authorization' : NOTION_TOKEN,  'Notion-Version' : NOTION_VERSION } )
    if all_records_resp.status_code == 200 :
        return all_records_resp.json()
    else :
        return {'Error' : all_records_resp.headers}

def get_notion_fields(DB_ID):
    all_fields = requests.get( f'https://api.notion.com/v1/databases/{DB_ID}', headers={ 'Authorization' : NOTION_TOKEN,  'Notion-Version' : NOTION_VERSION } )
    fields = {}
    for row in all_fields.json()['properties']:
        fields[row] = None
    return fields


def format_row(row, page_fields):
    result = page_fields.copy()
    for r in row:
        if row[r]['type'] == "title":
            result[r] = row[r]['title'][0]['text']['content'] if len(row[r]['title'])>0 else ""
        elif row[r]['type'] == "email":
            result[r] = row[r]['email']
        elif row[r]['type'] == "phone_number":
            result[r] = row[r]['phone_number']
        elif row[r]['type'] == "select":
            result[r] = row[r]['select']['name']
        elif row[r]['type'] == "multi_select":
            Skills = list(map(lambda x: x['name'],row[r]['multi_select']))
            result[r] = Skills
        elif row[r]['type'] == "select":
            result[r] = row[r]['select']['name']
        elif row[r]['type'] == "rich_text":
            result[r] = row[r]['rich_text'][0]['plain_text'] if len(row[r]['rich_text']) > 0 else None
        ## for linkedIn and Twitter (if type = url)
        elif row[r]['type'] == "url":
            result[r] = row[r]['url']
        elif row[r]['type'] == "files":
            result[r] = row[r]['files'][0]['file']['url'] if len(row[r]['files']) ==1 else None if len(row[r]['files']) ==0 else list(map(lambda x: x['file']['url'],row[r]['files']))
        elif row[r]['type'] == 'created_time':
            result[r] = row[r]['created_time'] if ['created_time'] else None
    return result

def formate_paragraph(id):
    content = []
    record_description = requests.get( f'https://api.notion.com/v1/blocks/{id}/children', headers={ 'Authorization' : NOTION_TOKEN,  'Notion-Version' : NOTION_VERSION })
    for block in record_description.json()['results']:
        if block['type'] == 'paragraph':
            content.append(block['paragraph']['text'][0]['plain_text'] if len(block['paragraph']['text']) > 0 else '\n')
    return content

def get_data_from_notion_db(DB_ID, file_name):
    page_fields = get_notion_fields(DB_ID)

    '''
    Steps -
    0. Pull data from DB
    1. Parse the data
    2. Rewrite different files like -
        navgurukul-openings.json
        navgurukul-team.json
        ...
    '''

    # Step 0. Get the data
    navgurkul_res = get_navgurkul_records(DB_ID)
    
    # Step 1. Parse the data. Currently, only two columns => {name, tag}
    '''
    Notion already has an ID to store each record.
    We will use thid "id" as our key as well
    '''
    navgrukul_db_dump = {}
    for row in navgurkul_res['results']:
        id = row['id']
        row = row['properties']
        row_data = format_row(row, page_fields).copy()
        row_data['Content'] = formate_paragraph(id)
        navgrukul_db_dump[id] = row_data

    # Step 3. Dump data to tmp/navgurukul_testing.json
    with open(f'tmp/{file_name.lower()}.json', 'w+') as json_file:
        json.dump(navgrukul_db_dump, json_file, indent=2)

if __name__ == '__main__':
    try:
        load_dotenv()
        NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
        NOTION_VERSION = os.environ.get('NOTION_VERSION')
        NAVGURUKUL_DB_ID_MERAKI_TEAM = os.environ.get('NAVGURUKUL_DB_ID_MERAKI_TEAM')
        NAVGURUKUL_DB_ID_PARTNERS = os.environ.get('NAVGURUKUL_DB_ID_PARTNERS')
        NAVGURUKUL_DB_ID_NG_TEAM = os.environ.get('NAVGURUKUL_DB_ID_NG_TEAM')
        NAVGURUKUL_DB_ID_ALUMNI = os.environ.get('NAVGURUKUL_DB_ID_ALUMNI')
        NAVGURUKUL_DB_ID_SUPPORTERS = os.environ.get('NAVGURUKUL_DB_ID_SUPPORTERS')
        NAVGURUKUL_DB_ID_GALLERY = os.environ.get('NAVGURUKUL_DB_ID_GALLERY')
        NAVGURUKUL_DB_ID_MEDIA = os.environ.get('NAVGURUKUL_DB_ID_MEDIA')
        NAVGURUKUL_DB_ID_PROJECTS = os.environ.get('NAVGURUKUL_DB_ID_PROJECTS')
        NAVGURUKUL_DB_ID_CAMPUSES = os.environ.get('NAVGURUKUL_DB_ID_CAMPUSES')
        NAVGURUKUL_DB_ID_MERAKI_PARTNERS = os.environ.get('NAVGURUKUL_DB_ID_MERAKI_PARTNERS')

        # print(NOTION_TOKEN, NOTION_VERSION,NAVGURUKUL_DB_ID_MERAKI_TEAM, NAVGURUKUL_DB_ID_PARTNERS, NAVGURUKUL_DB_ID_NG_TEAM)
        get_data_from_notion_db(NAVGURUKUL_DB_ID_MERAKI_TEAM, "meraki_team")
        get_data_from_notion_db(NAVGURUKUL_DB_ID_PARTNERS, "partners")
        get_data_from_notion_db(NAVGURUKUL_DB_ID_NG_TEAM, "ng_team")
        get_data_from_notion_db(NAVGURUKUL_DB_ID_ALUMNI, "alumni")
        get_data_from_notion_db(NAVGURUKUL_DB_ID_SUPPORTERS, "supporters")
        get_data_from_notion_db(NAVGURUKUL_DB_ID_GALLERY, "gallery")
        get_data_from_notion_db(NAVGURUKUL_DB_ID_MEDIA, "media")
        get_data_from_notion_db(NAVGURUKUL_DB_ID_PROJECTS, "projects")
        get_data_from_notion_db(NAVGURUKUL_DB_ID_CAMPUSES, "campuses")
        get_data_from_notion_db(NAVGURUKUL_DB_ID_MERAKI_PARTNERS, "meraki_partners")

    except Exception as e:
        print("Got Error In Your Code: ", e)
