# -*- coding: utf-8 -*-

class YahooTopicAnswer (object):
    def _tipoClasse(self):
        return "modello di dati"
        
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
        
    def __init__(self, body, like, dislike, date, url):
        """ questa classe mi serve per modellare i dati. 
        """
       
        self.__answerText=body
        self.__answerLike=like
        self.__answerDislike=dislike
        self.__answerDate=date
        self.__url=url

    def getText(self):      
        return self.__answerText
    def getLike(self):
        return self.__answerLike
    def getDislike(self):  
        return self.__answerDislike
    def getData(self): 
        return self.__answerDate
    def getUrl(self):   
        return self.__url

if __name__=='__main__':
    print 'test class'
    