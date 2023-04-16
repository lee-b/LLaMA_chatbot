# LLaMA_chatbot

WIP, based of https://github.com/spv420/LLaMA\_chatbot

## Development builds

- On debian-likes: `apt-get install $(cat requirements.apt)`, or the equivalent for your distro
- `poetry install`

## Running it
- Copy dot-envrc-example to .envrc edit it as needed
- Run `direnv allow` to activate your .envrc file, or just `source .envrc`
- Copy the example/* files to config/ and edit them if you like
- Install and run text-generation-webui per its instructions, and run with the `--listen` flag.
- Run `llamatrix`
- Login as another user, and start chatting with llamatrix on the server they're registered with.
- Enjoy

