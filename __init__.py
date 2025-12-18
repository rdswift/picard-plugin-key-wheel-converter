# -*- coding: utf-8 -*-
"""Key Wheel Converter Plugin
"""
#
# Copyright (C) 2022-2025 Bob Swift (rdswift)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

# pylint: disable=C0413     (wrong-import-position)
# pylint: disable=W0613     (unused-argument)


import re

from picard.plugin3.api import PluginApi


class KeyMap:
    """
        Class to hold the mapping dictionary.  The dictionary is
        stored as a class variable so that it is only generated once.
    """
    # pylint: disable=too-few-public-methods

    # Circle of Fifths reference:
    # https://www.circleoffifths.com

    # Key Wheel references:
    # https://i.imgur.com/p9Kdevi.jpg
    # http://www.quanta.com.br/wp-content/uploads/2013/07/traktor-key-wheel_alta.jpg

    # Mapping dictionary with 'camelot', 'standard with text' and 'traktor' keys.
    keys = {}

    # Alternate mapping for standard keys
    s_alt = {
        'G-Flat Major': 'F-Sharp Major',
        'D-Sharp Minor': 'E-Flat Minor',
    }

    # Alternate mapping for traktor keys
    t_alt = {
        'G#': 'Ab',
        'A#': 'Bb',
        'C#': 'Db',
        'D#': 'Eb',
        'G#m': 'Abm',
        'A#m': 'Bbm',
        'C#m': 'Dbm',
        'D#m': 'Ebm',
        'F#m': 'Gbm',
    }

    @classmethod
    def initialize(cls):
        """Initialize the mapping dictionary.
        """

        # List of tuples of:
        #   'camelot key',
        #   'open key',
        #   'standard key /w symbols',
        #   'standard key /w text'
        #   'traktor key'
        _keys = [
            ('1A', '6m', 'A♭ Minor', 'A-Flat Minor', 'Abm'),
            ('1B', '6d', 'B Major', 'B Major', 'B'),
            ('2A', '7m', 'E♭ Minor', 'E-Flat Minor', 'Ebm'),
            ('2B', '7d', 'F# Major', 'F-Sharp Major', 'F#'),
            ('3A', '8m', 'B♭ Minor', 'B-Flat Minor', 'Bbm'),
            ('3B', '8d', 'D♭ Major', 'D-Flat Major', 'Db'),
            ('4A', '9m', 'F Minor', 'F Minor', 'Fm'),
            ('4B', '9d', 'A♭ Major', 'A-Flat Major', 'Ab'),
            ('5A', '10m', 'C Minor', 'C Minor', 'Cm'),
            ('5B', '10d', 'E♭ Major', 'E-Flat Major', 'Eb'),
            ('6A', '11m', 'G Minor', 'G Minor', 'Gm'),
            ('6B', '11d', 'B♭ Major', 'B-Flat Major', 'Bb'),
            ('7A', '12m', 'D Minor', 'D Minor', 'Dm'),
            ('7B', '12d', 'F Major', 'F Major', 'F'),
            ('8A', '1m', 'A Minor', 'A Minor', 'Am'),
            ('8B', '1d', 'C Major', 'C Major', 'C'),
            ('9A', '2m', 'E Minor', 'E Minor', 'Em'),
            ('9B', '2d', 'G Major', 'G Major', 'G'),
            ('10A', '3m', 'B Minor', 'B Minor', 'Bm'),
            ('10B', '3d', 'D Major', 'D Major', 'D'),
            ('11A', '4m', 'G♭ Minor', 'G-Flat Minor', 'Gbm'),
            ('11B', '4d', 'A Major', 'A Major', 'A'),
            ('12A', '5m', 'D♭ Minor', 'D-Flat Minor', 'Dbm'),
            ('12B', '5d', 'E Major', 'E Major', 'E'),
        ]

        # Build mapping dictionary with 'camelot', 'standard with text' and 'traktor' keys.
        cls.keys = {}
        for item in _keys:
            for i in [0, 3, 4]:
                cls.keys[item[i]] = {
                    'camelot': item[0],
                    'open': item[1],
                    'standard_s': item[2],
                    'standard_t': item[3],
                    'traktor': item[4],
                }


