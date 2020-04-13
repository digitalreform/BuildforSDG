import math
import json

class Estimate():
  '''
  Class defining estimates. 
  The class can be used for normal impact or severe impact, using the argument "estimateType" as "I"
  for normal or "S" for severe.
  All parameters needed for caculations is passed during creation
  "period" needs to be passed as days only
  '''
  
  def __init__(self, estimateType, reportedCases, period, hospitalBeds, population, dailyIncome):
    
    #Normal or Severe Impact Estimation
    if estimateType == 'I':
      self.currentlyInfected = reportedCases * 10
    elif estimateType == 'S':
      self.currentlyInfected = reportedCases * 50
    
    #Determine factor and calculate infectionsByRequestedTime
    factor = math.trunc(period / 3)
    self.infectionsByRequestedTime = self.currentlyInfected * (2 ** factor)
    
    #Severe cases are estimated at 15% of Infections
    self.severeCasesByRequestedTime = math.trunc(self.infectionsByRequestedTime * 0.15)

    #Hospitals beds are determined to be 35%(Available for CoVID19 Cases) of 35%(Available of hospital operates at 65%
    # of beds occupied) of 90% (If all hospitals operate at 90% capacity) of the Total Beds Available
    self.hospitalBedsByRequestedTime = math.trunc(self.severeCasesByRequestedTime - (hospitalBeds * 0.9 * 0.35 * 0.35))

    #ICU cases are estimated at 5% of infected cases
    self.casesForICUByRequestedTime = math.trunc(self.infectionsByRequestedTime * 0.05)
    
    #Respirator cases are estimated at 2% of infected cases
    self.casesForVentilatorsByRequestedTime = math.trunc(self.severeCasesByRequestedTime * 0.02)
    
    #Income Lost is estimated as infections * population earning income * Income per day and given per day
    self.dollarsInFlight = math.trunc((self.infectionsByRequestedTime * population * dailyIncome) / period)

  
  def __repr__(self):
    #To return data in JSON String format

    return '{' + f'"currentlyInfected" : {self.currentlyInfected},\
"infectionsByRequestedTime" : {self.infectionsByRequestedTime},\
"severeCasesByRequestedTime" : {self.severeCasesByRequestedTime},\
"hospitalBedsByRequestedTime" : {self.hospitalBedsByRequestedTime},\
"casesForICUByRequestedTime" : {self.casesForICUByRequestedTime},\
"casesForVentilatorsByRequestedTime" : {self.casesForVentilatorsByRequestedTime},\
"dollarsInFlight" : {self.dollarsInFlight}' + '}'


def estimator(data):
  
  #Convert JSON to Python
 
  #Convert time to days
  if data.get("periodType") == "days":
    dayperiod = data.get("timeToElapse")
  elif data.get("periodType") == "weeks":
    dayperiod = math.trunc(data.get("timeToElapse") * 7)
  elif data.get("periodType") == "months":
    dayperiod = math.trunc(data.get("timeToElapse") * 30)

  #Calculate Income Earning Size of Population
  earningPopulation = math.trunc(data.get("population") * data.get("region").get("avgDailyIncomePopulation"))

  #Create Impact Object
  impact = Estimate(estimateType="I", 
  reportedCases=data.get("reportedCases"), 
  period=dayperiod, 
  hospitalBeds=data.get("totalHospitalBeds"), 
  population=earningPopulation, 
  dailyIncome=data.get("region").get("avgDailyIncomeInUSD"))

  #Create Severe Impact Object
  severeImpact = Estimate(estimateType="S", 
  reportedCases=data.get("reportedCases"), 
  period=dayperiod, 
  hospitalBeds=data.get("totalHospitalBeds"), 
  population=earningPopulation, 
  dailyIncome=data.get("region").get("avgDailyIncomeInUSD"))

  return '{' + f'"data" : {data}, "impact" : {impact}, "severeImpact" : {severeImpact}' + '}'
