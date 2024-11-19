import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import random
import string


intents = discord.Intents.all()
client = commands.Bot(command_prefix="?", description="Bot Warn", intents=intents)

# IDs degli utenti autorizzati
authorized_users = [1234567890123456789]

# Connessione al database
conn = sqlite3.connect("warns.db")
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS warns (
    warn_id TEXT PRIMARY KEY,
    user_id INTEGER,
    username TEXT,
    avatar_url TEXT,
    reason TEXT
)
''')
conn.commit()

def generate_warn_id():
    """Generate a casual warn ID"""
    return "#" + ''.join(random.choices(string.ascii_letters + string.digits, k=8))


@client.event
async def on_ready():
    print(f"Bot connesso come {client.user}")
    await client.tree.sync()
    print("Comandi sincronizzati.")



@client.tree.command(name="warn", description="Avvisa un utente con una motivazione.")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    if interaction.user.id not in authorized_users:
        await interaction.response.send_message("Non hai l'autorizzazione per usare questo comando.", ephemeral=True)
        return


    warn_id = generate_warn_id()


    c.execute("INSERT INTO warns (warn_id, user_id, username, avatar_url, reason) VALUES (?, ?, ?, ?, ?)",
              (warn_id, user.id, user.name, user.display_avatar.url, reason))
    conn.commit()


    embed = discord.Embed(title="Utente Avvisato", color=discord.Color.orange())
    embed.add_field(name="Utente", value=f"{user.mention}", inline=False)
    embed.add_field(name="Motivazione", value=reason, inline=False)
    embed.add_field(name="Warn ID", value=f"`{warn_id}`", inline=False) 
    embed.set_footer(text=f"Avvisato da {interaction.user}")

    await interaction.response.send_message(embed=embed)



@client.tree.command(name="warnlist", description="Mostra la lista dei warn degli utenti.")
async def warnlist(interaction: discord.Interaction):
    if interaction.user.id not in authorized_users:
        await interaction.response.send_message("Non hai l'autorizzazione per usare questo comando.", ephemeral=True)
        return


    c.execute("SELECT warn_id, user_id, username, reason FROM warns")
    warns = c.fetchall()

    if not warns:
        await interaction.response.send_message("Non ci sono warn registrati.", ephemeral=True)
        return


    embed = discord.Embed(title="Lista dei Warn", color=discord.Color.blue())
    for warn_id, user_id, username, reason in warns:
        embed.add_field(name=f"{username} (ID Utente: {user_id})",
                        value=f"**Warn ID:** `{warn_id}`\n**Motivazione:** {reason}", inline=False)

    await interaction.response.send_message(embed=embed)



@client.tree.command(name="warnremove", description="Rimuove un warn specifico tramite il suo ID.")
async def warnremove(interaction: discord.Interaction, warn_id: str):
    if interaction.user.id not in authorized_users:
        await interaction.response.send_message("Non hai l'autorizzazione per usare questo comando.", ephemeral=True)
        return


    c.execute("SELECT user_id, username, reason FROM warns WHERE warn_id = ?", (warn_id,))
    warn = c.fetchone()

    if not warn:
        await interaction.response.send_message(f"Non è stato trovato alcun warn con ID `{warn_id}`.", ephemeral=True)
        return


    c.execute("DELETE FROM warns WHERE warn_id = ?", (warn_id,))
    conn.commit()


    user_id, username, reason = warn
    embed = discord.Embed(title="Warn Rimosso", color=discord.Color.green())
    embed.add_field(name="Utente", value=f"{username} (ID Utente: {user_id})", inline=False)
    embed.add_field(name="Warn ID Rimosso", value=f"`{warn_id}`", inline=False)
    embed.add_field(name="Motivazione", value=reason, inline=False)

    await interaction.response.send_message(embed=embed)

client.run("your_token")
