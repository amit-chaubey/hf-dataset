import requests
import os
from tqdm import tqdm

def download_file(url, filename):
    """
    Download a file from a URL with progress bar
    """
    if os.path.exists(filename):
        print(f"{filename} already exists. Skipping download.")
        return
    
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    
    print(f"Downloaded {filename} successfully.")

def main():
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # URLs for the PDFs
    urls = {
        "data/Manifesto.pdf": "https://www.marxists.org/archive/marx/works/download/pdf/Manifesto.pdf",
        "data/Capital-Volume-I.pdf": "https://www.marxists.org/archive/marx/works/download/pdf/Capital-Volume-I.pdf"
    }
    
    # Download each PDF
    for filename, url in urls.items():
        download_file(url, filename)
    
    print("All PDFs downloaded successfully.")

if __name__ == "__main__":
    main() 