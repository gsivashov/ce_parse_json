import csv
import re
import ijson
import sys

result = {}

# event fields
# properties.internalsearchTerm - search term (clean_keyword)
# context.page.path - referer (result[url][keyword]["url"])
# context.page.url - page (url)

# count: ammount of events with `properties.internalsearchTerm` (result[url][keyword]["count"])


def clean_search_term(term: str) -> bool:
    # variant 1
    clean_keyword = re.sub(r'[^\'\d\w\s-]+', '', term).replace(
        ' ', '{}').replace('}{', '').replace('{}', ' ').replace('\t', '').lower().strip()
    return clean_keyword

# raw-events-export-438d3553-a1f2-4f30-b077-0cbebc227d66-part-00-000.json


with open('raw-events-export-438d3553-a1f2-4f30-b077-0cbebc227d66-part-04-000.json') as start_file:
    obj = ijson.items(start_file, 'data', multiple_values=True)

    for idx, item in enumerate(obj, 1):
        if idx % 10_000 == 0:
            print(f'processed events {idx}', file=sys.stderr)

        if 'properties.internalsearchTerm' not in item:
            continue

        search_term = clean_search_term(item['properties.internalsearchTerm'])
        parrent_url = item['context.page.path']  # referer
        target_url = item['context.page.url']  # page
        target_url = parrent_url + f"?fts={'+'.join(search_term.split())}"

        if parrent_url in result:
            if search_term in result[parrent_url]:
                result[parrent_url][search_term]['count'] += 1
            else:
                result[parrent_url].update(
                    {search_term: {'count': 1, 'url': target_url}})
        else:
            result[parrent_url] = {
                search_term: {'count': 1, 'url': target_url}
            }

for url in result:
    for keyword in result[url]:
        print(
            f'{url}|{keyword}|{result[url][keyword]["count"]}|{result[url][keyword]["url"]}', flush=True)
