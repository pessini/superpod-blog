# Superpod

In case you want to use Ollama as a Docker Container.

## For Mac / Apple Silicon users

If you're using a Mac with an M1 or newer processor, you can't expose your GPU to the Docker instance, unfortunately. 
Currently GPU support in Docker Desktop is only available on Windows with the WSL2 backend.

There are two options in this case:

    - Run the ollama with docker on CPU.
    - Run Ollama on your Mac for faster inference, and connect to that from superpod.
