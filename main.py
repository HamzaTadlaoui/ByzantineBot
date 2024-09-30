import discord
from discord.utils import get
import os
import requests
import json
from replit import db
import keep_alive
client = discord.Client()

def help():
  embed=discord.Embed(title="Profile", color=0xFF5733)
  embed.add_field(name="link [website][username]:", value = "Links your account to your discord user, the websites are lichess and chesscom",inline=False)
  embed.add_field(name="profile", value = "Display and update your chess profile",inline=False)
  embed.add_field(name="unlink:", value = "Unlinks both chess.com and lichess accounts from your discord user",inline=False)
  return embed

def add_elo_roles(message,ename,emin,emax):
  keys = db.keys()
  if "roles" not in keys:
    db["roles"]= []
  for i in db["roles"]:
    if i[0]==ename:
      return "role already exist"
  if get(message.guild.roles, name=ename):
    db["roles"].append([ename,emin,emax])
  else:
    return "role doesnt exist in the server"
  return "role created succesfully"

async def remove_all_roles(message):
  keys = db.keys()
  if "roles" not in keys:
    return
  for i in db["roles"]:
    if get(message.guild.roles, name=i[0]):
      role = get(message.guild.roles, name=i[0])
      await message.author.remove_roles(role)

async def give_elo_role(message):
  elo = get_elo(message.author)
  keys = db.keys()
  if "roles" not in keys:
    return "No roles exist"
  for i in db["roles"]:
    if get(message.guild.roles, name=i[0]):
      if elo > int(i[1]) and elo <int(i[2]):
        role = get(message.guild.roles, name=i[0])
        await message.author.add_roles(role,1)

def get_elo(user):
  keys = db.keys()
  dbu = []
  if (str(user) in keys):
    for i in range(8):
      dbu.append(db[str(user)][i])
  else:
    return -1
  return max(dbu[1],dbu[2],dbu[3],dbu[5]*0.75+650,dbu[6]*0.75+650,dbu[7]*0.75+650)
 
def show_profile(user,thumb):
  embed=discord.Embed(title="Profile", color=0xFF5733)
  embed.add_field(name="User:", value = "*"+str(user)+"*",inline=False)
  embed.set_thumbnail(url=thumb)
  keys = db.keys()
  dbu = []
  if (str(user) in keys):
    if(db[str(user)][0]!=""):
      user_rating_update(user,"lichess")
    if(db[str(user)][4]!=""):
      user_rating_update(user,"chesscom")
    for i in range(8):
      dbu.append(db[str(user)][i])
  else:
    embed.set_footer(text="Not linked yet")
    return embed
  EloFinal = calculate_def_elo(str(user))
  embed.add_field(name="Rating:", value = EloFinal,inline=False)

  number_of_user = 0
  number_of_higher = 1
  for userh in keys:
    if(userh != 'roles'):
      number_of_user = number_of_user + 1
      eloOther = calculate_def_elo(userh)
      if(eloOther>EloFinal):
        number_of_higher = number_of_higher + 1
    rank = str(number_of_higher) + " / " + str(number_of_user)
  embed.add_field(name="Server Ranking:", value = rank,inline=False)
  if(dbu[0]!=""):
    embed.add_field(name="Lichess", value="https://lichess.org/@/"+dbu[0], inline=False)
    embed.add_field(name="Bullet", value=dbu[3], inline=True)
    embed.add_field(name="Blitz", value=dbu[2], inline=True)
    embed.add_field(name="Rapid", value=dbu[1], inline=True)
  if(dbu[4]!=""):
    embed.add_field(name="Chess.com", value="https://chess.com/member/"+dbu[4], inline=False) 
    embed.add_field(name="Bullet", value=str(round(dbu[7]*0.75+650))+'('+str(dbu[7])+')', inline=True)
    embed.add_field(name="Blitz", value=str(round(dbu[6]*0.75+650))+'('+str(dbu[6])+')', inline=True)
    embed.add_field(name="Rapid", value=str(round(dbu[5]*0.75+650))+'('+str(dbu[5])+')', inline=True)
  return embed

