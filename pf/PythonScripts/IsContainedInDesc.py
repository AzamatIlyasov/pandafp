#! python3
# -*- coding: utf-8 -*-

"""
:author:       Vinzent Krausse (V.Krausse@digsilent.de)
:organization: DIgSILENT GmbH
:version:      002
:date:         2017-03-01
:short:        Searches for a string in description of an element.
:todo:         -
:description:  It has the same functionality like the DPL script "SetStatus.ComDpl".
:notes:
                 001 (??): base functionality to check the existence of a substring in the description
                 002 (VK): re-factoring (rename variables and add description/comments)
"""

from typing import Tuple


def Execute(oObject: object, sSubstring: str) -> Tuple[int, int, int, int]:
    """
    Searches for a string in description of an element.

    The description should have a format like <SUBSTRING>=<MODE> with <MODE> := i|o|io|oi.
    Optionally the description line contains also the orientation: Orientation=<ORIENTATION> with
    <ORIENTATION> := g|l

    :param[in] oStaExtMea: The external measurement to set status.
    :param[in] iIsReader:  Reader status: 0=no; otherwise: yes.
    :param[in] iIsWriter:  Writer status: 0=no; otherwise: yes.

    :return:               A tuple of flags: (iFound, iModeIn, iModeOut, iOrientation).
    """
    # initialisation
    iFound = 0
    iModeIn = 0
    iModeOut = 0
    iOrientation = 0

    # iterate over all descriptions
    iPos = -1
    for sDesc in oObject.desc:
        # search substring in description line
        iPos = sDesc.find(sSubstring)
        if iPos >= 0:
            iFound = 1    # substring found

            # get 1st character behind found substring to get mode
            iPos += len(sSubstring)
            iPos += 1
            sMode = sDesc[iPos]
            if sMode == 'i':
                iModeIn = 1    # input mode
            if sMode == 'o':
                iModeOut = 1    # output mode

            # get 2nd character behind found substring to get mode
            iPos += 1
            sMode = sDesc[iPos] if iPos < len(sDesc) else ''
            if sMode == 'i':
                iModeIn = 1    # input mode
            if sMode == 'o':
                iModeOut = 1    # output mode
        else:
            # get orientation
            iPos = sDesc.find('Orientation')
            if iPos >= 0:
                iPos += len('Orientation')
                iPos += 1
                sMode = sDesc[iPos]
                if sMode == 'g':
                    iOrientation = 1    # generator orientation

    # return
    return (iFound, iModeIn, iModeOut, iOrientation)
