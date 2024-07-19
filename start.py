import os


commands = [
    # "poetry shell",
    "poetry update package",
    # "docker pull postgres",
    "docker-compose up -d",
    "alembic",
    "alembic upgrade head",
    "uvicorn main:app --host localhost --port 8000 --reload",
]



def run_command(command):
    print("Running command: {}".format(command))
    os.system(command)


for command in commands:
    run_command(command)
