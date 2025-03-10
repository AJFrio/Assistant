import requests

url = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC8914635/'
response = requests.get(url)
print(response.status_code)