class KeyWheelConverter:
    """Key Wheel Converter Plugin Class
    """
    api: PluginApi = None

    @classmethod
    def set_api(cls, api: PluginApi):
        cls.api = api

    @classmethod
    def converter(cls, text, out_type):
        """Function that performs the actual key lookup.

        Args:
            text (str): Key provided by the user.
            out_type (str): Output format to use for the return value

        Returns:
            str: Value mapped to the key for the specified output type
        """
        # pylint: disable=consider-using-f-string
        match_text = cls._parse_input(text)
        if match_text not in KeyMap.keys:
            cls.api.logger.debug("Unable to match key: '%s'", text,)
            return ''
        return KeyMap.keys[match_text][out_type]

    @classmethod
    def _parse_input(cls, text):
        """Helper function to parse the input argument to try to match
        one of the supported formats used for the mapping keys.

        Args:
            text (str): Input argument provided by the user

        Returns:
            str: Argument converted to supported key format (if possible)
        """
        # pylint: disable=too-many-return-statements

        text = text.strip()
        if not text:
            return ''

        if re.match("[0-9]{1,2}[ABab]$", text):
            # Matches camelot key.  Fix capitalization for lookup.
            return text.upper()

        if re.match("[0-9]{1,2}[dmDM]$", text):
            # Matches open key format.  Convert to camelot key for lookup.
            temp = int(text[0:-1])
            if 0 < temp < 13:
                _num = ((temp + 6) % 12) + 1
                _char = text[-1:].lower().replace('m', 'A').replace('d', 'B')
                return "{0}{1}".format(_num, _char,)

        # if re.match("[a-gA-G][#bB♭]?[mM]?$", text):
        if re.match("[a-gA-G][#Bb]?[mM]?$", text):
            # Matches Traktor key format.  Fix capitalization for lookup.
            temp = text[0:1].upper() + text[1:].replace('♭', 'b').lower()
            # Handle cases where there are multiple entries for the item
            if temp in KeyMap.t_alt:
                return KeyMap.t_alt[temp]
            return temp

        # Parse as standard key
        # Add missing hyphens before 'Flat' and 'Sharp'
        text = text.lower().replace(' s', '-s').replace(' f', '-f')
        # Convert symbols to text for lookup.
        parts = text.replace('♭', '-Flat').replace('#', '-Sharp').split()
        for (i, part) in enumerate(parts):
            parts[i] = part[0:1].upper() + part[1:]
        temp = ' '.join(parts).replace('-s', '-S').replace('-f', '-F')
        # Handle cases where there are multiple entries for the item
        if temp in KeyMap.s_alt:
            return KeyMap.s_alt[temp]
        return temp


def func_key2camelot(parser, text):
    """Any key to camelot format converter.

    Args:
        parser (object): Picard parser object
        text (str): Key to convert

    Returns:
        str: Converted key value
    """
    return KeyWheelConverter.converter(text, 'camelot')


def func_key2openkey(parser, text):
    """Any key to open key format converter.

    Args:
        parser (object): Picard parser object
        text (str): Key to convert

    Returns:
        str: Converted key value
    """
    return KeyWheelConverter.converter(text, 'open')


def func_key2standard(parser, text, use_symbol=''):
    """Any key to standard key format converter.

    Args:
        parser (object): Picard parser object
        text (str): Key to convert
        use_symbol (str, optional): Use '♭' and '#' symbols. Defaults to False.

    Returns:
        str: Converted key value
    """
    if use_symbol:
        return KeyWheelConverter.converter(text, 'standard_s')
    return KeyWheelConverter.converter(text, 'standard_t')


def func_key2traktor(parser, text):
    """Any key to traktor key format converter.

    Args:
        parser (object): Picard parser object
        text (str): Key to convert

    Returns:
        str: Converted key value
    """
    return KeyWheelConverter.converter(text, 'traktor')


def enable(api: PluginApi):
    """Called when plugin is enabled."""
    KeyMap.initialize()
    KeyWheelConverter.set_api(api)

    standard_note = api.tr(
        'help.standard_note',
        (
            "The `key` argument can be entered in any of the supported formats, such as "
            "'2B' (camelot), '6d' (open key), 'A♭ Minor' (standard with symbols), "
            "'A-Flat Minor' (standard with text) or 'C#' (traktor). If the `key` argument "
            "is not recognized as one of the standard keys in the supported formats, then "
            "an empty string will be returned."
        )
    )

    # Register the new functions
    api.register_script_function(
        func_key2camelot,
        name='key2camelot',
        documentation=api.tr(
            'help.key2camelot',
            (
                "`$key2camelot(key)`\n\n"
                "Returns the key string `key` in camelot key format."
            )
        )
        + "\n\n" + standard_note,
    )

    api.register_script_function(
        func_key2openkey,
        name='key2openkey',
        documentation=api.tr(
            'help.key2openkey',
            (
                "`$key2openkey(key)`\n\n"
                "Returns the key string `key` in open key format."
            )
        )
        + "\n\n" + standard_note,
    )

    api.register_script_function(
        func_key2standard,
        name='key2standard',
        documentation=api.tr(
            'help.key2standard',
            (
                "`$key2standard(key[,symbols])`\n\n"
                "Returns the key string `key` in standard key format. If the optional argument "
                "`symbols` is set, then the '♭' and '#' symbols will be used, rather than "
                "spelling out '-Flat' and '-Sharp'."
            )
        )
        + "\n\n" + standard_note,
    )

    api.register_script_function(
        func_key2traktor,
        name='key2traktor',
        documentation=api.tr(
            'help.key2traktor',
            (
                "`$key2traktor(key)`\n\n"
                "Returns the key string `key` in traktor key format."
            )
        )
        + "\n\n" + standard_note,
    )
