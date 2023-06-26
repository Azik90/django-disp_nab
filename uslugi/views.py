from django.shortcuts import render
import sqlite3

# Create your views here.
def home(request):
    return render(request,'uslugi/home.html')

def usluga(request):
    ds1 = request.GET.get('code')
    ds = ds1.replace(" ","").upper() # удалим пробелы и переведем вверхний регистр
    
    con = sqlite3.connect('mes_mkb.db') # подключимся базе данных 
    sql = con.cursor()

    sql.execute("SELECT * FROM mes") # запросим все элементы из таблицы 
    mes_tab = sql.fetchall() # получаем все записи из базы данных, используя метод cursor.fetchall()
    # mes_tab = [ 76-1-1, теравепт, МКБ1, МКБ2, 100, периодичность, коммент]

    sql.execute("SELECT * FROM mkb10") # запросим все элементы из таблицы 
    baza_mkb = sql.fetchall() # получаем все записи из базы данных, используя метод cursor.fetchall()

    con.close() # закрываем базу

    vidimes =[]

    for n in mes_tab: # пройдемся по базе дисп
        dian =[]
        a = 0
        for k in baza_mkb: # пройдемся по базе мкб, ищем совпадения
            if k[0] == n[2]: # начало диапазона
                a = 1
            if a == 1:
                dian.append(k[0])
            if k[0] == n[3]: # конец диапазона
                a = 0
                continue
        for j in dian: # сохраним диапазон
            if ds == j:
                vidimes.append(n) # хранить данные как : [ 76-1-1, теравепт, МКБ1, МКБ2, 100, периодичность, коммент]



    con = sqlite3.connect('mes_mkb.db') # подключимся базе данных 
    sql = con.cursor()
    sql.execute("SELECT * FROM SPSERVSTANDARD") # запросим все элементы из таблицы 
    SPSERVSTANDARD = sql.fetchall() # получаем все записи из базы данных, используя метод cursor.fetchall()
    con.close()

    mes_medserv =[]
    v_serv =[]

    for n in vidimes:  # хранить данные как : [ 76-1-1, теравепт, МКБ1, МКБ2, 100, периодичность, коммент]
        for irec in SPSERVSTANDARD:
        
            if (n[0] == irec[0]):
                
                a2 = [irec[0], irec[1], irec[2], irec[3], n[1],n[5],n[6],irec[4]]
                
                mes_medserv.append(a2) # [ 76-1-1  0, дивизион 1, код услуги 2, мастхев 3, теравепт 4, периодичность 5, коммент 6, имя МЭС 7]
  

    if mes_medserv != v_serv:

        con = sqlite3.connect('mes_mkb.db') # подключимся базе данных 
        sql = con.cursor()
        sql.execute("SELECT * FROM SPMEDSERVICE") # запросим все элементы из таблицы 
        RECsv = sql.fetchall() # получаем все записи из базы данных, используя метод cursor.fetchall()
        # RECsv = [code 0, division 1, name 2]
        con.close()

        for irec in RECsv:
            for chil in mes_medserv:
                
                if chil[2] == irec[0] and chil[1] == irec[1]:

                    #25-1-3, имя МЭС , кардиолог, 301[дивизион], [MUSTHAVE], [периодичность], B03.016.002.999, клинический анализ крови, COMM
                    # 0        1          2           3               4           5                   6              7                    8
                    ans = [chil[0],chil[7],chil[4],chil[1],chil[3],chil[5],irec[0],irec[2],chil[6]]
                    v_serv.append(ans)
                    
        stan =[] # будем хранить стандаты по текушему диагнозу  типа 76-1-5

        for elem in v_serv:

            if elem[0] not in stan:
                stan.append(elem[0])

        # stan.reverse()
        stand =[]
        #--------------------------------------------------------------------------------------------------
        for elem in stan: 

            text =''
            profil =''
            period =''
            mes_name =''
            
            for k in v_serv:
                if elem == k[0]:
                    profil = k[2]
                    period = k[5]
                    mes_name = k[1]

           
            text += "<h4>СТАНДАРТ (МЭС) : " +elem + "   Наименование: " + mes_name +'\nПРОФИЛЬ : '+ profil+'\n'+'периодичность : '+ period+'  раз(а) в год\n' +"предусмотрены следующие обязательные услуги:</h4>"
           

            for k in v_serv:
                if elem == k[0] and k[4] == '1':
                    #print(k[6],k[7])
                    text += "- " + k[6] +"  "+ k[7] +'\n'
                    
        
            #print("\nИ ЧТО-ТО ИЗ ЭТОГО:")
            
            w = True
            for k in v_serv:
                
                if elem == k[0] and k[4] == '2':
                    #print(k[6],k[7])
                    if w:
                        text +="\n<h4>а так же обязательно необходима одна из услуг из этого списка:</h4>"
                        w = False
                    text += "- " + k[6] +"  "+ k[7] +'\n'
                    

            #print("\nИ МОЖНО ДОПОЛНИТЕЛЬНО:")
            
            w = True
            for k in v_serv:
                if elem == k[0] and k[4] == '0':
                    #print(k[6],k[7])
                    if w:
                        text +="\n<h4>кроме того, можно дополнительно оказать услуги из этого списка:</h4>"
                        w = False
                    text += "- " + k[6] +"  "+ k[7] +'\n'

            w = True
            for k in v_serv:
                
                if elem == k[0]:
                    #print(k[6],k[7])
                    if w:
                        text += '\n<h4>комментарий:\n</h4>'+ k[8]
                        w = False         
            
                    

            stand.append(text)
           


        return render(request,'uslugi/usluga.html',{'ds':ds,'stand':stand})
    
    elif vidimes != v_serv:
        stand=[]
        text = "стандарт "+ vidimes[0][0] + ', но он отсутсвует в справочнике SPSERVSTANDARD, используйте приказ 168'
        
        stand.append(text)
        return render(request,'uslugi/usluga.html',{'stand':stand})

    else:
        stand=[]
        print(" нет в базе ДН с таким диагнозом ")
        text ='В 168 Приказе отсутстует такой диагноз или порверте правильно ли Вы пишите диагноз, то есть на английском, а не на русском языке'
        stand.append(text)
        return render(request,'uslugi/usluga.html',{'stand':stand})

