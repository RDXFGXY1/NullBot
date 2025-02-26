import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO

load_dotenv()

class Love(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="love", description="Love command")
    async def love(self, ctx, member: discord.Member = None):
        if member is None:
            await ctx.send("Please specify a member.")
            return

        love_percentage = random.randint(1, 100)
        future_status = "Future: Marriage"
        developer_info = f"Developed By: {os.getenv('OWNER_NAME')}"
        image_serial = f"Image Serial: {random.randint(1000, 9999)}"

        # Create the base image
        image_width = 800
        image_height = 600
        img = Image.new('RGBA', (image_width, image_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Draw the love percentage text
        try:
            font = ImageFont.truetype("cogs/funny/SmileDay.otf", 48)
        except IOError:
            print(f"Error loading font. Using a default font instead.")
            font = ImageFont.load_default()  # Fallback to a default font

        text = f"{love_percentage}%"
        
        # Use textbbox() instead of textsize()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        draw.text(((image_width - text_width) / 2, 20), text, font=font, fill="white")

        # Draw the heart in the middle
        heart = Image.new('RGBA', (image_width // 2, image_height // 2), (255, 255, 255, 0))
        heart_draw = ImageDraw.Draw(heart)
        heart_draw.polygon([(0, 128), (256, 512), (512, 128)], fill=(255, 0, 0, 128))

        # Get user avatars
        asset1 = ctx.author.display_avatar.with_size(128)
        asset2 = member.display_avatar.with_size(128)
        
        try:
            image1 = Image.open(BytesIO(await asset1.read()))
            image2 = Image.open(BytesIO(await asset2.read()))
        except Exception as e:
            print(f"Error opening avatar images: {e}")
            await ctx.send("Error processing avatars. Please try again later.")
            return

        # Paste avatars onto the heart
        heart.paste(image1, (0, 0))
        heart.paste(image2, (256, 0))

        # Paste heart onto the base image
        img.paste(heart, ((image_width - heart.width) // 2, 150))

        # Draw the future status text
        future_text = future_status
        bbox = draw.textbbox((0, 0), future_text, font=font)
        future_text_width = bbox[2] - bbox[0]
        future_text_height = bbox[3] - bbox[1]
        draw.text(((image_width - future_text_width) / 2, 470), future_text, font=font, fill="white")

        # Draw developer info
        developer_text = developer_info
        bbox = draw.textbbox((0, 0), developer_text, font=font)
        dev_text_width = bbox[2] - bbox[0]
        dev_text_height = bbox[3] - bbox[1]
        draw.text(((image_width - dev_text_width) / 2, 510), developer_text, font=font, fill="white")

        # Draw the image serial
        serial_text = image_serial
        bbox = draw.textbbox((0, 0), serial_text, font=font)
        serial_text_width = bbox[2] - bbox[0]
        serial_text_height = bbox[3] - bbox[1]
        draw.text(((image_width - serial_text_width) / 2, 550), serial_text, font=font, fill="white")

        # Save the image to send
        with BytesIO() as image_binary:
            try:
                img.save(image_binary, 'PNG')
            except Exception as e:
                print(f"Error saving image: {e}")
                await ctx.send("Error creating the image. Please try again.")
                return
            image_binary.seek(0)
            await ctx.send(file=discord.File(fp=image_binary, filename='love.png'))

async def setup(bot):
    await bot.add_cog(Love(bot))
