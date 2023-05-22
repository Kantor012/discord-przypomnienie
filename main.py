import discord
import os
from google.oauth2 import service_account
from tabulate import tabulate
from discord.ext import commands
from datetime import datetime, timedelta
import gspread
from discord.ext import tasks
import asyncio
import requests
import pandas as pd

# -----------------------------------------

# Konfiguracja uwierzytelniania do arkusza kalkulacyjnego Google
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

credentials_dict = {
    "type": os.environ.get("GOOGLE_SERVICE_ACCOUNT_TYPE"),
    "project_id": os.environ.get("GOOGLE_PROJECT_ID"),
    "private_key_id": os.environ.get("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": os.environ.get("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
    "auth_uri": os.environ.get("GOOGLE_AUTH_URI"),
    "token_uri": os.environ.get("GOOGLE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.environ.get("GOOGLE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.environ.get("GOOGLE_CLIENT_CERT_URL")
}

credentials = service_account.Credentials.from_service_account_info(credentials_dict, scopes=scope)

# Tworzenie klienta Google Sheets
client = gspread.authorize(credentials)

# ID arkusza i zakres danych
spreadsheet_id = '1EYt39GPGzv4x8KEi3hX0rx9HpOvQALcmKnRSFaxVszE'
sheet_name = 'Arkusz1'
range_name = 'C5:E25'


# -----------------------------------------


# Funkcja do pobierania danych z arkusza
def fetch_sheet_data():
    try:
        # Otwarcie arkusza i pobranie danych z określonego zakresu
        sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
        values = sheet.get_values(range_name)

        data = [row for row in values if row]  # Pominięcie pustych wierszy
        table1 = tabulate(data, headers="firstrow", tablefmt="fancy_grid")

        return data

    except Exception as e:
        print(f'Wystąpił błąd podczas pobierania danych z arkusza: {e}')

    return []


@tasks.loop(seconds=30)  # Wywołanie co 30 sekund
async def fetch_sheet_data_task():
    data = fetch_sheet_data()

    # Tworzenie nowej tabeli z pobranymi danymi
    table = "\n".join(["\t".join(row) for row in data])
    # print(f"Pobrane dane:\n{table}")


@fetch_sheet_data_task.before_loop
async def before_fetch_sheet_data_task():
    await bot.wait_until_ready()


def read_csv_file(file_path):
    response = requests.get(file_path)
    content = response.content.decode('utf-8')
    df = pd.read_csv(pd.compat.StringIO(content))
    return df


# -----------------------------------------

intents = discord.Intents.all()
bot_token = os.environ.get("BOT_TOKEN")
short_message_options = ["Przypomnienie Trening Klubowy", "Najbliższy mecz ligowy"]
message_options = [
    "Cześć! Zapraszamy na trening klubowy o godzinie 20:00."
    "\n\nPozdrawiamy, zarząd klubu Black Team\n.",
    "Cześć! Zapraszamy na najbliższy mecz ligowy:\n"
    "Data: {event_date}\n"
    "Godzina: {event_hour}\n"
    "Link do meczu: {event_link}\n"
    "Pozdrawiamy, zarząd klubu Black Team\n."
]


def get_closest_event():
    current_datetime = datetime.now()
    closest_event = None

    for event_date, event_data in event_schedule.items():
        event_hour = event_data["time"]
        event_datetime = datetime.strptime(event_date + " " + event_hour, "%d.%m.%Y %H:%M")
        if event_datetime >= current_datetime:
            if closest_event is None or event_datetime < closest_event:
                closest_event = event_datetime
                closest_link = event_data["link"]

    return closest_event, closest_link if closest_event else (None, None)


# ----------------------------------------------------------------------------------------------------------------------

bot = commands.Bot(command_prefix='!', intents=intents)
menu = discord.ui.Select(
    placeholder="Wybierz wiadomość",
    options=[discord.SelectOption(label=message, value=message) for message in short_message_options]
)

# ----------------------------------------------------------------------------------------------------------------------

event_hours = {
    "22.05.2023": "16:00",
    "23.05.2023": "17:30",
    "24.05.2023": "18:00",
    "25.05.2023": "15:00",
    "26.05.2023": "16:30",
    "27.05.2023": "15:00",
    "28.05.2023": "17:30",
    "29.05.2023": "17:30",
    "30.05.2023": "17:30",
    "31.05.2023": "16:30",
    "01.06.2023": "17:00",
    "02.06.2023": "16:00",
    "03.06.2023": "17:00",
    "04.06.2023": "15:30",
    "05.06.2023": "16:00",
    "06.06.2023": "16:00",
    "07.06.2023": "16:30",
    "08.06.2023": "16:30",
    "09.06.2023": "18:00",
    "10.06.2023": "15:00",
    "11.06.2023": "15:00",
    "12.06.2023": "17:00",
    "13.06.2023": "18:00",
    "14.06.2023": "18:30",
    "15.06.2023": "15:30",
    "16.06.2023": "18:00",
    "17.06.2023": "17:30"
}

event_links = {
    "22.05.2023": "https://pl.footballteamgame.com/match/1252490/live",
    "23.05.2023": "https://pl.footballteamgame.com/match/1252501/live",
    "24.05.2023": "https://pl.footballteamgame.com/match/1252510/live",
    "25.05.2023": "https://pl.footballteamgame.com/match/1252512/live",
    "26.05.2023": "https://pl.footballteamgame.com/match/1252523/live",
    "27.05.2023": "https://pl.footballteamgame.com/match/1252528/live",
    "28.05.2023": "https://pl.footballteamgame.com/match/1252541/live",
    "29.05.2023": "https://pl.footballteamgame.com/match/1252549/live",
    "30.05.2023": "https://pl.footballteamgame.com/match/1252557/live",
    "31.05.2023": "https://pl.footballteamgame.com/match/1252563/live",
    "01.06.2023": "https://pl.footballteamgame.com/match/1252573/live",
    "02.06.2023": "https://pl.footballteamgame.com/match/1252582/live",
    "03.06.2023": "https://pl.footballteamgame.com/match/1252589/live",
    "04.06.2023": "https://pl.footballteamgame.com/match/1252601/live",
    "05.06.2023": "https://pl.footballteamgame.com/match/1252608/live",
    "06.06.2023": "https://pl.footballteamgame.com/match/1252615/live",
    "07.06.2023": "https://pl.footballteamgame.com/match/1252620/live",
    "08.06.2023": "https://pl.footballteamgame.com/match/1252630/live",
    "09.06.2023": "https://pl.footballteamgame.com/match/1252638/live",
    "10.06.2023": "https://pl.footballteamgame.com/match/1252648/live",
    "11.06.2023": "https://pl.footballteamgame.com/match/1252655/live",
    "12.06.2023": "https://pl.footballteamgame.com/match/1252662/live",
    "13.06.2023": "https://pl.footballteamgame.com/match/1252671/live",
    "14.06.2023": "https://pl.footballteamgame.com/match/1252678/live",
    "15.06.2023": "https://pl.footballteamgame.com/match/1252685/live",
    "16.06.2023": "https://pl.footballteamgame.com/match/1252691/live",
    "17.06.2023": "https://pl.footballteamgame.com/match/1252698/live"
}

event_schedule = {
    "22.05.2023": {"time": "16:00", "link": "https://pl.footballteamgame.com/match/1252490/live"},
    "23.05.2023": {"time": "17:30", "link": "https://pl.footballteamgame.com/match/1252501/live"},
    "24.05.2023": {"time": "18:00", "link": "https://pl.footballteamgame.com/match/1252510/live"},
    "25.05.2023": {"time": "15:00", "link": "https://pl.footballteamgame.com/match/1252512/live"},
    "26.05.2023": {"time": "16:30", "link": "https://pl.footballteamgame.com/match/1252523/live"},
    "27.05.2023": {"time": "15:00", "link": "https://pl.footballteamgame.com/match/1252528/live"},
    "28.05.2023": {"time": "17:30", "link": "https://pl.footballteamgame.com/match/1252541/live"},
    "29.05.2023": {"time": "17:30", "link": "https://pl.footballteamgame.com/match/1252549/live"},
    "30.05.2023": {"time": "17:30", "link": "https://pl.footballteamgame.com/match/1252557/live"},
    "31.05.2023": {"time": "16:30", "link": "https://pl.footballteamgame.com/match/1252563/live"},
    "01.06.2023": {"time": "17:00", "link": "https://pl.footballteamgame.com/match/1252572/live"},
    "02.06.2023": {"time": "16:00", "link": "https://pl.footballteamgame.com/match/1252578/live"},
    "03.06.2023": {"time": "17:00", "link": "https://pl.footballteamgame.com/match/1252588/live"},
    "04.06.2023": {"time": "15:30", "link": "https://pl.footballteamgame.com/match/1252593/live"},
    "05.06.2023": {"time": "16:00", "link": "https://pl.footballteamgame.com/match/1252602/live"},
    "06.06.2023": {"time": "16:00", "link": "https://pl.footballteamgame.com/match/1252610/live"},
    "07.06.2023": {"time": "16:30", "link": "https://pl.footballteamgame.com/match/1252619/live"},
    "08.06.2023": {"time": "16:30", "link": "https://pl.footballteamgame.com/match/1252627/live"},
    "09.06.2023": {"time": "18:00", "link": "https://pl.footballteamgame.com/match/1252638/live"},
    "10.06.2023": {"time": "15:00", "link": "https://pl.footballteamgame.com/match/1252640/live"},
    "11.06.2023": {"time": "15:00", "link": "https://pl.footballteamgame.com/match/1252648/live"},
    "12.06.2023": {"time": "17:00", "link": "https://pl.footballteamgame.com/match/1252660/live"},
    "13.06.2023": {"time": "18:00", "link": "https://pl.footballteamgame.com/match/1252670/live"},
    "14.06.2023": {"time": "18:30", "link": "https://pl.footballteamgame.com/match/1252679/live"},
    "15.06.2023": {"time": "15:30", "link": "https://pl.footballteamgame.com/match/1252681/live"},
    "16.06.2023": {"time": "18:00", "link": "https://pl.footballteamgame.com/match/1252694/live"},
    "17.06.2023": {"time": "17:30", "link": "https://pl.footballteamgame.com/match/1252701/live"}
}


# ----------------------------------------------------------------------------------------------------------------------
async def display_channel_list():
    server_id = '1053076841289760778'
    server = bot.get_guild(int(server_id))
    if server:
        print(f'Lista kanałów na serwerze {server.name}:')
        for channelx in server.channels:
            print(f'- {channelx.name} (ID: {channelx.id}, Typ: {channelx.type})')
    else:
        print(f'Nie można znaleźć serwera o ID: {server_id}')


async def display_players_with_role():
    server_id = '1053076841289760778'
    role_id = 1053327072312958976  # ID roli graczy

    server = bot.get_guild(int(server_id))

    if server:
        role = discord.utils.get(server.roles, id=role_id)
        if role:
            players = [member.name for member in server.members if role in member.roles]
            print(f'Gracze z rolą {role.name} (ID: {role.id}):')
            for player in players:
                print(player)
        else:
            print(f'Nie można znaleźć roli o ID: {role_id}')
    else:
        print(f'Nie można znaleźć serwera o ID: {server_id}')


@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user.name}')
    await display_channel_list()
    await display_players_with_role()
    fetch_sheet_data_task.start()
    bot.loop.create_task(schedule_tabela())
    bot.loop.create_task(match_reminder_loop())
    bot.loop.create_task(training_reminder_loop())


@bot.command()
@commands.has_role(1053325817314287717)
@commands.has_role(1053326345633017876)
@commands.has_role(1108480456816611432)
async def wiadomosc(ctx):
    if ctx.channel.id != 1109106084129554543:
        return await ctx.send("Nie możesz używać tej komendy w tym kanale.")

    closest_event, event_link = get_closest_event()

    if closest_event:
        event_date = closest_event.strftime("%d.%m.%Y")
        event_hour = closest_event.strftime("%H:%M")
        message = message_options[1].format(event_date=event_date, event_hour=event_hour, event_link=event_link)
    else:
        message = "Brak najbliższego wydarzenia."

    class MessageSelect(discord.ui.Select):
        def __init__(self):
            super().__init__(
                placeholder="Wybierz wiadomość",
                options=[discord.SelectOption(label=msg, value=msg) for msg in short_message_options],
            )

        async def callback(self, interaction: discord.Interaction):
            selected_option = self.values[0]
            index = short_message_options.index(selected_option)
            selected_message = message_options[index]
            server = ctx.guild
            role = discord.utils.get(server.roles, id=1053327072312958976)
            if index == 1:
                selected_message = message
                if role:
                    for member in role.members:
                        try:
                            await member.send(selected_message)
                            await ctx.send(f'Wysłano wiadomość prywatną do {member.name}')
                        except discord.Forbidden:
                            await ctx.send(f'Nie można wysłać wiadomości prywatnej do {member.name}')
                    channel = bot.get_channel(int('1108782919591415958'))
                if channel:
                    await channel.send('@everyone' + '\n\n\n' + selected_message)
            else:
                if role:
                    for member in role.members:
                        try:
                            await member.send(selected_message)
                            await ctx.send(f'Wysłano wiadomość prywatną do {member.name}')
                        except discord.Forbidden:
                            await ctx.send(f'Nie można wysłać wiadomości prywatnej do {member.name}')
                    channel = bot.get_channel(int('1108737410197622784'))
                if channel:
                    await channel.send('@everyone' + '\n\n\n' + selected_message)

    view = discord.ui.View()
    view.add_item(MessageSelect())

    await ctx.send(content="Wybierz wiadomość:", view=view)


# Komenda "tabela" do pobierania i wysyłania tabeli na kanał Discord
async def tabela():
    data = fetch_sheet_data()
    if data:
        try:
            # Wyrównanie danych tabeli i utworzenie formatu wyrównanej tabeli
            table = tabulate(data, headers="firstrow", tablefmt="fancy_grid")

            # Tworzenie wiadomości z tabelą
            message = f'Pobrane dane:\n```\n{table}\n```'

            # Pobranie kanału na podstawie ID
            channel = bot.get_channel(1108793255333744660)
            if channel is None:
                print(f'Nie można znaleźć kanału o ID {1108793255333744660}')
                return

            # Kasowanie poprzedniej wiadomości na kanale
            async for old_message in channel.history(limit=1):
                await old_message.delete()

            # Wysłanie nowej wiadomości z tabelą na kanał
            await channel.send(message)
            print('Tabela została wysłana na kanale.')

        except Exception as e:
            print(f'Wystąpił błąd podczas wysyłania tabeli na kanał Discord: {e}')


async def schedule_tabela():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.now()
        if now.hour == 22 and now.minute == 00:
            await tabela()
        await asyncio.sleep(60)  # Oczekiwanie 60 sekund przed sprawdzeniem warunku ponownie


@bot.command()
@commands.has_role(1108480456816611432)
async def koszulki(ctx):
    file_path = os.environ.get("FILE_PATH")
    data = read_csv_file(file_path)

    # Pobranie kanału na podstawie ID
    channel = bot.get_channel(1108783308411777128)
    if channel is None:
        await ctx.send(f'Nie można znaleźć kanału o ID 1108783308411777128')
        return

    # Podział danych na bloki po 5 graczy
    blocks = [data[i:i + 5] for i in range(0, len(data), 5)]

    # Wysłanie bloków jako osobne wiadomości
    for block in blocks:
        # Utworzenie nagłówków tabeli
        # headers = ['Nick z gry', '-', 'Numer', 'Obrazek']

        # Utworzenie wiadomości z blokiem graczy jako sformatowaną tabelą
        table = tabulate(block, tablefmt="fancy_grid")
        message = f'```\n{table}\n```'

        # Wysłanie wiadomości z blokiem na kanał
        await channel.send(message)

    # Wysłanie potwierdzenia na kanale, z którego została wykonana komenda
    await ctx.send('Wszystkie bloki zostały wysłane na kanał.')


# @bot.command()
# async def purge(ctx):
#    await ctx.channel.purge(limit=10)

async def send_match_message():
    closest_event, event_link = get_closest_event()

    if closest_event:
        event_date = closest_event.strftime("%d.%m.%Y")
        event_hour = closest_event.strftime("%H:%M")
        message = f"@here \nWitam, zapraszam na mecz {event_date}, {event_hour}\n{event_link}"
        channel = bot.get_channel(1108782919591415958)  # ID kanału docelowego

        if channel:
            await channel.send(message)


async def match_reminder_loop():
    while True:
        current_time = datetime.now()
        closest_event, _ = get_closest_event()

        if closest_event:
            ten_minutes_before_event = closest_event - timedelta(minutes=10)

            if current_time >= ten_minutes_before_event:
                await send_match_message()

        # Obliczanie czasu do najbliższego meczu
        time_to_next_match = closest_event - current_time if closest_event else timedelta(minutes=10)

        # Oczekiwanie na najbliższy mecz
        await asyncio.sleep(time_to_next_match.total_seconds())


async def send_training_reminder():
    guild = bot.get_guild(1053076841289760778)  # ID serwera
    role = discord.utils.get(guild.roles, id=1053327072312958976)  # ID roli graczy
    channel1 = bot.get_channel(1108737410197622784)  # ID kanału na 20:00
    channel2 = bot.get_channel(1053330003464552600)  # ID kanału na 20:40

    if channel1:
        await channel1.send("Zapraszam na Trening klubowy!\n @here "
                            "\n https://pl.footballteamgame.com/training/team-training")
    if channel2:
        await channel2.send("Powtórne przypomnienie, Zapraszam na Trening Klubowy!\n @here"
                            "\n https://pl.footballteamgame.com/training/team-training")

    if role:
        for member in role.members:
            try:
                await member.send("Zapraszam na TRENING KLUBOWY!\n"
                                  "https://pl.footballteamgame.com/training/team-training")
            except discord.Forbidden:
                pass


async def training_reminder_loop():
    while True:
        current_time = datetime.now()

        # Ustawienie czasu otreningów
        training_time1 = current_time.replace(hour=20, minute=0, second=0, microsecond=0)
        training_time2 = current_time.replace(hour=20, minute=40, second=0, microsecond=0)

        # Obliczenie czasu do najbliższego otreningu
        if current_time < training_time1:
            time_to_training = training_time1 - current_time
        elif current_time < training_time2:
            time_to_training = training_time2 - current_time
        else:
            # Jeśli już minął czas drugiego otreningu, ustawiamy czas na następny dzień
            next_day = current_time + timedelta(days=1)
            time_to_training = next_day.replace(hour=20, minute=0, second=0, microsecond=0) - current_time

        # Oczekiwanie na czas otreningu
        await asyncio.sleep(time_to_training.total_seconds())

        # Sprawdzenie, który otrening powinien się odbyć
        if current_time < training_time1:
            await send_training_reminder()
        elif current_time < training_time2:
            await send_training_reminder()


bot.run(bot_token)
