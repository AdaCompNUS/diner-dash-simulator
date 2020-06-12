import gym
# import requests
# import json
import time
import numpy as np

env = gym.make('gym_duckietown:Duckietown-udem1-v0')
ob = env.reset()
env.render()

time.sleep(3)
result = env.step(np.array([0.35, +1]))
env.render()
time.sleep(3)
result = env.step(np.array([0.35, +1]))
env.render()
time.sleep(3)
result = env.step(np.array([0.35, +1]))
env.render()
time.sleep(2)
ob = env.reset()


# def register_env():
#     r = requests.post("http://localhost:9000/api/registerEnv", data={})
#     return json.loads(r.text)["uuid"]
#
#
# def get_state(uuid):
#     state = None
#
#     while state is None:
#         try:
#             r = requests.post("http://localhost:9000/api/getState/" + uuid, data={})
#             state = json.loads(r.text)
#
#         except Exception:
#             time.sleep(0.05)
#
#     return process_state(state)
#
#
# def process_state(state):
#     status_map = {
#         "none": 0,
#         "reading": 1,
#         "ready": 2,
#         "ordered": 3,
#         "eating": 4,
#         "dishes": 5,
#         "billme": 6
#     }
#
#     ob = []
#     ob.append(int(state['tablesLost']))
#     ob.append(int(state['masterScore']))
#     ob.extend(json.loads(state['foodCounters']))
#     for table in json.loads(state['tableArray']):
#         ob.append(status_map[table['myStatus']])
#         ob.append(table['numChairs'])
#         ob.append(1 if table['havePeeps'] else 0)
#
#     for queue in json.loads(state['myQueue']):
#         ob.append(queue['redCount'])
#         ob.append(queue['hapCount'])
#         ob.append(queue['cusType'])
#         ob.append(len(queue['myPeople']))
#
#     # pad to fixed length 45
#     ob.extend([0] * (45 - len(ob)))
#     return ob
#
#
# def update_action(uuid, action):
#     data = {
#         "uuid": uuid,
#         "action": action
#     }
#     headers = {'Content-Type': 'application/json'}
#     r = requests.post("http://localhost:9000/api/updateAction", headers=headers, data=json.dumps(data))
#     print(r.text)
#
#
# uuid = register_env()
# state = get_state(uuid)
# time.sleep(1)
# update_action(uuid, 15)
# state = get_state(uuid)
# time.sleep(10)
# update_action(uuid, 1)
# state = get_state(uuid)
# time.sleep(1)
# update_action(uuid, 7)
# state = get_state(uuid)
#
# print(state)
