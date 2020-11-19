from crawler import covid, clinic, festival
from model.CovidModel import CovidModel
from data.CovidResult import CovidResult

CovidResult.reset_table()

print('Start collecting data...')
covid.get_from_web()
festival.run_crawling()
print('Data collected.')

print('Start modeling...')
model = CovidModel()
model.predict()
print('Modeling finished.')
