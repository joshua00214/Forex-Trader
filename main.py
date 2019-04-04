#


import numpy as np
from System.Drawing import Color
class BasicTemplateAldgorithm(QCAlgorithm):
    
    def Initialize(self):
      
        self.SetCash(100000)
        self.values = [];
        self.pip_offset = .0002
        self.orderId = -1
        self.time_of_trade = 0
        self.hold_length = 10 #10 minutes
        self.cash_before_trade = 100000
        self.stopLoss = .0003 #will be using 2:1 ratio for profit:loss
        
        self.rising = []
      
        self.SetStartDate(2017,1,1)
        self.SetEndDate(2017,1,2)
        
       
        self.SetBrokerageModel(BrokerageName.OandaBrokerage)
        
        self.eurusd = self.AddForex("EURUSD", Resolution.Minute).Symbol
        
        
        stockPlot = Chart('Trade Plot')
        stockPlot.AddSeries(Series('Price', SeriesType.Line, '$', Color.Green))
        stockPlot.AddSeries(Series('Long', SeriesType.Line, '$', Color.Blue))
        stockPlot.AddSeries(Series('Short', SeriesType.Line, '$', Color.Red))
        self.AddChart(stockPlot)
        
        
        
        
        
        
    def stops(self, slice, bar):
        amt = (self.Portfolio["EURUSD"].Quantity)
        OldOrder = self.orderId
        #going long
        
        if self.Portfolio["EURUSD"].Quantity > 0:
            #take profit
            if float(bar) > float((float(OldOrder.AverageFillPrice) + float((float(2) * float(self.stopLoss))))):
                self.MarketOrder("EURUSD", (-1)*amt)
                OldOrder.Cancel
                self.Log("taking profit at " + str(bar))
            #stop loss
            if bar < float((float(OldOrder.AverageFillPrice) - float(self.stopLoss))):
                self.MarketOrder("EURUSD", (-1)*amt)
                OldOrder.Cancel
                self.Log("taking loss at " + str(bar))
                
                
        #going short
        if self.Portfolio["EURUSD"].Quantity < 0:
            #take profit
            if bar < float((float(OldOrder.AverageFillPrice) - float((float(2) * float(self.stopLoss))))):
                self.MarketOrder("EURUSD", (-1)*amt)
                OldOrder.Cancel
                self.Log("taking profit at " + str(bar))
            # stop loss
            if bar > float((float(OldOrder.AverageFillPrice) + float(self.stopLoss))):
                self.MarketOrder("EURUSD", (-1)*amt)
                OldOrder.Cancel
                self.Log("taking loss at " + str(bar))
        
        
        
        
        
        
        
    def time_stop(self, slice, bar):
        #Only hold for delta time duration
        #self.Log( str( self.Time))
        string_hours = str(self.Time)[10:13]
        string_minutes = str(self.Time)[14:16]
        int_hours = int(string_hours) * 60
        int_minutes = int(string_minutes)
        time_in_minutes = int_hours + int_minutes
        #self.Log( str(time_in_minutes) + " " + str(int_hours) + " " + str(int_minutes))
            
            
            
        #self.Log("adding value: " + str(bar))
            
        if (self.Portfolio["EURUSD"].Quantity > 0 or self.Portfolio["EURUSD"].Quantity < 0) and (time_in_minutes > (self.time_of_trade + self.hold_length)):
            self.Log("Held for 10 minutes/ closing position")
            amt = (self.Portfolio["EURUSD"].Quantity)
            self.orderId = self.MarketOrder("EURUSD", (-1)*amt)
            priceClosing = amt * bar
            self.Log("cash delta: " + str(self.Portfolio.Cash - self.cash_before_trade))
            self.Log("current holdings: " + str(self.Portfolio["EURUSD"].Quantity))
      
        return time_in_minutes
                
                
                
                
                
                
                
                
                
                
    def OnData(self, slice):
        openOrder = None #self.Transactions.GetOrderById(self.orderId.Orderid)
        if openOrder is not None: #error code for invalid orderId
            if openOrder.Quantity != openOrder.QuantityFilled:
                openOrder.cancel
                self.orderId = -1
                 
                
            
        else:
            #inserting next val
            bar = slice["EURUSD"].Close
            self.values.insert(0,bar)
            #stop loss and take profit
            self.stops(slice, bar)
            #stop holding pos after delta time
            time_in_minutes = self.time_stop(slice, bar)
            
            # TODO plots
            self.Plot('Trade Plot', 'Price', bar)
            
            
            #showing increase/decrease
            if bar > self.values[0]:
                self.rising.insert(0, True)
            else:
                self.rising.insert(0, False)
            if len(self.rising) > 2:
                self.rising.pop()
            rising = True
            for value in self.rising:
                if value == False:
                    rising = False
                    break
            falling = True
            for va in self.rising:
                if va == True:
                    falling = False
                    break
                
                
                
            #creating average
            if (len(self.values) > 10):
                self.values.pop()
            if len(self.values) == 10:
                sum = 0.0
                for v in self.values:
                    sum += float(v)
                average = float(sum) / float(10)
                #self.Log("Average is: " + str(average))
            
                
                if bar > (average + self.pip_offset) and self.Portfolio["EURUSD"].Quantity == 0:#and rising
                    self.Log("going long with" + str(self.Portfolio.Cash/10) + " at: " + str(bar))
                    self.cash_before_trade = self.Portfolio.Cash
                    self.orderId = self.MarketOrder("EURUSD", self.Portfolio.Cash/10)
                    self.time_of_trade = time_in_minutes
                    self.Plot('Trade Plot', 'Long', bar)
                    
                    
                elif bar < (float(average) - self.pip_offset) and self.Portfolio["EURUSD"].Quantity == 0: #and falling
                    self.Log("going short with" + str(self.Portfolio.Cash/10) + " at: " + str(bar))
                    self.cash_before_trade = self.Portfolio.Cash
                    self.orderId = self.MarketOrder("EURUSD", (-1)*(self.Portfolio.Cash/10))
                    self.time_of_trade = time_in_minutes
                    self.Plot('Trade Plot', 'Price', bar)