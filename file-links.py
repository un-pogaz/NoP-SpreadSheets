import argparse
import os.path
import random
import time

from common import (
    get_filtered_post,
    parse_content,
    read_lines,
    requests,
    run_animation,
    write_lines,
)

args = argparse.ArgumentParser(description='Retrive the data from a list of link')
args.add_argument('-u', '--url', '--exclude-url', dest='exclude_url', action='store_true', help='Exclude where the url post is already in the spreadsheets')
args.add_argument('file', type=str, nargs='+', help='File path of txt containing urls to check')
args = args.parse_args()

for file in args.file:
    print()
    if not os.path.exists(file):
        print("The path don't exist:", file)
        continue
    if os.path.isdir(file):
        print("The path is a folder:", file)
        continue
    
    basename = os.path.splitext(file)[0]
    lines = []
    all_post = []
    
    lst_invalide_link = set()
    
    all_link = set(read_lines(file, []))
    lenght = len(all_link)
    
    async def read_all_link():
        for idx, base_url in enumerate(all_link, 1):
            i = random.randint(8,22)
            run_animation.extra = f'{idx}/{lenght} (waiting {i} seconds to appease reddit)'
            
            if 'reddit.com' not in base_url:
                continue
            
            for suffix in ['/', '.json']:
                if not base_url.endswith(suffix):
                    base_url += suffix
            
            reponse = requests.get(base_url, timeout=1000).json()
            if isinstance(reponse, list) and reponse:
                r = reponse[0]['data']['children'][0]['data']
                parse_content(r)
                all_post.append(r)
            else:
                lst_invalide_link.add(base_url)
                write_lines(f'{basename}-invalide-link.txt', sorted(lst_invalide_link))
            
            time.sleep(i+round(random.random(),1))
    
    run_animation(read_all_link, f'Reading links in "{file}"')
    
    lines = get_filtered_post(
        source_data=all_post,
        exclude_url=args.exclude_url,
    )
    lines = [e.to_string() for e in lines]
    
    write_lines(f'{basename}.csv', lines)
    
    print(f'Data extracted from "{file}".', 'Post found:', len(lines),'Invalide link:',len(lst_invalide_link))
