#! python3
# -*- coding: utf-8 -*-

"""
:author:       Vinzent Krausse (V.Krausse@digsilent.de)
:organization: DIgSILENT GmbH
:version:      002
:date:         2017-03-01
:short:        Deletes all StaExt* objects in the active grid.
:todo:         -
:description:  It has the same functionality like the DPL script "DeleteMeas.ComDpl".
:notes:
               001 (??): base functionality to delete all external measurements
               002 (VK): re-factoring (rename variables and add description/comments)
"""

import powerfactory                     # @UnresolvedImport pylint: disable=import-error


def Execute(pfApp: "powerfactory.Application"=None, iDebug: int=0) -> int:
    """
    Deletes all StaExt* objects in the active grid.

    :param[in] pfApp:       The PowerFactory application.
    :param[in] iDebug:      Debug output: 0=no output; otherwise=output.

    :return:                The number of deleted measurement objects.
    """
    # perhaps gets the PowerFactory application and the current script
    if not pfApp:
        pfApp = powerfactory.GetApplication()     # @UndefinedVariable
    script = pfApp.GetCurrentScript()

    # initialise the counter
    iCounter = 0

    # iterate over all external measurements
    aStaExtMeas = pfApp.GetCalcRelevantObjects('*.StaExt*')
    for oStaExtMea in aStaExtMeas:
        # debug output: full name of the delete measurement
        if iDebug:
            sFullName = oStaExtMea.GetFullName()
            pfApp.PrintInfo("%s - Delete measurement %s." % (script.loc_name, sFullName))

        # delete the measurement and increment counter
        oStaExtMea.Delete()
        iCounter += 1

    # debug output: summary
    if iDebug:
        pfApp.PrintInfo("%s - Deleted %d *.StaExt* objects." % (script.loc_name, iCounter))

    # return the number of deleted measurements
    return iCounter


if __name__ == "__main__":
    PF_APP = powerfactory.GetApplication()     # @UndefinedVariable
    SCRIPT = PF_APP.GetCurrentScript()
    I_DEBUG = int(SCRIPT.iDebug) if hasattr(SCRIPT, 'iDebug') else 0
    Execute(PF_APP, I_DEBUG)
    PF_APP = None
