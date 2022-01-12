logger_setup = {
    'handlers': [
        {
            'sink': 'logs/bot.log',
            'format': '{time:YYYY-MM-DD at HH:mm:ss} '
                      '| {level} | {message}',
            'encoding': 'utf-8',
            'level': 'DEBUG',
            'rotation': '5 MB',
            'compression': 'zip'
        },
    ],
}