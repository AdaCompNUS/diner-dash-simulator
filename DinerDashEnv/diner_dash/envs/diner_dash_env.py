import gym
from gym import error, spaces, utils
import requests
import json
import time
import numpy as np
import random

from diner_dash.envs.DinerDashVirtualEnv import DinerDashVirtualEnv


class DinerDashEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    advance_cus_threshold = 100000
    env = None

    def __init__(self):
        self.uuid = "-1"
        self.flash_sim = False

        """
        table1_status
        table1_size
        table1_hap
        ...
        table6_status
        table6_size
        table6_hap
        
        table_1_food : 0 not ready for collection, 1 : ready
        ...
        table_6_food
        
        group_1_hap
        group_1_size
        ...
        group_7_hap
        group_7_size
        
        hand_item1
        hand_item2
        """
        # self.observation_space = np.array([spaces.Discrete(7),  # table1-6_status
        #                                    spaces.Discrete(4),  # table1-6_seats
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # table1-6_happiness
        #                                    spaces.Discrete(7),  # table1-6_status
        #                                    spaces.Discrete(4),  # table1-6_seats
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # table1-6_happiness
        #                                    spaces.Discrete(7),  # table1-6_status
        #                                    spaces.Discrete(4),  # table1-6_seats
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # table1-6_happiness
        #                                    spaces.Discrete(7),  # table1-6_status
        #                                    spaces.Discrete(4),  # table1-6_seats
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # table1-6_happiness
        #                                    spaces.Discrete(7),  # table1-6_status
        #                                    spaces.Discrete(4),  # table1-6_seats
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # table1-6_happiness
        #                                    spaces.Discrete(7),  # table1-6_status
        #                                    spaces.Discrete(4),  # table1-6_seats
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # table1-6_happiness
        #
        #                                    spaces.Discrete(2),  # food_ready for table1-6
        #                                    spaces.Discrete(2),  # food_ready for table1-6
        #                                    spaces.Discrete(2),  # food_ready for table1-6
        #                                    spaces.Discrete(2),  # food_ready for table1-6
        #                                    spaces.Discrete(2),  # food_ready for table1-6
        #                                    spaces.Discrete(2),  # food_ready for table1-6
        #
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # group1-7 happiness
        #                                    spaces.Discrete(7),  # group 1-7 size
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # group1-7 happiness
        #                                    spaces.Discrete(7),  # group 1-7 size
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # group1-7 happiness
        #                                    spaces.Discrete(7),  # group 1-7 size
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # group1-7 happiness
        #                                    spaces.Discrete(7),  # group 1-7 size
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # group1-7 happiness
        #                                    spaces.Discrete(7),  # group 1-7 size
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # group1-7 happiness
        #                                    spaces.Discrete(7),  # group 1-7 size
        #                                    spaces.Box(low=0, high=1000, shape=(1,)),  # group1-7 happiness
        #                                    spaces.Discrete(7),  # group 1-7 size
        #
        #                                    # 1-6 order_1 - order_6
        #                                    # 7-12 food_1 - food_6
        #                                    # 13-18 dish_1 - dish_6
        #                                    spaces.Discrete(19),  # item in hand 1
        #                                    spaces.Discrete(19),  # item in hand 2
        #                                    ])

        """
            if 15 <= action <= 56:
                allocate_table(env, action)
                # 15 - 20: allocate group 1 to table 1-6
                # 21 - 26: allocate group 2 to table 1-6
                ...
                # 51 - 56: allocate group 7 to table 1-6
            elif action == 14:
                move_to_dish_collection(env, action)
            elif 8 <= action <= 13:
                pick_food(env, action) # 8 -> pick food for table 1, 13 -> table 6
            elif action == 7:
                submit_order(env, action)
            elif 1 <= action <= 6:
                move_to_table(env, action)
        """

        self.low_state = np.array([0] * 40, dtype=np.float32)
        self.high_state = np.array([20] * 40, dtype=np.float32)

        self.viewer = None
        self.observation_space = spaces.Box(low=self.low_state, high=self.high_state, dtype=np.float32)
        self.action_space = spaces.Discrete(57)

    def step(self, action):

        if not self.flash_sim:
            return self.env.step(action)

        action = int(action)
        last_score = self.env.master_score
        self.update_action(action)
        time.sleep(1)
        self.get_state()

        reward = self.env.master_score - last_score
        episode_over = self.env.table_lost >= 5
        return self.env.get_simple_ob(), reward, episode_over, {}

    def reset(self):
        self.env = DinerDashVirtualEnv()
        self.env.flash_sim = self.flash_sim
        self.env.reset()

        if not self.flash_sim:
            return self.env.get_simple_ob()

        self.end_env()
        self.uuid = self.register_env()
        self.get_state()
        return self.env.get_simple_ob()

    def seed(self, seed):
        random.seed(seed)
        return 0

    """
    ----------------------- Flash Simulator Functions -----------------------
    """

    def render(self, mode='human'):
        pass

    def register_env(self):
        r = requests.post("http://localhost:9000/api/registerEnv", data={})
        return json.loads(r.text)["uuid"]

    def end_env(self):
        requests.post("http://localhost:9000/api/endGame/" + self.uuid, data={})
        self.uuid = ""

    def update_action(self, action):
        data = {
            "uuid": self.uuid,
            "action": action
        }
        headers = {'Content-Type': 'application/json'}
        requests.post("http://localhost:9000/api/updateAction", headers=headers, data=json.dumps(data))

    def get_state(self):
        state = None
        count = 0
        max_count = 600

        while state is None:
            if count >= max_count:
                self.env.table_lost = 6
                return self.env.get_simple_ob()
            try:
                r = requests.post("http://localhost:9000/api/getState/" + self.uuid, data={})
                state = json.loads(r.text)

            except Exception:
                time.sleep(0.05)
                count += 1

        return self.process_state(state)

    def process_state(self, state):
        status_map = {
            "none": 0,
            "reading": 1,
            "ready": 2,
            "ordered": 3,
            "eating": 4,
            "dishes": 5,
            "billme": 6
        }
        self.env.table_lost = int(state['tablesLost'])
        self.env.master_score = int(state['masterScore'])
        self.env.food_counters = json.loads(state['foodCounters'])

        # tables
        table_arr_text = state['tableArray']
        table_arr_text = table_arr_text.replace("undefined", "null")
        for table_json in json.loads(table_arr_text):
            table_index = table_json['myNum'] - 1
            table = self.env.my_tables[table_index]
            table['start_read_time'] = self.env.steps_passed
            table['start_eat_time'] = self.env.steps_passed
            table['status'] = status_map[table_json['myStatus']]
            if table['status'] in [0, 5]:
                table['people'] = None
            else:
                table['people'] = {
                    'hap': table_json['hapCount'] if table_json['hapCount'] else 0,
                    'tem_hap': 0,
                    'hap_take': 12
                }

            for i in range(table['size']):
                table['colors'][i] = table_json['chair' + str(i + 1)]['comCol']
                table['combo'][i] = table_json['chair' + str(i + 1)]['combo']

        # queues
        self.env.my_queue = []
        for queue in json.loads(state['myQueue'])[::-1]:
            people = {}
            people['cus_type'] = queue['cusType']
            people['hap'] = queue['hapCount']
            people['tem_hap'] = queue['pausedTimer']
            people['hap_take'] = 12 if people['cus_type'] == 1 else 7  # every unit time deduct amount
            people['size'] = len(queue['myPeople'])
            people['colors'] = queue['myPeople']
            self.env.my_queue.append(people)

        # hand items
        self.env.item_hold = []
        hand1_text = state['hand1'].replace("dishes", "dish")
        hand2_text = state['hand2'].replace("dishes", "dish")
        try:
            hand1 = json.loads(hand1_text)
            if hand1['idNum'] > 0 and len(hand1['holding']) > 0:
                self.env.item_hold.append(hand1['holding'] + "_" + str(hand1['idNum']))
        except Exception:
            pass

        try:
            hand2 = json.loads(hand2_text)
            if hand2['idNum'] > 0 and len(hand2['holding']) > 0:
                self.env.item_hold.append(hand2['holding'] + "_" + str(hand2['idNum']))
        except Exception:
            pass
        return self.env.get_simple_ob()