def user_rating_update(userr, website):
  user = str(userr)
  keys = db.keys()
  if (user in keys):
    if (website == "lichess"):
      profil = requests.get("https://lichess.org/api/user/" +str(db[user][0]))
      json_data = json.loads(profil.text)
      db[user][1] = json_data['perfs']['rapid']['rating']
      db[user][2] = json_data['perfs']['blitz']['rating']
      db[user][3] = json_data['perfs']['bullet']['rating']
    elif (website == "chesscom"):
      profil = requests.get("https://api.chess.com/pub/player/" +str(db[user][4]) + "/stats")
      json_data = json.loads(profil.text)
      if('chess_rapid' in json_data):
        db[user][5] = json_data['chess_rapid']['last']['rating']
      if('chess_blitz' in json_data):
        db[user][6] = json_data['chess_blitz']['last']['rating']
      if('chess_bullet' in json_data):
        db[user][7] = json_data['chess_bullet']['last']['rating']

def user_linking(userr, website, username):
  user = str(userr)
  keys = db.keys()
  if (user in keys):
    if (website == "lichess" or website == "Lichess" ):
      if (db[user][0] == ""):
        db[user][0] = username
        profil = requests.get("https://lichess.org/api/user/" +username)
        json_data = json.loads(profil.text)
        db[user][1] = json_data['perfs']['rapid']['rating']
        db[user][2] = json_data['perfs']['blitz']['rating']
        db[user][3] = json_data['perfs']['bullet']['rating']
      else:
        return "user already linked"
    elif (website == "chesscom" or website == "chess.com" or website == "Chesscom" or website == "Chess.com"):
      if (db[user][4] == ""):
        db[user][4] = username
        profil = requests.get("https://api.chess.com/pub/player/" +username + "/stats")
        json_data = json.loads(profil.text)
        if('chess_rapid' in json_data):
          db[user][5] = json_data['chess_rapid']['last']['rating']
        if('chess_blitz' in json_data):
          db[user][6] = json_data['chess_blitz']['last']['rating']
        if('chess_bullet' in json_data):
          db[user][7] = json_data['chess_bullet']['last']['rating']
      else:
          return "user already linked"
    else:
      return "website not recognized"
  else:
    db[user] = ["", -1, -1, -1, "", -1, -1, -1]
    if (website == "lichess"):
        db[user][0] = username
        profil = requests.get("https://lichess.org/api/user/" + username)
        json_data = json.loads(profil.text)
        db[user][1] = json_data['perfs']['rapid']['rating']
        db[user][2] = json_data['perfs']['blitz']['rating']
        db[user][3] = json_data['perfs']['bullet']['rating']
    elif (website == "chesscom"):
        db[user][4] = username
        profil = requests.get("https://api.chess.com/pub/player/" +username + "/stats")
        json_data = json.loads(profil.text)
        if('chess_rapid' in json_data):
          db[user][5] = json_data['chess_rapid']['last']['rating']
        if('chess_blitz' in json_data):
          db[user][6] = json_data['chess_blitz']['last']['rating']
        if('chess_bullet' in json_data):
          db[user][7] = json_data['chess_bullet']['last']['rating']
    else:
        return "website not recognized"

  dbu = []
  for i in range(8):
    dbu.append(db[user][i])
  return "Linking successfull"

def user_unlinking(user):
  keys = db.keys()
  if (str(user) in keys):
    del db[str(user)]
    return "Unlinked succesfully"
  else:
    return "Not linked yet"

def get_profil(user):
  keys = db.keys()
  if (str(user) in keys):
    dbu = []
    for i in range(8):
      dbu.append(db[str(user)][i])
    return str(dbu)
    
  else:
    return "Not linked yet"

