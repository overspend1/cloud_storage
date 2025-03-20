# Cloud Storage Bot 🌥️

A Telegram bot that provides cloud storage functionality, allowing users to upload, download, and manage files through Telegram.

![Telegram Cloud Storage Bot](https://img.shields.io/badge/Telegram-Bot-blue)
![Python](https://img.shields.io/badge/Python-3.7+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Features

- 🔐 Authentication with password protection
- 📤 Upload files to cloud storage
- 📥 Download files from storage
- 📂 List all stored files
- 🗑️ Delete files
- ✏️ Rename files
- 🚚 Move files between directories
- 📄 Copy files
- 📝 View file metadata
- 🧹 Cleanup old files (30+ days old)
- 📊 View storage statistics
- 📈 Interactive progress animations

---

## 🛠️ Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/cloud-storage-bot.git
   cd cloud-storage-bot
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your Telegram Bot Token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

4. Run the bot:
   ```
   python cloud_bot.py
   ```

---

## 📄 Requirements

- Python 3.7+
- python-telegram-bot
- python-dotenv

Install all dependencies:
```
pip install python-telegram-bot python-dotenv
```

---

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and authenticate |
| `/help` | Show available commands |
| `/upload` | Upload a file |
| `/download` | Download a file |
| `/list` | List all stored files |
| `/delete` | Delete a file |
| `/rename` | Rename a file |
| `/move` | Move a file |
| `/copy` | Copy a file |
| `/metadata` | Show file information |
| `/cleanup` | Remove files older than 30 days |
| `/stats` | Show storage statistics |

---

## 🔧 Configuration

Edit the following variables in the `cloud_bot.py` file to customize your bot:

- `STORAGE_DIR`: Local directory for storing files
- `PASSWORD`: Authentication password
- `ADMIN_USERNAME`: Admin username for special privileges

---

## 🔒 Security Features

- Password-protected access
- Activity logging
- Session management
- Timestamped operations
- Admin controls

---

## 💡 Usage Example

1. Start a chat with your bot on Telegram
2. Enter `/start` to begin
3. Enter the authentication password
4. Use `/help` to see available commands
5. Upload a file by using `/upload` and then sending a file
6. Download a file using `/download` and selecting the file name

---

## 📊 Progress Animations

The bot includes interactive progress bars and animations to show:
- File upload progress
- Download preparation
- Cleanup operations
- Authentication process

---

## 📝 To-Do

- [ ] Add file compression
- [ ] Implement user access levels
- [ ] Add file sharing functionality
- [ ] Create file categories
- [ ] Add search functionality
- [ ] Implement file encryption

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

Your Name - [@yourusername](https://github.com/yourusername)

---

## 🙏 Acknowledgements

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Python-dotenv](https://github.com/theskumar/python-dotenv)
