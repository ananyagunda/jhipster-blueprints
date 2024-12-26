"""
Uvicorn config file. [Production]

by WeDAA (https://www.wedaa.tech/)

# Uvicorn Configuration File
# To run Uvicorn with this config, execute the script:
#
#       $ python uvicorn_prod_config.py
#
"""

import multiprocessing
import asyncio
import os
import logging
import signal
from dotenv import load_dotenv
from uvicorn import Config, Server

<%_ if (eureka) { _%>
from core import eureka
<%_ } _%>
<%_ if (rabbitmqClient != null && rabbitmqClient.length) { _%>
from main import send_message
<%_ } _%>
<%_ if (mongodb) { _%>
from core.mongodb import run_migrations as run_mongo_migrations
<%_ } _%>
<%_ if (postgresql) { _%>
from core.postgres import run_migrations as run_postgres_migrations
<%_ } _%>

# Load environment variables
load_dotenv()

# ===============================================
#           Server Socket
# ===============================================

HOST = "0.0.0.0"
PORT = <%= serverPort %>  # Replace <%= serverPort %> with your server port

# ===============================================
#           Worker Processes
# ===============================================

WORKERS = multiprocessing.cpu_count() * 2 + 1

# ===============================================
#           Logging
# ===============================================

LOG_LEVEL = "info"

# ===============================================
#           Security
# ===============================================

# Security parameters
LIMIT_REQUEST_LINE = 1024
LIMIT_REQUEST_FIELDS = 100
LIMIT_REQUEST_FIELD_SIZE = 1024

# ===============================================
#           Database Migrations
# ===============================================

async def async_migration():
    """Run migrations asynchronously when the server starts."""
    <%_ if (mongodb) { _%>
    print("Running MongoDB migrations...")
    await run_mongo_migrations()
    <%_ } _%>
    <%_ if (postgresql) { _%>
    print("Running PostgreSQL migrations...")
    await run_postgres_migrations()
    <%_ } _%>
    print("Migrations completed.")

# ===============================================
#           RabbitMQ Producer util
# ===============================================

<%_ if (rabbitmqClient != null && rabbitmqClient.length) { _%>
async def send_messages_concurrently():
    """Send RabbitMQ messages asynchronously."""
    try:
<%_ for (let i = 0; i < rabbitmqClient.length; i++) { _%>
        task<%= i + 1 %> = asyncio.create_task(
            send_message(
                "<%= baseName.charAt(0).toUpperCase() + baseName.slice(1) %>To<%= rabbitmqClient[i].charAt(0).toUpperCase() + rabbitmqClient[i].slice(1) %>_message_queue",
                {
                    "producer": "<%= baseName.charAt(0).toUpperCase() + baseName.slice(1) %>",
                    "consumer": "<%= rabbitmqClient[i].charAt(0).toUpperCase() + rabbitmqClient[i].slice(1) %>",
                },
            )
        )
<%_ } _%>
        await asyncio.gather(
<%_ for (let i = 0; i < rabbitmqClient.length; i++) { _%>
            task<%= i + 1 %><%= i + 1 < rabbitmqClient.length ? ',' : '' %>
<%_ } _%>
        )
    except Exception as e:
        logging.error(f"Error during RabbitMQ initialization: {e}")
<%_ } _%>

# ===============================================
#           Eureka Lifecycle
# ===============================================

<%_ if (eureka) { _%>
async def startup_eureka():
    """Start the Eureka client."""
    print("Starting Eureka client...")
    await eureka.startup_event()

async def shutdown_eureka():
    """Shutdown the Eureka client."""
    print("Shutting down Eureka client...")
    await eureka.shutdown_event()
<%_ } _%>

# ===============================================
#           Server Hooks
# ===============================================

async def startup_tasks():
    """Execute startup tasks."""
    print("Running startup tasks...")
    await async_migration()
    <%_ if (rabbitmqClient != null && rabbitmqClient.length) { _%>
    await send_messages_concurrently()
    <%_ } _%>
    <%_ if (eureka) { _%>
    await startup_eureka()
    <%_ } _%>
    print("Startup tasks completed.")

async def shutdown_tasks():
    """Execute shutdown tasks."""
    print("Running shutdown tasks...")
    <%_ if (eureka) { _%>
    await shutdown_eureka()
    <%_ } _%>
    print("Shutdown tasks completed.")

# Signal Handlers
def handle_signal(signum, frame):
    """Handle termination signals like SIGINT and SIGTERM."""
    logging.info("Signal received, exiting immediately.")
    os._exit(0)

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# ===============================================
#           Main Server Logic
# ===============================================

def main():
    """Main entry point for the server."""
    asyncio.run(startup_tasks())
    try:
        server = Server(
            Config(
                app="main:app",  # Replace 'main:app' with the actual module and app instance
                host=HOST,
                port=PORT,
                log_level=LOG_LEVEL,
                workers=WORKERS,
                limit_max_header_count=LIMIT_REQUEST_FIELDS,
                limit_max_header_size=LIMIT_REQUEST_FIELD_SIZE,
                limit_max_request_size=LIMIT_REQUEST_LINE,
            )
        )
        server.run()
    finally:
        asyncio.run(shutdown_tasks())

if __name__ == "__main__":
    main()
