import discord
import requests
import json
import time

TOKEN = DISCORD_TOKEN
client = discord.Client()
cycle_time = 7200
amp = 0

# API query parameters
params = {
    'api_key': API_KEY,
    'type': 'search',
    'amazon_domain': 'amazon.com',
    'search_term': 'graphics card',
    'sort_by': 'most_recent',
    'output': 'json'
}

asins = []


# setup API query
def get_amazon(param):
    product_list = []
    links = []
    price_list = []
    int_val = []
    api_result = requests.get('https://api.rainforestapi.com/request', param)
    api_result = api_result.json()
    products = api_result['search_results']
    for product in products:
        asin = product['asin']
        if asin in asins:
            print("Item blocked because already shown.")
        else:
            asins.append(product['asin'])
            product_list.append(product['title'])
            links.append(product['link'])
            try:
                price_list.append(product['price']['raw'])
                int_val.append(product['price']['value'])
            except:
                price_list.append("unknown")
                int_val.append(-1)
    return product_list, links, price_list, int_val


# Read data JSON file
file = open('data.json')
data = json.load(file)


async def search():
    amazon_data = get_amazon(params)
    data_len = len(amazon_data[0])
    if data_len > 0:
        for x in range(data_len):
            for index in data['graphics_cards']:
                name_arr = amazon_data[0]
                actual_name = str(name_arr[x])
                check_name = str(index['name'])
                price_arr = amazon_data[2]
                price = str(price_arr[x])
                link_arr = amazon_data[1]
                link = str(link_arr[x])
                cost_int_arr = amazon_data[3]
                cost_int = cost_int_arr[x]
                max_price = index['price'] + amp
                print(check_name + " : " + actual_name + "\n" + str(max_price) + " : " + str(cost_int))
                if check_name in actual_name and cost_int <= max_price:
                    final_message = actual_name + "\nCost: " + price + "\n" + link
                    await client.get_channel(940719467506331688).send(final_message)


async def loop():
    global amp
    global cycle_time
    while True:
        await search()
        time.sleep(cycle_time)  # 2 hour cycle


# on message sent
@client.event
async def on_message(message):
    global amp
    global cycle_time
    if message.content.startswith('!amp'):
        text = str(message.content)
        command = text.split(' ')
        amp = int(command[1])
        await message.channel.send("The Acceptable Maximum Price (AMP) has been changed to MSRP + $" + str(amp))

    if message.content.startswith('!test'):
        await search()

    if message.content.startswith('!start'):
        await message.channel.send("Starting loop with a delay of " + str(cycle_time / 3600))
        await loop()

    if message.content.startswith('!delay'):
        text = str(message.content)
        command = text.split(' ')
        tim = int(command[1]) * 3600
        cycle_time = tim
        await message.channel.send("The loop delay is now " + str(cycle_time / 3600) + " hours.")


client.run(TOKEN)
