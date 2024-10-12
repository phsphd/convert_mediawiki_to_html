import re
import requests
import os

# Define the API endpoint
url = "http://134.202.192.176/api.php"  # Replace with your actual API URL

# Function to log in (if the site requires authentication)
def login(session, url, username, password):
    # Step 1: Get login token
    params = {
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json"
    }
    response = session.get(url, params=params)
    login_token = response.json()['query']['tokens']['logintoken']

    # Step 2: Send login request with credentials
    login_data = {
        "action": "login",
        "lgname": username,
        "lgpassword": password,
        "lgtoken": login_token,
        "format": "json"
    }
    session.post(url, data=login_data)
    print("Logged in successfully!")

# Function to download a single page's HTML
def download_page(session, url, title, output_dir):
    params = {
        "action": "parse",
        "page": title,
        "format": "json",
        "prop": "text"
    }
    response = session.get(url, params=params)
    data = response.json()

    if 'error' in data:
        print(f"Error fetching page {title}: {data['error']['info']}")
        return

    html_content = data['parse']['text']['*']

    # Replace spaces with underscores in the title for the filename
    sanitized_title = title.replace(' ', '_')
    filename = os.path.join(output_dir, f"{sanitized_title.replace('/', '_')}.html")

    # Remove comment blocks from the HTML
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)

    # Save the cleaned HTML content to a file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"Saved {title} to {filename}")

# Function to retrieve all page titles
def get_all_pages(session, url):
    all_titles = []
    params = {
        "action": "query",
        "list": "allpages",
        "aplimit": "max",  # Get maximum number of pages per request
        "format": "json"
    }
    while True:
        response = session.get(url, params=params)
        data = response.json()
        pages = data['query']['allpages']
        all_titles.extend([page['title'] for page in pages])

        # Check if there are more pages to be fetched
        if 'continue' in data:
            params['apcontinue'] = data['continue']['apcontinue']
        else:
            break

    return all_titles

# Main function to download the entire website
def download_entire_site(api_url, output_dir, username=None, password=None):
    # Create a session to manage cookies and state
    session = requests.Session()

    # Log in if username and password are provided
    if username and password:
        login(session, api_url, username, password)

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get the list of all pages
    all_titles = get_all_pages(session, api_url)
    print(f"Found {len(all_titles)} pages to download.")

    # Download each page as HTML
    for title in all_titles:
        download_page(session, api_url, title, output_dir)

# Entry point of the script
if __name__ == "__main__":
    api_url = "http://34.202.92.176/api.php"  # Replace with your actual API URL
    output_dir = "downloaded_wiki"  # Directory to save the downloaded HTML files
    username = None  # Optional: provide username if login is required
    password = None  # Optional: provide password if login is required

    # Call the function to download the entire site
    download_entire_site(api_url, output_dir, username, password)
