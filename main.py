import discord
import asyncio

TOKEN = 'TWÓJ_TOKEN_BOTA'

client = discord.Client()


@client.event
async def on_ready():
    print(f'Zalogowano jako {client.user.name}')
    # Uruchomienie pętli czasowej
    await send_private_messages()
    await asyncio.sleep(86400)  # Oczekiwanie 24 godziny
    await send_private_messages()


async def send_private_messages():
    server_id = 'ID_SERWERA'
    player_ids = ['ID_GRACZA1', 'ID_GRACZA2', 'ID_GRACZA3']  # Lista ID graczy, do których chcesz wysłać wiadomości

    server = client.get_guild(int(server_id))
    for player_id in player_ids:
        player = server.get_member(int(player_id))
        if player:
            try:
                message = "Cześć! To jest wiadomość od bota."
                await player.send(message)
                print(f'Wysłano wiadomość prywatną do {player.name}')
            except discord.Forbidden:
                print(f'Nie można wysłać wiadomości prywatnej do {player.name}')
        else:
            print(f'Nie można znaleźć gracza o ID: {player_id}')


client.run(TOKEN)
