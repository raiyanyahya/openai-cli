import click
import configparser
import openai
import requests
from requests.structures import CaseInsensitiveDict
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

import os

console = Console()

CONFIG_FILE_PATH = "config.ini"

def get_api_key():
    if not os.path.exists(CONFIG_FILE_PATH):
        api_key = input("Please enter your OpenAI API key: ")
        config = configparser.ConfigParser()
        config['openai'] = {'api_key': api_key}
        with open(CONFIG_FILE_PATH, 'w') as f:
            config.write(f)
    else:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        api_key = config.get('openai', 'api_key')
    return api_key

@click.group()
def cli():
    openai.api_key = get_api_key()

    if not openai.api_key:
        console.print("[bold red]No OpenAI API key found. Exiting...[/bold red]")
        raise click.Abort()

@cli.command()
@click.argument('prompt')
@click.option('--model', '-m', default='davinci', help='GPT-3 model to use')
@click.option('--max-tokens', '-t', default=2048, help='Max number of tokens in generated text')
@click.option('--temperature', '-tp', default=0.5, help='Sampling temperature for generated text')
def generate_text(prompt, model, max_tokens, temperature):
    try:
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=temperature,
        )

        message = response.choices[0].text.strip()
        console.print(f"[bold green]Output:[/bold green] {message}")
    except Exception as e:
        console.print(f"[bold red]Failed to generate text. Error: {e}[/bold red]")

@cli.command()
@click.argument('prompt')
@click.option('--model', '-m', default='image-alpha-001', help='DALL-E model to use')
@click.option('--size', '-s', default='256x256', help='Size of the generated image')
def generate_image(prompt, model, size):
    try:
        response = openai.Image.create(
            prompt=prompt,
            model=model,
            size=size
        )
        image_url = response['data'][0]['url']
        console.print(Markdown(f"![Generated Image]({image_url})"))
    except Exception as e:
        console.print(f"[bold red]Failed to generate image. Error: {e}[/bold red]")

@cli.command()
@click.pass_context
def get_quota(ctx):
    url = "https://api.openai.com/v1/usage"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {openai.api_key}"

    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        console.print(f"[bold red]Failed to fetch quota information. Status code: {resp.status_code}[/bold red]")
        return

    usage = resp.json()
    console.print(f"[bold green]API Key Quota:[/bold green]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Model")
    table.add_column("Current Usage")
    table.add_column("Limit")
    for model in usage["data"]:
        table.add_row(
            model["model"],
            str(model["usage"]),
            str(model["limit"]))
    console.print(table)

@cli.command()
@click.argument('text')
@click.option('--model', '-m', default='davinci', help='GPT-3 model to use')
@click.option('--max-length', '-l', default=50, help='Max summary length')
def summarize(text, model, max_length):
    try:
        response = openai.Completion.create(
            engine=model,
            prompt=f"Please summarize the following text:\n\n{text}\n\nSummary:",
            max_tokens=max_length,
            n=1,
            stop=None,
        )

        summary = response.choices[0].text.strip()
        console.print(f"[bold green]Summary:[/bold green] {summary}")
    except Exception as e:
        console.print(f"[bold red]Failed to summarize text. Error: {e}[/bold red]")

@cli.command()
@click.argument('code')
@click.option('--language', '-l', default='python', help='Programming language of the code')
@click.option('--max-tokens', '-t', default=1024, help='Max number of tokens in generated code')
@click.option('--temperature', '-tp', default=0.7, help='Sampling temperature for generated code')
def find_bug(code, language, max_tokens, temperature):
    try:
        prompt = f"Find a bug in the following {language} code:\n\n{code}\n\nBug description:"
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=temperature,
        )

        bug_description = response.choices[0].text.strip()
        console.print(f"[bold green]Bug Description:[/bold green] {bug_description}")
    except Exception as e:
        console.print(f"[bold red]Failed to find bug. Error: {e}[/bold red]")


@cli.command()
@click.argument('text')
@click.option('--model', '-m', default='text-davinci-002', help='GPT-3 model to use')
def grammar_correct(text, model):
    try:
        response = openai.Completion.create(
            engine=model,
            prompt=f"Please correct the following text for grammar errors:\n{text}",
            max_tokens=2048,
            n=1,
            stop=None,
            temperature=0.5,
        )

        message = response.choices[0].text.strip()
        console.print(f"[bold green]Output:[/bold green] {message}")
    except Exception as e:
        console.print(f"[bold red]Failed to correct grammar. Error: {e}[/bold red]")
