import logging.config
import logging
import structlog


def configure_logging(processor, log_level='DEBUG'):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'formater': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': processor,
                # Adjust log entries that are not from structlog
                'foreign_pre_chain': [
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.add_logger_name,
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.format_exc_info,
                ],
            },
        },
        'handlers': {
            'default': {
                'level': log_level,
                # 'class': 'logging.StreamHandler',
                'class': 'logging.NullHandler',
                'formatter': 'formater',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': log_level,
                'propagate': True,
            },
        }
    })

    structlog.configure_once(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


