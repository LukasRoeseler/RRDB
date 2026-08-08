import requests
import csv

def fetch_and_save_zotero_library():
    group_id = '5937153'
    url = f'https://api.zotero.org/groups/{group_id}/items/top'
    headers = {'Zotero-API-Version': '3'}
    params = {'limit': 100, 'start': 0}
    
    all_items = []
    
    print("Fetching data from Zotero API...")
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        items = response.json()
        
        if not items:
            break
            
        for item in items:
            data = item.get('data', {})
            
            # Flatten authors
            creators = data.get('creators', [])
            authors = []
            for c in creators:
                if 'lastName' in c and 'firstName' in c:
                    authors.append(f"{c['lastName']}, {c['firstName']}")
                elif 'name' in c:
                    authors.append(c['name'])
            data['authors_flattened'] = "; ".join(authors)
            
            # Flatten tags and identify Stage 1 vs Stage 2
            tags = data.get('tags', [])
            tag_strings = [t.get('tag', '') for t in tags]
            data['tags_flattened'] = ", ".join(tag_strings)
            
            # Flag if the item is a Stage 1 report based on tags
            is_stage_1 = any("stage 1" in t.lower() for t in tag_strings)
            data['is_stage_1'] = is_stage_1
            
            # Clean up nested fields so they don't break the CSV structure
            for key in ['creators', 'tags', 'collections', 'relations', 'attachments', 'notes']:
                data.pop(key, None)

            # FIX: Remove line breaks from string fields (like abstracts, titles, and 'extra')
            # This ensures stable CSV exports across all software (Excel, Numbers, etc.)
            for key, value in data.items():
                if isinstance(value, str):
                    # Replace newlines/carriage returns with space, and clean up double spaces
                    clean_string = value.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
                    data[key] = ' '.join(clean_string.split())
                
            all_items.append(data)
            
        total_results = int(response.headers.get('Total-Results', 0))
        params['start'] += params['limit']
        
        if params['start'] >= total_results:
            break

    # Determine unique columns across all item types
    columns = set()
    for item in all_items:
        columns.update(item.keys())
        
    sorted_columns = sorted(list(columns))
    preferred_order = ['itemType', 'title', 'authors_flattened', 'date', 'publicationTitle', 'DOI', 'url', 'is_stage_1', 'tags_flattened']
    final_columns = [col for col in preferred_order if col in sorted_columns] + \
                    [col for col in sorted_columns if col not in preferred_order]

    # --- SAVE FIRST CSV (ALL ITEMS) ---
    filename_all = 'zotero_registered_reports.csv'
    with open(filename_all, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=final_columns)
        writer.writeheader()
        writer.writerows(all_items)
    print(f"Successfully saved {len(all_items)} total items to {filename_all}.")

    # --- SAVE SECOND CSV (STAGE 2 / EXCLUDING STAGE 1) ---
    stage_2_items = [item for item in all_items if not item.get('is_stage_1', False)]
    filename_stage2 = 'zotero_registered_reports_stage2.csv'
    
    with open(filename_stage2, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=final_columns)
        writer.writeheader()
        writer.writerows(stage_2_items)
    print(f"Successfully saved {len(stage_2_items)} Stage 2/Non-Stage-1 items to {filename_stage2}.")

if __name__ == "__main__":
    fetch_and_save_zotero_library()
