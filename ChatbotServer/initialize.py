from crawler import covid, clinic, festival
from model.CovidModel import CovidModel
from data.Covid import Covid
from data.CovidResult import CovidResult
from data.Clinic import Clinic
from data.Festival import Festival

Covid.reset_table()
CovidResult.reset_table()
Clinic.reset_table()
Festival.reset_table()

print('Start collecting data...')
covid.get_from_csv()
clinic.get_from_csv()
festival.run_crawling()
print('Data collected.')

print('Start modeling...')
model = CovidModel(max_date='2020-11-17')
model.predict()
print('Modeling finished.')
