# -*- coding: utf-8 -*-
"""
Spyder Editor

"""
from __future__ import unicode_literals, division

import YahooTopic
import ErrorLog2
from MyFunction import LevaDApici
import PulisciSent

import urllib
import sqlite3
from bs4 import BeautifulSoup

class YahooAnswer(object):
    def _tipoClasse(self):
        return "estrattore dati dal web"
    def _statoLavorazione(self):
        return "in fitting per il progetto"
    def _todo(self):
        return "gestione errore con ErrorLog e sistemare restituzione dati"
    def _dataUltimazione(self):
        return "23\06\2015"
    def __author__(self):
        return "Patrizio Bellan \n patrizio.bellan@gmail.com"
    def __version__(self):
        return "0.1-a"

    def __init__(self, answer='ask', ordinamento='rillevanza', numeroRisultati=1 ,language=''):
        """ questa classe si occupa di effettuare ricerche su internet riguardo a tutte le domande
        i dati estratti serviranno per la costituzione della coscienza interna
        """
        try:
            self.__folder="risorse\\Dati\\"
            self.__pathFile=self.__folder+'answers\\'
            
            self.__pulisci=PulisciSent.PulisciSent()            
                
            
            self.t=[]   #var interna, ora la uso per restituire il primo topic e la risposta maggiormente votata
            
            #imposto i parametri interni
            self.__urlYahooAnswer='.answers.yahoo.com/search/search_result?fr=uh3_answers_vert_gs&type=2button&p='
            self.__urlYahoo='.answers.yahoo.com/'
                        
            self.__fileName=u""
  
            self.__defaultLang=u"it"
            self.__defaultAnswer=u"default"
            
            self.__answer=u""
            self.__language=u"it"
            
            self.__rawData=None
            self.__htmlHead=None
            self.__htmlBody=None
            self.__htmlCoding=None
            self.__urlYahooCurrentAnswer=u""
             
            self.__tipiOrdinamento={'recenti':'new','rillevanza':'rel','piu risposte':'most','meno risposte':'least'} 
            self.__ordinamento=''
            
            self.__numRisultati=numeroRisultati           
            self.__numRisultatiAnswer=0
            
            self.__topicpages=[]
            
            #inizializzo l'oggetto
            self.SetAnswer(answer)
            self.SetOrdinamento(ordinamento)
            self.SetLanguage(language)
            
            self.__costruisciUrl()
    
            if self.__answer!=self.__defaultAnswer:
                self.Answer()
                
                
        except Exception, e:
            ErrorLog2.ErrorLog(self.__class__.__name__, '__init__', e)

    def __str__(self):
        text='\n'+' YAHOO ANSWER '.center(25,'-')+'\n'
        text=text+'answer: ' +self.__answer+'\n'
        for topic in self.__topicpages:
            text=text+'\n titolo    : '+str(topic['title'])
            text=text+'\n             '+str(topic['body'])
            text=text+'\n categoria : '+str(topic['categoria'])
            text=text+'\n risposte  : '+str(topic['risposte'])
        return text
        
        
    def SetLanguage(self, language):         
        if language=='':
            self.__language=self.__defaultLang
        else:
            self.SetLanguage(language)
            #per ora non controllo se la lingua esiste

    def SetOrdinamento(self, ordinamento):
        if ordinamento not in self.__tipiOrdinamento.keys(): ordinamento='rillevanza'
        self.__ordinamento=self.__tipiOrdinamento[ordinamento]
        
        
    def __costruisciUrl(self, numPage=0):
        #costruisco l'url
        if numPage<=1:
            self.__urlYahooCurrentAnswer='https://'+   \
            self.__language+self.__urlYahooAnswer+self.__answer+ \
            '&sort=' + self.__ordinamento
        else:
            self.__urlYahooCurrentAnswer='https://'+   \
            self.__language+self.__urlYahooAnswer+self.__answer+ \
            '&s=' +str(numPage)+'&sort=' + self.__ordinamento
        return self.__urlYahooCurrentAnswer
        
    def Answer(self):
        """ 
            questa funzione avvia il processo di ricerca dei dati, i parametri sono 
            specificati quando creo l'istanza
            
            i dati sono salvati su file dalla classe YahooTopic.py
            
            ritorna True se il processo termina correttamente
            
        """

        try:
            #estraggo i dati
            self.__TopicsPages()
            #invio le richiste ai vari YahooTopic
            for topic in self.__topicpages:
                topic['ask url']=u'https://' +topic['ask url']
                #print 'elaborazione di :', topic['ask url']
                
                _t=YahooTopic.YahooTopic(topic['ask url'])
                
                self.t.append(_t)

            return True
