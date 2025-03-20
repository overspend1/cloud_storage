import logging
import os
import shutil
import datetime
import time
import asyncio
from enum import Enum, auto
from typing import Dict, Union
from datetime import datetime, timezone
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Load environment variables
load_dotenv()

# Get bot token from environment variable
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
STORAGE_DIR = 'local_storage'
PASSWORD = 'cloudstorage1'
ADMIN_USERNAME = 'overspend1'
ANIMATION_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
UPLOAD_PROGRESS = ["▱", "▰"]

# Create storage directory if it doesn't exist
os.makedirs(STORAGE_DIR, exist_ok=True)

# State definitions for conversation
class States(Enum):
    WAITING_FOR_PASSWORD = auto()
    WAITING_FOR_FILENAME = auto()
    WAITING_FOR_NEWNAME = auto()

# Store user sessions and activity
user_sessions: Dict[int, Dict] = {}

def get_current_time() -> str:
    """Get current UTC time in YYYY-MM-DD HH:MM:SS format."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def format_progress_bar(progress: float, width: int = 20) -> str:
    """Create a progress bar string."""
    filled = int(width * progress / 100)
    bar = UPLOAD_PROGRESS[1] * filled + UPLOAD_PROGRESS[0] * (width - filled)
    return f"[{bar}] {progress:.1f}%"

async def animate_progress(message, text: str, total_time: int = 3):
    """Animate a progress message."""
    start_time = time.time()
    while time.time() - start_time < total_time:
        for frame in ANIMATION_FRAMES:
            progress = min(100, ((time.time() - start_time) / total_time) * 100)
            progress_bar = format_progress_bar(progress)
            try:
                await message.edit_text(f"{text}\n{frame} {progress_bar}")
                await asyncio.sleep(0.1)
            except:
                pass

async def log_activity(user_id: int, action: str) -> None:
    """Log user activity with timestamp."""
    timestamp = get_current_time()
    if user_id in user_sessions:
        user_sessions[user_id]['last_activity'] = timestamp
        user_sessions[user_id]['activities'].append(f"{timestamp} - {action}")async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States.WAITING_FOR_PASSWORD:
    """Start the conversation and ask for password."""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    msg = await update.message.reply_text(
        f"🌟 Welcome to Cloud Storage Bot!\n"
        f"Current time (UTC): {get_current_time()}\n"
        f"Your username: {username}"
    )
    
    await animate_progress(msg, "Initializing bot...")
    
    await msg.edit_text(
        f"👋 Welcome to Cloud Storage Bot!\n"
        f"Current time (UTC): {get_current_time()}\n"
        f"Your username: {username}\n"
        "Please enter the password to continue."
    )
    
    user_sessions[user_id] = {
        'username': username,
        'authenticated': False,
        'last_activity': get_current_time(),
        'activities': []
    }
    
    return States.WAITING_FOR_PASSWORD

async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, States]:
    """Check the provided password."""
    user_id = update.effective_user.id
    if update.message.text == PASSWORD:
        user_sessions[user_id]['authenticated'] = True
        await log_activity(user_id, "Authentication successful")
        msg = await update.message.reply_text("Verifying password...")
        await animate_progress(msg, "Authenticating...")
        await msg.edit_text(
            f"✅ Password accepted! Use /help to see available commands.\n"
            f"Current time (UTC): {get_current_time()}"
        )
        return ConversationHandler.END
    else:
        await log_activity(user_id, "Authentication failed")
        await update.message.reply_text("❌ Incorrect password. Please try again.")
        return States.WAITING_FOR_PASSWORD

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message."""
    user_id = update.effective_user.id
    if not user_sessions.get(user_id, {}).get('authenticated', False):
        await update.message.reply_text("❌ Please use /start to enter password first.")
        return

    msg = await update.message.reply_text("Loading help...")
    await animate_progress(msg, "Loading commands...")

    help_text = f"""
📚 Available commands:
/upload - Upload a file 📤
/download - Download a file 📥
/list - List files 📂
/delete - Delete a file 🗑️
/rename - Rename a file ✏️
/move - Move a file 🚚
/copy - Copy a file 📄
/metadata - Show file info 📝
/cleanup - Remove old files 🧹
/stats - Show statistics 📊
/help - Show this message ℹ️

Current time (UTC): {get_current_time()}
Your username: {update.effective_user.username}
"""
    await log_activity(user_id, "Viewed help")
    await msg.edit_text(help_text)

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /upload command."""
    user_id = update.effective_user.id
    if not user_sessions.get(user_id, {}).get('authenticated', False):
        await update.message.reply_text("❌ Please use /start to enter password first.")
        return
    
    await log_activity(user_id, "Initiated file upload")
    msg = await update.message.reply_text("Preparing upload...")
    await animate_progress(msg, "Initializing upload system...")
    await msg.edit_text(
        f"📤 Please send me any file to upload to cloud storage.\n"
        f"Current time (UTC): {get_current_time()}\n"
        f"User: {update.effective_user.username}"
    )

async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle uploaded files."""
    user_id = update.effective_user.id
    if not user_sessions.get(user_id, {}).get('authenticated', False):
        await update.message.reply_text("❌ Please use /start to enter password first.")
        return

    try:
        file = update.message.document
        if not file:
            await update.message.reply_text("❌ Please send a file to upload.")
            return

        file_name = file.file_name
        file_path = os.path.join(STORAGE_DIR, file_name)

        # Check if file already exists
        if os.path.exists(file_path):
            await update.message.reply_text(
                f"⚠️ File {file_name} already exists.\n"
                f"Please rename the file or delete the existing one.\n"
                f"Current time (UTC): {get_current_time()}"
            )
            return

        msg = await update.message.reply_text("Starting upload...")
        
        # Simulate upload progress
        progress_steps = [0, 20, 40, 60, 80, 90, 95, 100]
        for progress in progress_steps:
            progress_bar = format_progress_bar(progress)
            await msg.edit_text(
                f"📤 Uploading {file_name}...\n"
                f"{progress_bar}\n"
                f"⏳ Please wait..."
            )
            await asyncio.sleep(0.5)

        new_file = await context.bot.get_file(file.file_id)
        await new_file.download_to_drive(custom_path=file_path)
        
        file_size = os.path.getsize(file_path)
        await log_activity(user_id, f"Uploaded file: {file_name} ({file_size / 1024:.1f} KB)")
        
        # Final success message
        await msg.edit_text(
            f"✅ File uploaded successfully!\n"
            f"📄 Name: {file_name}\n"
            f"📦 Size: {file_size / 1024:.1f} KB\n"
            f"⏰ Time: {get_current_time()}\n"
            f"👤 Uploaded by: {update.effective_user.username}\n"
            f"{format_progress_bar(100)}"
        )
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        await update.message.reply_text(
            "❌ Error uploading file. Please try again.\n"
            f"Time: {get_current_time()}"
        )async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States.WAITING_FOR_FILENAME:
    """Ask for file name to download."""
    user_id = update.effective_user.id
    if not user_sessions.get(user_id, {}).get('authenticated', False):
        await update.message.reply_text("❌ Please use /start to enter password first.")
        return ConversationHandler.END

    msg = await update.message.reply_text("Loading file list...")
    await animate_progress(msg, "Scanning storage...")

    # List available files
    files = os.listdir(STORAGE_DIR)
    if not files:
        await msg.edit_text(
            f"📂 Storage is empty. No files to download.\n"
            f"Current time (UTC): {get_current_time()}"
        )
        return ConversationHandler.END

    file_list = "Available files:\n"
    for file in files:
        size = os.path.getsize(os.path.join(STORAGE_DIR, file))
        file_list += f"📄 {file} ({size / 1024:.1f} KB)\n"

    await msg.edit_text(
        f"📥 Enter the name of the file you want to download:\n\n{file_list}\n"
        f"Current time (UTC): {get_current_time()}"
    )
    return States.WAITING_FOR_FILENAME

