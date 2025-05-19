from pathlib import Path
import time
from selenium_client import ChatGPTClient,init_driver

chrome_user_data = Path("./tmp/profile")
driver = init_driver(chrome_user_data)
client = ChatGPTClient(driver)

time.sleep(10)
client.start_editor()
client.insert_simple_text("Test Test Test")
client.insert_simple_text("Test Test Test")
client.insert_simple_text("Test Test Test")
client.insert_simple_text("Test Test Test")
client.insert_simple_text("Test Test Test")

client.insert_newline()
client.insert_newline()
client.insert_hashtags(["#automation","#test"])
client.insert_newline()
client.insert_link("https://karl.fail/projects/")
client.remove_first_br()
# bot.submit_post()
time.sleep(10)
client.cancel_post()
client.discard_draft()
input("✅ Fertig. Enter zum Beenden...")

#bot.close()
