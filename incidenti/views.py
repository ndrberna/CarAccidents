from django.shortcuts import render
from django.http import HttpResponse
import csv
from django.shortcuts import render_to_response, render, redirect
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from time import sleep
from pandas import *  
import os
from collections import Counter
import math
import pandas as pd

import time
# Create your views here.

def base(request):

	print("Statistiche pedoni")
	module_dir = os.path.dirname(__file__)  # get current directory
	
	file_path_pedoni = os.path.join(module_dir, 'static/data/pedoni.csv')
	pedoniData = read_csv(file_path_pedoni, encoding = 'iso-8859-1',na_values=[" "]) 
	
	file_path_dati_completi = os.path.join(module_dir, 'static/data/dati_completi.csv')
	dati_completiData = read_csv(file_path_dati_completi, encoding = 'iso-8859-1',na_values=[" "]) 

	file_path_incidenti = os.path.join(module_dir, 'static/data/incidenti11_12_2015.csv')
	incidentiData = read_csv(file_path_incidenti, encoding = 'iso-8859-1', quotechar='"',na_values=[" "]) 
	
	# Heatmap data
	matrix_settimanale = [[0 for i in range(7)] for j in range(24)]
	matrix_morti = [[0 for i in range(7)] for j in range(24)]
	matrix_illesi = [[0 for i in range(7)] for j in range(24)]
	matrix_feriti = [[0 for i in range(7)] for j in range(24)]

	#for interaction in interactions:  
	#			matrix[interaction['dt'].hour-1][interaction['dt'].weekday()] += 1

	filter_incidentiData=incidentiData[['_Illuminazione','_Visibilita','_Traffico','_CondizioneAtmosferica','_FondoStradale','_DataOraIncidente','_TipoStrada','_ParticolaritaStrade']]
	

	gravita_incidentiData=incidentiData[['_NUM_FERITI','_NUM_RISERVATA','_NUM_MORTI','_NUM_ILLESI','_DataOraIncidente']]

	#print(gravita_incidentiData.values.T.tolist())
	row_iterator = gravita_incidentiData.iterrows()
	count_morti =0
	count_feriti=0
	count_illesi=0
	count_incidenti=0
	for i, row in row_iterator:
		try:
			converted_date=datetime.strptime(row['_DataOraIncidente'],'%Y-%m-%dT%H:%M:%S')
		except:
			converted_date=datetime.strptime(row['_DataOraIncidente'],'%d/%m/%YT%H:%M:%S')


		matrix_morti[converted_date.hour][converted_date.weekday()] += int(row['_NUM_MORTI']) 
		count_morti+= int(row['_NUM_MORTI'])
		matrix_illesi[converted_date.hour][converted_date.weekday()] += int(row['_NUM_ILLESI'])
		count_illesi+= int(row['_NUM_ILLESI'])
		matrix_feriti[converted_date.hour][converted_date.weekday()] += int(row['_NUM_RISERVATA'])+int(row['_NUM_FERITI'])
		count_feriti+= int(row['_NUM_FERITI'])

		
	dataOraIncidente=filter_incidentiData['_DataOraIncidente'].tolist()
	for date in dataOraIncidente:
		try:
			converted_date=datetime.strptime(date,'%Y-%m-%dT%H:%M:%S')
			
		except:
			converted_date=datetime.strptime(date,'%d/%m/%YT%H:%M:%S')
		matrix_settimanale[converted_date.hour][converted_date.weekday()] += 1
		count_incidenti += 1

	tipo_strada= Counter(filter_incidentiData['_TipoStrada'].tolist())


	illuminazione= filter_incidentiData['_Illuminazione'].value_counts().to_dict()
	visibilita=filter_incidentiData['_Visibilita'].value_counts().to_dict()
	condizioni_atmosferiche=filter_incidentiData['_CondizioneAtmosferica'].value_counts().to_dict()

	fondo_stradale=filter_incidentiData['_FondoStradale'].value_counts().to_dict()
	particolarita_strada=filter_incidentiData['_ParticolaritaStrade'].value_counts().to_dict()

	#visibilita=Counter(filter_incidentiData['_Visibilita'].tolist())
	#condizioni_atmosferiche=Counter(filter_incidentiData['_CondizioneAtmosferica'].tolist())
	#fondo_stradale=Counter(filter_incidentiData['_FondoStradale'].tolist())
	#particolarita_strada=Counter(filter_incidentiData['_ParticolaritaStrade'].tolist())
	

	particolarita_strada.pop("nan", None)
	tipo_strada.pop("nan", None)
	illuminazione.pop("nan", None)
	visibilita.pop("nan", None)
	condizioni_atmosferiche.pop("nan", None)
	fondo_stradale.pop("nan", None)
	
	#print(visibilita)
	#print(condizioni_atmosferiche)
	#print(tipo_strada)
	#print(particolarita_strada)
	#print(illuminazione)
	#print(fondo_stradale)
	


	filter_data= dati_completiData[['_TipoPersona', '_AnnoNascita','_Sesso','_TipoLesione', '_DecedutoDopo']]
	


	conducente= filter_data.loc[filter_data['_TipoPersona'] == "Conducente"]
	passeggero = filter_data.loc[filter_data['_TipoPersona'] == "Passeggero"]
	
	lesione_conducente=conducente['_TipoLesione'].value_counts().to_dict()
	lesione_passeggero=passeggero['_TipoLesione'].value_counts().to_dict()
	
	numero_feriti_conducente= lesione_conducente['Ricoverato'] +  lesione_conducente['Prognosi riservata']
	numero_feriti_passeggeri= lesione_passeggero['Ricoverato'] +  lesione_passeggero['Prognosi riservata']

	print("feriti")
	print(numero_feriti_conducente)

	lesione_conducente.pop(0, None)
	lesione_passeggero.pop(0, None)

	numero_lesione_conducente=len(conducente)
	numero_lesione_passeggero=len(passeggero)
	#print(list(lesione_passeggero.keys()))
	#print(list(lesione_passeggero.value()))

	#print(list(lesione_conducente.keys()))
	#print(list(lesione_conducente.value()))

	nascita_conducente= conducente['_AnnoNascita'].value_counts().to_dict()
	nascita_passeggero= passeggero['_AnnoNascita'].value_counts().to_dict()
	nascita_conducente.pop(0, None)
	nascita_passeggero.pop(0, None)
	

	deceduti_pedoni = pedoniData['_Deceduto'].value_counts().to_dict()
	deceduti_conducenti_passeggeri = (pedoniData['_DecedutoDopo'].value_counts().to_dict())
	
	
	numero_totale_deceduti_conducenti_passeggeri=deceduti_conducenti_passeggeri['DECEDUTO ENTRO IL QUARTO GIORNO']+deceduti_conducenti_passeggeri['DECEDUTO DA 13 A 24 ORE DOPO']


	anni=pedoniData['_AANascita'].value_counts().to_dict()
	anni.pop(0, None)
	
	numero_lesione_pedone=len(pedoniData['_TipoLesione'])
	lesione = pedoniData['_TipoLesione'].value_counts().to_dict()
	
	feriti = lesione['Ricoverato'] + lesione['Prognosi riservata']

	sesso=pedoniData['_Sesso'].value_counts().to_dict()
	#print (sesso)
	#print(list(lesione.keys()))
	#lesione_lista =[]

	#for i in list(lesione.keys()):
	#	lesione_lista.append(str(i))

	#print(lesione_lista)
	#lesione_lista=["Deceduto durante prime cure","Prognosi riservata","Deceduto sul posto","Ricoverato","Illeso","Rimandato","Rifiuta cure immediate"]
	
	#lesione_lista=pedoniData['_Sesso'].value_counts().to_dict()
	
	#for i in list(lesione.keys()):
		
	#	lesione_lista.append(i)
	#print(lesione_lista)
	#print(list(lesione.keys()))
	#print(list(lesione.values()))
	numero_totale_pedoni=len(pedoniData)
	numero_totale_conducenti_passeggeri = len(dati_completiData)
	'''
	with open(file_path) as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			print(row)
			data.append(row)
	'''
	context = {
		'data' : [tuple(x) for x in pedoniData.values],
		#'dataOraIncidente':dataOraIncidenteClean,
		'count_morti': count_morti, 
		'count_feriti':count_feriti,
		'count_illesi':count_illesi,
		'count_incidenti':count_incidenti,
		
		'anni': anni,
		'anni_lista': list(anni.keys()),
		'anni_valori': list(anni.values()),
		'numero_lesione_pedone':numero_lesione_pedone,
		'numero_totale_pedoni':numero_totale_pedoni,
		'numero_totale_conducenti_passeggeri':numero_totale_conducenti_passeggeri,
		'deceduti_pedoni':deceduti_pedoni[True],
		'deceduti_conducenti_passeggeri':numero_totale_deceduti_conducenti_passeggeri,
		'nascita_passeggero_lista':list(nascita_passeggero.keys()),
		'nascita_passeggero_valore':list(nascita_passeggero.values()),
		'nascita_conducente_lista':list(nascita_conducente.keys()),
		'nascita_conducente_valore':list(nascita_conducente.values()),
		'numero_feriti_conducente':numero_feriti_conducente,
		'numero_feriti_passeggeri':numero_feriti_passeggeri,
		'numero_feriti_passeggeri_conducenti':numero_feriti_passeggeri+numero_feriti_conducente,
		'percentuale_feriti_conducenti_passeggeri': math.ceil(100*(int(numero_feriti_passeggeri+numero_feriti_conducente)+numero_totale_deceduti_conducenti_passeggeri)/int(numero_totale_conducenti_passeggeri)),
		'sesso_lista': list(sesso.keys()),
		'sesso_valori': list(sesso.values()),
		'lesione':lesione,
		'lesione_lista': list(lesione.keys()),
		'lesione_valori': list(lesione.values()),
		'percentuale': math.ceil(100*(int(feriti)+len(deceduti_pedoni))/int(numero_totale_pedoni)),
		
		'illuminazione_lista':list(illuminazione.keys()),
		'illuminazione_valori':list(illuminazione.values()),

		'visibilita_lista':list(visibilita.keys()),
		'visibilita_valori':list(visibilita.values()),
		'condizioni_atmosferiche_lista':list(condizioni_atmosferiche.keys()),
		'condizioni_atmosferiche_valori':list(condizioni_atmosferiche.values()),
		'particolarita_strada_lista':list(particolarita_strada.keys()),
		'particolarita_strada_valori':list(particolarita_strada.values()),
		'fondo_stradale_lista':list(fondo_stradale.keys()),
		'fondo_stradale_valori':list(fondo_stradale.values()),
		
		

		'numero_lesione_passeggero': numero_lesione_passeggero,
		'numero_lesione_conducente': numero_lesione_conducente,
		'feriti': feriti,
		'matrix_settimanale':matrix_settimanale,
		'matrix_morti':matrix_morti,
		'matrix_illesi':matrix_illesi,
		'matrix_feriti':matrix_feriti,
		
		
	}
	return render_to_response('incidenti/base2.html',context)

def mappa(request):
	
	return render_to_response('incidenti/mappa.html')



def incidenti_gravi(request):
	
	return render_to_response('incidenti/gravi.html')