#! python3
# -*- coding: utf-8 -*-

"""
:author:       Vinzent Krausse (V.Krausse@digsilent.de)
:organization: DIgSILENT GmbH
:version:      004
:date:         2019-01-21
:short:        Creates breaker measurements for all switches/couplers.
:todo:         -
:description:  It has the same functionality like the DPL script "CreateTapMeas.ComDpl".
:notes:
               001 (??): base functionality to create all external measurements for all transformers.
               002 (VK): re-factoring (rename variables and add description/comments)
               003 (AS): set foreign key for input
               004 (VK): replace StaExttapmea template by generic creation
"""

import powerfactory                     # @UnresolvedImport pylint: disable=import-error

import ReplaceInvalidChars
import SetStatus


def Execute(pfApp: "powerfactory.Application"=None, sTagPrefix: str='PF.', sSeparator: str=',', iDebug: int=0) -> int:
    """
    Creates external measurements for all transformers (ElmTr*):
     * StaExtdatmea for tap output:
        - use name:  <TRANSFORMER>_Tap_Res
        - use tag:   <TAG_PREFIX>TAP_<TRANSFORMER>_RES
     * StaExttapmea (see TapMeaTemplate) for tap input:
        - use name:  <TRANSFORMER>_Tap
        - use tag:   <TAG_PREFIX>TAP_<TRANSFORMER>
     * StaExtdatmea for tap control:
        - use name:  <TRANSFORMER>_Tap_Ctrl
        - use tag:   <TAG_PREFIX>TAP_<TRANSFORMER>_CTRL
     * StaExtdatmea for setting automatic tap changing mode:
        - use name:  <TRANSFORMER>_Tap_Mode
        - use tag:   <TAG_PREFIX>TAP_<TRANSFORMER>_MODE

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

    # add external measurements (StaExttapmea+StaExtdatmea) to all hv cubicles of transformers (ElmTr*)
    aTransformers = pfApp.GetCalcRelevantObjects('*.ElmTr*')
    for oTransformer in aTransformers:
        # get cubicle
        oCubicle = oTransformer.bushv    # cubicle on hv side
        if not oCubicle:
            continue

        # get nearest busbar
        oTerminal = oCubicle.GetParent()
        iRes = getattr(oTerminal, 'iUsage') if hasattr(oTerminal, 'iUsage') else None
        if iRes > 0:
            aConnectedBusbars, aConnectableBusbars = oCubicle.GetNearestBusbars(0)
            oTerminal = aConnectedBusbars[0] or aConnectableBusbars[0]

        # prepare transformer name (as base for the tag id)
        sTransformer = oTransformer.loc_name
        oStation = getattr(oTransformer, 'cpSite') if hasattr(oTransformer, 'cpSite') else None
        if not oStation:
            oStation = getattr(oTransformer, 'cpSubstat') if hasattr(oTransformer, 'cpSubstat') else None
        if oStation:
            sStation = oStation.loc_name
        else:
            sStation = oTerminal.loc_name

        sClassName = oTransformer.GetClassName()
        sClassName = sClassName[3:]
        sBaseName = '%s_%s' % (sClassName, sTransformer)
        sBaseTag = '%s%s%s%s_TAP' % (sTagPrefix, sStation, sSeparator, sBaseName)
        sBaseTag = ReplaceInvalidChars.Execute(sBaseTag)

        # create measurement (StaExttapmea) for tap input
        oStaExtMea = oCubicle.CreateObject('StaExttapmea', sStation, '_', sBaseName)
        if iDebug:
            pfApp.PrintInfo('%s - Create measurement %s in cubicle %s for transformer %o.'
                            % (script.loc_name, oStaExtMea, oCubicle, oTransformer))

        oTransformerType = oTransformer.typ_id
        if not oTransformerType:
            pfApp.PrintWarn('%s - The transformer %o has no type, so the measurement %o has no measurement table.'
                            % (script.loc_name, oTransformer, oStaExtMea))
        else:
            iTapMin = getattr(oTransformerType, 'ntpmn') if hasattr(oTransformerType, 'ntpmn') else None
            iTapMax = getattr(oTransformerType, 'ntpmx') if hasattr(oTransformerType, 'ntpmx') else None
            if iTapMin and iTapMax:
                taps = list(range(iTapMin, iTapMax + 1))  # list(range(iTapMax, iTapMin - 1, -1))
                oStaExtMea.Tap = taps
                oStaExtMea.Exttap = taps
            # change measurement value
            if hasattr(oTransformerType, 'nntap0'):
                iTapPos = getattr(oTransformerType, 'nntap0')
                setattr(oStaExtMea, 'Tapmea', iTapPos)  # default value

        SetStatus.Execute(oStaExtMea, 1, 0)  # set status to read (OPC -> PF)
        oStaExtMea.pObject = oTransformer
        oStaExtMea.variabName = 'nntap'

        sTagId = sBaseTag
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

        # create measurement (StaExtdatmea) for tap output
        oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'Tap_', sStation, '_', sBaseName, '_Res')
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for transformer %s."
                            % (script.loc_name, oStaExtMea, oCubicle, oTransformer))

        SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
        oStaExtMea.pCalObj = oTransformer
        oStaExtMea.varCal = 'nntap'
        oStaExtMea.pCalObjSim = oTransformer
        oStaExtMea.varCalSim = 'nntap'
        oStaExtMea.i_dat = 1    # set type to integer

        sTagId = ('%s_RES' % (sBaseTag))
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

        # create measurement (StaExtdatmea) for tap control
        oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'Tap_', sStation, '_', sBaseName, '_Ctrl')
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for transformer %s."
                            % (script.loc_name, oStaExtMea, oCubicle, oTransformer))

        SetStatus.Execute(oStaExtMea, 1, 0)    # set status to read (OPC -> PF)
        oStaExtMea.pObject = oTransformer
        oStaExtMea.variabName = 'nntap'
        oStaExtMea.pCtrl = oTransformer         # work-around for not using a tap controller
        oStaExtMea.varName = 'nntap_int'
        oStaExtMea.pCalObj = oTransformer
        oStaExtMea.varCal = 'nntap'
        oStaExtMea.pCalObjSim = oTransformer
        oStaExtMea.varCalSim = 'nntap'
        oStaExtMea.i_mode = 1    # set mode to incremental
        oStaExtMea.i_dat = 1    # set type to integer

        sTagId = '%s_CTRL' % (sBaseTag)
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

        # create measurement (StaExtdatmea) for setting automatic tap changing mode
        oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'Tap_', sStation, '_', sBaseName, '_Mode')
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for transformer %s."
                            % (script.loc_name, oStaExtMea, oCubicle, oTransformer))

        SetStatus.Execute(oStaExtMea, 1, 0)  # set status to read (OPC -> PF)
        oStaExtMea.pObject = oTransformer
        oStaExtMea.variabName = 'ntrcn'
        oStaExtMea.i_dat = 1  # set type to integer

        sTagId = '%s_MODE' % (sBaseTag)
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

    # debug output: summary
    if iDebug:
        pfApp.PrintInfo("%s - Create %d *.{StaExtbrkmea,StaExtdatmea} objects." % (script.loc_name, iCounter))

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
