#!/usr/bin/env python3
import requests
import scrapy
from pprint import pprint

def print_menu(data):
    for cafe, categories in data.items():
        print('# ', cafe + ':', end='\n\n')
        for category, dishes in categories.items():
            print('## ', category)
            for dish in dishes:
                print('\t• ',
                    dish.get('title', 'unnamed'),
                    ' ',
                    dish.get('price', 'unknown price'))
                print('\t  ', dish.get('description', ''), end='')
                if 'allergener' in dish:
                    print(' [' + dish.get('allergener', '') + ']', end='')
                if 'attribute' in dish:
                    print(' [' + dish.get('attribute', '') + ']', end='')
                print()
            print()

def get_menu():
    def get_page(debug=False):
        if debug:
            with open('kantina.html', 'r') as f:
                retval = f.read()
        else:
            retval = requests.get('https://samskipnaden.no/dagens-meny/day/1').content
        return retval

    def parse_item(sel):
        retval = {}
        retval['price'] = sel.xpath('div[contains(@class, "views-field-field-price")]/div/text()').extract_first()
        title_section = sel.xpath('div[contains(@class, "views-field-nothing")]/span')
        retval['title'] = title_section.xpath('strong/text()').extract_first().rstrip()
        if title_section.xpath('div/img'):
            retval['attribute'] = title_section.xpath('div/img/@alt').extract_first()
        retval['description'] = sel.xpath('div[contains(@class, "views-field-field-description")]/div/text()').extract_first()
        allergener = sel.xpath('div[contains(@class, "views-field-field-allergener")]/div/text()').extract_first()
        if allergener:
            retval['allergener'] = allergener
        return retval

    def parse_category(sel):
        retval = []
        if sel.xpath('h3'):
            category_name = sel.xpath('h3/text()').extract_first()
        else:
            category_name = 'Unknown'
        for k in sel.xpath('ul/li'):
            retval.append(parse_item(k))
        return category_name, retval

    page = get_page()

    res = scrapy.Selector(text=page)

    date = res.xpath('//*[@id="block-samskipnaden-content"]/div/div/header/h3/text()').extract_first()
    contents = res.xpath('//*[@id="block-samskipnaden-content"]/div/div/div[2]')
    data = {}

    current_cafe = 'Unknown'
    for i, k in enumerate(contents.xpath('div')):
        div_class = k.xpath('@class').extract_first()
        if div_class == 'view-grouping-title':
            current_cafe = k.xpath('text()').extract_first()
        elif div_class == 'item-list':
            if current_cafe not in data:
                data[current_cafe] = {}
            category_name, dishes = parse_category(k)

            data[current_cafe][category_name] = dishes
    return data
    
if __name__ == '__main__':
    print_menu(get_menu())