async def handle_download_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle file download."""
    user_id = update.effective_user.id
    file_name = update.message.text
    file_path = os.path.join(STORAGE_DIR, file_name)

    try:
        if os.path.exists(file_path):
            msg = await update.message.reply_text("Preparing download...")
            await animate_progress(msg, "Preparing file...")

            file_size = os.path.getsize(file_path)
            await msg.edit_text(
                f"📤 Sending file: {file_name}\n"
                f"📦 Size: {file_size / 1024:.1f} KB\n"
                f"⏰ Time: {get_current_time()}\n"
                f"{format_progress_bar(50)}"
            )

            # Send the actual file
            with open(file_path, 'rb') as file:
                await update.message.reply_document(
                    document=file,
                    filename=file_name,
                    caption=f"✅ File downloaded at {get_current_time()}"
                )
            
            await msg.edit_text(
                f"✅ Download complete!\n"
                f"📄 {file_name}\n"
                f"⏰ {get_current_time()}\n"
                f"{format_progress_bar(100)}"
            )
            
            await log_activity(user_id, f"Downloaded file: {file_name}")
        else:
            await update.message.reply_text(
                f"❌ File {file_name} not found.\n"
                f"Time: {get_current_time()}"
            )
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        await update.message.reply_text(
            "❌ Error downloading file. Please try again.\n"
            f"Time: {get_current_time()}"
        )

    return ConversationHandler.END

async def delete_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States.WAITING_FOR_FILENAME:
    """Ask for file name to delete."""
    user_id = update.effective_user.id
    if not user_sessions.get(user_id, {}).get('authenticated', False):
        await update.message.reply_text("❌ Please use /start to enter password first.")
        return ConversationHandler.END

    msg = await update.message.reply_text("Loading file list...")
    await animate_progress(msg, "Scanning storage...")

    files = os.listdir(STORAGE_DIR)
    if not files:
        await msg.edit_text(
            f"📂 Storage is empty. No files to delete.\n"
            f"Current time (UTC): {get_current_time()}"
        )
        return ConversationHandler.END

    file_list = "Available files:\n"
    for file in files:
        size = os.path.getsize(os.path.join(STORAGE_DIR, file))
        file_list += f"📄 {file} ({size / 1024:.1f} KB)\n"

    await msg.edit_text(
        f"🗑️ Enter the name of the file to delete:\n\n{file_list}\n"
        f"Current time (UTC): {get_current_time()}"
    )
    return States.WAITING_FOR_FILENAME

async def handle_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle file deletion."""
    user_id = update.effective_user.id
    file_name = update.message.text
    file_path = os.path.join(STORAGE_DIR, file_name)

    msg = await update.message.reply_text("Processing deletion request...")
    await animate_progress(msg, "Deleting file...")

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            await log_activity(user_id, f"Deleted file: {file_name}")
            await msg.edit_text(
                f"✅ File {file_name} deleted successfully.\n"
                f"⏰ Time: {get_current_time()}"
            )
        else:
            await msg.edit_text(
                f"❌ File {file_name} not found.\n"
                f"Time: {get_current_time()}"
            )
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        await msg.edit_text(
            "❌ Error deleting file.\n"
            f"Time: {get_current_time()}"
        )

    return ConversationHandler.END

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show storage statistics."""
    user_id = update.effective_user.id
    if not user_sessions.get(user_id, {}).get('authenticated', False):
        await update.message.reply_text("❌ Please use /start to enter password first.")
        return

    msg = await update.message.reply_text("Loading statistics...")
    await animate_progress(msg, "Calculating storage usage...")

    try:
        files = os.listdir(STORAGE_DIR)
        total_size = sum(os.path.getsize(os.path.join(STORAGE_DIR, f)) for f in files)
        
        stats_text = (
            f"📊 Storage Statistics (as of {get_current_time()}):\n"
            f"📁 Total files: {len(files)}\n"
            f"💾 Total size: {total_size / 1024 / 1024:.1f} MB\n"
            f"👥 Active users: {len(user_sessions)}\n"
            f"👤 Current user: {update.effective_user.username}\n"
            f"🕒 Last activity: {user_sessions[user_id]['last_activity']}"
        )
        
        await log_activity(user_id, "Viewed statistics")
        await msg.edit_text(stats_text)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await msg.edit_text(
            "❌ Error getting statistics.\n"
            f"Time: {get_current_time()}"
        )

async def cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clean up old files (older than 30 days)."""
    user_id = update.effective_user.id
    if not user_sessions.get(user_id, {}).get('authenticated', False):
        await update.message.reply_text("❌ Please use /start to enter password first.")
        return

    msg = await update.message.reply_text("Starting cleanup...")
    await animate_progress(msg, "Scanning for old files...")

    try:
        now = datetime.now()
        deleted = 0
        deleted_size = 0
        
        for file in os.listdir(STORAGE_DIR):
            file_path = os.path.join(STORAGE_DIR, file)
            if os.path.isfile(file_path):
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (now - mtime).days > 30:
                    size = os.path.getsize(file_path)
                    deleted_size += size
                    os.remove(file_path)
                    deleted += 1
                    await msg.edit_text(
                        f"🗑️ Removing old file: {file}\n"
                        f"{format_progress_bar(deleted * 100 / len(os.listdir(STORAGE_DIR)))}"
                    )
        
        await log_activity(user_id, f"Cleanup: removed {deleted} files ({deleted_size / 1024 / 1024:.1f} MB)")
        await msg.edit_text(
            f"✅ Cleanup complete!\n"
            f"🗑️ Removed {deleted} old files\n"
            f"💾 Freed up: {deleted_size / 1024 / 1024:.1f} MB\n"
            f"⏰ Time: {get_current_time()}"
        )
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        await msg.edit_text(
            "❌ Error during cleanup.\n"
            f"Time: {get_current_time()}"
        )

def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable is not set")
        return
        
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler for password protection
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            States.WAITING_FOR_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add delete conversation handler
    delete_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("delete", delete_file_command)],
        states={
            States.WAITING_FOR_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    # Add download conversation handler
    download_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("download", download)],
        states={
            States.WAITING_FOR_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download_request)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(delete_conv_handler)
    application.add_handler(download_conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_files))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("cleanup", cleanup))
    application.add_handler(CommandHandler("upload", upload))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file_upload))

    # Start the bot
    print(f"🤖 Bot started at {get_current_time()}")
    print(f"👤 Admin username: {ADMIN_USERNAME}")
    print(f"📁 Storage directory: {os.path.abspath(STORAGE_DIR)}")
    application.run_polling()

if __name__ == "__main__":
    main()
