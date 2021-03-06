# yaml_format is ported from uniborg
import io

from ..utils import admin_cmd, sudo_cmd
from . import CMD_HELP, parse_pre, reply_id, yaml_format


@bot.on(admin_cmd(pattern="json$"))
@bot.on(sudo_cmd(pattern="json$", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    the_real_message = None
    reply_to_id = await reply_id(event)
    if event.reply_to_msg_id:
        catevent = await event.get_reply_message()
    the_real_message = catevent.stringify()
    if len(the_real_message) > Config.MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(the_real_message)) as out_file:
            out_file.name = "json.text"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                reply_to=reply_to_id,
            )
            await event.delete()
    else:
        await edit_or_reply(event, the_real_message, parse_mode=parse_pre)


@bot.on(admin_cmd(pattern="yaml$"))
@bot.on(sudo_cmd(pattern="yaml$", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    the_real_message = None
    reply_to_id = await reply_id(event)
    if event.reply_to_msg_id:
        catevent = await event.get_reply_message()
    the_real_message = yaml_format(catevent)
    if len(the_real_message) > Config.MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(the_real_message)) as out_file:
            out_file.name = "yaml.text"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                reply_to=reply_to_id,
            )
            await event.delete()
    else:
        await edit_or_reply(event, the_real_message, parse_mode=parse_pre)


CMD_HELP.update(
    {
        "json": """__**NAMA PLUGIN :** Json__
      \n\n✅** CMD ➥** `.json` <balas>
      \n**Fungsi   ➥  **__Balas pesan untuk mendapatkan detail pesan itu dalam format json__  
      \n\n✅** CMD ➥** `.yaml` <balas>
      \n**Fungsi   ➥  **__Balas pesan untuk mendapatkan detail pesan itu dalam format yaml__ """
    }
)
