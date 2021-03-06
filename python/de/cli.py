import asyncio
import functools
from pathlib import Path
from typing import Any, Awaitable, Callable, List, Union

import click
import click_log

from de.config import Config, PROJECT_ROOT, SCRIPTS_DIR, SRC_ROOT, TESTS_DIR
from de.discord import DiscordBot, EDIT, REPLACE
from de.logger import logger
from de.steps import fmt_step, Step, StepError, steps as _steps

click_log.basic_config(logger)


CLIHandler = Callable[..., Any]
AsyncCLIHandler = Callable[..., Awaitable[Any]]


def capture(fn: CLIHandler) -> CLIHandler:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except StepError as exc:
            logger.error(f"Step {fmt_step(exc.step)} failed!")
            logger.debug(exc.env)
            raise click.Abort()
        except Exception:
            logger.exception("FLAGRANT SYSTEM ERROR")
            raise click.Abort()

    return wrapper


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = Config.load()


def run_steps(name: str, steps: List[Step]):
    def command(config):
        _steps(steps, config)

    command.__name__ = name

    return cli.command()(
        click_log.simple_verbosity_option(logger)(capture(click.pass_obj(command)))
    )


_SHELLCHECK_CMD: Union[Path, str] = "shellcheck"
_SCRIPTS: List[Union[Path, str]] = list(SCRIPTS_DIR.glob("*.sh"))

FORMAT_STEP: Step = ["black", PROJECT_ROOT]
PYTHON_LINT_STEP: Step = ["flake8", PROJECT_ROOT]
SHELL_LINT_STEP: Step = [_SHELLCHECK_CMD] + _SCRIPTS
TYPE_CHECK_STEP: Step = ["mypy", SRC_ROOT, TESTS_DIR]
TEST_STEP: Step = ["pytest"]

format_ = run_steps("format", [FORMAT_STEP])
type_check = run_steps("type_check", [TYPE_CHECK_STEP])
lint = run_steps("lint", [PYTHON_LINT_STEP, SHELL_LINT_STEP])
test = run_steps("test", [TEST_STEP])

qa = run_steps("qa", [PYTHON_LINT_STEP, SHELL_LINT_STEP, TEST_STEP])


def async_command(fn: AsyncCLIHandler) -> CLIHandler:
    @cli.command()
    @click_log.simple_verbosity_option(logger)
    @click.pass_obj
    @functools.wraps(fn)
    def command(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(capture(fn)(*args, **kwargs))

    return command


class UpdateActionParam(click.ParamType):
    name = "update_action"

    def convert(self, value, param, ctx):
        for action in [EDIT, REPLACE]:
            if value == action or value == str(action):
                return action
        self.fail(f"Unexpected value {value!r}!", param, ctx)


UPDATE_ACTION = UpdateActionParam()


@async_command
@click.option("--yarly", is_flag=True, default=False)
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--update-action", type=UPDATE_ACTION, default=EDIT)
async def sync_emojis(config, yarly, dry_run, update_action):
    bot = DiscordBot(config)

    async with bot.connection():
        changeset = await bot.get_custom_emoji_changeset()

        click.echo(changeset.report(update_action=update_action))

        if dry_run:
            logger.info("Exiting after a dry run...")
        elif yarly or click.confirm("Do you want to apply these changes?"):
            await bot.apply_custom_emoji_changeset(
                changeset, update_action=update_action
            )
        else:
            logger.warning("Not doing!")


if __name__ == "__main__":
    cli()
