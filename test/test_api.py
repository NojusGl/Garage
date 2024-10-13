import requests

HOST = 'localhost'
PORT = 8080

def test_registering_and_getting_garage():
  register_garage("1", 10, "Geroji g. 1, Kaunas")
  garage = get_garage("1").json()

  assert garage["id"] == "1", "Garažo id nesutampa"
  assert garage["spots"] == 10, "Garažo vietos išsaugotos neteisingai"
  assert garage["address"] == "Geroji g. 1, Kaunas", "Garažo adresas išsaugotas neteisingai"

def test_garage_configuration():
  register_garage("2", 10, "Geroji g. 2, Kaunas")

  garage = get_garage("2").json()
  assert garage["spots"] == 10

  update_spots("2", 15)
  garage = get_garage("2").json()
  spots = garage["spots"]
  assert spots == 15

def test_occupying_spots():
  register_garage("3", 10, "Geroji g. 3, Kaunas")
  occupy_spot("3", "1", "ABC-123")
  occupier = get_spot_occupier("3", 1).text
  assert occupier == "ABC-123"

  occupy_spot("3", "2", "DEF-456")
  occupier = get_spot_occupier("3", 2).text
  assert occupier == "DEF-456"

  garage_status = get_garage_status("3").json()
  assert garage_status["occupiedSpots"] == 2
  assert garage_status["freeSpots"] == 8

  free_spot("3", "1")
  occupier_response = get_spot_occupier("3", 1, False)
  assert occupier_response.status_code == 204

  free_spot("3", "2")
  occupier_response = get_spot_occupier("3", 2, False)
  assert occupier_response.status_code == 204

  garage_status = get_garage_status("3").json()
  assert garage_status["occupiedSpots"] == 0
  assert garage_status["freeSpots"] == 10


def register_garage(garage_id, spots, address, assrt = True):
  garage_url = f"http://{HOST}:{PORT}/garage"
  body = {"id": garage_id, "spots": spots, "address": address}
  response = requests.put(garage_url, json=body)

  if assrt:
    assert response.status_code == 201

  return response

def get_garage(garage_id, assrt = True):
  garage_url = f"http://{HOST}:{PORT}/garage/"
  response = requests.get(garage_url + "/" + garage_id)

  if assrt:
    assert response.status_code == 200

  return response

def get_spots(garage_id, assrt = True):
  garage_url = f"http://{HOST}:{PORT}/garage/"
  response = requests.get(garage_url + "/" + garage_id + "/configuration/spots")

  if assrt:
    assert response.status_code == 200

  return response

def update_spots(garage_id, spots, assrt = True):
  garage_url = f"http://{HOST}:{PORT}/garage/"
  response = requests.post(garage_url + "/" + garage_id + "/configuration/spots", json={ "spots": spots })

  if assrt:
    assert response.status_code == 200

  return response

def occupy_spot(garage_id, spot_id, license_no,  assrt = True):
  garage_url = f"http://{HOST}:{PORT}/garage/{garage_id}/spots/{spot_id}"
  body = { "licenseNo" : license_no }
  response = requests.post(garage_url, json=body)

  if assrt:
    assert response.status_code == 200

  return response

def get_spot_occupier(garage_id, spot_id, assrt = True):
  garage_url = f"http://{HOST}:{PORT}/garage/{garage_id}/spots/{spot_id}"
  response = requests.get(garage_url)

  if assrt:
    assert response.status_code == 200

  return response

def free_spot(garage_id, spot_id, assrt = True):
  garage_url = f"http://{HOST}:{PORT}/garage/{garage_id}/spots/{spot_id}"
  response = requests.delete(garage_url)

  if assrt:
    assert response.status_code == 200

  return response

def get_garage_status(garage_id, assrt = True):
  garage_url = f"http://{HOST}:{PORT}/garage/"
  response = requests.get(garage_url + "/" + garage_id + "/status")

  if assrt:
    assert response.status_code == 200

  return response