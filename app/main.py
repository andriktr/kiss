import logging
import sys
import click

from app import __version__, __release__, __author__
from app.commands.show_images import show_images
from app.commands.scan_images import scan_images


# ASCII art logo and description
APP_DESCRIPTION = f"""
*****************************************************************************************
     _  _____ ____ _____                                                                                          
    | |/ /_ _/ ___/ ___|                                                               
    | ' / | |\___ \\___ \\                                                             
    | . \\ | | ___) |__) |                                                             
    |_|\\_\\___|____/____/                                                             
                                                                                                                                       
    Give a security * to your cluster !!!                                              
    Version: {__version__}                                                             
    Release: {__release__}                                                             
    Author:  {__author__}                                                               
    Description: A CLI tool to get images in a namespace and scan for vulnerabilities.                       
*****************************************************************************************
"""

# Custom Click Command to include ASCII art in help
class CustomGroup(click.Group):
    def format_help(self, ctx, formatter):
        # Print the ASCII art at the top of the help message
        formatter.write(APP_DESCRIPTION)
        formatter.write("\n")
        # Call the original help formatter
        super().format_help(ctx, formatter)

@click.group(
    cls=CustomGroup,  # Use the custom group class
    context_settings=dict(help_option_names=["-h", "--help"])
)
def main():
    pass

# Add the subcommands to the main group
main.add_command(show_images)
main.add_command(scan_images)

if __name__ == "__main__":
    main()