#            return self.t[0].MostVotedAnswer.getText(), self.t[0].sogliaMostVotedAnswer
                
        except Exception, e:
            ErrorLog2.ErrorLog(self.__class__.__name__, 'Answer', e)
            return False
            
    def SetAnswer(self,answer):
        if answer==u"":
            self.__answer=self.__defaultAnswer 
        else:
            self.__answer=answer
            
        
    def __OpenPage(self, url):
        try:
            risposta= urllib.urlopen(url).read()
            soup=BeautifulSoup(risposta)
            self.__rawData=soup
            #Verifico se la Pagina Esiste
            if not self.__PageExist(soup):return False
            #estraggo e verifico i metatag
            return soup
            
        except Exception, e:
            ErrorLog2.ErrorLog(self.__class__.__name__, 'OpenPage', e)
            return False
    
    
    def __PageExist(self, soup):
        #se la pagina contiente la class fs16 fwl con id error-message, allora non esiste e il suo len è 0
        if len(soup.findAll('div',id='error-message', class_='fs16 fwl'))==0: 
            return True
        else:
            return False
    
    def __MetaOperazioni(self,soup):
        """ estrazione dei metadati"""
        try:
            self.__htmlHead=soup.head
            self.__htmlBody=soup.body
            
            #CODIFICA
            #estrazione codifica pagina            
            tmp=soup.head.meta
            tmp=soup.head.meta.attrs['content'].split(';')
            #print 'tmp2:',tmp[1]        
            tmp=tmp[1].split('=')
            self.__htmlCoding=str(tmp[1])
            #print 'codifica in __MetaOperazioni: ', self.__htmlCoding
            
            #verifico che l'encoding originale sia uguale a quello della pagina
            encoding=unicode(self.__htmlCoding,self.__htmlCoding)
            if encoding.lower() != soup.original_encoding:
                print '###--->>> ATTENZIONE, ERRORE DI CODIFICA, LA PAGINA è CODIFICATA \
                    CON ', encoding, ' METRE BS4 HA CODIFICA \
                    INTERNA CON ', soup.original_encoding
                return False
            
        
            #numero totale di risposte alla domanda fatta
            nres=soup.body.p.text
            nres=nres.replace('.','')
            nres=nres.strip()
            #nres=nres.split(' ') 
            try:
                nres=int(nres)
            except:
                nres=2147483647
            self.__numRisultatiAnswer=nres
            #se il numero di risultati che cerco è maggiore dei risultati trovati, lo modifico con quest'ultimi
            if int(self.__numRisultati)>int(self.__numRisultatiAnswer):
                self.__numRisultati=self.__numRisultatiAnswer
            #print self.__numRisultati, self.__numRisultatiAnswer
            return True
        
        except Exception, e:
            ErrorLog2.ErrorLog(self.__class__.__name__, 'MataOperazioni', e)
            return False
        
        
    def __TopicsPages(self):
        """ 
            questa funzione si occupa di estrarre i dati dal web
        """
        
        try:
            #apro l'url
            pagina=self.__OpenPage(self.__urlYahooCurrentAnswer)
            if not self.__MetaOperazioni(pagina): 
                return False            
            #gestisco l'eventuale errore di url
            if not pagina:
                #print 'La ricerca  non ha prodotto risultati'
                return False
            else:
                #ora per il numero di risultati che voglio estrarre
                #1- estraggo i risultati dalla pagina
                #2 estraggo le altre pagine
                
                indexpages=1
                pag=[]
                
                while True:
                    #devo iterare tra tutte le pagine fino a che ho i risultati, 
                    #le pagine esisteranno sempre dato che ho impostato il numero di risultati consultabili al max come i 
                    #risultati totali ottenuti
                    topicrel=pagina.findAll('div',{'class':'dynamic'})
                    #IN OGNIUNA C HO IL PEZZO DA CUI ESTRARRE LE INFORMAZIONI RELATIVE A N RISP, LINK, CATEGORIA ECC...
                    for c in topicrel[0].findAll('li'):
                        #d è una variabile temporanea 
                        
                        #per prima cosa identifico il tipo in cui è stata strutturata la domanda
                        #tipo 0: no badge
                        #tipo 1: badge-o
                        
                        asktitle=c.h3.text
                        askbody=c.span.text
                        asktitle=asktitle.strip()
                        askbody=askbody.strip()
                        #se il corpo della domanda è vuoto lo sostituisco con il titolo
                        if askbody==u'':askbody=asktitle
                            
                        tipo=c.findAll('span',{'class':'badge-o'})
                        
                        if tipo==[]: 
                            #print 'tipo 0'
         
                            d=c.findAll('a')
    
                            paginarisposte=d[0]['href']
                            paginarisposte=unicode(paginarisposte,'UTF-8')
                            
                            _url=self.__language+self.__urlYahoo[:-1]
                        
                            paginarisposte=_url+paginarisposte
  
                            askcategoria=d[1].text #categoria/e
                            askcategoria=askcategoria.strip()
                            askcategorialink=d[1]['href'] #indirizzo categoria
                            _url=self.__language+self.__urlYahoo[:-1]
                            
                            askcategorialink=unicode(askcategorialink,'UTF-8')
                            askcategorialink=_url+askcategorialink
                            
                            if c.find('img',{'class':'img-video-tn'})!=None: #se ha il video
                            
                                d=c.findAll('div')
                                d=d[3].text
                                d=d.replace(askcategoria,'')
                                d=d.strip()
                                d=d.split()
                                
                                d=d[0]
                                numerorisposte=d            
                                numerorisposte=unicode(str(numerorisposte), 'utf-8')
                                
                            else:
                                d=c.findAll('div')
                                d=d[2].text
                                d=d.replace(askcategoria,'')
                                d=d.strip()
                                d=d.split()
                                if d=='' or d==u'' or d==[]:    #quando non ci sono risposte
                                    d=0                            
                                else:
                                    d=d[0]
                                    
                                numerorisposte=d           
                                numerorisposte=unicode(str(numerorisposte), 'utf-8')

                        else:
                            #print 'tipo 1'
                            
                            d=c.findAll('a')
                            #d[0]['href']   #indirizzoRisposta
                            paginarisposte=d[0]['href']
                            _url=self.__language+self.__urlYahoo[:-1]
                            paginarisposte=unicode(paginarisposte,'UTF-8')
                            paginarisposte=_url+paginarisposte                                              
                                                    
                            askcategoria=d[2].text #categoria/e
                            askcategoria=askcategoria.strip()
                            askcategorialink=d[2]['href'] #indirizzo categoria
                            _url=self.__language+self.__urlYahoo[:-1]
                            askcategorialink=unicode(askcategorialink,'UTF-8')
                            askcategorialink=_url+askcategorialink
                            d=c.findAll('div')
                            
                            d=d[2].text
                            d=d.strip()
                            d=d.split()
        
                            numerorisposte=d[-(len(askcategoria.split())+3)]
                            numerorisposte=int(numerorisposte)

                            numerorisposte=unicode(str(numerorisposte), 'utf-8')       

                        page={'title':asktitle, 'body':askbody, 'categoria':askcategoria, \
                                'categoria url':askcategorialink,'ask url':paginarisposte, \
                                'risposte':numerorisposte}
                        pag.append(page)
                        if len(pag)>int(self.__numRisultati):
                            self.__topicpages=pag
                            return pag
                            
                    indexpages+=1       
                    urlpage=self.__costruisciUrl(indexpages)
                    pagina=self.__OpenPage(urlpage)
                    if not pagina:
                        return False
        except Exception, e:
            ErrorLog2.ErrorLog(self.__class__.__name__, 'TopicPages', e)
            return False

        
    def getUrlYahoo (self):   
        return self.__urlYahooAnswer
        
    def getAnswer (self):     
        return self.__answer
        
    def getLanguage(self):    
        return self.__language
        
    def getCurrentUrl(self):
        return self.__urlYahooCurrentAnswer
        
    def getTipiOrdinamento(self):   
        return self.__tipiOrdinamento.keys()
        
    def getOrdinamento(self):       
        return self.__ordinamento
        
    def getNumeroRisultatiDaEspolare(self):     
        return self.__numRisultati
        
    def getNumeroRisultatiAnswer (self):        
        return self.__numRisultatiAnswer
            
    
    #utili per costruzione e manutenzione classe
    def getRawData(self):     
        return self.__rawData
        
    def getSoup(self):        
        return self.__rawData
        
    def getHtmlEncoding(self):
        return self.__htmlCoding
        
    def getTopicPages(self):  
        return self.__topicpages
    