def mes_usl(request):
    mes1 = request.GET.get('mes')
    mes = str(mes1.replace(" ","")) # удалим пробелы
    print(mes)
 
    con = sqlite3.connect('mes_mkb.db') # подключимся базе данных 
    sql = con.cursor()
    sql.execute("SELECT * FROM SPSERVSTANDARD") # запросим все элементы из таблицы 
    REC = sql.fetchall() # получаем все записи из базы данных, используя метод cursor.fetchall()
    con.close()

    mes_medserv =[]
    stand =[]
    mes_name = ''

    for irec in REC:
    
        if (mes == str(irec[0])):
            #[irec.getAttribute("MEDSTANDARD"), irec.getAttribute("DIVISION"), irec.getAttribute("MEDSERVICE"), irec.getAttribute("MUSTHAVE")]
            a= [irec[0], irec[1], irec[2], irec[3]]
            mes_name = irec[4]
            mes_medserv.append(a)
            
    if mes_medserv == []:
        print(" нет в базе ДН с таким диагнозом ")
        text ='В спавочнике отсутствует такой МЭС или Вы не правильно ввели код МЭС'
        stand.append(text)
        return render(request,'uslugi/uslmes.html',{'stand':stand})
            
  

    con = sqlite3.connect('mes_mkb.db') # подключимся базе данных 
    sql = con.cursor()
    sql.execute("SELECT * FROM SPMEDSERVICE") # запросим все элементы из таблицы 
    RECsv = sql.fetchall() # получаем все записи из базы данных, используя метод cursor.fetchall()
    con.close()

    serv_usl=[]    
    for irec in RECsv:
        for k in mes_medserv:
     
            if k[2] == irec[0] and irec[1] == k[1]:

                #25-1-3, 301[дивизион], 1[MUSTHAVE],  B03.016.002.999, клинический анализ крови, 
                # 0        1               2               3               4                                              
                ans = [k[0],k[1],k[3],irec[0],irec[2]]
                #print(ans) ['76-1-1', '300', '2', 'B04.047.001', 'Прием (осмотр, консультация) врача-терапевта диспансерный']
                serv_usl.append(ans)
    #print(serv_usl)        
                
    stan =[] # будем хранить стандаты по текушему диагнозу  типа 76-1-5

    for elem in serv_usl:

        if elem[0] not in stan:
            stan.append(elem[0])

    stan.reverse()
    

    for elem in stan: 

        text =''

        text += "<h4>СТАНДАРТ (МЭС) : " +elem + " предусмотрены следующие обязательные услуги:</h4>"
        

        for k in serv_usl:
            if elem == k[0] and k[2] == '1':
              
                text += "- " + k[3] +"  "+ k[4] +'\n'
                
    
        #print("\nИ ЧТО-ТО ИЗ ЭТОГО:")
        
        w = True
        for k in serv_usl:
            
            if elem == k[0] and k[2] == '2':
                
                if w:
                    text +="\n<h4>а так же обязательно необходима одна из услуг из этого списка:</h4>"
                    w = False
                text += "- " + k[3] +"  "+ k[4] +'\n'
                

        #print("\nИ МОЖНО ДОПОЛНИТЕЛЬНО:")
        
        w = True
        for k in serv_usl:
            if elem == k[0] and k[2] == '0':

                if w:
                    text +="\n<h4>кроме того, можно дополнительно оказать услуги из этого списка:</h4>"
                    w = False
                text += "- " + k[3] +"  "+ k[4] +'\n'
        
        w = True
        for k in serv_usl:
            if elem == k[0] and k[2] == '4':

                if w:
                    text +="\n<h4>а так же не понятные услуги из этого списка, где MUSTHAVE = 4 :</h4>"
                    w = False
                text += "- " + k[3] +"  "+ k[4] +'\n'
            
        stand.append(text)
        
    return render(request,'uslugi/uslmes.html',{'stand':stand, 'mes_name':mes_name})
