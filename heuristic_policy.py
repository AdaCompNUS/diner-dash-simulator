import gym


def step_forward(env, action):
    if 15 <= action <= 56:
        allocate_table(env, action)
    elif action == 14:
        move_dish_collection(env, action)
    elif 8 <= action <= 13:
        pick_food(env, action)
    elif action == 7:
        submit_order(env, action)
    elif 1 <= action <= 6:
        move_table(env, action)

    time_flow(env, action)


def allocate_table(env, action):
    table_index_raw = action - 15
    group_index = table_index_raw // 6
    table_index = table_index_raw % 6
    table = env.my_tables[table_index]
    if table['status'] > 0 or len(env.my_queue) == 0:
        # table not available or no queue
        return

    if len(env.my_queue) < group_index + 1:
        return

    people = env.my_queue[group_index]
    if people['size'] > table['size']:
        # cannot fit
        return

    if people['size'] <= 4 and table['size'] == 6:
        env.master_score -= 100

    # allocate table
    # remove from list and assign to table
    env.master_score += 10
    people = env.my_queue.pop(group_index)
    table['people'] = people
    table['status'] = 1
    table['people']['tem_hap'] += 100
    table['start_read_time'] = env.steps_passed
    if table['people']['hap'] < 700:
        env.master_score += round((700 - table['people']['hap']) / 5)


def move_dish_collection(env, action):
    new_item_hold = []

    found = False
    # clear dish in hand
    for item in env.item_hold:
        if 'dish' not in item:
            new_item_hold.append(item)
        else:
            found = True
            env.master_score += 10

    if not found:
        return

    env.master_score += 10
    env.item_hold = new_item_hold
    if env.flo_target == 8:
        env.flo_target = 0


def pick_food(env, action):
    table_num = action - 7

    if table_num not in env.food_counters:
        return

    # food ready for pick up
    if len(env.item_hold) >= 2:
        return

    # print("Action: pick_food ", table_num)
    # able to pick up
    env.master_score += 10
    table = env.my_tables[table_num - 1]
    if table['people']['hap'] < 700:
        env.master_score += round((700 - table['people']['hap']) / 10)
    food_index = env.food_counters.index(table_num)
    env.food_counters[food_index] = -1
    env.item_hold.append('food_' + str(table_num))
    env.flo_target = table_num


def submit_order(env, action):
    new_item_hold = []
    found = False

    # clear dish in hand
    for item in env.item_hold:
        if 'order' not in item:
            new_item_hold.append(item)
        else:
            found = True
            env.master_score += 10
            table_index = int(item.split("_")[1])
            env.food_counters_start_time.append({
                'table_index': table_index,
                'start_step': env.steps_passed
            })

    if not found:
        return

    # print("Action: submit_order")
    env.master_score += 10
    env.item_hold = new_item_hold
    if env.flo_target == 7:
        env.flo_target = 0


def move_table(env, table_index):
    table = env.my_tables[table_index - 1]

    if table['status'] == 2:
        # ready for order
        if len(env.item_hold) >= 2:
            # cannot hold more order
            return

        table['status'] = 3
        env.flo_target = 7
        env.item_hold.append('order_' + str(table_index))
        env.master_score += 20
        if table['people']['hap'] < 700:
            env.master_score += round((700 - table['people']['hap']) / 10)
        table['people']['tem_hap'] += 100
        return

    if table['status'] == 3:
        # ordered
        food = 'food_' + str(table_index)
        if food not in env.item_hold:
            return

        table['status'] = 4
        env.item_hold.pop(env.item_hold.index(food))
        env.master_score += 30
        if table['people']['hap'] < 700:
            env.master_score += round((700 - table['people']['hap']) / 10)
        table['people']['tem_hap'] += 100
        table['start_eat_time'] = env.steps_passed
        return

    if table['status'] == 6:
        # 6 is waiting for bill
        # 5 is wait to clear table

        table['status'] = 5
        table['start_read_time'] = -1
        table['start_eat_time'] = -1
        env.master_score += 50
        if table['people']['hap'] < 700:
            env.master_score += round((700 - table['people']['hap']) / 10)
        table['people'] = None
        return

    if table['status'] == 5:
        # 5 is wait to clear table
        if len(env.item_hold) >= 2:
            return

        env.flo_target = 8
        env.item_hold.append('dish_' + str(table_index))
        table['status'] = 0
        env.master_score += 40
        return


