# LLaMA_chatbot

WIP, based of https://github.com/spv420/LLaMA\_chatbot

## Development builds

- On debian-likes: `apt-get install $(cat requirements.apt)`, or the equivalent for your distro
- `poetry install`

## Running it
- Copy dot-envrc-example to .envrc edit it as needed
- Download the LLaMA weights, whatever is the largest that'll fit on your GPU(s)
- Run text-generation-webui for that model, `--listen`
- Run `direnv allow` to activate your .envrc file, or just `source .envrc`
- llamatrix
- Enjoy

