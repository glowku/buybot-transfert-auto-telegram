import asyncio
import os
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
STRING_SESSION = os.environ["STRING_SESSION"]
SOURCE_GROUP = int(os.environ["SOURCE_GROUP"])
TARGET_GROUP = int(os.environ["TARGET_GROUP"])

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)


@client.on(events.NewMessage(chats=SOURCE_GROUP))
async def on_new_message(event):
  msg = event.message
  try:
    await client.forward_messages(TARGET_GROUP, msg)
    print(f"[FORWARD OK] Message {msg.id} transféré.")
  except Exception as e:
    print(f"[FORWARD BLOQUÉ] ({e}) -> tentative de copie...")
    try:
      if msg.media:
        await client.send_file(
            TARGET_GROUP, file=msg.media, caption=msg.text or ""
        )
      elif msg.text:
        await client.send_message(TARGET_GROUP, msg.text)
      print(f"[COPY OK] Message {msg.id} republié.")
    except Exception as e2:
      print(f"[ERREUR ENVOI] Impossible d'envoyer dans le groupe cible : {e2}")


async def health_handler(request):
  return web.Response(text="OK")


async def start_web_server():
  app = web.Application()
  app.router.add_get("/", health_handler)
  port = int(os.environ.get("PORT", 10000))
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, "0.0.0.0", port)
  await site.start()
  print(f"Serveur web actif sur le port {port}")


async def main():
  await start_web_server()
  await client.start()
  print("Connecté ! En attente de nouveaux messages...")
  await client.run_until_disconnected()


if __name__ == "__main__":
  asyncio.run(main())