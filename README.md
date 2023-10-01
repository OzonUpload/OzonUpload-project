Проект выгрузки остатков и цен на маркетплейс Ozon с сайтов поставщиков.

### Поддерживаемые сайты поставщиков:
- [str-mobile.ru](http://str-mobile.ru/)

## Установка
> Требуется версия Python **3.11.0** и выше

`py setup.py full`

## Использование
#### Запуск:
`py main.py`
#### Настройка:
**Место хранение конфигурационного файла:**
`OzonUpload/files/config.ini`
**Параметры настроек:**
[OzonUpload] - настройки программы
city - город по которому узнается время. Значения MCK; ЕКБ
notification - включение уведомлений в бота. Значения: True, False
[TelegramBot] - настройки бота и чата уведомлений
token - токен бота из @BotFather
chat_id - id чата в который будут приходить сообщения
topic_id - id сообщения о создании темы чата, для отправки в нужную тему чата
[LinkFiles] - ссылки файлов для синхронизации
link_data - ссылка на файл с базой данных
link_groups_update - ссылка на файл с настройками групп

#### Команды:
> `OzonUpload>` - основная командная оболочка.
```
OzonUpload>
			ozon - к. о. получения данных с Ozon
			parser - к. о. получения данных с сайтов поставщиков
			create
				group {name} - создание групп
			get 
				groups - получение списка групп
			update
					stocks 
							full - обновление остатка всех товаров на Ozon
							category - обновление остатка товаров категории
							product - обновление остатка товара
									id
									article
									code
			start - запуск автообновления
			stop - остановление автообновления
			exit - выход из программы
```

> `ozon` - к. о. получения данных с Ozon по api. 
> **Место хранение файла конфигурации ozon:**
> `C:\Users\{UserName}\AppData\Roaming\ozon\config.ini`
```
ozon>
	get
		warehouses - получения списка складов
	update
		warehouses - обновление списка складов с Ozon Api
		products - обновление списка товаров с Ozon Api
	exit - выход из к. о.
```

> `parser` - к. о. получения данных с сайта поставщика. **Место хранение файла конфигурации ozon:**
> `C:\Users\{UserName}\AppData\Roaming\parser\str_mobile\config.ini`

```
OzonUpload> parser
				str_mobile - к. о. поставщика str-mobile.ru

parser:str_mobile>
					add
					get
					update
					start
						update - запуск автоматического обновления
								stocks
										...
								prices
										...
					stop
						 update - остановка автоматического обновления
								 stocks
								 prices
					сlеаr - очистка списков
						products
								...
						categories 
					exit - выход из к. о. 
					
parser:str_mobile>add
					product - добавление товара в список
								id 
								article  
								code
						category {code} - добавление категории
						category_settings - добавление настроек категории				
parser:str_mobile>get 
					products - получение списка товаров
							ids 
							artictes
							codes
					categories - получение списка категорий
					category_settings {code} - получение настроек категорий
parser:str_mobile>update
						stocks
							products - обновление остатка списка товаров
									ids
									articles
									codes
							categories - обновление остатка списка категорий
						prices
								products - обновление цен списка товаров
									ids
									articles
									codes
								categories - обновление цен списка категорий
						product - получение информации товара
								id 
								article  
								code
						category {code} - получение инфорамции товаров категории
						list
							products - обновление информации списка товаров
									ids
									articles
									codes
							categories - обновление информаци списка категорий
						full - обновление всех товаров поставщиков
```