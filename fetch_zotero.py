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
            
            # Flatten tags
            tags = data.get('tags', [])
            data['tags_flattened'] = ", ".join([t.get('tag', '') for t in tags])
            
            # Clean up nested fields so they don't break the CSV
            for key in ['creators', 'tags', 'collections', 'relations', 'attachments', 'notes']:
                data.pop(key, None)
                
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
    preferred_order = ['itemType', 'title', 'authors_flattened', 'date', 'publicationTitle', 'DOI', 'url']
    final_columns = [col for col in preferred_order if col in sorted_columns] + \
                    [col for col in sorted_columns if col not in preferred_order]

    filename = 'zotero_registered_reports.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=final_columns)
        writer.writeheader()
        writer.writerows(all_items)

    print(f"Successfully saved {len(all_items)} items to {filename}.")

if __name__ == "__main__":
    fetch_and_save_zotero_library()
