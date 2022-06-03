#! python3
# -*- coding: utf-8 -*-

"""
:author:       Vinzent Krausse (V.Krausse@digsilent.de)
:organization: DIgSILENT GmbH
:version:      002
:date:         2017-03-01
:short:        Sets read and write status of a StaExt* object.
:todo:         -
:description:  It has the same functionality like the DPL script "SetStatus.ComDpl".
:notes:
                 001 (??): base functionality to delete all external measurements
                 002 (VK): re-factoring (rename variables and add description/comments)
"""


def Execute(oStaExtMea: "powerfactory.DataObject", iIsReader: int, iIsWriter: int) -> None:
    """
    Sets read and write status of a StaExt* object.

    :param[in] oStaExtMea: The external measurement to set status.
    :param[in] iIsReader:  Reader status: 0=no; otherwise: yes.
    :param[in] iIsWriter:  Writer status: 0=no; otherwise: yes.
    """
    STATUS_WRITE = 1073741824  # write flag
    STATUS_READ = 536870912    # read flag

    # perhaps set the reader flag
    if iIsReader:
        oStaExtMea.SetStatusBit(STATUS_READ)

    # perhaps set the writer flag
    if iIsWriter:
        oStaExtMea.SetStatusBit(STATUS_WRITE)
