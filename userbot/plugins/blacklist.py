# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Filters
Available Commands:
.addblacklist
.listblacklist
.rmblacklist"""

import re

from telethon import events

import userbot.plugins.sql_helper.blacklist_sql as sql

from .. import CMD_HELP
from ..utils import admin_cmd, edit_or_reply, sudo_cmd


@bot.on(events.NewMessage(incoming=True))
async def on_new_message(event):
    # TODO: exempt admins from locks
    name = event.raw_text
    snips = sql.get_chat_blacklist(event.chat_id)
    for snip in snips:
        pattern = r"( |^|[^\w])" + re.escape(snip) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            try:
                await event.delete()
            except Exception:
                await event.reply("I do not have DELETE permission in this chat")
                sql.rm_from_blacklist(event.chat_id, snip.lower())
            break


@bot.on(admin_cmd(pattern="addblacklist ((.|\n)*)"))
@bot.on(sudo_cmd(pattern="addblacklist ((.|\n)*)", allow_sudo=True))
async def on_add_black_list(event):
    text = event.pattern_match.group(1)
    to_blacklist = list(
        {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
    )

    for trigger in to_blacklist:
        sql.add_to_blacklist(event.chat_id, trigger.lower())
    await edit_or_reply(
        event,
        "Ditambahkan {} Memicu daftar hitam pada obrolan saat ini".format(
            len(to_blacklist)
        ),
    )


@bot.on(admin_cmd(pattern="rmblacklist ((.|\n)*)"))
@bot.on(sudo_cmd(pattern="rmblacklist ((.|\n)*)", allow_sudo=True))
async def on_delete_blacklist(event):
    text = event.pattern_match.group(1)
    to_unblacklist = list(
        {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
    )

    successful = sum(
        1
        for trigger in to_unblacklist
        if sql.rm_from_blacklist(event.chat_id, trigger.lower())
    )

    await edit_or_reply(
        event, f"Dihapus {successful} / {len(to_unblacklist)} dari daftar hitam"
    )


@bot.on(admin_cmd(pattern="listblacklist$"))
@bot.on(sudo_cmd(pattern="listblacklist$", allow_sudo=True))
async def on_view_blacklist(event):
    all_blacklisted = sql.get_chat_blacklist(event.chat_id)
    OUT_STR = "Blacklists in the Current Chat:\n"
    if len(all_blacklisted) > 0:
        for trigger in all_blacklisted:
            OUT_STR += f"👉 {trigger} \n"
    else:
        OUT_STR = "No Blacklists found. Start saving using `.addblacklist`"
    if len(OUT_STR) > Config.MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(OUT_STR)) as out_file:
            out_file.name = "blacklist.text"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="Blacklists in the Current Chat",
                reply_to=event,
            )
            await event.delete()
    else:
        await edit_or_reply(event, OUT_STR)


CMD_HELP.update(
    {
        "blacklist": "__**NAMA PLUGIN :** Blacklist__\
    \n\n✅** CMD ➥** `.addblacklist` <word/words>\
    \n**Fungsi   ➥  **Kata atau kata-kata yang diberikan akan ditambahkan ke daftar hitam di obrolan tertentu itu jika ada pengguna yang mengirim, maka pesan itu akan dihapus.\
    \n\n✅** CMD ➥** `.rmblacklist` <word/words>\
    \n**Fungsi   ➥  **Kata atau kata-kata tertentu akan dihapus dari daftar hitam di obrolan tertentu itu\
    \n\n✅** CMD ➥** `.listblacklist`\
    \n**Fungsi   ➥  **Shows you the list of blacklist words in that specific chat\
    \n\n**NOTE : **Jika Anda menambahkan lebih dari satu kata sekaligus melalui ini, maka ingatlah bahwa kata baru harus diberikan di baris baru, bukan [halo].  itu harus seperti\
    [hai \n halo]"
    }
)
