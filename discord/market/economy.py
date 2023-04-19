# ---- discord/market/economy.py ----
# market file. manages economy for overarching bot

import json
import os
from traceback import format_exc

def info(mes):
    print(f'INFO - {mes}')
def error(mes):
    print(f'ERROR - {mes}')

#TODO: implement api calls to wyatt's web server to prevent data issues

# reads json file from passed path
def read_json(path) -> dict:
    with open(path,'r') as r:
        data = json.loads(r.read())
    return data

# write json file to passed path
def write_json(path,data):
    with open(path,'w') as w:
        json.dump(data,w)

# checks if file exists
def is_file(path) -> bool:
    try:
        f = open(path)
        f.close()
        return True
    except FileNotFoundError:
        return False

class Market():
    def __init__(self):
        self.users_path = 'market/user_data/users.json'
        self.users = read_json(self.users_path)
        self.shop_items_path = 'market/goods.json'
        self.perms_path = 'market/perms.json'

    def refresh_users(self):
        self.users = read_json(self.users_path)

    def update_users(self):
        write_json(self.users_path,self.users)

    def error_response(self,func_name, error):
        return False, f'Couldn\'t process function {func_name}. {error} - {format_exc()}'

    def get_perms_list(self):
        return read_json(self.perms_path)

    def blacklist(self,user_id):
        try:
            path = self.perms_path
            data = read_json(path)
            if user_id in data['whitelist']:
                data['whitelist'].remove(int(user_id))
            if user_id not in data['blacklist']:
                data['blacklist'].append(int(user_id))
            else:
                return False, 'user already blacklisted'
            write_json(path,data)
            return True, 'user blacklisted'
        except Exception as e:
            return self.error_response('blacklist',e)

    def remove_blacklist(self,user_id):
        try:
            path = self.perms_path
            data = read_json(path)
            if user_id in data['blacklist']:
                data['blacklist'].remove(int(user_id))
            else:
                return False, 'user wasn\'t blacklisted'
            write_json(path,data)
            return True, 'user blacklist removed'
        except Exception as e:
            return self.error_response('remove_blacklist',e)

    def give_admin(self,user_id):
        try:
            path = self.perms_path
            data = read_json(path)
            if user_id in data['blacklist']:
                data['blacklist'].remove(int(user_id))
            if user_id not in data['whitelist']:
                data['whitelist'].append(int(user_id))
            else:
                return False, 'user already whitelisted'
            write_json(path,data)
            return True, 'user whitelist added'
        except Exception as e:
            return self.error_response('give_admin',e)

    def remove_admin(self,user_id):
        try:
            path = self.perms_path
            data = read_json(path)
            if user_id in data['whitelist']:
                data['whitelist'].remove(int(user_id))
            else:
                return False, 'user wasn\'t whitelisted'
            write_json(path,data)
            return True, 'user whitelist removed'
        except Exception as e:
            return self.error_response('remove_admin',e)

    def cheat_money(self,user_id, amount):
        try:
            self.refresh_users()
            if str(user_id) in list(self.users.keys()):
                self.users[str(user_id)]['balance'] += amount
                return True, 'amount added successfully'
            else:
                return False, 'user could not be located'
        except Exception as e:
            return self.error_response('cheat_money',e)

    # user interactions
    def create_user(self,user_id):
        try:
            self.refresh_users()
            if str(user_id) in list(self.users.keys()):
                return False, 'user file already exists'
            else:
                self.users[str(user_id)] = {
                    'balance': 0,
                    'inventory':{}
                }
                self.update_users()
                return True, 'user file created successfully'
        except Exception as e:
            return self.error_response('create_user',e)

    def delete_user(self,user_id):
        try:
            self.refresh_users()
            if str(user_id) in list(self.users.keys()):
                del self.users[str(user_id)]
                self.update_users()
                return True, 'user file deleted successfully'
            else:
                return False, 'user could not be located to delete'
        except Exception as e:
            return self.error_response('delete_user',e)

    def get_user_balance(self,user_id):
        try:
            self.refresh_users()
            if str(user_id) in list(self.users.keys()):
                return True, self.users[str(user_id)]['balance']
            else:
                return False, 'user could not be located'
        except Exception as e:
            return self.error_response('get_user_balance',e)

    def give_money(self,giver_id,user_id,amount):
        try:
            if amount <= 0:
                return False, 'amount value out of range'
            self.refresh_users()
            if int(giver_id) in self.users:
                if self.users[int(giver_id)]['balance'] < amount:
                    return False, 'amount value out of range'
                if str(user_id) not in self.users:
                    return False, 'user ID could not be located to transfer funds'
                self.users[str(user_id)]['balance'] += amount
                self.users[int(giver_id)]['balance'] -= amount
                self.update_users()
                return True, f'{user_id} given {amount} by {giver_id}'
            else:
                return False, 'giver ID could not be located to transfer funds'
        except Exception as e:
            return self.error_response('give_money',e)

    def lose_money(self, user_id, amount):
        try:
            if amount >= 0:
                return False, 'amount value out of range'
            self.refresh_users()
            if str(user_id) in list(self.users.keys()):
                self.users[str(user_id)]['balance'] -= amount
                if self.users[str(user_id)]['balance'] < 0:
                    self.users[str(user_id)]['balance'] = 0
                self.update_users()
                return True, f'{user_id} given {amount}'
            else:
                return False, 'giver ID could not be located to transfer funds'
        except Exception as e:
            return self.error_response('give_money',e)

    def sort_inventory(self, user_id):
        try:
            self.refresh_users()
            self.users[user_id] = dict(sorted(self.users[user_id].items(),key = lambda x:x))
            self.update_users()
            return True, 'Shop sorted successfully'
        except Exception as e:
            mes = f'Could not process sorting shop. {e} - {format_exc()}'
            error(mes)
            return False, mes

    def get_user_inventory(self,user_id):
        try:
            self.refresh_users()
            self.sort_inventory(str(user_id))
            self.update_users()
            return True, self.users[str(user_id)]['inventory']
        except Exception as e:
            return self.error_response('get_user_inventory',e)

    # market interactions 
    def add_item(self,name,price,description,role,toggle):
        try:
            path = self.shop_items_path
            data = read_json(path)
            if name not in data:
                data[name] = {
                    'price':price,
                    'description':description,
                    'toggle':toggle,
                    'role':int(role)
                }
                write_json(path,data)
                result = self.sort_shop()
                if result[0]:
                    return True, f'item successfully added: {name}:{data[name]}'
                return False, result[1]
            else:
                return False, 'item already exists'
        except Exception as e:
            return self.error_response('add_item',e)

    def edit_item(self,name,price,description,role,toggle):
        try:
            path = self.shop_items_path
            data = read_json(path)
            if name in data:
                data[name] = {
                    'price':price,
                    'description':description,
                    'toggle':toggle,
                    'role':role
                }
                write_json(path,data)
                result = self.sort_shop()
                if result[0]:
                    return True, f'item successfully updated: {name}:{data[name]}'
                return False, result[1]
            else:
                return False, 'item could not be located'
        except Exception as e:
            return self.error_response('edit_item',e)

    def remove_item(self,name):
        try:
            path = self.shop_items_path
            data = read_json(path)
            if name in data:
                del data[name]
                write_json(path,data)
                result = self.sort_shop()
                if result[0]:
                    return True, f'item successfully removed: {name}'
                return False, result[1]
            else:
                return False, 'item could not be located'
        except Exception as e:
            return self.error_response('remove_item',e)

    def sort_shop(self):
        try:
            write_json(self.shop_items_path,dict(sorted(read_json(self.shop_items_path).items(),key = lambda x:x)))
            return True, 'Shop sorted successfully'
        except Exception as e:
            mes = f'Could not process sorting shop. {e} - {format_exc()}'
            error(mes)
            return False, mes

    def buy_item(self,user_id,name):
        try:
            store_path = self.shop_items_path
            user_path = self.users[str(user_id)]
            store = read_json(store_path)
            if is_file(user_path):
                user_data = read_json(user_path)
            else:
                return False, 'couldn\'t locate user file'
            possible_items = []
            if not name.isnumeric():
                for item in list(store.keys()):
                    if name.lower() in item.lower():
                        info(item)
                        possible_items.append(item)
                if len(possible_items) > 1:
                    return False, f'Multiple items fit description: {possible_items}'
                elif len(possible_items) == 0:
                    return False, f'no matching items containing "{name}"'
                else:
                    item_name = possible_items[0]
            else:
                if int(name)-1 >= 0 and int(name)-1 <= len(list(store.keys())):
                    item_name = list(store.keys())[int(name)-1]
            if item_name in store:
                if item_name in user_data['inventory']:
                    return False, 'item already in inventory'
                if user_data['balance'] >= store[item_name]['price']:
                    user_data['balance'] -= store[item_name]['price']
                    user_data['inventory'][item_name] = {'description': store[item_name]['description'], 'toggle':store[item_name]['toggle'],'role':int(store[item_name]['role']),'activated': True}
                    write_json(user_path,user_data)
                    return True, item_name
                else:
                    return False, 'not enough balance present'
            else:
                return False, 'couldn\'t locate item in store'
        except Exception as e:
            return self.error_response('buy_item',e)

    def activate_item(self,user_id,name):
        try:
            user_path = self.users[str(user_id)]
            if is_file(user_path):
                user_data = read_json(user_path)
            else:
                return False, 'couldn\'t locate user file'
            possible_items = []
            if not name.isnumeric():
                for item in list(user_data['inventory'].keys()):
                    if name.lower() in item.lower():
                        info(item)
                        possible_items.append(item)
                if len(possible_items) > 1:
                    return False, f'Multiple items fit description: {possible_items}'
                elif len(possible_items) == 0:
                    return False, f'no matching items containing "{name}"'
                else:
                    item_name = possible_items[0]
            else:
                item_name = list(user_data.keys())[int(name)]
            inv = user_data['inventory']
            if item_name in inv:
                if inv[item_name]['toggle']:
                    if inv[item_name]['activated'] == True:
                        return False, f'{item_name} is already activated'
                    inv[item_name]['activated'] = True
                    user_data['inventory'] = inv
                    write_json(user_path,user_data)
                    return True, item_name
                else:
                    return False, f'{item_name} is not able to toggle'
            else:
                return False, f'{item_name} is not in inventory'
        except Exception as e:
            return self.error_response('activate_item',e)

    def deactivate_item(self,user_id,name):
        try:
            user_path = self.users[str(user_id)]
            if is_file(user_path):
                user_data = read_json(user_path)
            else:
                return False, 'couldn\'t locate user file'
            possible_items = []
            if not name.isnumeric():
                for item in list(user_data['inventory'].keys()):
                    if name.lower() in item.lower():
                        info(item)
                        possible_items.append(item)
                if len(possible_items) > 1:
                    return False, f'Multiple items fit description: {possible_items}'
                elif len(possible_items) == 0:
                    return False, f'no matching items containing "{name}"'
                else:
                    item_name = possible_items[0]
            else:
                item_name = list(user_data.keys())[int(name)]
            inv = user_data['inventory']
            if item_name in inv:
                if inv[item_name]['toggle']:
                    if inv[item_name]['activated'] == False:
                        return False, f'{item_name} is already deactivated'
                    inv[item_name]['activated'] = False
                    user_data['inventory'] = inv
                    write_json(user_path,user_data)
                    return True, item_name
                else:
                    return False, f'{item_name} is not able to toggle'
            else:
                return False, f'{item_name} is not in inventory'
        except Exception as e:
            return self.error_response('deactivate_item',e)

    def get_role_id(self,user_id,name):
        try:
            path = self.users[str(user_id)]
            if is_file(path):
                inv = read_json(path)['inventory']
            else:
                return False, 'couldn\'t locate user file'
            possible_items = []
            if not name.isnumeric():
                for item in list(inv.keys()):
                    if name.lower() in item.lower():
                        info(item)
                        possible_items.append(item)
                if len(possible_items) > 1:
                    return False, f'Multiple items fit description: {possible_items}'
                elif len(possible_items) == 0:
                    return False, f'no matching items containing "{name}"'
                else:
                    item_name = possible_items[0]
            else:
                item_name = list(inv.keys())[int(name)]
            if item_name in inv:
                if inv[item_name]['role'] != None:
                    return True, int(inv[item_name]['role'])
                else:
                    return True, f'no role to return for {item_name}'
            return False, 'item could\'t be located'
        except Exception as e:
            return False, self.error_response('show_goods',e)

    def show_goods(self):
        try:
            path = self.shop_items_path
            if is_file(path):
                return True, read_json(path)
            return False, 'file could\'t be located'
        except Exception as e:
            return False, self.error_response('show_goods',e)

if __name__ == '__main__':
    # def was used for debugging individual pieces
    mar = Market()
    