def is_profil_exist(user):
  keys = db.keys()
  if (str(user) in keys):
    return ""
  else:
    return "Profile does not exist."
    
def get_ranking():
  keys = db.keys()
  dbu = []
  for user in keys:
    if(user!="roles"):
      dbu.append([calculate_def_elo(user),user])
  dbu.sort(reverse=True)
  embed=discord.Embed(title="Ranking", color=0xFF5733)
  names = ""
  elos = ""
  pos = ""
  for i in range(len(dbu)):
    pos = pos + str(i+1)+"\n"
    elos = elos + str(dbu[i][0]) + "\n"
    names = names + str(dbu[i][1]) + "\n"
  embed.add_field(name="P", value=pos, inline="true")
  embed.add_field(name="Name", value=names, inline="true")
  embed.add_field(name="Elo", value=elos, inline="true")


  return embed

  
def calculate_def_elo(user):
  keys = db.keys()
  if(user in keys):
    if(user!="roles"):
      debugu = db[user]
      debug = max(db[user][1],db[user][2],db[user][3],db[user][5]*0.75+650,db[user][6]*0.75+650,db[user][7]*0.75+650)
      return max(db[user][1],db[user][2],db[user][3],db[user][5]*0.75+650,db[user][6]*0.75+650,db[user][7]*0.75+650)
  else:
    return -1
  
@client.event
async def on_ready():
  print("Hello World!")
  print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith("$ath"):
    msg = message.content
    username = msg.split("$ath ", 1)[1]
    await message.channel.send(username)

  if message.content.startswith("$link") or message.content.startswith("$Link") :
    msg = message.content
    parameters = msg.split("$link ", 1)[1]
    website = parameters.split(" ")[0]
    username = parameters.split(" ")[1]
    await message.channel.send(user_linking(message.author, website, username))
    await remove_all_roles(message)
    await give_elo_role(message)
    embed=show_profile(message.author,message.author.avatar_url)
    await message.channel.send(embed=embed)


  if message.content.startswith("$profile") or message.content.startswith("$Profile"):
    embed=show_profile(message.author,message.author.avatar_url)
    await message.channel.send(embed=embed)
    #await message.channel.send(get_profil(message.author))
    await message.channel.send(is_profil_exist(message.author))
    await remove_all_roles(message)
    await give_elo_role(message)

  if message.content.startswith("$lookup"):
    msg = message.content
    user_id = msg.split("$lookup ", 1)[1]
    embed=show_profile(user_id,message.author.avatar_url)
    await message.channel.send(embed=embed)
    #await message.channel.send(get_profil(message.author))
    await message.channel.send(is_profil_exist(message.author))
    await remove_all_roles(message)
    await give_elo_role(message)

  if message.content.startswith("$debuglookup"):
    msg = message.content
    user_id = msg.split("$debuglookup ", 1)[1]
    await message.channel.send(get_profil(user_id))

  if message.content.startswith("$leaderboard"):
    embed=get_ranking()
    await message.channel.send(embed=embed)
    
  if message.content.startswith("$unlink"):
    await message.channel.send(user_unlinking(message.author))
    await message.channel.send(is_profil_exist(message.author))
    await remove_all_roles(message)

  if message.content.startswith("$help"):
    embed=help()
    await message.channel.send(embed=embed)

  if message.content.startswith("$showdb"):
    keys = db.keys()
    await message.channel.send(keys)
    result=""
    for user in keys:
      if(user != 'roles'):
        result = result + str(db[user]) + "\n"
    await message.channel.send(result)

  if message.content.startswith("$add role"):
    msg = message.content
    temp = msg.split("$add role ", 1)[1]
    rolename = temp.split(" ")[0]
    emin = temp.split(" ")[1]
    emax = temp.split(" ")[2]
    await message.channel.send(add_elo_roles(message,rolename,emin,emax))

    
   
keep_alive.keep_alive()      
client.run(os.environ['TOKEN'])

