#! python3
# -*- coding: utf-8 -*-

"""
:author:       Vinzent Krausse (V.Krausse@digsilent.de)
:organization: DIgSILENT GmbH
:version:      002
:date:         2017-03-01
:short:        Changes invalid chars so that sText is a regular OPC tag id.
:todo:         -
:description:  It has the same functionality like the DPL script "ReplaceInvalidChars.ComDpl".
:notes:
                 001 (??): base functionality to replace invalid characters in OPC tag names
                 002 (VK): re-factoring (rename variables and add description/comments)
"""


def Execute(sText: str) -> str:
    """
    Changes invalid chars so that sText is a regular OPC tag id:
      * replace all spaces by '_'
      * replace all '/' by '_'
      * convert sText to upper case

    :param[in] sText: The text to replace.

    :return:          A regular OPC tag id for the given text.
    """
    # replace all spaces by '_'
    sText = sText.replace(' ', '_')

    # replace all '/' by '_'
    sText = sText.replace('/', '_')

    # to upper case
    sText = sText.upper()

    # return text
    return sText
