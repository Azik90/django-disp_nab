from django.shortcuts import render
import sqlite3

# Create your views here.
def home(request):
    return render(request,'uslugi/home.html')

def usluga(request):
    ds1 = request.GET.get('code')
    ds = ds1.replace(" ","").upper() # удалим пробелы и переведем вверхний регистр

    #stand ="654685"
    #return render(request,'uslugi/usluga.html',{'ds':ds, 'st':stand})
    
    con = sqlite3.connect('mes_mkb.db') # подключимся базе данных 
    sql = con.cursor()
    sql.execute("SELECT * FROM SPDISPMKB") # запросим все элементы из таблицы 
    baza_disp_mkb = sql.fetchall() # получаем все записи из базы данных, используя метод cursor.fetchall()

    sql.execute("SELECT * FROM mkb10") # запросим все элементы из таблицы 
    baza_mkb = sql.fetchall() # получаем все записи из базы данных, используя метод cursor.fetchall()

    con.close() # закрываем базу
    
    

    vidmes =[]

    for n in baza_disp_mkb: # пройдемся по базе дисп
        dian =[]
        a = 0
        for k in baza_mkb: # пройдемся по базе мкб, ищем совпадения
            if k[0] == n[0]: # начало диапазона
                a = 1
            if a == 1:
                dian.append(k[0])
            if k[0] == n[1]: # конец диапазона
                a = 0
                continue
        for j in dian: # сохраним диапазон
            if ds == j:
                vidmes.append(n) # хранить данные как SPDISPMKB: MKB1 , MKB2 ,DISPD ,PERIOD ,COMM 




    vmes =[] # ['76-1-2', '100', 'врач-терапевт', '2',COMM]


    bd = sqlite3.connect('mes_mkb.db') # подключимся базе данных 
    sql = bd.cursor()
    sql.execute("SELECT * FROM mes") # запросим все элементы из таблицы 
    a = sql.fetchall() # получаем все записи из базы данных, используя метод cursor.fetchall()
    bd.close() # закрываем базу

    for n in vidmes:
        # ['76-1-34', '100', 'врач-терапевт', '2']
        for j in a:
            #print(type(n[0]),type(j[2]),type(n[1]),type(j[3]),type(n[2]),type(j[4]))
            if (n[0] == j[2]) and (n[1] == j[3]) and (n[2] == j[4]):
                ans = [j[0],j[4],j[1],n[3],n[4]] # МЭС, КОД ВРАЧА (100), НАЗВАНИЕ ВРАЧА, ПЕРИОДИЧНОСТЬ ПОСЕЩЕНИЯ В ГОД,COMM
                vmes.append(ans)
            

    vidmes.clear()

    con = sqlite3.connect('mes_mkb.db') # подключимся базе данных 
    sql = con.cursor()
    sql.execute("SELECT * FROM SPSERVSTANDARD") # запросим все элементы из таблицы 
    REC = sql.fetchall() # получаем все записи из базы данных, используя метод cursor.fetchall()
    con.close()

    mes_medserv =[]
    v_serv =[]

    for n in vmes:
        for irec in REC:
        
            if (n[0] == irec[0]):
                #a2 = [irec.getAttribute("MEDSTANDARD"), irec.getAttribute("DIVISION"), irec.getAttribute("MEDSERVICE"), irec.getAttribute("MUSTHAVE"), n[1],n[2],n[3]]
                a2 = [irec[0], irec[1], irec[2], irec[3], n[1],n[2],n[3],n[4]]
                #v_serv.append(a2)
                mes_medserv.append(a2)
  
    v_serv.clear()

    if mes_medserv != v_serv:

        con = sqlite3.connect('mes_mkb.db') # подключимся базе данных 
        sql = con.cursor()
        sql.execute("SELECT * FROM SPMEDSERVICE") # запросим все элементы из таблицы 
        RECsv = sql.fetchall() # получаем все записи из базы данных, используя метод cursor.fetchall()
        con.close()

        for irec in RECsv:
            for chil in mes_medserv:
                
                if chil[2] == irec[0] and irec[1] == chil[1]:

                    #25-1-3, 200[врач], кардиолог, 301[дивизион], 1[MUSTHAVE], 2[периодичность], B03.016.002.999, клинический анализ крови, COMM
                    # 0        1          2           3               4           5                   6              7                       8
                    ans = [chil[0],chil[4],chil[5],chil[1],chil[3],chil[6],irec[0],irec[2],chil[7]]
                    v_serv.append(ans)
                    
        stan =[] # будем хранить стандаты по текушему диагнозу  типа 76-1-5

        for elem in v_serv:

            if elem[0] not in stan:
                stan.append(elem[0])

        stan.reverse()
        stand =[]

        for elem in stan: 

            text =''
            profil =''
            period =''
            
            for k in v_serv:
                if elem == k[0]:
                    profil = k[2]
                    period = k[5]

           
            text += "<h4>СТАНДАРТ (МЭС) : " +elem +'\nПРОФИЛЬ : '+ profil+'\n'+'периодичность : '+ period+'  раз(а) в год\n' +"предусмотрены следующие обязательные услуги:</h4>"
           

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
                    
    else:
        stand=[]
        print(" нет в базе ДН с таким диагнозом ")
        text ='В 168 Приказе отсутстует такой диагноз или порверте правильно ли Вы пишите диагноз, то есть на английском, а не на русском языке'
        stand.append(text)
        return render(request,'uslugi/usluga.html',{'stand':stand})
