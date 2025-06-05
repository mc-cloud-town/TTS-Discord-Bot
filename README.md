# TTS Discord Bot

🎵 A powerful Discord bot that brings text-to-speech functionality to your server using the GPT-SoVITS v2 API. Transform text messages into natural-sounding speech with multiple character voices, including support for custom user voice samples.

## ✨ Features

### 🎙️ Text-to-Speech Capabilities
- **Multiple Character Voices**: Choose from a variety of pre-configured character voices
- **Custom Voice Samples**: Upload and use your own voice samples for personalized TTS
- **Real-time Voice Chat Integration**: Automatically convert text messages to speech in voice channels
- **Intelligent Text Processing**: Handles Discord mentions, markdown formatting, and special characters

### 🤖 AI Integration
- **LLM Commands**: Ask questions and get AI-powered responses with voice playback
- **Image Analysis**: Upload images along with questions for visual content analysis
- **Conversation History**: Maintains chat context for more natural conversations
- **Gemini AI Integration**: Powered by Google's Gemini language model

### 🎛️ Voice Management
- **Per-user Voice Settings**: Each user can configure their preferred voice character
- **Voice Channel Controls**: Join/leave voice channels with simple commands
- **TTS Toggle**: Enable/disable TTS functionality per user
- **Message Commands**: Right-click any message to convert it to speech

### 📋 Available Commands

#### Slash Commands
- `/ask` - Ask a question to the AI and get voice response
- `/chat` - Have a conversation with the AI assistant
- `/clear_chat` - Clear conversation history
- `/set_voice` - Configure your preferred voice character
- `/get_voice` - Check your current voice settings
- `/play_tts` - Convert text to speech and play in voice channel
- `/join_voice` - Make the bot join your voice channel
- `/leave_voice` - Make the bot leave the current voice channel
- `/tts_start` - Enable TTS functionality
- `/tts_stop` - Disable TTS functionality

#### Text Commands
- `!!tts start` - Enable automatic TTS for your messages
- `!!tts stop` - Disable automatic TTS for your messages

#### Context Menu Commands
- **Play TTS** - Right-click any message to convert it to speech

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- FFmpeg (included in the project)
- GPT-SoVITS v2 API server running on `http://127.0.0.1:9880/tts` or your custom endpoint
- Discord Bot Token
- Google Gemini API Key (for AI features)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/TTS-Discord-Bot.git
   cd TTS-Discord-Bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   GUILD_ID=your_discord_guild_id
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. **Set up voice samples**
   - Place voice sample files in the `data/samples/` directory
   - Configure sample metadata in `data/sample_data.json`

5. **Start the bot**
   ```bash
   python run.py
   ```
   
   Or use the provided batch file on Windows:
   ```bash
   start.bat
   ```

## 📁 Project Structure

```
TTS-Discord-Bot/
├── bot/                           # Core bot modules
│   ├── api/                       # API integrations
│   │   ├── gemini_api.py          # Google Gemini API client
│   │   ├── gemini_chat_history.py # Chat history management
│   │   └── tts_handler.py         # TTS processing and audio generation
│   ├── commands/                  # Slash commands
│   │   ├── general.py             # General utility commands
│   │   ├── llm_commands.py        # AI/LLM related commands
│   │   ├── tts_commands.py        # TTS configuration commands
│   │   └── voice_commands.py      # Voice channel management
│   ├── events/                    # Event listeners
│   │   ├── message_listener.py    # Target channel message processing
│   │   ├── on_ready.py            # Bot startup events
│   │   └── voice_chat_text_channel_listener.py # Voice chat text processing
│   └── message_command/           # Context menu commands
│       ├── analyze_material.py    # Material analysis
│       └── play_tts.py            # Message TTS conversion
├── data/                          # Data storage
│   ├── samples/                   # Voice sample files
│   ├── conversations/             # Chat history storage
│   └── *.json                     # Configuration files
├── utils/                         # Utility functions
├── config.py                      # Configuration settings
└── run.py                         # Main entry point
```

## ⚙️ Configuration

### Voice Samples
Add new voice characters by:
1. Placing audio files in `data/samples/`
2. Adding character metadata to `data/sample_data.json`:
   ```json
   {
     "character_name": {
       "file": "character_voice.wav",
       "text": "Sample text for this character"
     }
   }
   ```

### Channel Configuration
Configure target channels in `config.py`:
- `TTS_TARGET_CHANNEL_ID`: Channel for message-based TTS
- `VOICE_TEXT_INPUT_CHANNEL_IDS`: Channels for automatic voice chat TTS

## 🔧 Dependencies

- **disnake**: Discord API wrapper
- **google-genai**: Google Gemini API client
- **pydub**: Audio processing
- **requests**: HTTP requests
- **python-dotenv**: Environment variable management
- **PyNaCl**: Voice functionality

## 📝 Usage Examples

### Basic TTS Usage
1. Join a voice channel
2. Use `/tts_start` to enable automatic TTS
3. Type messages in configured channels to hear them spoken
4. Use `/set_voice` to change your voice character

### AI Conversations
1. Use `/ask "What is the weather like?"` for one-time questions
2. Use `/chat "Hello!"` to start a conversation
3. Upload images with `/ask` for visual analysis
4. Use `/clear_chat` to reset conversation history

### Voice Sample Management
1. Upload your voice samples to `data/samples/`
2. Select "自己聲音 (需要先上傳語音樣本）" in `/set_voice`
3. The bot will use your custom voice for TTS

## 🐳 Docker Support

A Dockerfile is included for containerized deployment:

```bash
docker build -t tts-discord-bot .
docker run -d --env-file .env tts-discord-bot
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [disnake](https://github.com/DisnakeDev/disnake) Discord API library
- Powered by [GPT-SoVITS v2](https://github.com/RVC-Boss/GPT-SoVITS) for high-quality TTS
- AI features provided by Google Gemini
- Supports multiple languages with focus on Traditional Chinese
