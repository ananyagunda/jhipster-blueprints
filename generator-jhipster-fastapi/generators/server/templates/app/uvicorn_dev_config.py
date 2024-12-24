"""
Uvicorn starter file [Development]

by WeDAA (https://www.wedaa.tech/)

# This script initializes the application using Uvicorn.
# To run the server, execute the following command:
#
#       $ python uvicorn_dev_starter.py
#
"""

import asyncio
import uvicorn
import os
import logging
from dotenv import load_dotenv

<%_ if (eureka) { _%>
from core import eureka
<%_ } _%>
<%_ if (mongodb) { _%>
from core.mongodb import run_migrations as run_mongo_migrations
<%_ } _%>
<%_ if (postgresql) { _%>
from core.postgres import run_migrations as run_postgres_migrations
<%_ } _%>
<%_ if (rabbitmqClient != null && rabbitmqClient.length) { _%>
from main import send_message
<%_ } _%>

load_dotenv()

# ===============================================
#           Database Migrations
# ===============================================

async def async_migration():
    """Run database migrations asynchronously."""
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
#           RabbitMQ Producer
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
#           Server Socket
# ===============================================

HOST = "0.0.0.0"
PORT = <%= serverPort %>  # Replace <%= serverPort %> with the actual port number

# ===============================================
#           Worker Processes
# ===============================================

WORKERS = 2

# ===============================================
#           Debugging
# ===============================================

RELOAD = True

# ===============================================
#           Logging
# ===============================================

LOG_LEVEL = "info"

# ===============================================
#           Main Server Logic
# ===============================================

async def startup_tasks():
    """Run all startup tasks."""
    await async_migration()
    <%_ if (rabbitmqClient != null && rabbitmqClient.length) { _%>
    await send_messages_concurrently()
    <%_ } _%>
    <%_ if (eureka) { _%>
    await startup_eureka()
    <%_ } _%>
    print("Startup tasks completed.")

async def shutdown_tasks():
    """Run all shutdown tasks."""
    <%_ if (eureka) { _%>
    await shutdown_eureka()
    <%_ } _%>
    print("Shutdown tasks completed.")

def main():
    """Main entry point for the Uvicorn server."""
    asyncio.run(startup_tasks())
    try:
        uvicorn.run(
            "main:app",  # Replace 'main:app' with the actual module and app instance
            host=HOST,
            port=PORT,
            log_level=LOG_LEVEL,
            reload=RELOAD,
            workers=WORKERS,
            lifespan="on",  # Enable lifecycle hooks
        )
    finally:
        asyncio.run(shutdown_tasks())

if __name__ == "__main__":
    main()
