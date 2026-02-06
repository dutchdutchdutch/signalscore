
from ddgs import DDGS
import sys

def research_company(company_name: str):
    print(f"🔎 Researching {company_name}...")
    
    # 1. Tech Blog Search
    queries = [
        f"{company_name} engineering blog",
        f"{company_name} tech blog",
        f"{company_name} artificial intelligence blog",
        f"{company_name} open source github"
    ]
    
    results = []
    
    with DDGS() as ddgs:
        for q in queries:
            print(f"  Querying: '{q}'...")
            try:
                # DDGS().text() returns an iterable of dicts
                search_res = list(ddgs.text(q, max_results=2))
                
                for res in search_res:
                    print(f"    Found: {res.get('title')} -> {res.get('href')}")
                    results.append(res.get('href'))
                    
                if not search_res:
                     print("    (No results found)")
                     
            except Exception as e:
                print(f"    Error: {e}")

    # Deduplicate
    unique_urls = list(set(r for r in results if r))
    print(f"\n✅ Found {len(unique_urls)} unique potential sources:")
    for u in unique_urls:
        print(f" - {u}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Netflix"
    research_company(target)
