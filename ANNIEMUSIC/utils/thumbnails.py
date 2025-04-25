import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from ANNIEMUSIC import app
from config import YOUTUBE_IMG_URL

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def truncate(text):
    list = text.split(" ")
    text1 = ""
    text2 = ""    
    for i in list:
        if len(text1) + len(i) < 30:        
            text1 += " " + i
        elif len(text2) + len(i) < 30:       
            text2 += " " + i

    text1 = text1.strip()
    text2 = text2.strip()     
    return [text1,text2]

def crop_center_circle(img, output_size, border, crop_scale=1.5):
    half_the_width = img.size[0] / 2
    half_the_height = img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    img = img.crop(
        (
            half_the_width - larger_size/2,
            half_the_height - larger_size/2,
            half_the_width + larger_size/2,
            half_the_height + larger_size/2
        )
    )
    
    img = img.resize((output_size - 2*border, output_size - 2*border))
    
    
    final_img = Image.new("RGBA", (output_size, output_size), "white")
    
    
    mask_main = Image.new("L", (output_size - 2*border, output_size - 2*border), 0)
    draw_main = ImageDraw.Draw(mask_main)
    draw_main.ellipse((0, 0, output_size - 2*border, output_size - 2*border), fill=255)
    
    final_img.paste(img, (border, border), mask_main)
    
    
    mask_border = Image.new("L", (output_size, output_size), 0)
    draw_border = ImageDraw.Draw(mask_border)
    draw_border.ellipse((0, 0, output_size, output_size), fill=255)
    
    result = Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)
    
    return result


async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}_v4.png"):
        return f"cache/{videoid}_v4.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    results = VideosSearch(url, limit=1)
    for result in (await results.next())["result"]:
        try:
            title = result["title"]
            # Preserve original title without removing Unicode
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
    
    # Use a font that supports Hindi characters
    arial = ImageFont.truetype("ANNIEMUSIC/assets/thumb/font2.ttf", 30)
    font = ImageFont.truetype("ANNIEMUSIC/assets/thumb/font.ttf", 30)
    title_font = ImageFont.truetype("ANNIEMUSIC/assets/thumb/font3.ttf", 45)
    username_font = ImageFont.truetype("ANNIEMUSIC/assets/thumb/font2.ttf", 35)

    # CHANGE 1: Rectangular thumbnail centered vertically with song controls
    thumbnail_width, thumbnail_height = 400, 400  # Taller rectangle
    thumbnail_x, thumbnail_y = 120, 160  # Higher position
    
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

    # USERNAME FIRST (above song title)
    username = ""
    
    # Draw username text above the title
    username_y = 140  # Position username above the title
    
    # Add a subtle shadow for the username to make it stand out
    shadow_offset = 2
    draw.text((text_x_position + shadow_offset, username_y + shadow_offset), 
              username, fill=(50, 50, 50), font=username_font)  # Shadow
    draw.text((text_x_position, username_y), username, 
              fill=(255, 255, 255), font=username_font)  # White text
    
    # Modified truncate function to handle Hindi text appropriately
    def truncate_text(text, max_length=30):
        if not text:
            return ["", ""]
        
        words = text.split(" ")
        line1 = ""
        line2 = ""
        
        for word in words:
            # For simplicity, just count characters instead of rendered width
            if len(line1) + len(word) < max_length:
                line1 += " " + word if line1 else word
            elif len(line2) + len(word) < max_length:
                line2 += " " + word if line2 else word
            else:
                # If we can't fit it in line2, just stop
                break
                
        return [line1, line2]
    
    # Split the title for proper display
    title_lines = truncate_text(title, 30)
    
    # Draw title with proper spacing (below username)
    title_y = 190  # Adjusted to be below username
    draw.text((text_x_position, title_y), title_lines[0], fill=(255, 255, 255), font=title_font)
    if title_lines[1]:
        draw.text((text_x_position, title_y + 50), title_lines[1], fill=(255, 255, 255), font=title_font)
    
    # Channel info below title
    channel_y = 310  # Adjusted position
    draw.text((text_x_position, channel_y), f"{channel}  |  {views[:23]}", (255, 255, 255), font=arial)

    line_length = 580

    red_length = int(line_length * 0.6)
    white_length = line_length - red_length

    # Adjust positions for progress bar
    progress_y = 370  # Position for progress bar
    
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
