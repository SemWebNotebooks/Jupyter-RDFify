import argparse
import re


class StopCellExecution(Exception):
    """Special exception which can be raised to stop the execution of the cell without visible error."""

    def _render_traceback_(self):
        pass


class MagicParser(argparse.ArgumentParser):

    def exit(self, status=0, message=None):
        if status:
            print("Parser exited with error: {}".format(message))
        raise StopCellExecution

    def error(self, message):
        print("Error: {}".format(message))
        self.exit()


def literal_to_string(literal, lang=None, datatype=None):
    lit = f"\"{literal}\""
    if lang is not None:
        lit += f"@{lang}"
    if datatype is not None:
        lit += f"^^{datatype}"
    return lit


def strip_comments(text):
    """Special comment strip function for formats which do not support comments (e.g. json)"""
    return re.sub("###.*$", '', text, 0, re.M)
