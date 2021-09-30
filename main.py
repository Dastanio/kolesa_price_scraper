import os
import requests
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
import statistics
import numpy as np
from outliers import smirnov_grubbs as grubbs
import time
start_time = time.time()


useragent = UserAgent(verify_ssl=False)

HEADERS = {'user-agent': useragent.random}
INPUT_PERCENT = 20
INPUT_PROBEG = 300000

class Kolesa:
    

    def __init__(self, model, brand, year, volume, type_engine, car_dwheel):
        self.model = model,
        self.brand = brand,
        self.params = {
            '_sys-hasphoto': '2', #С фото
            'auto-custom': '2', #Расстаможен
            'auto-car-order':'1', #В наличии

            'year[from]': year, #Год от
            'year[to]': year,#Год до
            'auto-fuel': type_engine, #Тип двигателя
            'car-dwheel': car_dwheel, #Привод 
            'auto-car-volume[from]': volume, # обьем от
            'auto-car-volume[to]': volume #обьем до
        }
    
    def get_html(self, url):

        response = requests.get(url, headers = HEADERS, params= self.params)
        html = BS(response.content, 'html.parser')

        return html
    
    def getPrice(self):

        prices_list = []
        url = f'https://kolesa.kz/cars/{self.model[0]}/{self.brand[0]}'
        html = self.get_html(url)

        all_cars_quantity = html.find('button', class_ = 'js__search-form-submit').get_text().split()[1]
        #Если в странице только одна страница то парсить без цикла
        if self.getCountPage(url) == None:

            print('Одна страница нашлось в этом url')
            prices_list.extend(self.getPriceScript(url))

        else:
            print(f'{self.getCountPage(url)} страниц нашлось в этом url')
            for page in range(1, int(self.getCountPage(url)) + 1):

                self.params['page'] = page
                print(f'[In process {page} page]')
                
                prices_list.extend(self.getPriceScript(url))

        print(prices_list)
        print(self.reject_outliers(np.array(prices_list)))

        print(f'Статистика на основе {len(self.reject_outliers(np.array(prices_list)))} машин')

        rejected_data = self.reject_outliers(np.array(prices_list))

        return self.data_grouping(rejected_data)

    # def reject_outliers(self, data, m = 2.):
    #     d = np.abs(data - np.median(data))
    #     mdev = np.median(d)
    #     s = d/mdev if mdev else 0.
    #     return data[s<m]

    def data_grouping(self, data):
        percent = 1.35
        resulting_list = []
        limit = None

        for number in sorted(data):
            if not limit or number > limit:
                limit = number*percent
                sublist = [number]
                resulting_list.append(sublist)
            else:
                sublist.append(number)

        return resulting_list

    def reject_outliers(self, data):
        data = np.array(data)
        return grubbs.test(data, alpha=0.05)

    def getPriceScript(self, url):

        prices_list = []
        html = self.get_html(url)

        car_items  = html.find_all('div', class_ = 'a-elem')      


        for i in car_items:
            if i.find('div', class_ = 'desc').find('span', class_ = 'emergency') == None and 'пробегом' in i.get_text().rstrip():

                
                if self.textFinder(i) == True:
                    prices_list.append(int("".join(i.find('span', class_ = 'price').get_text().replace('₸', '').split())))
            else:
                pass
        
        return prices_list


    #get quantity page for pagination 
    def getCountPage(self, url):

        try:
            page_count = ''
            html = self.get_html(url)

            page = html.find('div', class_ = 'pager').find('ul').find_all('span')[-1]

            for i in page:
                page_count = i.get_text()

            return page_count

        #Исключение срабатывает тогда когда в странице нет других страниц тоесть пагинации.
        except AttributeError:
            return None


    def textFinder(self, bs4):

        desc_texts = bs4.find('div', class_ = 'a-search-description').get_text().rstrip()
        
        min_ = INPUT_PROBEG - INPUT_PROBEG / 100 * INPUT_PERCENT
        max_ = INPUT_PROBEG + INPUT_PROBEG / 100 * INPUT_PERCENT


        words = desc_texts.split()
        for index, word in enumerate(words):
            if word.lower() == 'пробегом':
                c = index + 1
                result = words[c]
                while words[c+1].lower().find('км') == -1:

                    result += words[c+1]
                    c += 1

        if int(result) > min_ and int(result) < max_ or int(result) == max_ or int(result) == min_:
            return True

        else:
            return False


    # def getMeanPrice(self):
    #     return print(f'Среднее цена: {round(statistics.mean(self.getPrice()))}')

    # def getMaxPrice(self):
    #     return print(f'Максимальное цена: {max(self.getPrice())}' )

    # def getMinPrice(self):
    #     return print(f'Минимальное цена: {min(self.getPrice())}' )

    def getAllprices(self, data):

        max_ = max(data)
        min_ = min(data)
        mean = round(statistics.mean(data))

        return [min_, mean, max_]
    
    def main(self):

        final_data = []

        data = self.getPrice()
        for i in data:
            final_data.append(self.getAllprices(i)) 
        
        return print(final_data)
        


                  #Марка #Модель #год #обьем #двигатель #Привод
kolesa_obj = Kolesa('bmw', 'x5', '2007', '3', '1', None)
kolesa_obj.main()

print("--- %s seconds ---" % (time.time() - start_time))