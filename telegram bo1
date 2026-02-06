db = load_db()
    user = get_user(db, uid)
    lang = user.get("lang", "uk")
    return LANG_TEXTS.get(lang, LANG_TEXTS["uk"]).get(key, key)

def dish_label(uid: int, dish_key: str) -> str:
    db = load_db()
    user = get_user(db, uid)
    lang = user.get("lang", "uk")
    return DISH_NAMES.get(lang, DISH_NAMES["uk"]).get(dish_key, dish_key)


def main_keyboard(uid: int) -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton(t(uid, "menu")),
        types.KeyboardButton(t(uid, "photos")),
        types.KeyboardButton(t(uid, "favorites")),
        types.KeyboardButton(t(uid, "lang")),
    )
    return kb

def dishes_keyboard(uid: int) -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton(dish_label(uid, "pizza")),
        types.KeyboardButton(dish_label(uid, "borsch")),
        types.KeyboardButton(dish_label(uid, "taco")),
        types.KeyboardButton(dish_label(uid, "knedle")),
        types.KeyboardButton("⬅️")
    )
    return kb

def lang_inline_keyboard() -> types.InlineKeyboardMarkup:
    ikb = types.InlineKeyboardMarkup()
    ikb.add(
        types.InlineKeyboardButton("Hrvatski", callback_data="lang:hr"),
        types.InlineKeyboardButton("Українська", callback_data="lang:uk"),
        types.InlineKeyboardButton("English", callback_data="lang:en"),
    )
    return ikb

def dish_inline_actions(dish_key: str, uid: int) -> types.InlineKeyboardMarkup:
    ikb = types.InlineKeyboardMarkup()

    ikb.add(
        types.InlineKeyboardButton("📷 Photo", callback_data=f"photo:{dish_key}"),
        types.InlineKeyboardButton("🧾 " + t(uid, "ingredients"), callback_data=f"ing:{dish_key}"),
    )
    ikb.add(
        types.InlineKeyboardButton("➕ 🌟", callback_data=f"fav_add:{dish_key}")
    )
    return ikb


def send_dish_photo(chat_id: int, dish_key: str):

    cached_id = DISH_PHOTOS[dish_key].get("file_id_cache")
    if cached_id:
        return bot.send_photo(chat_id, cached_id)

    local = DISH_PHOTOS[dish_key]["local"]
    url = DISH_PHOTOS[dish_key]["url"]

    msg = None
    if os.path.exists(local):
        with open(local, "rb") as f:
            msg = bot.send_photo(chat_id, f)
    else:

        msg = bot.send_photo(chat_id, url)


    if msg and msg.photo:
        file_id = msg.photo[-1].file_id
        DISH_PHOTOS[dish_key]["file_id_cache"] = file_id
    return msg

def dish_key_from_label(uid: int, label: str) -> str | None:

    for key, name in DISH_NAMES.get(get_user(load_db(), uid)["lang"], {}).items():
        if name == label:
            return key

    for lang_map in DISH_NAMES.values():
        for key, name in lang_map.items():
            if name == label:
                return key
    return None


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    uid = message.from_user.id
    bot.send_message(
        message.chat.id,
        f"{t(uid, 'hello')}\n\n{t(uid, 'about_1')}\n{t(uid, 'about_2')}\n{t(uid, 'about_3')}",
        reply_markup=main_keyboard(uid)
    )

@bot.message_handler(commands=['about'])
def about(message: types.Message):
    uid = message.from_user.id
    bot.send_message(message.chat.id, t(uid, 'about_title').format(name=message.from_user.first_name))
    bot.send_message(message.chat.id, t(uid, 'about_contact'))
    bot.send_message(message.chat.id, t(uid, 'email'))

@bot.message_handler(commands=['menu'])
def cmd_menu(message: types.Message):
    uid = message.from_user.id
    bot.send_message(message.chat.id, t(uid, "menu_list"), reply_markup=dishes_keyboard(uid))

@bot.message_handler(commands=['photos'])
def cmd_photos(message: types.Message):
    uid = message.from_user.id
    bot.send_message(message.chat.id, t(uid, "photos_hint"), reply_markup=dishes_keyboard(uid))

