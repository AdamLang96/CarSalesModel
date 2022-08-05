import requests as rq

URL = 'https://carsandbids.com/past-auctions/?page='
for i in range(160):
  r = rq.get(url = URL + str(i))
  print(f'iteration {i+1}')
  print(r.headers)
  print(r.text)
  print('\n')