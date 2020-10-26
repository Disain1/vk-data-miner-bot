async def sort_data(res):
	return sorted(res, key=lambda x: res.get(x))[-1]

async def getFriends(user_id, vk):
    result = vk.method(method='friends.get', values={'user_id':user_id}) # получаем друзей
    if result['items'] == []: # если все друзья скрыты или их нет(
	    result = vk.method(method='users.getFollowers', values={'user_id':user_id}) # получаем подписчиков
    return result['items']

async def resolveScreenName(screen_name, vk):
	try:
		user_id = vk.method( # id пользователя
			method='utils.resolveScreenName',
			values={'screen_name':screen_name}
		)['object_id']
	except Exception:
		user_id = None
	return user_id

async def search(res, vk):
	users = vk.method(
        method='users.get',
        values={'user_ids': res, 'fields':'city, bdate, schools'}
	)

	citys = {}
	bdates = {}
	schools = {}

	for user in users:
		if 'city' in user.keys():
			city = user['city']['title']
			
			if city in citys.keys(): citys[city] += 1
			else: citys[city] = 1

		if 'bdate' in user.keys():
			bdate = user['bdate'].split('.')
			
			if len(bdate) == 3:
				if bdate[2] in bdates.keys(): bdates[bdate[2]] += 1
				else: bdates[bdate[2]] = 1

		if 'schools' in user.keys() and user['schools'] != []:
			schools_list = user['schools']

			for school in schools_list:
				if school['name'] in schools.keys(): schools[school['name']] += 1
				else: schools[school['name']] = 1

	return citys, bdates, schools