@bot.message_handler(commands=['favorites'])
def cmd_favorites(message: types.Message):
    uid = message.from_user.id
    db = load_db()
    user = get_user(db, uid)
    favs = user.get("favorites", [])
    if not favs:
        bot.send_message(message.chat.id, t(uid, "no_fav"))
        return
    bot.send_message(message.chat.id, t(uid, "your_fav"))
    for item in favs:

        if item.get("file_id"):
            bot.send_photo(message.chat.id, item["file_id"], caption=dish_label(uid, item.get("dish", "dish")))
        else:

            send_dish_photo(message.chat.id, item.get("dish", "pizza"))

@bot.message_handler(commands=['lang'])
def cmd_lang(message: types.Message):
    uid = message.from_user.id
    bot.send_message(message.chat.id, t(uid, "pick_lang"), reply_markup=lang_inline_keyboard())


@bot.callback_query_handler(func=lambda c: c.data.startswith("lang:"))
def cb_set_lang(call: types.CallbackQuery):
    lang = call.data.split(":")[1]
    db = load_db()
    user = get_user(db, call.from_user.id)
    user["lang"] = lang
    save_db(db)


    txt = {
        "hr": LANG_TEXTS["hr"]["lang_set"],
        "uk": LANG_TEXTS["uk"]["lang_set"],
        "en": LANG_TEXTS["en"]["lang_set"],
    }.get(lang, LANG_TEXTS["uk"]["lang_set"])

    bot.answer_callback_query(call.id, txt, show_alert=False)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, txt, reply_markup=main_keyboard(call.from_user.id))

@bot.callback_query_handler(func=lambda c: c.data.startswith("photo:"))
def cb_send_photo(call: types.CallbackQuery):
    dish = call.data.split(":")[1]
    send_dish_photo(call.message.chat.id, dish)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("ing:"))
def cb_send_ingredients(call: types.CallbackQuery):
    uid = call.from_user.id
    dish = call.data.split(":")[1]
    lang = get_user(load_db(), uid)["lang"]
    text = f"{dish_label(uid, dish)}\n{t(uid, 'ingredients')} {INGREDIENTS[dish][lang]}"
    bot.send_message(call.message.chat.id, text)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("fav_add:"))
def cb_add_favorite(call: types.CallbackQuery):
    uid = call.from_user.id
    dish = call.data.split(":")[1]


    msg = send_dish_photo(call.message.chat.id, dish)

    file_id = None
    if msg and msg.photo:
        file_id = msg.photo[-1].file_id

    db = load_db()
    user = get_user(db, uid)

    user["favorites"] = [f for f in user.get("favorites", []) if f.get("dish") != dish]
    user["favorites"].append({"dish": dish, "file_id": file_id})
    save_db(db)

    bot.answer_callback_query(call.id, t(uid, "added_fav"), show_alert=False)


@bot.message_handler(content_types=['text'])
def on_text(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()

    # Кнопки головного меню
    if text == t(uid, "menu"):
        bot.send_message(message.chat.id, t(uid, "menu_list"), reply_markup=dishes_keyboard(uid))
        return
    if text == t(uid, "photos"):
        bot.send_message(message.chat.id, t(uid, "photos_hint"), reply_markup=dishes_keyboard(uid))
        return
    if text == t(uid, "favorites"):
        cmd_favorites(message)
        return
    if text == t(uid, "lang"):
        cmd_lang(message)
        return
    if text == "⬅️":
        bot.send_message(message.chat.id, t(uid, "choose_action"), reply_markup=main_keyboard(uid))
        return


    dish = dish_key_from_label(uid, text)
    if dish:

        bot.send_message(
            message.chat.id,
            f"{dish_label(uid, dish)}",
            reply_markup=dish_inline_actions(dish, uid)
        )
        return


    bot.send_message(message.chat.id, t(uid, "unknown"), reply_markup=main_keyboard(uid))

@bot.message_handler(content_types=['photo'])
def on_photo(message: types.Message):
    uid = message.from_user.id
    file_id = message.photo[-1].file_id
    db = load_db()
    user = get_user(db, uid)
    user["uploads"].append({"file_id": file_id})
    save_db(db)
    bot.reply_to(message, t(uid, "send_photo_saved"))

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True, timeout=30)
