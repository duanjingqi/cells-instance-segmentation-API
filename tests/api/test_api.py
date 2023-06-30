# Configure Python environment
import random
from starlette.testclient import TestClient


def test_root(test_client: TestClient):
        
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json()['Application'] == 'CellSegger-0.0'


def test_single_prediction(image_path, test_client: TestClient, generate_multipartformdata):

    image = random.choice(list(image_path.glob('*')))
    data = generate_multipartformdata(image)
    response = test_client.post('/predict/single', files = {'infile': data})

    assert response.status_code == 200
    assert response[0]['Prediction'].shape == (256, 256, 3)
 

def test_batch_prediction(image_path, test_client: TestClient, generate_multipartformdata):

    all_images = list(image_path.glob('*'))
    data = generate_multipartformdata(all_images)
    response = test_client.post('/predict/batch', files = {'infiles': data})

    assert response.status_code == 200
    assert len(response) == len(data)
    assert response[random.randint(0, len(data))]['Prediction'].shape == (256, 256, 3)

def test_txt_prediction(fake_txt, test_client: TestClient, generate_multipartformdata):

    fake_data = fake_txt()
    response = test_client.post('/predict/single', files = {'infile': fake_data})

    assert response.status_code == 400