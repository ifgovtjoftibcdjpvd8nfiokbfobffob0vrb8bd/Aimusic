async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}_v4.png"):
        return f"cache/{videoid}_v4.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    results = VideosSearch(url, limit=1)
    for result in (await results.next())["result"]:
        try:
            title = result["title"]
            title = re.sub("\W+", " ", title)
            title = title.title()
        except:
            title = "Unsupported Title"
        try:
            duration = result["duration"]
        except:
            duration = "Unknown Mins"
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        try:
            views = result["viewCount"]["short"]
        except:
            views = "Unknown Views"
        try:
            channel = result["channel"]["name"]
        except:
            channel = "Unknown Channel"

    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    youtube = Image.open(f"cache/thumb{videoid}.png")
    image1 = changeImageSize(1280, 720, youtube)
    image2 = image1.convert("RGBA")
    background = image2.filter(filter=ImageFilter.BoxBlur(20))
    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.6)
    draw = ImageDraw.Draw(background)
    arial = ImageFont.truetype("ANNIEMUSIC/assets/thumb/font2.ttf", 30)
    font = ImageFont.truetype("ANNIEMUSIC/assets/thumb/font.ttf", 30)
    title_font = ImageFont.truetype("ANNIEMUSIC/assets/thumb/font3.ttf", 45)
    username_font = ImageFont.truetype("ANNIEMUSIC/assets/thumb/font2.ttf", 35)

    # CHANGE 1: Rectangular thumbnail instead of circle
    # Create rectangular thumbnail with slight rounded corners
    thumbnail_width, thumbnail_height = 400, 300
    thumbnail_x, thumbnail_y = 120, 210  # Adjusted position for rectangle
    
    # Resize youtube thumbnail to desired dimensions
    rect_thumbnail = youtube.resize((thumbnail_width, thumbnail_height))
    
    # Create mask for rounded corners
    mask = Image.new("L", (thumbnail_width, thumbnail_height), 0)
    mask_draw = ImageDraw.Draw(mask)
    corner_radius = 20
    mask_draw.rounded_rectangle([(0, 0), (thumbnail_width, thumbnail_height)], 
                                 radius=corner_radius, fill=255)
    
    # Add white border to thumbnail
    border_width = 5
    bordered_thumbnail = Image.new("RGBA", (thumbnail_width + 2*border_width, 
                                          thumbnail_height + 2*border_width), (255, 255, 255, 255))
    bordered_thumbnail.paste(rect_thumbnail, (border_width, border_width))
    
    # Create final mask with border
    final_mask = Image.new("L", (thumbnail_width + 2*border_width, 
                               thumbnail_height + 2*border_width), 0)
    final_mask_draw = ImageDraw.Draw(final_mask)
    final_mask_draw.rounded_rectangle([(0, 0), (thumbnail_width + 2*border_width, 
                                              thumbnail_height + 2*border_width)], 
                                       radius=corner_radius + border_width, fill=255)
    
    # Apply the mask and paste to background
    background.paste(bordered_thumbnail, (thumbnail_x - border_width, thumbnail_y - border_width), final_mask)

    text_x_position = 565

    title1 = truncate(title)
    draw.text((text_x_position, 180), title1[0], fill=(255, 255, 255), font=title_font)
    draw.text((text_x_position, 230), title1[1], fill=(255, 255, 255), font=title_font)
    
    # CHANGE 2: Add username with eye-catching style
    username = "@ScoutMusicBot"
    
    # Add a colored background for the username to make it stand out
    username_bg_width = 300
    username_bg_height = 45
    username_bg_x = text_x_position
    username_bg_y = 280
    
    # Draw gradient background for username
    for i in range(username_bg_width):
        # Create gradient from red to blue
        r = int(255 * (1 - i/username_bg_width))
        b = int(255 * (i/username_bg_width))
        g = 100
        draw.line([(username_bg_x + i, username_bg_y), 
                  (username_bg_x + i, username_bg_y + username_bg_height)], 
                  fill=(r, g, b), width=1)
    
    # Add a subtle glow effect
    draw.rounded_rectangle([(username_bg_x, username_bg_y), 
                          (username_bg_x + username_bg_width, username_bg_y + username_bg_height)], 
                          radius=10, outline=(255, 255, 255), width=2)
    
    # Draw the username text
    draw.text((username_bg_x + 10, username_bg_y + 5), username, 
              fill=(255, 255, 255), font=username_font)
    
    # Move channel info down slightly
    draw.text((text_x_position, 340), f"{channel}  |  {views[:23]}", (255, 255, 255), font=arial)

    line_length = 580

    red_length = int(line_length * 0.6)
    white_length = line_length - red_length

    # Adjust positions for progress bar
    progress_y = 400  # Moved down to accommodate username
    
    start_point_red = (text_x_position, progress_y)
    end_point_red = (text_x_position + red_length, progress_y)
    draw.line([start_point_red, end_point_red], fill="red", width=9)

    start_point_white = (text_x_position + red_length, progress_y)
    end_point_white = (text_x_position + line_length, progress_y)
    draw.line([start_point_white, end_point_white], fill="white", width=8)

    circle_radius = 10
    circle_position = (end_point_red[0], end_point_red[1])
    draw.ellipse([circle_position[0] - circle_radius, circle_position[1] - circle_radius,
                 circle_position[0] + circle_radius, circle_position[1] + circle_radius], fill="red")
    
    # Adjust time position
    draw.text((text_x_position, progress_y + 20), "00:00", (255, 255, 255), font=arial)
    draw.text((1080, progress_y + 20), duration, (255, 255, 255), font=arial)

    play_icons = Image.open("ANNIEMUSIC/assets/thumb/play_icons.png")
    play_icons = play_icons.resize((580, 62))
    background.paste(play_icons, (text_x_position, progress_y + 70), play_icons)

    try:
        os.remove(f"cache/thumb{videoid}.png")
    except:
        pass
    background.save(f"cache/{videoid}_v4.png")
    return f"cache/{videoid}_v4.png"