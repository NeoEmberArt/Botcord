import yt_dlp


@bot.tree.command(name="snag", description="Download any video from link (max 25mb each/max 10 links)")
@app_commands.describe(urls="One or more URLs separated by spaces")
async def download(interaction: discord.Interaction, urls: str):
    import random
    import os
    import traceback

    url_list = urls.split()
    max_files = 10
    max_size_mb = 10

    if len(url_list) > max_files:
        await interaction.response.send_message(f"Too many links! (max {max_files})", ephemeral=True)
        return

    await interaction.response.defer()
    # Cute success messages
    success_messages = [
        "here ya go :3",
        "meow file done!",
        "purrfect delivery~",
        "your download is ready!",
        "got it for you, enjoy!",
        "meow~ file incoming!",
        "here's your tasty download!",
        "done and delivered!",
        "snagged that for you!",
        "media at your paws!",
        "here ya go cuteness",
        "all set and shiny!",
        "does this mean i get treats?",
        "Im a good kitty arent i!?",
        "Great day for file transfers and hippo muzzles!",
        "fresh from the download oven!",
        "download magic complete!",
        "snuggled your media for you!",
        "mission complete, enjoy!",
        "happy kitty delivering!",
        "your vid is ready!",
        "Can i get cuddles from all this hard work?~",
        "wrapped it up nice just for you~",
        "NYA~~ You asked, i provided!",
        "Snuggles after?",
        "KISS BOYS, DOWNLOAD FILES",
        "snuck it out of the internet for ya~",
        "*holds out paw* here ya go!",
        "ta-da! file magically appeared!",
        "i fetched it like a good kitty!",
        "meownloaded successfully >w<",
        "it’s here and it’s adorable! wait, that's just you! ;3",
        "file’s here, all warm and cozy~",
        "fluff-approved and ready to go!",
        "MMMMMREEOW~ here!",
        "*gives file* :3",
        "*hands you the file cutely!*",
        "*Throws the file at ya*  :3",
        "Heck yeah! here ya go!",
        "pssst, i can download from nearly all links",
        "Done! Headpats now???",
        "It worked! Give headpats now!!",
        "Here ya go, now i demand headpats!!",

        # New entries
        "yaaay! i did it!!",
        "file go nyoom~ into your hands!",
        "success~ nya!",
        "zoomies complete, file fetched!",
        "meownload complete!",
        "*presents the file with sparkly eyes*",
        "delivered with extra fluff~",
        "meep! it’s done!",
        "brought it back like a proud kitty!",
        "*curls tail proudly* here it is~",
        "boop! download is done!",
        "i did a big smart, now here’s your file!",
        "*wiggles ears happily* file's ready!",
        "*sets file down gently and stares at you*",
        "*happy tail swishes* delivery successful!",
        "got it in one pounce~",
        "meowgic complete, file obtained!",
        "finished with extra squeaks~",
        "*excited bean noises* it’s done!",
        "ta-da nya! another success~",
        "*delivers file and demands chin scritches*",
        "zoom-zoom meow complete!",
        "done! now come pet meee~",
        "nyah! got it just for you, cutie~"
    ]


    # Cute error messages
    error_messages = {
        "download": [
        "uh oh! i tried and failed to snag this one... sowwy qwq",
        "something went ouchie while downloading... blame the gremlins!",
        "eep! i broke it T_T couldn't fetch this one.",
        "the download gods said no :c maybe try again?",
        "super bad error happened!",
        "big error!?",
        "i tripped on a cable, download failed!",
        "error 404: cuteness not found in file",
        "the media escaped my paws!",
        "fuzzy error in the system, try again?",
        "ow! my circuits hurt, download failed!",
        "uhuh, can't catch this one right now!",
        "a sneaky bug blocked the download!",
        "fluffy glitches stopped me :c",
        "error pawsing the download...",
        "nope nope nope, can't download that one!",
        "i dropped the file, try again?",
        "Download failed.",
        "please throw some treats and try again!",
        "meow meow, download broke! >.<",
    ],
    "toolarge": [
        "@BKexe_bot on telegram for larger file size (2gb)",
        "@BKexe_bot on telegram for larger file size (2gb)",
        "uhuh, cant upload it.. MRFFF TOO BIGG~ ",
        "this file is biggggggggg. discord said NOPE >///<",
        "hewwp it's too heavy for my lil paws! >w< max 25mb only!",
        "seems i hit a file limit for this one, try something smaller? ",
        "you expect me to give you that? i'm too small to hold something that large. ",
        "ARE YOU CRAZY!? THAT FILE IS TOO BIGGG!",
        "discord doesn't like that!",
        "HUFF, too biggggg~ ",
        "can't carry that big of a package! >.<",
        "that's a no-go, size too large!",
        "my paws can’t handle this size!",
        "send smaller bits, please!",
        "big file alert! gotta keep it tiny!",
        "sorry, too big!",
        "too bigggggggg",
        "File size too big, sorry!"
        "sorry fren, file too big!",
        "discord says 'nah' to that file size!",
        "cuter but smaller, please! >w<",
        "that file is larger than my... erm.... limits :3"
        "uhm... i tried, but discord slapped my paw away >///<",
        "maximum size exceeded!! try trimming it down~",
        "it's like... 10x my weight! nu-uh! too big!",
        "file’s a unit. a chonker. can’t do it.",
        "uploading that big a file would tear a hole in the snuggleverse! I refuse!",
        "i squeaked at the size and ran away!",
        
        "discord bonked me for even *trying* to upload that!",
         "discord bonked me for even *trying* to upload that!",
          "discord bonked me for even *trying* to upload that!",
        "gonna need a bigger basket for that file... maybe two!",
    ],
    "notfound": [
        "huh? file vanished after download... spooky O_O",
        "i downloaded it but... now it's gone? Odd...",
        "something went terribly wrong! but its okay ^^ try something else",
        "poof! file disappeared!",
        "its gone!?? nothing is thereeee",
        "MMMEEOWWW? I COULDENT FIND ITTT?!"
        "can't find the file anymore!",
        "file took a walk and didn't come back!",
        "uh-oh, the file ran away!",
        "looks like the file is hiding!",
        "error: file lost!",
        "file no-show, try again maybe?",
        "oopsie, file's not here!",
        "the file's playing hide and seek!",
        "file vanished without a trace!",
        "no file found, my paws are empty!",
    ],
    "novideo": [
        "couldn't find any video there... maybe it's private or gone :c",
        "tried looking but... no media found T~T",
        "the page is there, but the vid isn't! rip link?",
        "beep boop, no video??",
        "can't get anything from that URL, sorry!",
        "i looked but i couldn't find a video",
        "no vid detected, maybe it’s a secret?",
        "video must be ninja, I can't see it!",
        "looks like an empty box, no video inside!",
        "the link's shy, no video to show :(",
        "i searched high and low, no video found!",
        "video ghosted me, gone forever!",
        "no media on this link, sad cat :c",
        "nope, no vid here!",
        "the video is playing hide and seek!",
        "nothing but silence in this link...",
        "did the video get deleted? I can't find it!",
        "theres literally no video on that url i could find, sorry  :C"
        "link looks empty, no video content!",
        "can't grab what isn't there >w<",
        "no video detected, try another link maybe?",
    ],
    }

    for url in url_list:
        if not url.startswith("http"):
            await interaction.followup.send(f"That doesn't look like a link: `{url}`", ephemeral=True)
            continue

        try:
            downloaded_file = await asyncio.to_thread(download_twitter_media, url)

            if downloaded_file is None:
                msg = random.choice(error_messages["novideo"])
                await interaction.followup.send(f"{msg}\n`{url}`", ephemeral=True)
                continue

            if not os.path.exists(downloaded_file):
                msg = random.choice(error_messages["notfound"])
                await interaction.followup.send(f"{msg}\n`{url}`", ephemeral=True)
                continue

            file_size_mb = os.path.getsize(downloaded_file) / (1024 * 1024)
            if file_size_mb > max_size_mb:
                msg = random.choice(error_messages["toolarge"])
                file_size_display = f"-# {file_size_mb:.2f}MB"
                await interaction.followup.send(f"{msg}\n{file_size_display}\n`{url}`", ephemeral=True)
                os.remove(downloaded_file)
                continue


            chosen_msg = random.choice(success_messages)
            await interaction.followup.send(chosen_msg, file=discord.File(downloaded_file))
            os.remove(downloaded_file)

        except Exception as e:
            tb_str = str(e).lower()
            if any(key in tb_str for key in ["video unavailable", "unable to extract", "no video formats found"]):
                msg = random.choice(error_messages["novideo"])
            else:
                msg = random.choice(error_messages["download"])
            await interaction.followup.send(f"{msg}\n`{url}`", ephemeral=True)
