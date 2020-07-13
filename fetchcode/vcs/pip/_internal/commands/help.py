# The following comment should be removed at some point in the future.
# mypy: disallow-untyped-defs=False

from __future__ import absolute_import

from fetchcode.vcs.pip._internal.cli.base_command import Command
from fetchcode.vcs.pip._internal.cli.status_codes import SUCCESS
from fetchcode.vcs.pip._internal.exceptions import CommandError


class HelpCommand(Command):
    """Show help for commands"""

    usage = """
      %prog <command>"""
    ignore_require_venv = True

    def run(self, options, args):
        from fetchcode.vcs.pip._internal.commands import (
            commands_dict, create_command, get_similar_commands,
        )

        try:
            # 'pip help' with no args is handled by pip.__init__.parseopt()
            cmd_name = args[0]  # the command we need help for
        except IndexError:
            return SUCCESS

        if cmd_name not in commands_dict:
            guess = get_similar_commands(cmd_name)

            msg = ['unknown command "{}"'.format(cmd_name)]
            if guess:
                msg.append('maybe you meant "{}"'.format(guess))

            raise CommandError(' - '.join(msg))

        command = create_command(cmd_name)
        command.parser.print_help()

        return SUCCESS