#--------test della classe------------
    
def test_2():
    print 'test 2'
    a=YahooAnswer(answer='elettronica', ordinamento='piu risposte', numeroRisultati=5)
    a.Answer()
    print 'done'
    
def test_1():
    import time
    start= time.time() 
    print 'test 1'
    print 'start time: ', start    

    
    a=YahooAnswer(answer='film', ordinamento='piu risposte', numeroRisultati=11)
    b=YahooAnswer(answer='lista', ordinamento='meno risposte', numeroRisultati=11)    
    c=YahooAnswer(answer='pizza', ordinamento='piu risposte', numeroRisultati=41)
    d=YahooAnswer(answer='piacere', ordinamento='recenti', numeroRisultati=16)    
    e=YahooAnswer(answer='dolore', ordinamento='piu risposte', numeroRisultati=11)
    f=YahooAnswer(answer='odio', ordinamento='rillevanza', numeroRisultati=3)
    g=YahooAnswer(answer='perdono', ordinamento='meno risposte', numeroRisultati=21)    
    h=YahooAnswer(answer='vittoria', ordinamento='piu risposte', numeroRisultati=11)
    i=YahooAnswer(answer='ti senti fortunato', ordinamento='piu risposte', numeroRisultati=31)    
    l=YahooAnswer(answer='a cosa giochi? perché?',ordinamento='rillevanza',numeroRisultati=54)
   
    a.Answer()
    #a.DbWrite()
    print 'a completato'
    b.Answer()
    #b.DbWrite()
    print 'b completato'
    c.Answer()
    #c.DbWrite()
    print 'c completato'
    d.Answer()
    #d.DbWrite()
    print 'd completato'
    e.Answer()
    #e.DbWrite()
    print 'e completato'
    f.Answer()
    #f.DbWrite()
    print 'f completato'
    g.Answer()
    #g.DbWrite()
    print 'g completato'
    h.Answer()
    #h.DbWrite()
    print 'h completato'    
    i.Answer()
    #i.DbWrite()
    print 'i completato'
    l.Answer()
    #l.DbWrite()
    print 'l completato'
    
    end=time.time ()
    ntopics=11+11+41+16+11+3+21+11+31+54
    tempo=round((end-start),4)
    print 'processo completato per '+str(ntopics)+' topics in: '+ str(tempo)+' secondi'
    print 'media di:'+str(float(tempo/ntopics))+' sec per topics'
    print 'media di:'+str(float(ntopics/tempo))+' topics al secondo'
    
    print 'done'

if __name__=='__main__':
    a=YahooAnswer(answer='giocare', ordinamento='rillevanza', numeroRisultati=55)
#    b, c=a.Answer()
#    print b
#    print
#    print c
    print 'done'
      