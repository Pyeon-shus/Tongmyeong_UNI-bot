# bot_utils.py
async def load_extensions(bot):
    cogs = ['introduce', 'food_menu', 'weather', 'academic_schedule', 'notice', 'admin_commands', 'shuttle_timetable', 'ping_command', 'send_message']
    for cog in cogs:
        try:
            await bot.load_extension(f'cogs.{cog}')
            print(f"Loaded extension: {cog}")
        except Exception as e:
            print(f"Failed to load extension {cog}: {e}")