def time_flow(env, action):
    # to simulate time flow in the game
    # each action should takes 1 second in real game

    # compute queue
    new_my_queue = []
    for people in env.my_queue:
        people['tem_hap'] -= people['hap_take']
        if people['tem_hap'] < 0:
            people['hap'] -= people['hap_take']
            people['tem_hap'] = 0

        if people['hap'] > 0:
            new_my_queue.append(people)
        else:
            env.table_lost += 1

    env.my_queue = new_my_queue

    # compute table
    for table in env.my_tables:
        table_index = env.my_tables.index(table) + 1
        people = table['people']
        if people is None:
            continue

        people['tem_hap'] -= people['hap_take']
        if people['tem_hap'] < 0:
            people['hap'] -= people['hap_take']
            people['tem_hap'] = 0

        if people['hap'] > 0:
            continue

        # people run away
        table['status'] = 0
        table['people'] = None
        env.table_lost += 1

        # clear item hold
        new_item_hold = []
        for item in env.item_hold:
            if str(table_index) not in item:
                new_item_hold.append(item)

        env.item_hold = new_item_hold

        # clear food counter
        for index, value in enumerate(env.food_counters):
            if value == table_index:
                env.food_counters[index] = -1

            # clear food_counters_start_time

        env.food_counters_start_time = list(
            filter(lambda x: x['table_index'] != table_index, env.food_counters_start_time))
        # env.food_counters_start_time = filter(lambda x: x['table_index'] != table_index,env.food_counters_start_time)

        env.master_score -= 500
        # env.master_score = env.master_score if env.master_score >= 0 else 0

    # compute food counter
    new_food_counters_start_time = []
    for i, food_time in enumerate(env.food_counters_start_time):
        if env.steps_passed - food_time['start_step'] < 10:
            new_food_counters_start_time.append(food_time)
        else:
            # food is ready
            if food_time['table_index'] in env.food_counters:
                break

            for i2, food in enumerate(env.food_counters):
                if food == -1:
                    # env.food_counters[i] = table_index
                    env.food_counters[i2] = food_time['table_index']
                    break

    env.food_counters_start_time = new_food_counters_start_time

    # compute reading and eating
    for table in env.my_tables:
        if table['status'] == 1:
            assert table['start_read_time'] > -1
            if env.steps_passed - table['start_read_time'] >= 10:
                table['status'] = 2
                table['start_read_time'] = -1

        if table['status'] == 4:
            assert table['start_eat_time'] > -1
            if env.steps_passed - table['start_eat_time'] >= 10:
                table['status'] = 6
                table['start_eat_time'] = -1

    # compute new group
    if env.steps_passed > env.next_new_group_time:
        env.new_queue_group()

    env.steps_passed += 1
    return


def plan(env):
    max_reward = 0
    action = 0

    for a in range(57):
        env_temp = env.duplicate()
        step_forward(env_temp, a)
        reward = env_temp.master_score - env.master_score
        if reward > max_reward:
            action = a
            max_reward = reward

    return action


if __name__ == '__main__':
    env = gym.make('diner_dash:DinerDash-v0').unwrapped
    state = env.reset()

    done = False
    reward_sum = 0
    while not done:
        action = plan(env.env)
        state, reward, done, _ = env.step(action)
        reward_sum += reward

        if env.env.steps_passed % 100 == 0:
            print(f"Steps {env.env.steps_passed}, reward: {reward_sum}")

    print("Total reward", reward_sum)
