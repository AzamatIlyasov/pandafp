#! python3
# -*- coding: utf-8 -*-

"""
:author:       Vinzent Krausse (V.Krausse@digsilent.de)
:organization: DIgSILENT GmbH
:version:      003
:date:         2019-01-22
:short:        Creates external measurements for generators and loads.
:todo:         -
:description:  It has the same functionality like the DPL script "CreateGenLoadMeas.ComDpl".
:notes:
               001 (??): base functionality to create all external measurements for generators and loads
               002 (VK): re-factoring (rename variables and add description/comments)
               003 (AS): set foreign key for input, change name rules
"""

import powerfactory                     # @UnresolvedImport pylint: disable=import-error

import ReplaceInvalidChars
import SetStatus


# pylint: disable=too-many-branches, too-many-locals, too-many-statements
def Execute(pfApp: "powerfactory.Application"=None, sTagPrefix: str='PF.', sSeparator: str=',', iDebug: int=0) -> int:
    """
    Creates external measurements for all generators (ElmSym, ElmGenstat):
     * base name <BASE_NAME> = Gen_<VOLTAGE>kV_<GENERATOR>
     * base tag <BASE_TAG> = <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>
     * StaExtdatmea for generator's P output:
        - use name:  P_<STATION>_<BASE_NAME>_Res
        - use tag:   <BASE_TAG>_P_RES
     * StaExtdatmea for generator's Q output:
        - use name:  Q_<STATION>_<BASE_NAME>_Res
        - use tag:   <BASE_TAG>_Q_RES
     * StaExtdatmea for generator's V output:
        - use name:  V_<STATION>_<BASE_NAME>_Res
        - use tag:   <BASE_TAG>_V_RES
     * StaExtdatmea for generator's P control (only if no P control at slack machine):
        - use name:  P_<STATION>_<BASE_NAME>_Ctrl
        - use tag:   <BASE_TAG>_P_CTRL
     * StaExtdatmea for generator's V control:
        - use name:  V_<STATION>_<BASE_NAME>_Ctrl
        - use tag:   <BASE_TAG>_V_CTRL

    Creates external measurements for all loads (ElmLoad):
     * base name <BASE_NAME> = Load_<VOLTAGE>kV_<LOAD>
     * base tag <BASE_TAG> = <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>
     * StaExtdatmea for load's P output:
        - use name:  P_<STATION>_<BASE_NAME>_Res
        - use tag:   <BASE_TAG>_P_RES
     * StaExtdatmea for load's Q output:
        - use name:  Q_<STATION>_<BASE_NAME>_Res
        - use tag:   <BASE_TAG>_Q_RES
     * StaExtdatmea for load's V output:
        - use name:  V_<STATION>_<BASE_NAME>_Res
        - use tag:   <BASE_TAG>_V_RES

    :param[in] pfApp:       The PowerFactory application.
    :param[in] sTagPrefix:  The prefix of the generated measurement tag.
    :param[in] sSeparator:  Separator in the middle of the OPC tag.
    :param[in] iDebug:      Debug output: 0=no output; otherwise=output.

    :return:                The number of created measurement objects.
    """
    # perhaps gets the PowerFactory application and the current script
    if not pfApp:
        pfApp = powerfactory.GetApplication()     # @UndefinedVariable
    script = pfApp.GetCurrentScript()

    # initialise the counter
    iCounter = 0

    # add external measurements (StaExtdatmea) to all generators (ElmSym, ElmGenstat)
    aGenerators = pfApp.GetCalcRelevantObjects('*.ElmSym,*.ElmGenstat')
    for oGenerator in aGenerators:
        # get cubicle
        oCubicle = oGenerator.GetCubicle(0)

        # prepare generator name (as base for the tag id)
        sGenerator = oGenerator.loc_name
        oTerminal = oCubicle.GetParent()
        dVoltage = oTerminal.uknom

        # get nearest busbar
        iRes = getattr(oTerminal, 'iUsage') if hasattr(oTerminal, 'iUsage') else None
        if iRes > 0:
            aConnectedBusbars, aConnectableBusbars = oCubicle.GetNearestBusbars(0)
            oTerminal = aConnectedBusbars[0] or aConnectableBusbars[0]

        oStation = getattr(oGenerator, 'cpSite') if hasattr(oGenerator, 'cpSite') else None
        if not oStation:
            oStation = getattr(oGenerator, 'cpSubstat') if hasattr(oGenerator, 'cpSubstat') else None
        if oStation:
            sStation = oStation.loc_name
        else:
            sStation = oTerminal.loc_name

        sBaseName = 'Gen_%dkV_%s' % (int(dVoltage + 0.5), sGenerator)
        sBaseTag = '%s%s%s%s' % (sTagPrefix, sStation, sSeparator, sBaseName)
        sBaseTag = ReplaceInvalidChars.Execute(sBaseTag)

        # create measurement (StaExtdatmea) for generator's P output
        oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'P_', sStation, '_', sBaseName, '_Res')
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for generator %s."
                            % (script.loc_name, oStaExtMea, oCubicle, oGenerator))

        SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
        oStaExtMea.pCalObj = oGenerator
        oStaExtMea.varCal = 'm:P:bus1'
        oStaExtMea.pCalObjSim = oGenerator
        oStaExtMea.varCalSim = 'm:P:bus1'
        oStaExtMea.i_dat = 3    # set type to real

        sTagId = '%s_P_RES' % sBaseTag
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

        # create measurement (StaExtdatmea) for generator's Q output
        oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'Q_', sStation, '_', sBaseName, '_Res')
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for generator %s."
                            % (script.loc_name, oStaExtMea, oCubicle, oGenerator))

        SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
        oStaExtMea.pCalObj = oGenerator
        oStaExtMea.varCal = 'm:Q:bus1'
        oStaExtMea.pCalObjSim = oGenerator
        oStaExtMea.varCalSim = 'm:Q:bus1'
        oStaExtMea.i_dat = 3    # set type to real

        sTagId = '%s_Q_RES' % sBaseTag
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

        # create measurement (StaExtdatmea) for generator's V output
        oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'V_', sStation, '_', sBaseName, '_Res')
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for generator %s."
                            % (script.loc_name, oStaExtMea, oCubicle, oGenerator))

        SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
        oStaExtMea.pCalObj = oGenerator
        oStaExtMea.varCal = 'n:Ul:bus1'
        oStaExtMea.pCalObjSim = oGenerator
        oStaExtMea.varCalSim = 'n:Ul:bus1'
        oStaExtMea.i_dat = 3    # set type to real

        sTagId = '%s_V_RES' % sBaseTag
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

        # create measurement (StaExtdatmea) for generator's P control
        if oGenerator.ip_ctrl == 0:  # no P control at slack machine
            oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'P_', sStation, '_', sBaseName, '_Ctrl')
            if iDebug:
                pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for generator %s."
                                % (script.loc_name, oStaExtMea, oCubicle, oGenerator))

            SetStatus.Execute(oStaExtMea, 1, 0)    # set status to read (OPC -> PF)
            oStaExtMea.pObject = oGenerator
            oStaExtMea.variabName = 'pgini'
            oStaExtMea.pCalObj = oGenerator
            oStaExtMea.varCal = 'pgini'
            oStaExtMea.pCalObjSim = oGenerator
            oStaExtMea.varCalSim = 'pgini'
            oStaExtMea.i_mode = 1
            oStaExtMea.i_dat = 3    # set type to real

            sTagId = '%s_P_CTRL' % sBaseTag
            oStaExtMea.sTagID = sTagId
            oStaExtMea.for_name = sTagId

            iCounter += 1

        # create measurement (StaExtdatmea) for generator's V control
        oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'V_', sStation, '_', sBaseName, '_Ctrl')
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for generator %s."
                            % (script.loc_name, oStaExtMea, oCubicle, oGenerator))

        SetStatus.Execute(oStaExtMea, 1, 0)    # set status to read (OPC -> PF)
        oStaExtMea.pObject = oGenerator
        oStaExtMea.variabName = 'usetp'
        oStaExtMea.pCalObj = oGenerator
        oStaExtMea.varCal = 'usetp'
        oStaExtMea.pCalObjSim = oGenerator
        oStaExtMea.varCalSim = 'usetp'
        oStaExtMea.i_mode = 1
        oStaExtMea.Multip = 0.01
        oStaExtMea.i_dat = 3    # set type to real

        # set controller reference
        oPlant = oGenerator.c_pmod
        if oPlant:  # machine referring to plant (composite model)
            oStaExtMea.pCtrl = oPlant.pelm[2]
            oStaExtMea.varName = 'usetp'

        sTagId = '%s_V_CTRL' % sBaseTag
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

    # add external measurements (StaExtdatmea) to all loads (ElmLod)
    aLoads = pfApp.GetCalcRelevantObjects('*.ElmLod')
    for oLoad in aLoads:
        # get cubicle
        oCubicle = oLoad.GetCubicle(0)
        if not oCubicle:
            continue

        # prepare load name (as base for the tag id)
        sLoad = oLoad.loc_name
        oTerminal = oCubicle.GetParent()
        dVoltage = oTerminal.uknom

        # get nearest busbar
        iRes = getattr(oTerminal, 'iUsage') if hasattr(oTerminal, 'iUsage') else None
        if iRes > 0:
            aConnectedBusbars, aConnectableBusbars = oCubicle.GetNearestBusbars(0)
            oTerminal = aConnectedBusbars[0] or aConnectableBusbars[0]

        oStation = getattr(sLoad, 'cpSite') if hasattr(sLoad, 'cpSite') else None
        if not oStation:
            oStation = getattr(sLoad, 'cpSubstat') if hasattr(sLoad, 'cpSubstat') else None
        if oStation:
            sStation = oStation.loc_name
        else:
            sStation = oTerminal.loc_name

        sBaseName = 'Load_%dkV_%s' % (int(dVoltage + 0.5), sLoad)
        sBaseTag = '%s%s%s%s' % (sTagPrefix, sStation, sSeparator, sBaseName)
        sBaseTag = ReplaceInvalidChars.Execute(sBaseTag)

        # create measurement (StaExtdatmea) for load's P output
        oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'P_', sStation, '_', sBaseName, '_Res')
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for load %s."
                            % (script.loc_name, oStaExtMea, oCubicle, oLoad))

        SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
        oStaExtMea.pCalObj = oLoad
        oStaExtMea.varCal = 'm:P:bus1'
        oStaExtMea.pCalObjSim = oLoad
        oStaExtMea.varCalSim = 'm:P:bus1'
        oStaExtMea.i_dat = 3    # set type to real

        sTagId = '%s_P_RES' % sBaseTag
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

        # create measurement (StaExtdatmea) for load's Q output
        oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'Q_', sStation, '_', sBaseName, '_Res')
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for load %s."
                            % (script.loc_name, oStaExtMea, oCubicle, oLoad))

        SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
        oStaExtMea.pCalObj = oLoad
        oStaExtMea.varCal = 'm:Q:bus1'
        oStaExtMea.pCalObjSim = oLoad
        oStaExtMea.varCalSim = 'm:Q:bus1'
        oStaExtMea.i_dat = 3    # set type to real

        sTagId = '%s_Q_RES' % sBaseTag
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

        # create measurement (StaExtdatmea) for load's V output
        oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'V_', sStation, '_', sBaseName, '_Res')
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for load %s."
                            % (script.loc_name, oStaExtMea, oCubicle, oLoad))

        SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
        oStaExtMea.pCalObj = oLoad
        oStaExtMea.varCal = 'n:Ul:bus1'
        oStaExtMea.pCalObjSim = oLoad
        oStaExtMea.varCalSim = 'n:Ul:bus1'
        oStaExtMea.i_dat = 3    # set type to real

        sTagId = '%s_V_RES' % sBaseTag
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

    # debug output: summary
    if iDebug:
        pfApp.PrintInfo("%s - Create %d *.StaExtdatmea objects." % (script.loc_name, iCounter))

    # return the number of created measurements
    return iCounter


if __name__ == "__main__":
    PF_APP = powerfactory.GetApplication()     # @UndefinedVariable
    SCRIPT = PF_APP.GetCurrentScript()
    S_TAG_PREFIX = SCRIPT.sTagPrefix if hasattr(SCRIPT, 'sTagPrefix') else 'PF.'
    S_SEPARATOR = SCRIPT.sSeparator if hasattr(SCRIPT, 'sSeparator') else ','
    I_DEBUG = int(SCRIPT.iDebug) if hasattr(SCRIPT, 'iDebug') else 0
    Execute(PF_APP, S_TAG_PREFIX, S_SEPARATOR, I_DEBUG)
    PF_APP = None
