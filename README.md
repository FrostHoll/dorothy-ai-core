# Dorothy AI
<p align="center"> <img src="https://img.shields.io/badge/Python-3.13-blue?logo=python" alt="Python"/> <img src="https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi" alt="FastAPI"/> <img src="https://img.shields.io/badge/LLM-llama.cpp-orange" alt="LLM"/> <img src="https://img.shields.io/badge/ASR-Whisper-yellow" alt="Whisper"/> <img src="https://img.shields.io/badge/TTS-Silero-purple" alt="TTS"/> <img src="https://img.shields.io/badge/Discord.py-2.7-blueviolet" alt="Discord"/> <img src="https://img.shields.io/badge/Status-Development-lightgrey" alt="Status"/></p>

## Оглавление

- Описание проекта

- Архитектура

- Сервисы

- Технологический стек

- Демонстрация (WIP)

- Запуск и развертывание (WIP)

- Roadmap

## Описание проекта

Это полностью кастомизируемая микросервисная система для создания ИИ-ассистента, поддерживающего текстовый и голосовой каналы связи. В отличие от монолитных решений, данный подход позволяет гибко масштабировать отдельные компоненты (например, выносить TTS/STT на GPU) и заменять их на альтернативные модели без остановки всей системы.

Проект демонстрирует применение современных подходов к разработке:

Микросервисная архитектура с разделением ответственности.

Асинхронное взаимодействие (HTTP + планируется gRPC/Message Broker).

Интеграция SOTA-моделей (LLM, Whisper, Silero TTS).

Контейнеризация и оркестрация (Docker Compose).

## Архитектура

Система спроектирована по принципу "каждый сервис отвечает за свою доменную область". Связь между сервисами происходит синхронно через REST API (FastAPI).

**Описание потока данных:**

Текст: Сообщение от пользователя идет напрямую в core для генерации ответа.

Голос: Аудиосообщение попадает в voice-orchestrator, который последовательно вызывает STT -> core -> TTS, возвращая голосовой ответ обратно в Discord.

## Сервисы

1. Core (LLM Service)

Роль: Мозг системы.

**Функции:**

Загрузка и инференс LLM через llama-cpp-python (поддержка GGUF моделей).

Управление историей диалога (краткосрочная и долгосрочная память) на SQLite.

Текстовая генерация ответа.

Технологии: FastAPI, llama-cpp, SQLite, Pydantic.

2. Discord Bot Service

Роль: Интерфейс для пользователя в мессенджере.

**Функции:**

Обработка текстовых команд и сообщений.

Прием и ретрансляция голосовых сообщений в voice-orchestrator.

Отправка ответов (текст/голос) обратно в канал Discord.

Технологии: discord.py.

3. Voice Orchestrator

Роль: Дирижер голосового пайплайна.

**Функции:**

Принимает аудио, отправляет его в STT.

Полученный текст отправляет в core за ответом.

Текстовый ответ отправляет в TTS.

Возвращает итоговый аудиофайл в Discord-сервис.

Технологии: FastAPI, python-multipart, aiohttp.

4. STT (Speech-to-Text)

Роль: Преобразование речи в текст.

**Функции:**

Инференс модели Whisper для транскрибации аудио.

Технологии: FastAPI, faster-whisper.

5. TTS (Text-to-Speech)

Роль: Озвучивание ответов.

**Функции:**

Синтез речи из текста с помощью модели Silero TTS.

Технологии: FastAPI, TTS (Silero).

## Технологический стек

Backend: Python 3.11, FastAPI, Uvicorn

Модели ИИ: LLaMA (через llama.cpp), OpenAI Whisper, Silero TTS

База данных: SQLite (для хранения памяти/истории)

Интеграция: Discord API

Инфраструктура: Docker, Docker Compose, Git

## Roadmap / Планы по развитию

- Внедрение асинхронной очереди (RabbitMQ/Kafka) для отвязки оркестратора от синхронных вызовов.

- Добавить векторную базу данных (Chroma/FAISS) для долгосрочной памяти (RAG).

- Поддержка Telegram.

- Мониторинг (Prometheus + Grafana).

## Автор

Щербаков Олег – [Telegram](https://t.me/FrostHoll)
