from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import cloudscraper
import json
from fpdf import FPDF
import os
import shutil
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
import random

import asyncio

# Store queues for each user

api_id = "20951184" 
api_hash = "33da8f2403e95e6c2504a3c994223c73" 
bot_token = "8000939036:AAG4QvUuv3F7shFX5EJCJeIdC9rfNWzKuI8" 

# Initialize Bot
bot = Client("comick_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

scraper = cloudscraper.create_scraper()

# Store search results globally
manga_results = {}
chapter_pages = {}
user_queues = {}
headers = {
    "Referer": "https://comick.io",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

def fetch_manhwa_info(query):
    url = f"https://api.comick.io/v1.0/search?type=comic&page=1&limit=8&q={query}&t=false"
    response = scraper.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

def fetch_manga_details(slug):
    url = f"https://api.comick.fun/comic/{slug}"
    response = scraper.get(url)
    return response.json() if response.status_code == 200 else None

def fetch_manga_chapters(hid, page):
    url = f"https://api.comick.fun/comic/{hid}/chapters?lang=en&page={page}"
    response = scraper.get(url)
    return response.json() if response.status_code == 200 else None

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#
@bot.on_message(filters.command("start"))
async def start(client, message):
    buttons = [
        [InlineKeyboardButton("🤩 Main Channel", url="https://t.me/Manga_Sect"),
         InlineKeyboardButton("ℹ️ Help", callback_data="help")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]

    photo_url = "https://files.catbox.moe/m283uq.jpg"
    sent_message = await message.reply_photo(
        photo=photo_url,
        caption="👋 Welcome to the @Manga_Sect Search Bot!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Help Command (via Button)
@bot.on_callback_query(filters.regex("help"))
async def help_menu(client, callback_query):
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
    await callback_query.message.edit_text(
        "📌 **How to Use the Bot:**\n\n"
        "1️⃣ Send `/manga <query>` to search for a manga.\n"
        "2️⃣ Click on a title to get detailed info.\n\n"
        "🔹 Use `/start` to return to the main menu.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Back Button
@bot.on_callback_query(filters.regex("back"))
async def back_to_start(client, callback_query):
    buttons = [
        [InlineKeyboardButton("🤩 Main channel", url="https://t.me/Manga_Sect"),
         InlineKeyboardButton("ℹ️ Help", callback_data="help")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await callback_query.message.edit_caption(
        "👋 Welcome to the Manga Search Bot!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Close Button (Deletes Start Message Immediately)
@bot.on_callback_query(filters.regex("close"))
async def close(client, callback_query):
    try:
        await callback_query.message.delete()  # Deletes the message directly
    except Exception as e:
        print(f"Error deleting message: {e}")




#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
@bot.on_message(filters.command("queue") & filters.private)
async def check_queue(client, message):
    user_id = message.from_user.id

    # Get user queue size
    user_queue_size = user_queues[user_id].qsize() if user_id in user_queues else 0

    # Get total global queue size
    global_queue_size = sum(q.qsize() for q in user_queues.values())

    await message.reply_text(
        f"📌 **Queue Status:**\n\n"
        f"👤 **Your Queue:** {user_queue_size} chapter(s)\n"
        f"🌍 **Total Global Queue:** {global_queue_size} chapter(s)"
    )
@bot.on_message(filters.command("manga") & filters.private)
async def manga_search(client, message):
    global manga_results  

    query = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not query:
        await message.reply_text("Please provide a manga title to search.\n <code>/Solo Leveling</code>")
        return
    emojis = ["🥳", "🙂", "💅", "❤️", "👍", "💋", "😱", "⚡️", "🔥", "💸", "😘", "😁", "😜", "🥶", "🤯", "😈", "👾", "💦", "❣️", "🎉"]
    emoji = random.choice(emojis)
    #await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji=f"{emoji}")
    results = fetch_manhwa_info(query)
    if not results:
        await message.reply_text("No results found.")
        return

    chat_id = message.chat.id
    manga_results[chat_id] = {str(i): item['slug'] for i, item in enumerate(results)}

    buttons = [
        [InlineKeyboardButton(item.get("title", "Unknown"), callback_data=f"manga|{i}")]
        for i, item in enumerate(results)
    ]

    await message.reply_text("Select a manga:", reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex(r"manga\|(\d+)"))
async def manga_details(client, callback_query):
    global manga_results

    chat_id = callback_query.message.chat.id
    index = callback_query.matches[0].group(1)

    slug = manga_results.get(chat_id, {}).get(index)
    if not slug:
        await callback_query.message.reply_text("Manga details not found.")
        return

    data = fetch_manga_details(slug)

    if data and "comic" in data:
        comic = data["comic"]
        title = comic.get("title", "N/A")
        country = comic.get("country", "N/A")
        status = comic.get("status")
        translation_completed = comic.get("translation_completed", False)
        hid = comic.get("hid", "")

        status_text = {
            1: "ONGOING",
            2: "COMPLETED" if translation_completed else "PUBLISHING FINISHED",
            3: "CANCELLED",
            4: "ON HIATUS"
        }.get(status, "UNKNOWN")

        year = comic.get("year", "Unknown")
        rating = comic.get("bayesian_rating", "N/A")
        followers = comic.get("user_follow_count", "N/A")
        link = f"https://comick.io/comic/{comic['slug']}?lang=en" if comic.get("slug") else "N/A"
        cover = f'https://meo.comick.pictures/{comic["md_covers"][0]["b2key"]}' if comic.get("md_covers") else None
        description = comic.get("desc", "").split("\n\n---\n")[0]
        if len(description) > 500:
            description = description[:500] + "..."
        manga_type = {'kr': 'Manhwa', 'jp': 'Manga', 'cn': 'Manhua'}.get(country, 'N/A')

        text = f"""
<b>Title:</b> {title}
<b>Type:</b> {manga_type}
<b>Country:</b> {country}
<b>Status:</b> {status_text}
<b>Year:</b> {year}
<b>Rating:</b> {rating}
<b>Followers:</b> {followers}

<b>Description:</b>
<blockquote expandable>{description}</blockquote>

🔗 <a href="{link}">Read here</a>
"""

        buttons = [[InlineKeyboardButton("📖 Chapters", callback_data=f"chapters|{hid}|1")]]

        cover_url = f'https://meo.comick.pictures/{comic["md_covers"][0]["b2key"]}' if comic.get("md_covers") else None
        print(cover_url)
        if cover_url:
            await callback_query.message.reply_photo(cover_url, caption=text, reply_markup=InlineKeyboardMarkup(buttons), message_effect_id=5159385139981059251, parse_mode=ParseMode.HTML)
        else:
            await callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await callback_query.message.reply_text("Manga details not found.")

@bot.on_callback_query(filters.regex(r"chapters\|(.+)\|(\d+)$"))
async def fetch_chapters(client, callback_query):
    match = callback_query.matches[0]
    hid = match.group(1)
    page = int(match.group(2))

    chapters_data = fetch_manga_chapters(hid, page)

    if not chapters_data or "chapters" not in chapters_data or not chapters_data["chapters"]:
        await callback_query.answer("No chapters found!", show_alert=True)
        return

    seen_chapters = set()
    chapter_buttons = []
    all_chapters = []

    for chap in chapters_data["chapters"]:
        chap_number = chap["chap"]
        if chap_number not in seen_chapters:
            seen_chapters.add(chap_number)
            all_chapters.append((hid, chap["hid"], chap_number))
            chapter_buttons.append([
                InlineKeyboardButton(
                    f"Chapter {chap_number}",
                    callback_data=f"images|{hid}|{chap['hid']}|{chap_number}"
                )
            ])

    # Add Full Page button to queue all chapters on this page
    chapter_buttons.append([
        InlineKeyboardButton(
            "📥 Full Page", callback_data=f"fullpage|{hid}|{page}"
        )
    ])

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton("<<", callback_data=f"chapters|{hid}|{page-1}"))
    navigation_buttons.append(InlineKeyboardButton(">>", callback_data=f"chapters|{hid}|{page+1}"))

    if navigation_buttons:
        chapter_buttons.append(navigation_buttons)

    await callback_query.message.edit_text(
        f"📖 Chapters (Page {page}):",
        reply_markup=InlineKeyboardMarkup(chapter_buttons)
    )

@bot.on_callback_query(filters.regex(r"fullpage\|(.+)\|(\d+)$"))
async def queue_full_page(client, callback_query):
    match = callback_query.matches[0]
    hid = match.group(1)
    page = int(match.group(2))

    chapters_data = fetch_manga_chapters(hid, page)
    if not chapters_data or "chapters" not in chapters_data or not chapters_data["chapters"]:
        await callback_query.answer("No chapters found on this page!", show_alert=True)
        return

    user_id = callback_query.from_user.id
    if user_id not in user_queues:
        user_queues[user_id] = asyncio.Queue()

    seen_chapters = set()  
    unique_chapters = []

    for chap in chapters_data["chapters"]:
        try:
            chap_number = chap["chap"]

        except ValueError:
            continue  # Skip if not a valid number

        if chap_number not in seen_chapters:
            seen_chapters.add(chap_number)
            unique_chapters.append((hid, chap["hid"], chap_number))

    # Sort chapters numerically
    unique_chapters.sort(key=lambda x: x[2])

    # Add sorted chapters to queue
    for chapter in unique_chapters:
        await user_queues[user_id].put((*chapter, callback_query))

    if user_queues[user_id].qsize() == len(unique_chapters):
        asyncio.create_task(process_chapter_queue(user_id))


def download_and_convert_images(images, download_dir):
    image_files = []
    for idx, img in enumerate(images, 1):
        image_url = f"https://meo.comick.pictures/{img['b2key']}"
        print(image_url)
        image_response = requests.get(image_url)

        if image_response.status_code == 200:
            img_path = os.path.join(download_dir, f"{idx}.jpg")
            with open(img_path, 'wb') as img_file:
                img_file.write(image_response.content)

            try:
                with Image.open(img_path) as img:
                    img = img.convert("RGB")
                    img.save(img_path, "JPEG")
            except Exception as e:
                print(f"Error converting image: {e}")
                continue

            image_files.append(img_path)

    return image_files


def create_pdf(image_files, pdf_path):
    pdf = FPDF('P', 'pt')  # Use points for accurate scaling

    for img_path in image_files:
        try:
            with Image.open(img_path) as img:
                img = img.convert("RGB")  # Ensure RGB mode
                width, height = img.size  # Get original dimensions

                # Add a page with the same dimensions as the image
                pdf.add_page(format=(width, height))

                # Place image exactly at (0,0) without cropping or black bars
                pdf.image(img_path, x=0, y=0, w=width, h=height)

        except Exception as e:
            print(f"Skipping invalid image {img_path}: {e}")

    # Ensure directory exists before saving
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    pdf.output(pdf_path, "F")  # Save PDF   



async def process_chapter_queue(user_id):
    while not user_queues[user_id].empty():
        match = await user_queues[user_id].get()
        if match is None:
            break  

        comic_hid_full, chap_hid, chap_num, callback_query = match
        chap_num = chap_num # Keep as integer 


        download_dir = os.path.join("downloads", f"{user_id}/{comic_hid_full}/{chap_num}")
        os.makedirs(download_dir, exist_ok=True)

        chapter_url = f"https://comick.io/comic/{comic_hid_full}/{chap_hid}-chapter-{chap_num}-en"
        print(f"Processing: {chapter_url}")

        try:
            response = scraper.get(chapter_url, headers=headers)
            if response.status_code != 200:
                raise Exception("Failed to fetch chapter page")

            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find('script', id='__NEXT_DATA__')
            if not script_tag:
                raise Exception("JSON data not found")

            data = json.loads(script_tag.string)
            chapter_data = data['props']['pageProps']['chapter']
            images = chapter_data['md_images']

            # 🟢 Extract the manga title
            manga_title = chapter_data["md_comics"]["title"]
            sanitized_title = re.sub(r'[\\/*?:"<>|]', '', manga_title)  # Remove invalid characters

            if not images:
                raise Exception("No images found")

            image_files = download_and_convert_images(images, download_dir)
            if not image_files:
                raise Exception("Failed to download any images.")

            # 🟢 Set filename with manga title
            pdf_filename = f"[MS] [{chap_num}] {sanitized_title} @Manga_Sect.pdf"
            pdf_path = os.path.join(download_dir, pdf_filename)

            create_pdf(image_files, pdf_path)

            # 🟢 Set caption with manga title
            caption = f"<blockquote><b>[MS] [{chap_num}] {sanitized_title} @Manga_Sect</b></blockquote>"

            thumb_path = "thumb.jpg"
            await bot.send_document(
                chat_id=callback_query.message.chat.id,
                document=pdf_path,
                caption=caption,
                thumb=thumb_path
            )

            shutil.rmtree(download_dir)

        except Exception as e:
            await callback_query.answer(f"Error: {str(e)}", show_alert=True)

        user_queues[user_id].task_done()

@bot.on_callback_query(filters.regex(r"images\|(.+)\|(.+)\|(\d+)"))
async def send_chapter_images(client, callback_query):
    match = callback_query.matches[0]
    comic_hid_full = match.group(1)
    chap_hid = match.group(2)
    chap_num = match.group(3)
    user_id = callback_query.from_user.id

    # Create queue for user if not exists
    if user_id not in user_queues:
        user_queues[user_id] = asyncio.Queue()

    # Add the chapter request to the queue
    await user_queues[user_id].put((comic_hid_full, chap_hid, chap_num, callback_query))

    # If queue was empty before, start processing
    if user_queues[user_id].qsize() == 1:
        asyncio.create_task(process_chapter_queue(user_id))


bot.run()