import re
import pandas as pd
from datetime import datetime

def parse_whatsapp_chat(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        chat_content = f.read()

    message_pattern = re.compile(r'^\u200e?\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] ([^:]+): (.*)', re.MULTILINE)

    messages = []
    for line in chat_content.split('\n'):
        match = message_pattern.match(line)
        if match:
            date_str, time_str, sender, message = match.groups()
            timestamp_str = f"{date_str} {time_str}"
            try:
                timestamp = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')
            except ValueError:
                timestamp = None
            messages.append({'timestamp': timestamp, 'sender': sender.strip(), 'message': message.strip()})
        elif messages:  # Append to the last message if it's a continuation line
            messages[-1]['message'] += '\n' + line.strip()

    df = pd.DataFrame(messages)
    return df

if __name__ == '__main__':
    df = parse_whatsapp_chat('test_chat.txt')
    print(df.to_string())


