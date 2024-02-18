user_id = '5011353332'  # trump
amount = 10

def get_user_followers(user_id, amount):
    max_id = ''
    return_hits = 0
    while return_hits < amount:
        users, max_id = cl.user_followers_v1_chunk(user_id, max_amount=200, max_id=max_id)
        yield from users
        return_hits += len(users)
        if not max_id: 
            break

for user in get_user_followers(user_id, amount):
    userstr = f'{user.pk} {user.username} {user.full_name}\n'
    with open(f'{user_id}_{amount}.txt', 'a', encoding='utf-8') as fp:
        fp.write(userstr)