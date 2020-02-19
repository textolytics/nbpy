import sys
import time
import thread
import quickfix as fix
import quickfix44 as fix44
from datetime import datetime

class Application (fix.Application):
    orderID = 0
    execID = 0
    tradeID = 0
    global settings

    def onCreate (self, sessionID):
        self.sessionID = sessionID
        print ("Application created - session: " + sessionID.toString ())

    def onLogon (self, sessionID):
        print ("Logon")

    def onLogout (self, sessionID):
        print ("Logout")

    def onMessage (self, message, sessionID):
        print (message)

    def toAdmin (self, message, sessionID):
        msgType = fix.MsgType ()
        message.getHeader ().getField (msgType)
        if (msgType.getValue () == fix.MsgType_Logon):
            message.setField (fix.Password (settings.get (self.sessionID).getString ("Password")))
            message.setField (fix.ResetSeqNumFlag (True))

    def fromAdmin (self, message, sessionID):
        pass

    def toApp (self, message, sessionID):
        pass

    def fromApp (self, message, sessionID):
        pass

    def genOrderID (self):
        self.orderID += 1
        return repr (self.orderID)

    def genTradeReportID (self):
        self.tradeID += 1
        return repr (self.tradeID)

    def genExecID (self):
        self.execID += 1
        return repr (self.execID)

    def run (self):
        time.sleep (5)
        self.queryEnterOrder ()
        time.sleep (5)

    def queryEnterOrder (self):
        print ("\nTradeCaptureReport (AE)\n")
        trade = fix.Message ()
        trade.getHeader ().setField (fix.BeginString (fix.BeginString_FIX44))
        trade.getHeader ().setField (fix.MsgType (fix.MsgType_TradeCaptureReport))

        trade.setField (fix.TradeReportTransType (fix.TradeReportTransType_NEW))       # 487
        trade.setField (fix.TradeReportID (self.genTradeReportID ()))                  # 571
        trade.setField (fix.TrdSubType (4))                        # 829
        trade.setField (fix.SecondaryTrdType (2))                  # 855
        trade.setField (fix.Symbol ("MYSYMBOL"))                   # 55
        trade.setField (fix.LastQty (22))                          # 32
        trade.setField (fix.LastPx (21.12))                        # 31
        trade.setField (fix.TradeDate ((datetime.now ().strftime ("%Y%m%d"))))                      # 75
        trade.setField (fix.TransactTime ((datetime.now ().strftime ("%Y%m%d-%H:%M:%S.%f"))[:-3]))  # 60
        trade.setField (fix.PreviouslyReported (False))            # 570

        group = fix44.TradeCaptureReport ().NoSides ()

        group.setField (fix.Side (fix.Side_SELL))                  # 54
        group.setField (fix.OrderID (self.genOrderID ()))          # 37
        group.setField (fix.NoPartyIDs (1))                        # 453
        group.setField (fix.PartyIDSource (fix.PartyIDSource_PROPRIETARY_CUSTOM_CODE)) # 447
        group.setField (fix.PartyID ("CLEARING"))                  # 448
        group.setField (fix.PartyRole (fix.PartyRole_CLEARING_ACCOUNT))                # 452
        trade.addGroup (group)

        group.setField (fix.Side (fix.Side_BUY))                   # 54
        group.setField (fix.OrderID (self.genOrderID ()))          # 37
        group.setField (fix.NoPartyIDs (1))                        # 453
        group.setField (fix.PartyIDSource (fix.PartyIDSource_PROPRIETARY_CUSTOM_CODE)) # 447
        group.setField (fix.PartyID ("CLEARING"))                  # 448
        group.setField (fix.PartyRole (fix.PartyRole_CLEARING_ACCOUNT))                # 452
        trade.addGroup (group)

        fix.Session.sendToTarget (trade, self.sessionID)