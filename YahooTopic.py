# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 00:21:39 2015

@author: Patrizio

            SISTEMA IL NOME DEI FILE CON I META:
        MODIFICA IN                RIGA DI CODICE 260
        

"""
from __future__ import unicode_literals, division

import AnalizzatoreSents

import ErrorLog2

import PulisciSent

import SaveLoad


from YahooTopicAnswer import YahooTopicAnswer
from MyFunction import LevaEscape, DataPubblicazione, LevaDApici


import urllib

from bs4 import BeautifulSoup


class YahooTopic(object):
    def _tipoClasse(self):
        return "estrattore dati dal web"
    def _statoLavorazione(self):
        return "in fitting per il progetto"
    def _dataUltimazione(self):
        return "31\08\2015"
    def __author__(self):
        return "Patrizio Bellan \n patrizio.bellan@gmail.com"
    def __version__(self):
        return "0.1-a"
        
    def __init__(self, url, nrisp=10):
        """ questa classe si occupa di estrarre e salvare i topic
        
        #INCREMENTO 1 la classe restituisce la risposta con il raking maggiore. 
            il raking è dato dalla percentuale di like/dislike dato dalla rete
            a parità di punteggio vince la best answer
        
        """
        try:
            self.__SEPARATORE=u"\n[SEPARATORE]\n"
            
            self.__folder="risorse\\Dati\\"
            self.__pathAnswer=self.__folder+'answers\\'
            self.__extFile='.yahootopic'
            
            self.__pulisci=PulisciSent.PulisciSent()
            self.__Analizzatore=AnalizzatoreSents.AnalizzatoreSents()
            self.__topicAskTitle=''
            self.__topicAskBody=''
            self.__askdata=''
            
            self.__bestAnswer=None
            self.MostVotedAnswer=None
            self.sogliaMostVotedAnswer=float(0)
            
            self.__url=url
            
            self.__maxRisposte=nrisp
            
            self.__allAnswer=[]
                    
            self.__rawData=self.__OpenPage(url)
            if self.__rawData!=False:
                self.__estraiDati(self.__rawData)
                #salvo tutti i dati
                self.SaveFile()
                
        except Exception, e:
            ErrorLog2.ErrorLog(self.__class__.__name__, 'YahooTopic', e)
            
        
    def getAllAnswer(self): 
        return self.__allAnswer
    def getBestAnswer(self):
        return self.__bestAnswer.getText()
    def getRawData(self):   
        return self.__rawData
    def getUrl(self):       
        return self.__url
        
        
    def __str__(self):
        text='[TITLE]\n'
        text=text+self.__topicAskTitle
        text=text+'\n[BODY]\n'
        text=text+self.__topicAskBody
        text=text+'\n[DATA]\n'
        text=text+self.__askdata
        if self.__bestAnswer!=None:
            text=text+'\n[BEST ANSWER]\n'
            text=text+self.__bestAnswer.getText()
            text=text+'\n[LIKE]\n'
            text=text+self.__bestAnswer.getLike()
            text=text+'\n[DISLIKE]\n'
            text=text+self.__bestAnswer.getDislike()
            text=text+'\n[DATA]\n'
            text=text+self.__bestAnswer.getData()

            for i in range(len(self.__allAnswer)):
                if i == len(self.__allAnswer)-1:
                    break
                if i==0:
                    i+=1    #salto la BestAnswer 
                text=text+'\n[ANSWER]\n'
                text=text+self.__allAnswer[i].getText()
                text=text+'\n[LIKE]\n'
                text=text+self.__allAnswer[i].getLike()
                text=text+'\n[DISLIKE]\n'
                text=text+self.__allAnswer[i].getDislike()
                text=text+'\n[DATA]\n'
                text=text+self.__allAnswer[i].getData()
        text=text.encode('utf-8')
        
        return text

         
    def __OpenPage(self, url):
        try:
            risposta= urllib.urlopen(url).read()
            soup=BeautifulSoup(risposta)
            self.__currentUrl=url
            return soup
          
        except Exception, e:
            ErrorLog2.ErrorLog(self.__class__.__name__, 'OpenPage', e)
            return False
            
            
    def __estraiDati(self, pagina):
        try:
            #var temporanea d
            #per sapere quante risposte devo leggere, uso la variabile interna __maxRisposte
            numeropagina=1
            d=pagina.head.findAll('meta')
            asktitle=d[2]['content']
            self.__topicAskTitle=asktitle
            
            askbody=d[3]['content']
            
            self.__topicAskBody=askbody
            
            askkeywords=d[4]['content']
            
            askdata=d[8]['content']
            y=askdata[:4]
            
            askdata=y#+'-'+m+'-'+d
            self.__askdata=askdata
            
            #bestANsweR
      
            c=pagina.findAll('div')
            x=False
            for i in c:
                if i.has_attr('id'):
                    if i['id']=='ya-best-answer':
                        x=i
                        break
            if not x:
                #caso in cui non ci siano risposte alla domanda
                #esco e non faccio nessun'altra operazione
                return
            f=x.findAll('span')
            babody=f[2].text
            badata=f[5].text
            badata=badata.strip()        
            badata=badata.split()
            badata=badata[1:]
            badata=DataPubblicazione(badata)
            #print babody, badata
            f=x.findAll('div')
            balike=f[11].text
            badislike=f[14].text
            #print balike,badislike
            self.__bestAnswer=YahooTopicAnswer(babody,balike,badislike,badata, self.__currentUrl)
            self.__allAnswer.append(self.__bestAnswer)
            self.MostVotedAnswer=self.__bestAnswer
            self.sogliaMostVotedAnswer=float(self.__bestAnswer.getLike)/float(self.__bestAnswr.getDislike)
             
            #per le altre risposte itero e itero sulle pagine
            while True:
                if len(self.__allAnswer)>=self.__maxRisposte: return
                
                #le altre risposte....
                
                #se ho una perdita di dati dall'oggetto "pagina" 
                #non blocco il flusso del programma 
                #ma interrompo l'eseguzione dell'oggetto
                
                if pagina.body==None:return
                d=pagina.body.findAll('ul')
                
                #d[11] contiene tutte le risposte della pagina
                risposte=d[11].findAll('li')
                for risp in risposte:
                    corporisposta=risp.span.text
                    d=risp.findAll('span')
                    corporisposta=d[0].text
                    datapubblicazione=d[1].text
                    datapubblicazione=datapubblicazione.strip()        
                    datapubblicazione=datapubblicazione.split()
                    datapubblicazione=datapubblicazione[1:]
                    try:
                        datapubblicazione[0]=int(datapubblicazione[0])
                        datapubblicazione[0]=unicode(str(datapubblicazione[0]),'utf-8')
                    except:                    
                        
                        corporisposta=corporisposta +u'\n'+d[2].text
                        datapubblicazione=d[3].text
                        
                        datapubblicazione=datapubblicazione.strip()        
                        datapubblicazione=datapubblicazione.split()
                        datapubblicazione=datapubblicazione[1:]
                    datapubblicazione=DataPubblicazione(datapubblicazione)
                    
                    #ev, e è var tmp
                    e=risp.findAll('div')
                    rel=''
                    for div in e:
                        if div.has_attr('class') and div['class']==['D-ib', 'Mend-10', 'Clr-93']:
                            rel=div
                            break
                    #d è sempre una var tmp
                    dv=[]
                    for div in rel.findAll('div'):
                        if div.has_attr('class') and div['class']== ['D-ib', 'Mstart-23', 'count']:
                            dv.append(div.text)            
                    like=dv[0]
                    dislike=dv[1]
                    
                    _answer=YahooTopicAnswer(corporisposta,like,dislike,datapubblicazione,self.__currentUrl)
                    sogliatemp=float(_answer.getLike)/float(_answer.getDislike)
                    if sogliatemp>self.sogliaMostVotedAnswer:
                        self.sogliaMostVotedAnswer=sogliatemp
                        self.MostVotedAnswer=_answer

                    self.__allAnswer.append(_answer)
                    if len(self.__allAnswer)>=self.__maxRisposte:
                        return self.MostVotedAnswer
                    
                #itero sulle altre pagine
                numeropagina+=1
                url=self.__url+'&page='+str(numeropagina)
                #memorizzo nell'oggetto il codice html della pagina che sto analizzando
                #per facilitare la manutenzione
                self.__rawData=self.__OpenPage(url)
                pagina=self.__rawData
                
            return self.MostVotedAnswer
            
        except Exception, e:
            ErrorLog2.ErrorLog(self.__class__.__name__, '__estraiDati', e)
            return False
          
    
    def SaveFile(self):
        try:
            if self.MostVotedAnswer.getText()!=u"":
                dati=self.MostVotedAnswer.getText()
                dati=self.__pulisci.Pulisci(dati)
                dati=dati.strip()
                
                filename=self.__pulisci.PulisciFilename(self.__topicAskTitle)                
                filename=self.__pathAnswer+filename+self.__extFile
                self.filename=filename
                
                topic=self.__topicAskTitle+u"\n"+self.__topicAskBody
                topic=self.__pulisci.Pulisci(topic)
                body=self.__pulisci.Pulisci(self.MostVotedAnswer.getText())                
                dati=topic+self.__SEPARATORE+body
                                    
                if not SaveLoad.SaveLines(dati,filename):
                    print "file non salvato: ", filename        
                    return False
                else:
                    print "file saved:", filename
                return True
                
        except Exception, e:
            for i in e:print i
            ErrorLog2.ErrorLog(self.__class__.__name__, 'SaveFile', e)
            return False
                        
if __name__=='__main__':
    url='https://it.answers.yahoo.com/question/index?qid=20120723141422AAWsx3a'
    a=YahooTopic(url,5)
    a.filename
    print 'done'
    