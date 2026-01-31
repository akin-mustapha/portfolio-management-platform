# Prefect Server Hangs When you start

## Descriptions

Prefect server stopped working. I could start it, but it hangs, ui doesn't load.

### Commands

- prefect config view
- prefect server stop
- rm -rf ~/.prefect
- lsof -i :4200
- lsof -nP -iTCP:4200 -sTCP:LISTEN
