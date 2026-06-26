import re
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime

def fetch_rss_posts(feed_url):
    try:
        req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        posts = []
        for item in root.findall('.//item')[:3]:
            title = item.find('title').text.strip()
            link = item.find('link').text.strip()
            pub_date = item.find('pubDate').text.strip()
            try:
                # e.g., Wed, 28 Jan 2026 04:30:00 GMT or 2026-01-28
                dt = datetime.strptime(pub_date[:16], '%a, %d %b %Y')
                formatted_date = dt.strftime('%b %d, %Y')
            except Exception:
                formatted_date = pub_date
            posts.append(f"- ✍️ [{title}]({link}) ({formatted_date})")
        return "\n".join(posts) if posts else "- No recent posts found."
    except Exception as e:
        print(f"Error fetching RSS: {e}")
        return "- Failed to retrieve blog posts."

def fetch_latest_repos(username):
    try:
        url = f"https://api.github.com/users/{username}/repos?sort=pushed&per_page=10"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            repos = json.loads(response.read().decode('utf-8'))
        
        # Filter out forks and sort by pushed_at descending
        filtered_repos = [r for r in repos if not r['fork']]
        filtered_repos.sort(key=lambda x: x.get('pushed_at', ''), reverse=True)
        
        lines = []
        for repo in filtered_repos[:4]:
            name = repo['name']
            html_url = repo['html_url']
            desc = repo['description'] or "No description provided."
            lang = repo['language'] or "Misc"
            stars = repo['stargazers_count']
            lines.append(
                f"<tr>"
                f"<td width='65%'>🚀 <b><a href='{html_url}'>{name}</a></b><br/><sub>{desc}</sub></td>"
                f"<td width='20%' align='center'><code>{lang}</code></td>"
                f"<td width='15%' align='center'>⭐ {stars}</td>"
                f"</tr>"
            )
        
        if lines:
            return "<table>\n" + "\n".join(lines) + "\n</table>"
        return "- No repositories found."
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return "- Failed to retrieve repositories."

def fetch_publications():
    # Direct reference to the main preprint publication
    title = "Structure-Based Drug Design of Novel Inhibitors Targeting the Thiamine Biosynthesis Pathway in Bacteria"
    link = "https://www.biorxiv.org/"
    return f"- 🧬 **[{title}]({link})**<br/><sub><b>N. Krishna</b>, et al. • bioRxiv (Preprint)</sub>"

def update_block(readme_content, block_name, new_content):
    pattern = rf"(<!-- {block_name}:START -->)(.*?)(<!-- {block_name}:END -->)"
    replacement = rf"\1\n{new_content}\n\3"
    return re.sub(pattern, replacement, readme_content, flags=re.DOTALL)

def main():
    readme_path = "README.md"
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("README.md not found.")
        return

    blog_posts = fetch_rss_posts("https://nikilblog.netlify.app/rss.xml")
    latest_repos = fetch_latest_repos("greenrace666")
    publications = fetch_publications()

    content = update_block(content, "BLOG-POST-LIST", blog_posts)
    content = update_block(content, "LATEST-REPOS", latest_repos)
    content = update_block(content, "PUBLICATIONS", publications)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("README updated successfully.")

if __name__ == "__main__":
    main()
