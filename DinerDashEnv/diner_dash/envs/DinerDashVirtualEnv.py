import random
from queue import Queue

import more_itertools as mit

from copy import deepcopy

from diner_dash.envs.Transition import step_forward


class DinerDashVirtualEnv:
    advance_cus_threshold = 100000

    def __init__(self):
        self.uuid = "-1"
        self.flash_sim = False
        self.last_ob = None

        self.my_tables = []
        self.my_queue = []
        self.queue_waiting = []
        self.queue_size_history = []
        self.item_hold = []
        self.food_counters = [-1, -1, -1, -1, -1]
        self.ob = []

        self.steps_passed = 0
        self.next_new_group_time = 0
        self.flo_target = 0
        self.table_lost = 0
        self.master_score = 0

        """
        floTarget:0-8
        tablesLost : 0-5
        masterScore: 0-100000
        foodCounter1: -1, 1,2,3,4,5,6
        foodCounter2: -1, 1,2,3,4,5,6
        foodCounter3: -1, 1,2,3,4,5,6
        foodCounter4: -1, 1,2,3,4,5,6
        foodCounter5: -1, 1,2,3,4,5,6
        table1_status: none, reading, ready, ordered, eating, dishes, billme
        table1_seats: 2,4,6
        table1_havePep: yes, no
        queue1_redCount: 0-1000
        queue1_hapCount: 0-1000
        queue1_cusType: 1,2 
        queue1_size: 1-6
        """
        """
        self.observation_space = np.array([spaces.Discrete(9),  # flo target
                                           spaces.Discrete(6),  # tablesLost
                                           spaces.Box(low=0, high=100000, shape=(1,)),  # masterScore
                                           spaces.Discrete(7),  # foodCounter1
                                           spaces.Discrete(7),  # foodCounter2
                                           spaces.Discrete(7),  # foodCounter3
                                           spaces.Discrete(7),  # foodCounter4
                                           spaces.Discrete(7),  # foodCounter5
                                           spaces.Discrete(7),  # table6_status
                                           spaces.Discrete(3),  # table6_seats
                                           spaces.Discrete(2),  # table6_have_peps
                                           spaces.Discrete(7),  # table5_status
                                           spaces.Discrete(3),  # table5_seats
                                           spaces.Discrete(2),  # table5_have_peps
                                           spaces.Discrete(7),  # table4_status
                                           spaces.Discrete(3),  # table4_seats
                                           spaces.Discrete(2),  # table4_have_peps
                                           spaces.Discrete(7),  # table3_status
                                           spaces.Discrete(3),  # table3_seats
                                           spaces.Discrete(2),  # table3_have_peps
                                           spaces.Discrete(7),  # table2_status
                                           spaces.Discrete(3),  # table2_seats
                                           spaces.Discrete(2),  # table2_have_peps
                                           spaces.Discrete(7),  # table1_status
                                           spaces.Discrete(3),  # table1_seats
                                           spaces.Discrete(2),  # table1_have_peps
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue1_redCount
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue1_hapCount
                                           spaces.Discrete(2),  # queue1_cusType
                                           spaces.Box(low=1, high=6, shape=(1,)),  # queue1_size
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue2_redCount
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue2_hapCount
                                           spaces.Discrete(2),  # queue2_cusType
                                           spaces.Box(low=1, high=6, shape=(1,)),  # queue2_size
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue3_redCount
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue3_hapCount
                                           spaces.Discrete(2),  # queue3_cusType
                                           spaces.Box(low=1, high=6, shape=(1,)),  # queue3_size
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue4_redCount
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue4_hapCount
                                           spaces.Discrete(2),  # queue4_cusType
                                           spaces.Box(low=1, high=6, shape=(1,)),  # queue4_size
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue5_redCount
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue5_hapCount
                                           spaces.Discrete(2),  # queue5_cusType
                                           spaces.Box(low=1, high=6, shape=(1,)),  # queue5_size
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue6_redCount
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue6_hapCount
                                           spaces.Discrete(2),  # queue6_cusType
                                           spaces.Box(low=1, high=6, shape=(1,)),  # queue6_size
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue7_redCount
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # queue7_hapCount
                                           spaces.Discrete(2),  # queue7_cusType
                                           spaces.Box(low=1, high=6, shape=(1,))  # queue7_size
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # table1_hapCount
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # table2_hapCount
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # table3_hapCount
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # table4_hapCount
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # table5_hapCount
                                           spaces.Box(low=0, high=1000, shape=(1,)),  # table6_hapCount
                                           ])
        """
        """
        0: no op
        1-6: move to table i
        7: submit order
        8-13: pick food (9 -> first ordered food, 10 -> 2nd)
        14: move to dish collection point
        15-20: pick group to seat (15-20 -> first group in queue to table 1 - 6)
        """
        # self.action_space = spaces.Discrete(21)

    def step(self, action):
        action = int(action)
        last_score = self.master_score
        step_forward(self, action)

        reward = self.master_score - last_score
        episode_over = self.table_lost >= 5
        self.ob = self.get_simple_ob()
        return self.ob, reward, episode_over, {}

    def reset_tables(self):
        table_size = [4, 4, 2, 6, 4, 4]
        self.my_tables = []
        for size in table_size:
            table = {
                'status': 0,
                'size': size,
                'people': None,
                'start_read_time': -1,
                'start_eat_time': -1,
                'colors': [0] * size,
                'combo': [0] * size
            }
            self.my_tables.append(table)

    def generate_queue_waiting_list(self):
        # As every deepcopy of the env breaks the random seed, thus only random groups at start
        for i in range(200):
            cus_type = random.randint(1, 2)
            size = random.randint(1, 6)

            self.queue_waiting.append((cus_type, size))

    def new_queue_group(self):
        if len(self.my_queue) >= 7:
            return

        cus_type, size = self.queue_waiting[len(self.queue_size_history) % len(self.queue_waiting)]

        people = {}
        people['cus_type'] = cus_type
        people['hap'] = 600 if cus_type == 1 else 800
        people['tem_hap'] = 100  # tem_hap will be deducted first, then hap
        people['hap_take'] = 12 if cus_type == 1 else 7  # every unit time deduct amount
        people['size'] = size
        # people['colors'] = []

        # for i in range(people['size']):
        #     people['colors'].append(colors)

        self.my_queue.append(people)
        self.queue_size_history.append(people['size'])

        # seconds = int(self.steps_passed / 1000)
        # seconds = 7 if seconds >= 8 else seconds
        # self.next_new_group_time = self.steps_passed + random.randint(8 - seconds, 12 - seconds)  # 8 - 25
        self.next_new_group_time = self.steps_passed + 8  # 8 - 25

    def get_simple_ob(self):
        state = []

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

        # table status 6 x 9
        for index, table in enumerate(self.my_tables):
            state.append(table['status'])
            state.append(table['size'])
            if table['people']:
                # categorized as happiness level
                state.append(table['people']['hap'] // 200)
            else:
                # NA
                state.append(-1)

            # colors = list(mit.padded(table['colors'], 0, 6))
            # state.extend(colors)

        # food counter status 6
        for i in range(1, 7):
            if i in self.food_counters:
                state.append(1)
            else:
                state.append(0)

        # waiting group status 7 x 8
        for i in range(7):
            if i > len(self.my_queue) - 1:
                # group not exist
                state.extend([0] * 2)
                continue

            group = self.my_queue[i]
            state.append(group['hap'] // 200)
            state.append(group['size'])
            # colors = list(mit.padded(group['colors'], 0, 6))
            # state.extend(colors)

        # item in hand status
        map = {
            "order": 0,
            "food": 6,
            "dish": 12
        }
        for i in range(2):
            if i > len(self.item_hold) - 1:
                state.append(0)
                continue

            item = self.item_hold[i]
            base = map[item.split("_")[0]]
            num = base + int(item.split("_")[1])
            state.append(num)
            # 1-6 order_1 - order_6
            # 7-12 food_1 - food_6
            # 13-18 dish_1 - dish_6

        return state

    def duplicate(self):
        return deepcopy(self)

    def load_from_simple_ob(self, ob):
        self.reset()
        self.my_queue = []

        # load tables
        for i in range(6):
            table_idx = i * 3
            self.my_tables[i]['status'] = ob[table_idx]
            if self.my_tables[i]['status'] not in [0, 5]:
                # people on table
                hap = ob[table_idx + 2] * 200
                people = {'cus_type': 1, 'hap': hap, 'tem_hap': 100, 'hap_take': 12, 'size': 1}
                self.my_tables[i]['people'] = people

            if self.my_tables[i]['status'] == 1:
                self.my_tables[i]['start_read_time'] = self.steps_passed
            if self.my_tables[i]['status'] == 4:
                self.my_tables[i]['start_eat_time'] = self.steps_passed

        # load food counters
        food_counters = []
        for table_idx, food in enumerate(ob[18:24]):
            if food > 0:
                food_counters.append(table_idx + 1)
        food_counters += [-1] * (5 - len(food_counters))
        self.food_counters = food_counters

        # load groups
        for i in range(7):
            g_idx = 25 + i * 2
            size = ob[g_idx]
            hap = ob[g_idx + 1]

            if size == 0:
                break
                # self.my_queue.append(None)
            else:
                people = {'cus_type': 1, 'hap': hap, 'tem_hap': 100, 'hap_take': 12, 'size': size}
                self.my_queue.append(people)

        # load hand items

        for item in ob[-2:]:
            if item > 0:
                category = int((item - 1) / 6)
                table_num = int((item - 1) % 6) + 1
                if category == 0:
                    self.item_hold.append(f"order_{table_num}")
                elif category == 1:
                    self.item_hold.append(f"food_{table_num}")
                elif category == 2:
                    self.item_hold.append(f"dish_{table_num}")

    def print(self):
        self.ob = self.get_simple_ob()
        print("-----------------------------------------------------")
        print("step ", self.steps_passed)
        print("tables ob:", str(self.ob[:54]))
        print("food ob:", str(self.food_counters))
        print("hand item ob:", str(self.ob[-2:]))
        print("food_counters_start_time ", str(self.food_counters_start_time))
        print("item hold:  ", str(self.item_hold))
        print("my tables:")
        for table in self.my_tables:
            print(str(table))
        print("my queue:  ", str(self.my_queue))
        print("my queue history:  ", str(self.queue_size_history))
        print("-----------------------------------------------------")

    # def seed(self, seed):
    #     print("seed", seed)
    #     random.seed(seed)

    def reset(self):
        return self._reset()

    def _reset(self):
        self.steps_passed = 0
        self.next_new_group_time = 0
        self.item_hold = []
        self.my_queue = []
        self.queue_waiting = []
        self.queue_size_history = []
        self.generate_queue_waiting_list()

        if not self.flash_sim:
            self.new_queue_group()
        self.reset_tables()

        self.flo_target = 0
        self.table_lost = 0
        self.master_score = 0
        self.food_counters = [-1, -1, -1, -1, -1]
        self.food_counters_start_time = []
        self.ob = self.get_simple_ob()
        return self.ob


def test_transition():
    env = DinerDashVirtualEnv()
    env.reset()
    while True:
        env.print()
        action = input()
        while action is '':
            action = input()

        action = int(action)
        state, reward, done, _ = env.step(action)
        print("reward: ", reward)
        if done:
            break


if __name__ == '__main__':
    test_transition()
