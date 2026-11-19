from telegram import Update
from telegram import error
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment

import speech_recognition as sr
import os

TOKEN = "7977883231:AAHbcUSdK5S7Um6k73V0JciBWNiDRE5jres"  # Замените на реальный токен


def convert_aac_to_format(input_aac_path: str, output_path: str):
    try:
        # Загружаем AAC-файл
        print(input_aac_path)
        print(output_path)
        audio = AudioSegment.from_file(input_aac_path, format=input_aac_path.split(".")[-1])
        # Определяем формат из расширения выходного файла
        output_format = output_path.split(".")[-1]
        # Конвертируем и сохраняем
        audio.export(output_path, format=output_format)
        print(f"✅ Файл успешно конвертирован: {output_path}")
    except Exception as e:
        print(f"❌ Ошибка конвертации: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот. Пришлите аудиофайл")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.voice:
            audio_file = await update.message.voice.get_file()
            file_path = f"audio_{update.message.message_id}.ogg"
        elif update.message.audio:
            audio_file = await update.message.audio.get_file()
            file_path = f"audio_{update.message.message_id}." + update.message.audio.file_name.split(".")[-1]
        else:
            await update.message.reply_text("Пожалуйста, отправьте голосовое сообщение или аудиофайл.")
            return
        print(1)
        # Скачиваем файл
        file_path2 = f"audio_{update.message.message_id}.wav"
        await audio_file.download_to_drive(file_path)
        print(2)
        audio = AudioSegment.from_file(file_path)
        x = (len(audio))
        print(x)
        # Преобразуем аудио в текст
        try:
            convert_aac_to_format(file_path, file_path2)
            text = audio_to_text(file_path2)
            await update.message.reply_text(f"🔊 Распознанный текст:\n\n{text}")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
        finally:
            # Удаляем временный файл
             if os.path.exists(file_path):
                print("del")
                os.remove(file_path)
                os.remove(file_path2)
    except error.BadRequest as e:
        if "File is too big" in str(e):
            await update.message.reply_text("❌ Файл слишком большой для обработки")
        else:
            await update.message.reply_text(f"❌ Ошибка Telegram: {e}")
    except Exception as e:
        await update.message.reply_text(f"❌ Произошла ошибка: {e}")

def audio_to_text(audio_path: str) -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data, language="ru-RU")
        return text
    except sr.UnknownValueError:
        return "Не удалось распознать речь"
    except sr.RequestError:
        return "Ошибка сервиса распознавания"

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", start))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()