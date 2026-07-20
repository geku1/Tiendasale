from app import app

with app.test_client() as client:
    resp = client.post('/chat', json={'mensaje':'Quiero un RPG'})
    print('STATUS', resp.status_code)
    print(resp.get_data(as_text=True))
